# Step-by-Step Guide: Building AI Agents for Data Engineering Work

**A Practical Guide Using Proven Tools and Frameworks**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Foundation Setup](#phase-1-foundation-setup)
4. [Phase 2: Agent Architecture Design](#phase-2-agent-architecture-design)
5. [Phase 3: Building Your First Data Agent](#phase-3-building-your-first-data-agent)
6. [Phase 4: Advanced Agent Capabilities](#phase-4-advanced-agent-capabilities)
7. [Phase 5: Production Deployment](#phase-5-production-deployment)
8. [Phase 6: Monitoring and Optimization](#phase-6-monitoring-and-optimization)
9. [Real-World Examples](#real-world-examples)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Introduction

### What Are AI Agents for Data Engineering?

AI agents are autonomous systems that can:
- Analyze database schemas and recommend optimizations
- Generate test data that respects all constraints
- Automate ETL pipeline creation and debugging
- Monitor data quality and suggest fixes
- Write and optimize SQL queries
- Generate documentation from code
- Perform data profiling and analysis

### Why Use AI Agents?

**Benefits:**
- **Automation**: Reduce repetitive manual tasks by 70-90%
- **Accuracy**: Eliminate human error in constraint validation
- **Speed**: Generate thousands of test records in seconds
- **Scalability**: Handle complex schemas with 50+ tables
- **Consistency**: Apply the same standards across all projects

---

## Prerequisites

### Required Knowledge

- **Python**: Intermediate level (functions, classes, async/await)
- **SQL**: Strong understanding of DDL, constraints, relationships
- **Data Engineering**: ETL concepts, data modeling, normalization
- **APIs**: REST basics, JSON handling
- **Git**: Version control fundamentals

### Required Tools

```bash
# Core tools (must have)
- Python 3.10+
- Node.js 18+ (for Claude Code)
- Git
- Docker (optional but recommended)

# AI Frameworks (choose one to start)
- Claude API (Anthropic) - Recommended for reasoning tasks
- OpenAI API - Good alternative
- LangChain - For complex orchestration
```

### Installation Checklist

```bash
# 1. Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 2. Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install core Python packages
pip install anthropic langchain pandas sqlalchemy psycopg2-binary

# 4. Set API keys
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"  # if using OpenAI

# 5. Verify installation
claude --version
python --version
```

---

## Phase 1: Foundation Setup

### Step 1.1: Create Project Structure

```bash
# Create your agent project
mkdir data-engineering-agents
cd data-engineering-agents

# Set up directory structure
mkdir -p {agents,tools,workflows,patterns,examples,tests}
mkdir -p .claude/skills

# Initialize git
git init
```

**Directory Purpose:**
- `agents/`: Your AI agent implementations
- `tools/`: Reusable utility functions
- `workflows/`: Step-by-step agent processes
- `patterns/`: Common data engineering patterns
- `examples/`: Working examples and demos
- `tests/`: Unit and integration tests
- `.claude/skills/`: Claude Code skill definitions

### Step 1.2: Set Up Configuration

Create `config/agent_config.yaml`:

```yaml
# Agent Configuration
ai_provider: "anthropic"  # or "openai"
model: "claude-sonnet-4.5"  # or "gpt-4"

# Agent capabilities
enabled_agents:
  - schema_analyzer
  - test_data_generator
  - query_optimizer
  - data_validator

# Database connections
databases:
  dev:
    type: postgresql
    host: localhost
    port: 5432
    database: dev_db

  staging:
    type: postgresql
    host: staging-db.example.com
    port: 5432
    database: staging_db

# Generation settings
test_data:
  default_record_count: 100
  edge_case_percentage: 5
  output_formats: ["sql", "json", "csv"]

# Validation rules
validation:
  max_constraint_violations: 0
  require_referential_integrity: true
  validate_before_delivery: true
```

### Step 1.3: Create Base Agent Class

Create `agents/base_agent.py`:

```python
"""
Base Agent Class for Data Engineering Tasks
"""
import anthropic
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseDataAgent(ABC):
    """
    Abstract base class for all data engineering agents.
    Provides common functionality for AI-powered automation.
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4.5"):
        """
        Initialize the base agent.

        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-sonnet-4.5)
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.conversation_history: List[Dict] = []

    def call_llm(self,
                 prompt: str,
                 system_prompt: Optional[str] = None,
                 max_tokens: int = 4096) -> str:
        """
        Call the LLM with a prompt.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Maximum response tokens

        Returns:
            LLM response text
        """
        try:
            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": messages
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = self.client.messages.create(**kwargs)

            # Extract text from response
            response_text = response.content[0].text

            # Store in history
            self.conversation_history.append({
                "prompt": prompt,
                "response": response_text
            })

            return response_text

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main task.
        Must be implemented by subclasses.

        Returns:
            Results dictionary
        """
        pass

    def validate_output(self, output: Any) -> bool:
        """
        Validate agent output before delivery.
        Override in subclasses for specific validation.

        Args:
            output: Output to validate

        Returns:
            True if valid, False otherwise
        """
        return True

    def get_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
```

---

## Phase 2: Agent Architecture Design

### Step 2.1: Choose Agent Architecture Pattern

**Three proven patterns for data engineering:**

#### Pattern 1: Single-Purpose Agent (Simplest)
```
User Request → Agent → Tool → Result
```
**Best for:** Schema analysis, data validation, simple queries
**Example:** Test data generator (your current project)

#### Pattern 2: Multi-Agent Orchestration
```
Coordinator Agent
    ├─→ Schema Analyzer Agent
    ├─→ Data Generator Agent
    └─→ Validator Agent
```
**Best for:** Complex workflows, ETL pipelines
**Example:** Full database migration assistant

#### Pattern 3: ReAct (Reasoning + Acting)
```
Agent → Think → Act → Observe → Think → Act → ...
```
**Best for:** Debugging, optimization, exploratory analysis
**Example:** Query performance troubleshooter

### Step 2.2: Define Agent Capabilities

Create `agents/capabilities.md`:

```markdown
# Agent Capability Matrix

## Schema Analyzer Agent
- **Input**: DDL SQL, database connection string
- **Output**: Constraint report, optimization suggestions
- **Tools**: SQL parser, schema validator
- **Complexity**: Low
- **Execution Time**: < 5 seconds

## Test Data Generator Agent
- **Input**: Schema DDL, record count, constraints
- **Output**: SQL/JSON/CSV with validation report
- **Tools**: Constraint solver, data generator, validator
- **Complexity**: Medium
- **Execution Time**: 10-60 seconds (depends on volume)

## Query Optimizer Agent
- **Input**: SQL query, execution plan
- **Output**: Optimized query, index suggestions
- **Tools**: Query analyzer, EXPLAIN parser
- **Complexity**: High
- **Execution Time**: 5-30 seconds

## ETL Pipeline Builder Agent
- **Input**: Source/target schemas, transformation rules
- **Output**: Python/SQL pipeline code, DAG definition
- **Tools**: Code generator, dependency analyzer
- **Complexity**: Very High
- **Execution Time**: 30-120 seconds
```

### Step 2.3: Design Tool Interface

Create `tools/tool_interface.py`:

```python
"""
Tool Interface for Agents
Agents use tools to interact with databases, files, and external systems.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class Tool(ABC):
    """Base class for agent tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for LLM."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool."""
        pass


class SchemaParserTool(Tool):
    """Parse SQL DDL and extract constraints."""

    @property
    def name(self) -> str:
        return "parse_schema"

    @property
    def description(self) -> str:
        return """
        Parses SQL DDL and extracts:
        - Tables and columns
        - Primary keys
        - Foreign keys with cascade rules
        - Unique constraints
        - NOT NULL constraints
        - CHECK constraints
        - Data types with precision

        Input: SQL DDL string
        Output: JSON schema representation
        """

    def execute(self, ddl: str) -> Dict[str, Any]:
        """
        Parse DDL and return structured schema.

        Args:
            ddl: SQL DDL string

        Returns:
            Schema dictionary
        """
        # Implementation would use sqlparse or similar
        # Simplified example:
        schema = {
            "tables": [],
            "constraints": {
                "primary_keys": [],
                "foreign_keys": [],
                "unique": [],
                "not_null": [],
                "check": []
            }
        }

        # TODO: Implement actual parsing logic

        return schema


class DataValidatorTool(Tool):
    """Validate generated data against constraints."""

    @property
    def name(self) -> str:
        return "validate_data"

    @property
    def description(self) -> str:
        return """
        Validates data against schema constraints:
        - Primary key uniqueness
        - Foreign key integrity
        - Unique constraint satisfaction
        - NOT NULL compliance
        - CHECK constraint satisfaction
        - Data type compatibility

        Input: Schema dict, data records
        Output: Validation report with violations
        """

    def execute(self, schema: Dict, data: List[Dict]) -> Dict[str, Any]:
        """
        Validate data against schema.

        Args:
            schema: Schema dictionary
            data: List of data records

        Returns:
            Validation report
        """
        violations = []

        # Validate each constraint type
        # TODO: Implement validation logic

        return {
            "is_valid": len(violations) == 0,
            "total_records": len(data),
            "violations": violations,
            "constraint_satisfaction_rate": 1.0 if not violations else 0.95
        }
```

---

## Phase 3: Building Your First Data Agent

### Step 3.1: Schema Analyzer Agent (Starter Project)

Create `agents/schema_analyzer.py`:

```python
"""
Schema Analyzer Agent
Analyzes database schemas and provides optimization recommendations.
"""
from typing import Dict, Any, List
from agents.base_agent import BaseDataAgent
from tools.tool_interface import SchemaParserTool
import json


class SchemaAnalyzerAgent(BaseDataAgent):
    """
    Analyzes database schemas for:
    - Constraint completeness
    - Indexing opportunities
    - Normalization issues
    - Performance bottlenecks
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.parser = SchemaParserTool()

    def execute(self, ddl: str) -> Dict[str, Any]:
        """
        Analyze schema and provide recommendations.

        Args:
            ddl: SQL DDL string

        Returns:
            Analysis report with recommendations
        """
        # Step 1: Parse schema
        schema = self.parser.execute(ddl)

        # Step 2: Build analysis prompt
        system_prompt = """
        You are a database schema expert. Analyze the provided schema and:

        1. Identify missing indexes for foreign keys
        2. Check for missing NOT NULL constraints
        3. Verify referential integrity setup
        4. Suggest normalization improvements
        5. Flag potential performance issues

        Provide actionable, specific recommendations with SQL examples.
        """

        user_prompt = f"""
        Analyze this database schema:

        ```json
        {json.dumps(schema, indent=2)}
        ```

        Provide:
        1. Schema summary (tables, relationships, constraints)
        2. Issues found (critical, warnings, suggestions)
        3. Recommendations with SQL to fix issues
        4. Estimated impact of each recommendation

        Format as structured JSON.
        """

        # Step 3: Call LLM
        response = self.call_llm(user_prompt, system_prompt, max_tokens=8192)

        # Step 4: Parse response
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            analysis = {
                "raw_response": response,
                "parsed": False
            }

        return {
            "schema": schema,
            "analysis": analysis,
            "success": True
        }


# Example usage
if __name__ == "__main__":
    import os

    # Initialize agent
    agent = SchemaAnalyzerAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Example schema
    ddl = """
    CREATE TABLE users (
        id INT PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        age INT CHECK (age >= 18)
    );

    CREATE TABLE orders (
        id INT PRIMARY KEY,
        user_id INT REFERENCES users(id),
        total DECIMAL(10,2)
    );
    """

    # Run analysis
    result = agent.execute(ddl)

    print(json.dumps(result, indent=2))
```

### Step 3.2: Test Your First Agent

Create `tests/test_schema_analyzer.py`:

```python
"""
Tests for Schema Analyzer Agent
"""
import pytest
import os
from agents.schema_analyzer import SchemaAnalyzerAgent


@pytest.fixture
def agent():
    """Create agent instance."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return SchemaAnalyzerAgent(api_key)


def test_simple_schema_analysis(agent):
    """Test analysis of simple schema."""
    ddl = """
    CREATE TABLE users (
        id INT PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );
    """

    result = agent.execute(ddl)

    assert result["success"] is True
    assert "schema" in result
    assert "analysis" in result


def test_missing_indexes_detection(agent):
    """Test detection of missing FK indexes."""
    ddl = """
    CREATE TABLE users (id INT PRIMARY KEY);
    CREATE TABLE orders (
        id INT PRIMARY KEY,
        user_id INT REFERENCES users(id)
    );
    """

    result = agent.execute(ddl)

    # Should recommend index on orders.user_id
    assert result["success"] is True
    # Add more specific assertions based on response format


def test_constraint_completeness(agent):
    """Test checking for missing constraints."""
    ddl = """
    CREATE TABLE products (
        id INT PRIMARY KEY,
        price DECIMAL(10,2)
    );
    """

    result = agent.execute(ddl)

    # Should recommend CHECK price >= 0
    assert result["success"] is True
```

Run tests:

```bash
# Install pytest
pip install pytest pytest-cov

# Run tests
pytest tests/ -v --cov=agents
```

### Step 3.3: Build Test Data Generator Agent

Create `agents/test_data_generator.py`:

```python
"""
Test Data Generator Agent
Generates constraint-valid test data for databases.
"""
from typing import Dict, Any, List
from agents.base_agent import BaseDataAgent
from tools.tool_interface import SchemaParserTool, DataValidatorTool
import json


class TestDataGeneratorAgent(BaseDataAgent):
    """
    Generates production-quality test data that:
    - Respects ALL database constraints
    - Maintains referential integrity
    - Includes configurable edge cases
    - Validates before delivery
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.parser = SchemaParserTool()
        self.validator = DataValidatorTool()

    def execute(self,
                ddl: str,
                record_counts: Dict[str, int],
                edge_case_percentage: float = 0.05,
                output_format: str = "sql") -> Dict[str, Any]:
        """
        Generate test data.

        Args:
            ddl: SQL DDL string
            record_counts: Table → record count mapping
            edge_case_percentage: Percentage of edge cases (0.0-1.0)
            output_format: "sql", "json", or "csv"

        Returns:
            Generated data with validation report
        """
        # Step 1: Parse schema
        schema = self.parser.execute(ddl)

        # Step 2: Build generation prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            schema,
            record_counts,
            edge_case_percentage
        )

        # Step 3: Generate data
        response = self.call_llm(user_prompt, system_prompt, max_tokens=16384)

        # Step 4: Parse generated data
        data = self._parse_generated_data(response)

        # Step 5: Validate
        validation_report = self.validator.execute(schema, data)

        if not validation_report["is_valid"]:
            # Retry with constraint violations feedback
            return self._retry_with_feedback(
                schema,
                record_counts,
                validation_report
            )

        # Step 6: Format output
        output = self._format_output(data, output_format)

        return {
            "data": output,
            "validation_report": validation_report,
            "record_counts": {
                table: len(records)
                for table, records in data.items()
            },
            "success": True
        }

    def _build_system_prompt(self) -> str:
        """Build system prompt with generation rules."""
        return """
        You are a test data generation expert. Generate realistic, constraint-valid test data.

        MANDATORY RULES:
        1. ALL constraints must be satisfied (PK, FK, UNIQUE, NOT NULL, CHECK)
        2. Generate parent tables before child tables (topological order)
        3. All foreign keys must reference existing primary keys
        4. Use realistic data patterns (US names, emails, addresses)
        5. Include edge cases at requested percentage
        6. Validate before delivery (zero violations)

        CONSTRAINT HIERARCHY (in case of conflict):
        1. Database constraints (ALWAYS satisfied)
        2. Realistic patterns (prefer over random data)
        3. Edge cases (skip if violates constraints)

        OUTPUT FORMAT:
        Return JSON with structure:
        {
          "tables": {
            "table_name": [
              {"col1": val1, "col2": val2, ...},
              ...
            ]
          }
        }
        """

    def _build_user_prompt(self,
                          schema: Dict,
                          record_counts: Dict[str, int],
                          edge_case_percentage: float) -> str:
        """Build user prompt with generation request."""
        return f"""
        Generate test data for this schema:

        ```json
        {json.dumps(schema, indent=2)}
        ```

        Requirements:
        - Record counts: {json.dumps(record_counts)}
        - Edge case percentage: {edge_case_percentage * 100}%
        - Edge cases to include:
          * Boundary values (min/max for CHECK constraints)
          * Special characters in strings (O'Brien, test+tag@example.com)
          * NULL values for nullable fields

        Generate in topological order (parents before children).
        Ensure 100% constraint satisfaction.
        Return as JSON.
        """

    def _parse_generated_data(self, response: str) -> Dict[str, List[Dict]]:
        """Parse LLM response to extract data."""
        try:
            parsed = json.loads(response)
            return parsed.get("tables", {})
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if match:
                return json.loads(match.group(1)).get("tables", {})
            raise ValueError("Failed to parse generated data")

    def _retry_with_feedback(self,
                            schema: Dict,
                            record_counts: Dict[str, int],
                            validation_report: Dict) -> Dict[str, Any]:
        """Retry generation with constraint violation feedback."""
        # TODO: Implement retry logic
        return {
            "success": False,
            "error": "Validation failed",
            "validation_report": validation_report
        }

    def _format_output(self, data: Dict[str, List[Dict]], format: str) -> str:
        """Format data as SQL/JSON/CSV."""
        if format == "json":
            return json.dumps(data, indent=2)
        elif format == "sql":
            return self._to_sql_inserts(data)
        elif format == "csv":
            return self._to_csv(data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _to_sql_inserts(self, data: Dict[str, List[Dict]]) -> str:
        """Convert to SQL INSERT statements."""
        sql_parts = []

        for table_name, records in data.items():
            if not records:
                continue

            # Get column names from first record
            columns = list(records[0].keys())
            col_list = ", ".join(columns)

            # Build VALUES clauses
            values_clauses = []
            for record in records:
                values = []
                for col in columns:
                    val = record[col]
                    if val is None:
                        values.append("NULL")
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    else:
                        # Escape single quotes
                        escaped = str(val).replace("'", "''")
                        values.append(f"'{escaped}'")

                values_clauses.append(f"({', '.join(values)})")

            # Combine into INSERT statement
            sql = f"INSERT INTO {table_name} ({col_list}) VALUES\n"
            sql += ",\n".join(values_clauses) + ";"
            sql_parts.append(sql)

        return "\n\n".join(sql_parts)

    def _to_csv(self, data: Dict[str, List[Dict]]) -> Dict[str, str]:
        """Convert to CSV (one file per table)."""
        import csv
        import io

        csv_files = {}

        for table_name, records in data.items():
            if not records:
                continue

            output = io.StringIO()
            columns = list(records[0].keys())

            writer = csv.DictWriter(output, fieldnames=columns)
            writer.writeheader()
            writer.writerows(records)

            csv_files[f"{table_name}.csv"] = output.getvalue()

        return csv_files


# Example usage
if __name__ == "__main__":
    import os

    agent = TestDataGeneratorAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))

    ddl = """
    CREATE TABLE users (
        id INT PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        age INT CHECK (age >= 18)
    );
    """

    result = agent.execute(
        ddl=ddl,
        record_counts={"users": 10},
        edge_case_percentage=0.1,
        output_format="sql"
    )

    print(result["data"])
    print("\nValidation Report:")
    print(json.dumps(result["validation_report"], indent=2))
```

---

## Phase 4: Advanced Agent Capabilities

### Step 4.1: Add Tool Use (Function Calling)

Create `agents/agent_with_tools.py`:

```python
"""
Agent with Tool Use Capability
Demonstrates how to give agents access to tools via function calling.
"""
from typing import Dict, Any, List, Callable
from agents.base_agent import BaseDataAgent
import json


class ToolUseAgent(BaseDataAgent):
    """
    Agent that can use tools via function calling.
    Based on Anthropic's tool use pattern.
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: List[Dict] = []

    def register_tool(self,
                     name: str,
                     description: str,
                     parameters: Dict,
                     function: Callable):
        """
        Register a tool for the agent to use.

        Args:
            name: Tool name
            description: What the tool does
            parameters: JSON schema for parameters
            function: The actual function to call
        """
        self.tools[name] = function
        self.tool_definitions.append({
            "name": name,
            "description": description,
            "input_schema": parameters
        })

    def execute(self, task: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Execute task with tool use.

        Args:
            task: Task description
            max_iterations: Max tool use iterations

        Returns:
            Task result
        """
        messages = [{"role": "user", "content": task}]

        for iteration in range(max_iterations):
            # Call LLM with tools
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                tools=self.tool_definitions,
                messages=messages
            )

            # Check if tool use is requested
            if response.stop_reason == "tool_use":
                # Extract tool calls
                tool_uses = [
                    block for block in response.content
                    if block.type == "tool_use"
                ]

                # Execute tools
                tool_results = []
                for tool_use in tool_uses:
                    result = self._execute_tool(
                        tool_use.name,
                        tool_use.input
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": json.dumps(result)
                    })

                # Add results to messages
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

            else:
                # Task complete
                final_response = next(
                    (block.text for block in response.content
                     if hasattr(block, "text")),
                    ""
                )
                return {
                    "success": True,
                    "result": final_response,
                    "iterations": iteration + 1
                }

        return {
            "success": False,
            "error": "Max iterations reached"
        }

    def _execute_tool(self, tool_name: str, parameters: Dict) -> Any:
        """Execute a registered tool."""
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            return self.tools[tool_name](**parameters)
        except Exception as e:
            return {"error": str(e)}


# Example: Query optimizer agent with tools
class QueryOptimizerAgent(ToolUseAgent):
    """Agent that optimizes SQL queries using tools."""

    def __init__(self, api_key: str, db_connection):
        super().__init__(api_key)
        self.db = db_connection

        # Register tools
        self._register_query_tools()

    def _register_query_tools(self):
        """Register query optimization tools."""

        # Tool 1: Get EXPLAIN plan
        self.register_tool(
            name="get_explain_plan",
            description="Get query execution plan using EXPLAIN",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to analyze"
                    }
                },
                "required": ["query"]
            },
            function=self._get_explain_plan
        )

        # Tool 2: Get table statistics
        self.register_tool(
            name="get_table_stats",
            description="Get table statistics (row count, size, indexes)",
            parameters={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Table name"
                    }
                },
                "required": ["table_name"]
            },
            function=self._get_table_stats
        )

        # Tool 3: Check if index exists
        self.register_tool(
            name="check_index",
            description="Check if index exists on column(s)",
            parameters={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"},
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["table_name", "columns"]
            },
            function=self._check_index
        )

    def _get_explain_plan(self, query: str) -> Dict:
        """Get EXPLAIN plan for query."""
        # Implementation would execute EXPLAIN
        return {
            "plan": "Seq Scan on users (cost=0..100 rows=1000)",
            "has_index_scan": False,
            "estimated_cost": 100
        }

    def _get_table_stats(self, table_name: str) -> Dict:
        """Get table statistics."""
        return {
            "table": table_name,
            "row_count": 10000,
            "size_mb": 15.2,
            "indexes": ["users_pkey", "users_email_idx"]
        }

    def _check_index(self, table_name: str, columns: List[str]) -> Dict:
        """Check if index exists."""
        return {
            "exists": False,
            "recommendation": f"CREATE INDEX idx_{table_name}_{'_'.join(columns)} ON {table_name}({', '.join(columns)})"
        }


# Example usage
if __name__ == "__main__":
    import os

    agent = QueryOptimizerAgent(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        db_connection=None  # Would be real DB connection
    )

    task = """
    Optimize this query:

    SELECT u.name, COUNT(o.id)
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.created_at > '2024-01-01'
    GROUP BY u.name
    ORDER BY COUNT(o.id) DESC
    LIMIT 10;

    The query is slow on a table with 1M users and 5M orders.
    """

    result = agent.execute(task)
    print(result["result"])
```

### Step 4.2: Add Memory and Context

Create `agents/agent_with_memory.py`:

```python
"""
Agent with Long-Term Memory
Maintains context across multiple interactions.
"""
from typing import Dict, Any, List
from agents.base_agent import BaseDataAgent
import json
import sqlite3
from datetime import datetime


class MemoryAgent(BaseDataAgent):
    """
    Agent with persistent memory using SQLite.
    Remembers past interactions and learns from feedback.
    """

    def __init__(self, api_key: str, memory_db: str = "agent_memory.db"):
        super().__init__(api_key)
        self.memory_db = memory_db
        self._init_memory_db()

    def _init_memory_db(self):
        """Initialize memory database."""
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                task TEXT,
                context TEXT,
                result TEXT,
                feedback TEXT,
                success BOOLEAN
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_data TEXT,
                confidence REAL,
                usage_count INTEGER DEFAULT 0
            )
        """)

        conn.commit()
        conn.close()

    def execute(self, task: str, context: Dict = None) -> Dict[str, Any]:
        """
        Execute task with memory context.

        Args:
            task: Task description
            context: Additional context

        Returns:
            Task result
        """
        # Retrieve relevant memories
        memories = self._retrieve_memories(task)

        # Build enriched prompt
        prompt = self._build_prompt_with_memory(task, context, memories)

        # Execute
        response = self.call_llm(prompt)

        # Store interaction
        interaction_id = self._store_interaction(
            task=task,
            context=context,
            result=response
        )

        return {
            "result": response,
            "interaction_id": interaction_id,
            "memories_used": len(memories)
        }

    def _retrieve_memories(self, task: str, limit: int = 5) -> List[Dict]:
        """Retrieve relevant past interactions."""
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()

        # Simple keyword-based retrieval
        # In production, use embeddings + vector search
        cursor.execute("""
            SELECT task, result, feedback, success
            FROM interactions
            WHERE task LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{task[:20]}%", limit))

        memories = []
        for row in cursor.fetchall():
            memories.append({
                "task": row[0],
                "result": row[1],
                "feedback": row[2],
                "success": bool(row[3])
            })

        conn.close()
        return memories

    def _build_prompt_with_memory(self,
                                  task: str,
                                  context: Dict,
                                  memories: List[Dict]) -> str:
        """Build prompt enriched with memories."""
        prompt_parts = [f"Task: {task}"]

        if context:
            prompt_parts.append(f"\nContext: {json.dumps(context)}")

        if memories:
            prompt_parts.append("\nRelevant past experiences:")
            for i, mem in enumerate(memories, 1):
                prompt_parts.append(f"\n{i}. Similar task: {mem['task']}")
                if mem['feedback']:
                    prompt_parts.append(f"   Feedback received: {mem['feedback']}")

        return "\n".join(prompt_parts)

    def _store_interaction(self,
                          task: str,
                          context: Dict,
                          result: str) -> int:
        """Store interaction in memory."""
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO interactions (timestamp, task, context, result, success)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            task,
            json.dumps(context) if context else None,
            result,
            True  # Assume success unless feedback says otherwise
        ))

        interaction_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return interaction_id

    def add_feedback(self, interaction_id: int, feedback: str, success: bool):
        """Add feedback to past interaction."""
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE interactions
            SET feedback = ?, success = ?
            WHERE id = ?
        """, (feedback, success, interaction_id))

        conn.commit()
        conn.close()
```

---

## Phase 5: Production Deployment

### Step 5.1: Create Claude Code Skill

Create `.claude/skills/data-engineering/SKILL.md`:

```markdown
# Data Engineering AI Agent Skill

Transform Claude into a data engineering assistant that can:
- Analyze database schemas
- Generate constraint-valid test data
- Optimize SQL queries
- Build ETL pipelines
- Validate data quality

## Usage

Simply ask Claude naturally:

- "Analyze this database schema and suggest optimizations"
- "Generate 1000 test records for this schema"
- "Optimize this slow query"
- "Build an ETL pipeline from source to target"

## How It Works

Claude uses specialized agents that:

1. **Parse** your schema/query/requirements
2. **Analyze** constraints, patterns, and bottlenecks
3. **Generate** solutions using proven patterns
4. **Validate** output before delivery
5. **Deliver** with comprehensive reports

## Examples

See `examples/` directory for:
- Schema analysis
- Test data generation
- Query optimization
- ETL pipeline building
```

### Step 5.2: Package as Python Library

Create `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="data-engineering-agents",
    version="0.1.0",
    description="AI agents for data engineering automation",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "anthropic>=0.18.0",
        "sqlparse>=0.4.0",
        "pandas>=2.0.0",
        "sqlalchemy>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ]
    },
    python_requires=">=3.10",
)
```

Install in development mode:

```bash
pip install -e .
```

### Step 5.3: Create Docker Container

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY agents/ ./agents/
COPY tools/ ./tools/
COPY workflows/ ./workflows/

# Set environment
ENV PYTHONPATH=/app

# Run agent server
CMD ["python", "-m", "agents.server"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  agent:
    build: .
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=postgresql://user:pass@db:5432/testdb
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=testdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

Run with Docker:

```bash
docker-compose up -d
```

### Step 5.4: Create REST API

Create `agents/server.py`:

```python
"""
REST API Server for Data Engineering Agents
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from agents.schema_analyzer import SchemaAnalyzerAgent
from agents.test_data_generator import TestDataGeneratorAgent

app = FastAPI(title="Data Engineering Agents API")

# Initialize agents
api_key = os.getenv("ANTHROPIC_API_KEY")
schema_analyzer = SchemaAnalyzerAgent(api_key)
data_generator = TestDataGeneratorAgent(api_key)


class SchemaAnalysisRequest(BaseModel):
    ddl: str


class TestDataRequest(BaseModel):
    ddl: str
    record_counts: Dict[str, int]
    edge_case_percentage: float = 0.05
    output_format: str = "sql"


@app.post("/analyze-schema")
async def analyze_schema(request: SchemaAnalysisRequest) -> Dict[str, Any]:
    """Analyze database schema."""
    try:
        result = schema_analyzer.execute(request.ddl)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-test-data")
async def generate_test_data(request: TestDataRequest) -> Dict[str, Any]:
    """Generate test data."""
    try:
        result = data_generator.execute(
            ddl=request.ddl,
            record_counts=request.record_counts,
            edge_case_percentage=request.edge_case_percentage,
            output_format=request.output_format
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Install FastAPI:

```bash
pip install fastapi uvicorn pydantic
```

Run server:

```bash
python -m agents.server
```

Test API:

```bash
curl -X POST http://localhost:8000/analyze-schema \
  -H "Content-Type: application/json" \
  -d '{
    "ddl": "CREATE TABLE users (id INT PRIMARY KEY, email VARCHAR(255));"
  }'
```

---

## Phase 6: Monitoring and Optimization

### Step 6.1: Add Logging and Metrics

Create `agents/monitoring.py`:

```python
"""
Monitoring and observability for agents.
"""
import logging
import time
from functools import wraps
from typing import Callable, Any
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agents.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class AgentMetrics:
    """Track agent performance metrics."""

    def __init__(self):
        self.metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_duration_seconds": 0.0,
            "llm_calls": 0,
            "total_tokens": 0,
        }

    def record_execution(self,
                        success: bool,
                        duration: float,
                        llm_calls: int = 1,
                        tokens: int = 0):
        """Record execution metrics."""
        self.metrics["total_executions"] += 1
        self.metrics["total_duration_seconds"] += duration
        self.metrics["llm_calls"] += llm_calls
        self.metrics["total_tokens"] += tokens

        if success:
            self.metrics["successful_executions"] += 1
        else:
            self.metrics["failed_executions"] += 1

    def get_stats(self) -> dict:
        """Get summary statistics."""
        total = self.metrics["total_executions"]
        if total == 0:
            return self.metrics

        return {
            **self.metrics,
            "success_rate": self.metrics["successful_executions"] / total,
            "avg_duration_seconds": self.metrics["total_duration_seconds"] / total,
            "avg_tokens_per_call": self.metrics["total_tokens"] / max(self.metrics["llm_calls"], 1)
        }


# Global metrics instance
metrics = AgentMetrics()


def monitor_execution(func: Callable) -> Callable:
    """Decorator to monitor agent execution."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        success = False

        try:
            result = func(*args, **kwargs)
            success = result.get("success", True)

            # Log success
            logger.info(f"{func.__name__} completed successfully")

            return result

        except Exception as e:
            # Log error
            logger.error(f"{func.__name__} failed: {e}", exc_info=True)
            raise

        finally:
            duration = time.time() - start_time

            # Record metrics
            metrics.record_execution(
                success=success,
                duration=duration
            )

            # Log performance
            logger.info(f"{func.__name__} took {duration:.2f}s")

    return wrapper
```

Apply monitoring to agents:

```python
from agents.monitoring import monitor_execution

class SchemaAnalyzerAgent(BaseDataAgent):

    @monitor_execution
    def execute(self, ddl: str) -> Dict[str, Any]:
        # ... existing implementation
        pass
```

### Step 6.2: Add Cost Tracking

Create `agents/cost_tracker.py`:

```python
"""
Track LLM API costs.
"""

class CostTracker:
    """Track and estimate LLM API costs."""

    # Pricing (as of Jan 2025)
    PRICING = {
        "claude-sonnet-4.5": {
            "input": 0.003,   # per 1K tokens
            "output": 0.015   # per 1K tokens
        },
        "claude-opus-4.5": {
            "input": 0.015,
            "output": 0.075
        }
    }

    def __init__(self):
        self.total_cost = 0.0
        self.costs_by_model = {}

    def track_call(self,
                   model: str,
                   input_tokens: int,
                   output_tokens: int):
        """Track cost of an LLM call."""
        if model not in self.PRICING:
            return

        pricing = self.PRICING[model]
        cost = (
            (input_tokens / 1000) * pricing["input"] +
            (output_tokens / 1000) * pricing["output"]
        )

        self.total_cost += cost

        if model not in self.costs_by_model:
            self.costs_by_model[model] = 0.0
        self.costs_by_model[model] += cost

    def get_summary(self) -> dict:
        """Get cost summary."""
        return {
            "total_cost_usd": round(self.total_cost, 4),
            "costs_by_model": {
                model: round(cost, 4)
                for model, cost in self.costs_by_model.items()
            }
        }


# Global cost tracker
cost_tracker = CostTracker()
```

### Step 6.3: Add Performance Optimization

```python
"""
Performance optimization techniques.
"""
from functools import lru_cache
import asyncio
from typing import List, Dict, Any


class OptimizedAgent(BaseDataAgent):
    """Agent with performance optimizations."""

    @lru_cache(maxsize=128)
    def cached_call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """LLM call with caching for identical prompts."""
        return self.call_llm(prompt, system_prompt)

    async def batch_execute(self, tasks: List[Dict[str, Any]]) -> List[Dict]:
        """Execute multiple tasks in parallel."""

        async def execute_one(task):
            """Execute single task asynchronously."""
            # Wrap synchronous execute in async
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.execute, **task)

        # Run all tasks concurrently
        results = await asyncio.gather(*[execute_one(task) for task in tasks])

        return results

    def compress_prompt(self, prompt: str, max_length: int = 4000) -> str:
        """Compress prompt to reduce token usage."""
        if len(prompt) <= max_length:
            return prompt

        # Simple truncation (in production, use smarter summarization)
        return prompt[:max_length] + "\n... (truncated)"
```

---

## Real-World Examples

### Example 1: Complete ETL Pipeline Agent

```python
"""
ETL Pipeline Builder Agent
Generates complete ETL pipelines from source to target schemas.
"""
from agents.base_agent import BaseDataAgent
from typing import Dict, Any


class ETLPipelineAgent(BaseDataAgent):
    """Builds ETL pipelines automatically."""

    def execute(self,
                source_ddl: str,
                target_ddl: str,
                transformation_rules: Dict = None) -> Dict[str, Any]:
        """
        Generate ETL pipeline code.

        Args:
            source_ddl: Source schema DDL
            target_ddl: Target schema DDL
            transformation_rules: Optional transformation rules

        Returns:
            Pipeline code and documentation
        """
        system_prompt = """
        You are an ETL pipeline expert. Generate production-ready ETL code that:

        1. Extracts data from source tables
        2. Transforms according to rules
        3. Loads into target tables
        4. Handles errors and retries
        5. Logs progress and metrics

        Output Python code using pandas/sqlalchemy.
        Include comprehensive error handling.
        """

        user_prompt = f"""
        Build an ETL pipeline:

        Source Schema:
        ```sql
        {source_ddl}
        ```

        Target Schema:
        ```sql
        {target_ddl}
        ```

        Transformation Rules:
        {transformation_rules or "Auto-infer from schemas"}

        Generate:
        1. Python ETL code
        2. Configuration file
        3. Error handling strategy
        4. Monitoring/logging setup
        5. Deployment instructions
        """

        response = self.call_llm(user_prompt, system_prompt, max_tokens=16384)

        return {
            "pipeline_code": self._extract_code(response),
            "documentation": response,
            "success": True
        }

    def _extract_code(self, response: str) -> str:
        """Extract code from markdown response."""
        import re
        match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
        return match.group(1) if match else response
```

### Example 2: Data Quality Monitor Agent

```python
"""
Data Quality Monitor Agent
Monitors data quality and alerts on issues.
"""
from agents.base_agent import BaseDataAgent
import pandas as pd
from typing import Dict, Any, List


class DataQualityAgent(BaseDataAgent):
    """Monitors and validates data quality."""

    def execute(self,
                data: pd.DataFrame,
                schema: Dict,
                quality_rules: List[Dict] = None) -> Dict[str, Any]:
        """
        Check data quality.

        Args:
            data: DataFrame to validate
            schema: Expected schema
            quality_rules: Custom quality rules

        Returns:
            Quality report
        """
        # Run built-in checks
        issues = []

        # Check 1: Missing values
        missing = data.isnull().sum()
        for col, count in missing[missing > 0].items():
            issues.append({
                "type": "missing_values",
                "column": col,
                "count": int(count),
                "percentage": count / len(data) * 100
            })

        # Check 2: Duplicates
        duplicates = data.duplicated().sum()
        if duplicates > 0:
            issues.append({
                "type": "duplicates",
                "count": int(duplicates)
            })

        # Check 3: Outliers (for numeric columns)
        numeric_cols = data.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((data[col] < Q1 - 1.5 * IQR) |
                       (data[col] > Q3 + 1.5 * IQR)).sum()

            if outliers > 0:
                issues.append({
                    "type": "outliers",
                    "column": col,
                    "count": int(outliers)
                })

        # Use LLM for custom quality checks
        if quality_rules:
            llm_issues = self._check_custom_rules(data, quality_rules)
            issues.extend(llm_issues)

        # Generate recommendations
        recommendations = self._generate_recommendations(issues)

        return {
            "quality_score": self._calculate_score(issues, len(data)),
            "issues": issues,
            "recommendations": recommendations,
            "record_count": len(data),
            "success": True
        }

    def _check_custom_rules(self,
                           data: pd.DataFrame,
                           rules: List[Dict]) -> List[Dict]:
        """Use LLM to check custom quality rules."""
        # Sample data for LLM analysis
        sample = data.head(100).to_dict('records')

        prompt = f"""
        Check these custom data quality rules:

        Rules: {rules}

        Sample data (100 rows):
        {sample}

        For each rule violation, return:
        {{
          "type": "custom_rule",
          "rule": "rule description",
          "violation_count": estimated_count,
          "severity": "high|medium|low"
        }}
        """

        response = self.call_llm(prompt)
        # Parse response...
        return []

    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate fix recommendations."""
        if not issues:
            return ["Data quality is excellent! No issues found."]

        recs = []
        for issue in issues:
            if issue["type"] == "missing_values":
                recs.append(
                    f"Column '{issue['column']}': Impute {issue['count']} missing values "
                    f"or investigate why {issue['percentage']:.1f}% are null"
                )
            elif issue["type"] == "duplicates":
                recs.append(
                    f"Remove {issue['count']} duplicate records or verify if legitimate"
                )

        return recs

    def _calculate_score(self, issues: List[Dict], total_records: int) -> float:
        """Calculate overall quality score (0-100)."""
        if not issues:
            return 100.0

        # Simple scoring: deduct points per issue
        deduction = min(len(issues) * 5, 50)  # Max 50 point deduction
        return max(100.0 - deduction, 0.0)
```

---

## Best Practices

### 1. Prompt Engineering

```python
"""Best practices for prompts."""

# ✅ GOOD: Specific, structured prompt
prompt = """
Generate test data for this schema with these requirements:

Schema:
{schema}

Requirements:
1. Generate exactly {count} records
2. Respect all constraints (PK, FK, UNIQUE, NOT NULL, CHECK)
3. Include {edge_pct}% edge cases
4. Use realistic US patterns (names, emails, addresses)

Return as JSON with this structure:
{{
  "tables": {{
    "table_name": [
      {{"col1": val1, "col2": val2}},
      ...
    ]
  }}
}}
"""

# ❌ BAD: Vague, unstructured prompt
prompt = "Generate some test data for my database"
```

### 2. Error Handling

```python
"""Robust error handling."""

def execute_with_retry(self, task: str, max_retries: int = 3):
    """Execute with automatic retry."""

    for attempt in range(max_retries):
        try:
            result = self.execute(task)

            # Validate result
            if not self.validate_output(result):
                raise ValueError("Output validation failed")

            return result

        except anthropic.APIError as e:
            if attempt == max_retries - 1:
                raise

            # Exponential backoff
            wait_time = 2 ** attempt
            logger.warning(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
            time.sleep(wait_time)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
```

### 3. Testing

```python
"""Comprehensive testing strategy."""

# Unit tests
def test_schema_parser():
    """Test schema parsing."""
    parser = SchemaParserTool()
    schema = parser.execute("CREATE TABLE users (id INT PRIMARY KEY);")
    assert "users" in schema["tables"]
    assert len(schema["constraints"]["primary_keys"]) == 1


# Integration tests
def test_end_to_end_generation():
    """Test full generation workflow."""
    agent = TestDataGeneratorAgent(api_key=TEST_API_KEY)
    result = agent.execute(
        ddl=TEST_SCHEMA,
        record_counts={"users": 10}
    )

    assert result["success"]
    assert result["validation_report"]["is_valid"]
    assert len(result["data"]["users"]) == 10


# Regression tests
def test_known_edge_cases():
    """Test previously failing scenarios."""
    # Test Case: Self-referencing FK
    # Test Case: Circular dependencies
    # Test Case: Complex CHECK constraints
    pass
```

### 4. Security

```python
"""Security best practices."""

# ✅ GOOD: Parameterized queries
def safe_execute(self, query: str, params: tuple):
    """Execute with parameters."""
    cursor.execute(query, params)


# ❌ BAD: String interpolation (SQL injection risk)
def unsafe_execute(self, table: str, value: str):
    """NEVER DO THIS!"""
    cursor.execute(f"SELECT * FROM {table} WHERE col = '{value}'")


# ✅ GOOD: Validate LLM output before execution
def execute_generated_sql(self, sql: str):
    """Execute generated SQL safely."""
    # Validate no destructive operations
    forbidden = ["DROP", "DELETE", "TRUNCATE", "UPDATE"]
    if any(kw in sql.upper() for kw in forbidden):
        raise ValueError("Generated SQL contains forbidden operation")

    # Execute in read-only transaction
    with db.connect() as conn:
        conn.execute("SET TRANSACTION READ ONLY")
        result = conn.execute(sql)
        return result
```

---

## Troubleshooting

### Common Issues

**Issue 1: LLM not following schema constraints**

```python
# Solution: Add validation layer
def execute_with_validation(self, schema, record_count):
    result = self.execute_generation(schema, record_count)

    # Validate
    violations = self.validate(result)

    if violations:
        # Retry with violations as context
        return self.execute_with_feedback(schema, record_count, violations)

    return result
```

**Issue 2: High API costs**

```python
# Solution: Cache frequent calls
@lru_cache(maxsize=256)
def cached_analyze_schema(self, ddl: str):
    """Cache schema analysis results."""
    return self.analyze_schema(ddl)

# Solution: Use cheaper models for simple tasks
def choose_model(self, task_complexity: str):
    if task_complexity == "low":
        return "claude-haiku-4"  # Cheaper
    else:
        return "claude-sonnet-4.5"  # More capable
```

**Issue 3: Slow execution**

```python
# Solution: Parallel execution
async def process_tables_parallel(self, tables: List[str]):
    tasks = [self.process_table(table) for table in tables]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Next Steps

### Advanced Topics (Not Covered Here)

1. **Vector Embeddings**: Use embeddings for semantic search in schemas
2. **Fine-tuning**: Fine-tune models on your specific data patterns
3. **Multi-Modal**: Process ERD diagrams, screenshots
4. **Streaming**: Stream large result sets
5. **Distributed**: Scale across multiple agents

### Resources

**Documentation:**
- [Anthropic API Docs](https://docs.anthropic.com)
- [Claude Code Guide](https://github.com/anthropics/claude-code)
- [LangChain Docs](https://python.langchain.com)

**Example Projects:**
- Your current project: `datagen-skill`
- LangChain SQL Agent
- AutoGPT for data tasks

**Community:**
- Anthropic Discord
- LangChain GitHub Discussions
- Data Engineering Subreddit

---

## Conclusion

You now have a complete guide to building AI agents for data engineering:

1. **Foundation**: Base agent class, configuration, tools
2. **Architecture**: Single-purpose, multi-agent, ReAct patterns
3. **Implementation**: Schema analyzer, test data generator, query optimizer
4. **Advanced**: Tool use, memory, monitoring
5. **Production**: API, Docker, cost tracking
6. **Best Practices**: Testing, security, optimization

**Start simple:**
1. Build schema analyzer (today)
2. Add test data generation (week 1)
3. Add query optimization (week 2)
4. Deploy to production (week 3)
5. Iterate based on feedback

**Key Principles:**
- Validate everything before delivery
- Start with simple agents, compose into complex workflows
- Monitor costs and performance
- Test thoroughly
- Iterate based on real usage

Good luck building your data engineering agents!
