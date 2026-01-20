# Apache Spark

## Table of Contents

- [Apache Spark](#apache-spark)
  - [Table of Contents](#table-of-contents)
  - [Partitioning & Optimization](#partitioning--optimization)
    - [Repartition vs Coalesce](#repartition-vs-coalesce)
    - [Optimal Spark Cluster's Ideal Partition Size and Number Calculation Methods](#optimal-spark-clusters-ideal-partition-size-and-number-calculation-methods)
    - [Methods for Determining Optimal spark.sql.shuffle.partitions](#methods-for-determining-optimal-sparksqlshufflepartitions)
    - [Spark Broadcast Join Strategies](#spark-broadcast-join-strategies)
    - [Skew Detection Methods](#skew-detection-methods)
    - [Salting in Spark Operations](#salting-in-spark-operations)
    - [AQE vs Manual Salting for Skew Joins](#aqe-vs-manual-salting-for-skew-joins)
    - [Strategies for Avoiding Full Table Scans in Spark Operations](#strategies-for-avoiding-full-table-scans-in-spark-operations)
    - [Strategies for Handling 10TB Data Workloads Using Spark](#strategies-for-handling-10tb-data-workloads-using-spark)
    - [Spark AQE (Adaptive Query Execution) Limitations](#spark-aqe-adaptive-query-execution-limitations)
  - [Spark-Specific Features](#spark-specific-features)
    - [Spark Context Management](#spark-context-management)
    - [Spark Caching (Query-Specific & General)](#spark-caching-query-specific--general)
    - [Spark Checkpoints](#spark-checkpoints)
    - [Assert Spark DataFrame Equality Using Chispa](#assert-spark-dataframe-equality-using-chispa)
    - [JDBC Partitioning Optimization Strategies](#jdbc-partitioning-optimization-strategies)
  - [Scala vs Python for Data Engineering](#scala-vs-python-for-data-engineering)
    - [Scala vs Python Strengths and Weaknesses in Data Engineering](#scala-vs-python-strengths-and-weaknesses-in-data-engineering)
  - [Memory & Performance Tuning](#memory--performance-tuning)
    - [Spark Memory Tuning](#spark-memory-tuning)
    - [Spark Garbage Collection Tuning](#spark-garbage-collection-tuning)
    - [Spark Performance Benchmark](#spark-performance-benchmark)
    - [Spark Accumulators Limitations](#spark-accumulators-limitations)
    - [Spark Listeners](#spark-listeners)

## Partitioning & Optimization

### Repartition vs Coalesce

**Definition**: Repartition shuffles all data across partitions (expensive but enables better distribution); Coalesce combines partitions without shuffle (faster but may cause imbalance).

**External Resources**:

- https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.repartition.html
- https://databricks.com/blog/2021/08/04/adaptive-query-execution-brings-spark-sql-in-line-with-state-of-the-art-databases.html
- https://medium.com/swlh/difference-between-repartition-and-coalesce-in-spark-860a3e3d2c41

### Optimal Spark Cluster's Ideal Partition Size and Number Calculation Methods

**Definition**: Methods for determining optimal partition count based on cluster resources, data size, and workload characteristics (typically 2-4 partitions per core).

**Key Calculation Techniques**:

- **Executor Core Count Heuristic**: Multiply total executor cores by 2-4; baseline formula: Total Partitions = (Num Executors × Cores per Executor) × 2-4 (conservative to aggressive scaling)
- **Data Size Division Method**: Divide total dataset size by target partition size; formula: Partitions = Total Data Size ÷ Partition Size Target (aim for 128-256MB per partition for optimal performance)
- **Task Duration Targeting**: Aim for task execution times between 100ms-1000ms; if average task <100ms, increase partitions; if >5s, decrease to reduce overhead
- **Memory-Constrained Calculation**: Calculate max partitions = (Executor Memory × Memory Fraction) ÷ Expected Per-Task Memory; ensures tasks fit within executor memory without spill
- **Network Bandwidth Limitation**: Estimate available network bandwidth; partitions should allow 500MB-2GB shuffle per executor without network saturation
- **I/O Throughput Analysis**: Determine disk/network I/O capability; match partition count to allow full I/O throughput utilization without bottlenecks
- **Task Scheduling Fairness**: Keep total task count within 10,000-50,000 range; avoid excessive partitions that overwhelm the scheduler or too few that underutilize resources
- **File Size Alignment**: Align partition boundaries with storage block sizes (typically 128-256MB for HDFS/S3); reduces data movement and improves locality
- **Executor Memory per Partition**: Calculate as (Executor Memory × 0.6) ÷ Partition Count; ensure 50-100MB available per partition for processing
- **Cluster Resource Utilization Target**: Design for 80-90% CPU utilization during peak load; too many partitions = scheduling overhead, too few = underutilized cores
- **Data Locality Optimization**: For local data, use partition count matching data node/block count; for remote data, 2-4x core count to enable better scheduling flexibility
- **Shuffle Overhead Estimation**: For shuffle-heavy workloads, reduce partition count by 20-30% to minimize shuffle overhead; for map-only jobs, use full core multiplier
- **Workload Type Assessment**: Batch ETL can use higher partitions (4-8x cores); interactive queries use lower partitions (2-3x cores); streaming uses 1-2x cores
- **Peak Memory Profiling**: Run sample job and track peak executor memory; calculate sustainable partition count = (Peak Memory × 0.75) ÷ Task Memory
- **Iterative Benchmarking Approach**: Start with 2x executor cores, benchmark, then adjust by ±25% increments until performance plateaus; document final value
- **Data Skew Awareness**: For naturally skewed data, use higher partition count (4-8x cores) to distribute concentrated keys more evenly
- **Cost vs Performance Analysis**: Higher partitions = more scheduler overhead and CPU; calculate cost per partition and stop when marginal benefit < cost increase
- **Latency SLA Alignment**: For low-latency requirements (<1s), use lower partition count (1-2x cores) to minimize task queuing; for batch jobs (hours), use higher count
- **Shuffle and Sort Considerations**: For groupBy/join operations, use higher partitions (1000-5000); for sequential scans, use lower partitions (10-100)
- **Production Load Simulation**: Test with 10-20% production load using realistic data size and distribution; extrapolate partition count based on performance metrics

**Recommended Partition Sizing Workflow**:

1. Calculate baseline: Partitions = (Executors × Cores) × 3
2. Calculate partition size: Partition Size = Total Data ÷ Partitions
3. Target: 128-256MB per partition (adjust if outside range)
4. Run benchmark query on 10% sample data
5. Monitor: Task time (target 100ms-1s), executor memory (target <75%), shuffle bytes
6. Adjust partitions: ±20-30% based on metrics
7. Re-run full query and validate performance improvement
8. Lock optimal value once performance stabilizes

**External Resources**:

- https://spark.apache.org/docs/latest/tuning.html
- https://databricks.com/blog/2021/08/04/adaptive-query-execution-brings-spark-sql-in-line-with-state-of-the-art-databases.html
- https://www.youtube.com/watch?v=daXEp4HmS-E

### Methods for Determining Optimal spark.sql.shuffle.partitions

**Definition**: Techniques to set optimal shuffle partition count including benchmarking, heuristics based on cluster size and data volume, and adaptive query execution.

**Key Determination Techniques**:

- **Cluster Core Count Heuristic**: Multiply total executor cores by 2-4 (e.g., 100 cores × 3 = 300 partitions); a common baseline that provides good parallelism without overwhelming resources
- **Data Size-Based Calculation**: Divide total data size by target partition size (e.g., 100GB ÷ 128MB = ~800 partitions); aim for 128-256MB per partition for optimal I/O
- **Adaptive Query Execution (AQE)**: Enable AQE with `spark.sql.adaptive.enabled=true` to let Spark automatically adjust partition count at runtime based on actual data distribution
- **Start with Default and Profile**: Begin with default value (200) and use Spark UI to monitor shuffle metrics, then adjust upward/downward based on task completion times
- **Monitor Shuffle Write Size**: Track "Shuffle Bytes Written" in Spark UI; if consistently >1GB per partition, increase shuffle.partitions; if <100MB, decrease
- **Task Execution Time Analysis**: Examine task duration distribution; if many tasks complete <100ms, increase partitions to improve parallelism; if >30s, decrease to reduce overhead
- **Network Bandwidth Consideration**: Estimate network capacity between executors; shuffle partitions should allow efficient network utilization (target 500MB-2GB shuffle per network hop)
- **Memory Constraints Awareness**: Account for executor memory when setting partitions; more partitions = smaller per-partition memory footprint, reducing OOM risk
- **Benchmarking with Sample Data**: Run representative queries on 10-20% sample data with different partition counts (100, 200, 400, 800) and measure execution time
- **Peak Memory Usage Monitoring**: Set partitions to keep peak memory under 75% of executor memory to avoid spill; use `spark.executor.memory` constraints
- **Shuffle Spill Analysis**: Monitor shuffle spill metrics in Spark UI; high spill indicates too few partitions; adjust upward to reduce spill
- **Stage Completion Time Tracking**: Identify stages with wide transformations (joins, aggregations); use stage metrics to find optimal partition count for that stage
- **Experimentation with Skew**: Account for data skew; use higher partition count for naturally skewed datasets to distribute work more evenly
- **Query Complexity Assessment**: Complex queries with multiple shuffle operations benefit from higher partition counts; simple queries may use lower values
- **Iterative Tuning Process**: Start conservative, measure, then adjust incrementally (100-200 partitions); don't change drastically in single iteration
- **Industry Rule of Thumb**: For most workloads, 2-4 × executor core count works well; for 100GB+ datasets, consider 1000-2000 partitions
- **Time-Series and Streaming Adjustment**: For streaming or time-based queries, partition count should match expected batch size and processing latency SLAs
- **Disk I/O Efficiency**: Consider HDFS/S3 block size; align shuffle partitions with storage block boundaries when possible (typically 128-256MB blocks)
- **Task Scheduler Fairness**: Avoid excessive partitions that create scheduling overhead; keep total task count within 10,000-50,000 for reasonable scheduler latency
- **Cost vs Performance Tradeoff**: Higher partitions increase task scheduling overhead and CPU; lower partitions increase data per task; find sweet spot based on cost constraints

**Recommended Tuning Workflow**:

1. Enable AQE first (`spark.sql.adaptive.enabled=true`) for automatic optimization
2. Baseline with `spark.sql.shuffle.partitions` = 2 × executor cores
3. Run representative query and analyze Spark UI metrics
4. Adjust based on shuffle write size, task time, and spill metrics
5. Re-run and compare execution time to establish improvement
6. Lock optimal value once performance plateaus

**External Resources**:

- https://spark.apache.org/docs/latest/configuration.html#sql-configuration
- https://databricks.com/blog/2021/08/04/adaptive-query-execution-brings-spark-sql-in-line-with-state-of-the-art-databases.html
- https://www.youtube.com/watch?v=daXEp4HmS-E

### Spark Broadcast Join Strategies

**Definition**: Optimization technique broadcasting small DataFrames to all executor nodes, eliminating shuffle for joins and dramatically improving performance for asymmetric joins.

**Determining Optimal Broadcast Size Based on Cluster Hardware**:

1. **Executor Memory Calculation**
   - Base formula: `max_broadcast_size = executor_memory * 0.1 to 0.2`
   - Account for memory overhead: `usable_memory = spark.executor.memory - spark.executor.memoryOverhead`
   - Conservative rule: broadcast table should be < 10% of executor heap

2. **Driver Memory Consideration**
   - Driver must hold entire broadcast table during collection
   - Ensure: `broadcast_size < (spark.driver.memory * 0.3)`
   - Driver collects data before broadcasting, so it's often the bottleneck

3. **Network Bandwidth Factor**
   - Calculate broadcast time: `broadcast_time = table_size / network_bandwidth`
   - Compare against shuffle cost: broadcast wins when `broadcast_time < shuffle_time`
   - For 1Gbps networks: keep broadcasts under 100-200MB for sub-second transfers

4. **Number of Executors Impact**
   - Total cluster broadcast memory = `broadcast_size * num_executors`
   - More executors = more copies = higher aggregate memory usage
   - Formula: `safe_broadcast_size = cluster_total_memory / (num_executors * safety_factor)`

5. **Spark Configuration Thresholds**
   - Default: `spark.sql.autoBroadcastJoinThreshold = 10MB`
   - Recommended max: typically 100MB-1GB depending on cluster
   - Set to -1 to disable auto-broadcast and use explicit hints

6. **Practical Sizing Guidelines**

   | Executor Memory | Recommended Max Broadcast |
   |-----------------|---------------------------|
   | 4GB             | 200-400MB                 |
   | 8GB             | 400-800MB                 |
   | 16GB            | 800MB-1.5GB               |
   | 32GB+           | 1-2GB                     |

7. **Dynamic Assessment Methods**
   - Check DataFrame size before join: `df.cache().count(); spark.catalog.cacheTable()`
   - Use `df.storageLevel` and Spark UI Storage tab to verify actual size
   - Query `spark.sql("ANALYZE TABLE table_name COMPUTE STATISTICS")` for table stats

8. **Memory Pressure Indicators**
   - Monitor GC time in Spark UI (should be < 10% of task time)
   - Watch for OOM errors or excessive spilling to disk
   - Track executor memory usage via metrics or Ganglia/Prometheus

9.  **Formula for Optimal Threshold**
   ```
   optimal_threshold = min(
       executor_memory * 0.15,
       driver_memory * 0.25,
       network_transfer_budget,
       cluster_memory / (num_executors * 3)
   )
   ```

**AQE Automatic Broadcast Join Handling**:

AQE automatically handles broadcast joins through **Dynamic Broadcast Join Conversion**:

1. **Runtime Size Detection**: At compile time, Spark may not know the true size of a table (especially after filters). AQE re-evaluates sizes at runtime after stages complete.

2. **Dynamic Conversion**: If a table's runtime size falls below `spark.sql.autoBroadcastJoinThreshold` (default 10MB), AQE converts a sort-merge join to a broadcast hash join mid-execution.

3. **Configuration**:
   ```python
   spark.conf.set("spark.sql.adaptive.enabled", True)  # Enable AQE
   spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10MB")  # Threshold
   ```

4. **Example Scenario**:
   ```
   Table A: 100GB raw → after WHERE clause → 5MB
   Table B: 50GB

   Without AQE: Sort-merge join (planned at compile time based on 100GB estimate)
   With AQE: Broadcast join (detected 5MB at runtime, converted automatically)
   ```

5. **Limitations**:
   - Only converts to broadcast if the smaller side is truly small after runtime stats
   - Cannot convert if the join has already started executing
   - Doesn't help if both sides remain large after filtering
   - Still respects `autoBroadcastJoinThreshold`—won't broadcast tables larger than this

**AQE vs Manual Broadcast Hints**:

*When AQE Broadcast Works Well*:
- Table sizes are unknown at compile time but become clear after filtering
- Simple queries where runtime stats are accurate
- When you don't have prior knowledge of data sizes
- Ad-hoc/exploratory queries where manual tuning isn't practical

*When Manual Broadcast Hints Outperform AQE*:

1. **Statistics Unavailable or Stale**: AQE relies on runtime stats from completed stages. If stats are missing or inaccurate, AQE may miss broadcast opportunities. Manual hint `broadcast(small_df)` guarantees broadcast.

2. **Cross-Stage Dependencies**: AQE can only convert to broadcast *before* a join stage starts. If the small table's size is only known after a stage that runs concurrently with the join, AQE can't react in time.

3. **Known Small Dimension Tables**: Dimension tables (countries, product categories, date dims) are predictably small. Manual hints avoid AQE's runtime detection overhead and provide more deterministic query plans for production pipelines.

4. **Threshold Edge Cases**: Table is 12MB but threshold is 10MB—AQE won't broadcast. If you know 12MB broadcast is safe for your cluster, manual hint overrides.

5. **Complex Subqueries**: AQE struggles to estimate sizes of complex CTEs or subqueries. Use manual hints when you know the subquery result is small.

6. **Multiple Joins in Sequence**: AQE optimizes one stage at a time. You may know that after join #1, the result is small enough to broadcast for join #2. Manual hint on intermediate result can be more efficient.

7. **Driver Memory Awareness**: AQE doesn't consider driver memory constraints. If you know your driver can handle a 500MB broadcast, increase threshold or use hint.

*Decision Matrix*:

| Scenario | Recommendation |
|----------|----------------|
| Ad-hoc queries, unknown data | Trust AQE |
| Production pipelines, known dimensions | Manual hints |
| Complex multi-join queries | Manual hints on known small tables |
| Table size near threshold | Manual hint if you know it's safe |
| Unpredictable filter selectivity | Trust AQE |

*Best Practice - Hybrid Approach*:

```python
# Let AQE handle dynamic cases
spark.conf.set("spark.sql.adaptive.enabled", True)

# But use explicit hints for known small tables
result = (
    large_fact_table
    .join(broadcast(dim_country), "country_id")      # Known small
    .join(broadcast(dim_product_type), "type_id")    # Known small
    .join(dim_customer, "customer_id")               # Let AQE decide
)
```

**Summary**: AQE is excellent as a safety net and for dynamic scenarios, but experienced Spark users routinely use manual broadcast hints for known dimension tables and production pipelines where deterministic performance matters.

**External Resources**:
- https://spark.apache.org/docs/latest/sql-performance-tuning.html#broadcast-hint
- https://databricks.com/blog/2021/08/04/adaptive-query-execution-brings-spark-sql-in-line-with-state-of-the-art-databases.html
- https://medium.com/analytics-vidhya/spark-broadcast-joins-and-best-practices-f3b12265cf06

### Skew Detection Methods

**Definition**: Techniques and metrics to identify data skew (uneven distribution across partitions) before it impacts performance, enabling proactive optimization and mitigation strategies.

**Common Detection Techniques**:

- **Partition Size Analysis**: Examine partition sizes and identify outliers (e.g., one partition 10x larger than others)
- **Record Count Distribution**: Compare record counts per partition to detect imbalanced distribution
- **Execution Time Metrics**: Monitor task execution times; skewed partitions typically have longer execution times
- **Shuffle Metrics**: Analyze shuffle stage metrics for byte distribution across partitions
- **Key Cardinality Analysis**: Count distinct values in join/groupBy keys to identify heavily concentrated values
- **Histogram Analysis**: Generate histograms of key distributions to visualize concentration patterns
- **Spark Web UI Monitoring**: Use Spark UI task metrics to identify slow tasks indicating skew
- **Query Explain Plans**: Review query plans for stage complexity and potential skew indicators
- **Custom Metrics**: Implement accumulators or listeners to track key distribution during processing

**External Resources**:

- https://databricks.com/blog/2021/05/27/apache-spark-3-1-released.html
- https://www.youtube.com/watch?v=daXEp4HmS-E
- https://spark.apache.org/docs/latest/sql-performance-tuning.html

### Salting in Spark Operations

**Definition**: Technique adding random prefixes to join keys to distribute skewed data evenly across partitions, resolving join skew and improving performance.

**Guidelines and Best Practices**:

1. **When to Apply Salting**
   - Use when a small number of keys account for majority of data (e.g., 1% of keys = 50% of rows)
   - Apply when join/aggregation tasks show significant time variance in Spark UI
   - Consider when single partitions cause OOM errors while others complete quickly

2. **Choosing the Salt Factor**
   - Start with salt factor = number of executor cores (e.g., 8-16 for typical clusters)
   - Formula: `salt_factor = skewed_partition_size / target_partition_size`
   - Target partition size: 128MB-256MB for optimal performance
   - Higher salt factors increase parallelism but add overhead from explode operations

3. **Implementation Pattern for Joins**

   ```python
   # Small table: explode with salt values
   salt_range = list(range(num_salts))
   small_df = small_df.withColumn("salt", explode(array([lit(i) for i in salt_range])))
   small_df = small_df.withColumn("salted_key", concat(col("key"), lit("_"), col("salt")))

   # Large table: add random salt
   large_df = large_df.withColumn("salt", (rand() * num_salts).cast("int"))
   large_df = large_df.withColumn("salted_key", concat(col("key"), lit("_"), col("salt")))

   # Join on salted key
   result = large_df.join(small_df, "salted_key")
   ```

4. **Selective Salting (Recommended)**
   - Only salt the known skewed keys, not the entire dataset
   - Identify hot keys first: `df.groupBy("key").count().orderBy(desc("count")).limit(100)`
   - Use broadcast for non-skewed keys, salting only for problematic ones
   - Reduces overhead compared to full-table salting

5. **Salt Factor Tuning Guidelines**

   | Skew Ratio (max/avg) | Recommended Salt Factor |
   |----------------------|-------------------------|
   | 10x                  | 4-8                     |
   | 50x                  | 16-32                   |
   | 100x+                | 32-64                   |

6. **Aggregation Salting Pattern**
   - First pass: aggregate with salted keys (partial aggregation)
   - Second pass: aggregate results to remove salt (final aggregation)
   - Works for associative operations: SUM, COUNT, MIN, MAX, AVG (with care)

7. **Performance Considerations**
   - Salting increases data volume on small table by salt_factor
   - Memory overhead: small_table_size × salt_factor must fit in memory
   - Network overhead: more shuffle data due to exploded small table
   - Trade-off: parallelism gain vs. data amplification cost

8. **Avoiding Common Pitfalls**
   - Don't salt both tables with random values (keys won't match)
   - Remember to remove salt columns after join if not needed
   - Test with representative data; synthetic tests may not show real skew
   - Monitor shuffle spill metrics to validate improvement

9.  **Alternatives to Consider First**
   - Spark 3.0+ AQE skew join optimization: `spark.sql.adaptive.skewJoin.enabled=true`
   - Broadcast join if smaller table fits in memory
   - Isolation approach: process skewed keys separately, then union results

10. **Validation Checklist**
    - [ ] Confirmed skew exists via Spark UI task metrics
    - [ ] Identified specific hot keys causing skew
    - [ ] Calculated appropriate salt factor based on skew ratio
    - [ ] Tested with subset of data before full run
    - [ ] Compared execution time and resource usage before/after

**External Resources**:

- https://databricks.com/blog/2021/05/27/apache-spark-3-1-released.html
- https://medium.com/dataworks-eng/salting-de-salting-in-spark-63f233f4f6b7
- https://stackoverflow.com/questions/32473973/handling-data-skew-when-joining-data-in-apache-spark

### AQE vs Manual Salting for Skew Joins

**Definition**: Comparison of Spark's Adaptive Query Execution (AQE) automatic skew handling versus manual salting techniques, with guidance on when each approach is preferred.

**When AQE Skew Join Works Well**:

- Moderate skew (10-50x ratio) with standard join patterns
- When skew is unpredictable or varies between runs
- Spark 3.2+ where AQE has matured significantly
- Simpler pipelines where AQE can accurately detect skew at runtime

**When Manual Salting Outperforms AQE**:

1. **Extreme skew (100x+)**: AQE's default thresholds may not split partitions aggressively enough. It uses `skewedPartitionFactor` (default 5) and `skewedPartitionThresholdInBytes` (default 256MB) which can be insufficient for severe cases.

2. **Known, stable hot keys**: If you know a specific key (e.g., "US") always causes skew, pre-salting is more efficient than waiting for AQE to detect and react at runtime.

3. **Complex multi-stage pipelines**: AQE optimizes stage-by-stage. In long DAGs, early manual intervention can prevent skew from propagating through multiple stages.

4. **Memory-constrained clusters**: AQE's runtime statistics collection and re-planning have overhead. Pre-optimized salting avoids this.

5. **Aggregations**: AQE skew handling primarily targets joins. For `groupBy` skew, manual salting with two-pass aggregation is often necessary.

**Decision Flow**:

```
Start with AQE enabled (it's low-cost)
     ↓
Monitor Spark UI for skew symptoms
     ↓
If tasks still show 10x+ time variance → tune AQE thresholds first
     ↓
If still problematic → apply selective manual salting on known hot keys
```

**Tuning AQE Before Manual Salting**:

```python
# More aggressive skew detection
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", 2)
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "64MB")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128MB")
```

**Summary**: AQE should be the first line of defense—it handles many cases automatically. But experienced Spark users can outperform AQE in specific scenarios, particularly with severe/known skew patterns, aggregation skew, or when deterministic performance is required rather than runtime adaptation.

### Strategies for Avoiding Full Table Scans in Spark Operations

**Definition**: Techniques including proper indexing, pruning, partition elimination, and query optimization to avoid scanning entire datasets and reduce I/O.

**Common Avoidance Techniques**:

- **Partition Pruning**: Filter on partitioned columns early in queries to eliminate entire partitions from scan (e.g., WHERE date >= '2024-01-01')
- **Predicate Pushdown**: Push filter conditions down to data source level before Spark reads data, reducing bytes transferred
- **Column Projection**: Select only required columns rather than reading entire rows (SELECT col1, col2 instead of SELECT *)
- **Index Usage**: Utilize database indexes when reading from external sources (PostgreSQL, MySQL) via JDBC
- **Bucketing**: Pre-organize tables into buckets on join keys to avoid full scans during join operations
- **Bloom Filters**: Use bloom filter hints to skip partitions/files that don't match filter conditions
- **Statistics-Based Optimization**: Collect table statistics to enable CBO (Cost-Based Optimizer) to make better decisions
- **Query Caching**: Cache frequently accessed DataFrames to avoid re-scanning from source
- **File Format Selection**: Use columnar formats (Parquet, ORC) that support selective column reading and compression
- **Proper Join Ordering**: Order joins to filter early, reducing data passed through subsequent joins
- **Window Function Optimization**: Use window functions with OVER clauses strategically to avoid cross-joins
- **Aggregate Before Join**: Pre-aggregate data before joins to reduce scan volume
- **Data Sampling**: Use sample() for exploratory queries instead of full scans

**External Resources**:

- https://spark.apache.org/docs/latest/sql-performance-tuning.html
- https://databricks.com/blog/2021/08/04/adaptive-query-execution-brings-spark-sql-in-line-with-state-of-the-art-databases.html
- https://use-the-index-luke.com/

### Strategies for Handling 10TB Data Workloads Using Spark

**Definition**: Best practices for large-scale data processing including right-sizing clusters, optimizing shuffle, compression, caching strategies, and distributed SQL techniques.

**Key Best Practices for 10TB+ Workloads**:

- **Cluster Right-Sizing**: Calculate optimal executor memory, cores, and number based on data size (typically 1 executor per 4-8 cores, 4-16GB per executor)
- **Data Partitioning Strategy**: Create 100s-1000s of partitions based on cluster size (2-4 partitions per core minimum)
- **Shuffle Optimization**: Set `spark.sql.shuffle.partitions` based on data volume and cluster resources; use adaptive query execution
- **Compression Strategy**: Enable Spark compression (snappy, lz4) for shuffle and storage to reduce network/disk I/O
- **Columnar Format Usage**: Store data in Parquet or ORC format with column pruning for selective reads
- **Memory Management**: Configure `spark.executor.memory`, `spark.driver.memory`, and memory fractions for execution vs storage
- **Caching Strategy**: Cache frequently accessed DataFrames selectively; avoid caching entire datasets when possible
- **Query Optimization**: Use explain plans to identify bottlenecks; optimize join order and filter pushdown
- **Broadcast Optimization**: Broadcast small tables (<1GB) to avoid shuffle in joins
- **Skew Handling**: Detect and handle data skew using salting, repartitioning, or broadcasting
- **Dynamic Resource Allocation**: Enable dynamic allocation to scale executors based on task requirements
- **Spill Management**: Monitor shuffle spill and reduce it through partitioning and memory optimization
- **Network Optimization**: Consider job placement locality; use network optimization for wide transformations
- **Serialization**: Use Kryo serialization for better performance vs default Java serialization
- **File I/O Optimization**: Use S3 or HDFS directly; enable list optimization for cloud storage
- **Staging Tables**: Use intermediate staging/cached tables to break complex queries into smaller stages
- **Approximate Algorithms**: Use approximate algorithms (HyperLogLog for distinct counts) when exact results aren't necessary
- **Parallel Processing**: Maximize parallelism by tuning task allocation and avoiding single-threaded bottlenecks
- **Monitoring & Metrics**: Use Spark UI, event logs, and custom metrics to identify performance issues
- **Checkpointing**: Checkpoint long DAGs to truncate lineage and prevent stack overflow

**External Resources**:

- https://databricks.com/blog/2021/12/01/scaling-data-science-with-apache-spark.html
- https://spark.apache.org/docs/latest/tuning.html
- https://www.youtube.com/watch?v=daXEp4HmS-E

### Spark AQE (Adaptive Query Execution) Limitations

**Definition**: Adaptive Query Execution optimizes runtime behavior but has limitations with certain SQL patterns, shuffles, and doesn't apply to all operations.

**External Resources**:

- https://databricks.com/blog/2021/08/04/adaptive-query-execution-brings-spark-sql-in-line-with-state-of-the-art-databases.html
- https://spark.apache.org/docs/latest/sql-performance-tuning.html#adaptive-query-execution
- https://www.youtube.com/watch?v=daXEp4HmS-E

## Spark-Specific Features

### Spark Context Management

**Definition**: Managing SparkContext lifecycle (creation, configuration, cleanup) ensuring proper resource allocation, preventing memory leaks, and enabling correct session isolation.

**External Resources**:

- https://spark.apache.org/docs/latest/rdd-programming-guide.html#initializing-spark
- https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.html
- https://databricks.com/blog/2020/07/01/7-py-spark-best-practices-for-data-scientists.html

### Spark Caching (Query-Specific & General)

**Definition**: Persisting DataFrames in memory/disk to reuse computed results across multiple actions, improving performance for multi-use scenarios and iterative algorithms.

**External Resources**:

- https://spark.apache.org/docs/latest/rdd-programming-guide.html#rdd-persistence
- https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.cache.html
- https://databricks.com/blog/2015/04/24/recent-performance-improvements-in-apache-spark-sql-pushdown-predicates.html

### Spark Checkpoints

**Definition**: Truncating RDD lineage by saving intermediate results to reliable storage, crucial for iterative and stateful streaming applications to manage memory.

**External Resources**:

- https://spark.apache.org/docs/latest/rdd-programming-guide.html#checkpointing
- https://databricks.com/blog/2016/09/29/checkpoint-and-restore-spark-applications.html
- https://spark.apache.org/docs/latest/streaming-programming-guide.html#checkpointing

### Assert Spark DataFrame Equality Using Chispa

**Definition**: Testing library (Chispa) for comparing Spark DataFrames in unit tests with flexible comparison (ignoring order, handling nulls, schema matching).

**External Resources**:

- https://github.com/MrPowers/chispa
- https://mrpowers.medium.com/testing-pyspark-code-4d32765a2c80
- https://spark.apache.org/docs/latest/api/python/reference/pyspark.testing.html

### JDBC Partitioning Optimization Strategies

**Definition**: Techniques for efficiently reading large tables from external databases via JDBC using partitioning, predicate pushdown, and fetch sizes.

**Key Optimization Techniques**:

- **Partition Column Selection**: Choose columns with good cardinality and even distribution (auto-increment integers, primary keys, timestamps); avoid skewed columns
- **Number of Partitions Configuration**: Set `numPartitions` based on cluster size and network capacity (typically 2-4x cluster core count) to maximize parallelism without overwhelming source DB
- **Partition Bounds Definition**: Explicitly set `lowerBound` and `upperBound` to define partition range, avoiding expensive statistics queries on source database
- **Fetch Size Tuning**: Configure `fetchsize` parameter to balance memory usage and network efficiency (larger = fewer network roundtrips but more memory consumption)
- **Connection Pooling**: Reuse JDBC connections across partitions through connection pooling to reduce connection overhead
- **Predicate Pushdown**: Push WHERE clauses to source database to filter data early, reducing bytes transferred over network
- **Column Projection**: Select only required columns instead of reading entire tables (SELECT col1, col2 instead of SELECT *)
- **Batch Read Optimization**: Configure JDBC driver batch size settings to optimize data transfer batches
- **Time-Based Partitioning**: Use timestamp columns with appropriate time ranges (daily, hourly) for time-series data enabling temporal filtering
- **Index Alignment**: Ensure partition columns are indexed in source database to enable efficient range scans
- **Partition Skew Mitigation**: Use salting or custom partition logic for non-uniform distributions
- **Driver Configuration**: Tune JDBC driver settings (socket timeout, connection timeout, TCP buffer sizes) for stable large reads
- **Query Optimization**: Optimize underlying SQL query with JOINs and aggregations pushed to database rather than Spark
- **Database-Specific Hints**: Use database-specific query hints (e.g., Oracle /*+ PARALLEL */, MySQL USE INDEX) for optimization
- **Incremental Reads**: Use watermark columns (timestamps, sequence numbers) for incremental reads avoiding full table scans on repeated executions
- **Partition Validation**: Test partition strategy on subset of data before full-scale execution to identify bottlenecks
- **Network Configuration**: Optimize network settings (MTU size, TCP window scaling) between Spark cluster and database server
- **Query Caching**: Cache frequently accessed JDBC data locally to avoid repeated database reads
- **Bulk Operations**: Batch multiple small reads into single larger queries where possible
- **Connection Lifecycle**: Close connections properly and reuse connection pools across multiple read operations

**External Resources**:

- https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html
- https://databricks.com/blog/2018/08/27/apache-spark-2-4-better-support-for-machine-learning-and-a-faster-sql-engine.html
- https://stackoverflow.com/questions/34033934/spark-dataframe-jdbc-partitioncolumn-and-numpartitions

## Scala vs Python for Data Engineering

### Scala vs Python Strengths and Weaknesses in Data Engineering

**Definition**: Comparative analysis - Scala offers type safety, JVM performance, and better for production ETL; Python provides faster development, data science ecosystem, but slower execution.

**SWOT Analysis - Scala for Data Engineering**:

| Strengths | Weaknesses |
|-----------|------------|
| Native JVM language - no serialization overhead with Spark | Steeper learning curve, especially for functional paradigms |
| Compile-time type safety catches errors early | Slower development iteration (compile step required) |
| Access to Dataset API with strong typing | Smaller talent pool compared to Python |
| Better performance for complex transformations and UDFs | Verbose syntax for simple operations |
| Preferred for Spark internals and custom extensions | IDE/tooling less mature than Python ecosystem |

| Opportunities | Threats |
|---------------|---------|
| Growing adoption in enterprise data platforms | Python's dominance in data science creates pressure |
| Spark 3.x improvements favor JVM languages | PySpark performance gap narrowing with Arrow/Pandas UDFs |
| Strong fit for streaming and low-latency pipelines | Declining community momentum vs Python |
| Type-safe data contracts in production ETL | Databricks investing heavily in Python-first features |

**SWOT Analysis - Python for Data Engineering**:

| Strengths | Weaknesses |
|-----------|------------|
| Rapid development and prototyping | Serialization overhead (Py4J) for non-DataFrame operations |
| Massive ecosystem (pandas, numpy, scikit-learn, etc.) | No compile-time type checking (runtime errors) |
| Lower barrier to entry, larger talent pool | UDF performance significantly slower than Scala |
| Excellent for data science/ML integration | GIL limitations for CPU-bound parallel tasks |
| Interactive development (notebooks, REPL) | Dynamic typing can hide bugs until production |

| Opportunities | Threats |
|---------------|---------|
| Arrow-based optimizations closing performance gap | Complex pipelines may hit performance ceilings |
| Pandas API on Spark for familiar syntax | Type safety becoming more critical for data contracts |
| Growing support for type hints (mypy, pydantic) | Scala still preferred for Spark core contributions |
| Dominant in ML/AI creates natural data pipeline integration | Enterprise governance may prefer compiled languages |

**Comparison Table**:

| Aspect | Scala | Python | Winner |
|--------|-------|--------|--------|
| **Performance (DataFrame API)** | Native JVM, no serialization | Near-native via Catalyst | Tie |
| **Performance (UDFs)** | 2-10x faster | Py4J serialization overhead | Scala |
| **Performance (RDD operations)** | Native execution | Significant overhead | Scala |
| **Development Speed** | Slower (compile, verbose) | Faster (dynamic, concise) | Python |
| **Learning Curve** | Steep (FP concepts, types) | Gentle (readable syntax) | Python |
| **Type Safety** | Compile-time checking | Runtime only (optional hints) | Scala |
| **Data Science Integration** | Limited libraries | Rich ecosystem (pandas, sklearn) | Python |
| **Debugging** | Compile errors catch issues early | Runtime errors, but easier stack traces | Tie |
| **Spark API Coverage** | Full (including Dataset) | Full (except typed Dataset) | Scala |
| **Streaming** | Preferred for low-latency | Adequate for most use cases | Scala |
| **Community/Hiring** | Smaller, specialized | Larger, diverse | Python |
| **Notebook Experience** | Adequate (Zeppelin, Jupyter) | Excellent (Jupyter native) | Python |
| **Production ETL** | Preferred for critical pipelines | Common, improving | Scala |
| **ML Pipeline Integration** | Requires Python handoff | Native integration | Python |

**Recommendation by Use Case**:

| Use Case | Recommended | Rationale |
|----------|-------------|-----------|
| High-throughput production ETL | Scala | Type safety, performance, compile-time validation |
| Data exploration/ad-hoc analysis | Python | Faster iteration, notebook experience |
| ML feature engineering | Python | Seamless sklearn/pandas integration |
| Low-latency streaming | Scala | Better performance, native Spark Streaming |
| Team with mixed skills | Python | Lower barrier, easier hiring |
| Spark library/extension development | Scala | Native JVM, full API access |
| Prototyping new pipelines | Python | Rapid development, quick validation |
| Data contracts/schema enforcement | Scala | Compile-time type checking |

**External Resources**:

- https://databricks.com/blog/2015/11/16/a-tale-of-three-apache-spark-apis-rdds-dataframes-and-datasets.html
- https://medium.com/@rinu.gour123/scala-vs-python-for-data-engineering-4bc26bc87a7a
- https://www.linkedin.com/pulse/python-vs-scala-apache-spark-navneet-karnani/

## Memory & Performance Tuning

### Spark Memory Tuning

**Definition**: Optimization techniques for configuring executor heap size, memory fraction allocation (execution vs storage), and memory overhead to maximize throughput and minimize out-of-memory errors.

**External Resources**:

- https://spark.apache.org/docs/latest/tuning.html
- https://spark.apache.org/docs/latest/configuration.html#memory-management
- https://databricks.com/blog/2015/05/28/tuning-java-garbage-collection-for-spark-applications.html

### Spark Garbage Collection Tuning

**Definition**: Configuration of JVM garbage collection (G1GC, CMS) to minimize pause times and improve application stability during intensive processing.

**External Resources**:

- https://spark.apache.org/docs/latest/tuning.html#garbage-collection-tuning
- https://databricks.com/blog/2015/05/28/tuning-java-garbage-collection-for-spark-applications.html
- https://www.oracle.com/technical-resources/articles/java/g1gc.html

### Spark Performance Benchmark

**Definition**: Systematic measurement of Spark job performance using metrics (execution time, CPU, memory, I/O) to identify bottlenecks and validate optimization effectiveness.

**External Resources**:

- https://spark.apache.org/docs/latest/monitoring.html
- https://databricks.com/blog/2021/01/28/optimizing-distributed-machine-learning-pipelines.html
- https://github.com/databricks/spark-benchmark

### Spark Accumulators Limitations

**Definition**: Accumulator variables for distributed aggregation have limitations: only drivers can read results, no ordering guarantees, and limited use in transformations vs actions.

**External Resources**:

- https://spark.apache.org/docs/latest/rdd-programming-guide.html#accumulators
- https://stackoverflow.com/questions/47729935/spark-accumulator-limitations-and-best-practices
- https://databricks.com/blog/2015/06/22/understanding-spark-performance.html

### Spark Listeners

**Definition**: Observer pattern implementation allowing custom monitoring of Spark events (job start/end, task execution, executor metrics) for observability and debugging.

**External Resources**:

- https://spark.apache.org/docs/latest/monitoring.html#metrics
- https://databricks.com/blog/2015/06/22/understanding-spark-performance.html
- https://github.com/databricks/Spark-Listener-Examples