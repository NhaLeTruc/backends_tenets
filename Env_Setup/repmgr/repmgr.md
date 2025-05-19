# repmgr overview

The following terms are used throughout the repmgr documentation.

- **replication cluster**
In the repmgr documentation, "replication cluster" refers to the network of PostgreSQL servers connected by streaming replication.

- **node**
A node is a single PostgreSQL server within a replication cluster.

- **upstream node**
The node a standby server connects to, in order to receive streaming replication. This is either the primary server, or in the case of cascading replication, another standby.

- **failover**
This is the action which occurs if a primary server fails and a suitable standby is promoted as the new primary. The repmgrd daemon supports automatic failover to minimise downtime.

- **switchover**
In certain circumstances, such as hardware or operating system maintenance, it's necessary to take a primary server offline; in this case a controlled switchover is necessary, whereby a suitable standby is promoted and the existing primary removed from the replication cluster in a controlled manner. The repmgr command line client provides this functionality.

- **fencing**
In a failover situation, following the promotion of a new standby, it's essential that the previous primary does not unexpectedly come back on line, which would result in a split-brain situation. To prevent this, the failed primary should be isolated from applications, i.e. "fenced off".

- **witness server**
repmgr provides functionality to set up a so-called "witness server" to assist in determining a new primary server in a failover situation with more than one standby. The witness server itself is not part of the replication cluster, although it does contain a copy of the repmgr metadata schema.

The purpose of a witness server is to provide a "casting vote" where servers in the replication cluster are split over more than one location. In the event of a loss of connectivity between locations, the presence or absence of the witness server will decide whether a server at that location is promoted to primary; this is to prevent a "split-brain" situation where an isolated location interprets a network outage as a failure of the (remote) primary and promotes a (local) standby.

A witness server only needs to be created if repmgrd is in use.

## Components

repmgr is a suite of open-source tools to manage replication and failover within a cluster of PostgreSQL servers. It supports and enhances PostgreSQL's built-in streaming replication, which provides a single read/write primary server and one or more read-only standbys containing near-real time copies of the primary server's database. It provides two main tools:

- **repmgr**
  A command-line tool used to perform administrative tasks such as:

    1. setting up standby servers
    2. promoting a standby server to primary
    3. switching over primary and standby servers
    4. displaying the status of servers in the replication cluster

- **repmgrd**
  A daemon which actively monitors servers in a replication cluster and performs the following tasks:

  1. monitoring and recording replication performance
  2. performing failover by detecting failure of the primary and promoting the most suitable standby server
  3. provide notifications about events in the cluster to a user-defined script which can perform tasks such as sending alerts by email

