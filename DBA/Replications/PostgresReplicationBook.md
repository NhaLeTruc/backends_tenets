# Notes

## Chapter 1: Introduction

Basic concepts in data replication; CRUD; Cluster CAP; ACID; Partition; Sharding; and Scaling strategies.

## Chapter 2: Transaction Log

All about Postgres XLOG aka Trasaction Log aka Write ahead Log (WAL). What, When, Why and How of WAL. Its crucial role to Postgres's Availibility; and Consistency in ACID.

## Chapter 3: Point in time Recovery Backup

Point in time Recovery discusses PITR's basic concepts of WAL management, crucially **checkpointing**. It goes into Postgres's **pg_basebackup** and **pg_start_backup** method as foundation for basic small data backup tasks. With pg_basebackup has an option to capture XLOG created during the backup elaspes. This log streaming process would create a self-sufficient backup. Finally the chapter give instructions on how to restore a database from these backup methods.

Note that the above two methods are for backup database not replicate it. This means PITR try replaying the transaction log as soon as something nasty has happened. While replication replaying the transaction log as soon as possible in the replica server.

> So far most Postgres backup methods are just shell scripts for copying and moving files (data and logs) from one server/directory to another. Postgres's good performance and features despite this appearant simplicity might be why it is so popular.
---
> having an untested backup is the same as having no backup at all

## Chapter 4: Setting Up Asynchronous Replication

Instructions and considerations for planning and executing a Postgres asynchronous replication.

> Life is not always just black or white. Sometimes, there are also some shades of
gray. For some cases, streaming replication might be just perfect. In some other
cases, file-based replication and PITR are all you need. But there are also many
cases in which you need a bit of both. One example would be like this: when you
interrupt replication for a long period of time, you might want to resync the slave
using the archive again instead of performing a full base backup. It might also be
useful to keep an archive around for some later investigation or replay operation.

The chapter offers several well known errors which could occur during replication. It also goes into introducing conflict management between mains and workers. From classic conflicts like race condition on data row; to timeline difference; server crashes; etc.

> Keep in mind that normal Hot-Standby is definitely a wise option. The purpose
of a lagging slave is to protect yourself against unexpected DROP TABLE
statements, accidental deletions of data, and so on. It allows users to jump back
in time when really needed without having to touch too much data. A lagging
slave can be seen as a form of backup that constantly updates itself.

## Chapter 5: Setting Up Synchronous Replication

So far, we have dealt with file-based replication (or log shipping, as it is often called) and a simple streaming-based asynchronous setup. In both cases, data is submitted and received by the slave (or slaves) after the transaction has been committed on the master. During the time between the master's commit and the point when the slave actually has fully received the data, it can still be lost.

Synchronous replication can be the cornerstone of your replication setup, providing a system that ensures zero data loss.

## Chapter 6: Monitoring

Monitoring is a key component of every critical system, and therefore a deep and thorough understanding of it is essential in order to keep your database system up and running.

Monitoring the transaction log archive.

- pg_stat_replication
- pg_xlog_location_diff

Monitoring tool:

- [bucardo](http://bucardo.org/wiki/Check_postgres)
- [nagios](https://www.nagios.org/about/)

### Deciding on a monitoring strategy

If you happen to run a large analysis database that will be used only by a handful of people, checking for the number of open database connections might be of no use. If you happen to run a highperformance OLTP system serving thousands of users, checking for open connections might be a very good idea.

It is important to mention that certain checks that are not related to PostgreSQL are always useful. The following list contains a—nowhere complete—list of suggestions:

- CPU usage
- Disk space consumption and free space
- Memory consumption
- Disk wait
- Operating system swap usage
- General availability of the desired services

## Chapter 7. Understanding Linux High Availability

### Measuring availability

The idea behind availability is that the service provider tries to guarantee a certain level of it, and clients can then expect that or more.

> The quality of availability is measured in fraction of percentages, for example,
99.99 percent or 99.999 percent, which are referred to as "four nines" and "five
nines" respectively. These values are considered pretty good availability values,
but there is a small trick in computing this value. If the provider has a planned
downtime that is announced in advance; for example, the annual or bi-annual
maintenance for water pipes in a town doesn't make the availability number
worse, then availability is only measured outside the planned maintenance
window.

### Durability and availability

When designing data storage systems, it is important to distinguish between the
properties of availability and durability. Availability is a measure of the
probability that the system is able to accept reads and writes at any given point
in time. Durability is a measure of the probability that once a write has been
accepted (in PostgreSQL, this means a successful transaction commit), that
information will not be lost. All real systems must pick a compromise between
availability, durability, performance, and cost.

> It is extremely important to avoid situations where more than one database instance could be accepting writes from your application. Your data will end up in two places, and you will not be able to merge the two databases back together without a large data recovery effort. In effect, this causes you to lose data, so you fail on your durability guarantees.
---
> This situation is called a split-brain, and all cluster management systems must have ways to avoid it. The tools used to avoid split-brain are called **quorum and fencing**.

**Pacemaker High Availability stack** is the central tool for Linux-HA.

### Setting up a simple HA cluster

Instruction in [Guide](file:///D:/MyFile/_PDF/DBA/PostgreSQL%20Replication%20(%20PDFDrive%20).pdf) page 225 - 248.

## Chapter 8: Working with PgBouncer

The basic idea of PgBouncer is to save connection-related costs.
When a user creates a new database connection, it usually means burning a
couple of hundred kilobytes of memory. This consists of approximately 20 KB
of shared memory and the amount of memory used by the process serving the
connection itself. While the memory consumption itself might not be a problem,
the actual creation process of the connection can be comparatively time
consuming.

PgBouncer solves this problem by placing itself between the actual database
server and the heavily used application. To the application, PgBouncer looks just
like a PostgreSQL server. Internally, PgBouncer will simply keep an array of
open connections and pool them. Whenever a connection is requested by the
application, PgBouncer will take the request and assign a pooled connection. In
short, it is some sort of proxy.

## Chapter 9: Working with pgpool

The idea behind pgpool is to bundle connection pooling with some additional functionality to  improve replication, load balancing.

The pgpool tool is one that has been widely adopted for replication and failover.
It offers a vast variety of features including load balancing, connection pooling,
and replication. The pgpool tool will replicate data on the statement level and
integrate itself with PostgreSQL onboard tools such as streaming replication.

## Chapter 10: Configuring Slony

Slony is one of the most widespread replication solutions in the field of
PostgreSQL. It is not only one of the oldest replication implementations, it is
also one that has the most extensive support by external tools, such as
pgAdmin3. For many years, Slony was the only viable solution available for the
replication of data in PostgreSQL. Fortunately, the situation has changed and a
handful of new technologies have emerged.

## Chapter 11: Using SkyTools

SkyTools is a software package originally developed by Skype, and it serves a
variety of purposes. It is not a single program but a collection of tools and
services that you can use to enhance your replication setup. It offers solutions for
generic queues, a simplified replication setup, data transport jobs, as well as a
programming framework suitable for database applications (especially transport
jobs).

## Chapter 12: Working with Postgres-XC

In this chapter, we have to focus our attention on a write-scalable, multimaster,
synchronous, symmetric, and transparent replication solution for PostgreSQL,
called PostgreSQL eXtensible Cluster (Postgres-XC). The goal of this project
is to provide the end user with a transparent replication solution, which allows
higher levels of loads by horizontally scaling to multiple servers.

In an array of servers running Postgres-XC, you can connect to any node inside
the cluster. The system will make sure that you get exactly the same view of the
data on every node. This is really important, as it solves a handful of problems
on the client side. There is no need to add logic to applications that write to just
one node. You can balance your load easily. Data is always instantly visible on
all nodes after a transaction commits. Postgres-XC is wonderfully transparent,
and application changes are not required for scaling out.

## Chapter 13: Scaling with PL/Proxy

Adding a slave here and there is really a nice scalability strategy, which is
basically enough for most modern applications. Many applications will run
perfectly well with just one server; you might want to add a replica to add some
security to the setup, but in many cases, this is pretty much what people need.

If your application grows larger, you can, in many cases, just add slaves and
scale out reading. This too is not a big deal and can be done quite easily. If you
want to add even more slaves, you might have to cascade your replication
infrastructure, but for 98 percent of all applications, this is going to be enough.

In those rare, leftover 2 percent of cases, PL/Proxy can come to the rescue. The
idea of PL/Proxy is to be able to scale out writes. Remember that transactionlog-based replication can scale out only reads; there is no way to scale out
writes.

## Chapter 14: Scaling with BDR

People had to use Slony to replicate data. The core problem with solutions such as Slony is that there is a need for a changelog trigger, which actually writes data twice. Trigger-based solutions are hard to administer, are not able to handle DDLs, and are in general a bit tricky to operate.

BDR has been invented to put an end to trigger-based solutions and turn PostgreSQL into a more robust, more scalable, and easier way to administer solutions. Trigger-based replication is really a thing of the past, and should not be seen in a modern infrastructure anymore. You can safely bet on BDR—it is a long-term, safe solution.

## Chapter 15: Working with Walbouncer

It's all about filtering the stream of the transaction log to selectively replicate database objects from one server to a set of (not necessarily identical) slaves.

The purpose of the PostgreSQL transaction log is to help a failed database instance recover itself in the event of a crash. It can also be used to replicate an entire database instance, as already discussed in our chapters about synchronous as well as asynchronous replication.

The trouble is that it is necessary to replicate entire database instances. In many
real-world scenarios, this can be a problem. Let's assume there is a central server
containing information about students studying in many universities. Each
university should have a copy of its data. As of PostgreSQL 9.4, this was not
possible using a single database instance because streaming replication is only
capable of fully replicating an instance. Running many instances is clearly a lot
more work and, maybe, not the desired methodology.

The idea behind walbouncer is to connect to the PostgreSQL transaction log and
filter it. In this scenario, a slave will receive only a subset of the data, thus
filtering out all of the data that may be critical from legal or a security point of
view. In the case of our university example, each university would only have a
replica of its own database, and therefore, there is no way to see data from other
organizations. Hiding data is a huge step forward when it comes to securing
systems. There might also be a use case for walbouncer for the purpose of
sharding.
