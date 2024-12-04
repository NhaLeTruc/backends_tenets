# Coupling

One reason why distributed systems are so hard to design is coupling. One of the ways you can scale your system is by reducing it. Below are some topics and techniques that can help prevent coupling.

## Location coupling

When a program assumes that something is available at a known location, we can call that a Location coupling. For example, when one service knows the location of another service (lets say knows its URL).

It is difficult to horizontally scale location coupled systems. Location can change, or there may be multiple locations if there are multiple nodes running. Also systems can assume that accessing those locations may be fast, but usually in distributed systems a remote location can be on a entirely different server in a different country, thus a network trip to may be slow.

Location coupling is a problem when considering horizontal scalability because it directly prevents resources from being added dynamically at different locations.

To break location coupling you can abstract the specifics of accessing another part of the system. Your application should be agnostic to the called system.

This can be implemented differently in different scenarios:

- At the network layer, we can use DNS to mask the specific IP addresses of remote servers
- Load balancers can hide that there are multiple instances of some particular system are running to service high workloads
- Clients can hide the details of sharded database clusters
- When using microservices, you can use message broker (described below).

Abstracting the specifics of accessing another part of the system makes application depend only on that abstraction instead of keeping bunch of locations it needs. This lets application scale better. For example, this lets you dynamically add more services and instances to the network when you need it (during peak hours) without changing anything.

## Broker pattern

Broker pattern is used to structure distributed systems with decoupled components. These components can interact with each other by remote service invocations. A broker component is responsible for the coordination of communication among components.

In application that consists of microservices, your services shouldn't know the location of each other. Instead, you can publish your commands/messages/events to a common place (like a message broker) and let other services pick it up. Now all of your services will know about a common location (message broker), but not about each other. Prefer Asynchronous communication when using message brokers.

## Temporal coupling

Temporal coupling usually happens in synchronously communicated systems (a part of a system expects all other parts on which it depends to serve its needs instantaneously). If one part fails, all its dependent systems will also fail, creating a chain of failures.

The most common approach to breaking temporal coupling is the use of message queues. Instead of invoking other parts of a system synchronously (calling and waiting for the response), the caller instead puts a request on a queue and the other system consumes this request when it is available.

## Message queues

A message queue is a component used for Inter-process communication. In distributed systems typically used for asynchronous service-to-service communication. Messages are stored on the queue until they are processed by a consumer.

Each message should be processed only once by a single consumer (idempotent consumer).

Software examples: RabbitMQ and Kafka.

## Business data and logic coupling

To be autonomous, each component of a system must own its domain data and logic (this is called data ownership).

Try not to share business data between components. Otherwise you may end up with a distributed monolith where every change can impact and break the whole system. This is especially relevant in microservices world.

> Regardless of the method we use to share data across service boundaries we’ll end up with services that are not autonomous. Autonomous services can evolve independently from each other, non-autonomous ones cannot. They are coupled, they won’t be able to evolve without breaking each other, causing evolution to stop or causing friction at development time, deployment time, and run time.

> As soon as we allow cross-service data sharing, for example by allowing services to request data from another service, we end up with the worst of two worlds: a monolith suddenly turns into a distributed monolith with all distributed system problems on top of a monolithic one.

**Exception to this rule:**

- Sharing IDs. For example an "order" microservice may need to know what user made an order. In this case you can save a user ID in both services, but not the entire user object with all its properties.
- Some data, lets say email address, can be needed in multiple services, for example authentication service (to login your user) and a marketing service (to send marketing emails). In those cases you may need to duplicate emails between those services. Duplication is better than calling one service from another, but keep in mind that when updating email you'll need to guarantee tis update in both services. We discuss this further in a section below.

Your components must be independently deployable. In a microservices world, if deploying one microservice you have to change other microservices this means you have a tightly coupled architecture.

## Shared-nothing architecture

Shared-Nothing Architecture is a distributed computing architecture that consists of multiple separated nodes that don’t share resources.

This architecture reduces coupling, scales better, simplifies upgrades preventing downtime, eliminates single points of failure, allowing the overall system to continue operating despite failures in individual nodes, etc.

## Selective data replication

Selective data replication is creating a copy of the data needed from other remote system (external API, microservice, etc.) into the database of our system, essentially creating a cache of that data that is always available.

You can subscribe to the events that indicate data updates from other services, for example, subscribe to ProductPriceUpdatedEvent and update your local cache when the price changes. Alternatively, if events are not available, you can query an external service periodically to update your cache.

This approach reduces coupling, runtime dependency, improve latency and makes system more scalable and reliable. Even if external source of data is inaccessible, you still have this data replicated in your own database. But keep in mind that cached data can be stale.

## Event-driven architecture

Event-driven architecture is a design pattern for software applications that emphasizes the production, detection, and consumption of events as a core mechanism for communication and coordination. In an event-driven architecture, events are used to represent significant changes or actions that occur within the system, and are used to trigger functions or processes that react to those events.

In an event-driven architecture, events are typically represented as messages or notifications that are sent by one component of the system to another. These messages can be sent asynchronously, allowing the components of the system to operate independently and in parallel. When a component receives an event message, it can trigger a response or action, such as updating its internal state, performing an operation, or sending another event message.

An event is a broadcast by a software system about something which has happened within its boundary. For example, when the system successfully create an order, it can publish an ORDER_CREATED event.

Event-driven architecture is a flexible and scalable approach to building software applications, and can enable applications to respond quickly and efficiently to changes or actions within the system. It is often used in distributed systems, microservices architectures, and real-time applications, where it can provide a powerful and efficient mechanism for communication and coordination.

### Event-driven end-to-end

In typical web pages, when you load a page and data on the server changes afterwards, the browser does not know about this change until you reload the page. The state displayed on a page is stale cache that is not updated until you explicitly poll or query for changes.

More recent protocols have moved beyond simple request/response pattern. WebSockets provide communication channels which allow your browser to establish a TCP connection to your server. Your server can push messages to your browser as long as it remains connected. This provides an ability for the server to actively inform end-users about any state changes on the server.

Recent tools for developing client applications, like React, Redux, Flux etc. already manage client-side state by subscribing to a stream of changes that represent responses from a server. It would be very natural to extend this model to also allow server to push state-changing events to a client. This way changes and events could flow end-to-end, from the interaction of one device that triggers an event, to the server and event bus, to processing this event, storing it in a database, and back to the UI client that is observing the state changes on another device.

The idea of subscribing for changes instead of querying opens a bunch of new possibilities for more responsive user interfaces. It is already used in some places, like online games or messaging apps.

For typical data centric or CRUD services there may be not a lot of benefit designing an entire application using this approach, but some parts of your application can definitely benefit from it.

### Designing around dataflow

Some microservices example:

- In regular approach, when purchasing a product, your microservice can query an exchange rate service to get currency exchange rate.
- In a dataflow approach, the code that processes purchases would subscribe to a stream of exchange rate updates ahead of time and record the current rate in a local database whenever it changes. When processing a purchase it only needs to query its local database (Selective data replication).

Same as changing a single number in a spreadsheet column will change the output of a formula that depends on this value.

Subscribing to a stream of changes, rather than querying the current state when needed, brings up closer to a spredsheet-like model of computation: when some piece of data changes, any derived data that depends on it can swiftly be updated. - Martin Kleppman

By combining techniques like Event-driven Architecture and Selective Data Replication we can achieve interesting results.

## Consistency

Distributed systems are made up of parts which interact relatively slowly and unreliably. Asynchronous networks can duplicate data, drop packets, reorder messages, have delays, etc. Data can be spread across multiple data stores so managing and maintaining consistency in this environment is an important aspect of the system.

Weak consistency - After a write, there is no guarantee that reads will see it. Works well in real time use cases such as voice or video chat, and realtime multiplayer games, etc.
Strong consistency - After a write, there is a guarantee that reads will se it. Data is replicated synchronously, usually using some kind of transaction.
Eventual consistency - After a write, readers will eventually see written data (usually within seconds) and data is replicated asynchronously. Eventual consistency works best for distributed systems at a large scale.
Familiarize with Fallacies of distributed computing before implementing any kind of distributed system. Added complexities may not be worth it.

Below we will discuss where and why we need consistency, how to achieve it and some associated problems.