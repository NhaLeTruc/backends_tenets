# What is an AI Skill?

## Official Definition (Anthropic)

**Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks.**

Skills teach Claude how to complete specific tasks in a repeatable way—whether that's creating documents with your company's brand guidelines, analyzing data using your organization's specific workflows, or automating personal tasks.

---

## Core Components of a Skill

### 1. **The Structure**
A skill is simply a folder containing:
- `SKILL.md` file with YAML frontmatter and instructions
- Supporting scripts and resources

### 2. **SKILL.md Format**
```yaml
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Instructions that Claude will follow when this skill is active]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

### 3. **Metadata Requirements**
- `name` - Unique identifier (lowercase, hyphens for spaces)
- `description` - What the skill does and when to use it

### 4. **Content**
The markdown content contains:
- Instructions Claude follows when the skill is active
- Examples of skill usage
- Guidelines and constraints

---

## What Skills Enable

Skills teach Claude **domain-specific knowledge and processes**:

| Category | Examples |
|----------|----------|
| **Creative & Design** | Art generation, music composition, design systems |
| **Development & Technical** | Testing web apps, MCP server generation, code patterns |
| **Enterprise & Communication** | Branding consistency, company workflows, communications |
| **Document Skills** | PDF extraction, DOCX creation, XLSX manipulation, PPTX generation |
| **Data & Analysis** | Organization-specific workflows, analytical processes |

---

## How Skills Work

### Without a Skill
```
You: "Generate test data for my Postgres customers table"
Claude: [generates generic SQL without understanding your schema]
You: [must validate and adjust manually]
```

### With a Skill
```
You: "Generate test data for my Postgres customers table"
Claude: [loads your data-generation skill]
         [applies your organization's patterns]
         [generates realistic, validated data]
         [provides examples matching your standards]
```

---

## Skill vs MCP Server vs Prompt

Understanding the distinction:

### **Prompt** (Lowest level)
- One-off instruction to Claude
- No persistence
- No structure
- Example: "Generate SQL for..."

### **Skill** (Anthropic standard)
- Packaged instructions + guidelines + examples
- Reusable across sessions
- Discoverable and installable
- Can be shared with others
- Follows YAML + Markdown structure

### **MCP Server** (Deep integration)
- Exposes tools/functions to Claude
- Handles authentication and execution
- Operates on your actual systems
- Real-time access to databases, files, APIs
- Example: Read your Postgres schema, validate data, insert records

### **Combination: Skill + MCP Server**
```
Your Skill (instructions, patterns, guidelines)
         ↓
Claude (reasoning)
         ↓
MCP Server (tool execution)
         ↓
Your Systems (actual work)
```

**Example:** Your data-generation skill describes patterns. When activated, Claude uses an MCP server to read your schema, generate matching data, and validate it—all automatically.

---

## Where Skills Live

### **Claude.ai**
- Skills available to paid plans
- Upload custom skills directly
- Skills are available in the conversation

### **Claude Code**
- Install skills as plugins
- Use via Claude Code IDE
- Register plugin marketplace with repositories

### **Claude API**
- Use pre-built Anthropic skills
- Upload custom skills
- Available through API requests

---

## Skill Examples from Anthropic

From `anthropics/skills` repository:

### Document Skills (Production)
- **PDF Skill** - Extract forms, read text, process documents
- **DOCX Skill** - Create, edit, format Word documents  
- **XLSX Skill** - Build, modify Excel spreadsheets
- **PPTX Skill** - Generate presentations

### Example Skills
- `doc-coauthoring` - Collaborative document editing
- Web app testing patterns
- Design system documentation
- Enterprise communication templates

---

## Building Your Own Skill

### Step 1: Define the Task
What specific, repeatable task should Claude learn?
- "Generate realistic test data for Postgres"
- "Create YAML Airflow DAGs matching our patterns"
- "Validate CDC events for schema consistency"

### Step 2: Document Instructions
Write clear instructions in Markdown:
- What the skill does
- When to use it
- Step-by-step guidance
- Key constraints and patterns

### Step 3: Add Examples
Show Claude real examples:
- Input: "Generate 100 customers"
- Expected output: [structured data with your patterns]

### Step 4: Define Guidelines
Set constraints and best practices:
- Data validation rules
- Naming conventions
- Quality standards

### Step 5: Package as Skill
```
my-data-generation-skill/
├── SKILL.md          # Your instructions + metadata
├── templates/        # Example schemas, patterns
├── guidelines/       # Validation rules, best practices
└── examples/         # Real examples of good output
```

### Step 6: Activate & Test
- Upload to Claude
- Test in your domain
- Iterate on instructions

---

## Real-World Pattern: Data Generation Skill

### What Your Skill Teaches Claude

**When this skill is active, follow these patterns:**

1. **Understand the schema** - Ask for table DDL or structure
2. **Identify constraints** - Foreign keys, unique fields, data types
3. **Generate realistic data** - Names, emails, timestamps, amounts match real patterns
4. **Maintain relationships** - Orders reference valid customers, items reference valid products
5. **Include edge cases** - Null values, boundary conditions, error scenarios
6. **Validate before delivering** - Check constraint compliance

### Your Skill Instruction Example

```yaml
---
name: test-data-generation
description: Generate production-like test data for PostgreSQL databases with realistic patterns and constraint compliance
---

# Test Data Generation Skill

When generating test data, follow these practices:

## Understanding the Schema
1. Always ask for or inspect the table DDL
2. Identify all constraints (primary key, foreign key, unique, not null)
3. Understand data types and their ranges

## Realistic Data Patterns
- Email addresses: Use realistic domains and patterns
- Names: Vary from diverse name databases
- Timestamps: Maintain chronological order
- Amounts: Use realistic ranges for your domain
- IDs: Generate valid references to existing records

## Relationship Integrity
- Foreign key values must reference existing primary keys
- Cascade deletes respected
- Temporal ordering preserved

## Examples
[Show 2-3 examples of good generated data]

## Guidelines
- Always validate before presenting
- Include edge cases for testing
- Report data volume and characteristics
```

---

## Key Takeaway

**A Claude Skill is not:**
- Just a prompt
- A separate tool you install
- An MCP server
- A code library

**A Claude Skill is:**
- **Reusable instructions** that teach Claude how to do specific tasks
- **Packaged domain knowledge** (patterns, examples, guidelines)
- **Discoverable and shareable** - via Claude.ai, Claude Code, API
- **Stateful** - persists knowledge across conversations
- **Structured** - follows Anthropic's SKILL.md specification

**To use a skill:** Activate it in Claude, and Claude automatically applies the instructions, examples, and guidelines to improve its output on that task type.

---

## Resources

- [What are skills? (Anthropic Support)](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Skills API Quickstart](https://docs.claude.com/en/api/skills-guide#creating-a-skill)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Equipping agents for the real world with Agent Skills](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
