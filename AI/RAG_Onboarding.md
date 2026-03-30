# RAG for Employee Onboarding

---

## The Onboarding Problem RAG Solves

New employees are overwhelmed with:
- Scattered documentation (wikis, PDFs, Notion, Confluence)
- Tribal knowledge locked in people's heads or Slack history
- Codebase they've never seen
- Processes spread across 10 different tools

Instead of reading everything, they can just **ask**.

---

## What a RAG Onboarding Assistant Can Do

### Answer "How do we do X here?"
> *"How do I deploy to production?"*
> *"What's the code review process?"*
> *"Who owns the payments service?"*

RAG retrieves the answer from your actual internal docs — not a generic web answer.

### Explain the codebase
> *"What does the AuthService do?"*
> *"Where is the user registration flow?"*

If your repos are indexed, the new hire can explore code by asking questions.

### Surface the right document at the right time
Instead of "go read these 30 pages", the assistant answers the specific question and links to the source — the employee reads only what's relevant.

### Answer repeated questions without bothering senior staff
Senior engineers spend significant time answering the same questions for each new hire. RAG absorbs that load.

---

## What RAG Cannot Replace

| RAG Can Handle | RAG Cannot Handle |
|---|---|
| Written docs & wikis | Unwritten tribal knowledge |
| Code that's been indexed | How a system *actually* behaves in prod |
| Process docs | Culture, relationships, politics |
| FAQs | Mentor judgment calls |
| Architecture docs | Debugging muscle memory |

RAG is a **complement** to a human buddy/mentor, not a replacement.

---

## Practical Onboarding RAG Setup

```text
Index these sources:
  ✓ Internal wiki (Confluence, Notion, GitHub Wiki)
  ✓ Main repos + READMEs
  ✓ Runbooks and incident post-mortems
  ✓ Architecture decision records (ADRs)
  ✓ HR/process docs (leave policy, deployment process)
  ✓ Onboarding checklist docs

Add metadata so results can be scoped:
  - team: "payments" | "platform" | "frontend"
  - doc_type: "runbook" | "policy" | "architecture" | "code"
  - audience: "new_hire" | "all"
```

### System prompt tuning for onboarding context

```text
SYSTEM:
You are an onboarding assistant for [Company].
Answer as if explaining to someone on their first week.
- Prefer simple language over jargon
- Always link to the source document
- If something requires human judgment, say "ask your manager or buddy"
- Never guess — if it's not in the docs, say so
```

---

## Architecture

```text
                        ┌─────────────────────────────┐
                        │        SOURCE DOCUMENTS      │
                        │  Wiki · Repos · HR Docs      │
                        │  Runbooks · ADRs · READMEs   │
                        └────────────┬────────────────┘
                                     │ ingest (nightly or on change)
                                     ▼
                        ┌─────────────────────────────┐
                        │     INGESTION PIPELINE       │
                        │  Parse → Chunk → Embed       │
                        │  + attach metadata           │
                        │  (team, doc_type, audience)  │
                        └────────────┬────────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────────┐
                        │        VECTOR DB             │
                        │  pgvector or Qdrant          │
                        │  vectors + text + metadata   │
                        └────────────┬────────────────┘
                                     │
                  ┌──────────────────┼──────────────────┐
                  │           QUERY TIME                 │
                  │                                      │
          New hire asks question                         │
                  │                                      │
                  ▼                                      │
        ┌──────────────────┐                            │
        │  Query Rewrite   │  expand vague question     │
        └────────┬─────────┘                            │
                 │                                      │
                 ▼                                      │
        ┌──────────────────┐                            │
        │  Hybrid Search   │  vector + BM25             │
        │  + metadata      │  filter by team/doc_type   │
        │    filter        │                            │
        └────────┬─────────┘                            │
                 │                                      │
                 ▼                                      │
        ┌──────────────────┐                            │
        │    Re-rank       │  top 20 → top 5            │
        └────────┬─────────┘                            │
                 │                                      │
                 ▼                                      │
        ┌──────────────────┐                            │
        │  LLM Generate    │  onboarding system prompt  │
        │  + cite sources  │                            │
        └────────┬─────────┘                            │
                 │                                      │
                 ▼                                      │
        Answer + source links shown to new hire         │
                 │                                      │
                 ▼                                      │
        👍 / 👎 feedback → improve eval dataset ────────┘
```

---

## Recommended Stack

| Layer | Tool | Why |
|---|---|---|
| Orchestration | LlamaIndex | Strong document ingestion + metadata support |
| Embeddings | `text-embedding-3-small` | Good for mixed docs + code |
| Vector DB | pgvector (if Postgres exists) or Qdrant | Avoids extra infra |
| Re-ranker | Cohere Rerank or `bge-reranker` | Improves precision |
| LLM | Claude (Anthropic) | Strong instruction-following, good at citing sources |
| Frontend | Slack bot or simple web chat | Where new hires already are |
| Eval | RAGAS | Measures faithfulness + answer relevance |

---

## Measuring Whether It Works

| Metric | How to Measure |
|---|---|
| Time to first PR | Compare cohorts with vs without RAG |
| Repeated Slack questions | Count how often the same question is asked |
| New hire satisfaction | Onboarding survey score |
| RAG answer quality | Thumbs up/down on each answer |
| Unanswered questions | Queries that returned no useful result → doc gaps |

---

## Key Insight

> The value of RAG for onboarding is proportional to the quality of your existing documentation.
> RAG is a multiplier — it amplifies good docs, and exposes bad ones.

If docs are outdated or missing, RAG will surface wrong answers confidently.
The onboarding RAG project doubles as a **documentation audit**.

---

## Real Companies Doing This

- **Stripe** — internal docs assistant for engineers
- **Notion** — AI-powered search over their own wiki
- **GitHub Copilot for docs** — repo-aware Q&A
