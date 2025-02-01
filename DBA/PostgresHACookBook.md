# PostgreSQL 9 High Availability Cookbook

## Chapter 1: Hardware Planning

### Having enough IOPS

IOPS stands for Input/Output Operations Per Second. Essentially, this describes how
many operations a device can perform per second before it should be considered saturated.
If a device is saturated, further requests must wait until the device has spare bandwidth. A
server overwhelmed with requests can amount to seconds, minutes, or even hours of
delayed results.

### Estimate Hardware need

This chapter disucess rule of thumb and authors' expriences. It advises to plan for double hardware requirement every three to four year as the company grow. The emphasis is on the powers of two in computing. Especially with database doubling help with partition and sharding as well.

It is worth frequent returning for the author's IOP and hardware requirement formulas. Best compare with external sources though. These formulas are very informal.

> Our calculations always assume worst-case scenarios. This is both expensive and in many
cases, overzealous. We ignore RAM caching of disk blocks, we don't account for application
frontend caches, and the PostgreSQL shared buffers are also not included.
---
> The number of necessary IOPS, and hence disk requirements, are subject to risk evaluation
and cost benefit analysis. Deciding between 100 percent coverage and an acceptable fraction
is a careful balancing act. Feel free to reduce these numbers; just consider the cost of an
outage as part of the total. If a delay is considered standard operating procedures, fractions
up to 50 percent are relatively low risk. If possible, try to run tests for an ultimate decision
before purchase.

### Sizing storage

Query for collecting Postgres space usages:

```SQL
SELECT pg_size_pretty(sum(pg_database_size(oid))::BIGINT)
FROM pg_database;
```

This chapter intructs DBA to collect space usage every week to estimate usage growth. It admits that these are just estimates or educated guesses. Usage could spike and drop depend on each business's unique operations.

> Since there are a lot of variables that contribute to the volume of storage we want, we need
information about each of them. Gather as many data points as possible regarding things
such as: largest expected tables and indexes, row counts per day, indexes per table, desired
excess, and anything else imaginable. We'll use all of it.

### Investing in a RAID

RAID stands for Redundant Array of Independent (or Inexpensive) Disks, and often
requires a separate controller card for management. The primary purpose of a RAID is to
combine several physical devices into a single logical unit for the sake of redundancy and
performance.

Only a few RAID levels matter in a database context. Perform these steps to decide which
one is right for this server:

- If this is an OLTP (Online Transaction Processing) database primarily for handling very high speed queries, use RAID level 1+0
- If this is a non-critical development or staging system, use RAID level 5
- If this is a non-critical OLAP (Online Analytic Processing) reporting system, use RAID level 5
- If this is a critical OLAP reporting system, use RAID level 6
- If this is a long-term storage OLAP warehouse, use RAID level 6

> In this RAID 1+0, we have three sets, each consisting of two disks. Each of the two disks
mirror each other, and the data is striped across all three sets. We could lose a disk from
each set and still have all of our data. We only have a problem if we lose two disks from the
same set, since they mirror each other. Overall, this is the most robust RAID level available,
and the most commonly used for OLTP systems.
---
> The solid line shows that the data is spread across all six drives. The dotted line is the parity information. If a drive fails and the block can't be read directly from the necessary location, a RAID 5 will use the remaining parity information from all drives to reconstruct the missing data. The only real difference between a RAID 5 and a RAID 6 is that a RAID 6 contains a second parity line, so up to two drives can fail before the array begins operating in a degraded manner.

