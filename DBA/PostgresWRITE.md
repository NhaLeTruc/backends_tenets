# Writing one row of data

## A simple INSERT statement

In general, tables containing incomplete rows in unknown places can be
considered to be corrupted tables. We have to ensure that PostgreSQL will survive interruptions at any given point
in time without losing or corrupting data. Protecting your data is not something
nice to have but an absolute must-have. This is what is commonly referred to as
the "D" in Atomicity, Consistency, Isolation, and Durability (ACID).

To fix the problem that we have just discussed, PostgreSQL uses the so-called
WAL or simply XLOG. Using WAL means that a log is written ahead of data.

> If PostgreSQL is configured properly (fsync = on, and so on), crashing is
perfectly safe at any point in time (unless hardware is damaged of course; a
malfunctioning RAM and so on are, of course, always a risk).

## Read consistency

For the sake of simplicity, we can see a database instance as an entity consisting
of three major components:

- PostgreSQL data files
- The transaction log
- Shared buffer

### The purpose of the shared buffer

The shared buffer is the I/O cache of PostgreSQL. It helps cache 8K blocks,
which are read from the operating system, and also helps hold back writes to the
disk to optimize efficiency.

What happens if we perform a simple read? Maybe we are looking for
something simple, such as a phone number or a username, given a certain key.
The following list shows in a highly simplified way what PostgreSQL will do
under the assumption that the instance has been freshly restarted:

1. PostgreSQL will look up the desired block in the cache (as stated before,
this is the shared buffer). It will not find the block in the cache of a freshly
started instance.
2. PostgreSQL will ask the operating system for the block.
3. Once the block has been loaded from the OS, PostgreSQL will put it into
the first queue of the cache.
4. The query will be served successfully.

Let's assume that the same block will be used again, this time by a second query.
In this case, things will work as follows:

1. PostgreSQL will look up the desired block and come across a cache hit.
2. Then PostgreSQL will figure out that a cached block has been reused, and
move it from a lower level of cache (Q1) to a higher level of cache (Q2).
Blocks that are in the second queue will stay in the cache longer, because
they have proven to be more important than those that are only at the Q1
level.

### Mixed reads and writes

Remember that in this section, it is all about understanding writes to make sure
that our ultimate goal—full and deep understanding of replication—can be
achieved. Therefore, we have to see how reads and writes go together:

1. A write will come in.
2. PostgreSQL will write to the transaction log to make sure that consistency
can be reached.
3. Then PostgreSQL will grab a block inside the PostgreSQL shared buffer
and make the change in the memory.
4. A read will come in.
5. PostgreSQL will consult the cache and look for the desired data.
6. A cache hit will be landed and the query will be served.

> It is important to understand that data is usually not sent to a data file directly
after or during a write operation. It makes perfect sense to write data a lot later to
increase efficiency. The reason this is important is that it has subtle implications
on replication. A data file itself is worthless because it is neither necessarily
complete nor correct. To run a PostgreSQL instance, you will always need data
files along with the transaction log. Otherwise, there is no way to survive a
crash.

From a consistency point of view, the shared buffer is here to complete the view
a user has of the data. If something is not in the table, logically, it has to be in
memory.

In the event of a crash, the memory will be lost, and so the XLOG will be
consulted and replayed to turn data files into a consistent data store again. Under
all circumstances, data files are only half of the story.

## Consistency and data loss

It is hard, or even impossible, to keep data files in good shape without the ability to log changes beforehand.

So far, we have mostly talked about corruption. It is definitely not good to lose data files because of corrupted entries in them, but corruption is not the only issue you have to be concerned about. Two other important topics are:

- Performance
- Data loss

## All the way to the disk

When PostgreSQL wants to read or write a block, it usually has to go through a
couple of layers. When a block is written, it will be sent to the operating system.
The operating system will cache the data and perform some operation on it. At
some point, the operating system will decide to pass the data to some lower
level. This might be the disk controller. The disk controller will cache, reorder,
message the write again, and finally pass it to the disk. Inside the disk, there
might be one more caching level before the data ends up on the real physical
storage device.

In our example, we have used four layers. In many enterprise systems, there can
be even more layers. Just imagine a virtual machine with storage mounted over
the network, such as SAN, NAS, NFS, ATA-over_Ethernet, iSCSI, and so on.
Many abstraction layers will pass data around, and each of them will try to do its
share of optimization.

## From memory to memory

What happens when PostgreSQL passes an 8 K block to the operating system?
The only correct answer to this question might be, "something." When a normal
write to a file is performed, there is absolutely no guarantee that the data is
actually sent to the disk. In reality, writing to a file is nothing more than a copy
operation from the PostgreSQL memory to some system memory. Both memory
areas are in RAM, so in the event of a crash, data can be lost.

If a crash happens shortly after COMMIT, no data will be in danger because
nothing has happened. Even if a crash happens shortly after the INSERT statement
but before COMMIT, nothing can happen. The user has not issued a COMMIT
command yet, so the transaction is known to be running and thus unfinished. If a
crash occurs, the application will notice that things were unsuccessful and
(hopefully) react accordingly. Also keep in mind that every transaction that is not
committed will eventually end up as ROLLBACK.

However, the situation is quite different if the user has issued a COMMIT statement
and it has returned successfully. Whatever happens, the user will expect the
committed data to be available.

> Users expect that successful writes will be available after an unexpected reboot.
This persistence is also required by the ACID criteria. In computer science,
ACID is a set of properties that guarantee that database transactions are
processed reliably.

## From the memory to the disk

To make sure that the kernel will pass data from the memory to the disk,
PostgreSQL has to take some precautions. Upon a COMMIT command, a system
call will be issued. It forces data to the transaction log.

> PostgreSQL does not have to force data to the data files at this point because we
can always repair broken data files from the XLOG. If data is stored in the
XLOG safely, the transaction can be considered safe.

The system call necessary to force data to the disk is called fsync(). The
following listing has been copied from the BSD manual page. In our opinion, it
is one of the best manual pages ever written dealing with the topic:

```text
FSYNC(2) BSD System Calls Manual FSYNC(2)

NAME
fsync -- synchronize a file's in-core state with that on disk

SYNOPSIS
    #include <unistd.h>
int
fsync(intfildes);

DESCRIPTION

Fsync() causes all modified data and attributes of
fildes to be moved to a permanent storage device.

This normally results in all in-core modified
copies of buffers for the associated file to be
written to a disk.

Note that while fsync() will flush all data from
the host to the drive (i.e. the "permanent storage
device"), the drive itself may not physically
write the data to the platters for quite some time
and it may be written in an out-of-order sequence.

Specifically, if the drive loses power or the OS
crashes, the application may find that only some
or none of their data was written. The disk drive
may also reorder the data so that later writes
may be present, while earlier writes are not.

This is not a theoretical edge case. This scenario is easily
reproduced with real world work-loads and drive power failures.
```

It essentially says that the kernel tries to make its image of the file in the
memory consistent with the image of the file on the disk. It does so by forcing
all changes to the storage device.

> Without a disk flush on COMMIT, you just cannot be sure that your data is safe,
and this means that you can actually lose data in the event of some serious
trouble

**Flushing changes to the disk is especially expensive
because real hardware is involved**. The overhead we have is not some five
percent but a lot more. With the introduction of SSDs, the overhead has gone
down dramatically but it is still substantial.

### A word about batteries

Most production servers make use of a RAID controller to manage disks. The
important point here is that disk flushes and performance are usually strongly
related to RAID controllers. If the RAID controller has no battery, which is
usually the case, then it takes insanely long to flush. The RAID controller has to
wait for the slowest disk to return. However, if a battery is available, the RAID
controller can assume that a power loss will not prevent an acknowledged disk
write from completing once power is restored. So, the controller can cache a
write and simply pretend to flush. Therefore, a simple battery can easily increase
flush performance tenfold.

> Keep in mind that what we have outlined in this section is general knowledge,
and every piece of hardware is different. We highly recommend that you check
out and understand your hardware and RAID configuration to see how flushes
are handled.

### Beyond the fsync function

The fsync function is not the only system call that flushes data to the disk.
Depending on the operating system you are using, different flush calls are
available. In PostgreSQL, you can decide on your preferred flush call by
changing wal_sync_method. Again, this change can be made by tweaking
postgresql.conf.

The methods available are open_datasync, fdatasync, fsync,
fsync_writethrough, and open_sync.

> If you want to change these values, we highly recommend checking out the
manual pages of the operating system you are using to make sure that you have
made the right choice.

