# Understanding the XLOG records

Changes made to the XLOG are record-based. What does that mean? Let's
assume you are adding a row to a table:

```SQL
test=# INSERT INTO t_test VALUES (1, 'hans');
INSERT 0 1
```

In this example, we are inserting values into a table containing two columns. For
the sake of this example, we want to assume that both columns are indexed.

Remember what you learned before: the purpose of the XLOG is to keep those
data files safe. So this operation will trigger a series of XLOG entries. First, the
data file (or files) related to the table will be written. Then the entries related to
the indexes will be created. Finally, a COMMIT record will be sent to the log.

Not all the XLOG records are equal. Various types of XLOG records exist, for
example heap, B-tree, clog, storage, Generalized Inverted Index (GIN), and
standby records, to name a few.

XLOG records are chained backwards so, each entry points to the previous entry
in the file. In this way, we can be perfectly sure that we have found the end of a
record as soon as we have found the pointer to the previous entry.

As you can see, a single change can trigger a larger number of XLOG entries.
This is true for all kinds of statements; a large DELETE statement, for instance,
can easily cause a million changes. The reason is that PostgreSQL cannot simply
put the SQL itself into the log; it really has to log physical changes made to the
table.

This is because not all SQL script return the same result everytime it is run.

## Making the XLOG reliable

The XLOG itself is one of the most critical and sensitive parts in the entire
database instance. Therefore, we have to take special care to make sure that
everything possible is done to protect it. In the event of a crash, a database
instance is usually doomed if there is no XLOG around.

Internally, PostgreSQL takes some special precautions to handle the XLOG:

- Using CRC32 checksums
- Disabling signals
- Space allocation

First of all, each XLOG record contains a CRC32 checksum. This allows us to
check the integrity of the log at startup.

In addition to checksums, PostgreSQL will disable signals temporarily while
writing to the XLOG. This gives some extra level of security and reduces the
odds of a stupid corner-case problem somewhere.

Finally, PostgreSQL uses a fixed-size XLOG. The size of the XLOG is
determined by checkpoint segments as well as by
checkpoint_completion_target.

The size of the PostgreSQL transaction log is calculated as follows:

> (2 + checkpoint_completion_target) * checkpoint_segments + 1

An alternative way to calculate the size is this:

> checkpoint_segments + wal_keep_segments + 1 files

An important thing to note is that if something is of fixed size, it can rarely run
out of space.

> In the case of transaction-log-based replication, we can run out of space on the
XLOG directory if the transaction log cannot be archived.

## LSNs and shared buffer interaction

If you want to repair a table, you have to make sure that you do so in the correct
order; it would be a disaster if a row was deleted before it actually came into
existence. Therefore, the XLOG provides you with the order of all the changes.
Internally, this order is reflected through the Logical Sequence Number (LSN).
The LSN is essential to the XLOG. Each XLOG entry will be assigned an LSN
straight away.

In one of the previous sections, we discussed consistency level. With
synchronous_commit set to off, a client will get an approval even if the XLOG
record has not been flushed to disk yet. Still, since a change must be reflected in
cache and since the XLOG must be written before the data table, the system has
to make sure that not all the blocks in the shared buffer can be written to
instantly. The LSN will guarantee that we can write blocks from the shared
buffer to the data file only if the corresponding change has already made it to the
XLOG. Writing to the XLOG is fundamental, and a violation of this rule will
certainly lead to problems after a crash.

## Debugging the XLOG and putting it all together

Now that we have seen how an XLOG basically works, we can put it all together
and actually look into the XLOG. As of **PostgreSQL 9.2**, it works as follows: we
have to compile PostgreSQL from source. Before we do that, we should modify
the file located at *src/include/pg_config_manual.h*. At approximately line
250, we can uncomment **WAL_DEBUG** and compile as usual. This will then allow
us to set a client variable called wal_debug:

```SQL
test=# SET client_min_messages TO log;
SET
test=# SET wal_debug TO on;
SET
```

In addition to this, we have to set client_min_messages to make sure that the
LOG messages will reach our client.

