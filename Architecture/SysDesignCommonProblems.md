# 8 Most Important System Design Concepts

## I. Read Heavy System

Typically solve by implementing caching strategies on READ heavy low churn data like product listings.

READ MORE:

1. [database-caching](https://www.prisma.io/dataguide/managing-databases/introduction-database-caching#:~:text=The%20main%20differences%20between%20read,or%20some%20separate%20cache%20provider.)

## II. High Write Traffic

Typically solve by implementing message queues for load balancing WRITE heavy traffic. While also setup LSM-tree (Log-Structured Merge-tree) database as backend.

An LSM (Log-Structured Merge-tree) tree is a data structure used in databases, particularly NoSQL databases, to optimize performance for write-heavy workloads. It's designed for efficient handling of inserts, updates, and deletes, making it well-suited for applications with high data ingestion rates.

### Core Concepts

- **In-Memory Data Structure (Memtable):**

Writes are initially stored in an in-memory data structure, often a balanced tree or skip list, to provide fast write operations.

- **Sorted String Tables (SSTables):**

When the Memtable becomes full, its data is flushed to disk as a sorted string table (SSTable).

- **Sequential Writes:**

SSTables are written sequentially to disk, minimizing random I/O and maximizing write throughput.

- **Hierarchical Structure:**

LSM trees often organize SSTables into a hierarchical structure, with newer, less sorted SSTables at the bottom and older, more sorted SSTables at the top.

- **Bloom Filter:**

Bloom filters are used to quickly determine if a key exists in a particular SSTable, improving read performance.

### How LSM Trees Work

1. **Writes:** When a write operation is received, it's initially stored in the Memtable.
2. **Flushing:** When the Memtable reaches its capacity, its contents are sorted and written to a new SSTable on disk.
3. **Merging (Compaction):** To optimize storage and improve read performance, multiple SSTables may be merged into larger ones, removing redundant data.
4. **Reads:** Reads start by checking the Memtable for the desired key. If not found, the Bloom filter is used to quickly determine which SSTables might contain the key.
5. **Sequential Access:** If the key is likely in an SSTable, the LSM tree sequentially accesses the SSTables, starting with the most recent and moving towards older ones.

### Advantages of LSM Trees

1. **High Write Throughput:** LSM trees are optimized for high write speeds due to the sequential writing of SSTables.
2. **Efficient Data Storage:** They allow for compact and efficient storage of data on disk.
3. **Good Read Performance:** Read operations are optimized through the use of Bloom filters and hierarchical organization of SSTables.
4. **Well-Suited for NoSQL:** They are particularly well-suited for NoSQL databases that handle large amounts of unstructured or semi-structured data with high data ingestion rates.

Examples of Databases Using LSM Trees:

Cassandra: Apache Cassandra
RocksDB: RocksDB
LevelDB: LevelDB
ScyllaDB: ScyllaDB
DynamoDB: DynamoDB

### Disadvantages of LSM Trees

1. **Read Performance:** LSM-trees are optimized for writes, and reads can be slower compared to B-trees. Reads may involve searching multiple levels of data in Sorted String Tables (SSTables), potentially leading to slower lookup times. Compaction, while improving read performance over time, can also add to read amplification, making reads slower in some cases.
2. **Write Amplification:** Due to compaction, data may be written to disk multiple times, leading to write amplification. This can increase storage requirements and potentially shorten the lifespan of Solid State Drives (SSDs).
3. **Space Usage:** LSM-trees can require more storage space compared to B-trees, especially with size-tiered compaction strategies. Compaction processes and the need for multiple copies of data at different levels contribute to increased space usage.
4. **Compaction Overhead:** Compaction is a resource-intensive process that can impact both read and write performance. Compression, decompression, data copying, and key comparison during compaction can add to the processing overhead.
5. **Deletion Challenges:** Deleting data in an LSM-tree can be tricky because it doesn't typically support in-place replacement. Deletion operations can involve merging SSTables, which can impact performance and increase write amplification.
6. **Data Reordering:** In LSM-trees, when multiple cache-lines are written to persistent memory (PM), the writes may not follow the order of the instructions issued by the CPU, causing a data reordering problem.
7. **Large memory requirements:** LSM tree requires a large amount of memory to hold the memtable, which can be a problem for systems with limited memory. Not good for random access workloads: LSM tree is not well suited for random access workloads, where data is accessed randomly.

## III. Slow Databasse Queries

Potential remedies:

- Indexing (might slows WRITE)
- Partitioning
- Sharding
  - Range based
  - Hash based
  - Consistent hashing
  - Virtual bucket sharding

## IV. Handling Large Files

**Object storage and block storage** are two distinct types of data storage, each with its own strengths and weaknesses. Block storage divides data into fixed-size blocks and is optimized for fast access, while object storage stores data as individual objects with metadata, making it ideal for large volumes of unstructured data

### Block Storage

**How it works:** Block storage divides data into equal-sized blocks, which are then stored on underlying physical storage.

**Advantages:**

- **Fast Access:** Block storage allows for rapid retrieval of data due to its direct access to blocks.
- **Good for structured data:** Ideal for storing structured data like databases and virtual machines.

**Disadvantages:**

- **Expensive:** Requires storage area networks (SANs) and can be costly to manage.
- **Limited metadata:** Lacks rich metadata capabilities, making it less suitable for unstructured data.

### Object Storage

**How it works:** Object storage stores data as individual objects, each with a unique identifier and associated metadata.

**Advantages:**

- **Scalability:** Highly scalable for large volumes of data.
- **Cost-effective:** Can be more cost-effective for storing large amounts of unstructured data.
- **Rich metadata:** Supports rich metadata, making it suitable for unstructured data and search capabilities.

**Disadvantages:**
May not be suitable for transactional data: Not ideal for applications requiring frequent, small transactions.

Key Differences:

|Feature | Block Storage | Object Storage |
|---|---|---|
| Data Organization | Divided into fixed-size blocks | Stored as individual objects with metadata  |
| Access Speed | Fast, direct access to blocks | Object retrieval, potentially slower for small, frequent transactions |
| Metadata | Limited metadata | Rich metadata capabilities |
| Use Cases | Databases, virtual machines, high-performance applications | Large volumes of unstructured data, backups, archives, data lakes |
| Scalability | Less scalable than object storage | Highly scalable |
| Cost | Can be expensive, especially at scale | Potentially more cost-effective for large volumes of unstructured data |

---

In summary: Choose block storage for scenarios requiring fast access to structured data, while object storage is preferred for large volumes of unstructured data, backups, archives, and distributed data storage. Most system employs both where appropriate.

## V. Single Point of Failure

High available systems compose of leader(s) and replicas for its services ensure there is no single server failure which could bring down the entire system.

## VI. High Availability

Load balancing; failover; backup; and replication ensure a collection of interconnected nodes (servers) could withstand production uncertainties and maintain high availability throughout.

## VII. High Latency

CDN Caching; Edge computing; and multi-leaders system help leviate high latency problem in widely distributed systems.

## VIII. Monitoring and Alerting

### Distributed tracing

Distributed tracing is a technique that helps developers understand how requests flow through distributed systems, like those using microservices. It provides visibility into the interactions between different services and components, aiding in debugging, performance optimization, and understanding user experiences.

Distributed tracing is a method of observing requests as they propagate through distributed cloud environments. It follows an interaction and tags it with a unique identifier. This identifier stays with the transaction as it interacts with microservices, containers, and infrastructure.

**How it works:**

- **Request Tracking:** A unique identifier (trace ID) is assigned to a request as it enters the system.
- **Span Creation:** Each service or component that handles the request logs information about its part of the process, including timings and relevant details, creating a "span".
- **Trace Composition:** Spans from different services are combined into a single trace, providing a complete view of the request's journey.
- **Analysis and Visualization:** Distributed tracing tools allow developers to analyze the trace data, identify performance bottlenecks, and pinpoint errors.

**Benefits of Distributed Tracing:**

- **Improved Troubleshooting:** Pinpointing the exact location and cause of performance issues or errors in a complex system.
- **Performance Optimization:** Identifying bottlenecks and slow-running services to improve system performance.
- **Enhanced Observability:** Gaining a deeper understanding of how different services interact and how they contribute to the overall user experience.
- **Collaboration:** Facilitating communication and collaboration between different development teams working on different services.
- **Faster Time to Resolution:** Accurately diagnosing and resolving issues leads to faster recovery and reduced downtime.

### Distributed tracing tools

- OpenTelemetry
- Grafana Tempo
- Sentry

### Alerting

Keep alerting to real problems by log analysis (Kafka + Flink).
