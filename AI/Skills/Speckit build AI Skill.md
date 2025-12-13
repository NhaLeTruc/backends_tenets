# How Speckit Helps Build Anthropic AI Skills

## The Connection

**Speckit** = Specification-driven development methodology  
**AI Skill** = A packaged set of instructions + examples + guidelines

Speckit helps you **build the specification that becomes your skill**.

---

## Using Speckit to Build an AI Skill

### Workflow: Speckit → AI Skill

```
/constitution  ──→  Skill's core purpose & constraints
        ↓
/specify       ──→  Detailed instructions & examples  
        ↓
/clarify       ──→  Validate instructions are unambiguous
        ↓
/plan          ──→  Structure skill folder & content
        ↓
/task          ──→  Break into specific creation tasks
        ↓
/analyze       ──→  Ensure skill is complete & consistent
        ↓
/implement     ──→  Build & test the actual skill
```

---

## Step-by-Step: Building a Data Generation Skill

### **1. /constitution** - Define Skill Principles

```
/constitution
Build principles for a Claude skill that generates realistic test data.

Principles:
- Generated data must respect all database constraints
- Data should be production-like (realistic patterns)
- Relationships must be maintained (referential integrity)
- Include edge cases for testing
- Always validate before delivery
```

**Output:** Clear principles that become your skill's core guidelines

### **2. /specify** - Create Detailed Specifications

```
/specify
Create detailed specification for a test-data-generation skill.

Include:
- What the skill teaches Claude
- When to use it (data generation tasks)
- Required inputs (schema, volume, constraints)
- Expected outputs (SQL, JSON, CSV)
- Key patterns Claude should follow
- Examples of good vs bad output
```

**Output:** Detailed spec that becomes your `SKILL.md` instructions

### **3. /clarify** - De-risk the Specification

```
/clarify
Review the test-data-generation skill specification.

Questions to answer:
- Are the instructions clear enough for Claude to follow?
- Are the examples representative?
- Are edge cases well-defined?
- Can users activate and use this skill immediately?
- What ambiguities remain?
```

**Output:** Refined, unambiguous instructions ready for Claude

### **4. /plan** - Organize Skill Structure

```
/plan
Plan how to structure the test-data-generation skill.

Include:
- Folder organization
- SKILL.md content sections
- Supporting files (templates, examples, guidelines)
- Where to include real examples from user's databases
- How to organize instructions by complexity
```

**Output:** Clear structure for your skill folder

### **5. /task** - Break Into Actionable Tasks

```
/task
Generate tasks for building the test-data-generation skill.

Tasks should cover:
- Writing SKILL.md with frontmatter
- Creating instruction sections
- Building example templates
- Documenting guidelines
- Testing the skill
```

**Output:** Specific, actionable tasks to complete the skill

### **6. /analyze** - Validate Completeness

```
/analyze
Analyze the test-data-generation skill for:
- Consistency: Do instructions align with examples?
- Completeness: Are all necessary elements present?
- Clarity: Can Claude understand and execute?
- Usefulness: Does it solve real user problems?
```

**Output:** Gaps identified, quality validated

### **7. /implement** - Build the Skill

```
/implement
Build the test-data-generation skill based on the plan.

Create:
- SKILL.md with metadata and instructions
- Example templates
- Guidelines for users
- Test cases
```

**Output:** Production-ready skill

---

## Real Skill Built This Way

Using Speckit, you'd create something like:

```
test-data-generation-skill/
├── SKILL.md
│   ├── Frontmatter (name, description from /constitution)
│   ├── Instructions (detailed from /specify)
│   ├── Examples (validated from /clarify)
│   └── Guidelines (structured from /plan)
├── templates/
│   ├── postgres-customer-data.sql
│   ├── mongodb-orders.json
│   └── csv-transactions.csv
├── examples/
│   ├── good-output-1.sql
│   ├── good-output-2.json
│   └── edge-cases.md
└── validation-rules/
    ├── referential-integrity.md
    ├── data-patterns.md
    └── edge-cases.md
```

---

## Why This Works So Well

| Speckit Phase | Why It Helps Build Skills |
|---------------|---------------------------|
| **/constitution** | Forces you to define the skill's core purpose & constraints |
| **/specify** | Creates the detailed instructions Claude needs |
| **/clarify** | Ensures your instructions are unambiguous for Claude |
| **/plan** | Organizes content in the SKILL.md structure |
| **/task** | Breaks large skill-building work into steps |
| **/analyze** | Validates the skill is complete & consistent before release |
| **/implement** | Builds the actual skill artifact |

---

## The Key Insight

**Speckit is essentially a methodology for building the specification that becomes your AI Skill.**

Without Speckit, you might build a skill haphazardly:
- Unclear instructions
- Inconsistent examples
- Missing guidelines

With Speckit:
- Clear, validated instructions
- Consistent, representative examples
- Complete guidelines
- Well-organized structure

---

## Practical Example: Data Generation Skill Workflow

You could literally:

1. Open Speckit in VS Code
2. Run `/constitution` to define skill principles
3. Run `/specify` to detail the skill instructions
4. Run `/clarify` to validate they're clear
5. Run `/plan` to organize the skill structure
6. Run `/implement` to generate the skill folder
7. Upload to Claude → Activate the skill → Done

**The Speckit workflow produces a high-quality AI Skill as its output.**

---

## Summary

| Aspect | How Speckit Helps |
|--------|-------------------|
| **Clarity** | `/constitution` + `/clarify` ensure unambiguous instructions |
| **Completeness** | `/specify` + `/analyze` validate nothing is missing |
| **Structure** | `/plan` organizes the SKILL.md and supporting files |
| **Quality** | Each phase validates against the previous, ensuring consistency |
| **Actionability** | `/task` breaks skill creation into concrete steps |
| **Output** | Result is a production-ready AI Skill folder ready to upload |

Speckit transforms vague ideas into high-quality, structured AI Skills through its systematic specification-driven process.
