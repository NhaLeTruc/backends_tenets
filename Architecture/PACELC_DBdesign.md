# The PACELC (Partition, Availability, Consistency, Else, Latency, Consistency)

The PACELC (Partition, Availability, Consistency, Else, Latency, Consistency) design principle is a framework for understanding and managing trade-offs in distributed systems, building upon the CAP theorem. Wikipedia describes it as an extension to CAP, focusing on how systems behave both **during network partitions (P) and under normal operation (E)**. It highlights that while a distributed system must choose between **availability and consistency during a partition** (as in CAP), it must also choose between **latency and consistency in normal operation** (otherwise, or "else").

Distributed systems are the backbone of modern computing, powering everything from cloud platforms to e-commerce applications. While the CAP theorem provided a foundational understanding of trade-offs in distributed systems, it left out critical considerations for normal operations. The PACELC theorem, introduced by Daniel J. Abadi, fills this gap by addressing trade-offs not only during network partitions but also during regular operation.

PACELC Theorem is a concept in distributed computing that provides insight into the trade-offs between **consistency and latency** in distributed databases. PACELC stands for Partition, Availability, Consistency, Else, Latency, and Consistency. The theorem states that in the event of a network partition, a distributed system must choose between availability and consistency; otherwise, it must choose between latency and consistency. This theorem has implications on system design and performance, particularly in the context of data processing and analytics for data scientists and technology professionals.

## Key aspects of PACELC

- **Partition (P):** Represents network partitions or failures that can isolate parts of the system.
- **Availability (A):** Ensuring that the system is accessible and responsive during normal operation and in the event of failures.
- **Consistency (C):** Maintaining data integrity and ensuring that all replicas of the data are synchronized.
- **Else (E):** Refers to the situation when the system is not experiencing a partition, i.e., normal operation.
- **Latency (L):** The time it takes for the system to respond to requests.

PACELC provides a framework for understanding these trade-offs:

- **PA/EL:** Prioritizes availability during partitions and low latency otherwise.
- **PA/EC:** Prioritizes availability during partitions and strong consistency otherwise.
- **PC/EL:** Prioritizes consistency during partitions and low latency otherwise.
- **PC/EC:** Prioritizes consistency at all times.

In essence, PACELC guides system designers to make informed decisions about the balance between availability, consistency, and latency, particularly in the context of distributed data processing and analytics

## The Limitation of CAP

The CAP theorem states that in the event of a network partition (P), distributed systems must choose between Consistency (C) and Availability (A). However, CAP does not address trade-offs when there is no partition, leaving out a critical aspect of system design—performance under normal conditions.

- **Latency Matters:** In real-world applications, latency (response time) is often as critical as availability and consistency.
- **Everyday Trade-offs:** Even without partitions, distributed systems must balance consistency and latency to meet user expectations.

We cannot avoid partition in a distributed system, therefore, according to the CAP theorem, a distributed system should choose between consistency or availability. ACID (Atomicity, Consistency, Isolation, Durability) databases, such as RDBMSs like MySQL, Oracle, and Microsoft SQL Server, chose consistency (refuse response if it cannot check with peers), while BASE (Basically Available, Soft-state, Eventually consistent) databases, such as NoSQL databases like MongoDB, Cassandra, and Redis, chose availability (respond with local data without ensuring it is the latest with its peers).

One place where the CAP theorem is silent is what happens when there is no network partition? What choices does a distributed system have when there is no partition?

## PACELC’s Solution

PACELC extends CAP by introducing a second trade-off: when there is no partition (Else mode), systems must choose between Latency (L) and Consistency (C). This dual-layered approach ensures that both failure scenarios and normal operations are considered.

## How does PACELC work?

The PACELC theorem expands on CAP by introducing two operational modes:

1. **Partition Mode (PAC):** During network partitions, systems face the same trade-off as CAP—availability vs. consistency.
2. **Else Mode (ELC):** When there are no partitions, systems face a trade-off between latency and consistency.

## Key Difference

While CAP focuses exclusively on handling failures due to partitions, PACELC adds nuance by addressing performance trade-offs under normal conditions, making it more comprehensive for modern distributed systems.

## Trade-Offs Between Latency and Consistency in Real-World Applications

In distributed systems operating without partitions, the primary trade-off is between latency and consistency:

### 1. Consistency Requires Coordination

- Strong consistency ensures that all users see the same data simultaneously.
- Achieving this requires coordination between nodes, which increases response time.
- Example: Financial systems like stock trading platforms prioritize consistency to ensure accurate data but accept higher latency.

### 2. Low Latency Relaxes Consistency

- Low-latency systems prioritize speed by allowing eventual consistency.
- These systems respond quickly but may return stale or inconsistent data.
- Example: Social media platforms like Twitter often prioritize low latency to deliver fast user experiences.

## Use Cases for Each Trade-Off

- Applications requiring accurate data (e.g., banking) lean toward strong consistency.
- Applications prioritizing user experience (e.g., gaming) lean toward low latency. By explicitly incorporating these trade-offs into system design, PACELC enables architects to optimize for specific application requirements.

## Real-World Applications of PACELC

1. **Cloud Computing** Cloud providers like AWS design their services using PACELC principles:
2. **DynamoDB** operates as a PA/EL system to ensure high availability and low latency for global-scale applications.
3. **Google Spanner** follows PC/EC principles to maintain strong consistency across geographically distributed nodes.
4. **E-Commerce Platforms** E-commerce platforms like Amazon prioritize availability to ensure uninterrupted user access but balance this with consistent inventory records using PA/EC configurations.
5. **Online Gaming** Gaming platforms often prioritize low latency over strict consistency to provide seamless gameplay experiences under normal conditions.
6. **Financial Services** Financial databases prioritize strong consistency over availability or latency to ensure compliance with regulations and accurate transaction records.

## References

1. [beyond-cap](https://dev.to/ashokan/beyond-cap-unveiling-the-pacelc-theorem-for-modern-systems-465j)
