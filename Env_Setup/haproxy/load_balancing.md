# Load Balancing

The mechanism or component which performs the load balancing operation is called a load balancer. In web environments these components are called a "network load balancer", and more commonly a "load balancer" given that this activity is by far the best known case of load balancing.

Examples of load balancing:

- Process scheduling in multi-processor systems
- Link load balancing (e.g. EtherChannel, Bonding)
- IP address load balancing (e.g. ECMP, DNS round-robin)
- Server load balancing (via load balancers)

A load balancer may act:

- at the link level: this is called link load balancing, and it consists in choosing what network link to send a packet to;
- at the network level: this is called network load balancing, and it consists in choosing what route a series of packets will follow;
- at the server level: this is called server load balancing and it consists in deciding what server will process a connection or request.

## Packet vs Session Load Balancing

### Packets or L4 balancer

The first one acts at the **packet level** and processes packets more or less individually. There is a 1-to-1 relation between input and output packets.

This technology can be **very cheap and extremely fast**. It is usually implemented in hardware (ASICs) allowing to reach line rate, such as switches doing ECMP. **Usually stateless**, it can also be stateful (consider the session a packet belongs to and called **layer4-LB or L4**), may support DSR (direct server return, without passing through the LB again) if the packets were not modified, but provides almost no content awareness.

This technology is very well suited to **network-level load balancing**, though it is sometimes used for very basic server load balancing at high speed.

Packet-based load balancers are generally deployed in cut-through mode, so they are installed on the normal path of the traffic and divert it according to the configuration. The return traffic doesn't necessarily pass through the load balancer.

As in whichever backend server is selected will respond directly to the user’s request. Generally, all of the servers in the web-backend should be serving identical content–otherwise the user might receive inconsistent content.

### Sessions or L7 balancer

The second one acts on **session contents**. It requires that the input streams is reassembled and processed as a whole. The contents may be modified, and the output stream is segmented into new packets. For this reason it is generally performed by proxies and they're often called **layer 7 load balancers or L7**.

This implies that there are two distinct connections on each side, and that there is no relation between input and output packets sizes nor counts. Clients and servers are not required to use the same protocol (for example IPv4 vs IPv6, clear vs SSL). **The operations are always stateful**, and the return traffic must pass through the load balancer.

The extra processing comes with a cost so it's not always possible to achieve line rate, especially with small packets. On the other hand, it offers wide possibilities and is generally achieved by pure software, even if embedded into hardware appliances. This technology is very well suited for **server load balancing**.

Proxy-based load balancers are deployed as a server with their own IP addresses and ports, without architecture changes. Sometimes this requires to perform some adaptations to the applications so that clients are properly directed to the load balancer's IP address and not directly to the server's.

> A very scalable layered approach would consist in having a front router which receives traffic from multiple load balanced links, and uses ECMP to distribute this traffic to a first layer of multiple stateful packet-based load balancers (L4). These L4 load balancers in turn pass the traffic to an even larger number of proxy-based load balancers (L7), which have to parse the contents to decide what server will ultimately receive the traffic.

## Health-checks

The number of components and possible paths for the traffic increases the risk of failure; in very large environments, it is even normal to permanently have a few faulty components being fixed or replaced. Load balancing done without awareness of the whole stack's health significantly degrades availability. For this reason, **any sane load balancer will verify that the components it intends to deliver the traffic to are still alive and reachable**, and it will stop delivering traffic to faulty ones.

Periodically sending probes to ensure the component is still operational is called "health checks". A ping-based check will not detect that a web server has crashed and doesn't listen to a port anymore, while a connection to the port will verify this, and a more advanced request may even validate that the server still works and that the database it relies on is still accessible. **Health checks often involve a few retries to cover for occasional measuring errors**. The period between checks must be small enough to ensure the faulty component is not used for too long after an error occurs.

> Other methods consist in sampling the production traffic sent to a destination to observe if it is processed correctly or not, and to evict the components which return inappropriate responses. However this requires to sacrifice a part of the production traffic and this is not always acceptable. A combination of these two mechanisms provides the best of both worlds, with both of them being used to detect a fault, and only health checks to detect the end of the fault.
---
> A last method involves centralized reporting : a central monitoring agent periodically updates all load balancers about all components' state. This gives a global view of the infrastructure to all components, though sometimes with less accuracy or responsiveness. It's best suited for environments with many load balancers and many servers.

## Session stickiness or persistence

Layer 7 load balancers also face another challenge known as stickiness or persistence. The principle is that they generally have to **direct multiple subsequent requests or connections from a same origin (such as an end user) to the same target**. The best known example is the **shopping cart** on an online store. If each click leads to a new connection, the user must always be sent to the server which holds his shopping cart.

Content-awareness makes it easier to spot some elements in the request to identify the server to deliver it to, but that's not always enough. For example if the source address is used as a key to pick a server, it can be decided that a hash-based algorithm will be used and that a given IP address will always be sent to the same server based on a divide of the address by the number of available servers.

But if one server fails, the result changes and all users are suddenly sent to a different server and lose their shopping cart. The solution against this issue consists in **memorizing the chosen target so that each time the same visitor is seen**, he's directed to the same server regardless of the number of available servers.

The information may be stored in the **load balancer's memory**, in which case it may have to be replicated to other load balancers if it's not alone, or it may be stored in the **client's memory** using various methods provided that the client is able to present this information back with every request (cookie insertion, redirection to a sub-domain, etc).

This mechanism provides the extra benefit of not having to rely on unstable or unevenly distributed information (such as the source IP address). This is in fact the strongest reason to adopt a layer 7 load balancer instead of a layer 4 one.

> In order to extract information such as a cookie, a host header field, a URL or whatever, a load balancer may need to decrypt SSL/TLS traffic and even possibly to re-encrypt it when passing it to the server. This expensive task explains why in some high-traffic infrastructures, sometimes there may be a lot of load balancers.
---
> Since a layer 7 load balancer may perform a number of complex operations on the traffic (decrypt, parse, modify, match cookies, decide what server to send to, etc), it can definitely cause some trouble and will very commonly be accused of being responsible for a lot of trouble that it only revealed. That's why logging is an extremely important aspect of layer 7 load balancing. Once a trouble is reported, it is important to figure if the load balancer took a wrong decision and if so why so that it doesn't happen anymore.
