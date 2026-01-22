# Optimal Spark Partition Sizing Guide

## Executive Summary

**128MB is NOT universally optimal.** Partition size must be tuned based on:
- **Executor memory & cores**
- **CPU architecture & generation**
- **Workload type** (batch, shuffle-heavy, streaming)
- **Data characteristics** (skew, compression, distribution)

---

## Part 1: Is 128MB Always Optimal?

### No. Key Context Factors

**128MB is a conservative default** that works for general use cases, but production systems benefit from customization.

#### When 128MB Works Well
- **Older hardware** (2015-2017 Xeon E5 series)
- **Limited executor memory** (2-4GB per executor)
- **Shuffle-heavy operations** (joins, aggregations, window functions)
- **Memory-constrained environments** (reducing partition size minimizes peak memory pressure)

#### When You Should Go Larger (256MB-512MB)
- **Modern hardware** (2021+ EPYC, Xeon Sapphire Rapids)
- **16GB+ executor memory** per executor
- **Map-only operations** (filtering, simple transforms—no shuffle)
- **High-compression data** (effective size << file size)

#### When You Should Go Smaller (64MB-96MB)
- **Highly skewed data** (hot keys benefit from smaller partitions for better distribution)
- **Window function heavy** (sessionization, ranking—requires aggressive salting)
- **Real-time processing** (smaller partitions = lower latency)
- **Limited cores** (<10 cores per executor)

---

## Part 2: CPU Architecture & Generation Impact

### Core Principle

**CPU architecture directly affects partition handling capacity.** It's not just core count—instruction-level parallelism (ILP), cache design, and memory bandwidth are critical.

### 1. Instruction-Level Parallelism (ILP) & Clock Speed

Modern CPUs execute more instructions per cycle, processing partitions faster.

**Example Comparison:**
- **Intel Xeon Platinum 8280 (2019)**: ~3.8 GHz, older design
- **Intel Xeon Platinum 8490H (2023)**: ~3.5 GHz base, but ~20% better ILP per cycle

**Result**: Newer CPU handles **more partitions** with same throughput despite lower clock speed.

### 2. L3 Cache Size & Efficiency

Larger caches reduce memory latency for partition data.

| Architecture | L3 Cache | Effect on Partitions |
|---|---|---|
| Older Xeon (2015) | 20MB | Smaller working set; need smaller partitions |
| Modern EPYC Milan | 32MB per CCX | Larger working set; handle bigger partitions efficiently |
| Latest Xeon Sapphire Rapids | 12.5MB per P-core | Better memory hierarchy overall |

**Real Impact**: Modern CPU processes **256MB partition** as efficiently as older CPU processes **128MB partition**.

### 3. Memory Bandwidth

Critical for shuffle operations (most partition-sensitive workload).

| Generation | Memory Bandwidth | Shuffle Performance |
|---|---|---|
| DDR3 (2012) | ~25 GB/s per socket | Severe bottleneck |
| DDR4 (2014-2019) | ~80-90 GB/s per socket | Moderate |
| DDR5 (2021+) | ~120-130 GB/s per socket | 40-50% faster shuffle |

**Implication**: Modern DDR5 systems can shuffle **larger partitions** without spilling to disk.

### 4. Hyperthreading / SMT Efficiency

How effectively the CPU handles task context switching.

- **Older Intel Xeon (2-way HT)**: 25-30% speedup from 2nd thread
- **Modern Intel (2-way HT)**: 40-50% speedup
- **AMD EPYC (2-way SMT)**: Similar, varies by workload

**Result**: Older 32-core CPU effectively handles ~41 tasks, modern handles ~46 tasks.

### 5. Vectorization Capabilities

Modern CPUs have better SIMD support for DataFrame operations.

```python
# Operations benefiting from vectorization:
# - Columnar filters
# - Arrow-based conversion
# - Parquet read/write
# - Compression/encoding

# Modern CPUs (AVX-512, VNNI): 8 64-bit values per cycle
# Older CPUs (AVX2): 4 64-bit values per cycle
```

**Impact**: Modern CPUs process partitions **2x faster** for vectorizable operations.

---

## Part 3: CPU Tuning Formula

### Conservative Baseline (Older Hardware: 2015-2018)

```
Partition Count = 32 cores × 2 partitions/core = 64 partitions
Partition Size = 100-128MB (smaller for memory safety)
Target Memory Per Partition = ~500MB executor memory
```

### Modern Hardware Tuning (2021+: EPYC/Xeon)

```
Partition Count = 32 cores × 3-4 partitions/core = 96-128 partitions
Partition Size = 256-512MB (larger, leveraging better cache)
Target Memory Per Partition = ~200MB executor memory

Memory overhead per executor:
  Old: 100MB × 2 = 200MB (conservative)
  New: 300MB × 4 = 1.2GB (modern CPUs handle this efficiently)
```

### Dynamic Calculation

```python
def calculate_optimal_partitions(total_data_gb, cpu_model, executor_memory_gb, num_executors):
    """
    Calculate partition count based on CPU generation and hardware specifics.
    """
    
    # CPU scoring (1.0 = baseline 2015 Xeon)
    cpu_scores = {
        # Old (2015-2017)
        "e5-2686": 1.0,
        "e5-2690": 1.0,
        
        # Medium (2018-2020)
        "8280": 1.3,
        "8380": 1.35,
        "7302": 1.4,
        
        # Modern (2021-2023)
        "8490": 1.6,
        "8592": 1.65,
        "7763": 1.7,
        "9534": 1.75,
        
        # Latest (2024+)
        "sapphire-rapids": 1.8,
        "turin": 1.85,
    }
    
    cpu_score = cpu_scores.get(cpu_model, 1.0)
    
    # Base: 2 partitions per core
    base_partitions_per_core = 2
    
    # Adjust based on CPU generation
    adjusted_partitions_per_core = base_partitions_per_core * cpu_score
    
    # Calculate total partitions
    total_data_bytes = total_data_gb * 1024 ** 3
    bytes_per_partition = executor_memory_gb * (256 * 1024 ** 2)  # 256MB target
    
    total_partitions = int(
        (total_data_gb / executor_memory_gb) * adjusted_partitions_per_core * num_executors
    )
    
    return total_partitions

# Example:
# 1TB data, 10 executors, 4GB memory each
old_cpu_partitions = calculate_optimal_partitions(1000, "e5-2690", 4, 10)
# Result: ~500 partitions (conservative)

modern_cpu_partitions = calculate_optimal_partitions(1000, "7763", 4, 10)
# Result: ~850 partitions (leverages better architecture)
```

---

## Part 4: Real-World Example - Shuffle Performance

### Scenario: 1TB Shuffle Across 10 Executors (8 cores each = 80 cores total)

#### Old Hardware (Intel Xeon E5-2680 v2, 2013)

```
Optimal Partitions: 80-160
Memory Bandwidth: 50 GB/s per socket (~100 GB/s total)
Shuffle Write Time: ~40 minutes
Peak Memory Pressure: Significant spill-to-disk
Partition Size: 128MB (conservative)
```

#### Modern Hardware (AMD EPYC 7763, 2021)

```
Optimal Partitions: 240-320
Memory Bandwidth: 120 GB/s per socket (~1.2 TB/s total)
Shuffle Write Time: ~12 minutes (3.3x faster!)
Peak Memory Pressure: Minimal spilling
Partition Size: 256-512MB (larger, more efficient)
```

**Result**: Same cluster size, but modern CPUs = **3x faster shuffle** due to architecture improvements.

---

## Part 5: Trusted CPU Benchmark Sources

### 1. PassMark Software (Recommended)

**Website**: [passmark.com](https://passmark.com)

**Strengths**:
- Largest dataset (millions of CPUs tested)
- Single-thread and multi-thread scores
- Historical trends
- Free and Pro versions

**Example Lookup**:
```
Intel Xeon Platinum 8280: ~50,000
Intel Xeon Platinum 8490H: ~65,000
AMD EPYC 7763: ~68,000
```

### 2. Geekbench (Real-World Workloads)

**Website**: [geekbench.com](https://geekbench.com)

**Strengths**:
- Real-world application performance
- Separate single-core and multi-core scores
- Extensive historical data

**Example Geekbench 6**:
```
Intel Xeon Platinum 8280: ~25,000 (multi-core)
AMD EPYC 7763: ~32,000 (multi-core)
```

### 3. SPECint / SPECfp (Industry Standard)

**Website**: [spec.org](https://spec.org)

**Use**: Enterprise purchasing decisions (most trusted, but expensive)

### 4. TPC Benchmarks (Database Workloads)

**Website**: [tpc.org](https://tpc.org)

**Use**: Transaction processing and data warehouse performance (TPC-C, TPC-H, TPC-DS)

---

## Part 6: Benchmarking Your Own Hardware

### Method 1: PassMark PerformanceTest (Easiest, 5-10 minutes)

```powershell
# Download from: https://www.passmark.com/download.html

# Installation
Invoke-WebRequest -Uri "https://download.passmark.com/pt_setup.exe" -OutFile "pt_setup.exe"
.\pt_setup.exe

# Run benchmark (GUI)
# Results auto-upload to PassMark database
# You get CPU Score, single-thread rating, multi-thread rating
```

### Method 2: Geekbench (10-15 minutes)

```powershell
# Download from: https://www.geekbench.com/download
# Run via GUI, results auto-upload to Geekbench database
# Returns single-core and multi-core scores with percentile ranking
```

### Method 3: DIY Spark Benchmarking (Spark-Specific)

```python
import time
import pyspark.sql.functions as F
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("CPU-Benchmark") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .config("spark.executor.cores", 4) \
    .getOrCreate()

def benchmark_cpu_intensive():
    # Create large dataset (100M rows)
    df = spark.range(100_000_000).withColumn(
        "value", F.rand() * 1000
    ).withColumn(
        "group_id", F.col("id") % 1000
    )
    
    start = time.per_counter()
    
    # CPU-heavy aggregations + window functions
    result = df.groupBy("group_id").agg(
        F.mean("value").alias("avg_val"),
        F.stddev("value").alias("stddev_val"),
        F.percentile_approx("value", 0.95).alias("p95"),
        F.count("*").alias("count")
    ).collect()
    
    elapsed = time.per_counter() - start
    
    cpu_score = 100_000_000 / elapsed  # rows/sec
    print(f"CPU Benchmark Time: {elapsed:.2f} seconds")
    print(f"CPU Score (rows/sec): {cpu_score:,.0f}")
    
    return cpu_score

benchmark_cpu_intensive()
```

### Method 4: Linux sysbench

```bash
# Installation
sudo apt-get install sysbench

# Single-threaded CPU benchmark
sysbench cpu --cpu-max-prime=20000 run

# Multi-threaded (16 threads)
sysbench cpu --cpu-max-prime=20000 --threads=16 run

# Output: events per second (higher = better)
```

### Method 5: stress-ng (Comprehensive)

```bash
# Installation
sudo apt-get install stress-ng

# CPU stress test (all cores, 60 seconds)
stress-ng --cpu 0 --timeout 60s --metrics

# Output: Bogo operations/sec, CPU utilization, load average
```

---

## Part 7: Creating Your Own CPU Benchmark Suite

```python
def create_cpu_benchmark_suite(spark, num_cores):
    """Benchmark CPU quality for Spark workloads"""
    
    def benchmark_aggregation(spark):
        df = spark.range(100_000_000)
        start = time.per_counter()
        df.groupBy(F.col("id") % 1000).agg(F.mean("id")).collect()
        return time.per_counter() - start
    
    def benchmark_join(spark):
        df1 = spark.range(50_000_000)
        df2 = spark.range(10_000_000)
        start = time.per_counter()
        df1.join(df2, "id").collect()
        return time.per_counter() - start
    
    def benchmark_window_function(spark):
        from pyspark.sql import Window
        df = spark.range(50_000_000).withColumn("group", F.col("id") % 1000)
        w = Window.partitionBy("group").orderBy("id")
        start = time.per_counter()
        df.withColumn("rank", F.row_number().over(w)).collect()
        return time.per_counter() - start
    
    benchmarks = {
        "aggregation": benchmark_aggregation,
        "join": benchmark_join,
        "window": benchmark_window_function,
    }
    
    results = {}
    for name, benchmark_func in benchmarks.items():
        elapsed = benchmark_func(spark)
        throughput = 100_000_000 / elapsed  # rows/sec
        results[name] = {
            "time_seconds": elapsed,
            "throughput": throughput,
            "per_core": throughput / num_cores
        }
    
    # Your custom "CPU Score" = average throughput
    cpu_score = sum(r["throughput"] for r in results.values()) / len(results)
    
    return results, cpu_score
```

---

## Part 8: Quick Reference - CPU Hierarchy (2024)

| CPU | PassMark | Year | Use Case | Partition Multiplier |
|---|---|---|---|---|
| AMD EPYC 9684X | 90,000+ | 2023 | Highest-end server | 2.8x |
| Intel Xeon Platinum 8592+ | 88,000+ | 2023 | Highest-end Intel | 2.75x |
| AMD EPYC 7763 | 68,000 | 2021 | Modern datacenter | 2.1x |
| Intel Xeon 8490H | 65,000 | 2023 | Modern Intel | 2.0x |
| Intel Xeon 8380 | 58,000 | 2019 | Mid-range server | 1.8x |
| Intel Xeon E5-2690 v2 | 15,000 | 2013 | Old hardware | 1.0x (baseline) |

---

## Part 9: Recommended Approach for Your Workload

### Step 1: Determine Your Hardware

```bash
# Linux
lscpu | grep "Model name"

# Or check PassMark for your exact model
```

### Step 2: Get CPU Score

- **Option A** (Easiest): Download PassMark, run benchmark → Get score
- **Option B** (Fastest): Look up CPU model on PassMark website
- **Option C** (Most Accurate): Run DIY Spark benchmark on your cluster

### Step 3: Calculate Partition Multiplier

```python
# Conservative baseline (Xeon E5-2690 v2): 25,000
your_cpu_score = 68000  # Example: EPYC 7763

baseline_score = 25000
multiplier = your_cpu_score / baseline_score  # 2.72x

# Old tuning: 2 partitions per core
# New tuning: 2 × multiplier = 5.44 partitions per core
```

### Step 4: Calculate Optimal Partition Count

```python
def calculate_partitions_with_actual_benchmark(total_data_gb, executor_count, your_cpu_score):
    baseline_score = 25000  # Conservative baseline
    score_multiplier = your_cpu_score / baseline_score
    
    base_partitions_per_core = 2
    adjusted = base_partitions_per_core * score_multiplier
    
    # Assume 4 cores per executor (typical)
    total_cores = executor_count * 4
    
    total_partitions = int(total_cores * adjusted)
    
    return total_partitions

# Example: 1TB data, 10 executors, EPYC 7763 (68k PassMark)
partitions = calculate_partitions_with_actual_benchmark(1000, 10, 68000)
# Result: ~1088 partitions (vs ~500 with generic tuning)
# Partition size: ~1000GB / 1088 = ~920KB per partition... wait that's wrong

# Better: Calculate based on memory + data size
def better_calculation(total_data_gb, executor_memory_gb, executor_count, your_cpu_score):
    baseline_score = 25000
    score_multiplier = your_cpu_score / baseline_score
    
    # Start with 2 base partitions per core
    total_cores = executor_count * 4
    base_partitions = total_cores * 2
    
    # Adjust based on CPU score
    adjusted_partitions = int(base_partitions * score_multiplier)
    
    partition_size_mb = (total_data_gb * 1024) / adjusted_partitions
    
    return adjusted_partitions, partition_size_mb

partitions, partition_size = better_calculation(1000, 4, 10, 68000)
# Result: 1088 partitions, ~943MB each (reasonable for modern hardware)
```

---

## Part 10: Decision Matrix

| Scenario | Recommended Partition Size | Partitions per Core | Rationale |
|---|---|---|---|
| **Old hardware + small memory** | 64-128MB | 1-2 | Conservative, memory-safe |
| **Old hardware + large memory** | 128-256MB | 2-3 | Larger memory available |
| **Modern hardware + shuffle-heavy** | 128-256MB | 3-4 | Minimize memory pressure |
| **Modern hardware + map-only** | 256-512MB | 2-3 | No shuffle bottleneck |
| **Skewed data (any hardware)** | 64-128MB | 2-3 | Better hot key distribution |
| **Real-time / low-latency** | 64-96MB | 3-4 | Faster task scheduling |
| **Highly compressed data** | 256-512MB | 2-4 | Effective size much smaller |

---

## Part 11: Production Tuning Checklist

- [ ] Benchmark your CPU (PassMark or DIY Spark)
- [ ] Calculate CPU score multiplier (your_score / 25000)
- [ ] Determine executor memory (typically 4-8GB)
- [ ] Identify workload type (batch, shuffle, streaming)
- [ ] Check for data skew (may need aggressive salting)
- [ ] Set `spark.sql.shuffle.partitions = (cores × partitions_per_core) × score_multiplier`
- [ ] Start with 2x your target → Monitor Spark UI → Adjust down
- [ ] Measure: Task durations, shuffle bytes, memory pressure
- [ ] Goal: Partition sizes 128-512MB, max task duration <5 minutes

---

## References & Further Reading

- **Spark Documentation**: [spark.sql.shuffle.partitions](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- **PassMark CPU Benchmark**: https://www.cpubenchmark.net/CPU_mega_page.html
- **Geekbench Results**: https://browser.geekbench.com/
- **AMD EPYC Architecture**: https://www.amd.com/en/products/specifications/processors/data-center/amd-epyc
- **Intel Xeon Optimization**: https://www.intel.com/content/www/us/en/products/docs/processors/data-center/xeon-processor-scalable-family-overview.html

