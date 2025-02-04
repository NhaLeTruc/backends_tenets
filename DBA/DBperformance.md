# Database performance at scale

## What We Mean by Database Performance at Scale

Database performance at scale means different things to different teams. For some, it
might mean achieving extremely low read latencies; for others, it might mean ingesting
very large datasets as quickly as possible. For example:

- Messaging: Keeping latency consistently low for thousands to
millions of operations per second, because users expect to interact in
real-time on popular social media platforms, especially when there’s
a big event or major news

- Fraud detection: Analyzing a massive dataset as rapidly as possible
(millions of operations per second), because faster processing helps
stop fraud in its tracks.

- AdTech: Providing lightning fast (sub-millisecond P9999 latency)
responses with zero tolerance for latency spikes, because an ad bid
that’s sent even a millisecond past the cutoff is worthless to the ad
company and the clients who rely on it.

We specifically tagged on the “at scale” modifier to emphasize that we’re catering to
teams who are outside of the honeymoon zone, where everything is just blissfully fast
no matter what you do with respect to setup, usage, and management. Different teams
will reach that inflection point for different reasons, and at different thresholds. But one
thing is always the same: It’s better to anticipate and prepare than to wait and scramble
to react.

## Lessons Learned

1. Although some databases advertise themselves as universal, most
of them perform best for certain kinds of workloads. The analysis
before selecting a database for your own needs must include
estimating the characteristics of your own workload:

    a. Is it likely to be a predictable, steady flow of requests (e.g., updates being fetched from other systems periodically)?
    b. Is the variance high and hard to predict, with the system being idle for potentially long periods of time, with occasional bumps of activity?

2. If your workload is susceptible to spikes, be prepared for it and
try to architect your cluster to be able to survive a temporarily
elevated load. Database-as-a-service solutions tend to allow
configuring the provisioned throughput in a dynamic way, which
means that the threshold of accepted requests can occasionally
be raised temporarily to a previously configured level. Or,
respectively, they allow it to be temporarily decreased to make the
solution slightly more cost-efficient.

3. Always expect spikes. Even if your workload is absolutely steady, a
temporary hardware failure or a surprise DDoS attack can cause a
sharp increase in incoming requests.

4. Observability is key in distributed systems. It allows the developers
to retrospectively investigate a failure. It also provides real-time
alerts when a likely failure scenario is detected, allowing people to
react quickly and either prevent a larger failure from happening, or
at least minimize the negative impact on the cluster.

5. Unexpected spikes are inevitable, and scaling out the cluster
might not be swift enough to mitigate the negative effects of
excessive concurrency. Expecting the database to handle it
properly is not without merit, but not every database is capable
of that. If possible, limit the concurrency in your system as early
as possible. For instance, if the database is never touched directly
by customers (which is a very good idea for multiple reasons)
but instead is accessed through a set of microservices under your
control, make sure that the microservices are also aware of the
concurrency limits and adhere to them.
