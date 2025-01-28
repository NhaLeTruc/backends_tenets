# Understanding Point-in-time Recovery

When your system crashes, or when somebody just happens to drop a table accidentally, it is highly important not to replay the entire transaction log but just a fraction of it. Point-in-time Recovery (PITR) will be the tool to do this kind of partial replay of the transaction log.

## The purpose of PITR

PostgreSQL offers a tool called pg_dump to back up a database. Basically, pg_dump will connect to the database, read all of the data in "repeatable read" transaction isolation level and return the data as text. As we are using "repeatable read," the dump is always consistent.

So, if your pg_dump routine starts at midnight and finishes at 6 A.M., you will have created a backup that contains all of the data as of midnight, but no further data. This kind of snapshot creation is highly convenient and perfectly feasible for small to medium amounts of data.

But what if your data is so valuable and, maybe, so large in size that you want to
back it up incrementally? Taking a snapshot from time to time might be enough
for some applications, but for highly critical data, it is clearly not. In addition to
that, replaying 20 TB of data in textual form is not efficient either. Point-in-time
Recovery has been designed to address this problem.

> Based on a snapshot of the database, the XLOG will be replayed later on. This can happen indefinitely or up to a point chosen by you. In this way, you can reach any point in time.

This method opens the door to many different approaches and features:

- Restoring a database instance up to a given point in time
- Creating a standby database that holds a copy of the original data
- Creating a history of all changes

## Recovery Backups

> PostgreSQL produces 16 MB segments of transaction log

Every time one of those segments is filled up and ready, PostgreSQL will call the so-called **archive_command**.

The aim of **archive_command** is to transport the XLOG file from the database instance to an **archive**.

The beauty of the design is that you can basically use an arbitrary shell script to archive the transaction log. Here are some ideas:

- Use some simple copy to transport data to an NFS share
- Run rsync to move a file
- Use a custom-made script to checksum the XLOG file and move it to an
- FTP server
- Copy the XLOG file to a tape
- Upload data to a cloud-based storage provider

The possible options for managing XLOG are only limited by the imagination.

The **restore_command** is the exact counterpart of archive_command. Its purpose is to fetch data from the archive and provide it to the instance (Restore Backup), which is supposed to replay it.

In brief, **restore_command** and **archive_command** are simply shell scripts doing whatever you wish to do file by file.

> It is important to mention that you, the almighty administrator, are in charge of the archive. You have to decide how much XLOG to keep and when to delete it. The importance of this task cannot be underestimated.
---
> Keep in mind that when archive_command fails for some reason, PostgreSQL
will keep the XLOG file and retry after a couple of seconds. If archiving fails
constantly from a certain point onwards, it might happen that the master fills up.
The sequence of XLOG files must not be interrupted; if a single file is missing,
you cannot continue to replay XLOG. All XLOG files must be present because
PostgreSQL needs an uninterrupted sequence of XLOG files. Even if a single
file is missing, the recovery process will stop there.

## Archiving the transaction log

The first thing you have to do when it comes to Pointin-time Recovery is archive
the XLOG. PostgreSQL offers all the configuration options related to archiving
through postgresql.conf.

Let us see step by step what has to be done in postgresql.conf to start archiving:

1. First of all, you should turn archive_mode on.
2. In the second step, you should configure your archive_command. The archive_command is a simple shell, and it needs just two parameters to operate properly:
    - %p: This is a placeholder representing the XLOG file that should be archived, including its full path (source).
    - %f: This variable holds the name of XLOG without the path pointing to it.

Let's set up archiving now. To do so, we should create a place to put the XLOG.
Ideally, the XLOG is not stored on the same hardware as the database instance
you want to archive. For the sake of this example, we assume that we want to
copy an archive to **/archive**. The following changes have to be made to **postgresql.conf**:

```conf
wal_level = archive
# minimal, archive, hot_standby, or logical
# (change requires restart)
archive_mode = on
# allows archiving to be done
# (change requires restart)
archive_command = 'cp %p archive%f'
# command to use to archive a logfile segment
# placeholders: %p = path of file to archive
#               %f = file name only
```

Once these changes have been made to postgresql.conf, archiving is ready for
action. To activate these change, restarting the database server is necessary.

Before we restart the database instance, we want to focus your attention on
**wal_level**. Currently four different wal_level settings are available:

- replica
- minimal
- logical

**wal_level** determines how much information is written to the WAL. The default value is **replica**, which writes enough data to support WAL archiving and replication, including running read-only queries on a standby server. **minimal** removes all logging except the information required to recover from a crash or immediate shutdown. Finally, **logical** adds information necessary to support logical decoding. Each level includes the information logged at all lower levels.

> This parameter can only be set at server start.

However, **minimal** WAL does not contain sufficient information for **point-in-time recovery**.

> so replica or higher must be used to enable continuous archiving and streaming binary replication.

In fact, the server will not even start in this mode if **max_wal_senders** is non-zero.

> Note that changing wal_level to minimal makes previous base backups unusable for point-in-time recovery and standby servers.

In **logical** level, the same information is logged as with **replica**, plus information needed to extract logical change sets from the WAL.

> Using a level of logical will increase the WAL volume, particularly if many tables are configured for **REPLICA IDENTITY FULL** and many UPDATE and DELETE statements are executed

In releases prior to 9.6, this parameter also allowed the values archive and hot_standby. These are still accepted but mapped to replica.

## Taking base backups

Keep in mind that the XLOG itself is more or less worthless. It is only useful in combination with the initial base backup.

In PostgreSQL, there are two main options to create an initial base backup:

- Using pg_basebackup
- Traditional methods based on copy /rsync

**pg_basebackup** is used to take a base backup of a running PostgreSQL database cluster. The backup is taken without affecting other clients of the database, and can be used both for point-in-time recovery and as the starting point for a log-shipping or streaming-replication standby server.

**pg_basebackup** can take a full or incremental base backup of the database. When used to take a full backup, it makes an exact copy of the database cluster's files. When used to take an incremental backup, some files that would have been part of a full backup may be replaced with incremental versions of the same files, containing only those blocks that have been modified since the reference backup.
