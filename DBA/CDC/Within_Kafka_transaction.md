# Kafka Transaction & Atomically Committed

## Deep Dive: What "Within a Single Kafka Transaction" Fundamentally Means

**A Kafka transaction is a container for grouped operations that succeed or fail together.** Think of it like a database ACID transaction, but for Kafka.

### Traditional Kafka (No Transactions)

Without transactions, publishing is **fire-and-forget per message**:

```
Debezium: Send change#1 → Kafka ✅ (committed immediately)
Debezium: Send change#2 → Kafka ✅ (committed immediately)
Debezium: Send change#3 → Kafka ✅ (committed immediately)
Debezium: Advance offset → Kafka ✅ (committed immediately)
Debezium: CRASH! 💥
```

Problem: Consumer might see change#1, change#2, change#3, but then if Debezium restarts, it might re-send them because the offset wasn't safely committed before the crash. Result: **Duplicates.**

### Kafka With Transactions (Exactly-Once)

All messages are grouped into **one atomic unit**:

```
BEGIN TRANSACTION
  Debezium: Send change#1 → [buffered, not visible]
  Debezium: Send change#2 → [buffered, not visible]
  Debezium: Send change#3 → [buffered, not visible]
  Debezium: Commit offset → [buffered, not visible]
COMMIT TRANSACTION
```

**Key difference**: Nothing is visible to consumers until the ENTIRE transaction commits successfully.

```
Timeline:
T1: All 3 changes + offset buffered by Kafka broker (TX in progress)
T2: CRASH before COMMIT
   → Kafka rolls back entire TX
   → All changes discarded
   → Offset NOT advanced
   → Consumers see nothing
T3: Debezium restarts
   → Reads from previous offset (unchanged)
   → Re-sends exact same changes in new transaction
T4: New transaction commits successfully
   → Consumers now see all 3 changes
   → Because offset is included in TX, it advances safely
   → Exactly-once: ✅
```

**Fundamental guarantee**: COMMIT all 4 things (change#1, change#2, change#3, offset) or COMMIT none of them. No in-between states.

### Producer-Side Idempotence

To further strengthen this, Kafka producers in transaction mode use **producer ID + sequence numbers**:

```json
{
  "producer_id": "debezium-connector-01",
  "sequence": 1000,
  "value": {"id": 1, "name": "Alice"}
}
```

If Debezium retransmits the same message with the same producer_id + sequence, Kafka automatically **deduplicates** it by recognizing it as a retry, not a new message.

---

## Deep Dive: What "Offset Committed Atomically" Fundamentally Means

**The offset is the "bookmark" that tells Debezium where it left off reading the source database.** It's the answer to: "Which changes have I already sent to Kafka?"

### Source Offset Structure

For PostgreSQL, the offset looks like:

```json
{
  "server_id": "postgres-prod",
  "file": "000000010000000000000100",  // WAL file
  "pos": 8675309,                      // Position in WAL file
  "txId": 12345,                       // Transaction ID
  "ts_ms": 1671234567890
}
```

This offset is stored **in Kafka itself** (in the internal topic `__consumer_offsets`).

### The Atomic Commitment Problem (Without Transactions)

Imagine Debezium processes a batch without transactions:

```
Step 1: Read 100 rows from PostgreSQL WAL
Step 2: Send 100 change events to Kafka ✅
Step 3: Commit offset to Kafka ("I've processed up to txId=12345") ✅
Step 4: CRASH before Step 4 completes 💥
```

Result: Offset is committed → Next restart reads from txId=12346 → Changes from txId=12345 are lost. ❌

### With Atomic Offset Commitment

Now with transactions, ALL things commit together:

```
BEGIN TRANSACTION
  Step 1: Buffer 100 change events
  Step 2: Buffer offset update ("processed up to txId=12345")
  Step 3: Neither visible to consumers yet
COMMIT TRANSACTION
```

The **atomicity guarantee** means:

- ✅ Either both succeed: All 100 changes + offset visible to consumers
- ❌ Or both fail: Changes and offset both discarded, nothing visible
- 🚫 **Never**: Changes visible but offset not committed (or vice versa)

This is **atomic** in the sense of ACID: **All-or-nothing semantics.**

```
Timeline showing atomic commitment:

Before TX Commit:
  Kafka Broker State:
    [Changes]: [BUFFERED - not yet visible to consumers]
    [Offset]:  [BUFFERED - still points to old value]
  
  Debezium State:
    If crashes here → TX rolls back, no harm done
    Restart → reads from old offset again

After TX Commit:
  Kafka Broker State:
    [Changes]: [COMMITTED - visible to consumers reading TX]
    [Offset]:  [COMMITTED - points to new txId=12345]
  
  Consumer View:
    Can read all 100 changes
    Next Debezium restart knows to start from txId=12346
```

### Why Atomicity Matters

Without atomicity, you have windows of inconsistency:

```
Scenario A: Offset committed, changes not yet visible
  → Consumer restarts and reads from new offset
  → Misses those 100 changes forever ❌ (Data loss)

Scenario B: Changes visible, offset not committed
  → Consumer sees changes
  → Debezium restarts and re-sends same changes
  → Consumer sees duplicates ❌ (Duplicate data)
```

**Atomic commitment prevents both scenarios** by making them impossible.

---

## The Interplay: Why Both Concepts Work Together

The magic of exactly-once comes from combining these two concepts:

```
┌─────────────────────────────────────────────────────────────┐
│                    KAFKA TRANSACTION                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  CHANGES (100 events)                               │   │
│  │  - Row 1 inserted: {id: 1, name: "Alice"}          │   │
│  │  - Row 2 inserted: {id: 2, name: "Bob"}            │   │
│  │  - ...                                              │   │
│  │  - Row 100 inserted: {id: 100, name: "Zoe"}        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  OFFSET (Atomic Commitment)                         │   │
│  │  "I have processed up to WAL pos: 8675309"         │   │
│  │  "Next read starts from: 8675310"                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  GUARANTEE: Commit all or nothing                           │
│  No partial states, no inconsistencies                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**What makes it work:**

1. **Single Transaction Container**: All 101 things (100 changes + 1 offset) grouped together
2. **All-or-Nothing Commit**: Either all 101 things reach consumers, or none
3. **Offset Inclusion**: The offset commit is INSIDE the transaction, not outside
4. **Consumer Isolation**: Consumers reading in Read Committed mode see only successfully committed transactions

**Example failure scenario:**

```
Debezium preparing to commit transaction with 100 changes + offset
                ↓
Broker receives: "BEGIN TX, ADD 100 changes, UPDATE offset, COMMIT"
                ↓
Debezium crashes after sending 50 changes (T/X incomplete)
                ↓
Kafka automatically ROLLBACK (due to incomplete TX)
                ↓
Consumers see NOTHING (no changes, offset unchanged)
                ↓
Debezium restarts
                ↓
Reads from old offset
                ↓
Re-sends exact same 100 changes in new transaction
                ↓
Transaction succeeds this time
                ↓
Consumers see all 100 changes exactly once ✅
```

---

## Technical Implementation Details

### Producer Transactional State Machine

```
IDLE
  ↓ (beginTransaction())
INITIALIZING
  ↓ (successfully initialized)
IN_TRANSACTION
  ├─→ (send message) → IN_TRANSACTION
  ├─→ (send message) → IN_TRANSACTION
  └─→ (sendOffsetsToTransaction) → IN_TRANSACTION
       ↓ (commitTransaction())
COMMITTING
       ↓ (broker confirms)
IDLE
```

### Broker-Side Transaction Coordinator

Kafka brokers maintain a **transaction coordinator** that:

1. **Tracks transaction state** for each producer_id
2. **Buffers messages** until commit received
3. **Maintains transaction log** (for recovery)
4. **Handles rollback** if commit not received within timeout
5. **Manages offset commits** atomically with message commits

### Consumer-Side Transaction Visibility

Consumers use **isolation.level** setting:

- `read_uncommitted`: See all messages, even uncommitted ones (risky)
- `read_committed`: See only messages from committed transactions (safe)

Debezium sinks should use `read_committed` to ensure they never see partial transaction states.

```properties
# Consumer configuration for sink
isolation.level=read_committed
```
