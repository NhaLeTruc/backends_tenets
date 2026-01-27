import math
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional

class CPUGeneration(Enum):
    """CPU architecture generations with throughput multipliers"""
    OLD_XEON_E5_2013 = 1.0      # Baseline
    MEDIUM_XEON_8280_2018 = 1.3
    MODERN_EPYC_7763_2021 = 1.7
    LATEST_SAPPHIRE_RAPIDS_2023 = 1.8

class MemoryType(Enum):
    """Memory bandwidth impact"""
    DDR3_2012 = 25      # GB/s per socket
    DDR4_2014 = 80      # GB/s per socket
    DDR5_2021 = 120     # GB/s per socket

class DataCharacteristic(Enum):
    """Data characteristics affecting partition sizing"""
    SKEWED = 0.6        # Requires smaller partitions (4-8x cores)
    BALANCED = 1.0      # Normal distribution
    COMPRESSED = 1.3    # Larger partitions (compressed data)

@dataclass
class HardwareConfig:
    """Hardware configuration for a distributed cluster"""
    total_cores: int                    # Total executor cores across cluster
    executor_memory_gb: float           # Per-executor memory in GB
    num_executors: int                  # Number of executors
    cpu_generation: CPUGeneration       # CPU architecture
    memory_type: MemoryType             # Memory type (DDR3/4/5)
    network_bandwidth_gbps: float       # Network bandwidth in Gbps
    is_multi_socket: bool = True        # Multi-socket system (affects NUMA)
    has_ssd: bool = True                # SSD storage available
    
@dataclass
class WorkloadConfig:
    """Workload characteristics"""
    total_data_size_gb: float           # Total data to process
    avg_row_size_bytes: float           # Average row size
    compression_ratio: float = 1.0      # Data compression ratio (1.0 = no compression)
    is_skewed: bool = False             # Data skew distribution
    is_streaming: bool = False          # Streaming vs batch
    shuffle_intensive: bool = True      # Heavy shuffle operations
    
@dataclass
class PartitionRecommendation:
    """Recommended partition configuration"""
    num_partitions: int
    partition_size_mb: float
    partitions_per_core: float
    expected_task_duration_ms: float
    memory_per_partition_mb: float
    shuffle_throughput_mbs: float
    estimated_total_runtime_seconds: float
    notes: list

class PartitionCalculator:
    """Calculate optimal partition count and size for distributed data processing"""
    
    # Constants
    MIN_PARTITION_SIZE_MB = 64
    MAX_PARTITION_SIZE_MB = 512
    TARGET_TASK_DURATION_MS = 500      # Optimal: 100ms-1s
    GC_OVERHEAD_PERCENT = 0.10         # Reserve 10% for GC
    MEMORY_SAFETY_FACTOR = 0.75        # Keep peak memory at 75% of allocated
    
    def calculate(
        self, 
        hardware: HardwareConfig, 
        workload: WorkloadConfig
    ) -> PartitionRecommendation:
        """
        Calculate optimal partition configuration
        
        Args:
            hardware: Hardware configuration
            workload: Workload characteristics
            
        Returns:
            PartitionRecommendation with detailed breakdown
        """
        notes = []
        
        # Step 1: Calculate base partition count from CPU cores
        base_partitions_per_core = self._get_base_partitions_per_core(hardware, workload)
        cpu_multiplier = hardware.cpu_generation.value
        
        base_num_partitions = int(
            hardware.total_cores * base_partitions_per_core * cpu_multiplier
        )
        notes.append(f"Base partitions (cores={hardware.total_cores}, ppcore={base_partitions_per_core}, cpu_mult={cpu_multiplier}): {base_num_partitions}")
        
        # Step 2: Calculate partition size from available memory
        usable_memory_per_executor = self._get_usable_executor_memory(hardware)
        partition_size_from_memory = self._calculate_partition_size_from_memory(
            hardware, workload, usable_memory_per_executor
        )
        notes.append(f"Partition size from memory budget: {partition_size_from_memory:.1f}MB")
        
        # Step 3: Calculate partition size from network bandwidth
        partition_size_from_network = self._calculate_partition_size_from_network(
            hardware, workload
        )
        notes.append(f"Partition size from network budget: {partition_size_from_network:.1f}MB")
        
        # Step 4: Determine final partition size (most restrictive constraint)
        partition_size_mb = min(
            partition_size_from_memory,
            partition_size_from_network,
            self.MAX_PARTITION_SIZE_MB
        )
        partition_size_mb = max(partition_size_mb, self.MIN_PARTITION_SIZE_MB)
        notes.append(f"Final partition size (constrained): {partition_size_mb:.1f}MB")
        
        # Step 5: Calculate final partition count based on data size
        num_partitions = max(
            base_num_partitions,
            int(math.ceil(workload.total_data_size_gb * 1024 / partition_size_mb))
        )
        notes.append(f"Final partition count (constrained by data size): {num_partitions}")
        
        # Step 6: Apply data skew adjustment
        if workload.is_skewed:
            skew_multiplier = 4  # Use 4-8x more partitions for skewed data
            num_partitions = int(num_partitions * skew_multiplier)
            partition_size_mb = max(partition_size_mb / skew_multiplier, self.MIN_PARTITION_SIZE_MB)
            notes.append(f"Skewed data detected: multiplied partitions by {skew_multiplier}, reduced size to {partition_size_mb:.1f}MB")
        
        # Step 7: Calculate derived metrics
        partitions_per_core = num_partitions / hardware.total_cores
        memory_per_partition_mb = partition_size_mb / workload.compression_ratio
        shuffle_throughput_mbs = self._estimate_shuffle_throughput(hardware)
        expected_task_duration_ms = self._estimate_task_duration(
            partition_size_mb, shuffle_throughput_mbs
        )
        estimated_total_runtime = self._estimate_total_runtime(
            workload.total_data_size_gb,
            shuffle_throughput_mbs,
            hardware.total_cores
        )
        
        # Step 8: Validation checks
        if partitions_per_core > 10:
            notes.append(f"⚠️  WARNING: High partitions/core ratio ({partitions_per_core:.1f}). May cause scheduling overhead.")
        if partitions_per_core < 1:
            notes.append(f"⚠️  WARNING: Low partitions/core ratio ({partitions_per_core:.1f}). Cores may be underutilized.")
        if memory_per_partition_mb > usable_memory_per_executor * 0.8:
            notes.append(f"⚠️  WARNING: Partition memory ({memory_per_partition_mb:.1f}MB) near executor limit. Risk of spilling.")
        if expected_task_duration_ms < 100:
            notes.append(f"✓ Task duration ({expected_task_duration_ms:.0f}ms) is optimal (< 100ms threshold)")
        if expected_task_duration_ms > 2000:
            notes.append(f"⚠️  WARNING: Task duration ({expected_task_duration_ms:.0f}ms) is high. Consider smaller partitions.")
        
        return PartitionRecommendation(
            num_partitions=num_partitions,
            partition_size_mb=partition_size_mb,
            partitions_per_core=partitions_per_core,
            expected_task_duration_ms=expected_task_duration_ms,
            memory_per_partition_mb=memory_per_partition_mb,
            shuffle_throughput_mbs=shuffle_throughput_mbs,
            estimated_total_runtime_seconds=estimated_total_runtime,
            notes=notes
        )
    
    def _get_base_partitions_per_core(
        self, 
        hardware: HardwareConfig, 
        workload: WorkloadConfig
    ) -> float:
        """Determine base partitions per core based on workload type"""
        if workload.is_streaming:
            return 4.0  # Streaming needs more partitions for latency
        elif workload.shuffle_intensive:
            return 3.0  # Shuffle-heavy jobs benefit from more partitions
        else:
            return 2.5  # Default for general workloads
    
    def _get_usable_executor_memory(self, hardware: HardwareConfig) -> float:
        """Calculate usable memory per executor after overhead"""
        # Estimate executor memory overhead (~1.2GB for modern, ~0.2GB for old)
        if hardware.cpu_generation == CPUGeneration.OLD_XEON_E5_2013:
            overhead_gb = 0.2
        else:
            overhead_gb = 1.2
        
        usable = hardware.executor_memory_gb - overhead_gb
        return max(usable, hardware.executor_memory_gb * 0.75)  # At least 75% is usable
    
    def _calculate_partition_size_from_memory(
        self,
        hardware: HardwareConfig,
        workload: WorkloadConfig,
        usable_memory_per_executor: float
    ) -> float:
        """Calculate max partition size based on executor memory"""
        # Reserve memory: GC overhead + executor overhead + safety factor
        reserved_memory = usable_memory_per_executor * (self.GC_OVERHEAD_PERCENT + 0.1)
        available_memory = usable_memory_per_executor - reserved_memory
        
        # Assume 3-5 partitions in-flight per executor simultaneously
        partitions_in_flight = 4
        max_size_mb = (available_memory * self.MEMORY_SAFETY_FACTOR) / partitions_in_flight * 1024
        
        return max_size_mb
    
    def _calculate_partition_size_from_network(
        self,
        hardware: HardwareConfig,
        workload: WorkloadConfig
    ) -> float:
        """Calculate max partition size based on network bandwidth"""
        # Target: process partition in ~500ms to achieve target task duration
        network_bandwidth_mbs = hardware.network_bandwidth_gbps * 1000 / 8  # Convert Gbps to MB/s
        
        # Account for compression efficiency
        effective_bandwidth = network_bandwidth_mbs * (1 + (workload.compression_ratio - 1) / 2)
        
        # Partition should transfer in ~500ms for good throughput
        target_transfer_time_ms = 500
        max_size_mb = effective_bandwidth * (target_transfer_time_ms / 1000)
        
        return max_size_mb
    
    def _estimate_shuffle_throughput(self, hardware: HardwareConfig) -> float:
        """Estimate shuffle throughput in MB/s based on hardware"""
        # Memory bandwidth is primary determinant of shuffle performance
        memory_bandwidth_gbs = hardware.memory_type.value
        
        # Network bandwidth cap
        network_bandwidth_mbs = hardware.network_bandwidth_gbps * 1000 / 8
        
        # Shuffle throughput is limited by both
        # Real-world: memory bandwidth is typically the bottleneck
        shuffle_throughput = min(memory_bandwidth_gbs * 1000, network_bandwidth_mbs * 0.8)
        
        # Multi-socket penalty for remote memory access
        if hardware.is_multi_socket:
            shuffle_throughput *= 0.7  # ~30% penalty for NUMA traffic
        
        return shuffle_throughput
    
    def _estimate_task_duration(
        self,
        partition_size_mb: float,
        shuffle_throughput_mbs: float
    ) -> float:
        """Estimate task duration in milliseconds"""
        # Assume task is shuffle-write bound
        task_duration_ms = (partition_size_mb / shuffle_throughput_mbs) * 1000
        
        # Add fixed overhead for serialization, deserialization, etc.
        overhead_ms = 50
        
        return max(task_duration_ms + overhead_ms, 50)  # Minimum 50ms
    
    def _estimate_total_runtime(
        self,
        total_data_gb: float,
        shuffle_throughput_mbs: float,
        total_cores: int
    ) -> float:
        """Estimate total job runtime in seconds"""
        total_data_mb = total_data_gb * 1024
        
        # Runtime is limited by total data / (cores × throughput per core)
        # Assume 50% CPU utilization during shuffle
        effective_throughput_mbs = shuffle_throughput_mbs * (total_cores / 10) * 0.5
        
        runtime_seconds = total_data_mb / effective_throughput_mbs
        
        # Add overhead for initialization, finalization
        overhead_seconds = 30
        
        return runtime_seconds + overhead_seconds


# Example usage
if __name__ == "__main__":
    # Define hardware (typical production cluster)
    hardware = HardwareConfig(
        total_cores=80,
        executor_memory_gb=8.0,
        num_executors=10,
        cpu_generation=CPUGeneration.MODERN_EPYC_7763_2021,
        memory_type=MemoryType.DDR5_2021,
        network_bandwidth_gbps=10.0,
        is_multi_socket=True,
        has_ssd=True
    )
    
    # Define workload (1TB shuffle-heavy job)
    workload = WorkloadConfig(
        total_data_size_gb=1024,
        avg_row_size_bytes=100,
        compression_ratio=1.0,
        is_skewed=False,
        is_streaming=False,
        shuffle_intensive=True
    )
    
    # Calculate optimal partitions
    calculator = PartitionCalculator()
    recommendation = calculator.calculate(hardware, workload)
    
    print("=" * 80)
    print("PARTITION OPTIMIZATION RECOMMENDATION")
    print("=" * 80)
    print(f"\nOptimal Number of Partitions: {recommendation.num_partitions}")
    print(f"Partition Size: {recommendation.partition_size_mb:.1f} MB")
    print(f"Partitions per Core: {recommendation.partitions_per_core:.2f}")
    print(f"Memory per Partition: {recommendation.memory_per_partition_mb:.1f} MB")
    print(f"\nPerformance Estimates:")
    print(f"  Shuffle Throughput: {recommendation.shuffle_throughput_mbs:.0f} MB/s")
    print(f"  Expected Task Duration: {recommendation.expected_task_duration_ms:.0f} ms")
    print(f"  Estimated Total Runtime: {recommendation.estimated_total_runtime_seconds:.0f} seconds (~{recommendation.estimated_total_runtime_seconds/60:.1f} minutes)")
    print(f"\nNotes:")
    for i, note in enumerate(recommendation.notes, 1):
        print(f"  {i}. {note}")
    print("=" * 80)