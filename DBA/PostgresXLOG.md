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
