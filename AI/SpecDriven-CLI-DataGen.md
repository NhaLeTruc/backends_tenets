# Spec Kit

## What is Spec-Driven Development?

Spec-Driven Development flips the script on traditional software development. For decades, code has been king — specifications were just scaffolding we built and discarded once the "real work" of coding began. Spec-Driven Development changes this: specifications become executable, directly generating working implementations rather than just guiding them.

## Get started

```bash
# If not installed
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

specify init datagen-cli
# Choose AI agent and cmd script type to boostrap your project.
# Open project directory, which was created last step, in vscode.
cd datagen-cli && code .
# optional
specify check
```

## Constitution

Use the `/speckit.constitution` command to create your project's governing principles and development guidelines that will guide all subsequent development.

```bash
/speckit.constitution Create principles focused on clean code, strict TDD adherence, and security best practices for a cli tool that generate mock postgres archive files.
```

## Specify

Use the `/speckit.specify` command to describe what you want to build. Focus on the what and why, not the tech stack.

```txt
/speckit.specify A command-line tool that transforms declarative JSON schema definitions into fully-formed PostgreSQL dump files containing realistic mock data, without requiring a running PostgreSQL instance.

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
```

## Clarify

Clarify and de-risk specification (run before /plan)

```bash
/speckit.clarify
```

## Plan

Use the `/speckit.plan` command to provide your tech stack and architecture choices.

```txt
/speckit.plan build this cli tool with Go

## Architecture Pattern: Pipeline Architecture

```
JSON Input → Parser → Schema Builder → Data Generator → SQL Formatter → Output Writer
                           ↓                ↓
                    Validation Layer   Generator Registry
```

**Why Pipeline:**
- Clear separation of concerns
- Easy to test individual stages
- Allows streaming for large datasets
- Supports parallel processing per table
- Extensible at each stage

## Key Components & Libraries

### CLI Framework
**Cobra + Viper**
- Industry standard for Go CLIs
- Built-in help generation
- Supports subcommands, flags, and config files
- Environment variable binding

### JSON Schema Parsing
**encoding/json (stdlib) + go-jsonschema**
- Validate JSON inputs against schema
- Generate Go types from JSON schemas
- Support for JSON references and inheritance

### Data Generation
**gofakeit v6**
- Primary fake data generator
- Extensible with custom generators
- Supports 200+ data types out of the box
- Thread-safe for concurrent generation

**Custom Generator Layer**
- Plugin architecture for domain-specific generators
- Weighted random selection for distributions
- Markov chains for realistic text
- Time-series generation with seasonality

### SQL Generation
**Custom SQL Builder**
- Template-based approach using text/template
- Streaming writer to handle large outputs
- Proper escaping and quote handling
- Support for PostgreSQL-specific syntax

### Validation & Testing
**stretchr/testify**
- Comprehensive assertion library
- Mock support for testing
- Table-driven tests for generators

**PostgreSQL Parser (pg_query_go)**
- Validate generated SQL without a database
- Ensure syntactic correctness
- Parse and verify constraints

## Data Architecture

### Schema Representation
```go
type Schema struct {
    Tables     map[string]*Table
    Sequences  map[string]*Sequence
    Types      map[string]*CustomType
    Extensions []string
}

type Table struct {
    Columns      []*Column
    Constraints  []*Constraint
    Indexes      []*Index
    Triggers     []*Trigger
    RowCount     int
    Dependencies []string
}
```

### Generator Registry Pattern
```go
type GeneratorRegistry struct {
    generators map[string]DataGenerator
    custom     map[string]CustomGenerator
}

type DataGenerator interface {
    Generate(ctx Context) (interface{}, error)
    Validate(value interface{}) error
}
```

## Performance Optimizations

### Concurrent Generation
- Worker pool pattern for table generation
- Channel-based coordination
- Respect foreign key dependencies
- Memory-bounded buffering

### Memory Management
- Stream large tables directly to disk
- Use sync.Pool for object reuse
- Lazy loading of reference data
- Configurable batch sizes

### Caching Layer
- LRU cache for foreign key lookups
- Memoization of expensive computations
- Shared reference data across workers

## Configuration Management

### Multi-Layer Configuration
1. **Default templates** (embedded)
2. **User templates** (~/.pgmock/templates/)
3. **Project config** (.pgmock.yaml)
4. **JSON schema files** (per invocation)
5. **CLI flags** (override everything)

### Schema Format
```json
{
  "version": "1.0",
  "database": {
    "name": "myapp",
    "encoding": "UTF8",
    "locale": "en_US.utf8"
  },
  "tables": {
    "users": {
      "columns": {
        "id": {
          "type": "serial",
          "primaryKey": true
        },
        "email": {
          "type": "varchar(255)",
          "generator": "email",
          "unique": true
        }
      },
      "rowCount": 1000
    }
  }
}
```

## Plugin System

### Generator Plugins
- Go plugins for custom generators
- JavaScript generators via goja
- External process generators via stdin/stdout
- Hot reload in development mode

### Template Extensions
- Custom SQL templates
- Domain-specific schemas
- Industry-standard datasets

## Build & Distribution

### Release Strategy
- GitHub Actions for CI/CD
- Cross-compilation for major platforms
- Homebrew tap for macOS
- APT/YUM repositories for Linux
- Chocolatey for Windows
- Docker image with Alpine Linux

### Versioning
- Semantic versioning
- Backward compatibility for schema v1.x
- Migration tools for schema updates
- Changelog generation from commits

## Testing Strategy

### Test Levels
1. **Unit tests** - Each generator and component
2. **Integration tests** - Pipeline flow
3. **Validation tests** - Generated SQL against real PostgreSQL
4. **Performance benchmarks** - Data generation speed
5. **Fuzzing** - Schema parser robustness

### Test Data
- Golden files for regression testing
- Property-based testing for generators
- Snapshot testing for SQL output
- Docker-compose for PostgreSQL validation

## Error Handling

### Graceful Degradation
- Continue generation on non-critical errors
- Collect and report all validation errors
- Rollback partial outputs on failure
- Detailed error messages with context

### Debugging Support
- Verbose mode with generation details
- Dry-run mode for validation only
- SQL EXPLAIN output for complex queries
- Performance profiling flags

## Documentation

### Generation
- godoc for API documentation
- Embedded help via Cobra
- Man page generation
- Interactive examples

### Formats
- Markdown for GitHub
- Static site via Hugo
- Video tutorials for complex scenarios
- JSON Schema documentation
```

## Task and Implement

Use `/speckit.tasks` to create an actionable task list from your implementation plan.

```bash
/speckit.tasks
```

Validate alignment & surface inconsistencies (read-only)

```bash
/speckit.analyze
```

Use `/speckit.implement` to execute all tasks and build your feature according to the plan.

```bash
/speckit.implement
```
