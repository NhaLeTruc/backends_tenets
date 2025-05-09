# Key mechanisms for High Availability

## HAProxy & pgbouncer vs pgpoolII

PgPoolII is a generalist software which try to provide features of both a proxy and a connection pooler. Because of this it doesn't do anything too well.

PgBouncer is a simple lightweight specialist which provide only connection pooling, but it does that very well.

HAProxy is a specialized proxy, and it performs proxy tasks better than PgPoolII on the same hardware. Given that PgBouncer is so lightweight, it should be colocated on the same servers as the control panes and worker nodes. Thus on the same hardwares, HAProxy + PgBouncer would most likely outperforms PgPoolII in load balancing and connection pooling.

However PgPoolII could perform query routing (write/read splitting) out of the box. A feature lacking in both HAProxy (possible with complex configurations) and Pgbouncer (can't do at all).

PgPoolII therefore is best use in case which strict control over connection requests has been obtained. So that PgPoolII would receive only optimal amount of requests for its server hardwares e.g. test environments. Since it is simpler to setup and configure relative to HAProxy + PgBouncer.

## Integration of Failover Mechanisms with Load-Balancing Techniques

Failover mechanisms work in tandem with load- balancing strategies to ensure that PostgreSQL databases remain operational and accessible even during failures. Load balancing distributes the database workload across multiple servers, while failover ensures that if a primary server fails, the traffic is rerouted to a standby server without interruption.

+ **Failover in load- balancing setups:** In a typical load-balanced PostgreSQL environment, tools such aslike HAProxy or PGpool-II are configured to distribute database requests across several servers. If the primary server fails, the failover mechanism promotes a standby server, and the load balancer immediately redirects traffic to the new primary. This seamless transition ensures that users experience no downtime or disruptions in service.
+ **Coordinating failover and load balancing:** To achieve high availability, the failover and load balancing systems must work closely together. For example, HAProxy continually monitors the health of PostgreSQL servers. When the failover mechanism promotes a standby server, HAProxy updates its routing rules in real -time, directing queries to the new primary server without user intervention. Similarly, PGpool-II manages both load balancing and failover, making it a powerful all-in-one solution for high-availability PostgreSQL setups.
+ **Replication Manager (repmgr):** A traditional failover system used for managing failover in Postgres databases, i. It was initially designed to simplify the creation of Postgres replicas. Written in C, repmgr uses a custom consensus system similar to Raft, requiring at least three nodes to function correctly. While it supports wWitness nodes, each wWitness stores its data in its own Postgres® database, which can complicate deployment. It provides configuration options for endpoints and includes hook scripts to manage load balancers, proxies, and virtual IPs. It also offers hooks for custom fencing strategies, failover consensus, and other advanced features. Due to the need for manual scripting, repmgr is mostly recommended for advanced users.

### Load Balancing

This process involves routing database requests— – such as queries or transactions— – across multiple servers or nodes. It helps maintain efficient performance by sharing the workload, ensuring that no server becomes a bottleneck. For example, read operations can be distributed across replica servers, improving response times and reducing pressure on the primary server.

### Failover

The critical role of safeguarding PostgreSQL systems to ensure robust data availability.

Failover is the automatic switching to a backup system or server when the primary system fails. In a high- availability setup, if one PostgreSQL server goes offline or becomes unresponsive, a failover mechanism ensures that another server immediately takes over the operations without interrupting the service. This process is seamless, allowing businesses to continue functioning without noticeable disruption.

#### Automated vs. Manual Failover Strategies

+ **Automated failover:** In this strategy, failover occurs automatically when a failure is detected. Tools such aslike PGpool-II and Patroni monitor the health of primary and standby servers and, upon detecting an issue, promote a standby server to replace the failed primary. Automated failover minimizes human intervention and dramatically reduces downtime, making it ideal for applications requiring continuous availability. However, it’s essential to implement safeguards, such as quorum-based voting systems, to avoid false failovers, in whichwhere the primary is erroneously considered to be down.
+ **Manual Failover:** In a manual failover scenario, system administrators intervene to promote a standby server in the event of a failure. This approach provides greater control over the failover process and can be useful in scenarios in whichwhere the risk of accidental failover needs to be tightly controlled. Manual failover requires careful monitoring and experienced administrators, but it offers flexibility in environments where downtime can be tolerated for short periods and where failover decisions must be made with caution.

## HAProxy

HAProxy is an open source software widely used for load balancing and proxying TCP and HTTP-based applications, including PostgreSQL databases. It serves as an intermediary between clients and PostgreSQL servers, distributing incoming requests across multiple servers to prevent overload and ensure system reliability.

HAProxy sits between PostgreSQL clients and servers, intelligently routing traffic based on server availability and health. Its real-time monitoring capabilities ensure that only fully operational servers handle database requests, significantly reducing the risk of downtime. When a server fails, HAProxy automatically redirects traffic to healthy nodes, making it a key player in PostgreSQL’s high availability architecture.

> Key benefits

+ Scalability: By distributing load among multiple servers, HAProxy ensures that the PostgreSQL system can handle an increased number of simultaneous connections and provide continual optimal performance as demand grows.
+ Reliability: HAProxy offers robust failure management by redirecting traffic to standby servers if a primary instance goes down. This aids significantly in maintaining continuous database availability.
+ Failover support: Automatic failover capabilities enable seamless transition to backup systems, minimizing downtime and impact on users during server failures or maintenance.

## PGpool-II

PGpool-II goes beyond basic load balancing by offering advanced features, such as connection pooling, query routing, and in-depth failover management. As a middleware solution, it is highly effective in optimizing resource use and managing multiple connections in large-scale PostgreSQL deployments.

PGpool-II balances the load by distributing read queries across replica servers, while write queries are directed to the primary server. This helps improve performance, especially in read-heavy environments. PGpool-II can be configured to support synchronous and asynchronous replication setups, providing flexibility in how databases are managed.

> Key benefits

+ Connection pooling: PGpool-II reduces the overhead of establishing new connections by pooling existing connections. This allows the database to serve more clients simultaneously with reduced latency.Connection pooling: PGpool-II reduces the overhead of establishing new connections by pooling existing connections. This allows the database to serve more clients simultaneously with reduced latency.
+ Query routing: It intelligently routes queries to appropriate servers, ensuring efficient use of resources. For instance, read queries can be sent to replica servers, while write operations are handled by the master.Query routing: It intelligently routes queries to appropriate servers, ensuring efficient use of resources. For instance, read queries can be sent to replica servers, while write operations are handled by the master.
+ Failover management: Similar to HAProxy, PGpool-II provides failover capabilities. If a primary server goes down, it automatically promotes a standby server and reroutes traffic accordingly, ensuring business continuity.Failover management: Similar to HAProxy, PGpool-II provides failover capabilities. If a primary server goes down, it automatically promotes a standby server and reroutes traffic accordingly, ensuring business continuity.

