# Retrieval-Augmented Generation (RAG) & Vector Search

## Table of Contents

- [Retrieval-Augmented Generation (RAG) \& Vector Search](#retrieval-augmented-generation-rag--vector-search)
  - [Table of Contents](#table-of-contents)
  - [Sub-topics](#sub-topics)
  - [Explanation](#explanation)
    - [Setting Up a Public RAG Server for Claude Code](#setting-up-a-public-rag-server-for-claude-code)
      - [Complete RAG MCP Server Implementation](#complete-rag-mcp-server-implementation)
      - [Deploying to Production](#deploying-to-production)
      - [Claude Code Configuration](#claude-code-configuration)
      - [Security Considerations for Public RAG Servers](#security-considerations-for-public-rag-servers)
      - [Using Local Embedding Models (No API Costs)](#using-local-embedding-models-no-api-costs)
  - [Guidelines \& Best Practices](#guidelines--best-practices)
  - [Resources](#resources)

## Sub-topics

- RAG (Retrieval-Augmented Generation)
- Embedding models
- Vector databases (Qdrant vs Milvus vs Pinecone)
- Fine-tuning vs RAG
- Rerankers (cross-encoder, BGE reranker, reranker fine-tuning)
- Semantic chunking
- Cosine similarity vs Dot product similarity
- Public RAG server for Claude Code

## Explanation

**RAG** combines LLMs with external knowledge retrieval. Instead of relying solely on model parameters, RAG fetches relevant documents from a knowledge base to ground responses in factual, up-to-date information.

**Embedding models** convert text into dense vector representations that capture semantic meaning (e.g., OpenAI Ada, BGE, E5, Cohere Embed).

**Vector databases** store and efficiently search these embeddings:

| Database | Type | Best For |
|----------|------|----------|
| **Qdrant** | Open-source, self-hosted | Full control, cost-sensitive |
| **Milvus** | Open-source, distributed | Large-scale enterprise |
| **Pinecone** | Managed SaaS | Quick setup, serverless |

**Fine-tuning vs RAG**:

- Fine-tuning: Bakes knowledge into model weights; best for domain-specific behavior
- RAG: Dynamic retrieval; best for frequently changing data, citations needed

**Rerankers** (cross-encoders, BGE reranker) re-score initial retrieval results for higher precision. They process query-document pairs jointly, unlike bi-encoders.

**Similarity metrics**:

- Cosine similarity: Direction-based, normalized (range -1 to 1)
- Dot product: Magnitude-sensitive, faster computation

---

### Setting Up a Public RAG Server for Claude Code

A public RAG server allows Claude Code to query external knowledge bases via MCP, enabling context-aware responses grounded in your documentation, codebase, or domain-specific data.

**Architecture Overview**:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Claude Code   │────▶│   RAG MCP       │────▶│  Vector DB      │
│                 │◀────│   Server        │◀────│  (Qdrant/etc)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              ┌──────────┐         ┌──────────────┐
              │ Embedding│         │  Document    │
              │  Model   │         │  Store       │
              └──────────┘         └──────────────┘
```

**Deployment Options**:

| Option | Pros | Cons | Best For |
| ------ | ---- | ---- | -------- |
| **Self-hosted (VPS)** | Full control, cost-effective | Maintenance overhead | Teams, production |
| **Serverless (AWS Lambda)** | Auto-scaling, pay-per-use | Cold starts, complexity | Variable load |
| **Container (Railway/Fly.io)** | Easy deployment, managed | Monthly costs | Quick setup |
| **Local + Tunnel (ngrok)** | Free, simple | Unstable, not for production | Development/testing |

---

#### Complete RAG MCP Server Implementation

**Prerequisites**:

- Python 3.10+ or Node.js 18+
- Vector database (Qdrant recommended for self-hosting)
- Embedding model access (OpenAI, Cohere, or local)

**Project Structure**:

```
rag-mcp-server/
├── server.py              # Main MCP server
├── embeddings.py          # Embedding generation
├── indexer.py             # Document indexing
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

**Step 1: Core RAG MCP Server (Python)**

```python
# server.py
import os
import asyncio
from typing import Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configuration
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "documents")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize clients
qdrant = QdrantClient(url=QDRANT_URL)
server = Server("rag-server")

async def get_embedding(text: str) -> list[float]:
    """Generate embedding using OpenAI API."""
    import openai
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_documents",
            description="Search the knowledge base for relevant documents",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 5)",
                        "default": 5
                    },
                    "score_threshold": {
                        "type": "number",
                        "description": "Minimum similarity score (0-1)",
                        "default": 0.7
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="add_document",
            description="Add a document to the knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Document content"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata (title, source, etc.)"
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="list_collections",
            description="List available document collections",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search_documents":
        query = arguments["query"]
        limit = arguments.get("limit", 5)
        threshold = arguments.get("score_threshold", 0.7)

        # Generate query embedding
        query_vector = await get_embedding(query)

        # Search Qdrant
        results = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            score_threshold=threshold
        )

        if not results:
            return [TextContent(type="text", text="No relevant documents found.")]

        # Format results
        output = []
        for i, result in enumerate(results, 1):
            payload = result.payload
            output.append(
                f"**Result {i}** (score: {result.score:.3f})\n"
                f"Title: {payload.get('title', 'Untitled')}\n"
                f"Source: {payload.get('source', 'Unknown')}\n"
                f"Content: {payload.get('content', '')[:500]}...\n"
            )

        return [TextContent(type="text", text="\n---\n".join(output))]

    elif name == "add_document":
        content = arguments["content"]
        metadata = arguments.get("metadata", {})

        # Generate embedding
        embedding = await get_embedding(content)

        # Create point ID
        import uuid
        point_id = str(uuid.uuid4())

        # Upsert to Qdrant
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={"content": content, **metadata}
                )
            ]
        )

        return [TextContent(type="text", text=f"Document added with ID: {point_id}")]

    elif name == "list_collections":
        collections = qdrant.get_collections()
        names = [c.name for c in collections.collections]
        return [TextContent(type="text", text=f"Collections: {', '.join(names)}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]

def ensure_collection():
    """Create collection if it doesn't exist."""
    collections = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in collections:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

async def main():
    ensure_collection()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
```

**Step 2: Document Indexer**

```python
# indexer.py
import os
import asyncio
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import openai
import hashlib

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "documents")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

qdrant = QdrantClient(url=QDRANT_URL)
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks

def get_embedding(text: str) -> list[float]:
    """Generate embedding for text."""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def index_file(file_path: Path):
    """Index a single file."""
    content = file_path.read_text(encoding="utf-8")
    chunks = chunk_text(content)

    points = []
    for i, chunk in enumerate(chunks):
        # Create deterministic ID from content hash
        chunk_id = hashlib.md5(f"{file_path}:{i}:{chunk[:100]}".encode()).hexdigest()

        embedding = get_embedding(chunk)
        points.append(
            PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    "content": chunk,
                    "source": str(file_path),
                    "title": file_path.name,
                    "chunk_index": i
                }
            )
        )

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Indexed {len(points)} chunks from {file_path}")

def index_directory(directory: Path, extensions: list[str] = None):
    """Index all files in a directory."""
    extensions = extensions or [".md", ".txt", ".py", ".js", ".ts"]

    for file_path in directory.rglob("*"):
        if file_path.suffix in extensions and file_path.is_file():
            try:
                index_file(file_path)
            except Exception as e:
                print(f"Error indexing {file_path}: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python indexer.py <directory>")
        sys.exit(1)

    index_directory(Path(sys.argv[1]))
```

**Step 3: Requirements**

```text
# requirements.txt
mcp>=1.0.0
qdrant-client>=1.7.0
openai>=1.0.0
python-dotenv>=1.0.0
uvicorn>=0.24.0
```

**Step 4: Docker Deployment**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "server.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  rag-server:
    build: .
    environment:
      - QDRANT_URL=http://qdrant:6333
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - COLLECTION_NAME=documents
    depends_on:
      - qdrant
    ports:
      - "8080:8080"

volumes:
  qdrant_data:
```

---

#### Deploying to Production

**Option A: Railway Deployment**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init

# Set environment variables
railway variables set OPENAI_API_KEY=sk-xxx
railway variables set QDRANT_URL=https://your-qdrant-instance.cloud

# Deploy
railway up
```

**Option B: Fly.io Deployment**

```toml
# fly.toml
app = "rag-mcp-server"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  COLLECTION_NAME = "documents"

[http_service]
  internal_port = 8080
  force_https = true

[[services]]
  protocol = "tcp"
  internal_port = 8080

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

```bash
fly launch
fly secrets set OPENAI_API_KEY=sk-xxx QDRANT_URL=https://xxx
fly deploy
```

**Option C: HTTP Transport for Remote Access**

For public deployment, wrap the MCP server with HTTP transport:

```python
# http_server.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from server import server  # Import your MCP server

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Handle MCP requests over HTTP."""
    body = await request.json()

    # Process MCP request
    response = await server.handle_request(body)

    return Response(
        content=response.model_dump_json(),
        media_type="application/json"
    )

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

#### Claude Code Configuration

**Local MCP Server** (stdio transport):

```json
{
  "mcpServers": {
    "rag": {
      "command": "python",
      "args": ["/path/to/rag-mcp-server/server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "COLLECTION_NAME": "my-docs"
      }
    }
  }
}
```

**Remote MCP Server** (HTTP transport):

```json
{
  "mcpServers": {
    "rag-remote": {
      "type": "http",
      "url": "https://your-rag-server.fly.dev/mcp",
      "headers": {
        "Authorization": "Bearer ${RAG_API_KEY}"
      }
    }
  }
}
```

---

#### Security Considerations for Public RAG Servers

| Concern | Mitigation |
| ------- | ---------- |
| **Unauthorized access** | API key authentication, IP allowlisting |
| **Data exfiltration** | Role-based access to collections |
| **Injection attacks** | Sanitize queries before embedding |
| **Cost abuse** | Rate limiting, usage quotas |
| **Data privacy** | Encrypt data at rest, audit logging |

**Adding API Key Authentication**:

```python
# auth_middleware.py
from fastapi import Request, HTTPException
import os

VALID_API_KEYS = set(os.environ.get("API_KEYS", "").split(","))

async def verify_api_key(request: Request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")

    api_key = auth_header.replace("Bearer ", "")
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
```

---

#### Using Local Embedding Models (No API Costs)

For self-contained deployments without external API dependencies:

```python
# local_embeddings.py
from sentence_transformers import SentenceTransformer

# Load model once at startup
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

def get_embedding(text: str) -> list[float]:
    """Generate embedding using local model."""
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
```

**Model Options**:

| Model | Dimensions | Quality | Speed |
| ----- | ---------- | ------- | ----- |
| `BAAI/bge-small-en-v1.5` | 384 | Good | Fast |
| `BAAI/bge-base-en-v1.5` | 768 | Better | Medium |
| `BAAI/bge-large-en-v1.5` | 1024 | Best | Slower |
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | Good | Very Fast |

Update Qdrant collection for different dimensions:

```python
qdrant.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)  # Match model
)
```

## Guidelines & Best Practices

1. Use semantic chunking over fixed-size chunking for better context preservation
2. Implement a two-stage retrieval: fast bi-encoder retrieval → reranker refinement
3. Evaluate embedding models on your specific domain before committing
4. Consider hybrid search (dense + sparse/BM25) for better recall
5. Tune chunk size and overlap based on your content type

## Resources

- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [Pinecone Learning Center](https://www.pinecone.io/learn/)
- [BGE Embedding Models](https://huggingface.co/BAAI/bge-large-en-v1.5)
- [MTEB Leaderboard (Embedding Benchmarks)](https://huggingface.co/spaces/mteb/leaderboard)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
