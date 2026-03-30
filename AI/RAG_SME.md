# RAG Learning Roadmap: Beginner to Production SME

---

## Phase 1 — Foundations (2–4 weeks)

**Goal:** Understand what RAG is and why it exists.

**Concepts:**

- What is RAG? (vs. fine-tuning, vs. pure LLM)
- How LLMs work at a high level (tokens, context windows, hallucinations)
- Embeddings — what they are, why they matter
- Vector similarity (cosine, dot product)

**Hands-on:**

- Call an LLM API (OpenAI, Anthropic, etc.) with a simple prompt
- Use a pre-built embedding model (e.g., `sentence-transformers`)
- Manually embed 10 documents, compute similarity between a query and docs

**Resources:**

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) (skim)
- LangChain / LlamaIndex "Getting Started" docs
- OpenAI Embeddings guide

---

## Phase 2 — Core RAG Pipeline (3–5 weeks)

**Goal:** Build a working RAG system end-to-end.

**Concepts:**

- Chunking strategies (fixed-size, semantic, sentence-window)
- Vector databases (Chroma, FAISS, Pinecone, Weaviate, pgvector)
- Retrieval: dense vs. sparse (BM25) vs. hybrid
- Prompt engineering for RAG (system prompts, context injection)

**Hands-on:**

- Build a Q&A bot over a PDF using LangChain or LlamaIndex
- Try 3 different chunking strategies, compare retrieval quality
- Set up a local vector DB (Chroma or FAISS)

### Key Skills

```text
Document → Chunk → Embed → Store → Query → Retrieve → Generate
```

---

## Phase 3 — Evaluation & Quality (3–4 weeks)

**Goal:** Measure and improve RAG quality systematically.

**Concepts:**

- Retrieval metrics: Recall@K, MRR, NDCG
- Generation metrics: faithfulness, answer relevance, context precision
- RAG evaluation frameworks: RAGAS, TruLens, DeepEval
- Building a golden dataset (ground truth Q&A pairs)

**Hands-on:**

- Set up RAGAS on your pipeline
- Build a small eval dataset (50–100 Q&A pairs from your company docs)
- Identify your biggest failure modes (retrieval miss vs. hallucination)

---

## Phase 4 — Advanced Retrieval (4–6 weeks)

**Goal:** Fix the hard retrieval problems.

**Concepts:**

- Query rewriting & HyDE (Hypothetical Document Embeddings)
- Multi-query retrieval
- Re-ranking (cross-encoders, Cohere Rerank)
- Metadata filtering
- Parent-child chunking
- Knowledge graphs as a retrieval layer

**Hands-on:**

- Implement hybrid search (BM25 + dense) with RRF fusion
- Add a re-ranker to your pipeline, measure improvement on your eval set
- Use metadata filters (date, department, source) to scope retrieval

---

## Phase 5 — Production Architecture (4–6 weeks)

**Goal:** Make it reliable, scalable, and maintainable.

**Concepts:**

- Ingestion pipelines (batch vs. streaming, change detection)
- Caching (semantic caching with GPTCache or Redis)
- Latency optimization (async, batching, embedding caching)
- Observability: tracing with LangSmith, Arize, or custom logging
- Security: prompt injection, data leakage between tenants
- Access control — who can see what documents

### Architecture Patterns

```text
Ingest Pipeline        Query Pipeline
─────────────          ──────────────
Source → Parse         Query → Rewrite
       → Chunk                → Retrieve (hybrid)
       → Embed                → Re-rank
       → Store                → Filter (ACL)
       → Index                → Generate
                              → Log + Trace
```

**Hands-on:**

- Build an async ingestion pipeline with chunking + embedding workers
- Add end-to-end tracing (log query, retrieved chunks, final answer)
- Implement a simple semantic cache

---

## Phase 6 — Enterprise & SME Level (ongoing)

**Goal:** Own RAG decisions for the whole company.

**Advanced Topics:**

- **Agentic RAG** — LLM decides when/how to retrieve, multi-hop reasoning
- **Long-context trade-offs** — when to use 128k context vs. RAG
- **Fine-tuning embeddings** on your domain data
- **GraphRAG** — Microsoft's graph-based approach for complex documents
- **Multi-modal RAG** — images, tables, PDFs with structure
- **Cost optimization** — smaller models, tiered retrieval, batching

**Organizational Skills:**

- Choosing a vector DB for your scale and team (managed vs. self-hosted)
- Data governance — versioning, lineage, deletion (GDPR)
- Making the build vs. buy decision (LangChain vs. custom vs. managed)
- Communicating RAG quality to non-technical stakeholders

---

## Practical Track for Your Company

Since you're building for a company, prioritize in this order:

1. **What are your documents?** (PDFs, wikis, databases, emails)
2. **What are the user queries?** (factual lookup, summarization, comparison)
3. **What does failure look like?** (wrong answer vs. no answer vs. hallucination)
4. **Who owns the data pipeline?** (point to a single owner early)

---

## Recommended Stack to Learn On

| Layer | Tool |
| --- | --- |
| Orchestration | LangChain or LlamaIndex |
| Embeddings | `text-embedding-3-small` (OpenAI) or `bge-m3` (open source) |
| Vector DB | Chroma (local) → pgvector (prod) or Pinecone |
| Evaluation | RAGAS |
| Observability | LangSmith or Arize Phoenix |
| LLM | Claude (Anthropic) or GPT-4o |

---

## RAG Pipeline Deep Dive: GitHub Repos + Wiki Pages

---

## The Pipeline in Full

```text
Source Docs
    │
    ▼
[DOCUMENT]  — parse raw content into clean text
    │
    ▼
[CHUNK]     — split into retrieval-sized pieces
    │
    ▼
[EMBED]     — convert text to vectors
    │
    ▼
[STORE]     — persist vectors + metadata
    │
    ▼
[QUERY]     — user asks a question
    │
    ▼
[RETRIEVE]  — find relevant chunks
    │
    ▼
[GENERATE]  — LLM answers using retrieved context
```

---

## Step 1 — Document (Ingestion & Parsing)

Turn your raw sources into clean, structured text.

### GitHub Repos

Your repo contains multiple content types — each needs different handling:

| File Type | Parser | What to Extract |
| --- | --- | --- |
| `.md` / `.rst` | markdown parser | headings, body text, code blocks |
| `.py` / `.ts` / etc. | AST parser or raw | functions, classes, docstrings, comments |
| `README.md` | markdown parser | treat as high-value, weight it higher |
| `CHANGELOG.md` | markdown parser | version history, feature notes |
| `.yaml` / `.json` configs | key-value extractor | config keys + descriptions |
| Inline comments | language parser | strip `#`, `//`, `/* */` |

**Key decisions:**

- Do you index **source code itself** or only **documentation within code**?
- Do you index every branch or only `main`?
- Do you index commit messages? (useful for "why was X changed")

**Tooling:**

```python
# GitHub API — fetch repo contents
from github import Github
g = Github("token")
repo = g.get_repo("your-org/your-repo")
contents = repo.get_contents("")  # recursive tree walk

# For code parsing
import ast  # Python AST
import tree_sitter  # Multi-language AST parsing
```

### Wiki Pages

Wikis (Confluence, GitHub Wiki, Notion, etc.) have their own quirks:

| Wiki Type | Access Method | Gotchas |
| --- | --- | --- |
| GitHub Wiki | `git clone` the wiki repo | It's a separate git repo |
| Confluence | REST API | Pages nest deeply — preserve hierarchy |
| Notion | Notion API | Blocks-based, not flat text |

**Key decisions:**

- Preserve page hierarchy in metadata (parent page, breadcrumb)
- Strip navigation boilerplate, footers, sidebar content
- Handle `[[internal links]]` — they carry meaning

**Cleaning checklist for both sources:**

```text
✓ Remove HTML tags
✓ Normalize whitespace
✓ Preserve code blocks as-is (do not strip)
✓ Keep headings — they are context signals
✓ Strip boilerplate (nav bars, "last edited by...", footers)
✓ Decode special characters
```

### Step 1 Terminology

| Term | Meaning |
| --- | --- |
| **Ingestion** | The process of reading raw source files and preparing them for the AI pipeline |
| **Parsing** | Extracting structured content from a file (e.g., pulling text out of a PDF or code out of a `.py` file) |
| **AST (Abstract Syntax Tree)** | A tree-shaped representation of code structure — lets you find functions, classes, and comments without reading raw text |
| **`.rst` (reStructuredText)** | A markup language similar to Markdown, commonly used in Python project documentation |
| **Docstrings** | Text written inside a function or class in code to describe what it does (e.g., `"""Validates JWT and returns user."""`) |
| **GitHub API** | A programmatic interface that lets you read files, commits, and metadata from GitHub without manually downloading anything |
| **`tree-sitter`** | A parsing library that understands many programming languages — used to detect function/class boundaries in code |
| **Boilerplate** | Repetitive, non-informative content like nav bars, footers, and "last edited by" lines — stripped during cleaning |
| **Breadcrumb** | A trail showing a page's location in a hierarchy, e.g., `Auth > JWT > Validation` |

---

## Step 2 — Chunk

Split documents into pieces small enough to fit in context, large enough to be meaningful.

### Why chunking is hard

Too small → chunk has no context ("it returns True" — what does?)
Too large → irrelevant content dilutes retrieval signal

### Chunking strategies ranked for your use case

**1. Markdown Header Chunking** ← best for wikis
Split on `#`, `##`, `###` boundaries. Each chunk = one section.

```text
## Authentication Flow        ← chunk boundary
... content ...

## Token Refresh              ← chunk boundary
... content ...
```

Preserves semantic units. Headers become metadata.

**2. Code-aware Chunking** ← best for repos
Split on function/class boundaries, not arbitrary character counts.

```python
# Good chunk: one complete function
def authenticate_user(token: str) -> User:
    """Validates JWT and returns user."""
    ...

# Bad chunk: function split mid-body
def authenticate_user(token: str) -> User:
    """Validates JWT and returns
    # ← chunk cut here — loses meaning
```

Use AST parsing to detect boundaries.

**3. Parent-Child Chunking** ← best for retrieval precision

- **Child chunks** (256 tokens) — used for retrieval (precise matching)
- **Parent chunks** (1024 tokens) — sent to LLM (full context)

```text
Parent: Entire "Authentication" section
  ├── Child: "JWT validation logic"
  ├── Child: "Token expiry handling"
  └── Child: "Refresh token flow"

Query matches a child → LLM gets the full parent
```

**4. Sliding Window** ← fallback for unstructured content

```text
Chunk size: 512 tokens
Overlap:    50 tokens  ← prevents context loss at boundaries
```

### Metadata to attach to every chunk

This is what enables filtering later:

```json
{
  "source_type": "github_repo | wiki",
  "repo": "your-org/payments-service",
  "file_path": "src/auth/jwt.py",
  "language": "python",
  "chunk_type": "function | class | section | prose",
  "heading_breadcrumb": "Auth > JWT > Validation",
  "last_modified": "2026-01-15",
  "author": "jane.doe",
  "page_title": "Authentication Flow",
  "line_start": 42,
  "line_end": 89
}
```

### Step 2 Terminology

| Term | Meaning |
| --- | --- |
| **Chunk** | A small piece of a document that gets individually embedded and stored — the basic unit of retrieval |
| **Token** | The unit LLMs use to measure text length. Roughly 1 token ≈ ¾ of a word. "512 tokens" ≈ ~380 words |
| **Context window** | The maximum amount of text an LLM can read at once. Chunks must fit inside this limit |
| **Semantic unit** | A piece of text that carries a complete, self-contained meaning (e.g., a full function, a full section) |
| **Markdown Header Chunking** | Splitting a document at heading boundaries (`#`, `##`) so each chunk = one logical section |
| **Code-aware Chunking** | Splitting code at function or class boundaries instead of arbitrary character counts |
| **Parent-Child Chunking** | A two-level strategy: small child chunks are used for precise retrieval, but the larger parent chunk is sent to the LLM for full context |
| **Sliding Window** | A chunking method where consecutive chunks overlap slightly to avoid losing meaning at split boundaries |
| **Overlap** | The number of tokens shared between adjacent chunks to preserve context across boundaries |
| **Metadata** | Extra information attached to each chunk describing where it came from (repo, file, author, date) — used for filtering later |

---

## Step 3 — Embed

Convert each chunk into a vector that captures its meaning.

### How it works

```text
"How do I refresh a JWT token?"
        ↓  embedding model
[0.23, -0.87, 0.41, ... 1536 dimensions]

"Token refresh endpoint accepts POST /auth/refresh"
        ↓  embedding model
[0.21, -0.89, 0.38, ... 1536 dimensions]

cosine similarity → 0.94  ← very similar, will be retrieved
```

### Model choices for your use case

| Model | Best For | Cost | Dimensions |
| --- | --- | --- | --- |
| `text-embedding-3-small` (OpenAI) | general docs + wikis | low | 1536 |
| `text-embedding-3-large` (OpenAI) | higher accuracy | medium | 3072 |
| `bge-m3` (open source) | self-hosted, multilingual | free | 1024 |
| `nomic-embed-code` | source code specifically | free | 768 |

**For code, use a code-specific embedding model.** General text embeddings underperform on code because they weren't trained on it.

### Practical tip — embed code differently

```python
# Prepend a descriptor so the embedding carries intent
code_chunk = f"Language: Python\nFile: src/auth/jwt.py\nFunction: validate_token\n\n{raw_code}"
embedding = embed(code_chunk)
```

### Batch embedding to control cost

```python
# Don't embed one chunk at a time
for chunk in chunks:
    embed(chunk)  # ← slow, expensive

# Embed in batches
embeddings = embed_batch(chunks, batch_size=100)  # ← fast
```

### Step 3 Terminology

| Term | Meaning |
| --- | --- |
| **Embedding** | Converting text into a list of numbers (a vector) that represents its meaning in mathematical space |
| **Vector** | A list of floating-point numbers — the numerical form of a text's meaning. Similar texts produce similar vectors |
| **Dimensions** | The length of a vector (e.g., 1536 numbers). More dimensions can capture more nuance but cost more to store |
| **Cosine similarity** | A score (0–1) measuring how similar two vectors are. 1 = identical meaning, 0 = completely unrelated |
| **Embedding model** | An AI model whose job is to convert text into vectors (not to answer questions — just to represent meaning) |
| **`text-embedding-3-small`** | OpenAI's lightweight embedding model — good balance of cost and quality for general text |
| **`bge-m3`** | An open-source embedding model that runs locally for free and supports multiple languages |
| **`nomic-embed-code`** | An open-source embedding model fine-tuned specifically on source code |
| **Batch embedding** | Sending many chunks to the embedding model at once instead of one at a time — much faster and cheaper |

---

## Step 4 — Store

Persist vectors + metadata so they can be searched.

### Vector DB options for your scale

| DB | When to Use |
| --- | --- |
| **Chroma** | Local dev, prototyping |
| **pgvector** | You already use Postgres, want one less infra piece |
| **Weaviate** | Need hybrid search + schema enforcement |
| **Pinecone** | Fully managed, don't want to ops a DB |
| **Qdrant** | Self-hosted, high performance, good filtering |

### What gets stored per chunk

```text
┌──────────────────────────────────────┐
│  id:        "chunk_abc123"           │
│  vector:    [0.23, -0.87, ...]       │  ← for similarity search
│  text:      "func validate_token..." │  ← sent to LLM
│  metadata:  { repo, file, author }   │  ← for filtering
└──────────────────────────────────────┘
```

### Keeping the index fresh — critical for repos

Your repos change constantly. You need a sync strategy:

```text
Option A — Full re-index (simple, expensive)
  Cron job every night: delete all → re-embed everything

Option B — Incremental sync (efficient)
  GitHub webhook → file changed event
  → re-embed only changed files
  → upsert by chunk_id (overwrite old vectors)

Option C — Hybrid
  Incremental during day + full re-index weekly (catches drift)
```

### Step 4 Terminology

| Term | Meaning |
| --- | --- |
| **Vector DB** | A database built specifically for storing and searching vectors by similarity — not like a normal SQL database |
| **Chroma** | A lightweight, open-source vector DB that runs locally — good for development and prototyping |
| **pgvector** | A PostgreSQL extension that adds vector search to a regular Postgres database — avoids a separate DB service |
| **Pinecone** | A fully managed, cloud-hosted vector DB — no server to run, but costs money |
| **Qdrant** | A self-hosted, high-performance vector DB with strong metadata filtering support |
| **Weaviate** | A vector DB with built-in hybrid search and schema enforcement |
| **Upsert** | Insert a record if it doesn't exist; update it if it does — used to sync changed chunks without duplicating them |
| **Cron job** | A scheduled task that runs automatically at a set time (e.g., every night at midnight) |
| **Webhook** | An automatic HTTP notification sent by GitHub when a file changes — used to trigger incremental re-indexing |
| **Incremental sync** | Re-embedding only the files that changed, rather than re-processing everything |
| **Full re-index** | Deleting all stored vectors and re-embedding every document from scratch |

---

## Step 5 — Query

Transform the user's raw question into the best possible search signal.

### Problem: users ask bad questions

```text
User types:  "how does auth work"
Better for retrieval:  "explain the JWT authentication flow including token validation and refresh mechanism"
```

### Query transformations

**1. Query rewriting** — expand the question

```python
rewrite_prompt = """
Rewrite this question to be more specific and detailed for searching
a codebase and technical wiki.
Question: {user_question}
"""
# "how does auth work" → "How does the JWT authentication flow work,
# including token generation, validation, expiry, and refresh?"
```

**2. HyDE (Hypothetical Document Embedding)**
Instead of embedding the question, generate a fake answer and embed that.

```python
# The fake answer's embedding is closer to real doc embeddings
hyde_prompt = "Write a code snippet that shows how to validate a JWT token"
hypothetical_doc = llm(hyde_prompt)
query_vector = embed(hypothetical_doc)  # embed the fake answer, not the question
```

**3. Multi-query** — generate 3 variations, retrieve for each, merge results

```python
variations = [
  "JWT token validation in Python",
  "how to verify JWT signature",
  "authentication middleware token check"
]
# Retrieve for all 3, deduplicate, merge
```

### Step 5 Terminology

| Term | Meaning |
| --- | --- |
| **Query** | The user's question or search input before it is processed by the pipeline |
| **Query rewriting** | Automatically expanding or rephrasing a short user question into a more detailed version to improve retrieval |
| **HyDE (Hypothetical Document Embedding)** | Instead of embedding the question, ask the LLM to write a fake answer, then embed that — fake answers are closer in vector space to real documents than questions are |
| **Multi-query retrieval** | Generating 3–5 variations of the user's question, running retrieval for each, and merging the results to improve coverage |
| **Search signal** | The quality of information used to find relevant chunks — a better-formed query produces a stronger signal |
| **JWT (JSON Web Token)** | A compact, signed token used for authentication — carries user identity info and can be verified without a database lookup |

---

## Step 6 — Retrieve

Find the most relevant chunks for the query.

### Hybrid search — recommended for your use case

Pure vector search misses exact matches (function names, error codes, repo names).
Pure keyword search misses semantic meaning.
Hybrid combines both.

```text
User: "AuthenticationError in payments service"

Vector search finds:   chunks about authentication concepts
Keyword (BM25) finds:  exact "AuthenticationError" occurrences

Hybrid (RRF fusion):   best of both
```

```python
# Reciprocal Rank Fusion
def rrf(vector_results, keyword_results, k=60):
    scores = {}
    for rank, doc in enumerate(vector_results):
        scores[doc.id] = scores.get(doc.id, 0) + 1 / (k + rank)
    for rank, doc in enumerate(keyword_results):
        scores[doc.id] = scores.get(doc.id, 0) + 1 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)
```

### Metadata filtering — scope by source

```python
# User is asking about the payments service specifically
results = vectordb.query(
    vector=query_embedding,
    filter={
        "repo": "your-org/payments-service",
        "source_type": "github_repo",
        "last_modified": {"$gte": "2025-01-01"}  # only recent docs
    },
    top_k=10
)
```

### Re-ranking — precision pass after retrieval

Retrieve 20 candidates, re-rank to top 5.

```text
Vector DB returns top 20 (fast, approximate)
        ↓
Cross-encoder re-ranker scores each (slow, accurate)
        ↓
Top 5 most relevant chunks sent to LLM
```

### Step 6 Terminology

| Term | Meaning |
| --- | --- |
| **Dense retrieval** | Vector similarity search — finds chunks that are semantically similar to the query even if they use different words |
| **Sparse retrieval / BM25** | Keyword-based search (Best Match 25) — finds chunks containing the exact words in the query. Great for proper nouns, error codes, function names |
| **Hybrid search** | Combining dense (vector) and sparse (keyword) search to get the benefits of both |
| **RRF (Reciprocal Rank Fusion)** | An algorithm that merges ranked results from multiple searches into one combined ranking — no model required |
| **Metadata filtering** | Narrowing search results using attached fields like repo name, date, or file type before or after vector search |
| **Re-ranking** | A second, more accurate scoring pass over the top candidates retrieved by the vector DB — improves precision |
| **Cross-encoder** | A model that scores a (query, document) pair together for high accuracy re-ranking — slower than vector search but more precise |
| **Top-K** | The K highest-scoring results returned by retrieval (e.g., top-20 candidates, then re-rank to top-5) |

---

## Step 7 — Generate

Use the retrieved chunks as context for the LLM to answer.

### Prompt structure

```text
SYSTEM:
You are a helpful assistant for [Company]. Answer questions using
the provided context from our GitHub repos and internal wikis.
If the answer is not in the context, say so — do not guess.
Always cite the source (file path or wiki page).

CONTEXT:
[1] Source: payments-service/src/auth/jwt.py (lines 42-89)
    Content: def validate_token(token: str) -> bool: ...

[2] Source: Wiki > Auth > JWT Flow
    Content: Tokens expire after 24 hours. Refresh tokens...

[3] Source: payments-service/README.md
    Content: Authentication uses RS256 signed JWTs...

USER QUESTION:
How do I refresh a JWT token in the payments service?
```

### Handling failure modes

| Failure | Symptom | Fix |
| --- | --- | --- |
| Retrieval miss | LLM says "I don't know" but answer exists | better chunking, hybrid search |
| Hallucination | LLM answers confidently but wrongly | add "only use context" to prompt, raise temperature |
| Context overflow | Too many chunks exceed context window | re-rank + trim to top 3–5 |
| Stale answer | Code changed, old chunk retrieved | better incremental sync |
| Wrong repo scoped | Answer from unrelated service | metadata filtering by repo |

### Citation in the answer

Always return which chunks were used:

```python
response = {
    "answer": "To refresh a JWT, call POST /auth/refresh with...",
    "sources": [
        {"file": "payments-service/src/auth/jwt.py", "lines": "42-89"},
        {"wiki": "Auth > JWT Flow", "url": "..."}
    ]
}
```

### Step 7 Terminology

| Term | Meaning |
| --- | --- |
| **Generate** | The final step where the LLM reads the retrieved chunks and writes an answer to the user's question |
| **LLM (Large Language Model)** | The AI model that produces the final answer — e.g., Claude, GPT-4. It reads the context chunks and generates text |
| **Context injection** | Inserting the retrieved chunks into the prompt so the LLM can use them as a reference when answering |
| **System prompt** | Instructions given to the LLM before the conversation starts — sets its role, rules, and behaviour |
| **Hallucination** | When an LLM confidently states something false or made up — often happens when the answer is not in the context |
| **Retrieval miss** | When the correct document exists in the index but the retrieval step failed to find it |
| **Context overflow** | When the total size of retrieved chunks exceeds the LLM's context window limit |
| **RS256** | A JWT signing algorithm (RSA + SHA-256) — means the token is signed with a private key and verified with a public key |
| **Citation** | A reference to the source document or file that the LLM used to construct its answer — increases trust and traceability |
| **Faithfulness** | A quality metric measuring whether the LLM's answer is supported by the retrieved context (vs. made up) |

---

## Full Pipeline for Your Stack

```text
GitHub API / Wiki API
        │
        ▼
   Parse & Clean
   (markdown, AST for code)
        │
        ▼
   Chunk by boundaries
   (headers for wiki, functions for code)
   + attach metadata (repo, file, author, date)
        │
        ▼
   Embed
   (text-embedding-3-small for docs, nomic-embed-code for code)
        │
        ▼
   Store in pgvector or Qdrant
   (vector + text + metadata)
        │
   GitHub webhook → incremental sync
        │
  ── QUERY TIME ──
        │
   User question
        ↓
   Query rewrite / HyDE
        ↓
   Hybrid search (vector + BM25)
   + metadata filter (by repo / recency)
        ↓
   Re-rank top 20 → top 5
        ↓
   LLM generates answer with citations
```
