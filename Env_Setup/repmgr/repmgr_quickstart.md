# Setup repmgr

## PostgreSQL configuration

On the primary server, a PostgreSQL instance must be initialised and running. The following replication settings may need to be adjusted:

```cfg
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

## References

1. [quickstart-postgresql-configuration](https://www.repmgr.org/docs/current/quickstart-postgresql-configuration.html)
2. [CONFIGURATION-POSTGRESQL](https://www.repmgr.org/docs/current/configuration-prerequisites.html#CONFIGURATION-POSTGRESQL)
3. [repmgr configuration](https://www.repmgr.org/docs/current/configuration.html)
4. [Using pg_rewind](https://www.repmgr.org/docs/current/repmgr-node-rejoin.html#REPMGR-NODE-REJOIN-PG-REWIND)
