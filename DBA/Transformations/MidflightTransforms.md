# Computing throughput vs IOPS Tradeoff

Batch data transformation tasks carry a tradeoff between network IO and transformation throughput. In order to increace throughput through employing distributed computing engines (Spark; Flink; and other Cloud equivalents), data is often transferred from dedicated database storage (eg. Postgres) to engine integrated storage (eg. RDD). This save on network IO and might reduce disk spills, but how effective is it depend on several factors.

Every transformation incurrs several costs:

- network IO.
- storage.
- computing power per hour.

## 1. How complex is the transformation?

This drive up computing power per hour per transaction.

## 2. How large is the data?

This drive up all three factors, but with distributed computing it is networkIO and storage which is most affected.

## The cost benefit equaltion

> Total cost = (Partition Size + Transformation complexity) x (Storage + Network IO + Computing power per hour)

If transformations are performed on data in database:

- Storage cost will be minimized, as no second copy of data is made.
- Network IO cost will incurred during transformations. This could become unaffordable or unacceptable for production sources/sinks, if transformation frequency was not fixed (100% definitely known).
- Computing power per hour could raised if disk spill occur due to Partition Size + Transformation complexity requirement is larger than memory.

If transformations are performed data in integrated storage:

- Storage will be at least doubled, as data is replicated across distributed storage.
- Network IO would raised during data transfers and lowered while transformations are occurring, as data and engine is collocated.
- Computing power per hour could raised if disk spill occur due to Partition Size + Transformation complexity requirement is larger than memory.

## Caveats

- It is assumed that data is well partitioned. If not then it's best not to poke production too often.
