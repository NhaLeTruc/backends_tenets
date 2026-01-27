# Hardware Considerations for Optimizing Computation Throughput in Distributed Data Processing Systems

Hardware decisions directly impact throughput in distributed systems like Apache Spark. This guide catalogs essential hardware factors affecting data processing performance.

---

## 1. CPU Architecture & Generation

### Instruction-Level Parallelism (ILP) & Clock Speed

Modern CPUs execute more instructions per cycle despite lower clock speeds; newer architectures (2021+ EPYC, Sapphire Rapids) handle 20-30% more throughput per task than older Xeon E5 series.

- **Intel Xeon E5-2680 v2 (2013)**: ~3.8 GHz, older ILP design
- **AMD EPYC 7763 (2021)**: Similar base clock, ~1.7x better ILP efficiency
- **Intel Xeon Sapphire Rapids (2023)**: ~3.5 GHz base, ~1.8x better than baseline

**Impact**: Same cluster size, new CPU architecture = 20-30% faster throughput.

### Hyperthreading / SMT Efficiency

How effectively the CPU handles task context switching determines usable parallelism.

- **Older Intel Xeon (2-way HT)**: 25-30% speedup from 2nd thread
- **Modern Intel (2-way HT)**: 40-50% speedup
- **AMD EPYC (2-way SMT)**: Similar efficiency, varies by workload

**Result**: Older 32-core CPU effectively handles ~41 tasks, modern handles ~46 tasks.

### Vectorization Capabilities

Modern CPUs have better SIMD support for DataFrame operations.

- **Modern CPUs (AVX-512, VNNI)**: 8 64-bit values per cycle
- **Older CPUs (AVX2)**: 4 64-bit values per cycle

**Impact**: Modern CPUs process partitions **2x faster** for vectorizable operations (columnar filters, Arrow conversion, Parquet I/O, compression).

### L3 Cache Size & Efficiency

Larger caches reduce memory latency for partition data processing.

| Architecture | L3 Cache | Effect on Partitions |
|---|---|---|
| Older Xeon (2015) | 20MB | Smaller working set; need smaller partitions |
| Modern EPYC Milan | 32MB per CCX | Larger working set; handle bigger partitions efficiently |
| Latest Xeon Sapphire Rapids | 12.5MB per P-core | Better memory hierarchy overall |

**Real Impact**: Modern CPU processes **256MB partition** as efficiently as older CPU processes **128MB partition**.

---

## 2. Memory System

### Memory Bandwidth

**Critical for shuffle operations** (most partition-sensitive workload in Spark).

| Generation | Memory Bandwidth | Shuffle Performance |
|---|---|---|
| DDR3 (2012) | ~25 GB/s per socket | Severe bottleneck |
| DDR4 (2014-2019) | ~80-90 GB/s per socket | Moderate |
| DDR5 (2021+) | ~120-130 GB/s per socket | 40-50% faster shuffle |

**Implication**: Modern DDR5 systems can shuffle **larger partitions** without spilling to disk.

### Executor Memory Size

- Typical allocation: 4-8GB per executor
- Affects partition count and memory pressure
- Target: 50-100MB available per task for processing
- Formula: `usable_memory = spark.executor.memory - spark.executor.memoryOverhead`

### Memory Overhead Per Executor

- **Old hardware**: ~100MB × 2 = 200MB (conservative)
- **New hardware**: ~300MB × 4 = 1.2GB (modern CPUs handle this efficiently)

### Spill-to-Disk Risk

Exceeding executor memory forces spilling, reducing throughput significantly.

- Keep peak memory under 75% of allocated executor memory
- Spill-to-disk reduces throughput by 2-10x depending on I/O speed
- Monitor via Spark UI: "Shuffle Spill" metrics should be minimal

---

## 3. Storage & Disk I/O

### Disk Type Impact

- **SSD**: Critical for transaction logs, change data capture (CDC)
- **HDD**: Insufficient for distributed processing; causes severe bottlenecks
- **Impact**: SSD can sustain 100+ MB/s sequential; HDD limited to 10-30 MB/s

### HDFS/S3 Block Size Alignment

- Partition boundaries should align with storage blocks (typically 128-256MB)
- Reduces data movement and improves locality
- Misaligned partitions = unnecessary network transfers

### I/O Throughput Capacity

- Match partition count to allow full I/O utilization without bottlenecks
- Monitor "Task Input Size" in Spark UI
- Ensure disk I/O can sustain network bandwidth usage

### Transaction Log Speed

For CDC and change data operations:
- Fast SSD on transaction log is **critical** for throughput
- Single slow transaction log scan becomes bottleneck for entire connector

---

## 4. Network Infrastructure

### Network Bandwidth

Fundamental limit on shuffle performance and data transfer.

- **1Gbps network**: ~100-125 MB/s theoretical limit
- **10Gbps network**: ~1000-1250 MB/s (10x improvement)
- **Shuffle target**: 500MB-2GB per executor without saturation

**Shuffle throughput formula**: 
```
shuffle_throughput (MB/s) = (shuffle_bytes) / (execution_time_seconds)
```

### Network Latency

Between database, Spark cluster, and storage affects data transfer efficiency.

- Higher latency = more time between request and data arrival
- Affects broadcast join timing
- Critical for real-time streaming workloads

### Full-Duplex Gigabit Minimum

Required for distributed processing; half-duplex networking reduces throughput by ~50%.

### Broadcast Time vs Shuffle Cost

When deciding whether to broadcast a table:

```
broadcast_time = table_size / network_bandwidth
```

Broadcast wins when `broadcast_time < shuffle_time`.

For 1Gbps networks: keep broadcasts under 100-200MB for sub-second transfers.

---

## 5. Core Count & Multi-Core Scaling

### Total Executor Cores

Affects optimal partition count baseline:
- Baseline formula: **2-4 partitions per core**
- More cores = ability to handle more concurrent tasks
- Not all cores are equally useful (see SMT efficiency above)

### Single-Threaded Bottlenecks

Some operations use only 1 core per task regardless of total cores:
- CDC connectors: Single-threaded per task
- Driver operations: Single-threaded (broadcasts, collects)
- Serialization overhead: Can be single-threaded

### Task Parallelism Calculation

Effective concurrent tasks = (cores × SMT_efficiency)

- Old hardware (32 cores): ~41 effective tasks
- Modern hardware (32 cores): ~46 effective tasks

---

## 6. CPU Generation Impact on Partition Sizing

As CPU architecture improves, optimal partition sizes change due to better cache efficiency and memory bandwidth.

| Hardware Type | Partition Size | Partitions/Core | CPU Score Multiplier |
|---|---|---|---|
| Old (2015-2017 Xeon E5) | 100-128MB | 2x | 1.0x (baseline) |
| Medium (2018-2020 Xeon 8280) | 128-256MB | 2.6x | 1.3x |
| Modern (2021-2023 EPYC 7763) | 256-512MB | 3.4x | 1.7x |
| Latest (2024+ Turin/Sapphire Rapids) | 256-512MB | 3.6x | 1.8x |

**Formula for partition count**:
```
partitions = (executor_cores × partitions_per_core) × CPU_score_multiplier
```

---

## 7. Memory Pressure & Garbage Collection

### Garbage Collection Pause Time

- Should be < 10% of total task time
- Monitor via Spark UI: "GC Time" in task metrics
- Excessive GC indicates memory pressure or inefficient collection tuning

### Executor Memory Tuning

Set `spark.executor.memory` and memory fractions for execution vs storage:
```
spark.executor.memory = 4-8GB (typical)
spark.memory.fraction = 0.6 (60% for execution, 40% for storage)
spark.memory.storageFraction = 0.5 (within memory.fraction)
```

### JVM Heap Size

- Default may be insufficient for high-volume workloads
- Tune based on data size and partition count
- Monitor via JVM metrics or Ganglia/Prometheus

### GC Algorithm Choice

- **G1GC**: Better for large heaps (>4GB), predictable pauses
- **CMS**: Lower pause times but less throughput
- **ZGC/Shenandoah**: Ultra-low pause times, not always available

---

## 8. Data Characteristics Affecting Hardware Needs

### Data Skew

Uneven distribution of keys requires more partitions to distribute work evenly.

- **Skewed data**: Use 4-8x cores (instead of 2-4x) to distribute hot keys
- **Partition size**: Reduce to 64-128MB for better distribution
- Example: Salting technique creates artificial keys for even distribution

### Data Compression Ratio

Compressed data changes effective size vs actual size.

- **Highly compressed**: Larger partition size (256-512MB) since effective size is smaller
- **Uncompressed**: Smaller partition size (128MB) to avoid memory pressure
- Example: Parquet with Snappy compression: ~4:1 ratio

### Row Size

Larger rows reduce scan efficiency; network bandwidth becomes bottleneck faster.

- Small rows (< 1KB): Can use larger partitions
- Large rows (> 10KB): Use smaller partitions
- Formula: `network_throughput = rows_per_sec × avg_row_size_kb / 1024`

### Serialization Format

Different formats have different throughput characteristics.

- **JSON**: Fastest serialization, ~100-200MB/s
- **AVRO**: Compact binary, ~80-150MB/s
- **Parquet**: Excellent compression, ~50-100MB/s (but great for storage)
- **Protobuf**: Compact, ~70-120MB/s

---

## 9. Cluster-Level Considerations

### Executor Count

Affects broadcast memory overhead and cluster utilization.

- **Broadcast memory cost**: `total_broadcast_mem = broadcast_size × num_executors`
- More executors = more copies = higher aggregate memory usage
- Trade-off between parallelism and broadcast efficiency

### Driver Memory

Often the bottleneck for broadcast operations:
- Driver must hold entire broadcast table before distribution
- Ensure: `broadcast_size < (spark.driver.memory × 0.3)`
- Typical: 4-8GB driver memory

### Task Scheduling Fairness

Avoid overwhelming the scheduler.

- Keep total task count within 10,000-50,000 range
- Too many tasks = scheduler overhead and context switching
- Too few tasks = underutilized cores

### Resource Utilization Target

Design for optimal CPU usage during peak load:
- Target: 80-90% CPU utilization
- < 80%: Too few partitions, underutilized hardware
- > 90%: Risk of scheduling overhead and GC pressure

---

## 10. Real-World Shuffle Performance Impact

**Scenario: 1TB Shuffle Across 10 Executors (80 cores total)**

### Old Hardware (Intel Xeon E5-2680 v2, 2013)

```
Optimal Partitions: 80-160
Memory Bandwidth: 50 GB/s per socket (~100 GB/s total)
Shuffle Write Time: ~40 minutes
Peak Memory Pressure: Significant spill-to-disk
Partition Size: 128MB (conservative)
Task Count: ~41 effective (due to SMT)
```

### Modern Hardware (AMD EPYC 7763, 2021)

```
Optimal Partitions: 240-320
Memory Bandwidth: 120 GB/s per socket (~1.2 TB/s total)
Shuffle Write Time: ~12 minutes (3.3x faster!)
Peak Memory Pressure: Minimal spilling
Partition Size: 256-512MB (larger, more efficient)
Task Count: ~46 effective (due to SMT)
```

**Result**: Same cluster size, but **modern CPUs = 3.3x faster shuffle** due to architecture improvements.

---

## 11. Network Broadcast Optimization

### Max Broadcast Size by Executor Memory

Safe broadcast sizes based on executor heap:

| Executor Memory | Recommended Max Broadcast | Conservative Max |
|---|---|---|
| 4GB | 200-400MB | 200MB |
| 8GB | 400-800MB | 600MB |
| 16GB | 800MB-1.5GB | 1GB |
| 32GB+ | 1-2GB | 1.5GB |

### Broadcast Size Formula

```
optimal_threshold = min(
    executor_memory × 0.15,
    driver_memory × 0.25,
    network_transfer_budget,
    cluster_memory / (num_executors × 3)
)
```

### Memory Pressure Indicators

- Monitor GC time in Spark UI (should be < 10% of task time)
- Watch for OOM errors or excessive spilling to disk
- Track executor memory usage via metrics or monitoring systems

---

## 13. Software Stack & OS-Level Factors

### CPU Frequency Scaling & Power Management

Power-saving features can reduce throughput when not properly tuned.

- **CPU Turbo Boost/Turbo Core**: Must be enabled for peak performance; disabling can reduce throughput by 10-20%
- **Frequency Scaling Governors** (Linux):
  - `performance`: Always max frequency (best throughput)
  - `ondemand`: Scales with load (acceptable, minor overhead)
  - `powersave`: Reduces frequency aggressively (reduces throughput significantly)
- **P-States vs C-States**:
  - P-States (performance states): CPU frequency levels; impact throughput
  - C-States (C-sleep): CPU sleep modes; can cause wake latency
- **Recommendation**: Set to `performance` governor on production systems

### NUMA and Memory Locality

Critical for multi-socket systems (most production clusters).

- **NUMA Impact**: 30-50% throughput penalty for remote socket memory access
- **Inter-socket communication**: ~4x latency increase vs local access
- **Optimization**:
  - Enable NUMA awareness in Spark: pin tasks to local NUMA nodes
  - Use `numactl` on Linux to bind processes to specific sockets
  - Monitor with `numastat` for memory migration patterns
  - Keep executor memory allocation on single NUMA node when possible

### Thread Pool & Task Scheduling Overhead

Excessive threading and scheduling overhead can bottleneck throughput.

- **Context Switching Cost**: Each context switch = ~1-10 microseconds
- **Total Task Count**: Keep between 10,000-50,000 for reasonable scheduler latency
- **Too Many Partitions**: Scheduling overhead grows quadratically with task count
- **Thread Affinity**: Binding threads to specific cores can improve cache locality by 5-15%
- **Spark Executor Task Thread Pools**: Configure based on core count; default is reasonable but can be tuned

### Operating System Tuning

Linux kernel settings significantly impact throughput.

| OS Parameter | Tuning | Impact |
|---|---|---|
| TCP Window Size | `net.ipv4.tcp_rmem/wmem` | +10-20% network throughput |
| TCP Buffer | `net.core.rmem_max/wmem_max` | +5-15% for high-latency networks |
| File Descriptor Limits | `ulimit -n` | Critical for many connections |
| Network MTU | 9000 (jumbo frames) | +5-10% for large transfers |
| Dirty Buffer Threshold | `vm.dirty_ratio` | Affects I/O scheduling |
| Swappiness | `vm.swappiness=0` | Prevents disk swapping (critical) |

---

## 14. Thread Binding & CPU Affinity

### CPU Core Affinity

Binding tasks to specific CPU cores prevents migration overhead.

- **Core Migration**: Thread moving between cores causes L1/L2 cache invalidation
- **Cost**: 5-15% throughput penalty per migration
- **Benefit of Binding**: 10-20% improvement for cache-sensitive workloads
- **Spark Implementation**: Less direct control; depends on OS scheduler
- **Best Practice**: Run one task per core when possible (avoid oversubscription)

### NUMA Binding

For multi-socket systems (16+ cores).

```bash
# Linux: Bind Spark executor to single NUMA node
numactl --cpunodebind=0 --membind=0 spark-submit ...

# Check memory locality
numastat -n    # Shows local vs remote memory access
```

---

## 15. Polling Interval & Batching Effects

### Poll Interval Impact (CDC & Streaming Systems)

Polling intervals affect both throughput and latency significantly.

| Poll Interval | Throughput | Latency | Overhead |
|---|---|---|---|
| 1000ms (default) | Baseline | Baseline | Baseline |
| 500ms | +50-100% | -50% | 2x polling overhead |
| 100ms | +200-300% | -90% | 10x polling overhead |
| 50ms | +300-400% | -95% | Risk of overwhelming system |

**Trade-off Formula**: `optimal_interval = (average_record_size × network_latency) / available_bandwidth`

### Batch Size Effects

Larger batches increase throughput but add latency.

| Batch Size | Throughput | Latency | Memory |
|---|---|---|---|
| 1000 (default) | Baseline | Baseline | Baseline |
| 5000 | +300-400% | +4-5x | +5x |
| 10000 | +500-600% | +8-10x | +10x |

**Optimal Range**: 2000-5000 for CDC workloads; monitor memory pressure.

---

## 16. Serialization & Compression Overhead

### Serialization Throughput Comparison

Different serialization formats have vastly different performance characteristics.

| Format | Serialization Speed | Compression Ratio | Use Case |
|---|---|---|---|
| JSON | ~100-200 MB/s | 1:1 (no compression) | Human-readable, lightweight |
| AVRO | ~80-150 MB/s | 2:1 | Schema evolution, Kafka |
| Parquet | ~50-100 MB/s | 3-5:1 | Storage, analytical queries |
| Protobuf | ~70-120 MB/s | 2-3:1 | Compact binary |
| Kryo (Spark) | ~200-300 MB/s | 1.5:1 | Internal RDD serialization |

**Impact**: Choosing wrong format can reduce throughput by 30-50%.

### Compression Codec Trade-offs

Compression adds CPU overhead but reduces network bandwidth.

| Codec | Speed | Ratio | CPU Cost | Recommendation |
|---|---|---|---|---|
| LZ4 | ~500 MB/s | 2:1 | Very low | Best for high throughput |
| Snappy | ~200-300 MB/s | 3:1 | Low | Balanced choice |
| Gzip | ~50 MB/s | 5:1 | High | Only for storage |
| Zstd | ~100-200 MB/s | 4:1 | Medium | Good balance |

**Formula**: `compression_worth_it = (network_bytes_saved / (cpu_cycles_spent)) > 1`

---

## 17. File Format & Block Size Effects

### Parquet Block Size Tuning

Block size directly affects read throughput and memory usage.

| Block Size | I/O Pattern | Memory per Block | Throughput Impact |
|---|---|---|---|
| 64MB | Random access friendly | Low | -10% (too small) |
| 128MB (default) | Balanced | Medium | Baseline |
| 256MB | Streaming workload | Medium-High | +5-10% |
| 512MB | Large sequential reads | High | +10-20% |

**Recommendation**: Match to network MTU and memory availability; 256-512MB for Spark jobs.

### Small Files Problem

Numerous small files severely degrade throughput.

- **File Open Overhead**: ~5-50ms per file regardless of size
- **Metadata Listing**: ~100-1000ms per 10,000 files
- **Optimal File Size**: 128MB - 1GB per file
- **Impact of Small Files**: Can reduce throughput by 50-90% compared to properly sized files

**Formula**: `minimum_file_count = total_data_size / optimal_file_size`

---

## 18. Kafka-Specific Throughput Factors (CDC Pipelines)

### Broker Partitioning & Parallelism

Number of Kafka partitions directly limits parallel consumption.

- **Partitions < Consumers**: Some consumers idle; throughput = `partitions / total_consumers`
- **Partitions = Consumers**: Optimal; full parallelism
- **Partitions > Consumers**: Uneven load distribution
- **Recommendation**: Partitions ≥ expected consumer count; typically 2-4x cores

### Producer Throughput Limits

Kafka producer settings cap maximum achievable throughput.

| Setting | Value | Impact |
|---|---|---|
| `batch.size` | 3000-5000 | Larger batches → higher throughput |
| `linger.ms` | 100-500 | Longer wait → more batching |
| `buffer.memory` | 64MB | Affects burst capability |
| `compression.type` | snappy/lz4 | Reduces size by 40-60% |
| `acks` | 1 (vs all) | Single replica faster but less durable |

**Expected Impact**: Optimized producers achieve 10-50x vs default configuration.

### Replication & In-Sync Replicas (ISR)

Durability vs throughput trade-off.

| Config | Throughput | Durability | Use Case |
|---|---|---|---|
| `acks=1` | Highest | Single broker | Non-critical data |
| `acks=all, min.isr=1` | Medium | Async replicas | Balanced |
| `acks=all, min.isr=2` | Lower | Guaranteed replicas | Critical data |

---

## 19. Task Scheduling & Queuing Effects

### Queue Depth & Backpressure

Queuing adds latency and can reduce throughput under load.

- **Queue Depth < 2x CPU cores**: No backpressure, optimal throughput
- **Queue Depth 2-5x cores**: Acceptable queuing, minimal impact
- **Queue Depth > 5x cores**: Significant queuing latency, potential GC pressure
- **Optimal Target**: Keep queue depth < 100ms of processing time

### Task Duration Distribution

Uneven task durations cause stragglers and reduce throughput.

- **Ideal**: All tasks finish within 10% of each other
- **Acceptable**: 20-30% variance
- **Poor**: >50% variance (indicates data skew or resource contention)
- **Impact of Stragglers**: Job waits for slowest task; throughput reduced by straggler percentage

---

## 20. Data Format & Schema Evolution

### Schema Compatibility & Evolution Cost

Schema mismatches force data reprocessing.

| Approach | Compatibility | Overhead | Throughput Impact |
|---|---|---|---|
| No schema evolution | None | 0% | Best |
| Compatible adds (Avro) | Full forward | 2-5% | Minimal |
| Type changes | None | 100% (reprocess) | Worst |
| Column rearrangement | None | 20-30% (shuffle) | Significant |

**Recommendation**: Use Avro with schema registry for systems requiring evolution.

---

## 21. Throughput Optimization Checklist

### Hardware Assessment

- [ ] Benchmark CPU generation (PassMark or DIY Spark benchmark)
- [ ] Verify memory type and bandwidth (DDR3/4/5)
- [ ] Check network connectivity (1Gbps/10Gbps/etc)
- [ ] Ensure storage is SSD-backed for fast I/O
- [ ] Verify CPU frequency scaling is set to `performance`
- [ ] Check NUMA configuration (`numactl -H`)
- [ ] Verify TCP tuning parameters

### Partition Tuning

- [ ] Calculate partition count = (cores × partitions_per_core) × CPU_multiplier
- [ ] Target: 128-512MB per partition (based on hardware age)
- [ ] Align partitions with storage block boundaries (128-256MB)
- [ ] Verify file sizes are 128MB-1GB (avoid small file problem)
- [ ] Check block size is optimal for workload (256-512MB recommended)

### Performance Monitoring

- [ ] Monitor task duration (target 100ms-1s per task)
- [ ] Track shuffle bytes written in Spark UI
- [ ] Monitor memory pressure (target < 75% of executor memory)
- [ ] Check for spill-to-disk (should be minimal)
- [ ] Monitor queue depth (should be < 2x cores)
- [ ] Track GC time (should be < 10% of total time)
- [ ] Monitor context switch rate (via system tools)

### Configuration Optimization

- [ ] Enable Adaptive Query Execution (AQE): `spark.sql.adaptive.enabled=true`
- [ ] Set broadcast threshold based on memory: `spark.sql.autoBroadcastJoinThreshold=50MB` (tune based on cluster)
- [ ] Configure shuffle partitions: `spark.sql.shuffle.partitions = cores × 3` (baseline)
- [ ] Tune GC: Consider G1GC for executors > 4GB
- [ ] Set serialization to Kryo: `spark.serializer=org.apache.spark.serializer.KryoSerializer`
- [ ] Configure TCP settings for network throughput
- [ ] Set kernel swappiness to 0: `vm.swappiness=0`

### CDC/Streaming Optimization (if applicable)

- [ ] Tune polling interval: start with 500ms (not 1000ms default)
- [ ] Set batch size to 3000-5000 (not 1000 default)
- [ ] Enable compression: `compression.type=snappy`
- [ ] Use appropriate serialization format (AVRO for schema evolution)
- [ ] Configure Kafka broker partitions >= expected consumers

### Validation

- [ ] Run benchmark on 10-20% production data load
- [ ] Compare performance across different partition counts (100, 200, 400, 800)
- [ ] Validate improvement with production load
- [ ] Test with realistic CPU throttling / frequency scaling
- [ ] Monitor NUMA memory access patterns
- [ ] Document final optimal values for reproducibility

---

## Quick Reference: Hardware-Based Throughput Multipliers

Use these multipliers to estimate throughput improvement from hardware upgrades:

### CPU Architecture Impact

| Upgrade Path | Throughput Multiplier |
|---|---|
| Xeon E5 (2013) → Xeon 8280 (2018) | 1.3x |
| Xeon E5 (2013) → EPYC 7763 (2021) | 1.7x |
| Xeon 8280 (2018) → EPYC 7763 (2021) | 1.3x |
| EPYC 7763 (2021) → Sapphire Rapids (2023) | 1.06x |

### Memory Bandwidth Impact (Shuffle Workloads)

| Upgrade Path | Shuffle Performance Multiplier |
|---|---|
| DDR3 → DDR4 | 3-4x |
| DDR4 → DDR5 | 1.4-1.5x |
| Combined CPU + Memory | 2-5x total improvement |

### Network Impact (Data Transfer)

| Network Type | Throughput vs 1Gbps |
|---|---|
| 1Gbps | 1x (baseline) |
| 10Gbps | 10x |
| 40Gbps | 40x |

---

## Quick Reference: Hardware-Based Throughput Multipliers

Use these multipliers to estimate throughput improvement from hardware upgrades:

### CPU Architecture Impact

| Upgrade Path | Throughput Multiplier |
|---|---|
| Xeon E5 (2013) → Xeon 8280 (2018) | 1.3x |
| Xeon E5 (2013) → EPYC 7763 (2021) | 1.7x |
| Xeon 8280 (2018) → EPYC 7763 (2021) | 1.3x |
| EPYC 7763 (2021) → Sapphire Rapids (2023) | 1.06x |

### Memory Bandwidth Impact (Shuffle Workloads)

| Upgrade Path | Shuffle Performance Multiplier |
|---|---|
| DDR3 → DDR4 | 3-4x |
| DDR4 → DDR5 | 1.4-1.5x |
| Combined CPU + Memory | 2-5x total improvement |

### Network Impact (Data Transfer)

| Network Type | Throughput vs 1Gbps |
|---|---|
| 1Gbps | 1x (baseline) |
| 10Gbps | 10x |
| 40Gbps | 40x |

### Configuration & Software Impact

| Optimization | Throughput Multiplier |
|---|---|
| Batch size increase (1000 → 5000) | +3-4x |
| Poll interval decrease (1000ms → 500ms) | +0.5-1x |
| Compression enabled (snappy) | +1.2-1.4x (vs uncompressed) |
| Proper serialization (Kryo vs Java) | +2-3x |
| CPU frequency scaling (powersave → performance) | +1.1-1.3x |
| OS swappiness (enabled → disabled) | +1.05-1.2x |
| File size optimization (small files → 256MB) | +5-10x |
| NUMA awareness + binding | +1.2-1.5x |
| TCP tuning (buffer sizes optimized) | +1.1-1.3x |

### Combined Optimization Impact

Stacking multiple optimizations yields multiplicative improvements:

```
Final Throughput = Baseline × 1.7 (CPU) × 1.4 (Memory) × 1.2 (Serialization) 
                              × 1.3 (Config) × 1.1 (OS Tuning)
                 = Baseline × 4.2 - 4.8x

Example: 100K records/sec baseline → 420K-480K records/sec with all optimizations
```

---

## References

- [Apache Spark Tuning Guide](https://spark.apache.org/docs/latest/tuning.html)
- [Databricks Blog: Adaptive Query Execution](https://databricks.com/blog/2021/08/04/adaptive-query-execution-brings-spark-sql-in-line-with-state-of-the-art-databases.html)
- [PassMark CPU Benchmarks](https://passmark.com)
- [Intel Xeon Processor Specifications](https://www.intel.com/content/www/us/en/products/details/processors/xeon/scalable.html)
- [AMD EPYC Processor Specifications](https://www.amd.com/en/products/specifications/processors/data-center/amd-epyc)
- [Linux NUMA & Memory Management](https://www.kernel.org/doc/html/latest/vm/numa.html)
- [Kafka Performance Tuning](https://kafka.apache.org/documentation/#performance)
- [TCP Tuning for Linux](https://aws.amazon.com/blogs/networking-and-content-delivery/tcp-tuning-for-distributed-systems/)
- [Parquet Best Practices](https://parquet.apache.org/docs/file-format/)

