# Patroni configuration

There are 3 types of Patroni configuration:

## Global dynamic configuration

These options are stored in the DCS (Distributed Configuration Store) and applied on all cluster nodes. Dynamic configuration can be set at any time using patronictl edit-config tool or Patroni REST API. If the options changed are not part of the startup configuration, they are applied asynchronously (upon the next wake up cycle) to every node, which gets subsequently reloaded. If the node requires a restart to apply the configuration (for PostgreSQL parameters with context postmaster, if their values have changed), a special flag pending_restart indicating this is set in the members.data JSON. Additionally, the node status indicates this by showing "restart_pending": true.

## Local configuration file (patroni.yml)

These options are defined in the configuration file and take precedence over dynamic configuration. patroni.yml can be changed and reloaded at runtime (without restart of Patroni) by sending SIGHUP to the Patroni process, performing POST /reload REST-API request or executing patronictl reload. Local configuration can be either a single YAML file or a directory. When it is a directory, all YAML files in that directory are loaded one by one in sorted order. In case a key is defined in multiple files, the occurrence in the last file takes precedence.

## Environment configuration

It is possible to set/override some of the “Local” configuration parameters with environment variables. Environment configuration is very useful when you are running in a dynamic environment and you don’t know some of the parameters in advance (for example it’s not possible to know your external IP address when you are running inside docker).

## Important rules

### PostgreSQL parameters controlled by Patroni

Some of the PostgreSQL parameters must hold the same values on the primary and the replicas. For those, values set either in the local patroni configuration files or via the environment variables take no effect. To alter or set their values one must change the shared configuration in the DCS. Below is the actual list of such parameters together with the default values:

- max_connections: 100
- max_locks_per_transaction: 64
- max_worker_processes: 8
- max_prepared_transactions: 0
- wal_level: hot_standby
- track_commit_timestamp: off

For the parameters below, PostgreSQL does not require equal values among the primary and all the replicas. However, considering the possibility of a replica to become the primary at any time, it doesn’t really make sense to set them differently; therefore, Patroni restricts setting their values to the dynamic configuration.

- max_wal_senders: 10
- max_replication_slots: 10
- wal_keep_segments: 8
- wal_keep_size: 128MB

## Reference

[patroni_configuration](https://patroni.readthedocs.io/en/latest/patroni_configuration.html)