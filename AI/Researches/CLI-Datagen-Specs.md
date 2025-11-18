# Mock PostgreSQL Archive Generator CLI Tool

## What It Does

A command-line tool that transforms declarative JSON schema definitions into fully-formed PostgreSQL dump files containing realistic mock data, without requiring a running PostgreSQL instance.

### Core Functionality

**Schema Definition via JSON**
- Define tables, columns, data types, and constraints in readable JSON format
- Specify relationships between tables (foreign keys, joins)
- Set custom naming conventions and database-specific settings
- Support for all PostgreSQL data types including arrays, JSON, and custom types

**Intelligent Data Generation**
- Generate contextually appropriate fake data based on column names (e.g., "email" field gets valid emails, "phone" gets formatted phone numbers)
- Respect referential integrity and relationships automatically
- Support for custom data patterns and business rules
- Configurable data distributions (normal, skewed, sequential, random)
- Time-series data generation with realistic patterns

**Customizable Output Control**
- Specify exact row counts per table or proportional relationships
- Control data formats (SQL INSERT statements, COPY format, or pg_dump custom format)
- Generate consistent data across runs with seed values
- Support partial data generation for specific tables only
- Include or exclude schema definitions, indexes, and constraints

**Scenario-Based Templates**
- Pre-built templates for common scenarios (e-commerce, SaaS, healthcare, finance)
- Ability to extend and customize templates
- Mix multiple templates to create complex systems
- Version-controlled template libraries

## Why It's Needed

**Development and Testing**
- Developers need realistic test databases without using production data
- Eliminate privacy and compliance risks of using real customer data
- Create consistent, reproducible test environments across teams
- Generate databases of varying sizes for performance testing

**Documentation and Demos**
- Quickly spin up example databases for tutorials and documentation
- Create compelling demo data for sales presentations
- Provide new team members with realistic sandbox environments
- Share database schemas without exposing sensitive information

**CI/CD Integration**
- Generate fresh test data for each pipeline run
- Create deterministic datasets for regression testing
- Test migration scripts against various data scenarios
- Validate application behavior with edge cases and boundary conditions

**Compliance and Security**
- Meet regulatory requirements by never exposing real data
- Eliminate the need for complex data masking processes
- Provide auditable, synthetic datasets for external partners
- Reduce attack surface by keeping production data isolated

## Key Design Principles

**No Database Required**
The tool operates independently, generating valid PostgreSQL dump files without needing a running database instance. This makes it lightweight, fast, and easy to integrate into any workflow.

**Declarative Configuration**
Users describe what they want, not how to create it. The tool handles the complexity of generating valid SQL, maintaining referential integrity, and creating realistic data patterns.

**Extensible and Composable**
Start with simple schemas and progressively add complexity. Combine multiple JSON configurations to build comprehensive test environments. Add custom generators for domain-specific data.

**Production-Ready Output**
Generated files are indistinguishable from real pg_dump output, ensuring compatibility with all PostgreSQL tools and workflows. Include proper headers, encoding, and formatting.

## Example Use Cases

**Microservices Development**
Each service team maintains their own schema JSON. The tool generates isolated test databases for each service plus integrated datasets for end-to-end testing.

**Load Testing**
Generate databases with millions of records following realistic distribution patterns. Test application performance without the cost and risk of copying production data.

**Training and Education**
Instructors create sample databases for students. Each student gets their own unique dataset while following the same schema, preventing copying while ensuring consistent learning experiences.

**Compliance Testing**
Generate datasets that specifically test GDPR compliance, PII handling, or other regulatory requirements without risking real user data.
