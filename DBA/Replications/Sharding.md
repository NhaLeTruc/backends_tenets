# Using sharding and data distribution

Clearly, at some point, you cannot buy servers that are big enough to handle an
infinite load anymore. It is simply impossible to run a Facebook-or Google-like
application on a single server. At some point, you have to come up with a
scalability strategy that serves your needs. This is when sharding comes into
play.

The idea of sharding is simple: What if you could split data in a way that it can
reside on different nodes?

## Designing a sharded system

When designing a system, we can easily come up with an arbitrary number of
servers; all we have to do is to invent a nice and clever partitioning function to
distribute the data inside our server farm. If we want to split the data between 10
servers (not a problem), how about using user ID % 10 as a partitioning
function? If you are interested in sharding, consider checking out
shard_manager, which is available on PGXN.

> In many cases, a hash function will provide you with nicely and evenly
distributed data. This can especially be useful when working with character
fields (such as names, e-mail addresses, and so on).

## Querying different fields

In the previous section, you saw how we can easily query a person using their
key. Let's take this a little further and see what happens if the following query is
used:

```SQL
SELECT * FROM t_test WHERE name = 'Max';
```

Remember that we have distributed data using the ID. In our query, however, we
are searching for the name. The application will have no idea which partition to
use because there is no rule telling us what is where.

As a logical consequence, the application has to ask every partition for the name
parameter. This might be acceptable if looking for the name was a real corner
case; however, we cannot rely on this fact. Requiring to ask many servers instead
of one is clearly a serious deoptimization, and therefore, not acceptable.

We have two ways to approach the problem: coming up with a cleverer
partitioning function, or storing the data redundantly.

Coming up with a cleverer partitioning function would surely be the best option,
but it is rarely possible if you want to query different fields.

This leaves us with the second option, which is storing data redundantly. Storing
a set of data twice, or even more often, is not too uncommon, and it's actually a
good way to approach the problem.

We could have two clusters in this scenario. When a query comes in,
the system has to decide which data can be found on which node. For cases
where the name is queried, we have (for the sake of simplicity) simply split the
data into half alphabetically. In the first cluster, however, our data is still split by
user ID.

## Pros and cons of sharding

One important thing to understand is that sharding is not a simple one-way
street. If someone decides to use sharding, it is essential to be aware of the
upsides as well as the downsides of the technology. As always, there is no Holy
Grail that magically solves all the problems of mankind out of the box without
them having to think about it.

PROs:

- It has the ability to scale a system beyond one server
- It is a straightforward approach
- It is widely supported by various frameworks
- It can be combined with various other replication approaches
- It works nicely with PostgreSQL (for example, using PL/Proxy)

CONs:

- Adding servers on the fly can be far from simple (depending on the type of partitioning function)
- Your flexibility might be seriously reduced
- Not all types of queries will be as efficient as they would be on a single server
- There is an increase in overall complexity of the setup (such as failover, resyncing, maintenance and so on)
- Backups need more planning
- You might face redundancy and additional storage requirements
- Application developers need to be aware of sharding to make sure that efficient queries are written

## Choosing between sharding and redundancy

> Make sure that only large tables are sharded. In the case of small tables, full replicas of the tables might just make much more sense. Again, every case has to be thought over thoroughly.

## Increasing and decreasing the size of a cluster

How can you really tell for certain how many nodes will be
needed at the time a setup is designed? People might have a rough idea of the
hardware requirements, but actually knowing how much load to expect is more
art than science.

> System should be relatively easy to resize.

A commonly made mistake is that people tend to increase the size of their setup
in unnecessarily small steps. Somebody might want to move from five to maybe
six or seven machines. This can be tricky. Let's assume for a second that we have
split data using user id % 5 as the partitioning function. What if we wanted to
move to user id % 6? This is not so easy; the problem is that we have to
rebalance the data inside our cluster to reflect the new rules.

Practically, it is a lot easier to simply double the number of partitions. Doubling
your partitions does not require rebalancing of data because you can simply
follow the strategy outlined here:

1. Create a replica of each partition
2. Delete half of the data on each partition

If your partitioning function was user id % 5 before, it should be user id % 10
afterwards. The advantage of doubling is that data cannot move between
partitions. When it comes to doubling, users might argue that the size of your
cluster might increase too rapidly. This is true, but if you are running out of capacity, adding 10 percent storage to your resources won't fix the problem of
scalability anyway.

Instead of just doubling your cluster (which is fine for most cases), you can also
give more thought to writing a more sophisticated partitioning function that
leaves the old data in place but handles the more recent data more intelligently.
Having time-dependent partitioning functions might cause issues of its own, but
it might be worth investigating this path.

> Some NoSQL systems use range partitioning to spread out data. Range
partitioning means that each server has a fixed slice of data for a given time
frame. This can be beneficial if you want to perform time series analysis or
something similar. However, it can be counterproductive if you want to make
sure that data is split evenly.
> If you expect your cluster to grow, we recommend starting with more partitions
than those initially necessary, and packing more than just one partition on a
single server. Later on, it will be easy to move single partitions to additional
hardware joining the cluster setup. Some cloud services are able to do that, but
those aspects are not covered in this book.
> To shrink your cluster again, you can simply apply the opposite strategy and
move more than just one partition to a single server. This leaves the door for a
future increase of servers wide open, and can be done fairly easily.

**Consistent hashing** is another approach to distributing data. This technique is
widely used in NoSQL systems and allows us to extend clusters in a more
flexible way.

If a new server is added, new values for the server will be added to the array. The system has to rebalance some data, but of course, not all of the data. It is a major advantage over a simple hashing mechanism, such as a simple key % server_number function. Reducing the amount of data to be resharded is highly important.

The main advantage of consistent hashing is that it scales a lot better than simple approaches.

## Combining sharding and replication

Once data has been broken down into useful chunks, which can be handled by one server or a partition, we have to think about how to make the entire setup more reliable and fail-safe.

> Always avoid single points of failure when designing a highly scalable system.
> "One is none and two is one."

Each partition is a separate PostgreSQL database instance, and each of those
instances can have its own replica (or replicas). Essentially, it is the same
concept as you will find in a RAID 1+0 setup on the hardware side.
