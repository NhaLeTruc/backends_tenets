# MCP (Model Context Protocol) & Tooling

## Table of Contents

- [MCP (Model Context Protocol) & Tooling](#mcp-model-context-protocol--tooling)
  - [Table of Contents](#table-of-contents)
  - [Sub-topics](#sub-topics)
  - [Explanation](#explanation)
  - [Knowledge Graph MCPs](#knowledge-graph-mcps)
    - [Setting Up Neo4j Knowledge Graph MCP](#setting-up-neo4j-knowledge-graph-mcp)
    - [Setting Up Memory MCP (Lightweight Knowledge Graph)](#setting-up-memory-mcp-lightweight-knowledge-graph)
    - [Setting Up Custom Knowledge Graph MCP with Vector Search](#setting-up-custom-knowledge-graph-mcp-with-vector-search)
    - [Knowledge Graph MCP Best Practices](#knowledge-graph-mcp-best-practices)
  - [Setting Up PostgreSQL MCP Server](#setting-up-postgresql-mcp-server)
  - [Setting Up Spark Cluster MCP Server](#setting-up-spark-cluster-mcp-server)
  - [MCP Authentication for Claude Code](#mcp-authentication-for-claude-code)
    - [1. Environment Variable Authentication](#1-environment-variable-authentication)
    - [2. API Key Header Authentication](#2-api-key-header-authentication)
    - [3. OAuth 2.0 Authentication](#3-oauth-20-authentication)
    - [4. Token-Based Authentication with Refresh](#4-token-based-authentication-with-refresh)
    - [5. Mutual TLS (mTLS) Authentication](#5-mutual-tls-mtls-authentication)
    - [6. Secrets Management Integration](#6-secrets-management-integration)
  - [Guidelines & Best Practices](#guidelines--best-practices)
    - [General MCP Best Practices](#general-mcp-best-practices)
    - [Database MCP Best Practices](#database-mcp-best-practices)
    - [Spark MCP Best Practices](#spark-mcp-best-practices)
    - [MCP Security Checklist](#mcp-security-checklist)
  - [Resources](#resources)

## Sub-topics

- MCP (Model Context Protocol)
- Persistent memory MCPs
- Claude Code knowledge graph MCP
- Database MCP servers (PostgreSQL, MySQL)
- Big data MCP servers (Spark, Databricks)
- Custom MCP server development

## Explanation

**MCP (Model Context Protocol)** is Anthropic's open standard for connecting AI assistants to external tools, data sources, and services. It provides:

- Standardized tool definitions
- Secure communication protocol
- Resource access patterns

**Persistent memory MCPs** provide long-term storage capabilities:

- User preferences
- Conversation history
- Knowledge bases

**Knowledge graph MCPs** enable structured relationship-based data access for enhanced reasoning.

---

### Knowledge Graph MCPs

**Overview**: Knowledge graph MCPs connect Claude to graph databases and knowledge bases, enabling relationship-aware reasoning, semantic search, and complex graph traversals.

**Why Knowledge Graphs for AI?**

| Capability | Benefit |
| ---------- | ------- |
| **Relationship modeling** | Captures how entities relate (not just what they are) |
| **Multi-hop reasoning** | Answer questions requiring traversal across connections |
| **Context enrichment** | Provide relevant connected context automatically |
| **Semantic understanding** | Entity disambiguation and concept linking |
| **Explainability** | Trace reasoning paths through the graph |

**Knowledge Graph Architecture with MCP**:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│   Claude    │────▶│  KG MCP     │────▶│  Graph Database     │
│             │◀────│  Server     │◀────│  (Neo4j/etc)        │
└─────────────┘     └─────────────┘     └─────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Nodes   │ │  Edges   │ │  Vector  │
        │ (Entities)│ │(Relations)│ │  Index   │
        └──────────┘ └──────────┘ └──────────┘
```

**Available Knowledge Graph MCP Options**:

| Option | Database | Best For |
| ------ | -------- | -------- |
| **Neo4j MCP** | Neo4j | Enterprise knowledge graphs, Cypher queries |
| **Memory MCP** | In-memory JSON | Lightweight persistent memory, personal knowledge |
| **Custom KG MCP** | Any graph DB | Domain-specific ontologies, specialized use cases |
| **Obsidian MCP** | Markdown files | Note-based knowledge management |

---

#### Setting Up Neo4j Knowledge Graph MCP

**Prerequisites**:

- Neo4j database (local, Aura cloud, or self-hosted)
- Node.js 18+ or Python 3.10+

**Option 1: Community Neo4j MCP Server**

```bash
# Install from npm
npm install -g @neo4j-contrib/mcp-neo4j

# Or run directly
npx @neo4j-contrib/mcp-neo4j
```

**Claude Code Configuration** (`~/.claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "neo4j": {
      "command": "npx",
      "args": ["-y", "@neo4j-contrib/mcp-neo4j"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

**Neo4j Aura (Cloud) Configuration**:

```json
{
  "mcpServers": {
    "neo4j-aura": {
      "command": "npx",
      "args": ["-y", "@neo4j-contrib/mcp-neo4j"],
      "env": {
        "NEO4J_URI": "neo4j+s://xxxxxxxx.databases.neo4j.io",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your-aura-password"
      }
    }
  }
}
```

**Option 2: Custom Neo4j MCP Server (Python)**

```python
# neo4j_kg_mcp_server.py
import asyncio
import json
from neo4j import AsyncGraphDatabase
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource

server = Server("neo4j-knowledge-graph")

# Neo4j connection
driver = None

async def init_driver():
    global driver
    driver = AsyncGraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
    )

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="cypher_query",
            description="Execute a Cypher query on the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Cypher query to execute"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Query parameters",
                        "default": {}
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="find_entity",
            description="Find an entity and its relationships in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Entity name to search for"
                    },
                    "label": {
                        "type": "string",
                        "description": "Optional node label filter"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="find_path",
            description="Find shortest path between two entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_entity": {"type": "string"},
                    "to_entity": {"type": "string"},
                    "max_hops": {"type": "integer", "default": 4}
                },
                "required": ["from_entity", "to_entity"]
            }
        ),
        Tool(
            name="get_neighbors",
            description="Get all entities connected to a given entity",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_name": {"type": "string"},
                    "relationship_type": {
                        "type": "string",
                        "description": "Optional: filter by relationship type"
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["outgoing", "incoming", "both"],
                        "default": "both"
                    },
                    "limit": {"type": "integer", "default": 50}
                },
                "required": ["entity_name"]
            }
        ),
        Tool(
            name="add_entity",
            description="Add a new entity to the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "label": {"type": "string"},
                    "properties": {"type": "object", "default": {}}
                },
                "required": ["name", "label"]
            }
        ),
        Tool(
            name="add_relationship",
            description="Create a relationship between two entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_entity": {"type": "string"},
                    "to_entity": {"type": "string"},
                    "relationship_type": {"type": "string"},
                    "properties": {"type": "object", "default": {}}
                },
                "required": ["from_entity", "to_entity", "relationship_type"]
            }
        ),
        Tool(
            name="graph_stats",
            description="Get statistics about the knowledge graph",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_schema",
            description="Get the schema (node labels and relationship types) of the graph",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    async with driver.session() as session:
        try:
            if name == "cypher_query":
                query = arguments["query"]
                params = arguments.get("parameters", {})

                # Security: Block destructive operations
                forbidden = ["DELETE", "DETACH", "DROP", "REMOVE"]
                if any(kw in query.upper() for kw in forbidden):
                    return [TextContent(
                        type="text",
                        text="Error: Destructive operations not allowed"
                    )]

                result = await session.run(query, params)
                records = [dict(record) for record in await result.data()]
                return [TextContent(
                    type="text",
                    text=json.dumps(records, indent=2, default=str)
                )]

            elif name == "find_entity":
                entity_name = arguments["name"]
                label = arguments.get("label", "")

                label_filter = f":{label}" if label else ""
                query = f"""
                MATCH (n{label_filter})
                WHERE toLower(n.name) CONTAINS toLower($name)
                OPTIONAL MATCH (n)-[r]-(connected)
                RETURN n, collect(DISTINCT {{
                    relationship: type(r),
                    connected_node: connected.name,
                    connected_label: labels(connected)[0]
                }})[0..10] as connections
                LIMIT 5
                """
                result = await session.run(query, {"name": entity_name})
                records = await result.data()
                return [TextContent(
                    type="text",
                    text=json.dumps(records, indent=2, default=str)
                )]

            elif name == "find_path":
                query = """
                MATCH (start), (end)
                WHERE toLower(start.name) CONTAINS toLower($from)
                  AND toLower(end.name) CONTAINS toLower($to)
                MATCH path = shortestPath((start)-[*1..$max_hops]-(end))
                RETURN [node IN nodes(path) | node.name] AS path_nodes,
                       [rel IN relationships(path) | type(rel)] AS path_rels
                LIMIT 3
                """
                result = await session.run(query, {
                    "from": arguments["from_entity"],
                    "to": arguments["to_entity"],
                    "max_hops": arguments.get("max_hops", 4)
                })
                records = await result.data()
                return [TextContent(
                    type="text",
                    text=json.dumps(records, indent=2, default=str)
                )]

            elif name == "get_neighbors":
                entity = arguments["entity_name"]
                rel_type = arguments.get("relationship_type", "")
                direction = arguments.get("direction", "both")
                limit = arguments.get("limit", 50)

                rel_filter = f":{rel_type}" if rel_type else ""

                if direction == "outgoing":
                    pattern = f"(n)-[r{rel_filter}]->(neighbor)"
                elif direction == "incoming":
                    pattern = f"(n)<-[r{rel_filter}]-(neighbor)"
                else:
                    pattern = f"(n)-[r{rel_filter}]-(neighbor)"

                query = f"""
                MATCH (n)
                WHERE toLower(n.name) CONTAINS toLower($name)
                MATCH {pattern}
                RETURN neighbor.name AS name,
                       labels(neighbor)[0] AS label,
                       type(r) AS relationship
                LIMIT $limit
                """
                result = await session.run(query, {"name": entity, "limit": limit})
                records = await result.data()
                return [TextContent(
                    type="text",
                    text=json.dumps(records, indent=2, default=str)
                )]

            elif name == "add_entity":
                query = """
                MERGE (n:$label {name: $name})
                SET n += $properties
                RETURN n
                """
                # Use parameterized label safely
                label = arguments["label"]
                props = arguments.get("properties", {})
                props["name"] = arguments["name"]

                result = await session.run(
                    f"MERGE (n:{label} {{name: $name}}) SET n += $props RETURN n",
                    {"name": arguments["name"], "props": props}
                )
                records = await result.data()
                return [TextContent(
                    type="text",
                    text=f"Created/updated entity: {json.dumps(records, default=str)}"
                )]

            elif name == "add_relationship":
                query = """
                MATCH (a), (b)
                WHERE a.name = $from_entity AND b.name = $to_entity
                MERGE (a)-[r:$rel_type]->(b)
                SET r += $properties
                RETURN a.name, type(r), b.name
                """
                rel_type = arguments["relationship_type"]
                result = await session.run(
                    f"""
                    MATCH (a), (b)
                    WHERE a.name = $from AND b.name = $to
                    MERGE (a)-[r:{rel_type}]->(b)
                    SET r += $props
                    RETURN a.name AS from, type(r) AS rel, b.name AS to
                    """,
                    {
                        "from": arguments["from_entity"],
                        "to": arguments["to_entity"],
                        "props": arguments.get("properties", {})
                    }
                )
                records = await result.data()
                return [TextContent(
                    type="text",
                    text=f"Created relationship: {json.dumps(records, default=str)}"
                )]

            elif name == "graph_stats":
                stats_query = """
                CALL apoc.meta.stats() YIELD nodeCount, relCount, labels, relTypes
                RETURN nodeCount, relCount, labels, relTypes
                """
                # Fallback if APOC not installed
                try:
                    result = await session.run(stats_query)
                    records = await result.data()
                except:
                    result = await session.run("""
                        MATCH (n) WITH count(n) as nodes
                        MATCH ()-[r]->() WITH nodes, count(r) as rels
                        RETURN nodes, rels
                    """)
                    records = await result.data()
                return [TextContent(
                    type="text",
                    text=json.dumps(records, indent=2, default=str)
                )]

            elif name == "get_schema":
                query = """
                CALL db.schema.visualization()
                """
                try:
                    result = await session.run(query)
                    records = await result.data()
                except:
                    # Fallback for older Neo4j versions
                    labels_result = await session.run("CALL db.labels()")
                    labels = [r["label"] for r in await labels_result.data()]
                    rels_result = await session.run("CALL db.relationshipTypes()")
                    rels = [r["relationshipType"] for r in await rels_result.data()]
                    records = {"labels": labels, "relationship_types": rels}
                return [TextContent(
                    type="text",
                    text=json.dumps(records, indent=2, default=str)
                )]

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    await init_driver()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
```

**Claude Code Configuration for Custom Server**:

```json
{
  "mcpServers": {
    "knowledge-graph": {
      "command": "python",
      "args": ["/path/to/neo4j_kg_mcp_server.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

---

#### Setting Up Memory MCP (Lightweight Knowledge Graph)

**Overview**: The Memory MCP provides a simple file-based knowledge graph for personal knowledge management without requiring a database server.

**Installation**:

```bash
npx -y @modelcontextprotocol/server-memory
```

**Claude Code Configuration**:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE": "/path/to/knowledge.json"
      }
    }
  }
}
```

**Memory MCP Data Structure**:

```json
{
  "entities": [
    {
      "name": "Project Alpha",
      "entityType": "Project",
      "observations": [
        "Started in January 2024",
        "Uses React and TypeScript",
        "Team of 5 developers"
      ]
    },
    {
      "name": "John Smith",
      "entityType": "Person",
      "observations": [
        "Tech lead on Project Alpha",
        "Expert in distributed systems"
      ]
    }
  ],
  "relations": [
    {
      "from": "John Smith",
      "to": "Project Alpha",
      "relationType": "leads"
    }
  ]
}
```

**Available Memory MCP Tools**:

| Tool | Description |
| ---- | ----------- |
| `create_entities` | Add new entities with observations |
| `create_relations` | Link entities with typed relationships |
| `add_observations` | Add facts to existing entities |
| `delete_entities` | Remove entities from memory |
| `delete_observations` | Remove specific observations |
| `delete_relations` | Remove relationships |
| `read_graph` | Retrieve the entire knowledge graph |
| `search_nodes` | Search entities by name |
| `open_nodes` | Get specific entities by name |

**Example Usage in Claude**:

```txt
User: Remember that the API project uses PostgreSQL and Redis

Claude: I'll store this in the knowledge graph.
[Calls create_entities with entity "API Project"]
[Calls create_relations linking "API Project" to "PostgreSQL" and "Redis"]

User: What database does the API project use?

Claude: Let me check the knowledge graph.
[Calls open_nodes for "API Project"]
Based on my knowledge graph, the API Project uses PostgreSQL and Redis.
```

---

#### Setting Up Custom Knowledge Graph MCP with Vector Search

**Overview**: Combine graph structure with vector embeddings for semantic search capabilities.

```python
# hybrid_kg_mcp_server.py
import asyncio
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from neo4j import AsyncGraphDatabase
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("hybrid-knowledge-graph")

# Initialize embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')
driver = None

async def init_driver():
    global driver
    driver = AsyncGraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
    )

def get_embedding(text: str) -> list:
    """Generate embedding for text"""
    return embedder.encode(text).tolist()

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="semantic_search",
            description="Search the knowledge graph using natural language",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query"
                    },
                    "limit": {"type": "integer", "default": 10},
                    "entity_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: filter by entity types"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="add_knowledge",
            description="Add new knowledge to the graph with automatic embedding",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_name": {"type": "string"},
                    "entity_type": {"type": "string"},
                    "description": {"type": "string"},
                    "facts": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "related_to": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity": {"type": "string"},
                                "relationship": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["entity_name", "entity_type", "description"]
            }
        ),
        Tool(
            name="contextual_query",
            description="Answer questions using graph traversal and semantic matching",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "context_depth": {
                        "type": "integer",
                        "default": 2,
                        "description": "How many hops to traverse for context"
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="find_related_concepts",
            description="Find semantically related concepts to a given topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "concept": {"type": "string"},
                    "similarity_threshold": {
                        "type": "number",
                        "default": 0.7
                    },
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["concept"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    async with driver.session() as session:
        try:
            if name == "semantic_search":
                query_embedding = get_embedding(arguments["query"])
                limit = arguments.get("limit", 10)
                entity_types = arguments.get("entity_types", [])

                type_filter = ""
                if entity_types:
                    labels = ":".join(entity_types)
                    type_filter = f":{labels}"

                # Vector similarity search using Neo4j vector index
                cypher = f"""
                CALL db.index.vector.queryNodes('entity_embeddings', $limit, $embedding)
                YIELD node, score
                WHERE score > 0.5
                RETURN node.name AS name,
                       labels(node)[0] AS type,
                       node.description AS description,
                       score
                ORDER BY score DESC
                """
                result = await session.run(cypher, {
                    "embedding": query_embedding,
                    "limit": limit
                })
                records = await result.data()
                return [TextContent(
                    type="text",
                    text=json.dumps(records, indent=2)
                )]

            elif name == "add_knowledge":
                name = arguments["entity_name"]
                entity_type = arguments["entity_type"]
                description = arguments["description"]
                facts = arguments.get("facts", [])
                related_to = arguments.get("related_to", [])

                # Generate embedding for the entity
                text_for_embedding = f"{name}. {description}. {' '.join(facts)}"
                embedding = get_embedding(text_for_embedding)

                # Create entity with embedding
                cypher = f"""
                MERGE (n:{entity_type} {{name: $name}})
                SET n.description = $description,
                    n.facts = $facts,
                    n.embedding = $embedding,
                    n.updated_at = datetime()
                RETURN n
                """
                await session.run(cypher, {
                    "name": name,
                    "description": description,
                    "facts": facts,
                    "embedding": embedding
                })

                # Create relationships
                for rel in related_to:
                    rel_cypher = f"""
                    MATCH (a {{name: $from_name}})
                    MATCH (b {{name: $to_name}})
                    MERGE (a)-[r:{rel['relationship']}]->(b)
                    """
                    await session.run(rel_cypher, {
                        "from_name": name,
                        "to_name": rel["entity"]
                    })

                return [TextContent(
                    type="text",
                    text=f"Added knowledge: {name} ({entity_type})"
                )]

            elif name == "contextual_query":
                question = arguments["question"]
                depth = arguments.get("context_depth", 2)

                # Find relevant starting nodes via semantic search
                query_embedding = get_embedding(question)

                cypher = f"""
                CALL db.index.vector.queryNodes('entity_embeddings', 3, $embedding)
                YIELD node, score
                WHERE score > 0.5
                WITH node
                MATCH path = (node)-[*1..{depth}]-(connected)
                RETURN node.name AS start_node,
                       node.description AS start_description,
                       [n IN nodes(path) | n.name] AS path_nodes,
                       [n IN nodes(path) | n.description] AS descriptions,
                       [r IN relationships(path) | type(r)] AS relationships
                LIMIT 20
                """
                result = await session.run(cypher, {"embedding": query_embedding})
                records = await result.data()

                # Format context for response
                context = []
                for record in records:
                    context.append({
                        "entity": record["start_node"],
                        "description": record["start_description"],
                        "connected_context": list(zip(
                            record["path_nodes"],
                            record["descriptions"]
                        ))
                    })

                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "question": question,
                        "relevant_context": context
                    }, indent=2)
                )]

            elif name == "find_related_concepts":
                concept = arguments["concept"]
                threshold = arguments.get("similarity_threshold", 0.7)
                limit = arguments.get("limit", 10)

                concept_embedding = get_embedding(concept)

                cypher = """
                CALL db.index.vector.queryNodes('entity_embeddings', $limit, $embedding)
                YIELD node, score
                WHERE score >= $threshold
                RETURN node.name AS concept,
                       labels(node)[0] AS type,
                       node.description AS description,
                       score AS similarity
                ORDER BY score DESC
                """
                result = await session.run(cypher, {
                    "embedding": concept_embedding,
                    "limit": limit,
                    "threshold": threshold
                })
                records = await result.data()
                return [TextContent(
                    type="text",
                    text=json.dumps(records, indent=2)
                )]

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    await init_driver()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
```

**Neo4j Vector Index Setup** (required for semantic search):

```cypher
-- Create vector index for entity embeddings
CREATE VECTOR INDEX entity_embeddings IF NOT EXISTS
FOR (n:Entity)
ON n.embedding
OPTIONS {indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}};

-- For multiple entity types
CALL db.index.vector.createNodeIndex(
  'entity_embeddings',
  'Entity',
  'embedding',
  384,
  'cosine'
);
```

---

#### Knowledge Graph MCP Best Practices

**Graph Modeling for AI**:

1. **Use descriptive relationship types**: `MANAGES` is better than `RELATED_TO`
2. **Include temporal data**: Add `created_at`, `valid_from`, `valid_until` properties
3. **Store embeddings on nodes**: Enable semantic search alongside graph traversal
4. **Keep descriptions concise**: AI works better with clear, factual statements
5. **Version your schema**: Document node labels and relationship types

**Query Patterns for Common AI Tasks**:

| Task | Cypher Pattern |
| ---- | -------------- |
| Entity lookup | `MATCH (n {name: $name}) RETURN n` |
| Relationship discovery | `MATCH (n)-[r]->(m) WHERE n.name = $name RETURN type(r), m` |
| Path finding | `MATCH path = shortestPath((a)-[*]-(b)) RETURN path` |
| Neighborhood | `MATCH (n)-[*1..2]-(neighbors) RETURN DISTINCT neighbors` |
| Pattern matching | `MATCH (p:Person)-[:WORKS_AT]->(c:Company)-[:IN_INDUSTRY]->(i) RETURN p, c, i` |

**Performance Optimization**:

```cypher
-- Create indexes for frequently queried properties
CREATE INDEX entity_name_idx FOR (n:Entity) ON (n.name);
CREATE INDEX person_name_idx FOR (n:Person) ON (n.name);

-- Use parameterized queries (prevent injection, enable caching)
MATCH (n:Person {name: $name}) RETURN n  -- Good
MATCH (n:Person {name: 'John'}) RETURN n  -- Avoid

-- Limit results to prevent memory issues
MATCH (n)-[r*1..3]-(m) RETURN n, r, m LIMIT 100
```

**Security Considerations**:

1. **Read-only access by default**: Use separate credentials for read vs write
2. **Sanitize user inputs**: Validate entity names and relationship types
3. **Limit traversal depth**: Prevent expensive unbounded queries
4. **Audit access**: Log all knowledge graph operations
5. **Encrypt sensitive data**: Use Neo4j's property-level encryption for PII

**Example Knowledge Graph Schema for Claude Code**:

```cypher
// Schema for a software project knowledge graph
(:Project {name, description, status, start_date})
(:Person {name, role, email, expertise: []})
(:Technology {name, category, version})
(:Document {name, path, type, summary})
(:Decision {name, date, rationale, status})
(:Codebase {name, repo_url, language})

// Relationships
(:Person)-[:WORKS_ON]->(:Project)
(:Person)-[:AUTHORED]->(:Document)
(:Project)-[:USES]->(:Technology)
(:Project)-[:HAS_CODEBASE]->(:Codebase)
(:Decision)-[:AFFECTS]->(:Project)
(:Person)-[:MADE]->(:Decision)
(:Document)-[:DOCUMENTS]->(:Decision)
```

---

**MCP Architecture Overview**:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI Assistant  │────▶│   MCP Client    │────▶│   MCP Server    │
│   (Claude)      │◀────│   (SDK)         │◀────│   (Your Service)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  External       │
                                                │  Resources      │
                                                │  (DB, API, etc) │
                                                └─────────────────┘
```

**MCP Communication Protocol**:

| Component | Description |
| --------- | ----------- |
| **Transport** | stdio, HTTP/SSE, or WebSocket |
| **Messages** | JSON-RPC 2.0 format |
| **Capabilities** | Tools, Resources, Prompts |

---

### Setting Up PostgreSQL MCP Server

**Overview**: The PostgreSQL MCP server enables Claude to query databases, explore schemas, and perform data analysis through natural language.

**Installation Options**:

```bash
# Option 1: Use the official MCP Postgres server
npx -y @modelcontextprotocol/server-postgres

# Option 2: Install globally
npm install -g @modelcontextprotocol/server-postgres

# Option 3: Use Docker
docker run -e DATABASE_URL="postgresql://..." mcp/postgres-server
```

**Claude Code Configuration** (`~/.claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://username:password@localhost:5432/database"
      ]
    }
  }
}
```

**Environment Variable Configuration** (recommended for security):

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres"
      ],
      "env": {
        "DATABASE_URL": "postgresql://username:password@localhost:5432/database"
      }
    }
  }
}
```

**Connection String Formats**:

```bash
# Standard format
postgresql://username:password@host:port/database

# With SSL
postgresql://username:password@host:port/database?sslmode=require

# With connection pooling (PgBouncer)
postgresql://username:password@pgbouncer-host:6432/database

# AWS RDS
postgresql://username:password@mydb.abc123.us-east-1.rds.amazonaws.com:5432/database

# Supabase
postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

**Available Tools** (exposed by Postgres MCP):

| Tool | Description |
| ---- | ----------- |
| `query` | Execute read-only SQL queries |
| `list_tables` | List all tables in the database |
| `describe_table` | Get schema information for a table |
| `list_schemas` | List all schemas |
| `get_table_stats` | Get row counts and statistics |

**Custom PostgreSQL MCP Server** (Python implementation):

```python
# postgres_mcp_server.py
import asyncio
import asyncpg
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("postgres-mcp")

# Connection pool
pool = None

async def init_pool():
    global pool
    pool = await asyncpg.create_pool(
        dsn=os.environ["DATABASE_URL"],
        min_size=2,
        max_size=10
    )

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="query",
            description="Execute a read-only SQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL query to execute (SELECT only)"
                    }
                },
                "required": ["sql"]
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in the database",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="describe_table",
            description="Get column information for a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"}
                },
                "required": ["table_name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query":
        sql = arguments["sql"].strip()

        # Security: Only allow SELECT queries
        if not sql.upper().startswith("SELECT"):
            return [TextContent(
                type="text",
                text="Error: Only SELECT queries are allowed"
            )]

        async with pool.acquire() as conn:
            rows = await conn.fetch(sql)
            result = [dict(row) for row in rows]
            return [TextContent(
                type="text",
                text=json.dumps(result, default=str, indent=2)
            )]

    elif name == "list_tables":
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY table_schema, table_name
            """)
            return [TextContent(
                type="text",
                text=json.dumps([dict(r) for r in rows], indent=2)
            )]

    elif name == "describe_table":
        table_name = arguments["table_name"]
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position
            """, table_name)
            return [TextContent(
                type="text",
                text=json.dumps([dict(r) for r in rows], indent=2)
            )]

async def main():
    await init_pool()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
```

**PostgreSQL MCP Security Best Practices**:

1. **Use read-only database users**:

   ```sql
   CREATE USER mcp_readonly WITH PASSWORD 'secure_password';
   GRANT CONNECT ON DATABASE mydb TO mcp_readonly;
   GRANT USAGE ON SCHEMA public TO mcp_readonly;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_readonly;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO mcp_readonly;
   ```

2. **Restrict query capabilities**:
   - Whitelist allowed tables/schemas
   - Implement query timeout limits
   - Add row limit defaults (e.g., `LIMIT 1000`)

3. **Use connection pooling**: Prevent connection exhaustion

4. **Audit logging**: Log all queries for compliance

5. **Network isolation**: Use private networks, VPNs, or SSH tunnels

---

### Setting Up Spark Cluster MCP Server

**Overview**: A Spark MCP server enables Claude to submit jobs, query data lakes, and interact with distributed data processing clusters.

**Architecture**:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│   Claude    │────▶│  Spark MCP  │────▶│   Spark Cluster     │
│             │◀────│   Server    │◀────│   (YARN/K8s/Standalone)
└─────────────┘     └─────────────┘     └─────────────────────┘
                           │                      │
                           │              ┌───────┴───────┐
                           │              ▼               ▼
                           │        ┌──────────┐   ┌──────────┐
                           │        │  HDFS    │   │   S3     │
                           │        │  Data    │   │   Data   │
                           │        └──────────┘   └──────────┘
                           │
                    ┌──────┴──────┐
                    │  Livy REST  │
                    │  Server     │
                    └─────────────┘
```

**Prerequisites**:

- Apache Spark cluster (Standalone, YARN, or Kubernetes)
- Apache Livy (REST interface for Spark) - recommended
- Or direct Spark Connect (Spark 3.4+)

**Option 1: Spark MCP via Livy REST API**

```python
# spark_livy_mcp_server.py
import asyncio
import aiohttp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("spark-mcp")

LIVY_URL = os.environ.get("LIVY_URL", "http://localhost:8998")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="spark_sql",
            description="Execute Spark SQL query on the cluster",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Spark SQL query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max rows to return",
                        "default": 100
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_tables",
            description="List tables in Spark catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "default": "default"
                    }
                }
            }
        ),
        Tool(
            name="describe_table",
            description="Get schema of a Spark table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {"type": "string"}
                },
                "required": ["table"]
            }
        ),
        Tool(
            name="submit_pyspark_job",
            description="Submit a PySpark job to the cluster",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "PySpark code to execute"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="get_job_status",
            description="Check status of a submitted Spark job",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "integer"},
                    "statement_id": {"type": "integer"}
                },
                "required": ["session_id", "statement_id"]
            }
        )
    ]

async def get_or_create_session():
    """Get existing Livy session or create new one"""
    async with aiohttp.ClientSession() as http:
        # Check for existing sessions
        async with http.get(f"{LIVY_URL}/sessions") as resp:
            sessions = (await resp.json())["sessions"]
            active = [s for s in sessions if s["state"] == "idle"]
            if active:
                return active[0]["id"]

        # Create new session
        async with http.post(
            f"{LIVY_URL}/sessions",
            json={
                "kind": "pyspark",
                "conf": {
                    "spark.sql.adaptive.enabled": "true",
                    "spark.sql.shuffle.partitions": "200"
                }
            }
        ) as resp:
            session = await resp.json()
            session_id = session["id"]

        # Wait for session to be ready
        while True:
            async with http.get(f"{LIVY_URL}/sessions/{session_id}") as resp:
                state = (await resp.json())["state"]
                if state == "idle":
                    return session_id
                elif state in ("error", "dead"):
                    raise Exception(f"Session failed: {state}")
            await asyncio.sleep(2)

async def execute_statement(session_id: int, code: str):
    """Execute code in Livy session"""
    async with aiohttp.ClientSession() as http:
        # Submit statement
        async with http.post(
            f"{LIVY_URL}/sessions/{session_id}/statements",
            json={"code": code}
        ) as resp:
            statement = await resp.json()
            statement_id = statement["id"]

        # Poll for completion
        while True:
            async with http.get(
                f"{LIVY_URL}/sessions/{session_id}/statements/{statement_id}"
            ) as resp:
                result = await resp.json()
                if result["state"] == "available":
                    return result["output"]
                elif result["state"] in ("error", "cancelled"):
                    return result["output"]
            await asyncio.sleep(1)

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    session_id = await get_or_create_session()

    if name == "spark_sql":
        query = arguments["query"]
        limit = arguments.get("limit", 100)

        # Wrap query with limit for safety
        code = f'''
result = spark.sql("""{query}""").limit({limit})
result.toPandas().to_json(orient="records")
'''
        output = await execute_statement(session_id, code)

        if output["status"] == "ok":
            return [TextContent(type="text", text=output["data"]["text/plain"])]
        else:
            return [TextContent(type="text", text=f"Error: {output['evalue']}")]

    elif name == "list_tables":
        database = arguments.get("database", "default")
        code = f'''
tables = spark.catalog.listTables("{database}")
[(t.name, t.tableType) for t in tables]
'''
        output = await execute_statement(session_id, code)
        return [TextContent(type="text", text=str(output["data"]["text/plain"]))]

    elif name == "describe_table":
        table = arguments["table"]
        code = f'spark.sql("DESCRIBE {table}").toPandas().to_json(orient="records")'
        output = await execute_statement(session_id, code)
        return [TextContent(type="text", text=output["data"]["text/plain"])]

    elif name == "submit_pyspark_job":
        code = arguments["code"]
        output = await execute_statement(session_id, code)

        if output["status"] == "ok":
            return [TextContent(
                type="text",
                text=f"Job completed successfully:\n{output['data'].get('text/plain', 'No output')}"
            )]
        else:
            return [TextContent(type="text", text=f"Job failed: {output['evalue']}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
```

**Option 2: Spark Connect MCP (Spark 3.4+)**

```python
# spark_connect_mcp_server.py
from pyspark.sql import SparkSession
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("spark-connect-mcp")

# Initialize Spark Connect client
spark = SparkSession.builder \
    .remote("sc://spark-master:15002") \
    .appName("MCP-Spark-Client") \
    .getOrCreate()

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="spark_sql",
            description="Execute Spark SQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 100}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="read_parquet",
            description="Read and query a Parquet file/directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "query": {"type": "string", "description": "Optional SQL to run on the data"}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="read_delta",
            description="Read from Delta Lake table",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "version": {"type": "integer", "description": "Optional version for time travel"}
                },
                "required": ["path"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "spark_sql":
            limit = arguments.get("limit", 100)
            df = spark.sql(arguments["query"]).limit(limit)
            result = df.toPandas().to_json(orient="records", indent=2)
            return [TextContent(type="text", text=result)]

        elif name == "read_parquet":
            df = spark.read.parquet(arguments["path"])
            if "query" in arguments:
                df.createOrReplaceTempView("parquet_data")
                df = spark.sql(arguments["query"])
            result = df.limit(100).toPandas().to_json(orient="records", indent=2)
            return [TextContent(type="text", text=result)]

        elif name == "read_delta":
            reader = spark.read.format("delta")
            if "version" in arguments:
                reader = reader.option("versionAsOf", arguments["version"])
            df = reader.load(arguments["path"])
            result = df.limit(100).toPandas().to_json(orient="records", indent=2)
            return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

**Claude Code Configuration for Spark MCP**:

```json
{
  "mcpServers": {
    "spark": {
      "command": "python",
      "args": ["/path/to/spark_livy_mcp_server.py"],
      "env": {
        "LIVY_URL": "http://spark-cluster:8998",
        "SPARK_HOME": "/opt/spark",
        "PYSPARK_PYTHON": "/usr/bin/python3"
      }
    }
  }
}
```

**Spark MCP Security Best Practices**:

1. **Use Kerberos authentication** for secure clusters:

   ```python
   spark = SparkSession.builder \
       .config("spark.kerberos.principal", "user@REALM") \
       .config("spark.kerberos.keytab", "/path/to/keytab") \
       .getOrCreate()
   ```

2. **Implement resource limits**:

   ```python
   # Limit resources per MCP session
   spark.conf.set("spark.executor.memory", "2g")
   spark.conf.set("spark.executor.cores", "2")
   spark.conf.set("spark.sql.shuffle.partitions", "100")
   ```

3. **Query sandboxing**:
   - Whitelist allowed databases/tables
   - Implement query cost estimation before execution
   - Set maximum result sizes

4. **Audit all operations**: Log queries with user context

5. **Use service accounts with minimal permissions**

**Spark MCP Performance Tips**:

| Tip | Implementation |
| --- | -------------- |
| Connection pooling | Reuse Spark sessions across requests |
| Result caching | Cache frequent query results |
| Async execution | Use background jobs for long-running queries |
| Sampling | Use `TABLESAMPLE` for large table exploration |
| Partition pruning | Always filter on partition columns |

---

### MCP Authentication for Claude Code

MCP (Model Context Protocol) servers often connect to sensitive resources (databases, APIs, internal services). Proper authentication ensures only authorized clients can access these servers.

**Authentication Methods Overview**:

| Method | Use Case | Security Level |
| ------ | -------- | -------------- |
| **Environment Variables** | Local development, simple deployments | Basic |
| **API Key Headers** | Third-party API access | Medium |
| **OAuth 2.0** | Enterprise services, cloud APIs | High |
| **mTLS (Mutual TLS)** | High-security environments | Very High |
| **OIDC Tokens** | SSO-integrated services | High |

---

#### 1. Environment Variable Authentication

The simplest approach—credentials passed via environment variables in the MCP configuration.

**Claude Code Configuration** (`~/.claude.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "database-server": {
      "command": "node",
      "args": ["./mcp-servers/db-server.js"],
      "env": {
        "DB_HOST": "localhost",
        "DB_USER": "app_user",
        "DB_PASSWORD": "${DB_PASSWORD}",
        "DB_NAME": "production"
      }
    }
  }
}
```

**Security Best Practices**:

- Never commit credentials to version control
- Use `${VAR_NAME}` syntax to reference shell environment variables
- Store secrets in a `.env` file excluded from git (add to `.gitignore`)
- Consider using a secrets manager for production

**Loading from .env files**:

```bash
# .env file (add to .gitignore!)
DB_PASSWORD=your-secret-password
API_KEY=sk-xxxxxxxxxxxx
```

```bash
# Load before running Claude Code
source .env && claude
```

---

#### 2. API Key Header Authentication

For MCP servers connecting to REST APIs that require API key authentication.

**MCP Server Implementation (TypeScript)**:

```typescript
// api-mcp-server.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  console.error("API_KEY environment variable required");
  process.exit(1);
}

const server = new Server(
  { name: "api-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// Use API key in requests
async function authenticatedFetch(url: string, options: RequestInit = {}) {
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      "Authorization": `Bearer ${API_KEY}`,
      "X-API-Key": API_KEY,  // Some APIs use this header instead
    },
  });
}

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "query_api",
      description: "Query the authenticated API",
      inputSchema: {
        type: "object",
        properties: {
          endpoint: { type: "string" },
        },
        required: ["endpoint"],
      },
    },
  ],
}));

const transport = new StdioServerTransport();
await server.connect(transport);
```

**Claude Code Configuration**:

```json
{
  "mcpServers": {
    "api-server": {
      "command": "npx",
      "args": ["tsx", "./mcp-servers/api-mcp-server.ts"],
      "env": {
        "API_KEY": "${MY_SERVICE_API_KEY}"
      }
    }
  }
}
```

---

#### 3. OAuth 2.0 Authentication

For MCP servers that connect to OAuth-protected services (Google, Microsoft, GitHub, etc.).

**OAuth 2.0 Flow for MCP Servers**:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│ Claude Code │────▶│  MCP Server │────▶│ OAuth Provider  │
│             │     │             │     │ (Google, etc.)  │
└─────────────┘     └─────────────┘     └─────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        ┌──────────┐            ┌──────────────┐
        │  Token   │            │  Protected   │
        │  Storage │            │   Resource   │
        └──────────┘            └──────────────┘
```

**OAuth MCP Server Implementation (Python)**:

```python
# oauth_mcp_server.py
import os
import json
import asyncio
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from mcp.server import Server
from mcp.server.stdio import stdio_server

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
TOKEN_PATH = Path.home() / '.claude' / 'oauth_tokens' / 'google_drive.json'
CREDENTIALS_PATH = Path(os.environ.get('GOOGLE_CREDENTIALS_PATH', 'credentials.json'))

server = Server("google-drive-mcp")

def get_credentials():
    """Get or refresh OAuth credentials."""
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return creds

@server.list_tools()
async def list_tools():
    return [
        {
            "name": "list_drive_files",
            "description": "List files from Google Drive",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                }
            }
        }
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "list_drive_files":
        creds = get_credentials()
        # Use credentials to access Google Drive API
        # ... implementation

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
```

**Claude Code Configuration for OAuth**:

```json
{
  "mcpServers": {
    "google-drive": {
      "command": "python",
      "args": ["./mcp-servers/oauth_mcp_server.py"],
      "env": {
        "GOOGLE_CREDENTIALS_PATH": "~/.claude/credentials/google_oauth.json"
      }
    }
  }
}
```

---

#### 4. Token-Based Authentication with Refresh

For services requiring bearer tokens with automatic refresh.

**Token Manager MCP Server**:

```typescript
// token-auth-mcp-server.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import * as fs from "fs";
import * as path from "path";

interface TokenData {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

class TokenManager {
  private tokenPath: string;
  private tokenData: TokenData | null = null;
  private clientId: string;
  private clientSecret: string;
  private tokenEndpoint: string;

  constructor() {
    this.tokenPath = path.join(
      process.env.HOME || "",
      ".claude",
      "tokens",
      "service_token.json"
    );
    this.clientId = process.env.CLIENT_ID || "";
    this.clientSecret = process.env.CLIENT_SECRET || "";
    this.tokenEndpoint = process.env.TOKEN_ENDPOINT || "";
    this.loadToken();
  }

  private loadToken(): void {
    if (fs.existsSync(this.tokenPath)) {
      this.tokenData = JSON.parse(fs.readFileSync(this.tokenPath, "utf-8"));
    }
  }

  private saveToken(): void {
    const dir = path.dirname(this.tokenPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
    }
    fs.writeFileSync(this.tokenPath, JSON.stringify(this.tokenData), {
      mode: 0o600,
    });
  }

  async getAccessToken(): Promise<string> {
    if (this.tokenData && Date.now() < this.tokenData.expiresAt - 60000) {
      return this.tokenData.accessToken;
    }

    // Refresh the token
    const response = await fetch(this.tokenEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "refresh_token",
        refresh_token: this.tokenData?.refreshToken || "",
        client_id: this.clientId,
        client_secret: this.clientSecret,
      }),
    });

    const data = await response.json();
    this.tokenData = {
      accessToken: data.access_token,
      refreshToken: data.refresh_token || this.tokenData?.refreshToken || "",
      expiresAt: Date.now() + data.expires_in * 1000,
    };
    this.saveToken();
    return this.tokenData.accessToken;
  }
}

const tokenManager = new TokenManager();

// Use tokenManager.getAccessToken() in your tool implementations
```

**Configuration**:

```json
{
  "mcpServers": {
    "token-service": {
      "command": "npx",
      "args": ["tsx", "./mcp-servers/token-auth-mcp-server.ts"],
      "env": {
        "CLIENT_ID": "${SERVICE_CLIENT_ID}",
        "CLIENT_SECRET": "${SERVICE_CLIENT_SECRET}",
        "TOKEN_ENDPOINT": "https://auth.example.com/oauth/token"
      }
    }
  }
}
```

---

#### 5. Mutual TLS (mTLS) Authentication

For high-security environments requiring certificate-based authentication.

**mTLS MCP Server Configuration**:

```typescript
// mtls-mcp-server.ts
import * as https from "https";
import * as fs from "fs";

const httpsAgent = new https.Agent({
  cert: fs.readFileSync(process.env.CLIENT_CERT_PATH || ""),
  key: fs.readFileSync(process.env.CLIENT_KEY_PATH || ""),
  ca: fs.readFileSync(process.env.CA_CERT_PATH || ""),
  rejectUnauthorized: true,
});

// Use httpsAgent in fetch/axios calls
async function secureRequest(url: string) {
  const response = await fetch(url, {
    // @ts-ignore - Node.js specific
    agent: httpsAgent,
  });
  return response;
}
```

**Configuration**:

```json
{
  "mcpServers": {
    "mtls-service": {
      "command": "node",
      "args": ["./mcp-servers/mtls-mcp-server.js"],
      "env": {
        "CLIENT_CERT_PATH": "~/.claude/certs/client.crt",
        "CLIENT_KEY_PATH": "~/.claude/certs/client.key",
        "CA_CERT_PATH": "~/.claude/certs/ca.crt"
      }
    }
  }
}
```

---

#### 6. Secrets Management Integration

For production environments, integrate with secrets managers.

**AWS Secrets Manager Example**:

```typescript
// secrets-mcp-server.ts
import {
  SecretsManagerClient,
  GetSecretValueCommand,
} from "@aws-sdk/client-secrets-manager";

const client = new SecretsManagerClient({ region: process.env.AWS_REGION });

async function getSecret(secretName: string): Promise<Record<string, string>> {
  const response = await client.send(
    new GetSecretValueCommand({ SecretId: secretName })
  );
  return JSON.parse(response.SecretString || "{}");
}

// Usage in MCP server
const dbCredentials = await getSecret("prod/database/credentials");
const connection = await connectToDatabase({
  host: dbCredentials.host,
  user: dbCredentials.username,
  password: dbCredentials.password,
});
```

**HashiCorp Vault Example**:

```typescript
import Vault from "node-vault";

const vault = Vault({
  apiVersion: "v1",
  endpoint: process.env.VAULT_ADDR,
  token: process.env.VAULT_TOKEN,
});

async function getVaultSecret(path: string) {
  const result = await vault.read(path);
  return result.data.data;
}
```

---

## Guidelines & Best Practices

### General MCP Best Practices

1. Use official/verified MCP servers when possible
2. Implement proper error handling for MCP calls
3. Design idempotent MCP operations where possible
4. Document MCP server capabilities clearly
5. Monitor MCP server health and availability

### Database MCP Best Practices

1. **Always use read-only credentials** for exploration/analysis use cases
2. **Implement query timeouts** to prevent runaway queries
3. **Add result limits** by default (e.g., `LIMIT 1000`)
4. **Use connection pooling** to manage database connections efficiently
5. **Log all queries** for auditing and debugging
6. **Validate and sanitize inputs** to prevent SQL injection
7. **Use parameterized queries** where supported
8. **Implement schema-level access control** - only expose necessary tables
9. **Consider query cost estimation** before execution
10. **Cache metadata** (table schemas, statistics) to reduce database load

### Spark MCP Best Practices

1. **Reuse Spark sessions** - session creation is expensive
2. **Implement job queuing** for resource management
3. **Set memory and core limits** per MCP request
4. **Use Spark SQL over DataFrame API** for simpler query validation
5. **Implement result size limits** to prevent memory issues
6. **Support async job submission** for long-running operations
7. **Provide job status tracking** for submitted jobs
8. **Use Delta Lake** for ACID transactions and time travel
9. **Implement query explain plans** to help users understand performance
10. **Cache frequently accessed tables** using `spark.catalog.cacheTable()`

### MCP Security Checklist

```txt
□ Use dedicated service accounts with minimal permissions
□ Store credentials in environment variables, not config files
□ Enable TLS/SSL for all connections
□ Implement authentication for MCP server access
□ Add rate limiting to prevent abuse
□ Log all tool invocations with timestamps
□ Validate all input parameters
□ Sanitize outputs to prevent data leakage
□ Use network isolation (VPN, private subnets)
□ Regular security audits of MCP server code
```

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [Anthropic MCP Documentation](https://docs.anthropic.com/en/docs/agents-and-tools/mcp)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Apache Livy Documentation](https://livy.apache.org/)
- [Spark Connect Guide](https://spark.apache.org/docs/latest/spark-connect-overview.html)
- [asyncpg (PostgreSQL)](https://magicstack.github.io/asyncpg/)
- [Building MCP Servers Guide](https://modelcontextprotocol.io/docs/concepts/servers)
