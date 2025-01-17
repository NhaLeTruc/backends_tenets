# The PostgreSQL disk layout

In contrast to other database systems, such as Oracle, PostgreSQL will always
rely on a filesystem to store data. PostgreSQL does not use raw devices. The idea
behind this is that if a filesystem developer has done their job well, there is no
need to reimplement the filesystem functionality over and over again.

## PG_VERSION - the PostgreSQL version number

The PG_VERSION file will tell the system at startup whether the data directory
contains the correct version number. Note that only the major release version is
in this file. It is easily possible to replicate between different minor versions of
the same major version (for example, inside the 9.3 or 9.4 series):

```bash
cat PG_VERSION # 9.2
```

The file is plain text readable.

## base – the actual data directory

The base directory is one of the most important things in our data directory. It
actually contains the real data (that is, tables, indexes, and so on). Inside the
base directory, each database will have its own subdirectory:

We can easily link these directories to the databases in our system. It is worth
noticing that PostgreSQL uses the object ID of the database here. This has many
advantages over using the name, because the object ID (oid) never changes and offers
a good way to abstract all sorts of problems, such as issues with different
character sets on the server.

```SQL
SELECT oid, datname FROM pg_database;
```

We can check the system table to retrieve the so-called relfilenode
variable, which represents the name of the storage file on the disk:

```SQL
SELECT relfilenode, relname FROM pg_class WHERE relname = 't_test';
```

> Note that relfilenode can change if TRUNCATE or similar commands occur on a certain table

### Growing data files

Tables can sometimes be quite large, and therefore it is not wise to put all of the
data related to a table into a single data file. To solve this problem, PostgreSQL
will add more files every time 1 GB of data has been added.

So, if the file called 16385 grows beyond 1 GB, there will be a file called
16385.1; once this has been filled, you will see a file named 16385.2; and so on.

### Performing I/O in chunks

To improve I/O performance, PostgreSQL will usually perform I/O in 8 K
chunks. Thus, you will see that your data files will always grow in steps of 8 K
each. When considering physical replication, you have to make sure that both
sides (master and slave) are compiled with the same block size.

> Unless you have explicitly compiled PostgreSQL on your own using different block sizes, you can always rely on the fact that block sizes will be identical and exactly 8KB.

### Relation forks

Other than the data files discussed in the previous paragraph, PostgreSQL will
create additional files using the same relfilenode number. Till now, those files
have been used to store information about free space inside a table (Free Space
Map), the so-called Visibility.

## global – the global data

The global directory will contain the global system tables. This directory is small, so you should not expect excessive storage consumption

> A single PostgreSQL data file is basically more or less worthless. In order to read data, you need an instance that is more or less complete. It is hardly possible to restore data reliably if you just have a data file.

## pg_clog – the commit log

The commit log is an essential component of a working database instance. It
stores the status of the transactions on this system. A transaction can be in four
states: TRANSACTION_STATUS_IN_PROGRESS, TRANSACTION_STATUS_COMMITTED,
TRANSACTION_STATUS_ABORTED, and TRANSACTION_STATUS_SUB_COMMITTED. If
the commit log status for a transaction is not available, PostgreSQL will have no
idea whether a row should be seen or not. The same applies to the end user.

> If the commit log is broken, we recommend that you snapshot the database
instance (filesystem) and fake the commit log. This can sometimes help retrieve
a reasonable amount of data from the database instance in question. Faking the
commit log won't fix your data—it might just bring you closer to the truth. This
faking can be done by generating a file as required by the clog infrastructure

## pg_dynshmem – shared memory

This "shared memory" is somewhat of a misnomer, because what it is really
doing is creating a bunch of files and mapping them to the PostgreSQL address
space. So it is not system-wide shared memory in a classical sense. The
operating system may feel obliged to synchronize the contents to the disk, even
if nothing is being paged out, which will not serve us well. The user can relocate
the pg_dynshmem directory to a RAM disk, if available, to avoid this problem.

## pg_hba.conf – host-based network configuration

The pg_hba.conf file configures the PostgreSQL's internal firewall and represents one of the two most important configuration files in a PostgreSQL cluster. Understanding the pg_hba.conf file is of vital importance because this file decides whether a slave is allowed to connect to the master or not.

## pg_ident.conf – ident authentication

The pg_ident.conf file can be used in conjunction with the pg_hba.conf file to configure ident authentication.

## pg_logical – logical decoding

The pg_logical directory, information for logical decoding is stored (snapshots and the like).

## pg_multixact – multitransaction status data

The multiple-transaction-log manager handles shared row locks efficiently. There are no replication-related practical implications of this directory

## pg_notify – LISTEN/NOTIFY data

In the pg_notify directory, the system stores information about LISTEN/NOTIFY (the async backend interface)

## pg_replslot – replication slots

Information about replication slots is stored in the pg_replslot directory.

## pg_serial – information about committed serializable transactions

Information about serializable transactions is stored in pg_serial directory. We
need to store information about commits of serializable transactions on the disk
to ensure that long-running transactions will not bloat the memory. A simple
Segmented Least Recently Used (SLRU) structure is used internally to keep
track of these transactions.

## pg_snapshot – exported snapshots

The pg_snapshot file consists of information needed by the PostgreSQL
snapshot manager. In some cases, snapshots have to be exported to the disk to
avoid going to the memory. After a crash, these exported snapshots will be
cleaned out automatically.

## pg_stat – permanent statistics

The pg_stat file contains permanent statistics for the statistics subsystem.

## pg_stat_tmp – temporary statistics data

Temporary statistical data is stored in the pg_stst_tmp file. This information is needed for most pg_stat_* system views.

## pg_subtrans – subtransaction data

In this directory, we store information about subtransactions. The pg_subtrans (and pg_clog) directories are a permanent (on-disk) storage of transactionrelated information. There are a limited number of pages of directories kept in the memory, so in many cases, there is no need to actually read from the disk.

However, if there's a long-running transaction or a backend sitting idle with an open transaction, it may be necessary to be able to read and write this information to the disk. These directories also allow the information to be permanent across server restarts.

## pg_tblspc – symbolic links to tablespaces

The pg_tblspc directory is a highly important directory. In PostgreSQL, a tablespace is simply an alternative storage location that is represented by a directory holding the data.

The important thing here is that if a database instance is fully replicated, we
simply cannot rely on the fact that all the servers in the cluster use the same disk
layout and the same storage hardware. There can easily be scenarios in which a
master needs a lot more I/O power than a slave, which might just be around to
function as backup or standby. To allow users to handle different disk layouts,
PostgreSQL will place symlinks in the pg_tblspc directory. The database will
blindly follow those symlinks to find the tablespaces, regardless of where they
are.

> We recommend using the trickery outlined in this section only when it is really
needed. For most setups, it is absolutely recommended to use the same
filesystem layout on the master as well as on the slave. This can greatly reduce
the complexity of backups and replay. Having just one tablespace reduces the
workload on the administrator.

## pg_twophase – information about prepared statements

PostgreSQL has to store information about twophase commit. While twophase
commit can be an important feature, the directory itself will be of little
importance to the average system administrator.

## pg_xlog – the PostgreSQL transaction log (WAL)

The pg_xlog log contains all the files related to the so-called
XLOG. If you have used PostgreSQL in the past, you might be familiar with the
term Write-Ahead Log (WAL). XLOG and WAL are two names for the same
thing. The same applies to the term transaction log.

The log is a bunch of files that are always exactly 16 MB in size (the
default setting). The filename of an XLOG file is generally 24 bytes long. The
numbering is always hexadecimal. So, the system will count "… 9, A, B, C, D,
E, F, 10" and so on.

One important thing to mention is that the size of the pg_xlog directory will not
vary wildly over time, and it is totally independent of the type of transactions
you are running on your system. The size of the XLOG is determined by the
postgresql.conf parameters.

## postgresql.conf – the central PostgreSQL configuration file

the main PostgreSQL configuration file. All configuration
parameters can be changed in postgresql.conf.

> If you happen to use prebuilt binaries, you might not find postgresql.conf
directly inside your data directory. It is more likely to be located in some
subdirectory of etc (on Linux/Unix) or in your place of choice in Windows. The
precise location is highly dependent on the type of operating system you are
using. The typical location of data directories is varlib/pgsql/data, but
postgresql.conf is often located under
etcpostgresql/9.X/main/postgresql.conf (as in Ubuntu and similar
systems), or under /etc directly.