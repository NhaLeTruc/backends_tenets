# Skew Handling

Spark's repartition, salting, and bucketing are techniques used to manage data distribution and improve performance, particularly when dealing with data skewness.

1. `repartition()`:
+ **Purpose:**
Redistributes data across a specified number of partitions, either increasing or decreasing the number of partitions.
+ **Mechanism:**
Involves a full shuffle of data across the cluster, which can be a costly operation.
+ **Use Case:**
Useful for controlling the parallelism of subsequent operations or for addressing general data distribution issues, but not specifically designed to handle data skew on particular keys.

2. `Salting`:
+ **Purpose:**
Mitigates data skewness in operations like joins or aggregations by distributing skewed keys more evenly across partitions.
+ **Mechanism:**
Involves adding a random "salt" value to the skewed key before performing the operation. This creates new, more evenly distributed keys, which are then used for partitioning or grouping.
+ **Use Case:**
Employed when a specific key in a dataset has a highly uneven distribution, leading to performance bottlenecks during operations that require data shuffling based on that key.

3. `Bucketing`:
+ **Purpose:**
Organizes data into a fixed number of buckets based on the hash of a chosen column, optimizing performance for specific operations like joins and aggregations on that column.
+ **Mechanism:**
Data is hashed based on the bucketed column and placed into a pre-defined number of files (buckets). This process involves an initial shuffle and sort.
+ **Use Case:**
Beneficial for frequently joined or aggregated tables where the join/aggregation key has a high cardinality and you want to avoid repeated shuffles for these operations. Bucketing information is stored in the metastore.

## Key Differences and When to Choose

+ **Data Skew Focus:**
Salting directly addresses data skewness on specific keys, while repartition() offers general control over partition count, and bucketing optimizes for recurring operations on specific columns.

+ **Pre-computation vs. On-the-fly:**
Bucketing is a pre-computation step that organizes data for future queries, whereas salting is applied dynamically during operations to handle skew. repartition() is also a dynamic operation.

+ **Overhead:**
repartition() and salting involve shuffles during execution. Bucketing has an initial overhead during table creation but can significantly reduce shuffle costs for subsequent operations.

+ **Flexibility:**
Salting offers more flexibility in handling skewed keys dynamically, while bucketing requires pre-defining the number of buckets. repartition() provides basic control over partition count.

In essence, repartition() is a general tool for managing parallelism, salting is a targeted solution for data skew, and bucketing is a persistent optimization for frequently accessed data based on specific columns.
