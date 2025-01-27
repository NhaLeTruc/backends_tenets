# Making use of replication slots

In PostgreSQL 9.4, a major new feature called "replication slots" has been
introduced. The idea is to give users and tools alike a chance to connect to the
transaction log stream in a standard way and consume data.
Basically, two types of replication slots exist:

- Physical replication slots
- Logical replication slots

## Physical replication slots

Physical replication slots are an important new feature of PostgreSQL 9.4. The idea is that a client (worker/remote) can create a replication slot to make sure that the server (main/local) only discards what has really made it to the client.

If the slave/client cannot consume the transaction log fast enough or if there is simply not enough bandwidth, it can happen that the master throws away stuff that is actually still needed in the future. By giving clients an actual name, the master knows when to recycle the XLOG and make sure that the client won't lose sight of it.

Of course, a replication slot can also be dangerous. What if a slave disconnects and does not come back within a reasonable amount of time to consume all of the XLOG kept in stock? In this case, the consequences for the master are not good, because by the time the master fills up, it might be too late.

> To use replication slots in your setup, you have to tell PostgreSQL via postgresql.conf to allow this feature, otherwise the system will error out immediately.

```conf
max_replication_slots = 10 # max number of replication slots # (change requires restart)
```

Before the database is restarted, make sure that wal_level is set to at least
archive to make this work. Once the database has been restarted, the replication
slot can be created:

```SQL
SELECT * FROM pg_create_physical_replication_slot('my_slot');
```

In this scenario, a replication slot called my_slot has been created. So far, no
XLOG position has been assigned to it yet.

In the next step, it is possible to check which replication slots already exist. In
this example, there is only one, of course. To retrieve the entire list, just select
from pg_replication_slots:

```bash
\d pg_replication_slots
```

> The important thing here is that a physical replication slot has been created. It
can be used to stream XLOG directly, so it is really about physical copies of the
data.

If a replication slot is not needed any more, it can be deleted. To do so, the
following instruction can be helpful:

```SQL
SELECT pg_drop_replication_slot('my_slot');
```

> It is important to clean out replication slots as soon as they are not needed any
more. Otherwise, it might happen that the server producing the XLOG fills up
and faces troubles because of filled-up filesystems. It is highly important to keep
an eye on those replication slots and make sure that cleanup of spare slots really
happens.

## Logical replication slots

In contrast to physical replication slots, logical replication slots return decoded
messages through a mechanism called **logical decoding**. The main idea is to
have a means of extracting changes going on in the database directly by
connecting to the XLOG.

The output plugin reads data through a standard API and transforms things into the desired output format. No changes to the core of PostgreSQL are required because modules can be loaded on demand.

The following example shows how a simple plugin, called test_decoding, can
be utilized to dissect the XLOG:

```SQL
SELECT * FROM pg_create_logical_replication_slot('slot_name', 'test_decoding');
```

As soon as the replication slot is created, the transaction log position is returned.
This is important to know because from this position onward, the decoded
XLOG will be sent to the client.

The replication slot is, of course, visible in the system view:

```bash
test=# \x
Expanded display is on.
test=# SELECT * FROM pg_replication_slots;
-[ RECORD 1 ]+--------------
slot_name | slot_name
plugin | test_decoding
slot_type | logical
datoid | 21589
database | test
active | f
xmin |
catalog_xmin | 937
restart_lsn | D/438DCE78
```

## Configuring replication identities

Starting with PostgreSQL 9.4, there is also some new functionality related to
replication slots in ALTER TABLE. The idea is to give users control over the
amount of transaction log created during the UPDATE command. In general, the
goal of the transaction log is to allow the server to repair itself. If replication
slots are used, it is necessary to know a bit more about the change.

> Postgres tables require a replica identity to be configured in order to capture the changes made to the table. Replica identity specifies the type of information written to the write-ahead log with respect to what the previous values were.

```SQL
ALTER TABLE t_test REPLICA IDENTITY FULL;
```

The UPDATE command will now create a more verbose representation of the changed row.

At this point, PostgreSQL provides four different levels of REPLICA IDENTITY:

- DEFAULT: This records the old values of the columns of the primary key, if any.
- USING INDEX: This index records the old values of the columns covered by the named index, which must be unique, not partial, and not deferrable, and must include only columns marked as NOT NULL.
- FULL: This records the old values of all the columns in the row.
- NOTHING: This records no information about the old row.
