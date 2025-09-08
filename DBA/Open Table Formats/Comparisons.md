# Comparison of popular Open Table Formats

Open table formats like Delta Lake, Apache Iceberg, and Apache Hudi provide a layer of metadata on top of data lake files to offer `ACID transactions, schema evolution, and time travel`.

+ `Delta Lake` is Spark-native and good for Databricks environments. It offers ACID transactions via a transaction log. Best for Data lakes and data pipelines within Spark environments.
+ `Iceberg` is engine-agnostic and supports widespread adoption via scalable metadata management, and supports advanced schema evolution and partition evolution. Best for Data warehousing and broad analytics across multiple query engines.
+ `Hudi` excels in streaming-heavy workloads and real-time data processing with its native primary key support and indexing. Best for Streaming analytics and real-time processing.
+ `Lance` is newer, focused on ML with vector search. Designed for ML workloads, offering random access performance and built-in vector search capabilities. Best for Machine learning model training.
+ `Apache Paimon` is emerging for real-time lakehouse architectures. Optimized for real-time lakehouse architecture, combining streaming and traditional lake format features. Best for Real-time data ingestion and streaming analytics.

## Shared Features

All major open table formats offer features found in traditional databases, such as:

+ `ACID Transactions`: Ensure data reliability and consistency.
+ `Schema Evolution`: Allow for adding, deleting, or modifying columns in existing tables.
+ `Time Travel`: Enable querying historical versions of the data.
