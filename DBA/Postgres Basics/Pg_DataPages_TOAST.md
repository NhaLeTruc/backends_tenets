# Postgres data pages and TOAST

## Data Page

PostgreSQL organizes and stores data in units called "pages," which are fixed-length blocks of data. The default page size is 8KB (8,192 bytes), though this can be configured during server compilation.

### Structure of a PostgreSQL Page

Each page typically consists of the following components:

- **PageHeader**: Located at the beginning of the page, this 24-byte header contains metadata about the page itself. This includes information like the most recent WAL entry related to the page, page checksum (if enabled), flag bits, and offsets to the start and end of free space and special space within the page. It also stores the page size and a version indicator.
- **ItemIdData (Line Pointers)**: This is an array of (offset, length) pairs, acting as pointers to the actual data items (rows) stored on the page. These are allocated from the start of the free space.
- **Items (Tuples/Rows)**: These are the actual data records (rows or tuples) of a table or index. They are stored in reverse order from the end of the free space. Each item is referenced by an ItemIdData pointer.
- **Free Space**: This is the unallocated space on the page, available for storing new rows or updates to existing rows. New data is typically allocated from the end of this space.
- **Special Space**: This is a reserved area at the end of the page where PostgreSQL can store information that doesn't fit within the page header, often used by index access methods for specific index-related metadata.

### Key Characteristics

- **Fixed Size**: Pages have a fixed size, typically 8KB, which is the unit of disk I/O for PostgreSQL.
- **No Spanning Tuples**: A single tuple (row) cannot span multiple pages. If a tuple's combined field size exceeds the page's capacity (around 2KB before TOASTing), PostgreSQL employs TOAST (The Oversized-Attribute Storage Technique) to store large field values externally.
- **Efficient Data Access**: The page structure, with its header and item pointers, allows for efficient location and retrieval of individual rows within a page.
- **Buffer Cache**: PostgreSQL utilizes a buffer cache in memory, organized as a collection of 8KB pages, to store frequently accessed data pages and reduce disk I/O.

---
---

## TOAST

PostgreSQL TOAST <mark>(The Oversized-Attribute Storage Technique)</mark> is a built-in system for efficiently handling large data values like TEXT, BYTEA, and JSON. When a row's data exceeds a certain size, PostgreSQL automatically compresses it and, if necessary, splits it into smaller chunks, which are stored in a separate TOAST table. A pointer in the original table then links to the data in the TOAST table, ensuring the main table can still fit within its standard page size.

### How TOAST works

- **Compression**: PostgreSQL first attempts to compress the large value to see if it can fit into the standard 2KB buffer.
- **Out-of-line storage**: If compression isn't enough, the data is split into smaller chunks and stored in a separate table, typically named pg_toast_$(OID).
- **Pointer**: A pointer is placed in the original table's row to reference the location of the data in the TOAST table.

### Key Characteristics

- **Automatic**: This process happens automatically and is transparent to the user for the most part.
- **Large data types**: It is designed for large data types like TEXT, BYTEA, and JSON.
- **Performance impact**: Retrieving TOASTed data can add overhead, as it requires an extra step to retrieve the data from the TOAST table.

### Management and alternatives

- **attstorage**: The <mark>attstorage</mark> attribute of a column can be used to control how TOAST works (e.g., PLAIN to prevent TOASTing).
- **Compression policies**: TOAST doesn't offer user-friendly policies for compression.
- **Modern alternatives**: Extensions like TimescaleDB offer more advanced compression methods, such as columnar compression, which can significantly reduce storage size and improve query performance.
