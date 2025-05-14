# Introduction to HAProxy

## HAProxy is

- **a TCP proxy (L4) :** it can accept a TCP connection from a listening socket, connect to a server and attach these sockets together allowing traffic to flow in both directions; IPv4, IPv6 and even UNIX sockets are supported on either side, so this can provide an easy way to translate addresses between different families.
- **an HTTP reverse-proxy (called a "gateway" in HTTP terminology - L7) :** it presents itself as a server, receives HTTP requests over connections accepted on a listening TCP socket, and passes the requests from these connections to servers using different connections. It may use any combination of HTTP/1.x or HTTP/2 on any side and will even automatically detect the protocol spoken on each side when ALPN is used over TLS.
- **an SSL terminator / initiator / offloader :** SSL/TLS may be used on the connection coming from the client, on the connection going to the server, or even on both connections. A lot of settings can be applied per name (SNI), and may be updated at runtime without restarting. Such setups are extremely scalable and deployments involving tens to hundreds of thousands of certificates were reported.
- **a TCP normalizer :** since connections are locally terminated by the operating system, there is no relation between both sides, so abnormal traffic such as invalid packets, flag combinations, window advertisements, sequence numbers, incomplete connections (SYN floods), or so will not be passed to the other side. This protects fragile TCP stacks from protocol attacks, and also allows to optimize the connection parameters with the client without having to modify the servers' TCP stack settings.
- **an HTTP normalizer :** when configured to process HTTP traffic, only valid complete requests are passed. This protects against a lot of protocol-based attacks. Additionally, protocol deviations for which there is a tolerance in the specification are fixed so that they don't cause problem on the servers (e.g. multiple-line headers).
- **an HTTP fixing tool :** it can modify / fix / add / remove / rewrite the URL or any request or response header. This helps fixing interoperability issues in complex environments.
- **a content-based switch :** it can consider any element from the request to decide what server to pass the request or connection to. Thus it is possible to handle multiple protocols over a same port (e.g. HTTP, HTTPS, SSH).
- **a server load balancer :** it can load balance TCP connections and HTTP requests. In TCP mode, load balancing decisions are taken for the whole connection. In HTTP mode, decisions are taken per request.
- **a traffic regulator :** it can apply some rate limiting at various points, protect the servers against overloading, adjust traffic priorities based on the contents, and even pass such information to lower layers and outer network components by marking packets.
- **a protection against DDoS and service abuse :** it can maintain a wide number of statistics per IP address, URL, cookie, etc and detect when an abuse is happening, then take action (slow down the offenders, block them, send them to outdated contents, etc).
- **an observation point for network troubleshooting :** due to the precision of the information reported in logs, it is often used to narrow down some network-related issues.
- **an HTTP compression offloader :** it can compress responses which were not compressed by the server, thus reducing the page load time for clients with poor connectivity or using high-latency, mobile networks.
- **a caching proxy :** it may cache responses in RAM so that subsequent requests for the same object avoid the cost of another network transfer from the server as long as the object remains present and valid. It will however not store objects to any persistent storage. Please note that this caching feature is designed to be maintenance free and focuses solely on saving haproxy's precious resources and not on save the server's resources. Caches designed to optimize servers require much more tuning and flexibility. If you instead need such an advanced cache, please use Varnish Cache, which integrates perfectly with haproxy, especially when SSL/TLS is needed on any side.
- **a FastCGI gateway :** FastCGI can be seen as a different representation of HTTP, and as such, HAProxy can directly load-balance a farm comprising any combination of FastCGI application servers without requiring to insert another level of gateway between them. This results in resource savings and a reduction of maintenance costs.

## HAProxy is not

- **an explicit HTTP proxy**, i.e. the proxy that browsers use to reach the internet. There are excellent open-source software dedicated for this task, such as Squid. However HAProxy can be installed in front of such a proxy to provide load balancing and high availability.
- **a data scrubber :** it will not modify the body of requests nor responses.
- **a static web server :** during startup, it isolates itself inside a chroot jail and drops its privileges, so that it will not perform any single file-system access once started. As such it cannot be turned into a static web server (dynamic servers are supported through FastCGI however). There are excellent open-source software for this such as Apache or Nginx, and HAProxy can be easily installed in front of them to provide load balancing, high availability and acceleration.
- **a packet-based load balancer :** it will not see IP packets nor UDP datagrams, will not perform NAT or even less DSR. These are tasks for lower layers. Some kernel-based components such as IPVS (Linux Virtual Server) already do this pretty well and complement perfectly with HAProxy.

## How HAProxy works

HAProxy is an event-driven, non-blocking engine combining a very fast I/O layer with a priority-based, multi-threaded scheduler. As it is designed with a data forwarding goal in mind, its architecture is optimized to move data as fast as possible with the least possible operations.

It focuses on optimizing the CPU cache's efficiency by sticking connections to the same CPU as long as possible. As such it implements a layered model offering bypass mechanisms at each level ensuring data doesn't reach higher levels unless needed.

Most of the processing is performed in the kernel, and HAProxy does its best to help the kernel do the work as fast as possible by giving some hints or by avoiding certain operation when it guesses they could be grouped later. As a result, typical figures show 15% of the processing time spent in HAProxy versus 85% in the kernel in TCP or HTTP close mode, and about 30% for HAProxy versus 70% for the kernel in HTTP keep-alive mode.

> A single process can run many proxy instances; configurations as large as 300'000 distinct proxies in a single process were reported to run fine. A single core, single CPU setup is far more than enough for more than 99% users, and as such, users of containers and virtual machines are encouraged to use the absolute smallest images they can get to save on operational costs and simplify troubleshooting.
---
> However the machine HAProxy runs on must never ever swap, and its CPU must not be artificially throttled (sub-CPU allocation in hypervisors) nor be shared with compute-intensive processes which would induce a very high context-switch latency.
---
> Threading allows to exploit all available processing capacity by using one thread per CPU core. This is mostly useful for SSL or when data forwarding rates above 40 Gbps are needed. In such cases it is critically important to avoid communications between multiple physical CPUs, which can cause strong bottlenecks in the network stack and in HAProxy itself. While counter-intuitive to some, the first thing to do when facing some performance issues is often to reduce the number of CPUs HAProxy runs on.

## HAProxy Logging and Startup

HAProxy only requires the haproxy executable and a configuration file to run. For logging it is highly recommended to have a properly configured syslog daemon and log rotations in place. Logs may also be sent to stdout/stderr, which can be useful inside containers. The configuration files are parsed before starting, then HAProxy tries to bind all listening sockets, and refuses to start if anything fails. Past this point it cannot fail anymore. This means that there are no runtime failures and that if it accepts to start, it will work until it is stopped.

Once HAProxy is started, it does exactly 3 things :

- process incoming connections;
- periodically check the servers' status (known as health checks);
- exchange information with other haproxy nodes.

## Reference

1. [HAProxy introduction](https://www.haproxy.com/documentation/haproxy-configuration-manual/latest/intro/)
