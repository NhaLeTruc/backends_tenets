# Postgres 9.6 Adminstration Guide

Nitty gritty of postgress admin. Provides best practice recipes for database administration.

## Chapter 1: First Steps

In this chapter, we will cover the following recipes:

- Getting PostgreSQL
- Connecting to the PostgreSQL server
- Enabling access for network/remote users
- Using graphical administration tools
- Using the psql query and scripting tool
- Changing your password securely
- Avoiding hardcoding your password
- Using a connection service file
- Troubleshooting a failed connection

## Chapter 2: Exploring the Database

In this chapter, we will cover the following recipes:

- What version is the server?
- What is the server uptime?
- Locating the database server files
- Locating the database server's message log
- Locating the database's system identifier
- Listing databases on this database server
- How many tables are there in a database?
- How much disk space does a database use?
- How much disk space does a table use?
- Which are my biggest tables?
- How many rows are there in a table?
- Quickly estimating the number of rows in a table
- Listing extensions in this database
- Understanding object dependencies

## Chapter 3: Configuration

In this chapter, we will cover the following recipes:

- Reading the fine manual
- Planning a new database
- Changing parameters in your programs
- Finding the current configuration settings
- Which parameters are at non-default settings?
- Updating the parameter file
- Setting parameters for particular groups of users
- The basic server configuration checklist
- Adding an external module to PostgreSQL
- Using an installed module
- Managing installed extensions

## Chapter 4: Server Control

In this chapter, we will cover the following recipes:

- Starting the database server manually
- Stopping the server safely and quickly
- Stopping the server in an emergency
- Reloading the server configuration files
- Restarting the server quickly
- Preventing new connections
- Restricting users to only one session each
- Pushing users off the system
- Deciding on a design for multitenancy
- Using multiple schemas
- Giving users their own private database
- Running multiple servers on one system
- Setting up a connection pool
- Accessing multiple servers using the same host and port

## Chapter 5: Tables and Data

In this chapter, we will cover the following recipes:

- Choosing good names for database objects
- Handling objects with quoted names
- Enforcing the same name and definition for columns
- Identifying and removing duplicates
- Preventing duplicate rows
- Finding a unique key for a set of data
- Generating test data
- Randomly sampling data
- Loading data from a spreadsheet
- Loading data from flat files

## Chapter 6: Security

In this chapter, we will cover the following recipes:

- The PostgreSQL superuser
- Revoking user access to a table
- Granting user access to a table
- Granting user access to specific columns
- Granting user access to specific rows
- Creating a new user
- Temporarily preventing a user from connecting
- Removing a user without dropping their data
- Checking whether all users have a secure password
- Giving limited superuser powers to specific users
- Auditing DDL changes
- Auditing data changes
- Always knowing which user is logged in
- Integrating with LDAP
- Connecting using SSL
- Using SSL certificates to authenticate
- Mapping external usernames to database roles
- Encrypting sensitive data

## Chapter 7: Database Administration

In this chapter, we will cover the following recipes:

- Writing a script that either succeeds entirely or fails entirely
- Writing a psql script that exits on the first error
- Investigating a psql error
- Performing actions on many tables
- Adding/removing columns on a table
- Changing the data type of a column
- Changing the definition of a data type
- Adding/removing schemas
- Moving objects between schemas
- Adding/removing tablespaces
- Moving objects between tablespaces
- Accessing objects in other PostgreSQL databases
- Accessing objects in other foreign databases
- Updatable views
- Using materialized views

## Chapter 8: Monitoring and Diagnosis

In this chapter, we will cover the following recipes:

- Checking whether a user is connected
- Checking which queries are running
- Checking which queries are active or blocked
- Knowing who is blocking a query
- Killing a specific session
- Detecting an in-doubt prepared transaction
- Knowing whether anybody is using a specific table
- Knowing when a table was last used
- Usage of disk space by temporary data
- Understanding why queries slow down
- Investigating and reporting a bug
- Producing a daily summary of log file errors
- Analyzing the real-time performance of your queries

## Chapter 9: Regular Maintenance

In this chapter, we will cover the following recipes:

- Controlling automatic database maintenance
- Avoiding auto-freezing and page corruptions
- Removing issues that cause bloat
- Removing old prepared transactions
- Actions for heavy users of temporary tables
- Identifying and fixing bloated tables and indexes
- Monitoring and tuning vacuum
- Maintaining indexes
- Adding a constraint without checking existing rows
- Finding unused indexes
- Carefully removing unwanted indexes
- Planning maintenance

## Chapter 10: Performance and Concurrency

In this chapter, we will cover the following recipes:

- Finding slow SQL statements
- Collecting regular statistics from pg_stat* views
- Finding out what makes SQL slow
- Reducing the number of rows returned
- Simplifying complex SQL queries
- Speeding up queries without rewriting them
- Discovering why a query is not using an index
- Forcing a query to use an index
- Using parallel query
- Using optimistic locking
- Reporting performance problems

## Chapter 11: Backup and Recovery

In this chapter, we will cover the following recipes:

- Understanding and controlling crash recovery
- Planning backups
- Hot logical backup of one database
- Hot logical backup of all databases
- Backup of database object definitions
- Standalone hot physical database backup
- Hot physical backup and continuous archiving
- Recovery of all databases
- Recovery to a point in time
- Recovery of a dropped/damaged table
- Recovery of a dropped/damaged database
- Improving performance of backup/recovery
- Incremental/differential backup and restore
- Hot physical backups with Barman
- Recovery with Barman

## Chapter 12: Replication and Upgrades

In this chapter, we will cover the following recipes:

- Replication best practices
- Setting up file-based replication - deprecated
- Setting up streaming replication
- Setting up streaming replication security
- Hot Standby and read scalability
- Managing streaming replication
- Using repmgr
- Using replication slots
- Monitoring replication
- Performance and synchronous replication
- Delaying, pausing, and synchronizing replication
- Logical replication
- Bi-directional replication
- Archiving transaction log data
- Upgrading - minor releases
- Major upgrades in-place
- Major upgrades online
