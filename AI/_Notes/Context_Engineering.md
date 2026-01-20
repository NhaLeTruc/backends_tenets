# Context & Prompt Engineering

## Table of Contents

- [Context \& Prompt Engineering](#context--prompt-engineering)
  - [Table of Contents](#table-of-contents)
  - [Sub-topics](#sub-topics)
  - [Explanation](#explanation)
    - [Context Engineering for Claude Code](#context-engineering-for-claude-code)
      - [CLAUDE.md: Project Context File](#claudemd-project-context-file)
      - [Dynamic Context with MCP Servers](#dynamic-context-with-mcp-servers)
      - [Conversation History Management](#conversation-history-management)
      - [Optimizing Tool Result Context](#optimizing-tool-result-context)
      - [Structured Prompting for Claude Code](#structured-prompting-for-claude-code)
      - [Context Injection via Hooks](#context-injection-via-hooks)
      - [Memory MCP for Persistent Context](#memory-mcp-for-persistent-context)
      - [Context Engineering Best Practices Summary](#context-engineering-best-practices-summary)
  - [Guidelines \& Best Practices](#guidelines--best-practices)
  - [Resources](#resources)

## Sub-topics

- Context engineering
- Prompt compression
- Structured prompting
- Information prioritization in prompting
- Dynamic context adjustment
- Sliding window
- Context sharing/state management
- Context engineering for Claude Code

## Explanation

**Context engineering** is the systematic design of what information to include in prompts and how to structure it for optimal LLM performance.

**Prompt compression** reduces token usage while preserving semantic content using techniques like:

- LLMLingua (Microsoft)
- Selective context removal
- Summary-based compression

**Structured prompting** uses consistent formats (XML tags, markdown, JSON schemas) to improve parsing reliability and model understanding.

**Information prioritization** places critical information at the beginning or end of prompts (primacy/recency effects).

**Sliding window** manages context by keeping recent tokens while discarding older ones, essential for long conversations.

**Dynamic context adjustment** adaptively includes/excludes context based on relevance to the current query.

---

### Context Engineering for Claude Code

Context engineering in Claude Code involves strategically managing what information Claude sees during coding sessions. Effective context engineering improves response quality, reduces token costs, and enables Claude to work on larger codebases.

**Claude Code Context Sources**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Code Context Window                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   System    │  │ Conversation│  │     Tool Results        │  │
│  │   Prompt    │  │   History   │  │  (file reads, searches) │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  CLAUDE.md  │  │    MCP      │  │    User Messages        │  │
│  │  (Project)  │  │  Resources  │  │    & Attachments        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Context Budget Allocation**:

| Source | Typical % | Optimization Strategy |
| ------ | --------- | --------------------- |
| System prompt | 5-10% | Keep focused, use CLAUDE.md for project-specific |
| CLAUDE.md | 5-15% | Concise patterns, not full documentation |
| Conversation history | 20-40% | Auto-summarized by Claude Code |
| Tool results | 30-50% | Request specific files, use targeted searches |
| User message | 5-10% | Be specific, reference files by path |

---

#### CLAUDE.md: Project Context File

The `CLAUDE.md` file provides persistent project-specific context that's automatically loaded for every conversation.

**Location Hierarchy** (merged in order):

```txt
~/.claude/CLAUDE.md          # Global defaults (all projects)
~/work/CLAUDE.md             # Organization defaults
~/work/myproject/CLAUDE.md   # Project-specific (highest priority)
```

**Effective CLAUDE.md Structure**:

```markdown
# Project: MyApp

## Tech Stack
- Frontend: React 18, TypeScript, Tailwind CSS
- Backend: Node.js, Express, PostgreSQL
- Testing: Vitest, Playwright

## Architecture
- `/src/components/` - React components (use functional + hooks)
- `/src/api/` - API routes (RESTful, use Zod validation)
- `/src/db/` - Database queries (use Kysely query builder)
- `/src/utils/` - Shared utilities

## Code Conventions
- Use named exports, not default exports
- Prefer `interface` over `type` for object shapes
- Error handling: use Result<T, E> pattern from `@/utils/result`
- All API endpoints return `{ data, error, meta }` shape

## Common Commands
- `npm run dev` - Start development server
- `npm run test` - Run tests
- `npm run db:migrate` - Run migrations

## Important Files
- `src/config/env.ts` - Environment configuration
- `src/middleware/auth.ts` - Authentication middleware
- `src/db/schema.ts` - Database schema definitions

## Gotchas
- Always use `getServerSession()` not `getSession()` in API routes
- PostgreSQL uses snake_case, TypeScript uses camelCase (mapper in db/utils)
- Rate limiter is per-user, not per-IP (see middleware/rateLimit.ts)
```

**CLAUDE.md Anti-patterns to Avoid**:

| Anti-pattern | Problem | Better Approach |
| ------------ | ------- | --------------- |
| Full API documentation | Wastes tokens | Link to docs, summarize key endpoints |
| Complete type definitions | Redundant (Claude reads files) | Note unusual patterns only |
| Step-by-step tutorials | Too verbose | Brief commands and gotchas |
| Outdated information | Causes errors | Keep current or remove |
| Generic best practices | Claude already knows | Project-specific conventions only |

---

#### Dynamic Context with MCP Servers

MCP servers can provide dynamic, query-relevant context instead of static file content.

**Context-Aware MCP Server**:

```typescript
// context-mcp-server.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import * as fs from "fs";
import * as path from "path";

const server = new Server(
  { name: "context-server", version: "1.0.0" },
  { capabilities: { tools: {}, resources: {} } }
);

// Provide context as a resource that updates dynamically
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: "context://project/summary",
      name: "Project Summary",
      description: "Dynamic project context based on recent changes",
      mimeType: "text/markdown",
    },
    {
      uri: "context://project/recent-files",
      name: "Recently Modified Files",
      description: "Files changed in the last 24 hours",
      mimeType: "text/markdown",
    },
  ],
}));

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === "context://project/summary") {
    const summary = await generateProjectSummary();
    return {
      contents: [{ uri, mimeType: "text/markdown", text: summary }],
    };
  }

  if (uri === "context://project/recent-files") {
    const recentFiles = await getRecentlyModifiedFiles();
    return {
      contents: [{ uri, mimeType: "text/markdown", text: recentFiles }],
    };
  }

  throw new Error("Unknown resource");
});

async function generateProjectSummary(): Promise<string> {
  // Analyze package.json, git status, etc.
  const packageJson = JSON.parse(fs.readFileSync("package.json", "utf-8"));
  const gitBranch = execSync("git branch --show-current").toString().trim();
  const uncommitted = execSync("git status --porcelain").toString();

  return `## Current Project State
- **Branch**: ${gitBranch}
- **Package**: ${packageJson.name}@${packageJson.version}
- **Uncommitted changes**: ${uncommitted ? "Yes" : "No"}

## Key Dependencies
${Object.entries(packageJson.dependencies || {})
  .slice(0, 10)
  .map(([k, v]) => `- ${k}: ${v}`)
  .join("\n")}
`;
}

async function getRecentlyModifiedFiles(): Promise<string> {
  const result = execSync(
    'find . -type f -mtime -1 -not -path "*/node_modules/*" -not -path "*/.git/*"'
  )
    .toString()
    .split("\n")
    .filter(Boolean)
    .slice(0, 20);

  return `## Recently Modified Files (24h)\n${result.map((f) => `- ${f}`).join("\n")}`;
}

const transport = new StdioServerTransport();
await server.connect(transport);
```

---

#### Conversation History Management

Claude Code automatically manages conversation history, but you can optimize it.

**How Claude Code Handles Long Conversations**:

```
┌─────────────────────────────────────────────────────────────┐
│                   Conversation Flow                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Turn 1-5: Full messages retained                           │
│       ↓                                                      │
│  Turn 6+: Older turns compressed/summarized                 │
│       ↓                                                      │
│  Context limit approached: Aggressive summarization         │
│       ↓                                                      │
│  New conversation: Start fresh with CLAUDE.md context       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Strategies for Long Sessions**:

| Strategy | When to Use | How |
| -------- | ----------- | --- |
| **Explicit summaries** | Before complex task | "Let me summarize what we've done..." |
| **Fresh conversation** | Context pollution | Start new chat, reference previous work |
| **Checkpoint files** | Multi-day projects | Save state to a `PROGRESS.md` file |
| **Scoped requests** | Large codebase | "Focus only on src/auth/" |

**Creating Context Checkpoints**:

```markdown
<!-- PROGRESS.md - Update periodically -->

# Implementation Progress

## Completed
- [x] User authentication (src/auth/)
- [x] Database schema (src/db/schema.ts)
- [x] API routes for users (src/api/users/)

## In Progress
- [ ] Payment integration
  - Stripe SDK installed
  - Webhook endpoint created at src/api/webhooks/stripe.ts
  - TODO: Implement subscription logic

## Decisions Made
- Using Stripe for payments (not PayPal) - better API
- JWT tokens stored in httpOnly cookies (not localStorage)
- Rate limiting: 100 req/min per user

## Open Questions
- Should we support team billing?
- Redis for session store or PostgreSQL?
```

Reference in conversation: "Check PROGRESS.md for current state, then continue with payment integration."

---

#### Optimizing Tool Result Context

Tool results (file reads, searches) consume significant context. Optimize them.

**File Reading Strategies**:

```typescript
// Instead of reading entire files, be specific

// ❌ Bad: Reads entire large file
"Read src/components/Dashboard.tsx"

// ✅ Good: Read specific section
"Read lines 50-100 of src/components/Dashboard.tsx"

// ✅ Good: Search then read
"Search for 'handleSubmit' in src/components/, then read that function"
```

**Search Optimization**:

```typescript
// ❌ Bad: Broad search fills context with irrelevant results
"Search for 'user' in the codebase"

// ✅ Good: Targeted search
"Search for 'userAuthentication' in src/auth/"

// ✅ Good: File type filtering
"Search for 'interface User' in *.ts files"

// ✅ Good: Specific pattern
"Find where UserService is instantiated"
```

**Glob Patterns for Focused Context**:

```typescript
// Get only relevant files
"List all *.test.ts files in src/auth/"
"Find all files named 'index.ts' in src/components/"
"Show package.json files (there might be multiple)"
```

---

#### Structured Prompting for Claude Code

Use structured formats to improve Claude's understanding and response quality.

**XML Tags for Complex Requests**:

```xml
<task>
Implement a rate limiter middleware for the Express API.
</task>

<requirements>
- Limit: 100 requests per minute per user
- Use Redis for distributed counting
- Return 429 status with Retry-After header when exceeded
- Bypass for admin users
</requirements>

<constraints>
- Must work with existing auth middleware (see src/middleware/auth.ts)
- Don't modify existing route files
- Use the existing Redis client from src/lib/redis.ts
</constraints>

<output>
Create the middleware file and show how to apply it to routes.
</output>
```

**Template for Bug Reports**:

```xml
<bug>
Payment webhook fails silently for subscription renewals
</bug>

<reproduction>
1. Create a subscription via /api/subscribe
2. Wait for Stripe to send renewal webhook
3. Check logs - no entry for webhook receipt
</reproduction>

<expected>
Webhook should be logged and subscription extended in database.
</expected>

<relevant_files>
- src/api/webhooks/stripe.ts (webhook handler)
- src/services/subscription.ts (subscription logic)
- src/db/queries/subscriptions.ts (database queries)
</relevant_files>
```

**Template for Feature Requests**:

```xml
<feature>
Add dark mode toggle to the settings page
</feature>

<acceptance_criteria>
- Toggle switch in Settings > Appearance
- Preference saved to user profile (database)
- Applied immediately without page reload
- Persists across sessions
</acceptance_criteria>

<design_notes>
- Use CSS custom properties for theming
- Match existing toggle component style (see src/components/ui/Toggle.tsx)
</design_notes>
```

---

#### Context Injection via Hooks

Use Claude Code hooks to inject context automatically based on the task.

**Pre-tool Hook for Context Injection**:

```javascript
// .claude/hooks/pre-tool.js
module.exports = async function preToolHook(context) {
  const { toolName, toolArgs, conversationHistory } = context;

  // Inject relevant context before file operations
  if (toolName === "read_file" || toolName === "edit_file") {
    const filePath = toolArgs.path;

    // Add architecture context for certain directories
    if (filePath.includes("/api/")) {
      return {
        injectContext: `
Note: API routes follow these conventions:
- Use Zod for request validation
- Return { data, error, meta } shape
- Wrap handlers with asyncHandler() for error handling
- See src/api/_template.ts for reference
`,
      };
    }

    if (filePath.includes("/components/")) {
      return {
        injectContext: `
Note: Components follow these patterns:
- Functional components with TypeScript
- Props interface named {ComponentName}Props
- Use cn() utility for className merging
- Colocate styles in {component}.module.css
`,
      };
    }
  }

  return null;
};
```

**Post-message Hook for Summary Injection**:

```javascript
// .claude/hooks/post-message.js
const fs = require("fs");

module.exports = async function postMessageHook(context) {
  const { messageCount } = context;

  // Every 10 messages, remind about project state
  if (messageCount % 10 === 0) {
    const progress = fs.existsSync("PROGRESS.md")
      ? fs.readFileSync("PROGRESS.md", "utf-8")
      : null;

    if (progress) {
      return {
        injectReminder: `
Checkpoint reminder - Current project state:
${progress.slice(0, 500)}...
`,
      };
    }
  }

  return null;
};
```

---

#### Memory MCP for Persistent Context

Use a memory MCP server to maintain context across conversations.

**Memory MCP Configuration**:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE": "~/.claude/memory/project-memory.json"
      }
    }
  }
}
```

**Using Memory for Context**:

```markdown
# In conversation:

"Remember that we decided to use Stripe for payments instead of PayPal"

# Later, in a new conversation:

"What payment provider did we decide to use?"
# Claude retrieves from memory: "Stripe"
```

**Custom Memory MCP with Semantic Search**:

```python
# memory_mcp_server.py
import json
from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer
import numpy as np
from mcp.server import Server
from mcp.server.stdio import stdio_server

MEMORY_FILE = Path.home() / ".claude" / "memory" / "semantic_memory.json"
model = SentenceTransformer("all-MiniLM-L6-v2")
server = Server("semantic-memory")

def load_memories() -> list[dict]:
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return []

def save_memories(memories: list[dict]):
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(memories, indent=2))

@server.list_tools()
async def list_tools():
    return [
        {
            "name": "remember",
            "description": "Store information for later recall",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["content"]
            }
        },
        {
            "name": "recall",
            "description": "Retrieve relevant memories",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        }
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    memories = load_memories()

    if name == "remember":
        content = arguments["content"]
        embedding = model.encode(content).tolist()

        memories.append({
            "content": content,
            "embedding": embedding,
            "tags": arguments.get("tags", []),
            "timestamp": datetime.now().isoformat()
        })
        save_memories(memories)

        return [{"type": "text", "text": f"Remembered: {content[:100]}..."}]

    elif name == "recall":
        query = arguments["query"]
        limit = arguments.get("limit", 5)

        query_embedding = model.encode(query)

        # Compute similarities
        scored = []
        for mem in memories:
            similarity = np.dot(query_embedding, mem["embedding"])
            scored.append((similarity, mem))

        # Return top matches
        scored.sort(reverse=True, key=lambda x: x[0])
        results = scored[:limit]

        if not results:
            return [{"type": "text", "text": "No relevant memories found."}]

        output = "\n\n".join([
            f"**Memory** (relevance: {score:.2f})\n{mem['content']}"
            for score, mem in results
        ])

        return [{"type": "text", "text": output}]

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

#### Context Engineering Best Practices Summary

| Practice | Implementation |
| -------- | -------------- |
| **Layer context appropriately** | Global → Org → Project CLAUDE.md |
| **Keep CLAUDE.md concise** | Conventions and gotchas, not documentation |
| **Use checkpoints** | PROGRESS.md for multi-session work |
| **Scope requests** | Specify directories/files to focus on |
| **Leverage MCP resources** | Dynamic context over static files |
| **Inject via hooks** | Automatic context based on actions |
| **Use semantic memory** | Persist decisions across conversations |
| **Structure complex requests** | XML tags for clarity |
| **Start fresh when needed** | New conversation > polluted context |
| **Reference, don't repeat** | "See file X" instead of pasting content |

## Guidelines & Best Practices

1. Place most important instructions at the beginning AND end of prompts
2. Use consistent delimiters (XML tags recommended by Anthropic)
3. Provide examples (few-shot) for complex tasks
4. Be explicit about output format expectations
5. Test prompt variations systematically
6. Monitor context window utilization to avoid truncation

## Resources

- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [OpenAI Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- [LLMLingua Prompt Compression](https://github.com/microsoft/LLMLingua)
- [DSPY Framework](https://dspy-docs.vercel.app/)
