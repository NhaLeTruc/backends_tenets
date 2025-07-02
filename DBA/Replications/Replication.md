# Replication

## Understanding the CAP theorem

- **Consistency:** This term indicates whether all the nodes in a cluster see the
same data at the same time or not. A read-only node has to see all
previously completed reads at any time.
- **Availability:** Reads and writes have to succeed all the time. In other words
a node has to be available for users at any point of time.
- **Partition tolerance:** This means that the system will continue to work even
if arbitrary messages are lost on the way. A network partition event occurs
when a system is no longer accessible (think of a network connection
failure). A different way of considering partition tolerance is to think of it as
message passing. If an individual system can no longer send or receive
messages from other systems, it means that it has been effectively
partitioned out of the network. The guaranteed properties are maintained
even when network failures prevent some machines from communicating
with others.

## Understanding the limits of physics

To explain the concept of latency, let's cover
a very simple example. Let's assume you are a European and you are
sending a letter to China. You will easily accept the fact that the size of your
letter is not the limiting factor here. It makes absolutely no difference
whether your letter is two or 20 pages long; the time it takes to reach the
destination is basically the same. Also, it makes no difference whether you
send one, two, or 10 letters at the same time. Given a reasonable numbers
of letter, the size of the aircraft required (that is, the bandwidth) to ship the
stuff to China is usually not the problem. However, the so-called round trip
might very well be an issue. If you rely on the response to your letter from
China to continue your work, you will soon find yourself waiting for a long
time.

The most important point you have to keep in mind here is that bandwidth is not
always the magical fix to a performance problem in a replicated environment. In
many setups, latency is at least as important as bandwidth.

## Different types of replication

### I. Synchronous versus asynchronous replication

- **Asynchronous replication** the data can be replicated after the
transaction has been committed on the master. In other words, the slave is never
ahead of the master; and in the case of writing, it is usually a little behind the
master. This delay is called lag.

- **Synchronous replication** enforces higher rules of consistency. The system has to ensure that
the data written by the transaction will be at least on two servers at the time the
transaction commits. This implies that the slave does not lag behind the master
and that the data seen by the end users will be identical on both the servers.

> Tip: Some systems will also use a quorum server to decide. So, it is not always about just two or more servers. If a quorum is used, more than half of the servers must agree on an action inside the cluster.

#### Considering performance issues

Sending unnecessary messages over the network can be expensive and timeconsuming. If a transaction is replicated in a synchronous way, PostgreSQL has to make sure that the data reaches the second node, and this will lead to latency
issues.

Synchronous replication can be more expensive than asynchronous replication in many ways, and therefore, people should think twice about whether this overhead is really needed and justified. In the case of synchronous replication, confirmations from a remote server are needed. This, of course, causes some additional overhead. A lot has been done in PostgreSQL to reduce this overhead as much as possible. However, it is still there.

> Tip: Use synchronous replication only when it is really needed.

### II. Single-master versus multimaster replication

**Single-master** means that writes can go to exactly one server, which distributes the data to the slaves inside the setup. Slaves may receive only reads, and no writes.

**Multimaster** replication allows writes to all the servers inside a cluster.

The ability to write to any node inside the cluster sounds like an advantage, but it
is not necessarily one. The reason for this is that multimaster replication adds a
lot of complexity to the system. In the case of only one master, it is totally clear
which data is correct and in which direction data will flow, and there are rarely
conflicts during replication. Multimaster replication is quite different, as writes
can go to many nodes at the same time, and the cluster has to be perfectly aware
of conflicts and handle them gracefully. An alterative would be to use locks to
solve the problem, but this approach will also have its own challenges.

> Tip: Keep in mind that the need to resolve conflicts will cause network traffic, and this can instantly turn into scalability issues caused by latency.

### III. Logical versus physical replication

- **Physical replication** means that the system will move data as is to the remote box. So, if something is inserted, the remote box will get data in binary format, not via SQL.
- **Logical replication** means that a change, which is equivalent to data coming in, is replicated.

In the case of **logical replication**, the change will be sent to some sort of queue in
logical form, so the system does not send plain SQL, but maybe something such
as this:

```SQL
test=# INSERT INTO t_test VALUES ('2013-02-08');
INSERT 0 1
```

*Note* that the function call has been replaced with the real value. It would be a
total disaster if the slave were to calculate now() once again, because the date on
the remote box might be a totally different one.

MySQL uses a so-called bin-log statement to replicate, which is
actually not too binary but more like some form of logical replication. Of course,
there are also counterparts in the PostgreSQL world, such as pgpool, Londiste,
and Bucardo.

**Physical replication** will work in a totally different way; instead of sending some
SQL (or something else) over, which is logically equivalent to the changes made,
the system will send binary changes made by PostgreSQL internally.

Here are some of the binary changes our two transactions might have triggered
(but by far, this is not a complete list):

1. Added an 8 K block to pg_class and put a new record there (to indicate that the table is present).
2. Added rows to pg_attribute to store the column names.
3. Performed various changes inside the indexes on those tables.
4. Recorded the commit status, and so on.

The goal of physical replication is to create a copy of your system that is
(largely) **identical on the physical level**. This means that the same data will be in
the same place inside your tables on all boxes. In the case of logical replication,
the content should be identical, but it makes no difference whether it is in the
same place or not.

#### When to use physical replication

Physical replication is very convenient to use and especially easy to set up. It is widely used when the goal is to have identical replicas of your system (to have a backup or to simply scale up). In many setups, physical replication is the standard method that exposes the end user to the lowest complexity possible. It is ideal for scaling out the data.

#### When to use logical replication

Logical replication is usually a little harder to set up, but it offers greater flexibility. It is also especially important when it comes to upgrading an existing database. Physical replication is totally unsuitable for version jumps because you cannot simply rely on the fact that every version of PostgreSQL has the same ondisk layout. The storage format might change over time, and therefore, a binary copy is clearly not feasible for a jump from one version to the next.

## Understanding replication and data loss

Let's assume that we are replicating data asynchronously in the following manner:

1. A transaction is sent to the master.
2. It commits on the master.
3. The master dies before the commit is sent to the slave.
4. The slave will never get this transaction.

In the case of asynchronous replication, there is a window (lag) during which
data can essentially be lost. The size of this window might vary, depending on
the type of setup. Its size can be very short (maybe as short as a couple of
milliseconds) or long (minutes, hours, or days). The important fact is that data
can be lost. A small lag will only make data loss less likely, but any lag larger
than zero lag is susceptible to data loss. If data can be lost, we are about to
sacrifice the consistency part of CAP (if two servers don't have the same data,
they are out of sync).

If you want to make sure that data can never be lost, you have to switch to
synchronous replication. As you have already seen in this chapter, a synchronous
transaction is synchronous because it will be valid only if it commits to at least
two servers.
