# Database Testing

Database testing includes performing:

+ data validity
+ data integrity testing
+ performance check related to database and testing of procedures, triggers and functions in the database.

Database testing involves checking stored procedures, views, schemas in database, tables, indexes, keys, triggers, data validations and data consistence check.

Based on the function and structure of a database, DB testing can be categorized into three
categories:

+ Structural Database Testing – It deals with table and column testing, schema testing, stored procedures and views testing, checking triggers, etc.
+ Functional Testing – It involves checking functionality of database from user point of view. Most common type of Functional testing are White box and black box testing.
+ Nonfunctional Testing – It involves load-testing, risk testing in database, stress testing, minimum system requirements, and deals with the performance of the database.

---

## Structural Database Testing

Structural database testing involves verifying those components of database, which are not exposed to end users. It involves all the components of repository, which are used to store the data and are not changed by the end users. Database administrators with good command over SQL stored procedures and other concepts normally perform this testing.

### Schema / Mapping Testing

It involves validating the objects of front-end application with database object mapping.

In Schema Testing:

+ Sometimes it happens that the end user application objects are not correctly mapped or compatible with database objects. Therefore, checking the validation of the various schema formats associated with the databases is required.
+ It is required to find the unmapped objects in database, like tables, views, columns etc. is required.

There are various tools in the market that can be used to perform object mapping in schemas.

Example: In Microsoft SQL Server, a tester can write simple queries to check and validate schemas in the database.

If the tester wants to make changes to a table structure, he/she should ensure that all the stored procedures having that table are compatible with this change.

### Stored Procedures and Views Testing

In this testing, a tester ensures that the manual execution of stored procedures and views generate the required result.

The most common tools that are used to perform stored procedures testing are LINQ, SP Test tool, etc.

### Trigger Testing

+ Whether the coding conventions are followed during the coding phase of the triggers.
+ See the triggers executed meets the required conditions.
+ Whether the trigger updates the data correctly, once they have been executed.
+ Validation of Update/Insert/Delete triggers functionality w.r.t application under test.

### Tables and Column testing

+ Validating the data types in the database to field values in front-end application.
+ Validating the length of data field in database to length of data types in the application.
+ Checking if there are any unmapped tables or columns in the database from application field objects.
+ Naming conventions of database tables and columns are verified, if they are in accordance with business requirement or not.
+ Validating the Keys and Indexes in the database, i.e., primary and foreign keys in tables are defined as per requirement.
+ Check if the primary keys and their corresponding foreign keys are same in two tables.
+ Check Unique and NOT NULL characteristics of keys are maintained.
+ Length and data type of keys and indexes are maintained as per requirement.

### Database Server Check

+ If the database server can handle the expected number of transactions as per the business requirement.
+ If the configuration details of database servers meets the business requirement.
+ If the user authorization is maintained as per requirement.

---

## Functional Testing (Doing the right things)

Functional testing is performed keeping in mind an end-user point of view; whether the required transactions and operations run by the end-users meet the business specifications.

### Black Box Testing

Black Box Testing involves verifying the integration of database to check the functionality. The test cases are simple and are used to verify incoming data and outgoing data from the function.

Its advantages are as follows:

+ It is fairly simple and is performed in the early stages of development.
+ Cost of developing test-cases is less as compared to white-box testing.

Its disadvantages are as follows:

+ A few errors cannot be detected.
+ It is unknown how much program needs to be tested.

### White Box Testing

White Box Testing deals with the internal structure of the database and the specification details are hidden from the users. It involves the testing of database triggers and logical views, which are going to support database refactoring.

It performs module testing of database functions, triggers, views, SQL queries etc. This type of testing validates database tables, data models, database schema etc. It checks rules of Referential integrity. It selects default table values to check on database consistency.

The most common techniques used to perform white box testing are condition coverage, decision coverage, statement coverage, etc.

Coding errors can be detected in white-box testing, so internal bugs in the database can be eliminated. The limitation of white-box testing is that SQL statements are not covered.

---

## Nonfunctional Testing (Doing things right)

Nonfunctional testing involves performing load testing, stress testing, checking minimum system requirements to meet business specification, risk finding and performance optimization of database.

### Performance Testing vs Load Testing

Performance testing is a broad category that evaluates how a system performs under various conditions, including its speed, scalability, and stability. Load testing, on the other hand, is a specific type of performance testing that focuses on simulating real-world user loads to assess how the system handles expected or peak load. Thus load testing is a subset of Performance testing, which is a techinical term for testing suites. Unlike functional and non-functional which defined by user's requirements thus is more of a business term.

### Load Testing

The primary target of load testing is to check if most running transactions have performance impact on the database.

+ The response time for executing the transactions for multiple remote users.
+ Time taken by the database to fetch specific records.

Examples of load testing in different testing types:

+ Running most used transaction repeatedly to see performance of database system.
+ Downloading a series of large files from the internet.
+ Running multiple applications on a computer or server simultaneously.

### Stress Testing

Stress testing is performed to identify the system breakpoint. In this testing, application is loaded in such a way that the system fails at one point. This point is called the breakpoint of database system.

Determining the state of database transactions involves a significant amount of effort. Proper planning is required to avoid any time and cost-based issues.
