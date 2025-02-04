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

