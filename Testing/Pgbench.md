# Benchmarking Postgres clusters

Benchmarking is the equivalent term for testing when it comes to database instances/clusters.

## Pgbench

a

### What is the “Transaction” Actually Performed in pgbench?

pgbench executes test scripts chosen randomly from a specified list. The scripts may include built-in scripts specified with -b and user-provided scripts specified with -f. Each script may be given a relative weight specified after an @ so as to change its selection probability. The default weight is 1. Scripts with a weight of 0 are ignored.

The default built-in transaction script (also invoked with -b tpcb-like) issues seven commands per transaction over randomly chosen aid, tid, bid and delta. The scenario is inspired by the TPC-B benchmark, but is not actually TPC-B, hence the name.

```SQL
BEGIN;

UPDATE pgbench_accounts SET abalance = abalance + :delta WHERE aid = :aid;

SELECT abalance FROM pgbench_accounts WHERE aid = :aid;

UPDATE pgbench_tellers SET tbalance = tbalance + :delta WHERE tid = :tid;

UPDATE pgbench_branches SET bbalance = bbalance + :delta WHERE bid = :bid;

INSERT INTO pgbench_history (tid, bid, aid, delta, mtime) VALUES (:tid, :bid, :aid, :delta, CURRENT_TIMESTAMP);

END;
```

If you select the simple-update built-in (also -N), steps 4 and 5 aren't included in the transaction. This will avoid update contention on these tables, but it makes the test case even less like TPC-B.

If you select the select-only built-in (also -S), only the SELECT is issued.
