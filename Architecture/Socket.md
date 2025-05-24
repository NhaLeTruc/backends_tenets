# Sockets

A socket is an endpoint of a two-way communication link between programs, typically on different machines, over a network. It acts like a port, allowing programs to send and receive data. A socket is identified by a combination of an IP address and a port number.

Socket packages messages into TCP/UDP packets on layer 4 of the OSI model. These packets are then sent to layer 3 for IP routing to their destinations.

## Sockets in Networking

- **Two-way communication:** Sockets enable programs to exchange data in both directions.
- **Network communication:** They are the foundation for programs to interact over a network, whether it's a local network or the internet.
- **Endpoints:** Each socket represents an endpoint of a connection, and a connection is identified by the IP address and port number of both endpoints.
- **Abstraction:** Sockets provide a convenient abstraction for network communication, hiding the complexities of lower-level protocols.
- **File descriptors:** In some systems, sockets can be treated as file descriptors, allowing programs to read and write to them as they would with regular files.

## Socket Types

- **Stream sockets (TCP):** Provide reliable, ordered data delivery using the Transmission Control Protocol (TCP).
- **Datagram sockets (UDP):** Offer unreliable, unordered data delivery using the User Datagram Protocol (UDP).
- **Unix Domain Sockets:** Allow communication between processes on the same machine, using local files instead of network interfaces.
- **Raw sockets:** Provide direct access to network packets, allowing applications to create and modify packets at a lower level.

## How Sockets Work

1. **Create a socket:** An application creates a socket, specifying its type (TCP or UDP) and other options.
2. **Bind to a port:** The socket is bound to a specific port number, allowing the operating system to identify the application that should receive data for that port.
3. **Establish a connection:** For TCP sockets, a client socket connects to a server socket, establishing a persistent connection.
4. **Send and receive data:** Applications can send and receive data through the socket, using the read and write system calls (or equivalent functions in programming languages).
5. **Close the connection:** When communication is complete, the connection is closed.
