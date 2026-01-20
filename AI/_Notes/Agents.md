# AI Agents & Multi-Agent Systems

## Table of Contents

- [AI Agents \& Multi-Agent Systems](#ai-agents--multi-agent-systems)
  - [Table of Contents](#table-of-contents)
  - [Sub-topics](#sub-topics)
  - [Explanation](#explanation)
    - [Setting Up Agents and Sub-agents for Claude Code](#setting-up-agents-and-sub-agents-for-claude-code)
      - [Claude Agent SDK Overview](#claude-agent-sdk-overview)
      - [Building a Custom Agent (TypeScript)](#building-a-custom-agent-typescript)
      - [Implementing Sub-agents](#implementing-sub-agents)
      - [Building a Multi-Agent System](#building-a-multi-agent-system)
      - [Python Implementation](#python-implementation)
      - [Integrating Custom Agents with Claude Code](#integrating-custom-agents-with-claude-code)
      - [Agent Communication Patterns](#agent-communication-patterns)
      - [Best Practices for Claude Code Agents](#best-practices-for-claude-code-agents)
  - [Guidelines \& Best Practices](#guidelines--best-practices)
  - [Resources](#resources)

## Sub-topics

- Agents
- Agent unified memory
- A2A (Agent-to-Agent protocol)
- Agent-to-agent handoff
- Multi-agentic frameworks
- Subagents
- Agent routers
- HuggingFace's smolagents
- Agents and sub-agents for Claude Code

## Explanation

**AI Agents** are autonomous systems that use LLMs to reason, plan, and execute tasks using tools. They operate in loops: observe → think → act → observe.

**Agent unified memory** provides persistent context across interactions, including:

- Short-term (conversation context)
- Long-term (user preferences, past interactions)
- Episodic (specific past events)

**A2A (Agent-to-Agent)** is Google's protocol for agent interoperability, enabling agents from different frameworks to communicate.

**Agent handoff** patterns manage task delegation between specialized agents (e.g., triage agent → specialist agent).

**Agent routers** intelligently direct requests to appropriate specialized agents based on intent classification.

**smolagents** is HuggingFace's lightweight agent framework focused on simplicity and code-based tool use.

---

### Setting Up Agents and Sub-agents for Claude Code

Claude Code supports a powerful agent architecture through the Claude Agent SDK, allowing you to build custom agents and orchestrate sub-agents for complex workflows.

**Agent Architecture in Claude Code**:

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Claude Agent                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   Agent Loop                         │    │
│  │    ┌──────────┐    ┌──────────┐    ┌──────────┐     │    │
│  │    │  Parse   │───▶│  Think   │───▶│  Act     │     │    │
│  │    │  Input   │    │  (LLM)   │    │  (Tools) │     │    │
│  │    └──────────┘    └──────────┘    └──────────┘     │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                 │
│              ┌─────────────┼─────────────┐                  │
│              ▼             ▼             ▼                  │
│      ┌───────────┐  ┌───────────┐  ┌───────────┐           │
│      │ Sub-agent │  │ Sub-agent │  │ Sub-agent │           │
│      │  (Code)   │  │  (Search) │  │  (Test)   │           │
│      └───────────┘  └───────────┘  └───────────┘           │
└─────────────────────────────────────────────────────────────┘
```

**When to Use Sub-agents**:

| Scenario | Approach | Example |
| -------- | -------- | ------- |
| **Specialized tasks** | Dedicated sub-agent | Code review agent, test runner agent |
| **Parallel work** | Multiple sub-agents | Search docs + analyze code simultaneously |
| **Complex reasoning** | Chain of agents | Planner → Implementer → Reviewer |
| **Domain expertise** | Expert sub-agents | Security auditor, performance optimizer |

---

#### Claude Agent SDK Overview

The Claude Agent SDK provides the foundation for building custom agents that integrate with Claude Code.

**Installation**:

```bash
# Install the SDK
npm install @anthropic-ai/claude-code-sdk

# Or with pip for Python
pip install claude-code-sdk
```

**Core Concepts**:

| Concept | Description |
| ------- | ----------- |
| **Agent** | Autonomous entity with tools and instructions |
| **Tool** | Function the agent can invoke |
| **Sub-agent** | Specialized agent spawned by parent agent |
| **Context** | Shared state and conversation history |
| **Hooks** | Lifecycle callbacks for customization |

---

#### Building a Custom Agent (TypeScript)

**Basic Agent Structure**:

```typescript
// my-agent.ts
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

interface AgentConfig {
  name: string;
  systemPrompt: string;
  tools: Anthropic.Tool[];
  maxTurns?: number;
}

class Agent {
  private config: AgentConfig;
  private conversationHistory: Anthropic.MessageParam[] = [];

  constructor(config: AgentConfig) {
    this.config = config;
  }

  async run(userMessage: string): Promise<string> {
    this.conversationHistory.push({
      role: "user",
      content: userMessage,
    });

    let turns = 0;
    const maxTurns = this.config.maxTurns || 10;

    while (turns < maxTurns) {
      const response = await client.messages.create({
        model: "claude-sonnet-4-20250514",
        max_tokens: 4096,
        system: this.config.systemPrompt,
        tools: this.config.tools,
        messages: this.conversationHistory,
      });

      // Handle response
      if (response.stop_reason === "end_turn") {
        const textContent = response.content.find((c) => c.type === "text");
        return textContent?.text || "";
      }

      if (response.stop_reason === "tool_use") {
        // Process tool calls
        const toolResults = await this.processToolCalls(response.content);
        this.conversationHistory.push({
          role: "assistant",
          content: response.content,
        });
        this.conversationHistory.push({
          role: "user",
          content: toolResults,
        });
      }

      turns++;
    }

    return "Max turns reached";
  }

  private async processToolCalls(
    content: Anthropic.ContentBlock[]
  ): Promise<Anthropic.ToolResultBlockParam[]> {
    const results: Anthropic.ToolResultBlockParam[] = [];

    for (const block of content) {
      if (block.type === "tool_use") {
        const result = await this.executeTool(block.name, block.input);
        results.push({
          type: "tool_result",
          tool_use_id: block.id,
          content: result,
        });
      }
    }

    return results;
  }

  private async executeTool(name: string, input: unknown): Promise<string> {
    // Implement tool execution logic
    throw new Error(`Tool ${name} not implemented`);
  }
}
```

**Defining Tools**:

```typescript
// tools.ts
import Anthropic from "@anthropic-ai/sdk";

export const codeAnalysisTool: Anthropic.Tool = {
  name: "analyze_code",
  description: "Analyze code for issues, patterns, and improvements",
  input_schema: {
    type: "object" as const,
    properties: {
      code: {
        type: "string",
        description: "The code to analyze",
      },
      language: {
        type: "string",
        description: "Programming language",
      },
      focus: {
        type: "string",
        enum: ["security", "performance", "style", "all"],
        description: "Analysis focus area",
      },
    },
    required: ["code", "language"],
  },
};

export const fileOperationsTool: Anthropic.Tool = {
  name: "file_operations",
  description: "Read, write, or modify files",
  input_schema: {
    type: "object" as const,
    properties: {
      operation: {
        type: "string",
        enum: ["read", "write", "append", "delete"],
      },
      path: {
        type: "string",
        description: "File path",
      },
      content: {
        type: "string",
        description: "Content for write/append operations",
      },
    },
    required: ["operation", "path"],
  },
};

export const spawnSubagentTool: Anthropic.Tool = {
  name: "spawn_subagent",
  description: "Spawn a specialized sub-agent for a specific task",
  input_schema: {
    type: "object" as const,
    properties: {
      agentType: {
        type: "string",
        enum: ["code_reviewer", "test_writer", "docs_generator", "security_auditor"],
        description: "Type of sub-agent to spawn",
      },
      task: {
        type: "string",
        description: "Task description for the sub-agent",
      },
      context: {
        type: "object",
        description: "Additional context to pass to the sub-agent",
      },
    },
    required: ["agentType", "task"],
  },
};
```

---

#### Implementing Sub-agents

**Sub-agent Factory Pattern**:

```typescript
// subagents.ts
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

interface SubagentResult {
  success: boolean;
  output: string;
  artifacts?: Record<string, unknown>;
}

const SUBAGENT_CONFIGS: Record<
  string,
  { systemPrompt: string; tools: Anthropic.Tool[] }
> = {
  code_reviewer: {
    systemPrompt: `You are a code review specialist. Analyze code for:
- Logic errors and bugs
- Security vulnerabilities
- Performance issues
- Code style and best practices
- Potential edge cases

Provide specific, actionable feedback with line references.`,
    tools: [
      /* code analysis tools */
    ],
  },

  test_writer: {
    systemPrompt: `You are a test writing specialist. Create comprehensive tests including:
- Unit tests for individual functions
- Integration tests for component interactions
- Edge case coverage
- Mock setup for external dependencies

Use the project's existing test framework and patterns.`,
    tools: [
      /* file and test tools */
    ],
  },

  security_auditor: {
    systemPrompt: `You are a security auditor. Check for:
- OWASP Top 10 vulnerabilities
- Injection attacks (SQL, command, XSS)
- Authentication/authorization issues
- Sensitive data exposure
- Security misconfigurations

Rate findings by severity (Critical, High, Medium, Low).`,
    tools: [
      /* security analysis tools */
    ],
  },

  docs_generator: {
    systemPrompt: `You are a documentation specialist. Generate:
- Function/method documentation
- API documentation
- README updates
- Architecture diagrams (as mermaid)
- Usage examples

Match the project's existing documentation style.`,
    tools: [
      /* file tools */
    ],
  },
};

export async function spawnSubagent(
  agentType: string,
  task: string,
  context?: Record<string, unknown>
): Promise<SubagentResult> {
  const config = SUBAGENT_CONFIGS[agentType];
  if (!config) {
    return { success: false, output: `Unknown agent type: ${agentType}` };
  }

  const contextStr = context ? `\n\nContext:\n${JSON.stringify(context, null, 2)}` : "";

  try {
    const response = await client.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 4096,
      system: config.systemPrompt,
      tools: config.tools,
      messages: [
        {
          role: "user",
          content: `${task}${contextStr}`,
        },
      ],
    });

    // Process response (simplified - real implementation needs tool loop)
    const textContent = response.content.find((c) => c.type === "text");

    return {
      success: true,
      output: textContent?.text || "No output",
    };
  } catch (error) {
    return {
      success: false,
      output: `Sub-agent error: ${error}`,
    };
  }
}
```

---

#### Building a Multi-Agent System

**Orchestrator Pattern**:

```typescript
// orchestrator.ts
import { spawnSubagent } from "./subagents";

interface TaskPlan {
  steps: {
    id: string;
    agentType: string;
    task: string;
    dependsOn: string[];
  }[];
}

class AgentOrchestrator {
  private results: Map<string, SubagentResult> = new Map();

  async executePlan(plan: TaskPlan): Promise<Map<string, SubagentResult>> {
    const completed = new Set<string>();
    const pending = [...plan.steps];

    while (pending.length > 0) {
      // Find steps ready to execute (dependencies satisfied)
      const ready = pending.filter((step) =>
        step.dependsOn.every((dep) => completed.has(dep))
      );

      if (ready.length === 0 && pending.length > 0) {
        throw new Error("Circular dependency detected");
      }

      // Execute ready steps in parallel
      const executions = ready.map(async (step) => {
        // Gather context from dependencies
        const context: Record<string, unknown> = {};
        for (const dep of step.dependsOn) {
          context[dep] = this.results.get(dep);
        }

        const result = await spawnSubagent(step.agentType, step.task, context);
        this.results.set(step.id, result);
        completed.add(step.id);

        // Remove from pending
        const index = pending.findIndex((p) => p.id === step.id);
        pending.splice(index, 1);
      });

      await Promise.all(executions);
    }

    return this.results;
  }
}

// Example usage
const plan: TaskPlan = {
  steps: [
    {
      id: "analyze",
      agentType: "code_reviewer",
      task: "Review the authentication module for issues",
      dependsOn: [],
    },
    {
      id: "security",
      agentType: "security_auditor",
      task: "Audit authentication for security vulnerabilities",
      dependsOn: [],
    },
    {
      id: "tests",
      agentType: "test_writer",
      task: "Write tests based on review findings",
      dependsOn: ["analyze"],
    },
    {
      id: "docs",
      agentType: "docs_generator",
      task: "Update documentation based on all findings",
      dependsOn: ["analyze", "security", "tests"],
    },
  ],
};
```

---

#### Python Implementation

**Agent with Sub-agents (Python)**:

```python
# agent.py
import anthropic
from dataclasses import dataclass
from typing import Any
import asyncio

client = anthropic.Anthropic()

@dataclass
class SubagentConfig:
    name: str
    system_prompt: str
    tools: list[dict]

SUBAGENT_REGISTRY: dict[str, SubagentConfig] = {
    "code_reviewer": SubagentConfig(
        name="Code Reviewer",
        system_prompt="""You are a code review expert. Analyze code for:
- Bugs and logic errors
- Security vulnerabilities
- Performance issues
- Best practices violations
Provide specific, actionable feedback.""",
        tools=[]
    ),
    "test_writer": SubagentConfig(
        name="Test Writer",
        system_prompt="""You are a test writing specialist.
Create comprehensive unit and integration tests.
Follow the project's testing conventions.""",
        tools=[]
    ),
}

class Agent:
    def __init__(
        self,
        system_prompt: str,
        tools: list[dict] | None = None,
        max_turns: int = 10
    ):
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.max_turns = max_turns
        self.history: list[dict] = []

    async def run(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})

        for _ in range(self.max_turns):
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=self.system_prompt,
                tools=self.tools,
                messages=self.history
            )

            if response.stop_reason == "end_turn":
                text = next(
                    (c.text for c in response.content if c.type == "text"),
                    ""
                )
                return text

            if response.stop_reason == "tool_use":
                self.history.append({
                    "role": "assistant",
                    "content": response.content
                })

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = await self.execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                self.history.append({"role": "user", "content": tool_results})

        return "Max turns reached"

    async def execute_tool(self, name: str, input_data: dict) -> str:
        if name == "spawn_subagent":
            return await self.spawn_subagent(
                input_data["agent_type"],
                input_data["task"],
                input_data.get("context")
            )
        raise NotImplementedError(f"Tool {name} not implemented")

    async def spawn_subagent(
        self,
        agent_type: str,
        task: str,
        context: dict | None = None
    ) -> str:
        config = SUBAGENT_REGISTRY.get(agent_type)
        if not config:
            return f"Unknown agent type: {agent_type}"

        context_str = f"\n\nContext: {context}" if context else ""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=config.system_prompt,
            messages=[{"role": "user", "content": f"{task}{context_str}"}]
        )

        return next(
            (c.text for c in response.content if c.type == "text"),
            "No response"
        )


# Main orchestrator agent
ORCHESTRATOR_PROMPT = """You are a software engineering orchestrator.
You coordinate specialized sub-agents to complete complex tasks.

Available sub-agents:
- code_reviewer: Reviews code for issues and improvements
- test_writer: Writes comprehensive tests

Use spawn_subagent tool to delegate tasks. Synthesize results into
a coherent response for the user."""

orchestrator_tools = [
    {
        "name": "spawn_subagent",
        "description": "Spawn a specialized sub-agent",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_type": {
                    "type": "string",
                    "enum": ["code_reviewer", "test_writer"]
                },
                "task": {"type": "string"},
                "context": {"type": "object"}
            },
            "required": ["agent_type", "task"]
        }
    }
]

async def main():
    agent = Agent(
        system_prompt=ORCHESTRATOR_PROMPT,
        tools=orchestrator_tools
    )

    result = await agent.run(
        "Review the auth.py file and write tests for any issues found"
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

---

#### Integrating Custom Agents with Claude Code

**Method 1: MCP Server Wrapping Agent**

Create an MCP server that exposes your agent as a tool:

```typescript
// agent-mcp-server.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { Agent } from "./my-agent";

const server = new Server(
  { name: "custom-agent-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

const codeReviewAgent = new Agent({
  name: "code-reviewer",
  systemPrompt: "You are a code review specialist...",
  tools: [],
});

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "code_review",
      description: "Run the code review agent on specified code",
      inputSchema: {
        type: "object",
        properties: {
          code: { type: "string", description: "Code to review" },
          language: { type: "string", description: "Programming language" },
        },
        required: ["code"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "code_review") {
    const { code, language } = request.params.arguments;
    const result = await codeReviewAgent.run(
      `Review this ${language || ""} code:\n\n${code}`
    );
    return { content: [{ type: "text", text: result }] };
  }
  throw new Error("Unknown tool");
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

**Claude Code Configuration**:

```json
{
  "mcpServers": {
    "custom-agents": {
      "command": "npx",
      "args": ["tsx", "./agent-mcp-server.ts"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

**Method 2: Hooks Integration**

Use Claude Code hooks to trigger agents on specific events:

```javascript
// .claude/hooks/post-tool.js
// Triggered after tool execution

module.exports = async function postToolHook(context) {
  const { toolName, toolResult, conversation } = context;

  // Auto-trigger security audit after file writes
  if (toolName === "write_file" && toolResult.success) {
    const filePath = toolResult.filePath;

    if (filePath.includes("auth") || filePath.includes("security")) {
      // Spawn security auditor sub-agent
      return {
        injectMessage: `Please run security audit on ${filePath}`,
        autoExecute: true,
      };
    }
  }

  return null;
};
```

---

#### Agent Communication Patterns

**Pattern 1: Sequential Pipeline**

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Planner │────▶│  Coder  │────▶│ Tester  │────▶│Reviewer │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
```

**Pattern 2: Parallel Fan-out/Fan-in**

```
                    ┌─────────────┐
                    │  Security   │
              ┌────▶│   Auditor   │────┐
              │     └─────────────┘    │
┌──────────┐  │     ┌─────────────┐    │  ┌────────────┐
│ Analyzer │──┼────▶│ Performance │────┼─▶│ Aggregator │
└──────────┘  │     │   Checker   │    │  └────────────┘
              │     └─────────────┘    │
              │     ┌─────────────┐    │
              └────▶│   Style     │────┘
                    │   Linter    │
                    └─────────────┘
```

**Pattern 3: Hierarchical Delegation**

```
                ┌───────────────┐
                │  Orchestrator │
                └───────┬───────┘
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Frontend │  │ Backend  │  │ Database │
    │  Agent   │  │  Agent   │  │  Agent   │
    └────┬─────┘  └────┬─────┘  └────┬─────┘
         │             │             │
    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │Sub-agent│   │Sub-agent│   │Sub-agent│
    └─────────┘   └─────────┘   └─────────┘
```

---

#### Best Practices for Claude Code Agents

| Practice | Description |
| -------- | ----------- |
| **Single Responsibility** | Each agent should have one clear purpose |
| **Explicit Handoffs** | Clearly define what context passes between agents |
| **Failure Handling** | Implement timeouts, retries, and fallbacks |
| **Token Budgets** | Set max_tokens limits to control costs |
| **Observability** | Log agent decisions and tool calls |
| **Idempotency** | Sub-agent tasks should be safe to retry |
| **Context Minimization** | Only pass necessary context to sub-agents |
| **Graceful Degradation** | Main agent should handle sub-agent failures |

## Guidelines & Best Practices

1. Design agents with single responsibilities (separation of concerns)
2. Implement proper error handling and fallback mechanisms
3. Use structured outputs for reliable agent communication
4. Monitor and log agent reasoning chains for debugging
5. Set clear boundaries and guardrails for agent autonomy
6. Consider token costs when designing multi-agent workflows

## Resources

- [LangChain Agents](https://python.langchain.com/docs/concepts/agents/)
- [Google A2A Protocol](https://github.com/google/A2A)
- [HuggingFace smolagents](https://huggingface.co/docs/smolagents/)
- [AutoGen Multi-Agent Framework](https://microsoft.github.io/autogen/)
- [CrewAI Documentation](https://docs.crewai.com/)
