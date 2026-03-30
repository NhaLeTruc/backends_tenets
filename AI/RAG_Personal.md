# Personal PDF Folder RAG

> Goal: Query a local folder full of PDFs using AI, as if it were one big document.

---

## Option 1: Notebook LM (Easiest, No Code)

- Go to [notebooklm.google.com](https://notebooklm.google.com)
- Upload your PDFs as sources
- Query them in natural language instantly
- **Limit:** ~50 sources, ~500k words total

---

## Option 2: Local RAG with Python (Free, Private)

Best balance of control, privacy, and power.

### Stack

| Role | Library |
|------|---------|
| PDF parsing | `pypdf` / `pymupdf` |
| Embeddings | `sentence-transformers` (local, free) |
| Vector store | `chromadb` or `faiss` (local DB) |
| LLM query | Claude API or local Ollama |

### How it works

1. **Ingest:** Read all PDFs → split into chunks → embed each chunk → store in vector DB
2. **Query:** Embed your question → find top-N similar chunks → send chunks + question to LLM

### Install

```bash
pip install pypdf sentence-transformers chromadb anthropic
```

### ingest.py — run once

```python
import os, glob
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./pdf_db")
col = client.get_or_create_collection("docs")

for pdf_path in glob.glob("C:/your/pdf/folder/**/*.pdf", recursive=True):
    reader = PdfReader(pdf_path)
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            col.add(
                documents=[text],
                ids=[f"{pdf_path}::page{i}"],
                metadatas=[{"source": pdf_path, "page": i}]
            )
print("Done indexing!")
```

### query.py

```python
import anthropic, chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./pdf_db")
col = client.get_collection("docs")
claude = anthropic.Anthropic()

question = "What are the main topics across all my documents?"

results = col.query(query_texts=[question], n_results=10)
context = "\n\n---\n\n".join(results["documents"][0])

response = claude.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": f"Context from my PDFs:\n\n{context}\n\nQuestion: {question}"}]
)
print(response.content[0].text)
```

---

## Option 3: Turn-key GUI Tools (No Code)

| Tool | Notes |
|------|-------|
| **Anything LLM** | Desktop app, drag-drop folder, built-in RAG |
| **Open WebUI** | Web UI + Ollama, folder upload |
| **LM Studio** | Fully local LLM + RAG, no API key needed |

---

## Recommendation

| Scenario | Best Option |
|----------|-------------|
| Privacy matters / large folder | Python script + ChromaDB + Claude API |
| Just want it working now | NotebookLM or Anything LLM |
| Fully offline, no API key | Anything LLM + Ollama |
