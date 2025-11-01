# Handling Data Skew in CRUD Operations

## Understanding Data Skew
Data skew occurs when data is unevenly distributed across partitions or shards, leading to:
- Hotspots in read/write operations
- Uneven load distribution
- Performance bottlenecks
- Resource utilization issues

## Common Causes
1. **Natural skew**: Some data values naturally occur more frequently
2. **Temporal skew**: Recent data accessed more frequently
3. **Geographic skew**: Data clusters by region/location
4. **Design-induced skew**: Poor partitioning strategies

## Solutions for Different CRUD Operations

### 1. CREATE Operations

#### Partition Key Design
```sql
-- Bad: Using timestamp as partition key
CREATE TABLE events (
    timestamp TIMESTAMP PRIMARY KEY,
    event_data JSONB
);

-- Better: Composite key with distribution element
CREATE TABLE events (
    bucket_id INT,
    timestamp TIMESTAMP,
    event_data JSONB,
    PRIMARY KEY (bucket_id, timestamp)
);
```

#### Write Distribution
```python
def calculate_bucket(key):
    return hash(key) % NUM_BUCKETS

def insert_data(data):
    bucket_id = calculate_bucket(data['id'])
    data['bucket_id'] = bucket_id
    db.execute("INSERT INTO events (bucket_id, timestamp, event_data) VALUES (:bucket_id, :timestamp, :data)",
               data)
```

### 2. READ Operations

#### Caching Strategy
```python
def get_cached_data(key):
    cache_key = f"data:{calculate_bucket(key)}:{key}"
    data = cache.get(cache_key)
    if not data:
        data = db.fetch_data(key)
        cache.set(cache_key, data, expire=3600)
    return data
```

#### Query Optimization
```sql
-- Add indexes for common access patterns
CREATE INDEX idx_events_bucket_timestamp ON events (bucket_id, timestamp);

-- Use materialized views for hot data
CREATE MATERIALIZED VIEW recent_events AS
SELECT * FROM events 
WHERE timestamp >= NOW() - INTERVAL '24 hours'
WITH DATA;
```

### 3. UPDATE Operations

#### Batch Processing
```python
def batch_update(records):
    buckets = defaultdict(list)
    for record in records:
        bucket_id = calculate_bucket(record['id'])
        buckets[bucket_id].append(record)
    
    for bucket_id, bucket_records in buckets.items():
        db.execute_batch("""
            UPDATE events 
            SET event_data = :data 
            WHERE bucket_id = :bucket_id AND id = :id
            """, bucket_records)
```

### 4. DELETE Operations

#### Soft Delete Strategy
```sql
-- Add soft delete column
ALTER TABLE events ADD COLUMN deleted_at TIMESTAMP;

-- Update instead of delete
UPDATE events 
SET deleted_at = CURRENT_TIMESTAMP 
WHERE id = :id;

-- Background cleanup process
DELETE FROM events 
WHERE deleted_at < NOW() - INTERVAL '30 days' 
AND bucket_id = :current_bucket_id
LIMIT 1000;
```

## Monitoring and Detection

### Query Analytics
```sql
-- Find hot partitions
SELECT bucket_id, COUNT(*) as access_count
FROM query_log
GROUP BY bucket_id
HAVING COUNT(*) > (SELECT AVG(count) * 2 
                   FROM (SELECT COUNT(*) as count 
                         FROM query_log 
                         GROUP BY bucket_id));
```

### Implementation Example

```python
class DataSkewHandler:
    def __init__(self, num_buckets=1024):
        self.num_buckets = num_buckets
        self.cache = Cache()
        
    def write_data(self, key, data):
        bucket = self._get_bucket(key)
        return self._distributed_write(bucket, key, data)
        
    def read_data(self, key):
        bucket = self._get_bucket(key)
        cached_data = self.cache.get(f"{bucket}:{key}")
        if cached_data:
            return cached_data
        return self._distributed_read(bucket, key)
        
    def _get_bucket(self, key):
        return hash(key) % self.num_buckets
```

## Best Practices

1. **Design Phase**
   - Choose appropriate partition keys
   - Plan for data growth
   - Consider access patterns

2. **Implementation**
   - Use consistent hashing
   - Implement caching strategies
   - Batch operations when possible

3. **Monitoring**
   - Track partition sizes
   - Monitor access patterns
   - Set up alerts for hotspots

4. **Maintenance**
   - Regularly rebalance data
   - Archive old data
   - Optimize hot partitions

## Tools and Technologies

1. **Databases with Built-in Support**
   - Apache Cassandra
   - Amazon DynamoDB
   - MongoDB

2. **Monitoring Tools**
   - Prometheus
   - Grafana
   - Custom metrics collectors

Remember: The key to handling data skew is proactive design and continuous monitoring.