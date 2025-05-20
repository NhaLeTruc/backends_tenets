# Setup repmgr

## PostgreSQL configuration

On the primary server, a PostgreSQL instance must be initialised and running. The following replication settings may need to be adjusted:

```conf
    # Enable replication connections; set this value to at least one more
    # than the number of standbys which will connect to this server
    # (note that repmgr will execute "pg_basebackup" in WAL streaming mode,
    # which requires two free WAL senders).
    #
    # See: https://www.postgresql.org/docs/current/runtime-config-replication.html#GUC-MAX-WAL-SENDERS

    max_wal_senders = 10

    # If using replication slots, set this value to at least one more
    # than the number of standbys which will connect to this server.
    # Note that repmgr will only make use of replication slots if
    # "use_replication_slots" is set to "true" in "repmgr.conf".
    # (If you are not intending to use replication slots, this value
    # can be set to "0").
    #
    # See: https://www.postgresql.org/docs/current/runtime-config-replication.html#GUC-MAX-REPLICATION-SLOTS

    max_replication_slots = 10

    # Ensure WAL files contain enough information to enable read-only queries
    # on the standby.
    #
    #  PostgreSQL 9.5 and earlier: one of 'hot_standby' or 'logical'
    #  PostgreSQL 9.6 and later: one of 'replica' or 'logical'
    #    ('hot_standby' will still be accepted as an alias for 'replica')
    #
    # See: https://www.postgresql.org/docs/current/runtime-config-wal.html#GUC-WAL-LEVEL

    wal_level = 'hot_standby'

    # Enable read-only queries on a standby
    # (Note: this will be ignored on a primary but we recommend including
    # it anyway, in case the primary later becomes a standby)
    #
    # See: https://www.postgresql.org/docs/current/runtime-config-replication.html#GUC-HOT-STANDBY

    hot_standby = on

    # Enable WAL file archiving
    #
    # See: https://www.postgresql.org/docs/current/runtime-config-wal.html#GUC-ARCHIVE-MODE

    archive_mode = on

    # Set archive command to a dummy command; this can later be changed without
    # needing to restart the PostgreSQL instance.
    #
    # See: https://www.postgresql.org/docs/current/runtime-config-wal.html#GUC-ARCHIVE-COMMAND

    archive_command = '/bin/true'
```

> Rather than editing these settings in the default postgresql.conf file, create a separate file such as postgresql.replication.conf and include it from the end of the main configuration file with: include 'postgresql.replication.conf'.
---
> Additionally, if you are intending to use pg_rewind, and the cluster was not initialised using data checksums, you may want to consider enabling wal_log_hints

## Create the repmgr user and database

Create a dedicated PostgreSQL superuser account and a database for the repmgr metadata, e.g. For the examples in this document, the name repmgr will be used for both user and database, but any names can be used.

```bash
    createuser -s repmgr
    createdb repmgr -O repmgr
```

> For the sake of simplicity, the repmgr user is created as a superuser. If desired, it's possible to create the repmgr user as a normal user. However for certain operations superuser permissions are required; in this case the command line option --superuser can be provided to specify a superuser. It's also assumed that the repmgr user will be used to make the replication connection from the standby to the primary; again this can be overridden by specifying a separate replication user when registering each node.
---
> repmgr will install the repmgr extension, which creates a repmgr schema containing the repmgr's metadata tables as well as other functions and views. We also recommend that you set the repmgr user's search path to include this schema name, e.g.

```SQL
    ALTER USER repmgr SET search_path TO repmgr, "$user", public;
```

## Configuring authentication in pg_hba.conf

Ensure the repmgr user has appropriate permissions in pg_hba.conf and can connect in replication mode; pg_hba.conf should contain entries similar to the following:

```conf
    local   replication   repmgr                              trust
    host    replication   repmgr      127.0.0.1/32            trust
    host    replication   repmgr      192.168.1.0/24          trust

    local   repmgr        repmgr                              trust
    host    repmgr        repmgr      127.0.0.1/32            trust
    host    repmgr        repmgr      192.168.1.0/24          trust
```

Note that these are simple settings for testing purposes. Adjust according to your network environment and authentication requirements.

## Preparing the standby

On the standby, do not create a PostgreSQL instance (i.e. do not execute initdb or any database creation scripts provided by packages), but do ensure the destination data directory (and any other directories which you want PostgreSQL to use) exist and are owned by the postgres system user. Permissions must be set to 0700 (drwx------).

> repmgr will place a copy of the primary's database files in this directory. It will however refuse to run if a PostgreSQL instance has already been created there.

Check the primary database is reachable from the standby using psql:

```bash
    psql 'host=node1 user=repmgr dbname=repmgr connect_timeout=2'
```

> repmgr stores connection information as libpq connection strings throughout. This documentation refers to them as conninfo strings; an alternative name is DSN (data source name). We'll use these in place of the -h hostname -d databasename -U username syntax.

## repmgr configuration file

Create a repmgr.conf file on the primary server. The file must contain at least the following parameters:

```conf
    node_id=1
    node_name='node1'
    conninfo='host=node1 user=repmgr dbname=repmgr connect_timeout=2'
    data_directory='/var/lib/postgresql/data'
```

repmgr.conf should not be stored inside the PostgreSQL data directory, as it could be overwritten when setting up or reinitialising the PostgreSQL server. See sections Configuration and configuration file for further details about repmgr.conf.

> repmgr only uses pg_bindir when it executes PostgreSQL binaries directly. For user-defined scripts such as promote_command and the various service_*_commands, you must always explicitly provide the full path to the binary or script being executed, even if it is repmgr itself. This is because these options can contain user-defined scripts in arbitrary locations, so prepending pg_bindir may break them.
---
> For Debian-based distributions we recommend explicitly setting pg_bindir to the directory where pg_ctl and other binaries not in the standard path are located. For PostgreSQL 9.6 this would be /usr/lib/postgresql/9.6/bin/.
---
> If your distribution places the repmgr binaries in a location other than the PostgreSQL installation directory, specify this with repmgr_bindir to enable repmgr to perform operations (e.g. repmgr cluster crosscheck) on other nodes.

## Register the primary server

To enable repmgr to support a replication cluster, the primary node must be registered with repmgr. This installs the repmgr extension and metadata objects, and adds a metadata record for the primary server:

```bash
    $ repmgr -f /etc/repmgr.conf primary register
    INFO: connecting to primary database...
    NOTICE: attempting to install extension "repmgr"
    NOTICE: "repmgr" extension successfully installed
    NOTICE: primary node record (id: 1) registered
```

Verify status of the cluster like this:

```bash
    $ repmgr -f /etc/repmgr.conf cluster show
     ID | Name  | Role    | Status    | Upstream | Connection string
    ----+-------+---------+-----------+----------+--------------------------------------------------------
     1  | node1 | primary | * running |          | host=node1 dbname=repmgr user=repmgr connect_timeout=2
```

The record in the repmgr metadata table will look like this:

```bash
    repmgr=# SELECT * FROM repmgr.nodes;
    -[ RECORD 1 ]----+-------------------------------------------------------
    node_id          | 1
    upstream_node_id |
    active           | t
    node_name        | node1
    type             | primary
    location         | default
    priority         | 100
    conninfo         | host=node1 dbname=repmgr user=repmgr connect_timeout=2
    repluser         | repmgr
    slot_name        |
    config_file      | /etc/repmgr.conf
```

Each server in the replication cluster will have its own record. If repmgrd is in use, the fields upstream_node_id, active and type will be updated when the node's status or role changes.

## Clone the standby server

Create a repmgr.conf file on the standby server. It must contain at least the same parameters as the primary's repmgr.conf, but with the mandatory values node, node_name, conninfo (and possibly data_directory) adjusted accordingly, e.g.:

```conf
    node_id=2
    node_name='node2'
    conninfo='host=node2 user=repmgr dbname=repmgr connect_timeout=2'
    data_directory='/var/lib/postgresql/data'
```

Use the --dry-run option to check the standby can be cloned:

```bash
    $ repmgr -h node1 -U repmgr -d repmgr -f /etc/repmgr.conf standby clone --dry-run
    NOTICE: using provided configuration file "/etc/repmgr.conf"
    NOTICE: destination directory "/var/lib/postgresql/data" provided
    INFO: connecting to source node
    NOTICE: checking for available walsenders on source node (2 required)
    INFO: sufficient walsenders available on source node (2 required)
    NOTICE: standby will attach to upstream node 1
    HINT: consider using the -c/--fast-checkpoint option
    INFO: all prerequisites for "standby clone" are met
```

If no problems are reported, the standby can then be cloned with:

```bash
    $ repmgr -h node1 -U repmgr -d repmgr -f /etc/repmgr.conf standby clone

    NOTICE: using configuration file "/etc/repmgr.conf"
    NOTICE: destination directory "/var/lib/postgresql/data" provided
    INFO: connecting to source node
    NOTICE: checking for available walsenders on source node (2 required)
    INFO: sufficient walsenders available on source node (2 required)
    INFO: creating directory "/var/lib/postgresql/data"...
    NOTICE: starting backup (using pg_basebackup)...
    HINT: this may take some time; consider using the -c/--fast-checkpoint option
    INFO: executing:
      pg_basebackup -l "repmgr base backup" -D /var/lib/postgresql/data -h node1 -U repmgr -X stream
    NOTICE: standby clone (using pg_basebackup) complete
    NOTICE: you can now start your PostgreSQL server
    HINT: for example: pg_ctl -D /var/lib/postgresql/data start
```

This has cloned the PostgreSQL data directory files from the primary node1 using PostgreSQL's pg_basebackup utility. Replication configuration containing the correct parameters to start streaming from this primary server will be automatically appended to postgresql.auto.conf. (In PostgreSQL 11 and earlier the file recovery.conf will be created).

> By default, any configuration files in the primary's data directory will be copied to the standby. Typically these will be postgresql.conf, postgresql.auto.conf, pg_hba.conf and pg_ident.conf. These may require modification before the standby is started.

Make any adjustments to the standby's PostgreSQL configuration files now, then start the server.

## Register the standby

Register the standby server with:

```bash
    $ repmgr -f /etc/repmgr.conf standby register
    NOTICE: standby node "node2" (ID: 2) successfully registered
```

Check the node is registered by executing repmgr cluster show on the standby:

```bash
    $ repmgr -f /etc/repmgr.conf cluster show

     ID | Name  | Role    | Status    | Upstream | Location | Priority | Timeline | Connection string
    ----+-------+---------+-----------+----------+----------+----------+----------+--------------------------------------
     1  | node1 | primary | * running |          | default  | 100      | 1        | host=node1 dbname=repmgr user=repmgr
     2  | node2 | standby |   running | node1    | default  | 100      | 1        | host=node2 dbname=repmgr user=repmgr
```

Both nodes are now registered with repmgr and the records have been copied to the standby server.

## References

1. [quickstart](https://www.repmgr.org/docs/current/quickstart.html)
2. [quickstart-postgresql-configuration](https://www.repmgr.org/docs/current/quickstart-postgresql-configuration.html)
3. [CONFIGURATION-POSTGRESQL](https://www.repmgr.org/docs/current/configuration-prerequisites.html#CONFIGURATION-POSTGRESQL)
4. [repmgr configuration](https://www.repmgr.org/docs/current/configuration.html)
5. [Using pg_rewind](https://www.repmgr.org/docs/current/repmgr-node-rejoin.html#REPMGR-NODE-REJOIN-PG-REWIND)
6. [repmgr.conf.sample](https://raw.githubusercontent.com/EnterpriseDB/repmgr/master/repmgr.conf.sample)
