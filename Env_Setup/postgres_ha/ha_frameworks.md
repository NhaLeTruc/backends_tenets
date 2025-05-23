# High Availability in Postgres

High availability (HA) in PostgreSQL refers to the implementation of systems and techniques that ensure continuous database operations and minimize downtime.

High Availability is a very important and needed feature for your database. A High Availability (HA) database architecture aims to ensure the normal working of applications by automatically detecting and healing from a disaster. Objective is to avoid having a single point of failure, i.e. having a component in the system which is not redundant and can be disabled without impacting the overall performance.

HA architecture ensures the application is highly available throughout its operation even in case of malfunction of one or more components. Most critical measure of a HA system is MTR (mean time to recover), as opposed to MTBF (mean time between failures) which measures reliability. Adding redundant components to a system makes it less reliable, in the sense that it increases probability of failure of the components, but it makes it more available, as failure does not cause downtime of the whole system.

At database level, a High Availability cluster is a group of servers handling business critical workloads. It consists of a couple of servers replicating with each other. Applications are managed by the Primary database and, in case of any malfunction, the standby database gets promoted to handle the role of Primary.

A High Availability architecture ensures that the application connectivity and user experience does not get hampered during a disaster and the application can continue to fetch data without any manual interference. HA architecture should be capable of handling and recovering from disasters automatically with minimal downtime and without manual intervention.

## Setup a Virtual IP (VIP)

A Virtual IP is basically a secondary IP configured on the server which can be used to connect to the instance. We will use this VIP to connect to the Primary Database from the Application end. This will be done by rerouting the connections coming over the VIP to point to the Network interface of the Primary Database.

In case of disaster, the repmgr daemon process records the Primary node going down. Once it verifies that the Primary database is not reachable, it will promote the standby instance as Primary. Once the new Primary is up, we will update the Routing tables to reroute the VIP to connect to the new Primary node so that the application continues to fetch data over the same IP address.

To set up a Virtual IP, first we need to make sure the IP being used as a VIP is out of the Allowed IP range of the underlying VPC or Virtual Network, so that it does not conflict with any future IP allotments on the VPC.

To define the VIP, we will use the Netplan utility that governs networking in Linux systems.  We will need to create a new netplan configuration for attaching the failover IP on all the servers in the replication cluster.

Once the new VIP is configured, we need to create routes to make this VIP point to the Network Interface of the Primary node in the Route Tables.

## Handling repmgr events to perform VIP failover

During a disaster, or a manual switchover, we will need to switch the VIP to point to the new Primary node in the route tables, so that the application can continue to access data. The process of updating Routing tables and/or reattaching Elastic IP to the new Primary can be automated using repmgr events recorded and monitored by the daemon process. We can set up a repmgr hook script to execute the script which will update the routing table to point to the network interface of the new primary node.

Once everything is configured and you are able to connect to the Primary database using the Virtual IP, we can update the Connection strings at the Application end to point to the VIP to connect to the database. After this is done, your application will still connect to the Primary node using the same VIP, and the repmgr daemon will invoke repmgr hook script to handle the task of pointing the VIP to the current Primary node.

## Handling Split Brain situations

In case of a split brain scenario, where the old primary database is started again after the failover is complete, the application will still point to the correct, new primary node, as the VIP is routing the connections to the network interface of the new Primary node. This prevents the application from connecting to the rebooted failed node and causing data integrity issues.

Using the repmgr checks, we can also monitor such split brain situations, where repmgr detects the replication is broken and both the nodes are working as primary.

When the replication cluster comes in such a state, we can use the repmgr node rejoin to force the old Primary to rejoin the replication cluster as a Standby node.

Monitoring and implementing the node rejoin during a split brain scenario can be automated as well to add Fault tolerance capability to the HA cluster, making it a reliable solution for Critical workloads.

## References

1. [Postgres High Availability using only Repmgr](https://www.enterprisedb.com/blog/how-to-achieve-high-availability-using-virtual-ips)

## Options for Highly Available Topology

You can set up an HA cluster:

1. With stacked control plane nodes, where etcd nodes are colocated with control plane nodes.
2. With external etcd nodes, where etcd runs on separate nodes from the control plane.

### Stacked etcd topology

A stacked HA cluster is a topology where the distributed data storage cluster provided by etcd is stacked on top of the cluster formed by the nodes that run control plane components.

This topology couples the control planes and etcd members on the same nodes. It is simpler to set up than a cluster with external etcd nodes, and simpler to manage for replication.

However, a stacked cluster runs the risk of failed coupling. If one node goes down, both an etcd member and a control plane instance are lost, and redundancy is compromised. You can mitigate this risk by adding more control plane nodes.

You should therefore run a minimum of three stacked control plane nodes for an HA cluster.

### External etcd topology

An HA cluster with external etcd is a topology where the distributed data storage cluster provided by etcd is external to the cluster formed by the nodes that run control plane components.

This topology decouples the control plane and etcd member. It therefore provides an HA setup where losing a control plane instance or an etcd member has less impact and does not affect the cluster redundancy as much as the stacked HA topology.

However, this topology requires twice the number of hosts as the stacked HA topology. A minimum of three hosts for control plane nodes and three hosts for etcd nodes are required for an HA cluster with this topology.

![](images/external_etcd_ha.png)

> NOTE: Theoretically, there is no hard limit. However, an etcd cluster probably should have no more than seven nodes. A 5-member etcd cluster can tolerate two member failures, which is enough in most cases. The larger clusters provide better fault tolerance, BUT write performance will suffer because data must be replicated across more machines.

It is possible to do so for small clusters (3 to 5 (or even 7) nodes) before the chattiness of the etcd quorum process becomes a problem.

Etcd clusters also need highly performant storage, so it may be better to provide specialised resources to the etcd nodes while the regular control plane nodes have less optimised (and probably cheaper) resources.

From the operations point of view, removing the etcd component from the control plane nodes will make them stateless (as far as I know), so they would be easier to maintain.

### References II

1. [etcd FAQ](https://etcd.io/docs/v3.3/faq/#what-is-maximum-cluster-size)
2. [Colocated or Separated etcd cluster](https://discuss.kubernetes.io/t/why-should-i-separate-control-plane-instances-from-etcd-instances/17706/2)
