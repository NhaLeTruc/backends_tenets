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
