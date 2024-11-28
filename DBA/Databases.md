# Databases

Database can be a bottleneck of the entire application. Below are some patterns that can help scale databases.

## 1. Indexing

Database indexing is a technique for organizing and storing data in a database in a way that allows it to be accessed and queried efficiently. A Database index is a data structure that is used to store a subset of the data in a database, and to provide fast access to the data based on the values in one or more columns.

When a query is executed, the database can use the index to quickly locate and retrieve the data that is needed to satisfy the query, without having to scan the entire database. This can improve the performance of the query and make it more efficient.

There are several types of indexes that can be used in a database, including primary indexes, secondary indexes, clustered indexes, and non-clustered indexes. The choice of index type depends on the data in the database and the type of queries that are being executed.

Creating indexes is one of the first things you should consider when you need to improve database read performance. To be able to create effective indexes, here are a few important things to consider:

- You need to know what index data structure works best for your particular use case. Most common index data structure is a B-Tree, it works well for most cases. But in some cases (like full text search, regex patterns like %text%) you may need something else, like GIN (Generalized Inverted Index) or Trigram Matching.
- Your query may need a full index, but in some cases a partial index can be a better choice
- When creating an index, an order of columns in an index may play a big role on how this index is going to perform. It is even possible to make query slower by creating a suboptimal index.
- While indexes can improve read performance, they slow down write performance since every time you insert something into a database each index has to be updated too. Create only minimum amount of indices that you will actually use, and remove all unused ones.

Indexing is a complex topic. Creating effective indexes requires deep understanding of how they work internally.

## 2. Replication

Data replication is when the same data is intentionally stored in more than one node.

Database replication is a technique for copying data from one database to another, in order to provide multiple copies of the data for fault tolerance, scalability, or performance. Database replication can be used to create a redundant copy of a database, or to distribute a database across multiple nodes or locations.

In database replication, data is copied from a source database to one or more target databases. The source and target databases can be located on the same server, or on different servers. The data can be copied asynchronously, which means that the source and target databases can operate independently of each other, and the data is copied in the background without interrupting the operation of the databases.

Database replication can provide several benefits, such as improved availability and fault tolerance, better performance and scalability, and easier data management and maintenance.

## 3. Partitioning

Database partitioning is a technique for dividing a database into smaller, independent parts, called partitions. The goal of partitioning is to improve the performance and scalability of the database by allowing data to be distributed across multiple partitions, and by allowing each partition to be managed and accessed independently of the others.

When you have large amounts of data that don't fit into one database partitioning is a logical next step to improve scalability.

There are several types of database partitioning, including:

- Horizontal partitioning: In this type of partitioning, rows of a database table are divided into multiple partitions based on the values in one or more columns. This allows different partitions to be managed and accessed independently of each other, and can improve the performance and scalability of the database.
- Vertical partitioning: In this type of partitioning, columns of a database table are divided into multiple partitions. This can help to reduce the size of each partition, and can make it easier to manage and access the data in the database.
- Range partitioning: In this type of partitioning, the rows of a database table are divided into multiple partitions based on the range of values in a specific column. This can be useful for managing data that has a natural range, such as dates or numbers.

Database partitioning is a technique that can improve the performance and scalability of a database by allowing data to be distributed across multiple partitions and managed independently.

## 4. Hot, Warm and Cold data

You can think about data as hot, cold or warm.

- Hot storage is data that is accessed frequently. For example blog posts created in the last couple of days will probably have a lot more attention than old posts.
- Warm storage is data that is accessed less frequently. For example blog posts that are created more than a week ago, but still get some attention from time to time.
- Cold storage is data that is rarely accessed. For example blog posts created long time ago that are rarely accessed nowadays.

When deciding what data to store where, it’s important to consider the access patterns. Hot data can be stored in a fast and expensive storage (SSDs), warm data can be stored in a cheaper storage (HDDs), and cold data can be stored on the cheapest storage.

## 5. Database Federation

Database Federation allows multiple databases to function as one, abstracting underlying complexity by providing a uniform API that can store or retrieve data from multiple databases using a single query.

For instance, using federated approach you can take data from multiple sources and combine it into a single piece, without your clients even knowing that this data comes from multiple sources.

A simple example can be a functional partitioning, when we split databases by some particular function or domain. For example, imagine we have "users", "wallets" and "transactions" tables. In a federated approach this could be 3 different databases. This can increase performance since load will be split across 3 databases instead of 1.

**Pros:**

- Federated databases can be more performant and scalable
- Easier to store massive volumes of data
- Single source of truth for your data, meaning there is one place where it is stored using a single schema/format (unlike in denormalized databases)

**But it also has its downsides:**

- You'll need to decide manually which database to connect to.
- Joining data from multiple databases will be much harder.
- More complexity in code and infrastructure.
- Consistency is harder to achieve since you lose ACID transactions

## 6. Denormalization

Denormalization is the process of trying to improve the read performance of a database by sacrificing some write performance by adding redundant copies of data.

Database denormalization is a technique for optimizing the performance of a database by adding redundant data to it. In a normalized database, data is organized into multiple, interconnected tables, with each table containing a unique set of data. This can improve the integrity and flexibility of the database, but can also result in complex and costly queries.

When denormalizing a database, data is copied or derived from one table and added to another, in order to reduce the number of table joins or other operations that are needed to retrieve the data. This can improve the performance of the database by reducing the amount of work that the database engine needs to do to satisfy a query, and can also reduce the amount of data that needs to be transmitted between the database engine and the application.

Database denormalization is often used in data warehousing and business intelligence applications, where complex and costly queries are common. It can also be used in other types of databases, such as operational databases, where the performance of the database is critical.

For example, instead of having separate "users" and "wallets" tables that must be joined, you put them in a single document that doesn't need any joins. This way querying database will be faster, and scaling this database into multiple partitions will be easier since there is no need to join anymore.

**Pros:**

- Reads are faster since there are fewer joins (or none at all)
- Since there is no joins it is easier to partition and scale
- Queries can be simpler to write

**Cons:**

- Writes (inserts and updates) are more expensive
- More redundancy requires more storage
- Data can be inconsistent. Since we have multiple copies of the same data, some of those copies may be outdated (or in some cases never updated at all, which is dangerous and must be handled by ensuring eventual consistency)

## 7. Materialized views

Materialized view is a pre-computed data set derived from a query specification and stored for later use.

Materialized view can be just a result of a SELECT statement:

```SQL
CREATE MATERIALIZED VIEW my_view AS SELECT * FROM some_table;
```

Result of this SELECT statement will be stored as a view so every time you query for it there is no need to compute the result again.

Materialized views can improve performance, but data may be outdated since refreshing a view can be an expensive operation that is only done periodically (for example once a day). This is great for some things like daily statistics, but not good enough for real time systems.

## 8. Multitenancy

Multitenant architecture is a design pattern for software applications that allows a single instance of the application to serve multiple tenants, or groups of users. In a multitenant architecture, the application is designed to isolate the data and resources of each tenant, so that each tenant can access and use the application independently of other tenants.

Multitenant architecture is often used in software as a service (SaaS) applications, where the application is provided to multiple tenants on a subscription basis. In this type of architecture, the application is designed to support multiple tenants, each with their own data and resources, and to provide each tenant with access to a specific instance of the application. This allows the application to be used by multiple tenants concurrently, without requiring each tenant to have their own separate instance of the application.

There are multiple tenancy models for databases:

- Single federated database for all tenants
- One database per tenant
- Sharded multi-tenant database
- And others

Which model to choose depends on a scale of your application.

## 9. SQL vs NoSQL

SQL, or relational, databases are good for structured data.

SQL databases are great for transaction-oriented systems that need strong consistency because SQL Databases are ACID compliant.

Relational databases can be very efficient at accessing well structured data, as it is placed in predictable memory locations.

Relational databases are usually scaled vertically. Because in relational databases data is structured and can have connections between tables it is harder to partition / scale horizontally.

Relational databases are a better choice as a main database for most projects, especially new ones, and can be good enough up to a few millions of active users, depending on a use case.

SQL databases include: MySQL, PostgreSQL, Microsoft SQL server, Oracle, MariaDB and many more. Cloud providers like AWS, GCP and Azure include their own relational database solutions.

NoSQL is a good choice for unstructured/non-relational data. Because unstructured data is usually self-contained and consists of independent objects with no relations, it is easier to shard/partition, thus it is easier to scale horizontally.

NoSQL / Non-Relational databases can be a good choice for large scale projects with more than few millions of active users (especially when you need to do sharding, because NoSQL with it's denormalized data is easier to shard), but since NoSQL databases lack ACID properties (NoSQL are usually eventually consistent) and relational structures, they are not the best choice as a main database for most projects, especially on a low scale.

Also, contrary to popular claims that NoSQL is faster, it's not always the case. In fact, for most of the typical query needs relational databases can be much faster (as described by this research: Performance benchmark: PostgreSQL/MongoDB), but ultimately everything depends on your query patterns.

NoSQL databases include: MongoDB, Cassandra, Redis and many more. Cloud providers like AWS, GCP and Azure include their own non-relational database solutions.

## 10. Identifiers

Identifiers (or primary keys) uniquely identify rows of data in tables, and make it easy to fetch data. It's important to know what options you have beyond serial integers and UUID v4, since on top of being unique (or globally unique GUIDs) your IDs can include encoded timestamp and/or other important metadata that can be used for efficient querying, sorting, better indexing locality, and other things. There are plenty of ID formats, like UUIDv7, Snowflake, ULID, or simply composite keys derived from your data. It's important to know which option is best to use for your database models and querying needs since it can improve your application performance dramatically.

## 11. Connection pooling

Opening and maintaining a database connection for each client is expensive (establishing TCP connection, process creation, etc.).

Connection pool is a cache of database connections maintained so that the connections can be reused when future requests to the database are required. After a connection is created, it is placed in the pool and reused again so that a new connection does not have to be established.

This can significantly improve performance when large amount of clients are connecting to the database at once.

For example, if you are using PostgreSQL, popular solutions include pgbouncer and pgcat. Though keep in mind that adding those technologies can come at a cost, more info here: PgBouncer is useful, important, and fraught with peril.

