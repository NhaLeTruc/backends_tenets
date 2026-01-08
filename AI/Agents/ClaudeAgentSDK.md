# Claude Agent SDK - Step-by-Step Guide

## Overview

The Claude Agent SDK enables you to build autonomous agents that can use tools, maintain state, and perform complex workflows. This guide provides practical, step-by-step examples for creating agents from basic to advanced.

---

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Installation & Setup](#installation--setup)
3. [Basic Agent](#basic-agent)
4. [Tool-Using Agent](#tool-using-agent)
5. [Stateful Agent](#stateful-agent)
6. [Multi-Step Workflow Agent](#multi-step-workflow-agent)
7. [Advanced Patterns](#advanced-patterns)

---

## Core Concepts

### What is a Claude Agent?
An agent is a long-running process that:
- **Perceives** the environment through observations
- **Reasons** about available tools and state
- **Acts** by calling tools or producing output
- **Iterates** until a goal is achieved

### Key Components
- **Claude Model**: The reasoning engine (Claude 3.5 Sonnet recommended)
- **Tools**: Functions the agent can invoke
- **Memory/State**: Persistent context across interactions
- **Tool Results**: Feedback that guides agent decisions

---

## Installation & Setup

### Prerequisites
```bash
# Python 3.8+
python --version

# Install Claude SDK
pip install anthropic
```

### Basic Import Structure
```python
from anthropic import Anthropic
import json

# Initialize client (uses ANTHROPIC_API_KEY env var)
client = Anthropic()
```

---

## Basic Agent

### Step 1: Simple Text-Based Agent

The simplest agent: takes input, produces output.

```python
from anthropic import Anthropic

def simple_agent(user_input: str) -> str:
    """
    Basic agent that responds to user input.
    No tools, just conversation.
    """
    client = Anthropic()
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system="You are a helpful assistant.",
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    
    return response.content[0].text


# Usage
result = simple_agent("What is the capital of France?")
print(result)
# Output: "The capital of France is Paris."
```

### Step 2: Multi-Turn Conversation Agent

Maintain conversation history across multiple turns.

```python
def conversation_agent():
    """
    Agent that maintains conversation history.
    """
    client = Anthropic()
    conversation_history = []
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get response from Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system="You are a helpful assistant with perfect memory.",
            messages=conversation_history
        )
        
        assistant_message = response.content[0].text
        
        # Add assistant response to history
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        print(f"Assistant: {assistant_message}\n")


# Usage
conversation_agent()
```

---

## Tool-Using Agent

### Step 3: Agent with Single Tool

Add a tool that the agent can invoke.

```python
import json
from anthropic import Anthropic

def agent_with_calculator():
    """
    Agent that can use a calculator tool.
    """
    client = Anthropic()
    
    # Define available tools
    tools = [
        {
            "name": "calculator",
            "description": "Performs basic arithmetic operations",
            "input_schema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The arithmetic operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        }
    ]
    
    # Tool implementation
    def execute_calculator(operation: str, a: float, b: float) -> float:
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                return "Error: Division by zero"
            return a / b
    
    # Agent loop
    messages = [
        {"role": "user", "content": "What is 15 * 23 + 7?"}
    ]
    
    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        
        # Check if we're done
        if response.stop_reason == "end_turn":
            # Extract final text response
            for block in response.content:
                if hasattr(block, 'text'):
                    print(f"Agent: {block.text}")
            break
        
        # Process tool use
        if response.stop_reason == "tool_use":
            # Add assistant response to messages
            messages.append({"role": "assistant", "content": response.content})
            
            # Find and execute tool call
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    
                    print(f"Calling tool: {tool_name}")
                    print(f"Input: {tool_input}")
                    
                    # Execute the tool
                    if tool_name == "calculator":
                        result = execute_calculator(
                            tool_input["operation"],
                            tool_input["a"],
                            tool_input["b"]
                        )
                    
                    print(f"Result: {result}\n")
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(result)
                            }
                        ]
                    })


# Usage
agent_with_calculator()
```

### Step 4: Agent with Multiple Tools

Expand with more tools for richer capabilities.

```python
def agent_with_multiple_tools():
    """
    Agent with weather lookup, web search, and calculator tools.
    """
    client = Anthropic()
    
    tools = [
        {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "web_search",
            "description": "Search the web for information",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "database_query",
            "description": "Query company database",
            "input_schema": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "Table name"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Query filters"
                    }
                },
                "required": ["table"]
            }
        }
    ]
    
    # Tool implementations
    def get_weather(location: str) -> str:
        # Simulated weather data
        return f"Clear, 72°F in {location}"
    
    def web_search(query: str) -> str:
        # Simulated search results
        return f"Found 10,000 results for '{query}'"
    
    def database_query(table: str, filters: dict = None) -> str:
        # Simulated database results
        return f"Retrieved 50 records from {table}"
    
    # Main agent loop
    messages = [
        {"role": "user", "content": "What's the weather in NYC and recent AI news?"}
    ]
    
    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, 'text'):
                    print(f"Agent: {block.text}")
            break
        
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    
                    # Dispatch to appropriate tool
                    if tool_name == "get_weather":
                        result = get_weather(tool_input["location"])
                    elif tool_name == "web_search":
                        result = web_search(tool_input["query"])
                    elif tool_name == "database_query":
                        result = database_query(
                            tool_input["table"],
                            tool_input.get("filters")
                        )
                    else:
                        result = "Unknown tool"
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            messages.append({
                "role": "user",
                "content": tool_results
            })


# Usage
agent_with_multiple_tools()
```

---

## Stateful Agent

### Step 5: Agent with Memory & Context

Maintain agent state and context across sessions.

```python
import json
from datetime import datetime

class StatefulAgent:
    """
    Agent with persistent memory and state.
    """
    
    def __init__(self, agent_name: str):
        self.client = Anthropic()
        self.agent_name = agent_name
        self.memory = {
            "facts": [],
            "tasks": [],
            "decisions": [],
            "created_at": datetime.now().isoformat()
        }
        self.messages = []
    
    def add_fact(self, fact: str):
        """Record a fact in memory."""
        self.memory["facts"].append({
            "fact": fact,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_task(self, task: str):
        """Track a task."""
        self.memory["tasks"].append({
            "task": task,
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        })
    
    def get_context(self) -> str:
        """Generate context from memory."""
        context = f"Agent: {self.agent_name}\n"
        context += f"Memory:\n"
        context += f"- Known facts: {len(self.memory['facts'])}\n"
        context += f"- Active tasks: {len([t for t in self.memory['tasks'] if t['status'] == 'pending'])}\n"
        return context
    
    def reason(self, input_text: str) -> str:
        """Process input and reason about it."""
        # Add context to system message
        system_message = f"""You are {self.agent_name}, an intelligent agent.
        
{self.get_context()}

Make decisions based on your memory and current context."""
        
        # Add user input
        self.messages.append({
            "role": "user",
            "content": input_text
        })
        
        # Get response
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_message,
            messages=self.messages
        )
        
        assistant_message = response.content[0].text
        self.messages.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def save_memory(self, filepath: str):
        """Persist memory to disk."""
        with open(filepath, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def load_memory(self, filepath: str):
        """Load memory from disk."""
        with open(filepath, 'r') as f:
            self.memory = json.load(f)


# Usage
agent = StatefulAgent("ResearchAgent")
agent.add_fact("User prefers detailed explanations")
agent.add_task("Complete project documentation")

response = agent.reason("How should I organize the project structure?")
print(f"Agent: {response}")

agent.save_memory("agent_memory.json")
```

---

## Multi-Step Workflow Agent

### Step 6: Agent with Workflow Orchestration

Handle complex multi-step processes.

```python
from enum import Enum
from typing import List

class WorkflowState(Enum):
    INIT = "init"
    PLANNING = "planning"
    EXECUTION = "execution"
    VALIDATION = "validation"
    COMPLETE = "complete"

class WorkflowAgent:
    """
    Agent that orchestrates multi-step workflows.
    """
    
    def __init__(self):
        self.client = Anthropic()
        self.state = WorkflowState.INIT
        self.steps = []
        self.results = []
    
    def plan(self, objective: str) -> List[str]:
        """Create a plan to achieve the objective."""
        self.state = WorkflowState.PLANNING
        
        messages = [{
            "role": "user",
            "content": f"Create a detailed step-by-step plan to: {objective}\nNumber each step."
        }]
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=messages
        )
        
        plan_text = response.content[0].text
        # Parse steps from response
        self.steps = [line.strip() for line in plan_text.split('\n') if line.strip()]
        return self.steps
    
    def execute_step(self, step: str, context: str = "") -> str:
        """Execute a single step."""
        self.state = WorkflowState.EXECUTION
        
        prompt = f"Execute this step: {step}"
        if context:
            prompt += f"\nContext: {context}"
        
        messages = [{"role": "user", "content": prompt}]
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=messages
        )
        
        result = response.content[0].text
        self.results.append({
            "step": step,
            "result": result
        })
        return result
    
    def validate(self) -> bool:
        """Validate that workflow completed successfully."""
        self.state = WorkflowState.VALIDATION
        
        summary = "\n".join([f"Step: {r['step']}\nResult: {r['result']}" 
                            for r in self.results])
        
        messages = [{
            "role": "user",
            "content": f"Validate this workflow completion:\n{summary}\n\nRespond with YES or NO."
        }]
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=messages
        )
        
        self.state = WorkflowState.COMPLETE
        return "YES" in response.content[0].text.upper()


# Usage
agent = WorkflowAgent()

objective = "Write and test a Python function to calculate Fibonacci numbers"
steps = agent.plan(objective)

print("Plan:")
for step in steps:
    print(f"  - {step}")

print("\nExecuting workflow:")
for step in steps[:3]:  # Execute first 3 steps
    result = agent.execute_step(step, context="Use Python 3.8+")
    print(f"✓ {step[:50]}...")

if agent.validate():
    print("\n✓ Workflow completed successfully!")
else:
    print("\n✗ Workflow validation failed")
```

---

## Advanced Patterns

### Step 7: Specialized Agent Types

#### Research Agent
```python
class ResearchAgent:
    """
    Specialized agent for research and information gathering.
    """
    
    def __init__(self):
        self.client = Anthropic()
        self.sources = []
        self.findings = []
    
    def research(self, topic: str, depth: str = "medium") -> dict:
        """
        Conduct research on a topic.
        depth: "shallow", "medium", "deep"
        """
        messages = [{
            "role": "user",
            "content": f"""Research the topic: {topic}
            Depth: {depth}
            Provide:
            1. Key findings
            2. Important sources
            3. Gaps in current knowledge
            4. Recommendations for further research"""
        }]
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=messages
        )
        
        return {
            "topic": topic,
            "depth": depth,
            "research": response.content[0].text
        }
```

#### Code Generation Agent
```python
class CodeGenerationAgent:
    """
    Specialized agent for code generation and refactoring.
    """
    
    def __init__(self):
        self.client = Anthropic()
        self.generated_code = []
    
    def generate(self, requirement: str, language: str = "python") -> str:
        """Generate code based on requirement."""
        messages = [{
            "role": "user",
            "content": f"""Generate production-quality {language} code for:
            {requirement}
            
            Include:
            - Type hints
            - Docstrings
            - Error handling
            - Unit tests"""
        }]
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=messages
        )
        
        code = response.content[0].text
        self.generated_code.append({
            "requirement": requirement,
            "language": language,
            "code": code
        })
        return code
```

#### Decision-Making Agent
```python
class DecisionAgent:
    """
    Specialized agent for evaluating options and making decisions.
    """
    
    def __init__(self):
        self.client = Anthropic()
        self.decisions = []
    
    def decide(self, decision_point: str, options: List[str], 
               criteria: List[str] = None) -> dict:
        """Make a decision between options."""
        
        criteria_text = ""
        if criteria:
            criteria_text = f"Evaluation criteria: {', '.join(criteria)}\n"
        
        options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        
        messages = [{
            "role": "user",
            "content": f"""Make a decision for: {decision_point}
            
Options:
{options_text}

{criteria_text}

Provide:
1. Pros and cons for each option
2. Recommended choice with reasoning
3. Risk assessment
4. Implementation considerations"""
        }]
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=messages
        )
        
        decision = {
            "decision_point": decision_point,
            "options": options,
            "analysis": response.content[0].text
        }
        self.decisions.append(decision)
        return decision
```

---

## Best Practices

### 1. **Agent Design**
- Keep agents focused on specific domains
- Design clear input/output contracts
- Plan tool availability carefully
- Implement proper error handling

### 2. **Tool Design**
- Tools should be atomic and single-purpose
- Provide clear, detailed descriptions
- Define input schemas precisely
- Handle errors gracefully

### 3. **State Management**
- Use persistent storage for important state
- Implement memory limits to prevent token overflow
- Archive old conversations periodically
- Version your agent memory

### 4. **Performance**
- Use streaming for long responses
- Batch tool calls when possible
- Monitor token usage
- Implement caching for repeated queries

### 5. **Safety & Reliability**
- Validate tool inputs
- Implement rate limiting
- Log all decisions and tool calls
- Add human-in-the-loop for critical decisions
- Test agents thoroughly before production

---

## Common Patterns

### Retry Logic
```python
def agent_with_retry(max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = client.messages.create(...)
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Retry {attempt + 1}/{max_retries}")
```

### Token Monitoring
```python
def track_tokens(response):
    usage = response.usage
    print(f"Input tokens: {usage.input_tokens}")
    print(f"Output tokens: {usage.output_tokens}")
```

### Structured Output
```python
def get_structured_response(client, prompt: str, output_format: str):
    """Get response in specific format (JSON, Markdown, etc.)"""
    return client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"{prompt}\n\nRespond in {output_format} format."
        }]
    )
```

---

## Testing Your Agent

```python
def test_agent(agent, test_cases: List[tuple]):
    """
    test_cases: List of (input, expected_output_pattern)
    """
    results = []
    for test_input, expected_pattern in test_cases:
        response = agent.reason(test_input)
        passed = expected_pattern.lower() in response.lower()
        results.append({
            "input": test_input,
            "passed": passed,
            "response": response
        })
    
    passed_count = sum(1 for r in results if r["passed"])
    print(f"Tests passed: {passed_count}/{len(test_cases)}")
    return results
```

---

## Resources

- [Anthropic API Documentation](https://docs.anthropic.com)
- [Claude Models Guide](https://docs.anthropic.com/en/docs/about-claude/models/overview)
- [Tool Use Documentation](https://docs.anthropic.com/en/docs/build-a-system-prompt-with-tools)
- [Agent Architecture Patterns](https://github.com/anthropics/agents)

