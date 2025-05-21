# Rigorous database benchmarking

There could be at least few reasons why it’s so easy to fail trying to understand performance of a database system, and they usually have something to do with the inherent duality:

- It’s necessary to combine expertise from both the domain specic area and general analytics expertise.
- One have to take into account both known and unknown factors.
- Establishing a comprehensive mental model of a database is surprisingly hard and could be counter-intuitive at times.

## Known vs unknown

More than once a proper benchmark was failed due to an obscure eect not being taken care of. This even goes beyond obvious known/unknown classication, and we usually have
following:

- Known knowns, e.g. we know max_wal_size parameter plays a signicant role in PostgreSQL performance.
- Known unknowns, e.g. we know max_wal_size is important, but have no idea what is the optimal value.
- Unknown unknowns, e.g. we have no idea that we run the database on a buggy Linux Kernel version, where buered IO in a cgroup is slow due to wrong memory pressure calculation and constant page reclaiming.
- Intrinsic noise, e.g. we run the database on a disk with particularly volatile latencies.

## Database model

Everyone has a dierent way of thinking about databases, and what we’re going to talk about in this section is only one particular example I nd useful. The idea is to view a database as a complex system that could be described as a function on the phase space.

What are the dimensions of our database model? Well, that’s where things get a bit scary – there are a lot of dimensions, which could be roughly grouped into following categories:

- **Database parameters**: all conguration knobs obviously affect the system performance one way or another.
- **Hardware resources**: another obvious part, the database is going to perform dierently if you give it more memory or CPU cores.
- **Workload parameters**: what exactly load we apply is important as well, the results are going to be dierent if we do one transaction per second vs if we hit it with thousands of tps.
- **Performance results**: surprisingly, the output of our system is also a part of the model. Note, that in this article we’re talking about performance, but the very same approach could be made for anything else, e.g. one can build a model describing the database availability to verify HA properties.

Besides the fact that we got a lot of dimensions here, **some of them are not even deterministic** (mostly out of the latest category) and could be defined only as random variables with certain probability distribution, which would lead us later on the dark path of statistics.

At the end we’re of course trying to simplify things and usually, at the risk of loosing high level
interaction between parameters, **we work with much smaller models**.

## Reference

1. [statistics-and-benchmarking](https://erthalion.info/2023/12/29/statistics-and-benchmarking/)