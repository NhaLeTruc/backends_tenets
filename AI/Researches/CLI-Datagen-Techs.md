# Tech Stack & Architecture Choices

## Core Language: Go

**Why Go:**
- Single binary distribution - no runtime dependencies
- Excellent performance for data generation and text processing
- Strong concurrency primitives for parallel data generation
- Rich ecosystem for CLI tools (cobra, viper)
- Cross-platform compilation out of the box
- Static typing catches schema errors at compile time

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

This architecture provides a solid foundation that's both performant and maintainable, while being extensible enough to grow with user needs.

---

## No Paid Tools - Fully Open Source Stack

**Everything in the proposed tech stack is completely free and open source.** Here's the breakdown:

## Core Technologies (All Free)

### Language & Runtime
- **Go** - Open source (BSD license)
- **Go standard library** - Included with Go

### CLI & Configuration
- **Cobra** - Apache 2.0 license
- **Viper** - MIT license

### Data Generation
- **gofakeit v6** - MIT license
- **goja** (JS engine) - MIT license

### Testing & Validation
- **stretchr/testify** - MIT license
- **pg_query_go** - PostgreSQL license (BSD-style)

### Distribution
- **GitHub Actions** - Free for public repos, generous free tier for private
- **Docker Hub** - Free for public images
- **Homebrew** - BSD 2-Clause license
- **Chocolatey** - Apache 2.0 license

### Documentation
- **Hugo** - Apache 2.0 license
- **godoc** - Part of Go toolchain

## Alternative Paid Options (Not Chosen)

While I didn't include these, here are paid alternatives that some might consider:

**What I chose instead of paid options:**
- GitHub Actions instead of CircleCI/Jenkins (paid tiers)
- Docker Hub free tier instead of paid registries
- Open source libraries instead of commercial SDKs
- Hugo instead of documentation platforms like GitBook (paid tiers)

## Cost Considerations

**The only potential costs would be:**
- GitHub Actions minutes (if exceeding free tier for private repos)
- Docker Hub (if needing private images)
- Hosting for documentation website (though GitHub Pages is free)
- Code signing certificates (optional, for trusted Windows/macOS binaries)

## Why This Open Source Approach?

1. **Lower barrier to entry** - Anyone can contribute
2. **No licensing complications** - Simple to distribute
3. **Community trust** - Full source code transparency
4. **Sustainability** - No vendor lock-in
5. **Cost-effective** - Zero licensing costs for users

The entire tool can be built, tested, and distributed without any paid dependencies, making it accessible for individual developers, startups, and enterprises alike.