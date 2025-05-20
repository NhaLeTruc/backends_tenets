# pgBackRest Introduction

pgBackRest can be used entirely with command-line parameters but a configuration file is more practical for installations that are complex or set a lot of options. The default location for the configuration file is **/etc/pgbackrest/pgbackrest.conf**. If no file exists in that location then the old default of **/etc/pgbackrest.conf** will be checked.

## Archive Options

The archive section defines options for the **archive-push** and **archive-get** commands.

### Asynchronous Archiving Option (--archive-async)

Push/get WAL segments asynchronously.

Enables asynchronous operation for the archive-push and archive-get commands.

Asynchronous operation is more efficient because it can reuse connections and take advantage of parallelism. See the **spool-path, archive-get-queue-max, and archive-push-queue-max** options for more information.

### Maximum Archive Get Queue Size Option (--archive-get-queue-max)

Maximum size of the pgBackRest archive-get queue.

Specifies the maximum size of the archive-get queue when **archive-async** is enabled. The queue is stored in the **spool-path** and is used to speed providing WAL to PostgreSQL.

### Retry Missing WAL Segment Option (--archive-missing-retry)

Retry missing WAL segment

Retry a WAL segment that was previously reported as missing by the archive-get command when in asynchronous mode. This prevents notifications in the spool path from a prior restore from being used and possibly causing a recovery failure if consistency has not been reached.

Disabling this option allows PostgreSQL to more reliably recognize when the end of the WAL in the archive has been reached, which permits it to switch over to streaming from the primary. With retries enabled, a steady stream of WAL being archived will cause PostgreSQL to continue getting WAL from the archive rather than switch to streaming.

When disabling this option it is important to ensure that the spool path for the stanza is empty. The restore command does this automatically if the spool path is configured at restore time. Otherwise, it is up to the user to ensure the spool path is empty.

### Maximum Archive Push Queue Size Option (--archive-push-queue-max)

Maximum size of the PostgreSQL archive queue.

After the limit is reached, the following will happen:

- pgBackRest will notify PostgreSQL that the WAL was successfully archived, then DROP IT.
- A warning will be output to the PostgreSQL log.

If this occurs then the archive log stream will be interrupted and PITR will not be possible past that point. A new backup will be required to regain full restore capability.

In asynchronous mode the entire queue will be dropped to prevent spurts of WAL getting through before the queue limit is exceeded again.

The purpose of this feature is to prevent the log volume from filling up at which point PostgreSQL will stop completely. Better to lose the backup than have PostgreSQL go down.

Deprecated Name: archive-queue-max

### Archive Timeout Option (--archive-timeout)

Archive timeout.

Set maximum time, in seconds, to wait for each WAL segment to reach the pgBackRest archive repository. The timeout applies to the check and backup commands when waiting for WAL segments required for backup consistency to be archived.

## References

1. [pgBackRest configuration](https://pgbackrest.org/configuration.html)
2. [pgBackRest user-guide](https://pgbackrest.org/user-guide.html)
