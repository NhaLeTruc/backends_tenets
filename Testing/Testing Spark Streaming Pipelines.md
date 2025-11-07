# Testing Spark Streaming Pipelines Locally

Guiding principles
- Prefer Structured Streaming for testability (deterministic micro-batches).
- Run Spark in local mode: master = "local[*]" and set spark.sql.shuffle.partitions = 1 for determinism.
- Use in-memory / file-backed sources and sinks (MemoryStream, file source, "memory" sink, or foreachBatch capture).
- Make time deterministic: control input timestamps or use manual clocks when possible.
- Use ephemeral checkpoint and temp dirs. Clean between tests.
- Drive micro-batches deterministically: use Query.processAllAvailable() or awaitTermination with timeouts.

Quick checklist
- SparkSession.builder.master("local[*]").config("spark.sql.shuffle.partitions","1")
- Use MemoryStream (Scala) or file/rate sources (Python) for deterministic inputs
- Use "memory" sink or collect outputs via foreachBatch into a thread-safe collection
- Call query.processAllAvailable() to force processing of all queued data
- Assert output contents (order-agnostic unless you control ordering)
- Reset Spark state between tests (stop SparkSession, delete checkpoints)

Scala example (recommended: MemoryStream)
- Dependencies: spark-sql & spark-sql-kafka (if needed) matching Spark version.

```scala
// ... test framework setup (ScalaTest / Specs2) ...
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.execution.streaming.MemoryStream
import org.apache.spark.sql.functions._
import scala.concurrent.duration._

val spark = SparkSession.builder()
  .master("local[2]")
  .appName("stream-test")
  .config("spark.sql.shuffle.partitions", "1")
  .getOrCreate()
import spark.implicits._

// MemoryStream of String
val input = MemoryStream[String]
val ds = input.toDS()
val counts = ds
  .flatMap(_.split("\\s+"))
  .groupByKey(identity)
  .count()

val query = counts.toDF("word","count")
  .writeStream
  .format("memory")       // in-memory sink for assertions
  .queryName("words")
  .outputMode("complete")
  .start()

// push data into stream
input.addData("hello world", "hello spark")
query.processAllAvailable()

val res = spark.sql("select * from words").collect()
// assert res contains expected rows: ("hello",2), ("world",1), ("spark",1)

query.stop()
spark.stop()
```

PySpark example (file source + memory sink)
- Use a temp directory as file source. Write files atomically (write then move) to avoid partial reads.

```python
from pyspark.sql import SparkSession
import tempfile
import shutil
import time
import os
import json

spark = SparkSession.builder \
    .master("local[2]") \
    .appName("py-stream-test") \
    .config("spark.sql.shuffle.partitions","1") \
    .getOrCreate()

src = tempfile.mkdtemp()
# memory sink query
df = spark.readStream.schema("value string").text(src)
counts = df.selectExpr("split(value,'\\s+') as words") \
           .selectExpr("explode(words) as word") \
           .groupBy("word").count()

q = counts.writeStream.format("memory").queryName("words").outputMode("complete").start()

# write test files
open(os.path.join(src, "f1.txt"), "w").write("hello world\n")
# ensure FS visibility on Windows before processing
time.sleep(0.2)

q.processAllAvailable()
res = spark.sql("select * from words").collect()
# assert on res

q.stop()
shutil.rmtree(src)
spark.stop()
```

Testing tips and patterns
- Use foreachBatch to capture batch outputs into a shared (thread-safe) list or temp table for assertions.
- For end-to-end tests with Kafka, run an ephemeral Kafka (containers) and use small topics + short retention; still use local[*] Spark.
- When ordering matters, include an ordering key and assert on deterministic sort.
- Use small partitions and local[*] to emulate parallelism but keep tests fast.
- Fail fast: set small timeouts for processAllAvailable / awaitTermination.

CI considerations
- Keep tests fast (< 30s). Use unit tests focused on logic; keep integration tests separate and run less frequently.
- Use Docker/Kubernetes for Kafka/Stateful components in integration pipeline only.
- Cache or snapshot small datasets; avoid large test data.

Summary
- Prefer MemoryStream (Scala) or controlled file/rate sources (Python).
- Force processing using processAllAvailable.
- Keep spark config deterministic (partitions=1), use temp dirs for checkpointing, and assert on "memory" sink or captured outputs.