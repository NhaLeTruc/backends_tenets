# I Heart Logs

## Chapter 1: Introduction

This chapter gives definitions of different types of logs. It goes into explaining the roles log plays in applications and systems especially distributed ones.

## Chapter 2: Data Integration

> Data integration means making available all the data that an organization has to all the services and systems that need it.

The phrase “data integration” isn’t all that common, but I don’t know a better one. The more recognizable term ETL (extract, transform, and load) usually covers only a limited part of data integration — populating a relational data warehouse. However, much of what I am describing can be thought of as ETL that is generalized to also encompass real-time systems and processing flows.

## Chapter 3: Logs and Real-Time Stream Processing

So far, I have only described what amounts to a fancy method of copying data from place to place. However, schlepping bytes between storage systems is not the end of the story. It turns out that “log” is another word for “stream” and logs are at the heart of stream processing.

It turns out that the log solves some of the most critical technical problems in stream processing, which I’ll describe, but the biggest problem that it solves is just making data available in real-time multisubscriber data feeds.

## Chapter 4: Building Data Systems with Logs

So there is already one possible simplification in the handling of data in the move to distributed systems: coalescing many little instances of each system into a few big clusters. Many systems aren’t good enough to allow this yet because they don’t have security, can’t guarantee performance isolation, or just don’t scale well enough. However, each of these problems is solvable. Instead of running many little single server instances of a system, you can instead run one big multitenant system shared by all the applications of an entire organization. This allows for huge efficiencies in management and utilization.

Logs give us a principled way to model changing data as it cascades through a distributed system. This works just as well to model data flow in a large enterprise as it does for the internals of data flow in a distributed database. Having this kind of basic abstraction in place gives us a way of gluing together disparate data systems, processing real-time changes, as well as a being an interesting system and application architecture in its own right. In some sense, all of our systems are distributed systems now, so what was once a somewhat esoteric implementation detail of a distributed database is now a concept that is quite relevant to the modern software engineer.
