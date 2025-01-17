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

