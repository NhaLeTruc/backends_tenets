# Distributed systems integration

## Synchronous communication

Synchronous communication is a type of communication in which the systems involved need to be in contact with each other at the same time in order to exchange messages or information. In synchronous communication, messages are typically transmitted and processed immediately, without any delay.

It is often used in real-time applications, where the parties need to exchange messages or information in a timely manner in order to maintain the integrity or consistency of the system. By using synchronous communication, systems can exchange messages and information in a coordinated and immediate manner, which can improve the reliability.

**Synchronous calls can be a good choice for:**

- Communication between your client (like web UI / mobile app) and your backend server (HTTP).
- Communication with internal shared/common services, like email service or a service to process some data (RPC or HTTP calls).
- Communication with external third-party services.

Synchronous calls between distributed systems is not always a good idea. It creates coupling, system becomes fragile and slow. For example, in microservices world synchronous communication between microservices can transform them to a distributed monolith. Try to avoid that as much as possible.

## Asynchronous communication

Asynchronous communication is a type of communication in which the systems involved do not need to be in contact with each other at the same time in order to exchange messages or information. In asynchronous communication, messages are typically processed at a later time.

It is often used in distributed systems where the parties involved are located in different places, or are operating at different times. By using asynchronous communication, systems can exchange messages without needing to be in contact with each other at the same time, which can improve the flexibility and scalability of the system.

There are several ways to implement asynchronous communication, including using message queues, event streams, or other mechanisms. The choice of approach depends on the specific requirements and constraints of the system, and on the type and amount of data that needs to be exchanged.

Examples: message brokers developed on top of AMQP protocol (like RabbitMQ) or event streams like Kafka.

When changes occur, you need some way to reconcile changes across the different systems. One solution is eventual consistency and event-driven communication based on asynchronous messaging.

Ideally, you should try to minimize the communication between the distributed systems. But it is not always possible. In microservices world, prefer asynchronous communication since it is better suited for communication between microservices than synchronous. The goal of each microservice is to be autonomous. If one of the microservices is down that shouldn't affect other microservices. Asynchronous communication via messaging can remove dependencies on the availability of other services.

## Data serialization

Data serialization is the process of converting structured data into a format that can be easily stored or transmitted. The process of serialization involves translating the data into a specific format, such as a string of characters or bytes, and then deserialized back to the original format when it is needed.

Data serialization is often used in distributed systems where data needs to be transferred between different nodes or components in the system. By serializing the data, it can be transmitted over a network or stored in a file, and then reconstructed at the other end of the transmission. This allows the data to be transferred efficiently and reliably.

To address the issue of multi-language microservices communication, a possible solution is to describe our data models in some language-agnostic way, so we can generate the same models for each language. This requires the use of an IDL, or interface definition language.

One of the most common formats for that lately is JSON. It is simple and human-readable. For most systems out there this format is a great choice.

But when your system is growing, there are better choices.

Protocol buffers, Apache Avro, Apache Thrift provide tools for cross platform and language neutral data formats to serialize data. Those formats are useful for services that communicate over a network or for storing data.

**Some pros for using a schema and serializing data include:**

- Messages are serialized to binary format which is compact (binary messages occupy about twice less storage than JSON)
- Provides interoperability with other languages (language agnostic).
- Provides forward and backward-compatible schema for your messages/events

## API Gateway

An API gateway is a software component that acts as a bridge between an application and the underlying services or resources that the application uses. The API gateway is responsible for routing requests from the application to the appropriate service or resource, and for translating the request and response data as needed to enable communication between the application and the service.

An API gateway is an API management tool that sits between a client and a collection of backend services. An API gateway acts as a reverse proxy to accept all application programming interface (API) calls, aggregate the various services required to fulfill them, and return the appropriate result.

In many cases, the API gateway is implemented as a layer between the application and the underlying services, and is responsible for routing requests from the application to the appropriate service, and for translating the request and response data as needed. This allows the API gateway to abstract the underlying services from the application, and to provide a consistent and standardized interface for the application to access the services.

You can implement your own API Gateway if needed, or you could use existing solutions like Kong or nginx.

**Api Gateway can also handle:**

- Gateway Routing pattern can help with routing requests to multiple services using a single endpoint
- Load balancing to evenly distribute load across your nodes
- Rate limiting to protect from DDoS and Brute Force attacks
- Authentication and Authorization to allow only trusted clients to access your APIs
- Circuit Breaker to prevent an application from repeatedly trying to execute an operation that's likely to fail
- Gateway Aggregation pattern can help to Compose data from multiple microservices for your client
- Analytics and monitoring for your API calls
- and much more

## Scalability

Scalability is the capability to handle the increased workload by repeatedly applying a cost-effective strategy for extending a system’s capacity.

- Vertical scaling means scaling by adding more power (CPU, RAM, Storage, etc.) to your existing servers.

- Horizontal scaling means adding more servers into your pool of resources.

### Performance and availability

Components of distributed systems communicate through a network. Networks are unreliable and slow compared to communication in a single process node. Ensuring good performance and availability in these conditions is an important aspect of a distributed system.

1. Performance is the amount of useful work accomplished by a computer system at reasonable time.
2. Availability is often quantified by uptime (or downtime) as a percentage of time the service is available. For example, around 8 hours of downtime per year may be considered as a 99.9% available system.
3. Redundancy means duplication of critical components like data, nodes and running processes, etc. Redundancy can improve flexibility, reliability, availability, scalability and performance of your system, failure resistance and recovery. Below we discuss techniques and patterns for creating redundancy.
4. Autoscaling is a method used in cloud computing that dynamically adjusts the amount of computational resources in a server based on the load. Autoscaling allows an application to scale up or down automatically, based on pre-defined policies and rules, in order to maintain optimal performance and cost efficiency.

### Load balancing

is a technique for distributing workloads or requests across multiple computing resources, such as servers, processors, or network links, in order to improve the performance and availability of a system. In a load-balanced system, requests are distributed evenly across the available resources, in order to balance the load and prevent any individual resource from becoming overwhelmed.

There are several approaches to load balancing, including hardware-based load balancers, software-based load balancers, and cloud-based load balancers. The choice of approach depends on the specific requirements and constraints of the system, and on the type and amount of workload that needs to be distributed.

**Load balancers can operate at one of the two levels described below:**

1. Layer 4 (Transport) load balancers operate at the transport level and make their routing decisions based on address information extracted from the first few packets in the TCP stream and do not inspect packet content.
2. Level 7 (Application) load balancing deals with the actual content of each message enabling the load balancer to make smarter load balancing decisions, can apply optimizations and changes to the content (such as compression and encryption) and make decisions based on the message content. Layer 7 gives a lot of interesting benefits, but is less performant.

Load balancing can be software and hardware based.

Software Load balancing can be done by an API gateway or a reverse proxy.
There are multiple algorithms for implementing load balancing: round-robin, least connection, hashing based, etc.
