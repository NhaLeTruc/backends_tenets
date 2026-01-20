# Storage Optimization

## Table of Contents

- [Storage Optimization](#storage-optimization)
  - [Table of Contents](#table-of-contents)
  - [S3 Storage Partitioning Strategies](#s3-storage-partitioning-strategies)
  - [Small Files Handling Strategies](#small-files-handling-strategies)
  - [Compaction](#compaction)
  - [Delta Lake Z-Ordering](#delta-lake-z-ordering)
  - [Parquet Versioned Schemas Feature](#parquet-versioned-schemas-feature)
  - [Snowflake Algorithm for Creating Uniformly Distributed Keys](#snowflake-algorithm-for-creating-uniformly-distributed-keys)

### S3 Storage Partitioning Strategies

**Definition**: Techniques to organize S3 objects hierarchically (by date, geography, product, etc.) to optimize query performance, reduce scan costs, and enable efficient data retrieval.

**External Resources**:

- https://docs.aws.amazon.com/AmazonS3/latest/userguide/BucketKeys.html
- https://aws.amazon.com/blogs/big-data/top-10-performance-optimization-tips-for-amazon-athena/
- https://docs.aws.amazon.com/athena/latest/ug/partitioning-data.html

### Small Files Handling Strategies

**Definition**: Approaches to address the "small files problem" where excessive small files degrade performance through metadata overhead and scheduling inefficiency. Solutions include compaction, consolidation, and proper partitioning.

**Common Strategies**:

1. **Coalesce/Repartition Before Write**
   - Use `coalesce(n)` to reduce partitions without shuffle (when reducing)
   - Use `repartition(n)` when increasing partitions or need even distribution
   - Rule of thumb: target 128MB-1GB files for optimal performance

2. **Adaptive Query Execution (AQE)**
   - Enable `spark.sql.adaptive.enabled=true`
   - Set `spark.sql.adaptive.coalescePartitions.enabled=true`
   - Automatically coalesces small partitions at runtime

3. **Target File Size Configuration**
   - Delta Lake: `spark.databricks.delta.targetFileSize` or `delta.targetFileSize`
   - Iceberg: `write.target-file-size-bytes` (default 512MB)
   - Hive: `hive.merge.smallfiles.avgsize` and `hive.merge.size.per.task`

4. **Scheduled Compaction Jobs**
   - Run periodic OPTIMIZE commands (Delta Lake)
   - Use `rewriteDataFiles` action (Iceberg)
   - Schedule during low-traffic periods

5. **Auto-Optimization Features**
   - Delta Lake: Enable `delta.autoOptimize.optimizeWrite=true`
   - Delta Lake: Enable `delta.autoOptimize.autoCompact=true`
   - Iceberg: Configure maintenance procedures

6. **Bin Packing**
   - Groups small files into optimal-sized bins during compaction
   - Iceberg uses bin-packing by default in `rewriteDataFiles`
   - Minimizes rewrites while achieving target file sizes

7. **Partition Strategy Optimization**
   - Avoid over-partitioning (too many small partitions)
   - Use composite keys wisely (date + hour vs date alone)
   - Consider partition pruning benefits vs file count trade-offs

8. **Write-time Hints**
   - `maxRecordsPerFile` option to control output file sizes
   - `spark.sql.files.maxRecordsPerFile` for global setting

**External Resources**:

- https://spark.apache.org/docs/latest/sql-data-sources-parquet.html#configuration
- https://databricks.com/blog/2023/02/15/improving-apache-spark-write-performance.html
- https://iceberg.apache.org/

### Compaction

**Definition**: Process of merging multiple small files into fewer larger files to improve I/O performance, reduce metadata overhead, and optimize storage utilization.

**External Resources**:

- https://docs.databricks.com/delta/optimize.html
- https://delta.io/blog/2021-09-01-delta-lake-compaction/
- https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameWriter.saveAsTable.html

### Delta Lake Z-Ordering

**Definition**: Data organization technique that co-locates related information by sorting data on multiple columns (Z-order curve), significantly improving query performance for multi-dimensional filters.

**External Resources**:

- https://docs.databricks.com/en/delta/best-practices.html#optimize-with-z-order-on-columns-to-speed-up-queries
- https://delta.io/blog/2023-06-14-delta-lake-zorder/
- https://en.wikipedia.org/wiki/Z-order_curve

### Parquet Versioned Schemas Feature

**Definition**: Parquet's capability to maintain multiple schema versions within files, supporting backward and forward compatibility while enabling schema evolution without data loss.

**External Resources**:

- https://parquet.apache.org/docs/file-format/
- https://parquet.apache.org/docs/file-format/schemas/
- https://github.com/apache/parquet-format

### Snowflake Algorithm for Creating Uniformly Distributed Keys

**Definition**: Distributed key generation algorithm (similar to Twitter Snowflake IDs) creating unique, sortable, uniformly distributed keys across systems without requiring central coordination.

**Snowflake ID Structure** (64-bit):

- **Timestamp** (41 bits): Milliseconds since epoch; allows IDs to be sortable by time (269 years of coverage)
- **Datacenter ID** (5 bits): Identifies which datacenter/region generated ID; supports up to 32 datacenters
- **Worker ID** (5 bits): Identifies which worker/server within datacenter; supports up to 32 workers per datacenter
- **Sequence** (12 bits): Counter within same millisecond to ensure uniqueness; supports 4,096 IDs per millisecond per worker

**Key Implementation Techniques**:

- **Standard Twitter Snowflake Layout**: Use 41-bit timestamp (ms precision), 5-bit datacenter, 5-bit worker, 12-bit sequence; proven production design
- **Custom Bit Allocation**: Adjust bit distribution based on constraints (e.g., 42-bit timestamp for extra years, 4-bit datacenter/worker if fewer servers)
- **Epoch Configuration**: Set custom epoch (e.g., Jan 1, 2020) instead of Unix epoch to extend future coverage; current timestamp becomes smaller
- **Timestamp Precision Selection**: Use millisecond precision for most use cases (sufficient for ordering, standard practice); use microsecond for high-throughput systems (requires more bits)
- **Datacenter ID Assignment**: Statically assign datacenter IDs (DC1=1, DC2=2); avoid dynamic assignment to prevent coordination overhead
- **Worker ID Assignment**: Assign worker IDs via configuration file, environment variable, or ZooKeeper/etcd for centralized coordination
- **Sequence Initialization**: Initialize sequence to 0 each millisecond; increment within millisecond; reset to 0 on timestamp advancement
- **Clock Skew Handling**: Detect backwards time jumps; wait/sleep until system clock catches up; log warnings for monitoring
- **Monotonic Guarantees**: Ensure IDs increase monotonically within single worker by preventing timestamp rollbacks and incrementing sequence
- **Thread-Safe Generation**: Use atomic operations or locking to ensure concurrent threads safely generate unique sequences within millisecond
- **Distributed Coordination**: Pre-assign datacenter/worker IDs at deployment time; avoid runtime coordination for performance
- **Batching for Performance**: Generate IDs in batches (cache sequence values) to reduce contention and improve throughput
- **Fallback ID Generation**: Use UUID (worse performance) as fallback if Snowflake generation fails (clock skew, sequence overflow)
- **Sequence Overflow Handling**: On overflow (>4096 IDs in single millisecond), wait for next millisecond to reset sequence (rare in practice)
- **Database Storage Optimization**: Use 64-bit BIGINT in databases (fits in single column); cluster by ID for sequential disk I/O benefits
- **Sortability Verification**: Extract timestamp from ID by right-shifting; verify IDs from consecutive requests have increasing timestamps
- **Collision Testing**: Stress test concurrent generation from multiple threads; validate all generated IDs are unique
- **Clock Synchronization Requirements**: Use NTP (Network Time Protocol) to keep system clocks synchronized across datacenters (<1ms drift typical)
- **Hybrid Centralized-Distributed**: Use distributed generation for performance with central registry tracking worker assignments for monitoring
- **Backward Compatibility**: Define migration path if changing bit allocations (new ID prefix, separate ID space, gradual rollout)
- **Application Integration**: Expose ID generation as library/service; clients call synchronously or use pub-sub for fire-and-forget scenarios

**Practical Snowflake Implementation Workflow**:

1. **Define Requirements**: Determine ID generation rate needed (IDs per second), number of datacenters, number of servers, required uniqueness guarantees
2. **Design Bit Allocation**: Choose timestamp precision (ms/μs) and bit split for datacenter/worker/sequence based on scale requirements
3. **Select Custom Epoch**: Pick epoch date (e.g., 2020-01-01) to maximize future timestamp coverage; calculate years available
4. **Datacenter ID Assignment**: Assign static datacenter IDs (1-31); document mapping (DC-US-East=1, DC-US-West=2)
5. **Worker ID Assignment**: Implement worker ID assignment via config files or service (ZooKeeper, etcd); validate uniqueness across fleet
6. **Timestamp Source Implementation**: Use system clock via `System.currentTimeMillis()` (Java) or `time.time_ns()` (Python); add NTP sync monitoring
7. **Sequence Counter Implementation**: Initialize counter to 0 per millisecond; use AtomicLong or thread-safe equivalent for concurrent access
8. **Clock Skew Detection**: Detect when `currentTime < lastTime`; implement sleep/wait logic to handle small skews gracefully
9. **ID Generation Algorithm**: Implement bit-shifting: `(timestamp << 22) | (datacenter << 17) | (worker << 12) | sequence`
10. **Concurrency Testing**: Write unit tests generating IDs from multiple threads; validate all unique, increasing within thread
11. **Performance Benchmarking**: Measure generation rate (target: 1M+ IDs per second per worker); optimize hot paths
12. **Database Integration**: Test insertion of generated IDs into production database; verify clustering and query performance benefits
13. **Monitoring Setup**: Track sequence counter distribution (detect hotspots), clock skew occurrences, collision attempts (should be zero)
14. **Documentation**: Document datacenter/worker ID assignments, epoch configuration, bit layout for operations and development teams
15. **Deployment Validation**: Pre-deployment: verify clocks synchronized across datacenters (NTP check), worker IDs assigned correctly, test ID extraction
16. **Gradual Rollout**: Deploy to subset of services first; monitor metrics before full rollout; establish rollback procedure if issues arise
17. **Production Monitoring**: Monitor ID generation rate, sequence counter resets, clock skew events; alert on anomalies
18. **Capacity Planning**: Calculate future coverage (e.g., 41-bit timestamp good until year 2189); plan migration strategy as approach limits

**Advantages Over Alternatives**:

- **No central coordination**: Each datacenter/worker generates IDs independently; no bottleneck, high availability
- **Sortable by timestamp**: IDs can be ordered chronologically; beneficial for database clustering and time-range queries
- **Unique across distributed system**: Bit fields ensure no collisions across datacenters and workers
- **Compact**: 64-bit fits in standard database BIGINT; less storage than UUID (128-bit)
- **Simple algorithm**: Fast to compute (single bit-shift operation); minimal CPU overhead
- **Monotonic**: Within single worker, IDs increase monotonically (important for some use cases)

**Comparison with Alternatives**:

- **UUID (v4)**: Random, 128-bit, no ordering, standard but not sortable, higher storage
- **UUIDv7**: Time-ordered UUID, 128-bit, more storage than Snowflake but more standardized
- **Database Sequence/Auto-Increment**: Centralized (single point of failure), requires database round-trip, high latency, poor for distributed systems
- **Hash-based IDs**: No ordering guarantee, collision risk, poor database performance

**External Resources**:

- https://blog.twitter.com/engineering/en_us/a/2010/announcing-snowflake
- https://en.wikipedia.org/wiki/Snowflake_(ID_generation_system)
- https://github.com/getsetbro/snowflake
- https://en.wikipedia.org/wiki/Universally_unique_identifier
- https://github.com/ecommercetech/snowflake
- https://medium.com/codex/understanding-snowflake-ids-7ff2aada964
