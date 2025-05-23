# System Design Trade-Offs

## SQL vs NoSQL

SQL typically process robust querying; consistency assuring capabilities, but is hard to scale horizontally; and grow data volumes. NoSQL is the opposite.

## Normalization vs Denormalization

Normalization: deduplicate data for data storage efficiency; WRITE efficiency; and data integrity.
Denormalization: duplicate data for READ efficiency

Normalization introduces increased querying cost as data volumes grow. Denormalization speed up query by increase data duplications. Thus they trades data storage efficiency; WRITE efficiency; and data integrity for READ efficiency and vice versa.

## CAP theorem

The CAP Theorem, also known as Brewer's Theorem, is a fundamental concept in distributed computing that states a distributed data store cannot simultaneously guarantee all three properties: Consistency, Availability, and Partition Tolerance. Essentially, it means you can only choose two of these three properties in a distributed system.

Here's a breakdown of each property:

**Consistency:**
All nodes in the system see the same data at the same time, meaning every read operation should receive the most recent write or an error according to AlgoMaster Newsletter.

Consistency exists on a spectrum between strong and eventual consistency. Synchronous replication (strong) ensure minimum latency between leader and replicas synchronization, but come at greater computational and network cost than asynchronous (eventual) replication.

Asynchronous replicas can also be utilized for healthy leader election due to them being slightly behind whatever update(s) may cause the leader(s) to fail.

**Availability:**
Every request (read or write) receives a non-error response, even if the system is experiencing issues like network partitions, with no guarantee of receiving the most recent write according to AlgoMaster Newsletter.

**Partition Tolerance:**
The system continues to operate despite network issues, such as a network partition where communication between nodes is disrupted according to AlgoMaster Newsletter.

## Batch vs Stream processing

Batch processing handles large amounts of data in discrete chunks at scheduled intervals, while stream processing deals with data continuously and incrementally as it arrives. Batch processing is suitable for tasks where speed isn't crucial, like scheduled reporting or historical analysis, while stream processing is ideal for real-time scenarios requiring immediate insights, such as fraud detection or real-time analytics.

### Batch Processing

- **Data Handling:** Processes data in bulk at scheduled times.
- **Latency:** Higher latency as data is processed periodically.
- **Cost:** Can be cost-effective, especially when leveraging existing infrastructure and scheduling jobs during off-peak times.
- **Use Cases:** Suitable for tasks like large-scale data aggregation, historical reporting, and ETL (Extract, Transform, Load) processes.
- **Complexity:** Generally less complex to manage, as data is handled in bulk at scheduled intervals.

### Stream Processing

- **Data Handling:** Processes data continuously as it arrives, analyzing it in real-time or near real-time.
- **Latency:** Low latency, as data is processed immediately, enabling immediate insights.
- **Cost:** Generally involves higher upfront costs due to specialized infrastructure requirements.
- **Use Cases:** Ideal for scenarios requiring immediate insights, such as real-time analytics, fraud detection, recommendation engines, and monitoring systems.
- **Complexity:** More complex to manage, requiring specialized skills and thorough robustness and recovery.

## Stateful vs Stateless

In computing, "stateful" and "stateless" refer to how applications handle information between requests. Stateful applications maintain information about past interactions, while stateless applications treat each request as independent, with no memory of previous interactions.

### Stateless Applications

- **No persistence:** Each request is handled as a new, isolated event, without relying on previous interactions.
- **Data handling:** Applications must include all necessary data in each request to be processed.
- **Benefits:** Easier to scale, simpler to implement, and more fault-tolerant.
Examples: REST APIs, HTTP protocol.

### Stateful Applications

- **Preserved state:** Applications store information about past interactions, allowing them to remember previous events.
- **Data handling:** Information is often stored in databases or server-side storage.
- **Benefits:** Facilitate personalized experiences and maintain continuity across user interactions.
Examples: Database applications, online banking, email servers.
