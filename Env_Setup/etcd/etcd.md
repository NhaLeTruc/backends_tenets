# etcd introduction

## Configuration options

etcd configuration files, flags, and environment variables
You can configure etcd through the following:

- Command-line flags
- Environment variables: every flag has a corresponding environment variable that has the same name but is prefixed with **ETCD_** and formatted in all caps and snake case. For example, **--some-flag** would be **ETCD_SOME_FLAG**.
- Configuration file **etcd.conf.yml**

## Command-line flags

Flags are presented below using the format **--flag-name DEFAULT_VALUE**.

The list of flags provided below may not be up-to-date due to ongoing development changes. For the latest available flags, run **etcd --help** or refer to the [etcd help](https://github.com/etcd-io/etcd/blob/main/server/etcdmain/help.go)

## Transport security model

Securing data in transit

etcd supports automatic TLS as well as authentication through client certificates for both clients to server as well as peer (server to server / cluster) communication.

Note that etcd doesn’t enable RBAC based authentication or the authentication feature in the transport layer by default to reduce friction for users getting started with the database. Further, changing this default would be a breaking change for the project which was established since 2013. An etcd cluster which doesn’t enable security features can expose its data to any clients.

To get up and running, first have a CA certificate and a signed key pair for one member. It is recommended to create and sign a new key pair for every member in a cluster.

## Clustering Guide

Bootstrapping an etcd cluster: Static, etcd Discovery, and DNS Discovery.

Starting an etcd cluster statically requires that each member knows another in the cluster. In a number of cases, the IPs of the cluster members may be unknown ahead of time. In these cases, the etcd cluster can be bootstrapped with the help of a discovery service.

Once an etcd cluster is up and running, adding or removing members is done via runtime reconfiguration. To better understand the design behind runtime reconfiguration, we suggest reading the runtime configuration design document.

This guide will cover the following mechanisms for bootstrapping an etcd cluster:

- Static
- etcd Discovery
- DNS Discovery

### Static

As we know the cluster members, their addresses and the size of the cluster before starting, we can use an offline bootstrap configuration by setting the initial-cluster flag. Each machine will get either the following environment variables or command line:

```conf
ETCD_INITIAL_CLUSTER="infra0=http://10.0.1.10:2380,infra1=http://10.0.1.11:2380,infra2=http://10.0.1.12:2380"
ETCD_INITIAL_CLUSTER_STATE=new
```

---

```bash
--initial-cluster infra0=http://10.0.1.10:2380,infra1=http://10.0.1.11:2380,infra2=http://10.0.1.12:2380 \
--initial-cluster-state new
```

Note that the URLs specified in initial-cluster are the advertised peer URLs, i.e. they should match the value of initial-advertise-peer-urls on the respective nodes.

If spinning up multiple clusters (or creating and destroying a single cluster) with same configuration for testing purpose, it is highly recommended that each cluster is given a unique initial-cluster-token. By doing this, etcd can generate unique cluster IDs and member IDs for the clusters even if they otherwise have the exact same configuration. This can protect etcd from cross-cluster-interaction, which might corrupt the clusters.

etcd listens on listen-client-urls to accept client traffic. etcd member advertises the URLs specified in advertise-client-urls to other members, proxies, clients. Please make sure the advertise-client-urls are reachable from intended clients. A common mistake is setting advertise-client-urls to localhost or leave it as default if the remote clients should reach etcd.

On each machine, start etcd with these flags:

```bash
$ etcd --name infra0 --initial-advertise-peer-urls http://10.0.1.10:2380 \
  --listen-peer-urls http://10.0.1.10:2380 \
  --listen-client-urls http://10.0.1.10:2379,http://127.0.0.1:2379 \
  --advertise-client-urls http://10.0.1.10:2379 \
  --initial-cluster-token etcd-cluster-1 \
  --initial-cluster infra0=http://10.0.1.10:2380,infra1=http://10.0.1.11:2380,infra2=http://10.0.1.12:2380 \
  --initial-cluster-state new

$ etcd --name infra1 --initial-advertise-peer-urls http://10.0.1.11:2380 \
  --listen-peer-urls http://10.0.1.11:2380 \
  --listen-client-urls http://10.0.1.11:2379,http://127.0.0.1:2379 \
  --advertise-client-urls http://10.0.1.11:2379 \
  --initial-cluster-token etcd-cluster-1 \
  --initial-cluster infra0=http://10.0.1.10:2380,infra1=http://10.0.1.11:2380,infra2=http://10.0.1.12:2380 \
  --initial-cluster-state new

$ etcd --name infra2 --initial-advertise-peer-urls http://10.0.1.12:2380 \
  --listen-peer-urls http://10.0.1.12:2380 \
  --listen-client-urls http://10.0.1.12:2379,http://127.0.0.1:2379 \
  --advertise-client-urls http://10.0.1.12:2379 \
  --initial-cluster-token etcd-cluster-1 \
  --initial-cluster infra0=http://10.0.1.10:2380,infra1=http://10.0.1.11:2380,infra2=http://10.0.1.12:2380 \
  --initial-cluster-state new
```

The command line parameters starting with --initial-cluster will be ignored on subsequent runs of etcd. Feel free to remove the environment variables or command line flags after the initial bootstrap process. If the configuration needs changes later (for example, adding or removing members to/from the cluster), see the runtime configuration guide.

### etcd discovery

#### Lifetime of a discovery URL

A discovery URL identifies a unique etcd cluster. Instead of reusing an existing discovery URL, each etcd instance shares a new discovery URL to bootstrap the new cluster.

Moreover, discovery URLs should ONLY be used for the initial bootstrapping of a cluster. To change cluster membership after the cluster is already running, see the runtime reconfiguration guide.

#### Custom etcd discovery service

Discovery uses an existing cluster to bootstrap itself. If using a private etcd cluster, create a URL like so:

```bash
$ curl -X PUT https://myetcd.local/v2/keys/discovery/6c007a14875d53d9bf0ef5a6fc0257c817f0fb83/_config/size -d value=3
```

#### DNS discovery

DNS SRV records can be used as a discovery mechanism. The --discovery-srv flag can be used to set the DNS domain name where the discovery SRV records can be found. Setting --discovery-srv example.com causes DNS SRV records to be looked up in the listed order:

- _etcd-server-ssl._tcp.example.com
- _etcd-server._tcp.example.com

If _etcd-server-ssl._tcp.example.com is found then etcd will attempt the bootstrapping process over TLS.

To help clients discover the etcd cluster, the following DNS SRV records are looked up in the listed order:

- _etcd-client._tcp.example.com
- _etcd-client-ssl._tcp.example.com

If _etcd-client-ssl._tcp.example.com is found, clients will attempt to communicate with the etcd cluster over SSL/TLS.

If etcd is using TLS, the discovery SRV record (e.g. example.com) must be included in the SSL certificate DNS SAN along with the hostname, or clustering will fail with log messages like the following:

```bash
[...] rejected connection from "10.0.1.11:53162" (error "remote error: tls: bad certificate", ServerName "example.com")
```

If etcd is using TLS without a custom certificate authority, the discovery domain (e.g., example.com) must match the SRV record domain (e.g., infra1.example.com). This is to mitigate attacks that forge SRV records to point to a different domain; the domain would have a valid certificate under PKI but be controlled by an unknown third party.

The -discovery-srv-name flag additionally configures a suffix to the SRV name that is queried during discovery. Use this flag to differentiate between multiple etcd clusters under the same domain. For example, if discovery-srv=example.com and -discovery-srv-name=foo are set, the following DNS SRV queries are made:

- _etcd-server-ssl-foo._tcp.example.com
- _etcd-server-foo._tcp.example.com

## References

1. [etcd docs](https://etcd.io/docs/v3.5/)
2. [etcd tutorials](https://etcd.io/docs/v3.5/tutorials/)
3. [etcd configuration](https://etcd.io/docs/v3.5/op-guide/configuration/)
4. [etcd runtime configuration](https://etcd.io/docs/v3.5/op-guide/runtime-configuration/)
5. [etcd.conf.yml.sample](https://github.com/etcd-io/etcd/blob/main/etcd.conf.yml.sample)
6. [etcd TLS](https://etcd.io/docs/v3.5/op-guide/security/)
7. [etcd tuning](https://etcd.io/docs/v3.5/tuning/)
8. [etcd clustering](https://etcd.io/docs/v3.5/op-guide/clustering/)
9. [discovery_protocol](https://etcd.io/docs/v3.5/dev-internal/discovery_protocol/)
