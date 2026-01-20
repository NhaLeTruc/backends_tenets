# Senior Data Engineer Interview - ETL Specialization

---

## Part 1: General Principles & Architecture

### Question:
Explain the key differences between a data lake and a data warehouse, and when you'd choose one over the other?

### Answer:
A data lake is a centralized repository that stores raw, unstructured, semi-structured, and structured data at any scale. It follows a schema-on-read approach, meaning the structure is applied when the data is read. In contrast, a data warehouse stores processed, structured data optimized for querying and analysis, following a schema-on-write approach.

Choose a data lake when:
- Dealing with diverse data sources and formats (JSON, Parquet, CSV, logs)
- Need to preserve raw data for future unknown use cases
- Building ML models requiring extensive historical data
- Cost is a concern for massive storage volumes

Choose a data warehouse when:
- Need consistent, fast query performance for business intelligence
- Working with structured, well-defined data models
- Require strong ACID guarantees and data quality
- Supporting concurrent users running complex analytical queries

In practice, we often use both in a hybrid architecture—data lake for raw storage and exploratory work, warehouse for production analytics.

### Question:
Excellent. Now, in the context of AWS specifically, if you're designing an ETL pipeline from S3 (data lake) to Snowflake, what are the key architectural components you'd consider?

### Answer:
For an S3-to-Snowflake pipeline, I'd architect it with these components:

**Ingestion Layer:**
- AWS Kinesis or Kafka for streaming data
- AWS Lambda for event-driven processing
- S3 event notifications for file arrival triggers

**Processing Layer:**
- EMR or Glue for Spark-based transformations
- AWS Glue Catalog for metadata management
- Step Functions for workflow orchestration

**Storage Layer:**
- S3 organized with proper partitioning (date, source, type)
- Separate zones: raw/, staging/, processed/
- Lifecycle policies for cost optimization

**Loading Layer:**
- Snowpipe for continuous loading
- COPY INTO statements for batch loads
- External tables for querying S3 directly

**Monitoring & Governance:**
- CloudWatch for logs and metrics
- AWS Lake Formation for access control
- Data quality checks using Great Expectations or custom validators

**Security:**
- IAM roles with least privilege
- S3 bucket encryption (SSE-S3 or KMS)
- Snowflake storage integration for secure access
- VPC endpoints for private connectivity

### Question:
Great overview. Let's talk about the Lambda architecture versus Kappa architecture. Which would you recommend for a use case requiring both real-time analytics and historical reporting?

### Answer:
That's a nuanced question. Let me compare both:

**Lambda Architecture** has three layers:
- Batch layer: processes complete dataset for accuracy
- Speed layer: processes real-time data for low latency
- Serving layer: merges both views

**Kappa Architecture** simplifies this:
- Single stream processing layer
- Reprocessing done by replaying the event stream

For real-time analytics AND historical reporting, I'd actually lean toward **Lambda** because:

1. **Data accuracy:** Batch layer ensures eventual correctness
2. **Different SLAs:** Real-time needs speed, historical needs completeness
3. **Tooling maturity:** Spark Structured Streaming for speed, Spark batch for historical
4. **Cost efficiency:** Can use spot instances for batch processing

However, I'd implement a "Lambda-lite" approach:
- Use Spark Structured Streaming for both real-time and micro-batch
- Maintain a single codebase with different trigger intervals
- Store in Delta Lake or Iceberg for time travel and updates
- This gives Lambda's benefits without maintaining two separate pipelines

If the team is small or data volumes aren't massive, I'd go full Kappa with Kafka + Spark Structured Streaming + Delta Lake for simplicity.

---

## Part 2: AWS & S3 Deep Dive

### Question:
Let's get more specific about S3. How would you optimize S3 for ETL performance? Walk me through partitioning strategies.

### Answer:
S3 optimization is critical for ETL performance. Here's my approach:

**Partitioning Strategy:**

```
s3://bucket/data-lake/
├── raw/
│   ├── source=salesforce/
│   │   ├── year=2025/
│   │   │   ├── month=12/
│   │   │   │   ├── day=27/
│   │   │   │   │   ├── hour=10/
│   │   │   │   │   │   └── batch_001.parquet
```

**Key principles:**
1. **Partition by query patterns:** Most common filter becomes the first partition
2. **Avoid high cardinality:** Don't partition by user_id if you have millions
3. **Date partitioning:** Year/month/day hierarchy for time-series data
4. **Avoid small files:** Combine into files 128MB-1GB for optimal Spark reading

**Performance optimizations:**

```python
# 1. File Format Selection
# Parquet for analytical workloads (columnar, compressed)
df.write.format("parquet") \
    .option("compression", "snappy") \
    .partitionBy("year", "month", "day") \
    .mode("append") \
    .save("s3://bucket/processed/")

# 2. S3 Request Optimization
spark.conf.set("spark.hadoop.fs.s3a.connection.maximum", "1000")
spark.conf.set("spark.hadoop.fs.s3a.threads.max", "256")
spark.conf.set("spark.hadoop.fs.s3a.fast.upload", "true")

# 3. S3 Select for filter pushdown
# Use when filtering large files server-side
```

**S3 Lifecycle Management:**

```json
{
  "Rules": [
    {
      "Id": "MoveToIA",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 180,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

**Naming Conventions:**
- Use consistent prefixes for parallel processing
- Avoid sequential prefixes (timestamps) that create hotspots
- Add hash prefix for high throughput: `abc123/year=2025/...`

### Question:
Good. Now, you mentioned small files. How do you handle the small file problem in production, especially when dealing with streaming data that creates many small files?

### Answer:
The small file problem is one of the most common ETL performance killers. Here's my multi-layered approach:

**1. Compaction Strategy:**

```python
# Scheduled compaction job (run hourly/daily)
from pyspark.sql import SparkSession

def compact_small_files(input_path, output_path, target_size_mb=512):
    spark = SparkSession.builder.appName("Compaction").getOrCreate()

    # Read all small files
    df = spark.read.parquet(input_path)

    # Repartition based on target size
    total_size_mb = df.queryExecution.optimizedPlan.stats.sizeInBytes / (1024**2)
    num_partitions = max(1, int(total_size_mb / target_size_mb))

    # Write compacted files
    df.repartition(num_partitions) \
        .write \
        .mode("overwrite") \
        .parquet(output_path)

    return num_partitions
```

**2. Auto-optimize in Delta Lake:**

```sql
-- Enable auto-optimization
SET spark.databricks.delta.optimizeWrite.enabled = true;
SET spark.databricks.delta.autoCompact.enabled = true;

-- Manual optimize command
OPTIMIZE delta.`s3://bucket/data/`
WHERE date >= current_date() - INTERVAL 7 DAYS;

-- Z-ordering for common query patterns
OPTIMIZE delta.`s3://bucket/data/`
ZORDER BY (customer_id, transaction_date);
```

**3. Spark Structured Streaming with Trigger Intervals:**

```python
# Instead of processing every micro-batch immediately
query = df.writeStream \
    .format("parquet") \
    .option("path", "s3://bucket/streaming-data/") \
    .trigger(processingTime='5 minutes')  # Batch multiple events
    .option("checkpointLocation", "s3://bucket/checkpoints/") \
    .start()
```

**4. AWS Glue ETL Job with Grouping:**

```python
# Glue job that groups files
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="raw_db",
    table_name="events",
    transformation_ctx="datasource",
    additional_options={
        "groupFiles": "inPartition",
        "groupSize": "134217728"  # 128 MB
    }
)
```

**5. Monitoring and Alerting:**

```python
# CloudWatch metric for file count monitoring
import boto3

def check_small_files(bucket, prefix, threshold=1000):
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')

    file_count = 0
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        file_count += len(page.get('Contents', []))

    if file_count > threshold:
        # Trigger compaction job
        cloudwatch.put_metric_data(
            Namespace='ETL',
            MetricData=[{
                'MetricName': 'SmallFileCount',
                'Value': file_count,
                'Unit': 'Count'
            }]
        )
```

**Best Practices:**
- Set up automated compaction during off-peak hours
- Use file format with built-in optimization (Delta, Iceberg, Hudi)
- Monitor file size distribution with Glue Catalog statistics
- Implement backpressure in streaming pipelines

### Question:
Excellent. Let's talk about data formats. When would you choose Parquet vs ORC vs Avro? And how do you handle schema evolution?

### Answer:
Great question. Each format has specific use cases:

**Parquet:**
- **Use when:** Analytical queries, Spark/Snowflake workloads, AWS Athena
- **Strengths:** Excellent compression, columnar format, predicate pushdown
- **Schema evolution:** Supports adding columns, handles missing columns gracefully
- **Compression:** Snappy for balance, GZIP for max compression

**ORC:**
- **Use when:** Hive-based workflows, heavy Hadoop ecosystem
- **Strengths:** Best compression ratios, built-in indexes, ACID support
- **Schema evolution:** Strong schema evolution support
- **Compression:** Zlib default, Snappy for speed

**Avro:**
- **Use when:** Schema evolution is critical, row-based access, Kafka integration
- **Strengths:** Compact serialization, schema embedded in file, splittable
- **Schema evolution:** Best-in-class schema evolution with compatibility modes
- **Compression:** Snappy, Deflate

**My recommendation matrix:**

```
Data Lake Storage (S3):        Parquet (analytical access)
Kafka Messages:                Avro (schema evolution)
Hive/Presto Queries:          ORC or Parquet
Snowflake External Tables:     Parquet
Long-term Archival:           Parquet with GZIP
```

**Schema Evolution Handling:**

```python
# 1. Using Delta Lake for schema evolution
df_new.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("s3://bucket/delta-table/")

# 2. Avro with schema registry
from confluent_kafka.avro import AvroProducer

avro_producer = AvroProducer({
    'bootstrap.servers': 'broker:9092',
    'schema.registry.url': 'http://schema-registry:8081'
}, default_value_schema=value_schema)

# 3. Explicit schema management
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Define base schema
base_schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("name", StringType(), True),
])

# Handle new fields with defaults
def merge_schemas(old_schema, new_schema):
    # Add new fields with null defaults
    # Validate no breaking changes (type modifications, required fields removed)
    pass

# 4. Glue Schema Registry integration
glueContext.write_dynamic_frame.from_options(
    frame=dyf,
    connection_type="s3",
    connection_options={
        "path": "s3://bucket/data/",
        "compressionType": "snappy"
    },
    format="parquet",
    format_options={
        "useGlueParquetWriter": True
    },
    transformation_ctx="write_parquet"
)
```

**Schema Evolution Best Practices:**
1. **Additive changes only:** Add new optional fields
2. **Version control:** Store schemas in Git with semantic versioning
3. **Backward/forward compatibility:** Test with old and new readers
4. **Documentation:** Maintain schema changelog
5. **Validation:** Schema validation before writing to production

---

## Part 3: Snowflake Deep Dive

### Question:
Let's shift to Snowflake. How do you optimize data loading from S3 to Snowflake? Walk me through both Snowpipe and COPY INTO approaches.

### Answer:
Excellent question. Let me cover both approaches and when to use each.

**Snowpipe (Continuous Loading):**

```sql
-- 1. Create storage integration
CREATE STORAGE INTEGRATION s3_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = S3
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789:role/snowflake-s3-role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://my-bucket/data/');

-- 2. Create stage
CREATE STAGE my_s3_stage
  STORAGE_INTEGRATION = s3_integration
  URL = 's3://my-bucket/data/'
  FILE_FORMAT = (TYPE = PARQUET);

-- 3. Create target table with clustering
CREATE TABLE fact_transactions (
  transaction_id NUMBER,
  customer_id NUMBER,
  transaction_date TIMESTAMP_NTZ,
  amount DECIMAL(18,2),
  status VARCHAR(50)
)
CLUSTER BY (transaction_date, customer_id);

-- 4. Create pipe
CREATE PIPE transaction_pipe
  AUTO_INGEST = TRUE
  AS
  COPY INTO fact_transactions
  FROM @my_s3_stage
  FILE_FORMAT = (TYPE = PARQUET)
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
  ON_ERROR = CONTINUE;

-- 5. Show pipe notification channel for S3 event
SHOW PIPES;
DESC PIPE transaction_pipe;
```

**AWS S3 Event Configuration:**

```json
{
  "QueueConfigurations": [
    {
      "Id": "SnowpipeEvent",
      "QueueArn": "arn:aws:sqs:us-east-1:123:snowflake-pipe-queue",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "data/transactions/"
            },
            {
              "Name": "suffix",
              "Value": ".parquet"
            }
          ]
        }
      }
    }
  ]
}
```

**COPY INTO (Batch Loading):**

```sql
-- 1. Basic COPY
COPY INTO fact_transactions
FROM @my_s3_stage/year=2025/month=12/
FILE_FORMAT = (TYPE = PARQUET)
PATTERN = '.*[.]parquet'
ON_ERROR = SKIP_FILE;

-- 2. Advanced COPY with transformations
COPY INTO fact_transactions (transaction_id, customer_id, transaction_date, amount, status)
FROM (
  SELECT
    $1:id::NUMBER,
    $1:customer::NUMBER,
    TO_TIMESTAMP_NTZ($1:timestamp::VARCHAR),
    $1:amount::DECIMAL(18,2),
    UPPER($1:status::VARCHAR)
  FROM @my_s3_stage
)
FILE_FORMAT = (TYPE = JSON)
ON_ERROR = CONTINUE
VALIDATION_MODE = RETURN_ERRORS;

-- 3. Partition-aware loading
COPY INTO fact_transactions
FROM @my_s3_stage
FILE_FORMAT = (TYPE = PARQUET)
FILES = (
  'year=2025/month=12/day=27/file1.parquet',
  'year=2025/month=12/day=27/file2.parquet'
)
FORCE = TRUE;  -- Reload even if already loaded
```

**When to use each:**

**Snowpipe:**
- Real-time/near real-time requirements (latency < 1 minute)
- Streaming data with continuous file arrivals
- Event-driven architecture
- Small to medium file sizes
- Cost: Charged per file + serverless compute

**COPY INTO:**
- Scheduled batch loads (hourly, daily)
- Large file volumes
- Need explicit control over load timing
- Initial historical data loads
- Complex transformations during load
- Cost: Use warehouse compute (more control)

**Optimization Techniques:**

```sql
-- 1. Use dedicated warehouse for loading
CREATE WAREHOUSE loading_wh WITH
  WAREHOUSE_SIZE = 'LARGE'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  SCALING_POLICY = 'ECONOMY';

-- 2. Increase parallelism
ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 3600;

-- 3. Monitor load history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'FACT_TRANSACTIONS',
  START_TIME => DATEADD(hours, -24, CURRENT_TIMESTAMP())
));

-- 4. Check pipe status
SELECT SYSTEM$PIPE_STATUS('transaction_pipe');

-- 5. Handle load errors
SELECT *
FROM TABLE(VALIDATE(fact_transactions, JOB_ID => '_last'));
```

### Question:
Great detail. Now, how do you handle slowly changing dimensions (SCDs) in Snowflake, specifically Type 2?

### Answer:
SCD Type 2 is crucial for maintaining historical accuracy. Here's my comprehensive approach:

**Method 1: MERGE Statement (Recommended):**

```sql
-- 1. Create dimension table with SCD Type 2 structure
CREATE TABLE dim_customer (
  customer_key NUMBER AUTOINCREMENT,  -- Surrogate key
  customer_id NUMBER,                 -- Natural key
  customer_name VARCHAR(100),
  email VARCHAR(100),
  segment VARCHAR(50),

  -- SCD Type 2 columns
  effective_date DATE,
  end_date DATE,
  is_current BOOLEAN,

  -- Audit columns
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

  PRIMARY KEY (customer_key)
)
CLUSTER BY (customer_id, is_current);

-- 2. Create staging table
CREATE TEMPORARY TABLE stg_customer AS
SELECT * FROM source_customer WHERE 1=0;

-- 3. Load new data into staging
COPY INTO stg_customer
FROM @my_s3_stage/customers/
FILE_FORMAT = (TYPE = PARQUET);

-- 4. MERGE for SCD Type 2
MERGE INTO dim_customer tgt
USING (
  SELECT
    s.*,
    CURRENT_DATE() AS effective_date,
    '9999-12-31'::DATE AS end_date,
    TRUE AS is_current
  FROM stg_customer s
) src
ON tgt.customer_id = src.customer_id
   AND tgt.is_current = TRUE
WHEN MATCHED AND (
  -- Check if any tracked attribute changed
  tgt.customer_name != src.customer_name OR
  tgt.email != src.email OR
  tgt.segment != src.segment
) THEN UPDATE SET
  -- Expire current record
  tgt.end_date = CURRENT_DATE(),
  tgt.is_current = FALSE,
  tgt.updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT (
  customer_id, customer_name, email, segment,
  effective_date, end_date, is_current
) VALUES (
  src.customer_id, src.customer_name, src.email, src.segment,
  src.effective_date, src.end_date, src.is_current
);

-- 5. Insert new versions for changed records
INSERT INTO dim_customer (
  customer_id, customer_name, email, segment,
  effective_date, end_date, is_current
)
SELECT
  s.customer_id,
  s.customer_name,
  s.email,
  s.segment,
  CURRENT_DATE() AS effective_date,
  '9999-12-31'::DATE AS end_date,
  TRUE AS is_current
FROM stg_customer s
INNER JOIN dim_customer d
  ON s.customer_id = d.customer_id
  AND d.end_date = CURRENT_DATE()  -- Just expired
WHERE d.is_current = FALSE;
```

**Method 2: Streams and Tasks (Automated):**

```sql
-- 1. Create stream on source
CREATE STREAM customer_stream ON TABLE source_customer;

-- 2. Create task to process changes
CREATE TASK process_customer_scd
  WAREHOUSE = etl_wh
  SCHEDULE = '5 MINUTE'
WHEN
  SYSTEM$STREAM_HAS_DATA('customer_stream')
AS
BEGIN
  -- Expire changed records
  UPDATE dim_customer tgt
  SET
    end_date = CURRENT_DATE(),
    is_current = FALSE,
    updated_at = CURRENT_TIMESTAMP()
  WHERE tgt.customer_id IN (
    SELECT customer_id
    FROM customer_stream
    WHERE METADATA$ACTION = 'INSERT'
  )
  AND tgt.is_current = TRUE;

  -- Insert new versions
  INSERT INTO dim_customer (
    customer_id, customer_name, email, segment,
    effective_date, end_date, is_current
  )
  SELECT
    customer_id, customer_name, email, segment,
    CURRENT_DATE(), '9999-12-31'::DATE, TRUE
  FROM customer_stream
  WHERE METADATA$ACTION = 'INSERT';
END;

-- 3. Enable task
ALTER TASK process_customer_scd RESUME;
```

**Method 3: Using Stored Procedures:**

```sql
CREATE OR REPLACE PROCEDURE sp_load_scd_type2(
  source_table STRING,
  target_table STRING,
  natural_key STRING,
  tracked_columns ARRAY
)
RETURNS STRING
LANGUAGE JAVASCRIPT
AS
$$
  // Build dynamic MERGE statement
  var tracked_cols_condition = TRACKED_COLUMNS.map(
    col => `tgt.${col} != src.${col}`
  ).join(' OR ');

  var merge_sql = `
    MERGE INTO ${TARGET_TABLE} tgt
    USING ${SOURCE_TABLE} src
    ON tgt.${NATURAL_KEY} = src.${NATURAL_KEY}
       AND tgt.is_current = TRUE
    WHEN MATCHED AND (${tracked_cols_condition}) THEN
      UPDATE SET
        tgt.end_date = CURRENT_DATE(),
        tgt.is_current = FALSE
  `;

  snowflake.execute({sqlText: merge_sql});

  // Insert new versions
  // ... similar logic

  return 'SCD Type 2 processing completed';
$$;

-- Call procedure
CALL sp_load_scd_type2(
  'stg_customer',
  'dim_customer',
  'customer_id',
  ARRAY_CONSTRUCT('customer_name', 'email', 'segment')
);
```

**Best Practices:**

```sql
-- 1. Create indexes for performance
CREATE INDEX idx_customer_natural ON dim_customer(customer_id, is_current);

-- 2. Cluster by common query patterns
ALTER TABLE dim_customer CLUSTER BY (customer_id, effective_date);

-- 3. Monitoring query
SELECT
  customer_id,
  COUNT(*) as version_count,
  MIN(effective_date) as first_seen,
  MAX(end_date) as last_updated
FROM dim_customer
GROUP BY customer_id
HAVING COUNT(*) > 10  -- Customers with many changes
ORDER BY version_count DESC;

-- 4. Point-in-time query
SELECT
  c.customer_id,
  c.customer_name,
  c.segment
FROM dim_customer c
WHERE c.effective_date <= '2025-01-01'
  AND c.end_date > '2025-01-01';

-- 5. Current snapshot
SELECT *
FROM dim_customer
WHERE is_current = TRUE;
```

---

## Part 4: Spark Optimization

### Question:
Let's dive into Spark. You're processing 10TB of data daily from S3. The job is taking 4 hours and you need to bring it down to under 1 hour. Walk me through your optimization strategy.

### Answer:
Great scenario. I'd approach this systematically across multiple dimensions:

**Phase 1: Diagnosis (15-30 minutes)**

```python
# 1. Enable detailed metrics
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.eventLog.enabled", "true")
spark.conf.set("spark.eventLog.dir", "s3://bucket/spark-logs/")

# 2. Check current execution plan
df = spark.read.parquet("s3://bucket/data/")
df.explain(mode="formatted")

# 3. Examine stage details
spark.sparkContext.setLogLevel("INFO")

# 4. Common bottleneck indicators
# - Many small tasks (< 128 MB each) → file consolidation needed
# - Data skew → repartitioning needed
# - Shuffle spill to disk → memory tuning needed
# - GC overhead > 10% → heap tuning needed
```

**Phase 2: Quick Wins (30% improvement)**

```python
# 1. Partition pruning
from pyspark.sql.functions import col

# Bad: Reads all partitions
df = spark.read.parquet("s3://bucket/data/")
df.filter(col("date") == "2025-12-27")

# Good: Reads only needed partitions
df = spark.read.parquet("s3://bucket/data/date=2025-12-27/")

# 2. Column pruning
# Bad: Reads all columns
df = spark.read.parquet("s3://bucket/data/")
result = df.select("id", "amount")

# Good: Project early
df = spark.read.parquet("s3://bucket/data/").select("id", "amount", "date")

# 3. Predicate pushdown
# Ensure filters are pushed to data source
df = spark.read.parquet("s3://bucket/data/") \
    .filter(col("amount") > 1000) \
    .filter(col("date") >= "2025-01-01")

# 4. Enable dynamic partition pruning
spark.conf.set("spark.sql.optimizer.dynamicPartitionPruning.enabled", "true")
```

**Phase 3: Spark Configuration Tuning (20% improvement)**

```python
# EMR cluster configuration for 10TB workload
spark_config = {
    # Executor configuration (r5.4xlarge: 16 cores, 128 GB RAM)
    "spark.executor.instances": "100",
    "spark.executor.cores": "5",
    "spark.executor.memory": "20g",
    "spark.executor.memoryOverhead": "4g",

    # Driver configuration
    "spark.driver.memory": "16g",
    "spark.driver.cores": "4",

    # Shuffle optimization
    "spark.sql.shuffle.partitions": "2000",  # ~200 partitions per TB
    "spark.default.parallelism": "2000",
    "spark.sql.files.maxPartitionBytes": "134217728",  # 128 MB

    # Adaptive query execution
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.sql.adaptive.skewJoin.enabled": "true",

    # S3 optimizations
    "spark.hadoop.fs.s3a.connection.maximum": "1000",
    "spark.hadoop.fs.s3a.threads.max": "256",
    "spark.hadoop.fs.s3a.fast.upload": "true",
    "spark.hadoop.fs.s3a.fast.upload.buffer": "disk",
    "spark.hadoop.fs.s3a.block.size": "134217728",

    # Memory management
    "spark.memory.fraction": "0.8",
    "spark.memory.storageFraction": "0.3",

    # Serialization
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    "spark.kryoserializer.buffer.max": "512m",

    # Compression
    "spark.sql.parquet.compression.codec": "snappy",
    "spark.io.compression.codec": "snappy"
}

# Apply configuration
for key, value in spark_config.items():
    spark.conf.set(key, value)
```

**Phase 4: Algorithm Optimization (30% improvement)**

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# 1. Broadcast joins for small tables
# Bad: Shuffle both sides
large_df.join(small_df, "customer_id")

# Good: Broadcast small table
from pyspark.sql.functions import broadcast
large_df.join(broadcast(small_df), "customer_id")

# 2. Handle data skew
# Identify skewed keys
skew_analysis = df.groupBy("customer_id").count() \
    .orderBy(col("count").desc()).limit(10)
skew_analysis.show()

# Salting technique for skewed joins
def skewed_join(large_df, skewed_df, join_key, salt_factor=10):
    # Add salt to large table
    large_salted = large_df.withColumn(
        "salt",
        (F.rand() * salt_factor).cast("int")
    )

    # Explode small table with all salt values
    from pyspark.sql.functions import explode, array, lit
    skewed_exploded = skewed_df.withColumn(
        "salt",
        explode(array([lit(i) for i in range(salt_factor)]))
    )

    # Join on composite key
    result = large_salted.join(
        skewed_exploded,
        [large_salted[join_key] == skewed_exploded[join_key],
         large_salted["salt"] == skewed_exploded["salt"]]
    ).drop("salt")

    return result

# 3. Avoid UDFs when possible
# Bad: Python UDF (serialization overhead)
from pyspark.sql.types import StringType
@F.udf(returnType=StringType())
def categorize_amount(amount):
    if amount > 1000:
        return "high"
    elif amount > 100:
        return "medium"
    else:
        return "low"

df.withColumn("category", categorize_amount(col("amount")))

# Good: Use built-in functions
df.withColumn(
    "category",
    F.when(col("amount") > 1000, "high")
     .when(col("amount") > 100, "medium")
     .otherwise("low")
)

# 4. Minimize shuffles
# Bad: Multiple aggregations causing multiple shuffles
df.groupBy("customer_id").agg(F.sum("amount").alias("total"))
df.groupBy("customer_id").agg(F.count("*").alias("count"))

# Good: Single aggregation
df.groupBy("customer_id").agg(
    F.sum("amount").alias("total"),
    F.count("*").alias("count")
)
```

**Phase 5: Data Format & Storage Optimization (20% improvement)**

```python
# 1. Use columnar formats with proper compression
df.write.format("parquet") \
    .option("compression", "snappy") \
    .option("parquet.block.size", 134217728) \
    .partitionBy("year", "month", "day") \
    .mode("overwrite") \
    .save("s3://bucket/optimized/")

# 2. File consolidation
# Target: 128MB - 1GB per file
def optimize_file_size(df, target_file_size_mb=512):
    # Calculate optimal partition count
    total_size_bytes = df.rdd.map(
        lambda row: len(str(row))
    ).reduce(lambda a, b: a + b)

    target_partitions = max(
        1,
        int(total_size_bytes / (target_file_size_mb * 1024 * 1024))
    )

    return df.repartition(target_partitions)

optimized_df = optimize_file_size(df)
optimized_df.write.parquet("s3://bucket/optimized/")

# 3. Z-ordering with Delta Lake
df.write.format("delta").save("s3://bucket/delta-table/")

spark.sql("""
    OPTIMIZE delta.`s3://bucket/delta-table/`
    ZORDER BY (customer_id, transaction_date)
""")

# 4. Bucketing for repeated joins
df.write.format("parquet") \
    .bucketBy(200, "customer_id") \
    .sortBy("transaction_date") \
    .saveAsTable("transactions_bucketed")
```

**Phase 6: Caching Strategy**

```python
from pyspark import StorageLevel

# Cache only when data is reused multiple times
base_df = spark.read.parquet("s3://bucket/data/") \
    .filter(col("date") >= "2025-01-01")

# Cache with appropriate storage level
if base_df.count() < 10_000_000:  # Small enough for memory
    base_df.persist(StorageLevel.MEMORY_AND_DISK)
else:
    base_df.persist(StorageLevel.DISK_ONLY)

# Multiple operations on cached data
result1 = base_df.groupBy("customer_id").count()
result2 = base_df.groupBy("product_id").sum("amount")

# Unpersist when done
base_df.unpersist()
```

**Phase 7: Monitoring & Validation**

```python
import time

def measure_performance(func, description):
    start = time.time()
    result = func()
    duration = time.time() - start

    print(f"{description}: {duration:.2f} seconds")

    # Log to CloudWatch
    import boto3
    cloudwatch = boto3.client('cloudwatch')
    cloudwatch.put_metric_data(
        Namespace='SparkETL',
        MetricData=[{
            'MetricName': 'JobDuration',
            'Value': duration,
            'Unit': 'Seconds',
            'Dimensions': [
                {'Name': 'JobName', 'Value': description}
            ]
        }]
    )

    return result

# Use in pipeline
result = measure_performance(
    lambda: df.groupBy("customer_id").count(),
    "CustomerAggregation"
)
```

**Expected Improvements:**
- Partition/column pruning: 30-40% reduction
- Configuration tuning: 15-20% reduction
- Algorithm optimization: 20-30% reduction
- File consolidation: 10-15% reduction
- **Total: 75-85% reduction (4 hours → 36-60 minutes)**

### Question:
Excellent. Now, you mentioned data skew. Can you show me how you'd detect and handle skew in a real-world join scenario?

### Answer:
Absolutely. Data skew is one of the most challenging performance issues. Here's my comprehensive approach:

**Detection:**

```python
from pyspark.sql import functions as F

# 1. Analyze key distribution
def detect_skew(df, key_column, threshold_ratio=10):
    """
    Detect skewed keys in a DataFrame
    threshold_ratio: Max/Avg ratio to consider skewed
    """
    key_counts = df.groupBy(key_column).count()

    stats = key_counts.select(
        F.max("count").alias("max_count"),
        F.avg("count").alias("avg_count"),
        F.stddev("count").alias("stddev_count"),
        F.count("*").alias("unique_keys")
    ).collect()[0]

    skew_ratio = stats["max_count"] / stats["avg_count"]

    print(f"Skew Analysis for {key_column}:")
    print(f"  Unique keys: {stats['unique_keys']:,}")
    print(f"  Average records per key: {stats['avg_count']:.2f}")
    print(f"  Max records per key: {stats['max_count']:,}")
    print(f"  Skew ratio: {skew_ratio:.2f}x")
    print(f"  Standard deviation: {stats['stddev_count']:.2f}")

    if skew_ratio > threshold_ratio:
        print(f"  ⚠️  SKEWED! (ratio > {threshold_ratio})")

        # Show top skewed keys
        print("\n  Top 10 skewed keys:")
        key_counts.orderBy(F.desc("count")).show(10)

        return True, key_counts.orderBy(F.desc("count")).limit(100).collect()
    else:
        print(f"  ✓ Not skewed (ratio < {threshold_ratio})")
        return False, []

# Example usage
orders_df = spark.read.parquet("s3://bucket/orders/")
is_skewed, skewed_keys = detect_skew(orders_df, "customer_id")

# 2. Check partition skew
def analyze_partition_skew(df):
    """Analyze data distribution across partitions"""
    partition_sizes = df.rdd.mapPartitions(
        lambda it: [sum(1 for _ in it)]
    ).collect()

    import numpy as np
    print(f"Partition Statistics:")
    print(f"  Total partitions: {len(partition_sizes)}")
    print(f"  Min size: {min(partition_sizes):,}")
    print(f"  Max size: {max(partition_sizes):,}")
    print(f"  Avg size: {np.mean(partition_sizes):,.0f}")
    print(f"  Std dev: {np.std(partition_sizes):,.0f}")
    print(f"  Skew ratio: {max(partition_sizes) / np.mean(partition_sizes):.2f}x")

    return partition_sizes

analyze_partition_skew(orders_df)
```

**Handling Strategy 1: Salting (Most Common)**

```python
def salted_join(large_df, small_df, join_key, skewed_keys=None, salt_factor=20):
    """
    Handle skewed joins using salting technique

    Args:
        large_df: Large DataFrame
        small_df: Small DataFrame (will be exploded)
        join_key: Column name to join on
        skewed_keys: List of skewed key values
        salt_factor: Number of salts to use
    """
    from pyspark.sql.functions import when, lit, explode, array

    # If skewed keys not provided, auto-detect
    if skewed_keys is None:
        _, skewed_key_rows = detect_skew(large_df, join_key)
        skewed_keys = [row[join_key] for row in skewed_key_rows]

    # Mark skewed keys in large table and add salt
    large_with_salt = large_df.withColumn(
        "is_skewed",
        when(F.col(join_key).isin(skewed_keys), lit(True)).otherwise(lit(False))
    ).withColumn(
        "salt",
        when(
            F.col("is_skewed"),
            (F.rand() * salt_factor).cast("int")
        ).otherwise(lit(0))
    )

    # Explode small table for skewed keys
    small_skewed = small_df.filter(
        F.col(join_key).isin(skewed_keys)
    ).withColumn(
        "salt",
        explode(array([lit(i) for i in range(salt_factor)]))
    ).withColumn("is_skewed", lit(True))

    # Regular small table for non-skewed keys
    small_regular = small_df.filter(
        ~F.col(join_key).isin(skewed_keys)
    ).withColumn("salt", lit(0)) \
     .withColumn("is_skewed", lit(False))

    # Union small tables
    small_combined = small_skewed.union(small_regular)

    # Join on composite key
    result = large_with_salt.join(
        small_combined,
        (large_with_salt[join_key] == small_combined[join_key]) &
        (large_with_salt["salt"] == small_combined["salt"])
    ).drop(large_with_salt["is_skewed"]) \
     .drop(large_with_salt["salt"]) \
     .drop(small_combined["is_skewed"]) \
     .drop(small_combined["salt"])

    return result

# Usage
result = salted_join(
    large_df=orders_df,
    small_df=customers_df,
    join_key="customer_id",
    salt_factor=20
)
```

**Handling Strategy 2: Isolated Skewed Keys**

```python
def isolated_skew_join(large_df, small_df, join_key, skew_threshold=100000):
    """
    Isolate skewed keys and process separately
    """
    # Identify skewed keys
    key_counts = large_df.groupBy(join_key).count()
    skewed_keys = key_counts.filter(F.col("count") > skew_threshold) \
        .select(join_key).rdd.flatMap(lambda x: x).collect()

    print(f"Found {len(skewed_keys)} skewed keys")

    # Split large DataFrame
    large_skewed = large_df.filter(F.col(join_key).isin(skewed_keys))
    large_normal = large_df.filter(~F.col(join_key).isin(skewed_keys))

    # Split small DataFrame
    small_skewed = small_df.filter(F.col(join_key).isin(skewed_keys))
    small_normal = small_df.filter(~F.col(join_key).isin(skewed_keys))

    # Process normal join with broadcast
    normal_result = large_normal.join(
        broadcast(small_normal),
        join_key
    )

    # Process skewed join with salting or BHJ if small enough
    if small_skewed.count() < 1000:
        # Small enough for broadcast
        skewed_result = large_skewed.join(
            broadcast(small_skewed),
            join_key
        )
    else:
        # Use salting
        skewed_result = salted_join(
            large_skewed,
            small_skewed,
            join_key,
            skewed_keys=skewed_keys
        )

    # Union results
    return normal_result.union(skewed_result)

# Usage
result = isolated_skew_join(orders_df, customers_df, "customer_id")
```

**Handling Strategy 3: Adaptive Query Execution (Spark 3.0+)**

```python
# Enable AQE with skew join optimization
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")

# Spark automatically handles skew
result = large_df.join(small_df, "customer_id")

# Monitor skew handling
result.explain(mode="extended")
```

**Handling Strategy 4: Bucketing**

```python
# Pre-bucket tables for repeated joins
large_df.write.format("parquet") \
    .bucketBy(200, "customer_id") \
    .sortBy("customer_id") \
    .mode("overwrite") \
    .saveAsTable("orders_bucketed")

small_df.write.format("parquet") \
    .bucketBy(200, "customer_id") \
    .sortBy("customer_id") \
    .mode("overwrite") \
    .saveAsTable("customers_bucketed")

# Join bucketed tables (no shuffle!)
orders = spark.table("orders_bucketed")
customers = spark.table("customers_bucketed")
result = orders.join(customers, "customer_id")

# Verify no shuffle in plan
result.explain()
# Should show "SortMergeJoin" without "Exchange" (shuffle)
```

**Real-world Example:**

```python
# Complete pipeline with skew handling
def process_orders_with_skew_handling():
    # Read data
    orders = spark.read.parquet("s3://bucket/orders/")
    customers = spark.read.parquet("s3://bucket/customers/")

    # Detect skew
    is_skewed, skewed_keys = detect_skew(orders, "customer_id", threshold_ratio=10)

    if is_skewed:
        print("Applying skew handling...")
        result = isolated_skew_join(
            orders,
            customers,
            "customer_id",
            skew_threshold=100000
        )
    else:
        print("No skew detected, using broadcast join...")
        result = orders.join(broadcast(customers), "customer_id")

    # Validate result
    print(f"Result count: {result.count():,}")

    # Check for data loss
    original_count = orders.count()
    result_count = result.count()
    if result_count < original_count * 0.95:  # Lost more than 5%
        print(f"⚠️  Warning: Potential data loss!")
        print(f"  Original: {original_count:,}")
        print(f"  Result: {result_count:,}")

    return result

# Execute
final_result = process_orders_with_skew_handling()
```

---

## Part 5: Postgres & Data Warehousing

### Question:
Let's talk about Postgres. When would you use Postgres vs Snowflake for analytical workloads, and how do you optimize Postgres for OLAP queries?

### Answer:
Great question. This is about choosing the right tool for the job.

**Postgres vs Snowflake Decision Matrix:**

```
Use Postgres when:
✓ Data volume < 1TB
✓ Need strong transactional guarantees (ACID)
✓ Require custom extensions (PostGIS, pg_vector, TimescaleDB)
✓ Low query concurrency (< 20 concurrent users)
✓ Hybrid OLTP/OLAP workload
✓ Cost-sensitive (single instance vs cloud DW pricing)
✓ Need fine-grained row-level security
✓ Real-time updates to analytical data

Use Snowflake when:
✓ Data volume > 1TB (multi-TB to PB scale)
✓ High query concurrency (100s of users)
✓ Pure OLAP workload
✓ Need instant elasticity
✓ Multi-tenant data sharing
✓ Separation of storage and compute
✓ Zero-maintenance scaling
✓ Time-travel and cloning features
```

**Optimizing Postgres for OLAP:**

```sql
-- 1. Table Design for Analytics
CREATE TABLE fact_sales (
    sale_id BIGSERIAL,
    customer_id INT,
    product_id INT,
    sale_date DATE,
    amount NUMERIC(18,2),
    quantity INT,
    region VARCHAR(50),

    PRIMARY KEY (sale_id, sale_date)  -- Composite key for partitioning
) PARTITION BY RANGE (sale_date);

-- Create monthly partitions
CREATE TABLE fact_sales_2025_01 PARTITION OF fact_sales
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE fact_sales_2025_02 PARTITION OF fact_sales
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- 2. Columnar Storage with Citus (for large tables)
-- Install citus extension
CREATE EXTENSION citus;

-- Convert table to columnar format
SELECT alter_table_set_access_method('fact_sales_2025_01', 'columnar');

-- 3. Indexes for OLAP
-- BRIN indexes for range queries on sorted data
CREATE INDEX idx_sale_date_brin ON fact_sales USING BRIN (sale_date);

-- B-tree for high-cardinality lookups
CREATE INDEX idx_customer ON fact_sales (customer_id);

-- Covering index for common queries
CREATE INDEX idx_sales_analytics ON fact_sales (sale_date, region)
INCLUDE (amount, quantity);

-- Partial index for hot data
CREATE INDEX idx_recent_sales ON fact_sales (sale_date)
WHERE sale_date >= CURRENT_DATE - INTERVAL '90 days';

-- 4. Materialized Views for Aggregations
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT
    sale_date,
    region,
    SUM(amount) as total_amount,
    SUM(quantity) as total_quantity,
    COUNT(*) as transaction_count,
    AVG(amount) as avg_amount
FROM fact_sales
GROUP BY sale_date, region
WITH DATA;

-- Create index on materialized view
CREATE INDEX idx_mv_daily_sales ON mv_daily_sales (sale_date, region);

-- Refresh strategy
CREATE OR REPLACE FUNCTION refresh_daily_sales()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
END;
$$ LANGUAGE plpgsql;

-- Schedule refresh (use pg_cron extension)
CREATE EXTENSION pg_cron;
SELECT cron.schedule('refresh-daily-sales', '0 1 * * *',
    'SELECT refresh_daily_sales()');

-- 5. Configuration for OLAP Workloads
-- postgresql.conf optimizations
```

```ini
# Memory Configuration
shared_buffers = 16GB                # 25% of RAM
effective_cache_size = 48GB          # 75% of RAM
work_mem = 256MB                     # Per operation
maintenance_work_mem = 2GB           # For VACUUM, CREATE INDEX

# Query Planner
random_page_cost = 1.1               # For SSD
effective_io_concurrency = 200       # For SSD/NVMe
default_statistics_target = 100      # More detailed stats

# Parallelism
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_worker_processes = 8

# Write-Ahead Log (less critical for OLAP)
wal_buffers = 16MB
checkpoint_timeout = 30min
checkpoint_completion_target = 0.9

# Query Optimization
enable_partitionwise_join = on
enable_partitionwise_aggregate = on
jit = on                             # Just-in-time compilation
```

```sql
-- 6. Query Optimization Techniques

-- Bad: Full table scan
SELECT COUNT(*) FROM fact_sales WHERE sale_date >= '2025-01-01';

-- Good: Partition pruning
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM fact_sales WHERE sale_date >= '2025-01-01';
-- Verify only relevant partitions scanned

-- Bad: Correlated subquery
SELECT
    c.customer_name,
    (SELECT SUM(amount) FROM fact_sales WHERE customer_id = c.customer_id)
FROM customers c;

-- Good: JOIN with aggregation
SELECT
    c.customer_name,
    COALESCE(s.total_amount, 0)
FROM customers c
LEFT JOIN (
    SELECT customer_id, SUM(amount) as total_amount
    FROM fact_sales
    GROUP BY customer_id
) s ON c.customer_id = s.customer_id;

-- 7. Window Functions for Analytics
SELECT
    sale_date,
    region,
    amount,
    -- Running total
    SUM(amount) OVER (
        PARTITION BY region
        ORDER BY sale_date
    ) as running_total,
    -- Moving average
    AVG(amount) OVER (
        PARTITION BY region
        ORDER BY sale_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7day,
    -- Rank
    RANK() OVER (
        PARTITION BY sale_date
        ORDER BY amount DESC
    ) as daily_rank
FROM fact_sales;

-- 8. Statistics and VACUUM
-- Analyze tables regularly
ANALYZE fact_sales;

-- Auto-vacuum configuration
ALTER TABLE fact_sales SET (
    autovacuum_analyze_scale_factor = 0.05,
    autovacuum_vacuum_scale_factor = 0.1
);

-- Monitor bloat
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_live_tup,
    n_dead_tup,
    ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- 9. Connection Pooling
-- Use PgBouncer for connection pooling
-- pgbouncer.ini
[databases]
analytics = host=localhost dbname=warehouse

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
reserve_pool_size = 5

-- 10. Foreign Data Wrappers for Federation
CREATE EXTENSION postgres_fdw;

CREATE SERVER snowflake_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'snowflake.example.com', dbname 'warehouse', port '5432');

CREATE USER MAPPING FOR CURRENT_USER
SERVER snowflake_server
OPTIONS (user 'etl_user', password 'password');

CREATE FOREIGN TABLE external_sales (
    sale_id BIGINT,
    amount NUMERIC,
    sale_date DATE
) SERVER snowflake_server
OPTIONS (schema_name 'public', table_name 'sales');

-- Query across local and remote
SELECT
    local.region,
    COUNT(DISTINCT local.customer_id) as local_customers,
    SUM(external.amount) as external_revenue
FROM fact_sales local
JOIN external_sales external ON local.sale_date = external.sale_date
GROUP BY local.region;
```

**Hybrid Architecture Example:**

```python
# Use Postgres for real-time, Snowflake for historical
class HybridDataWarehouse:
    def __init__(self):
        self.pg_conn = psycopg2.connect(
            "postgresql://localhost/realtime_dw"
        )
        self.sf_conn = snowflake.connector.connect(
            user='user',
            account='account',
            warehouse='compute_wh'
        )

    def query_recent_data(self, days=7):
        """Query last N days from Postgres"""
        with self.pg_conn.cursor() as cur:
            cur.execute("""
                SELECT sale_date, SUM(amount)
                FROM fact_sales
                WHERE sale_date >= CURRENT_DATE - %s
                GROUP BY sale_date
            """, (days,))
            return cur.fetchall()

    def query_historical_data(self, start_date):
        """Query historical data from Snowflake"""
        with self.sf_conn.cursor() as cur:
            cur.execute("""
                SELECT sale_date, SUM(amount)
                FROM fact_sales
                WHERE sale_date < CURRENT_DATE - 7
                  AND sale_date >= %s
                GROUP BY sale_date
            """, (start_date,))
            return cur.fetchall()

    def unified_query(self, start_date):
        """Combine Postgres and Snowflake data"""
        recent = self.query_recent_data()
        historical = self.query_historical_data(start_date)

        # Merge and return
        all_data = historical + recent
        return sorted(all_data, key=lambda x: x[0])
```

---

## Part 6: Data Quality & Monitoring

### Question:
Data quality is critical in ETL pipelines. How do you implement comprehensive data quality checks and monitoring?

### Answer:
Absolutely critical. I implement data quality at multiple layers:

**Layer 1: Schema Validation**

```python
# Using Great Expectations
import great_expectations as ge
from great_expectations.dataset import SparkDFDataset

def validate_schema(df, expectations_suite):
    """Validate DataFrame against expectations"""
    ge_df = SparkDFDataset(df)

    # Define expectations
    expectations = {
        "expect_column_to_exist": ["customer_id", "amount", "sale_date"],
        "expect_column_values_to_not_be_null": ["customer_id", "amount"],
        "expect_column_values_to_be_between": {
            "amount": {"min_value": 0, "max_value": 1000000}
        },
        "expect_column_values_to_be_of_type": {
            "customer_id": "IntegerType",
            "amount": "DecimalType"
        },
        "expect_column_values_to_match_regex": {
            "email": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        }
    }

    results = ge_df.validate(expectation_suite=expectations_suite)

    if not results["success"]:
        failed_expectations = [
            exp for exp in results["results"]
            if not exp["success"]
        ]
        raise ValueError(f"Validation failed: {failed_expectations}")

    return results

# AWS Glue Data Quality
glue_dq_ruleset = """
Rules = [
    ColumnCount = 10,
    IsComplete "customer_id",
    IsUnique "transaction_id",
    ColumnValues "amount" >= 0,
    ColumnValues "sale_date" >= (current_date - 365),
    Completeness "email" > 0.95,
    Uniqueness "email" > 0.99,
    CustomSql "SELECT COUNT(*) FROM primary WHERE status NOT IN ('active', 'inactive')" = 0
]
"""
```

**Layer 2: Data Profiling**

```python
from pyspark.sql import functions as F

def profile_dataframe(df, sample_fraction=0.1):
    """Generate comprehensive data profile"""

    # Basic stats
    row_count = df.count()
    col_count = len(df.columns)

    profile = {
        "row_count": row_count,
        "column_count": col_count,
        "columns": {}
    }

    # Sample for profiling
    sample_df = df.sample(fraction=sample_fraction)

    for col in df.columns:
        col_type = df.schema[col].dataType

        col_profile = {
            "type": str(col_type),
            "null_count": df.filter(F.col(col).isNull()).count(),
            "null_percentage": (
                df.filter(F.col(col).isNull()).count() / row_count * 100
            ),
            "distinct_count": df.select(col).distinct().count()
        }

        # Numeric columns
        if str(col_type) in ["IntegerType", "LongType", "DoubleType", "DecimalType"]:
            stats = df.select(
                F.min(col).alias("min"),
                F.max(col).alias("max"),
                F.avg(col).alias("mean"),
                F.stddev(col).alias("stddev"),
                F.expr(f"percentile_approx({col}, 0.5)").alias("median")
            ).collect()[0]

            col_profile.update({
                "min": stats["min"],
                "max": stats["max"],
                "mean": stats["mean"],
                "stddev": stats["stddev"],
                "median": stats["median"]
            })

        # String columns
        elif str(col_type) == "StringType":
            col_profile.update({
                "min_length": df.select(F.min(F.length(col))).collect()[0][0],
                "max_length": df.select(F.max(F.length(col))).collect()[0][0],
                "avg_length": df.select(F.avg(F.length(col))).collect()[0][0]
            })

        profile["columns"][col] = col_profile

    return profile

# Store profile for comparison
import json
profile = profile_dataframe(df)
with open("s3://bucket/profiles/daily_profile.json", "w") as f:
    json.dump(profile, f)
```

**Layer 3: Reconciliation**

```python
def reconcile_data(source_df, target_df, key_columns, value_columns):
    """Reconcile source and target data"""

    # Count reconciliation
    source_count = source_df.count()
    target_count = target_df.count()

    reconciliation = {
        "source_count": source_count,
        "target_count": target_count,
        "count_diff": abs(source_count - target_count),
        "count_match": source_count == target_count
    }

    # Key reconciliation
    source_keys = source_df.select(key_columns).distinct()
    target_keys = target_df.select(key_columns).distinct()

    missing_in_target = source_keys.subtract(target_keys).count()
    extra_in_target = target_keys.subtract(source_keys).count()

    reconciliation.update({
        "missing_in_target": missing_in_target,
        "extra_in_target": extra_in_target,
        "key_match": missing_in_target == 0 and extra_in_target == 0
    })

    # Value reconciliation (for matching keys)
    joined = source_df.alias("src").join(
        target_df.alias("tgt"),
        key_columns,
        "inner"
    )

    value_mismatches = 0
    for col in value_columns:
        mismatches = joined.filter(
            F.col(f"src.{col}") != F.col(f"tgt.{col}")
        ).count()
        value_mismatches += mismatches
        reconciliation[f"{col}_mismatches"] = mismatches

    reconciliation["value_match"] = value_mismatches == 0
    reconciliation["overall_match"] = (
        reconciliation["count_match"] and
        reconciliation["key_match"] and
        reconciliation["value_match"]
    )

    return reconciliation

# Usage
recon = reconcile_data(
    source_df=source_df,
    target_df=snowflake_df,
    key_columns=["transaction_id"],
    value_columns=["amount", "quantity", "status"]
)

if not recon["overall_match"]:
    send_alert(f"Reconciliation failed: {recon}")
```

**Layer 4: Anomaly Detection**

```python
def detect_anomalies(current_metrics, historical_metrics, threshold_std=3):
    """Detect anomalies in current data vs historical patterns"""

    import numpy as np

    anomalies = []

    for metric, current_value in current_metrics.items():
        if metric in historical_metrics:
            hist_values = historical_metrics[metric]
            mean = np.mean(hist_values)
            std = np.std(hist_values)

            # Z-score
            z_score = abs(current_value - mean) / std if std > 0 else 0

            if z_score > threshold_std:
                anomalies.append({
                    "metric": metric,
                    "current_value": current_value,
                    "expected_mean": mean,
                    "expected_std": std,
                    "z_score": z_score,
                    "severity": "high" if z_score > 5 else "medium"
                })

    return anomalies

# Example usage
current = {
    "row_count": 1500000,  # Usually ~1M
    "null_percentage_email": 0.15,  # Usually ~0.05
    "avg_amount": 125.50
}

historical = {
    "row_count": [980000, 1020000, 995000, 1010000],
    "null_percentage_email": [0.04, 0.05, 0.045, 0.048],
    "avg_amount": [123.20, 124.50, 122.80, 125.00]
}

anomalies = detect_anomalies(current, historical)
if anomalies:
    send_alert(f"Anomalies detected: {anomalies}")
```

**Layer 5: Monitoring & Alerting**

```python
import boto3
from datetime import datetime

class ETLMonitor:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.sns = boto3.client('sns')

    def log_metric(self, metric_name, value, unit='None', dimensions=None):
        """Log custom metric to CloudWatch"""
        self.cloudwatch.put_metric_data(
            Namespace='ETL/DataQuality',
            MetricData=[{
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow(),
                'Dimensions': dimensions or []
            }]
        )

    def log_pipeline_metrics(self, pipeline_name, metrics):
        """Log comprehensive pipeline metrics"""
        dimensions = [{'Name': 'Pipeline', 'Value': pipeline_name}]

        self.log_metric('RowsProcessed', metrics['rows_processed'],
                       'Count', dimensions)
        self.log_metric('DurationSeconds', metrics['duration'],
                       'Seconds', dimensions)
        self.log_metric('ErrorCount', metrics['error_count'],
                       'Count', dimensions)
        self.log_metric('DataQualityScore', metrics['dq_score'],
                       'Percent', dimensions)

    def send_alert(self, subject, message, severity='INFO'):
        """Send SNS alert"""
        topic_arn = 'arn:aws:sns:us-east-1:123456789:etl-alerts'

        self.sns.publish(
            TopicArn=topic_arn,
            Subject=f"[{severity}] {subject}",
            Message=message,
            MessageAttributes={
                'severity': {'DataType': 'String', 'StringValue': severity}
            }
        )

# Usage in ETL pipeline
monitor = ETLMonitor()

try:
    start_time = time.time()

    # Run ETL
    df = extract_data()
    df_transformed = transform_data(df)
    load_data(df_transformed)

    duration = time.time() - start_time

    # Log success metrics
    monitor.log_pipeline_metrics('daily_sales_etl', {
        'rows_processed': df_transformed.count(),
        'duration': duration,
        'error_count': 0,
        'dq_score': 99.5
    })

except Exception as e:
    monitor.send_alert(
        'ETL Pipeline Failed',
        f'Pipeline daily_sales_etl failed: {str(e)}',
        'CRITICAL'
    )
    raise
```

**Layer 6: Data Lineage**

```python
# Using AWS Glue Data Catalog
def register_lineage(source_tables, target_table, transformation_logic):
    """Register data lineage in Glue Data Catalog"""
    glue = boto3.client('glue')

    lineage_metadata = {
        'source_tables': source_tables,
        'target_table': target_table,
        'transformation': transformation_logic,
        'timestamp': datetime.utcnow().isoformat(),
        'etl_job': 'daily_sales_etl',
        'version': '1.0'
    }

    glue.update_table(
        DatabaseName='warehouse',
        TableInput={
            'Name': target_table,
            'Parameters': {
                'lineage': json.dumps(lineage_metadata)
            }
        }
    )
```

This comprehensive approach ensures data quality, detectability, and trust in the pipeline.

---

## Part 7: Advanced Topics & Best Practices

### Question:
Final section. Let's talk about some advanced scenarios. How would you handle CDC (Change Data Capture) from an operational Postgres database to Snowflake?

### Answer:
CDC is crucial for keeping data warehouses in sync with operational systems. Here's my comprehensive approach:

**Architecture Overview:**

```
Postgres (OLTP) → Debezium → Kafka → Spark Streaming → S3 → Snowflake
                   (CDC)              (Transform)      (Stage)  (DW)
```

**Implementation:**

```yaml
# 1. Debezium Connector Configuration
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnector
metadata:
  name: postgres-cdc-connector
spec:
  class: io.debezium.connector.postgresql.PostgresConnector
  tasksMax: 1
  config:
    database.hostname: postgres.example.com
    database.port: 5432
    database.user: debezium
    database.password: ${POSTGRES_PASSWORD}
    database.dbname: production
    database.server.name: prod-db

    # CDC Configuration
    plugin.name: pgoutput
    slot.name: debezium_slot
    publication.name: debezium_publication

    # Tables to track
    table.include.list: public.customers,public.orders,public.products

    # Snapshot mode
    snapshot.mode: initial

    # Message format
    transforms: unwrap
    transforms.unwrap.type: io.debezium.transforms.ExtractNewRecordState
    transforms.unwrap.drop.tombstones: false
    transforms.unwrap.delete.handling.mode: rewrite

    # Kafka topic
    topic.prefix: cdc
```

```sql
-- 2. Postgres Setup for CDC
-- Enable logical replication
ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET max_wal_senders = 10;
-- Restart Postgres

-- Create replication user
CREATE ROLE debezium WITH REPLICATION LOGIN PASSWORD 'password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium;
GRANT USAGE ON SCHEMA public TO debezium;

-- Create publication
CREATE PUBLICATION debezium_publication FOR TABLE
    customers, orders, products;

-- Monitor replication slot
SELECT * FROM pg_replication_slots;
SELECT * FROM pg_stat_replication;
```

```python
# 3. Spark Streaming Consumer
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

def process_cdc_stream():
    spark = SparkSession.builder \
        .appName("CDC-Processor") \
        .config("spark.sql.streaming.checkpointLocation",
                "s3://bucket/checkpoints/cdc/") \
        .getOrCreate()

    # Read from Kafka
    cdc_stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "cdc.public.customers,cdc.public.orders") \
        .option("startingOffsets", "earliest") \
        .option("maxOffsetsPerTrigger", 10000) \
        .load()

    # Define schema for CDC events
    cdc_schema = StructType([
        StructField("before", StringType(), True),
        StructField("after", StringType(), True),
        StructField("op", StringType(), False),  # c, u, d, r
        StructField("ts_ms", LongType(), False),
        StructField("source", StructType([
            StructField("table", StringType(), False),
            StructField("lsn", LongType(), True)
        ]))
    ])

    # Parse CDC events
    parsed_stream = cdc_stream.select(
        col("topic"),
        col("partition"),
        col("offset"),
        col("timestamp"),
        from_json(col("value").cast("string"), cdc_schema).alias("data")
    )

    # Extract table and operation
    processed_stream = parsed_stream.select(
        col("data.source.table").alias("table_name"),
        col("data.op").alias("operation"),
        col("data.after").alias("record"),
        col("data.ts_ms").alias("event_time"),
        current_timestamp().alias("processing_time")
    )

    # Route to different sinks by table
    def process_table_cdc(batch_df, batch_id):
        tables = batch_df.select("table_name").distinct().collect()

        for row in tables:
            table = row["table_name"]
            table_df = batch_df.filter(col("table_name") == table)

            # Write to S3 partitioned by table and date
            table_df.write \
                .format("delta") \
                .mode("append") \
                .partitionBy("table_name", "event_date") \
                .save(f"s3://bucket/cdc-staging/")

            # Optionally trigger Snowpipe
            trigger_snowpipe(table, batch_id)

    # Write stream
    query = processed_stream \
        .withColumn("event_date",
                   to_date(from_unixtime(col("event_time") / 1000))) \
        .writeStream \
        .foreachBatch(process_table_cdc) \
        .outputMode("append") \
        .trigger(processingTime='1 minute') \
        .start()

    query.awaitTermination()
```

```python
# 4. Apply CDC to Snowflake with MERGE
def apply_cdc_to_snowflake(table_name, cdc_path):
    """
    Apply CDC changes to Snowflake table
    """

    snowflake_query = f"""
    MERGE INTO {table_name} target
    USING (
        SELECT
            record:id::NUMBER as id,
            record:name::VARCHAR as name,
            record:email::VARCHAR as email,
            record:updated_at::TIMESTAMP as updated_at,
            operation
        FROM @cdc_stage/{table_name}/
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY record:id
            ORDER BY event_time DESC
        ) = 1
    ) source
    ON target.id = source.id
    WHEN MATCHED AND source.operation = 'd' THEN
        DELETE
    WHEN MATCHED AND source.operation IN ('u', 'c', 'r') THEN
        UPDATE SET
            target.name = source.name,
            target.email = source.email,
            target.updated_at = source.updated_at,
            target._cdc_timestamp = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED AND source.operation IN ('c', 'r') THEN
        INSERT (id, name, email, updated_at, _cdc_timestamp)
        VALUES (source.id, source.name, source.email,
                source.updated_at, CURRENT_TIMESTAMP());
    """

    # Execute via Snowflake connector or Task
    execute_snowflake_query(snowflake_query)

# 5. Snowflake Task for Automated CDC Processing
create_task_sql = """
CREATE OR REPLACE TASK apply_customers_cdc
  WAREHOUSE = CDC_WH
  SCHEDULE = '1 MINUTE'
WHEN
  SYSTEM$STREAM_HAS_DATA('customers_cdc_stream')
AS
  CALL sp_apply_cdc('customers');
"""
```

**Handling Schema Evolution in CDC:**

```python
def handle_schema_evolution(old_schema, new_schema, data):
    """Handle schema changes in CDC stream"""

    # Detect new columns
    old_cols = set(old_schema.fieldNames())
    new_cols = set(new_schema.fieldNames())

    added_cols = new_cols - old_cols
    removed_cols = old_cols - new_cols

    if added_cols:
        # Add columns with null defaults
        for col in added_cols:
            data = data.withColumn(col, lit(None))

    if removed_cols:
        # Log warning but continue
        logging.warning(f"Columns removed: {removed_cols}")

    # Detect type changes
    for field in new_schema.fields:
        if field.name in old_schema.fieldNames():
            old_type = old_schema[field.name].dataType
            new_type = field.dataType

            if old_type != new_type:
                # Handle type conversion
                logging.warning(
                    f"Type change detected: {field.name} "
                    f"{old_type} -> {new_type}"
                )

    return data
```

**Monitoring CDC Pipeline:**

```python
def monitor_cdc_lag():
    """Monitor CDC replication lag"""

    # Check Kafka consumer lag
    from kafka import KafkaConsumer

    consumer = KafkaConsumer(
        bootstrap_servers=['kafka:9092'],
        group_id='cdc-spark-consumer'
    )

    lag_metrics = {}

    for topic_partition in consumer.assignment():
        committed = consumer.committed(topic_partition)
        end_offset = consumer.end_offsets([topic_partition])[topic_partition]

        lag = end_offset - committed if committed else end_offset
        lag_metrics[topic_partition.topic] = lag

    # Alert if lag > threshold
    for topic, lag in lag_metrics.items():
        if lag > 100000:
            send_alert(
                f"High CDC lag detected",
                f"Topic {topic} has {lag:,} messages behind"
            )

    # Check Postgres replication slot lag
    pg_lag_query = """
        SELECT
            slot_name,
            pg_size_pretty(
                pg_current_wal_lsn() - confirmed_flush_lsn
            ) as replication_lag
        FROM pg_replication_slots
        WHERE slot_name = 'debezium_slot';
    """

    # Log to CloudWatch
    cloudwatch.put_metric_data(
        Namespace='CDC',
        MetricData=[{
            'MetricName': 'KafkaLag',
            'Value': sum(lag_metrics.values()),
            'Unit': 'Count'
        }]
    )
```

This provides real-time, reliable CDC with monitoring and error handling.

### Question:
Excellent! Last question: What are the key cost optimization strategies you'd implement for this entire stack—AWS, Spark, Snowflake, and Postgres?

### Answer:
Cost optimization is critical at scale. Here's my comprehensive strategy:

**AWS S3 Optimization:**

```python
# 1. Intelligent tiering
s3_lifecycle = {
    "Rules": [{
        "Id": "IntelligentTiering",
        "Status": "Enabled",
        "Transitions": [
            {"Days": 30, "StorageClass": "INTELLIGENT_TIERING"},
            {"Days": 90, "StorageClass": "GLACIER"},
            {"Days": 365, "StorageClass": "DEEP_ARCHIVE"}
        ],
        "NoncurrentVersionTransitions": [
            {"NoncurrentDays": 30, "StorageClass": "GLACIER"}
        ]
    }]
}

# 2. Optimize file sizes (larger files = fewer API calls)
# Target: 128MB - 1GB per file

# 3. Use S3 Select for filtering
# Saves on data transfer and processing costs

# 4. Enable S3 request metrics to identify hotspots
```

**EMR/Spark Optimization:**

```python
# 1. Use Spot Instances (70-90% cost savings)
emr_config = {
    "InstanceGroups": [
        {
            "Name": "Master",
            "Market": "ON_DEMAND",
            "InstanceRole": "MASTER",
            "InstanceType": "r5.xlarge",
            "InstanceCount": 1
        },
        {
            "Name": "Core",
            "Market": "SPOT",
            "InstanceRole": "CORE",
            "InstanceType": "r5.2xlarge",
            "InstanceCount": 2,
            "BidPrice": "OnDemandPrice"
        },
        {
            "Name": "Task",
            "Market": "SPOT",
            "InstanceRole": "TASK",
            "InstanceType": "r5.4xlarge",
            "InstanceCount": 10,
            "BidPrice": "OnDemandPrice"
        }
    ],
    "AutoTerminationPolicy": {
        "IdleTimeout": 900  # Terminate after 15 min idle
    }
}

# 2. Right-size instances based on workload
# Memory-intensive: r5 family
# Compute-intensive: c5 family
# Balanced: m5 family

# 3. Use Graviton instances (20% cost savings)
# r6g, m6g, c6g families

# 4. Enable auto-scaling
scaling_policy = {
    "MinCapacity": 2,
    "MaxCapacity": 50,
    "Rules": [{
        "Name": "ScaleUp",
        "Trigger": {
            "CloudWatchAlarmDefinition": {
                "MetricName": "YARNMemoryAvailablePercentage",
                "Threshold": 15,
                "ComparisonOperator": "LESS_THAN"
            }
        },
        "Action": {
            "SimpleScalingPolicyConfiguration": {
                "ScalingAdjustment": 5,
                "CoolDown": 300
            }
        }
    }]
}

# 5. Use AWS Glue instead of EMR for simple jobs
# Serverless, pay per second, auto-scaling
```

**Snowflake Optimization:**

```sql
-- 1. Right-size warehouses
-- Start small, scale up only when needed
CREATE WAREHOUSE etl_small WITH
    WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 60        -- 1 minute
    AUTO_RESUME = TRUE
    SCALING_POLICY = 'ECONOMY';

-- Use multi-cluster only for high concurrency
CREATE WAREHOUSE analytics_wh WITH
    WAREHOUSE_SIZE = 'LARGE'
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 3
    SCALING_POLICY = 'ECONOMY';  -- Favor cost over speed

-- 2. Cluster tables for query performance
ALTER TABLE fact_sales CLUSTER BY (sale_date, region);

-- Monitor clustering depth
SELECT SYSTEM$CLUSTERING_INFORMATION('fact_sales', '(sale_date, region)');

-- 3. Use materialized views sparingly
-- They consume storage and compute for refresh

-- 4. Leverage zero-copy cloning instead of duplicating
CREATE DATABASE dev_db CLONE prod_db;

-- 5. Query optimization
-- Use RESULT_SCAN to avoid re-running expensive queries
SELECT * FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));

-- 6. Monitor query performance
SELECT
    query_id,
    warehouse_name,
    warehouse_size,
    execution_time / 1000 as execution_seconds,
    bytes_scanned,
    credits_used_cloud_services
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE execution_time > 60000  -- Queries > 1 minute
ORDER BY credits_used_cloud_services DESC
LIMIT 100;

-- 7. Set resource monitors
CREATE RESOURCE MONITOR monthly_limit WITH
    CREDIT_QUOTA = 10000
    TRIGGERS
        ON 75 PERCENT DO NOTIFY
        ON 100 PERCENT DO SUSPEND;

ALTER WAREHOUSE etl_wh SET RESOURCE_MONITOR = monthly_limit;

-- 8. Use transient tables for temporary data
CREATE TRANSIENT TABLE staging_data (...);
-- No Fail-safe = lower storage costs

-- 9. Optimize storage
-- Partition pruning
SELECT * FROM fact_sales WHERE sale_date = '2025-12-27';

-- Column pruning
SELECT id, amount FROM fact_sales;  -- Not SELECT *

-- 10. Query acceleration service (for reporting workloads)
ALTER WAREHOUSE reporting_wh SET ENABLE_QUERY_ACCELERATION = TRUE;
ALTER WAREHOUSE reporting_wh SET QUERY_ACCELERATION_MAX_SCALE_FACTOR = 8;
```

**Postgres Optimization:**

```sql
-- 1. Use appropriate instance size
-- Start with db.t3.large, scale up as needed

-- 2. Use Aurora Serverless for variable workloads
-- Auto-scales capacity, pay per second

-- 3. Optimize storage
-- Enable storage auto-scaling
-- Use gp3 instead of gp2 (20% cost savings)

-- 4. Use read replicas for analytics
-- Offload reporting queries from primary

-- 5. Implement connection pooling
-- Reduce instance size needed

-- 6. Archive old data
-- Move to S3 using AWS DMS or Glue

-- 7. Monitor unused indexes
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
    AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Drop unused indexes
```

**Cross-Platform Optimization:**

```python
# 1. Data lifecycle management
def optimize_data_lifecycle():
    """Move data through tiers based on access patterns"""

    # Recent data (7 days): Postgres + Snowflake
    # Warm data (7-90 days): Snowflake
    # Cold data (90-365 days): Snowflake on cheaper storage tier
    # Archive (>365 days): S3 Glacier

    lifecycle_policy = {
        "recent": {
            "storage": ["postgres", "snowflake"],
            "retention_days": 7,
            "query_pattern": "real-time analytics"
        },
        "warm": {
            "storage": ["snowflake"],
            "retention_days": 90,
            "query_pattern": "regular reporting"
        },
        "cold": {
            "storage": ["snowflake_archived"],
            "retention_days": 365,
            "query_pattern": "occasional analysis"
        },
        "archive": {
            "storage": ["s3_glacier"],
            "retention_days": 2555,  # 7 years
            "query_pattern": "compliance/audit"
        }
    }

# 2. Cost monitoring dashboard
def create_cost_dashboard():
    """Unified cost monitoring"""

    costs = {
        "s3_storage": get_s3_costs(),
        "s3_requests": get_s3_request_costs(),
        "emr_compute": get_emr_costs(),
        "snowflake_compute": get_snowflake_compute_costs(),
        "snowflake_storage": get_snowflake_storage_costs(),
        "postgres_instance": get_rds_costs(),
        "data_transfer": get_transfer_costs()
    }

    total_cost = sum(costs.values())

    # Set up alerts
    if total_cost > monthly_budget * 0.8:
        send_alert(f"Cost alert: ${total_cost:.2f} / ${monthly_budget:.2f}")

    return costs

# 3. Query cost attribution
def track_query_costs():
    """Tag queries with team/project for chargeback"""

    # Snowflake
    query = """
    SELECT * FROM sales
    /* QUERY_TAG: {"team": "analytics", "project": "dashboard"} */
    """

    # Track in cost table
    log_query_cost(team="analytics", project="dashboard", cost=0.15)
```

**Expected Cost Savings:**
- S3: 30-40% (lifecycle, file optimization)
- EMR: 60-70% (spot instances, right-sizing, auto-scaling)
- Snowflake: 40-50% (warehouse sizing, query optimization, auto-suspend)
- Postgres: 25-35% (right-sizing, read replicas, Aurora Serverless)
- **Overall: 40-50% cost reduction**

---

## Conclusion

### Question:
Thank you so much for the comprehensive responses. You've demonstrated deep expertise across the entire ETL stack—from AWS services and S3 optimization, to Spark performance tuning, Snowflake best practices, and Postgres analytics optimization. Your understanding of data quality, CDC, and cost optimization shows you think holistically about data engineering. We'll be in touch soon!

### Answer:
Thank you for the opportunity! I really enjoyed diving deep into these topics. Building robust, performant, and cost-effective ETL pipelines is something I'm passionate about, and I'd love to bring that expertise to your team. Looking forward to hearing from you!

---

## Key Topics Covered

1. **General Principles**: Data lakes vs warehouses, Lambda/Kappa architectures
2. **AWS & S3**: Partitioning, file optimization, small file handling, data formats
3. **Snowflake**: Loading strategies (Snowpipe vs COPY), SCDs, performance tuning
4. **Spark**: Large-scale optimization, skew handling, configuration tuning
5. **Postgres**: OLAP optimization, hybrid architectures, partitioning
6. **Data Quality**: Validation, profiling, reconciliation, anomaly detection
7. **Advanced Topics**: CDC implementation, schema evolution, cost optimization

## Technologies Mentioned

- **Cloud**: AWS (S3, EMR, Glue, Lambda, CloudWatch, SNS, SQS)
- **Data Warehouse**: Snowflake, Postgres
- **Processing**: Apache Spark, Spark Structured Streaming
- **Streaming**: Kafka, Debezium
- **Data Quality**: Great Expectations, AWS Glue Data Quality
- **Formats**: Parquet, ORC, Avro, Delta Lake, Iceberg
- **Monitoring**: CloudWatch, pg_stat_user_tables, Snowflake account usage
- **Tools**: PgBouncer, pg_cron, Citus

---
