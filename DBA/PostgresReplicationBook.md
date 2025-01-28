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


