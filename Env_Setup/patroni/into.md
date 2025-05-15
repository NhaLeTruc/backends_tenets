# Patroni Intro

Patroni is a template for high availability (HA) PostgreSQL solutions using Python. Patroni originated as a fork of Governor, the project from Compose. It includes plenty of new features.

## Planning the Number of PostgreSQL Nodes

Patroni/PostgreSQL nodes are decoupled from DCS nodes (except when Patroni implements RAFT on its own) and therefore there is no requirement on the minimal number of nodes. Running a cluster consisting of one primary and one standby is perfectly fine. You can add more standby nodes later.

## Replication Choices

Patroni uses Postgres’ streaming replication, which is asynchronous by default. Patroni’s asynchronous replication configuration allows for **maximum_lag_on_failover** settings. This setting ensures failover will not occur if a follower is more than a certain number of bytes behind the leader. This setting should be increased or decreased based on business requirements. It’s also possible to use synchronous replication for better durability guarantees.

## Applications Should Not Use Superusers

When connecting from an application, always use a non-superuser. Patroni requires access to the database to function properly. By using a superuser from an application, you can potentially use the entire connection pool, including the connections reserved for superusers, with the **superuser_reserved_connections** setting. If Patroni cannot access the Primary because the connection pool is full, behavior will be undesirable.

## Testing Your HA Solution

Testing an HA solution is a **time consuming process**, with many variables. This is particularly true considering a cross-platform application. You need a trained system administrator or a consultant to do this work. It is **not something we can cover in depth in the documentation.**

That said, here are some pieces of your infrastructure you should be sure to test:

- Network (the network in front of your system as well as the NICs [physical or virtual] themselves)
- Disk IO
- file limits (nofile in Linux)
- RAM. Even if you have oomkiller turned off, the unavailability of RAM could cause issues.
- CPU
- Virtualization Contention (overcommitting the hypervisor)
- Any cgroup limitation (likely to be related to the above)
- kill -9 of any postgres process (except postmaster!). This is a decent simulation of a segfault.

One thing that you should not do is run kill -9 on a postmaster process. This is because doing so does not mimic any real life scenario. If you are concerned your infrastructure is insecure and an attacker could run kill -9, no amount of HA process is going to fix that. The attacker will simply kill the process again, or cause chaos in another way.
