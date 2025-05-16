# WAL_G Introduction

WAL-G is an archival restoration tool for PostgreSQL, MySQL/MariaDB, and MS SQL Server.

WAL-G is the successor of WAL-E with a number of key differences. WAL-G uses LZ4, LZMA, ZSTD, or Brotli compression, multiple processors, and non-exclusive base backups for Postgres.

## Configuration

There are two ways how you can configure WAL-G:

1. Using environment variables
2. Using a config file

**--config /path** flag can be used to specify the path where the config file is located.

Every configuration variable mentioned in the following documentation can be specified either as an environment variable or a field in the config file.

## Compression

config variable: **WALG_COMPRESSION_METHOD**

To configure the compression method used for backups. Possible options are: **lz4, lzma, zstd, brotli**. The default method is **lz4**. LZ4 is the fastest method, but the compression ratio is bad. LZMA is way much slower. However, it compresses backups about 6 times better than LZ4. Brotli and zstd are a good trade-off between speed and compression ratio, which is about 3 times better than LZ4.

## Encryption

config variable: **YC_CSE_KMS_KEY_ID**
To configure Yandex Cloud KMS key for client-side encryption and decryption. By default, no encryption is used.

config variable: **YC_SERVICE_ACCOUNT_KEY_FILE**
To configure the name of a file containing private key of Yandex Cloud Service Account. If not set a token from the metadata service (http://169.254.169.254) will be used to make API calls to Yandex Cloud KMS.

config variable: **WALG_LIBSODIUM_KEY**
To configure encryption and decryption with libsodium. WAL-G uses an algorithm that only requires a secret key. libsodium keys are fixed-size keys of 32 bytes. For optimal cryptographic security, it is recommened to use a random 32 byte key. To generate a random key, you can something like openssl rand -hex 32 (set WALG_LIBSODIUM_KEY_TRANSFORM to hex) or openssl rand -base64 32 (set WALG_LIBSODIUM_KEY_TRANSFORM to base64).

config variable: **WALG_LIBSODIUM_KEY_PATH**
Similar to WALG_LIBSODIUM_KEY, but value is the path to the key on file system. The file content will be trimmed from whitespace characters.

config variable: **WALG_LIBSODIUM_KEY_TRANSFORM**
The transform that will be applied to the WALG_LIBSODIUM_KEY to get the required 32 byte key. Supported transformations are base64, hex or none (default). The option none exists for backwards compatbility, the user input will be converted to 32 byte either via truncation or by zero-padding.

config variable: **WALG_GPG_KEY_ID (alternative form WALE_GPG_KEY_ID) ⚠️ DEPRECATED**
To configure GPG key for encryption and decryption. By default, no encryption is used. Public keyring is cached in the file "/.walg_key_cache".

config variable: **WALG_PGP_KEY**
To configure encryption and decryption with OpenPGP standard. You can join multiline key using \n symbols into one line (mostly used in case of daemontools and envdir). Set private key value when you need to execute wal-fetch or backup-fetch command. Set public key value when you need to execute wal-push or backup-push command. Keep in mind that the private key also contains the public key.

config variable: **WALG_PGP_KEY_PATH**
Similar to WALG_PGP_KEY, but value is the path to the key on file system.

config variable: **WALG_PGP_KEY_PASSPHRASE**
If your private key is encrypted with a passphrase, you should set passphrase for decrypt.

config variable: **WALG_ENVELOPE_PGP_KEY**
To configure encryption and decryption with the envelope PGP key stored in key management system. This option allows you to securely manage your PGP keys by storing them in the KMS. It is crucial to ensure that the key passed is encrypted using kms and encoded with base64. Also both private and publlic parts should be presents in key because envelope key will be injected in metadata and used later in wal/backup-fetch.
Please note that currently, only Yandex Cloud Key Management Service (KMS) is supported for configuring. Ensure that you have set up and configured Yandex Cloud KMS mentioned below before attempting to use this feature.

config variable: **WALG_ENVELOPE_CACHE_EXPIRATION**
This setting controls kms response expiration. Default value is 0 to store keys permanent in memory. Please note that if the system will not be able to redecrypt the key in kms after expiration, the previous response will be used.

config variable: **WALG_ENVELOPE_PGP_YC_ENDPOINT**
Endpoint is an API endpoint of Yandex.Cloud against which the SDK is used. Most users won't need to explicitly set it.

config variable: **WALG_ENVELOPE_PGP_YC_CSE_KMS_KEY_ID**
Similar to YC_CSE_KMS_KEY_ID, but only used for envelope pgp keys.

config variable: **WALG_ENVELOPE_PGP_YC_SERVICE_ACCOUNT_KEY_FILE**
Similar to YC_SERVICE_ACCOUNT_KEY_FILE, but only used for envelope pgp keys.

config variable: **WALG_ENVELOPE_PGP_KEY_PATH**
Similar to WALG_ENVELOPE_PGP_KEY, but value is the path to the key on file system.

## Monitoring

config variable: **WALG_STATSD_ADDRESS**
To enable metrics publishing to statsd or statsd_exporter. Metrics will be sent on a best-effort basis via UDP. The default port for statsd is 8125.

config variable: **WALG_STATSD_EXTRA_TAGS**
Use this setting to add static tags (host, operation, database, etc) to the metrics WAL-G publishes to statsd.

If you want to make demo for testing purposes, you can use graphite service from docker-compose file.

## Profiling

Profiling is useful for identifying bottlenecks within WAL-G.

config variable: **PROFILE_SAMPLING_RATIO**
A float value between 0 and 1, defines likelihood of the profiler getting enabled. When set to 1, it will always run. This allows probabilistic sampling of invocations. Since WAL-G processes may get created several times per second (e.g. wal-g wal-push), we do not want to profile all of them.

config variable: **PROFILE_MODE**
The type of pprof profiler to use. Can be one of cpu, mem, mutex, block, threadcreation, trace, goroutine. See the runtime/pprof docs for more information. Defaults to cpu.

config variable: **PROFILE_PATH**
The directory to store profiles in. Defaults to $TMPDIR.

## Rate limiting

config variable: **WALG_NETWORK_RATE_LIMIT**
Network traffic rate limit during the backup-push/backup-fetch operations in bytes per second.

## Reference

[readthedocs](https://wal-g.readthedocs.io/)
