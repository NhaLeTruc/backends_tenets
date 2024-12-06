# Understanding the CAP theorem

- **Consistency:** This term indicates whether all the nodes in a cluster see the
same data at the same time or not. A read-only node has to see all
previously completed reads at any time.
- **Availability:** Reads and writes have to succeed all the time. In other words
a node has to be available for users at any point of time.
- **Partition tolerance:** This means that the system will continue to work even
if arbitrary messages are lost on the way. A network partition event occurs
when a system is no longer accessible (think of a network connection
failure). A different way of considering partition tolerance is to think of it as
message passing. If an individual system can no longer send or receive
messages from other systems, it means that it has been effectively
partitioned out of the network. The guaranteed properties are maintained
even when netw