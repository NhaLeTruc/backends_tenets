# CRUD specific Workloads

## Write-Heavy Workloads

> If you have a write-heavy workload, we strongly recommend a database that stores data
in immutable files (e.g., Cassandra, ScyllaDB, and others that use LSM trees).2 These
databases optimize write speed because: 1) writes are sequential, which is faster in
terms of disk I/O and 2) writes are performed immediately, without first worrying about
reading or updating existing values (like databases that rely on B-trees do). As a result,
you can typically write a lot of data with very low latencies.
---
> But read performance doesn’t necessarily need to suffer. You can often minimize this
tradeoff with a write-optimized database that implements its own caching subsystem
(as opposed to those that rely on the operating system’s built-in cache), enabling fast
reads to coexist alongside extremely fast writes. Bypassing the underlying OS with a
performance-focused built-in cache should speed up your reads nicely, to the point
where the latencies are nearly comparable to read-optimized databases.
---
> With a write-heavy workload, it’s also essential to have extremely fast storage, such
as NVMe drives, if your peak throughput is high. Having a database that can theoretically
store values rapidly ultimately won’t help if the disk itself can’t keep pace.
---
> beware that write-heavy workloads can result in
surprisingly high costs as you scale. Writes cost around five times more than reads
under some vendors’ pricing models. Before you invest too much effort in performance
optimizations, and so on, it’s a good idea to price your solution at scale and make sure
it’s a good long-term fit.

## Read-Heavy Workloads

B-tree databases (such as DynamoDB) are optimized for reads (that’s the payoff for the extra time required to update values on the write path). However, the advantage that read-optimized databases offer for reads is generally not as significant as the advantage that write-optimized databases offer for writes, especially if the write-optimized database uses internal caching to make up the difference.

Careful data modeling will pay off in spades for optimizing your reads. So will careful
selection of read consistency (are eventually consistent reads acceptable as opposed to
strongly consistent ones?), locating your database near your application, and performing
a thorough analysis of your query access patterns. Thinking about your access patterns is
especially crucial for success with a read-heavy workload.

- What is the nature of the data that the application will be querying
mostly frequently? Does it tolerate potentially stale reads or does it
require immediate consistency?

- How frequently is it accessed (e.g., is it frequently-accessed “hot”
data that is likely cached, or is it rarely-accessed “cold” data)?

- Does it require aggregations, JOINs, and/or querying flexibility on
fields that are not part of your primary key component?

- Speaking of primary keys, what is the level of cardinality?

Assume that your use case requires dynamic querying capabilities (such
as type-ahead use cases, report-building solutions, etc.) where you frequently need to query
data from columns other than your primary/hash key component. In this case, you might
find yourself performing full table scans all too frequently, or relying on too many indexes.
Both of these, in one way or another, may eventually undermine your read performance.

On the infrastructure side, selecting servers with high memory footprints is key for
enabling low read latencies if you will mostly serve data that is frequently accessed. On
the other hand, if your reads mostly hit cold data, you will want a nice balance between
your storage speeds and memory. In fact, many distributed databases typically reserve
some memory space specifically for caching indexes; this way, reads that inevitably
require going to disk won’t waste I/O by scanning through irrelevant data.

> Some databases will allow you to read data without polluting your
cache (e.g., filling it up with data that is unlikely to be requested again).
Using such a mechanism is especially important when you’re running
large scans while simultaneously serving real-time data. If the large
scans were allowed to override the previously cached entries that the
real-time workload required, those reads would have to go through
disk and get repopulated into the cache again. This would effective
---
> For use cases requiring a distinction between hot/cold data storage
(for cost savings, different latency requirements, or both), then
solutions using tiered storage (a method of prioritizing data storage
based on a range of requirements, such as performance and costs)
are likely a good fit.
---
> Some databases will permit you to prioritize some workloads over
others. If that’s not sufficient, you can go one step further and
completely isolate such workloads logically.
---

## Mixed Workloads

> Not sure if your reads are from cold or hot data? Take a look at the ratio
of cache misses in your monitoring dashboards.

If your ratio of cache misses is higher than hits, this means that reads need to
frequently hit the disks in order to look up your data. This may happen because your
database is underprovisioned in memory space, or simply because the application
access patterns often read infrequently accessed data. It is important to understand the
performance implications here. If you’re frequently reading from cold data, there’s a risk
that I/O will become the bottleneck—for writes as well as reads. In that case, if you need
to improve performance, adding more nodes or switching your storage medium to a
faster solution could be helpful.

> As noted earlier, write-optimized databases can improve read latency via internal
caching, so it’s not uncommon for a team with, say, 60 percent reads and 40 percent
writes to opt for a write-optimized database. Another option is to boost the latency
of reads with a write-optimized database: If your database supports it, dedicate extra
“shares” of resources to the reads so that your read workload is prioritized when there is
resource contention.

## Delete-Heavy Workloads

> What about delete-heavy workloads, such as using your database as a durable queue
(saving data from a producer until the consumer accesses it, deleting it, then starting the
cycle over and over again)? Here, you generally want to avoid databases that store data
in immutable files and use tombstones to mark rows and columns that are slated for
deletion. The most notable examples are Cassandra and other Cassandra-compatible
databases.

Tombstones consume cache space and disk resources, and the database needs to search through all these tombstones to reach the live data. For many workloads, this is not a problem. But for delete-heavy workloads, generating an excessive amount of tombstones will, over time, significantly degrade your read latencies. There are ways and mechanisms to mitigate the impact of tombstones.  However, in general, if you have a delete-heavy workload, it may be best to use a different database.

• The main workload consists of queries triggered by a user clicking or
navigating on some areas of the web page. Here, users expect high
responsiveness, which usually translates to requirements for low
latency. You need low timeouts with load shedding as your overload
response, and you would like to have a lot of dedicated resources
available whenever this workload needs them.

• A second workload drives analytics being run periodically to collect
some statistics or to aggregate some information that should be
presented to users. This involves a series of computations. It’s a lot
less sensitive to latency than the main workload; it’s more throughput
oriented. You can have fairly large timeouts to accommodate for
always full queues. You would like to throttle requests under load so
the computation is stable and controllable. And finally, you would
like the workload to have very few dedicated resources and use
mostly unused resources to achieve better cluster utilization.


