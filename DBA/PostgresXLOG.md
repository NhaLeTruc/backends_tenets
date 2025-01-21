# XLOG and replication

## The format of the XLOG

An XLOG entry identifies the object it is supposed to change using
three variables:

- The OID (object id) of the database.
- The OID of the tablespace.
- The OID of the underlying data file.

This triplet is a unique identifier for any data-carrying object in the database
system. Depending on the type of operation, various types of records are used
(commit records, B-tree changes, heap changes, and so on).

In general, the XLOG is a stream of records lined up one after the other. Each
record is identified by the location in the stream. As already mentioned in this
chapter, a typical XLOG file is 16 MB in size (unless changed at compile time).
Inside those 16 MB segments, data is organized in 8 K blocks. XLOG pages
contain a simple header consisting of:

- The 16-bit "magic" value
- Flag bits
- The timeline ID
- The XLOG position of this page
- The length of data remaining from the last record on the previous page

In addition to this, each segment (16 MB file) has a header consisting of various
fields as well:

- System identifier
- Segment size and block size

The segment and block size are mostly available to check the correctness of the file.
Finally, each record has a special header with following contents:

- The XLOG record structure
- The total length of the record
- The transaction ID that produced the record
- The length of record-specific data, excluding header and backup blocks
- Flags
- The record type (for example, XLOG checkpoint, transaction commit, and B-tree insert)
- The start position of previous record
- The checksum of this record
- Record-specific data
- Full-page images

## The XLOG and replication

The idea of using this set of changes to replicate data is not farfetched. In fact, it
is a logical step in the development of every relational (or maybe even a
nonrelational) database system. For the rest of this book, you will see in many
ways how the PostgreSQL transaction log can be used, fetched, stored,
replicated, and analyzed.

In most replicated systems, the PostgreSQL transaction log is the backbone of
the entire architecture (for synchronous as well as for asynchronous replication).

## Tuning checkpoints and the XLOG

> we have seen that data has to be written to the XLOG before it
can go anywhere. The thing is that if the XLOG was never deleted, clearly, we
would not write to it forever without filling up the disk at some point in time.
To solve this problem, the XLOG has to be deleted at some point.

*This process is called checkpointing.*

The main question arising from this issue is, "When can the XLOG be truncated
up to a certain point?" The answer is, "When PostgreSQL has put everything that
is already in the XLOG into the storage files." If all the changes made to the
XLOG are also made to the data files, the XLOG can be truncated.

> Keep in mind that simply writing the data is worthless. We also have to flush the
data to the data tables.

In a way, the XLOG can be seen as the repairman of the data files if something
undesirable happens. If everything is fully repaired, the repair instructions can be
removed safely; this is exactly what happens during a checkpoint.

## Configuring the checkpoints

Checkpoints are highly important for consistency, but they are also highly
relevant to performance. If checkpoints are configured poorly, you might face
serious performance degradations.

When it comes to configuring checkpoints, the following parameters are
relevant. Note that all of these parameters can be changed in postgresql.conf:

```conf
checkpoint_segments = 3
checkpoint_timeout = 5min
checkpoint_completion_target = 0.5
checkpoint_warning = 30s
```

### Segments and timeouts

The **checkpoint_segments** and **checkpoint_timeout** parameters define the
distance between two checkpoints. A checkpoint happens either when we run out
of segments or timeout happens.

Remember that a segment is usually 16 MB, so three segments means that we
will perform a checkpoint every 48 MB. On modern hardware, 16 MB is far
from enough. In a typical production system, a checkpoint interval of 256 MB
(measured in segments) or even higher is perfectly feasible.

However, when setting **checkpoint_segments**, one thing has to be present at the
back of your mind: in the event of a crash, PostgreSQL has to replay all the
changes since the last checkpoint. If the distance between two checkpoints is
unusually large, you might notice that your failed database instance takes too
long to start up again. This should be avoided for the sake of **availability**.

> There will always be a trade-off between performance and recovery times after a crash. You have to balance your configuration accordingly.

---

> In PostgreSQL, you will figure out that there are a constant number of
transaction log files around. Unlike other database systems, the number of
XLOG files has nothing to do with the maximum size of a transaction; a
transaction can easily be much larger than the distance between two checkpoints.

### To write or not to write?

> At the COMMIT time, we cannot be sure whether the data is already in the data files or not.

So if the data files don't have to be consistent anyway, why not vary the point in
time at which the data is written? This is exactly what we can do with the
checkpoint_completion target. The idea is to have a setting that specifies the
target of checkpoint completion as a fraction of the total time between two
checkpoints.

Let's now discuss three scenarios to illustrate the purpose of the **checkpoint_completion_target** parameter.

#### Scenario 1 – storing stock market data

we want to store the most recent stock quotes of all stocks in the
Dow Jones Industrial Average (DJIA). We don't want to store the history of all
stock prices but only the most recent, current price.

Given the type of data we are dealing with, we can assume that we will have a
workload that is dictated by UPDATE statements.

What will happen now? PostgreSQL has to update the same data over and over
again. Given the fact that the DJIA consists of only 30 different stocks, the
amount of data is very limited and our table will be really small. In addition to
this, the price might be updated every second or even more often.

Internally, the situation is like this: when the first UPDATE command comes along,
PostgreSQL will grab a block, put it into the memory, and modify it. Every
subsequent UPDATE command will most likely change the same block. Logically,
all writes have to go to the transaction log, but what happens with the cached
blocks in the shared buffer?

The general rule is as follows: if there are many UPDATE commands (and as a
result, changes made to the same block), it is wise to keep the blocks in memory
as long as possible. This will greatly increase the odds of avoiding I/O by
writing multiple changes in one go.

> If you want to increase the odds of having many changes in one disk I/O,
consider decreasing checkpoint_complection_target. The blocks will stay in
the memory longer, and therefore many changes might go into the same block
before a write occurs.
---
> In the scenario just outlined, a checkpoint_completion_target variable having
value of 0.05 (or 5 percent) might be reasonable.

#### Scenario 2 – bulk loading

In our second scenario, we will load 1 TB of data into an empty table. If you are
loading so much data at once, what are the odds of hitting a block you have hit
10 minutes ago again? The odds are basically zero. There is no point in buffering
writes in this case, because we would simply miss the disk capacity lost by
idling and waiting for I/O to take place.

During a bulk load, we would want to use all of the I/O capacity we have all the
time. To make sure that PostgreSQL writes data instantly, we have to increase
checkpoint_completion_target to a value close to 1.

#### Scenario 3 – I/O spikes and throughput considerations

In this scenario, we want to assume an application storing the so-called Call
Detail Records (CDRs) for a phone company. You can imagine that a lot of
writing will happen and people will be placing phone calls all day long. Of
course, there will be people placing a phone call that is instantly followed by the
next call, but we will also witness a great number of people placing just one call
a week or so.

Technically, this means that there is a good chance that a block in the shared
memory that has recently been changed will face a second or a third change
soon, but we will also have a great deal of changes made to blocks that will
never be visited again.

How will we handle this? Well, it is a good idea to write data late so that as
many changes as possible will go to pages that have been modified before. But
what will happen during a checkpoint? If changes (in this case, dirty pages) have
been held back for too long, the checkpoint itself will be intense, and many
blocks will have to be written within a fairly short period of time. This can lead
to an I/O spike. During an I/O spike, you will see that your I/O system is busy. It
might show poor response times, and those poor response times can be felt by
your end user.

> We are not able to write all changes during the checkpoint anymore, because this might cause latency issues during a checkpoint. It is also no good to make a change to the data files more or less instantly (which means a high checkpoint_completion_target value), because we would be writing too much, too often.
---
> This is a classic example where you have got to compromise. A checkpoint_completion_target value of 0.5 might be the best idea in this case.

### Rule of Thumb for checkpoint_completion_target

The conclusion that should be drawn from these three examples is that no
configuration fits all purposes. You really have to think about the type of data
you are dealing with in order to come up with a good and feasible configuration.
For many applications, a value of 0.5 has been proven to be just fine.

## Tweaking WAL buffers

The wal_buffers parameter has been designed to tell PostgreSQL how much memory to keep around to remember the XLOG that has not been written to the disk so far. So, if somebody pumps in a large transaction, PostgreSQL will not write any "mini" change to the table to the XLOG before COMMIT

Remember that if a noncommitted transaction is lost during a crash, we won't care about it anyway
because COMMIT is the only thing that really counts in everyday life. It makes
perfect sense to write XLOG in larger chunks before COMMIT happens. This is
exactly what wal_buffers does. Unless changed manually in postgresql.conf,
it is an auto-tuned parameter (represented by -1) that makes PostgreSQL take
three percent of shared_buffers, but no more than 16 MB (one segment) to keep the XLOG
around before writing it to the disk.

> In older versions of PostgreSQL, the wal_buffers parameter was at 64 kB. That
was unreasonably low for modern machines. If you are running an old version,
consider increasing wal_buffers to 16 MB. This is usually a good value for
reasonably sized database instances.


