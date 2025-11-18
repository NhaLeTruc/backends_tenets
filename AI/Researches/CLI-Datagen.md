# Datagen CLI tool

There isn't a single dedicated CLI tool specifically for creating mock PostgreSQL archive files directly, but you can achieve this through a combination of approaches:

## Option 1: Generate Mock Data + pg_dump

The most common approach is to:
1. Create mock data in a real PostgreSQL database
2. Export it using `pg_dump`

**Tools for generating mock data:**

- **pgbench** - Built into PostgreSQL, creates sample TPC-B-like benchmark data:
  ```bash
  pgbench -i -s 10 mydb  # Initialize with scale factor 10
  pg_dump mydb > mock_archive.sql
  ```

- **faker + psql** - Use Python's Faker library with a script:
  ```bash
  python generate_mock_data.py | psql mydb
  pg_dump mydb > mock_archive.sql
  ```

- **dblab** - Can create thin clones of databases with synthetic data

## Option 2: Mock Data Generation Tools

**Mockaroo CLI** - Can generate SQL directly:
```bash
mockaroo schema.json --format sql --rows 1000 > mock_data.sql
```

**Synth** - A declarative data generator that supports PostgreSQL:
```bash
synth generate my_schema --size 1000 --to postgres://...
```

## Option 3: Custom Solution

You could create a simple script that generates a PostgreSQL archive format directly:

```bash
#!/bin/bash
cat <<EOF > mock_archive.sql
--
-- PostgreSQL database dump
--
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

COPY users (id, name, email) FROM stdin;
1	John Doe	john@example.com
2	Jane Smith	jane@example.com
\.
EOF
```

## Option 4: Docker-based Approach

Use a containerized PostgreSQL with mock data:
```bash
docker run -d --name mock-pg postgres
# Load mock data
docker exec mock-pg pg_dump > mock_archive.sql
```

The best approach depends on your specific needs - whether you need realistic relational data, specific table structures, or just simple test archives. For complex schemas with relationships, using a real PostgreSQL instance with a data generation tool like pgbench or Faker tends to work best.