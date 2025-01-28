# Notes

## Chapter 1

Basic concepts in data replication; CRUD; Cluster CAP; ACID; Partition; Sharding; and Scaling strategies.

## Chapter 2

All about Postgres XLOG aka Trasaction Log aka Write ahead Log (WAL). What, When, Why and How of WAL. Its crucial role to Postgres's Availibility; and Consistency in ACID.

## Chapter 3

Point in time Recovery discusses PITR's basic concepts of WAL management, crucially **checkpointing**. It goes into Postgres's **pg_basebackup** and **pg_start_backup** method as foundation for basic small data backup tasks. Finally the chapter give instructions on how to restore a database from these backup methods.

Note that the above two methods are physical and asynchronous replication. With pg_basebackup has an option to capture XLOG created during the backup elaspes. This log streaming process would create a self-sufficient backup.

> So far most Postgres backup methods are just shell scripts for copying and moving files (data and logs) from one server/directory to another. Postgres's good performance and features despite this appearant simplicity might be why it is so popular.
---
> having an untested backup is the same as having no backup at all

## Chapter 4

Setting Up Asynchronous Replication 
