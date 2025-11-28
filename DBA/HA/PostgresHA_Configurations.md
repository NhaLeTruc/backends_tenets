# Handling and Avoiding Downtime

## Determining acceptable losses

System outage and response escalation expectations are generally codified in a Service
Level Agreement (SLA). How long should the maintenance last? How often should
planned outages occur? When should users be informed and to what extent? Who is
included in the set of potential database users? All of these things, and more, should be
defined before a production system is released.

> Should there be a questionaire for engineers to follow with business partners in constructing a SLA?

The next question we need to answer is how uptime is defined. One frequently quoted
value is the number of nines, referring to a percentage approaching 100 percent. Three nines
for example, would be 99.9 percent of a year, which is almost nine hours. Four nines is only
about 50 minutes. Keep in mind that the SLA can be written to include or exclude planned
maintenance, depending on the audience. Unplanned outages definitely count, and
remember that this is the total cumulative time for the entire year.

## Common Postgres Configuration

Find these settings in the postgresql.conf file for the desired PostgreSQL instance and
perform the following steps:

1. Set max_connections to three times the number of processor cores on the
server. Include virtual (hyperthreading) cores. Set shared_buffers to 4GB for
servers with up to 64 GB of RAM. Use 8GB for systems with more than 64 GB of
RAM.
2. Set work_mem to 8MB for servers with up to 32 GB of RAM, 16MB for servers with
up to 64 GB of RAM, and 32MB for systems with more than 64 GB of RAM. If
max_connections is greater than 400, divide this by two. Systems with exceedingly large amounts of RAM (256GB and above) do not require artificially halving the final suggested value for work_mem.
3. Set maintenance_work_mem to 1GB.
4. Set wal_level to one of these settings:
        Use hot_standby for versions prior to 9.6.
        Use replica for version 9.6 and beyond.
5. Set minimum WAL size to (system memory in MB / 20 / 16):
        Use checkpoint_segments parameter for 9.4 and below.
        Use min_wal_size for 9.5 and beyond. Then double this value and
        use it to set max_wal_size.
6. Set checkpoint_completion_target to 0.8.
7. Set archive_mode to on.
8. Set archive_command to /bin/true.
9. Set max_wal_senders to 5.
10. Retain necessary WAL files with these settings:
Set wal_keep_segments to (3 * checkpoint_segments) for 9.3 and
below.
Set replication_slots to 5 for 9.4 and above.
11. Set random_page_cost to 2.0 if you are using RAID or high-performance SAN; 1.1 for SSD-based storage.
12. Set effective_cache_size to half of the available system RAM.
13. Set log_min_duration_statement to 1000.
14. Set log_checkpoints to on.

## Configuration – managing scary settings

When it comes to highly-available database servers and configuration, a very important
aspect is whether or not a changed setting requires a database restart before taking effect.
While it is true that many of these are important enough and they should be set correctly
before starting the server, sometimes our requirements evolve.

If or when this happens, there is no alternative but to restart the PostgreSQL service. There
are, of course, steps we can take to avoid this fate. Perhaps, an existing server didn't need
the WAL output to be compatible with hot standby servers. Maybe, we need to move the
logfile, enable WAL archival, or increase the amount of connections.

These are all scenarios that require us to restart PostgreSQL. We can avoid this by
identifying these settings early and paying special attention to them.

Follow these steps to learn more about PostgreSQL settings:

Execute the following query to obtain a list of settings that require a server restart
and their current value:

```SQL
 SELECT name, setting
 FROM pg_settings
 WHERE context = 'postmaster';
```

Execute this query for a list of only those settings that are not changed from the
default and require restart:

```SQL
 SELECT name, setting, boot_val
 FROM pg_settings
 WHERE context = 'postmaster'
 AND boot_val = setting;
```

Execute the following query for a list of all settings and a translation of how the
setting is managed:

```SQL
 SELECT name,
 CASE context
 WHEN 'postmaster' THEN 'REQUIRES RESTART'
 WHEN 'sighup' THEN 'Reload Config'
 WHEN 'backend' THEN 'Reload Config'
 WHEN 'superuser' THEN 'Reload Config / Superuser'
 WHEN 'user' THEN 'Reload Config / User SET'
 END AS when_changed
 FROM pg_settings
 WHERE context != 'internal'
 ORDER BY when_changed;
```
