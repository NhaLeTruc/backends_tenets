# Senior Data Engineer Interview: AI Tools & Productivity

---

## Part 1: Introduction & General AI Principles

**Q**: How you leverage AI tools in your development workflow.

**A**: AI tools as force multipliers—they should enhance, not replace, engineering judgment. My philosophy is "AI-augmented, human-validated." I use AI for boilerplate generation, exploring unfamiliar codebases, and rapid prototyping, but I always validate outputs, understand the generated code, and maintain ownership of architectural decisions.

**Q**: How do you think about the boundary between tasks you should delegate to AI versus tasks you should do yourself?

**A**: Use a framework I call the "CAV principle"—Complexity, Accountability, and Verification. For low-complexity, high-repeatability tasks like writing unit tests or data transformation boilerplate, AI excels. For high-stakes decisions like schema design or distributed system architecture, I lead and use AI as a research assistant. The key is: if I can't verify and explain the output, I shouldn't delegate it.

**Q**: What makes a good prompt when working with AI coding assistants?

**A**: A good prompt has five elements: context, constraint, clarity, criteria, and iterative refinement. For example, instead of "write a function to parse JSON," I'd say: "Write a Java 21 function using record types to parse this JSON schema [provide schema]. Handle malformed input with custom exceptions. Follow our project's error handling patterns in ErrorHandler.java. Optimize for readability over performance." Then I iterate based on the output.

---

## Part 2: Anthropic Claude & Skills Deep Dive

**Q**: You mentioned Anthropic specifically in your resume. What's your experience with Claude and Claude Code?

**A**: I've been using Claude extensively for about 18 months, and Claude Code for the past 6 months. What sets Claude apart is its extended context window—up to 200K tokens—which is game-changing for codebase understanding. I use it for multi-file refactoring, documentation generation, and complex debugging sessions where I need to provide full stack traces and related files.

**Q**: Tell me about Anthropic skills. How do you use them in practice?

**A**: Skills are pre-configured workflows that automate common development patterns. Think of them as parameterized scripts with AI reasoning. For example, I've created custom skills for:

1. **Database migration review** - Analyzes proposed migrations, checks for breaking changes, suggests rollback strategies
2. **Performance regression detection** - Compares query execution plans before/after changes
3. **Data quality validation** - Generates comprehensive test cases for ETL pipelines

The key is skills combine deterministic logic (running queries, parsing logs) with AI reasoning (interpreting results, suggesting fixes).

**Q**: Can you walk me through building a custom skill? Let's say for data lineage documentation.

**A**: Sure. A data lineage skill would have these components:

```yaml
name: data-lineage-documenter
description: Traces data flow through pipeline and generates documentation
tools:
  - code_search: Find table references and transformations
  - query_executor: Run EXPLAIN on SQL queries
  - graph_builder: Build dependency graph
steps:
  1. Parse SQL files for CREATE, INSERT, SELECT patterns
  2. Extract table dependencies and transformations
  3. Query metadata tables for column-level lineage
  4. Generate Mermaid diagrams showing data flow
  5. Create markdown documentation with business context
validation:
  - Verify all referenced tables exist
  - Check for circular dependencies
  - Flag undocumented transformations
```

The skill would use Claude's code understanding to interpret complex SQL logic and infer business meaning from naming conventions.

**Q**: How do you handle cases where AI-generated code doesn't match your project's patterns?

**A**: That's where context management is critical. I maintain a `.claude/` directory with:
- `project_conventions.md` - Coding standards, naming patterns
- `architecture_decisions.md` - ADRs with rationale
- `common_patterns.md` - Reusable snippets

I reference these in my prompts: "Follow the error handling pattern in .claude/common_patterns.md#error-handling." For Claude Code specifically, I use the CLAUDE.md file to persist project-specific instructions that are automatically included in context.

**Q**: You mentioned Claude Code. How does it differ from using Claude in the chat interface?

**A**: Claude Code is the CLI/SDK version optimized for agentic workflows. Key differences:

1. **Persistent context** - It maintains conversation state across terminal sessions
2. **Tool integration** - Direct access to filesystem, terminal commands, git operations
3. **Autonomous planning** - Can break down tasks, execute multiple steps, and self-correct
4. **IDE integration** - VSCode extension provides inline assistance

For data engineering, I use Claude Code to orchestrate complex workflows like: "Analyze this slow-running ETL job, profile the queries, identify bottlenecks, and refactor the top 3 slowest operations."

**Q**: Can you give an example of a complex task you've automated with Claude Code?

**A**: Recently, I automated our quarterly data warehouse optimization process:

```bash
claude-code "Analyze warehouse query logs from the past quarter.
1. Identify top 20 most expensive queries by compute time
2. Run EXPLAIN ANALYZE on each and detect missing indexes
3. Calculate potential cost savings per index
4. Generate CREATE INDEX statements with cost-benefit analysis
5. Create a PR with the changes and supporting documentation"
```

Claude Code parsed 100GB of logs, ran 20 EXPLAIN queries, calculated that 5 indexes would save $12K/month, and generated a complete PR with benchmark results. What would take me 2 days took 45 minutes.

**Q**: Impressive. How did you validate the recommendations?

**A**: I never auto-merge AI-generated changes. My validation checklist:
1. **Manual review** - Read every line, ensure I understand the logic
2. **Test on staging** - Run against production-like data
3. **Performance benchmark** - Measure actual impact with real queries
4. **Peer review** - Another engineer validates the approach
5. **Gradual rollout** - Apply indexes one at a time, monitor for locking issues

AI accelerates proposal generation, but human judgment governs production changes.

---

## Part 3: AI Agents & Autonomous Systems

**Q**: Let's shift to AI agents. What's your mental model for when to use agentic vs. single-shot AI interactions?

**A**: I use a decision tree:
- **Single-shot**: Well-defined input/output, no external dependencies, immediate verification possible
- **Agentic**: Multi-step workflow, requires external tool calls, iterative refinement needed

For data engineering specifically:
- Single-shot: "Generate a Pandas function to clean this column"
- Agentic: "Debug this failing Airflow DAG by checking logs, inspecting data, and fixing the root cause"

Agents shine when the solution requires exploration, decision-making across multiple steps, and adaptation based on intermediate results.

**Q**: What agent frameworks have you worked with?

**A**: I've used several:

1. **LangGraph** - My go-to for production pipelines. Great for stateful workflows where you need explicit control flow and checkpointing.

2. **CrewAI** - Excellent for multi-agent coordination. I used it to build a data quality monitoring system with specialized agents for validation, alerting, and auto-remediation.

3. **Claude Agent SDK** - Newer, but extremely powerful for development workflows. The tight integration with Claude Code and MCP makes it ideal for DevOps automation.

4. **AutoGPT/BabyAGI** - Experimented with these but found them too autonomous for production data systems. Useful for research tasks.

**Q**: Tell me about a production agent you've deployed.

**A**: I built an "ETL Reliability Agent" that monitors our data pipelines:

**Architecture:**
```
Orchestrator Agent (LangGraph)
├── Monitor Agent - Watches pipeline metrics
├── Diagnostic Agent - Investigates failures
├── Remediation Agent - Applies fixes
└── Notification Agent - Alerts on-call engineer
```

**Workflow:**
1. Monitor detects anomaly (e.g., row count drop >10%)
2. Diagnostic agent:
   - Queries logs for errors
   - Compares schema between source/target
   - Checks for upstream data issues
3. Remediation agent:
   - For known issues: Auto-retry with backoff
   - For schema changes: Generate migration script
   - For data quality: Quarantine bad records
4. Notification agent:
   - Pages engineer for unknown issues
   - Posts summary to Slack for resolved issues

**Impact:** Reduced pipeline downtime by 60%, prevented 15+ incidents before they affected dashboards.

**Q**: How do you handle agent failures? What if the agent makes incorrect decisions?

**A**: Multi-layered safety approach:

1. **Guardrails** - Agents can only modify staging environments. Production changes require human approval.
2. **Validation gates** - After each action, agent runs validation queries to verify correctness.
3. **Rollback mechanisms** - Every change is version-controlled, with automated rollback procedures.
4. **Confidence scoring** - Agent assigns confidence (0-1) to decisions. Below 0.7, it asks for human input.
5. **Audit logging** - Full trace of agent decisions, reasoning, and actions for post-mortem analysis.

I also implement "circuit breakers"—if an agent fails 3 times in a row, it disables itself and alerts the team.

**Q**: What about cost management? AI agents can rack up API costs quickly.

**A**: Critical concern. My strategies:

1. **Caching** - Aggressive caching of LLM responses for repeated queries. For diagnostic patterns, hit rate is ~70%.
2. **Model tiering** - Use Claude Haiku for simple tasks (log parsing), Sonnet for complex reasoning (root cause analysis), Opus only for critical decisions.
3. **Batch processing** - Instead of real-time analysis, some agents run on a schedule, processing batches.
4. **Budget constraints** - Set per-agent daily spending limits. Agent pauses and notifies if exceeded.
5. **Metrics tracking** - Dashboard showing cost per agent action, enabling ROI analysis.

Our ETL agent costs ~$200/month but saves ~$8K in engineer time and prevented incidents worth ~$50K in lost revenue.

---

## Part 4: Model Context Protocol (MCP)

**Q**: Let's dive into MCP. For those unfamiliar, can you explain what MCP is and why it matters?

**A**: Model Context Protocol is Anthropic's standardized way for AI models to interact with external tools and data sources. Think of it as an API layer between LLMs and your infrastructure.

**Why it matters:**
1. **Standardization** - Instead of custom integrations for each tool, one protocol works across all MCP-compatible systems.
2. **Composability** - Connect multiple MCP servers, each exposing different capabilities (database access, file systems, APIs).
3. **Security** - Granular permissions, credential management, audit logging built into the protocol.
4. **Flexibility** - Add new data sources without modifying your AI application.

For data engineering, MCP is transformative because our work involves diverse systems—databases, data warehouses, object storage, orchestrators—and MCP provides unified access.

**Q**: Can you walk through implementing an MCP server?

**A**: Absolutely. Let's build an MCP server for Postgres database access:

```python
from mcp import Server, Tool
import psycopg2

class PostgresMCPServer:
    def __init__(self):
        self.server = Server("postgres-mcp")
        self.connections = {}

    def register_tools(self):
        @self.server.tool()
        async def execute_query(
            connection_name: str,
            query: str,
            params: list = None
        ) -> dict:
            """Execute SQL query and return results"""
            conn = self.connections[connection_name]
            cursor = conn.cursor()

            # Safety checks
            if any(kw in query.upper() for kw in ['DROP', 'DELETE', 'TRUNCATE']):
                if not query.startswith('-- APPROVED:'):
                    raise ValueError("Destructive queries require approval comment")

            cursor.execute(query, params)

            if cursor.description:  # SELECT query
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return {
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows)
                }
            else:  # INSERT/UPDATE
                conn.commit()
                return {"rows_affected": cursor.rowcount}

        @self.server.tool()
        async def get_table_schema(
            connection_name: str,
            table_name: str
        ) -> dict:
            """Get table schema information"""
            query = """
                SELECT column_name, data_type, is_nullable,
                       column_default, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """
            return await execute_query(connection_name, query, [table_name])

        @self.server.tool()
        async def explain_query(
            connection_name: str,
            query: str
        ) -> dict:
            """Get query execution plan"""
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            result = await execute_query(connection_name, explain_query)
            return result

    def add_connection(self, name: str, connection_string: str):
        """Add a database connection"""
        self.connections[name] = psycopg2.connect(connection_string)

    def start(self):
        self.register_tools()
        self.server.run()
```

**Usage from Claude:**
```
User: "Analyze slow queries on the analytics database"

Claude (via MCP):
1. execute_query(connection_name="analytics", query="SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10")
2. For each slow query:
   - explain_query(connection_name="analytics", query=<slow_query>)
   - Analyze execution plan
   - Suggest optimizations
```

**Q**: How do you handle security with MCP servers?

**A**: Multi-layered security model:

1. **Authentication** - MCP servers require API keys or OAuth tokens. Rotated monthly.

2. **Authorization** - Role-based access control:
   ```yaml
   roles:
     data_analyst:
       tools: [execute_query, get_table_schema]
       databases: [analytics_readonly]
       query_restrictions: [SELECT_ONLY, MAX_ROWS_10000]

     data_engineer:
       tools: [execute_query, get_table_schema, explain_query]
       databases: [analytics_readonly, staging_readwrite]
       query_restrictions: [MAX_EXECUTION_TIME_30s]
   ```

3. **Query validation** - Parse SQL AST, block dangerous patterns:
   - No DROP/TRUNCATE without approval
   - Prevent cartesian joins
   - Require WHERE clauses on large tables
   - Block wildcard SELECT on tables >1M rows

4. **Audit logging** - Every MCP call logged with:
   - Timestamp, user, query, parameters
   - Execution time, rows affected
   - Result summary (not full data for privacy)

5. **Network isolation** - MCP servers run in private VPC, only accessible via VPN or bastion host.

**Q**: What MCP servers do you commonly use in your workflow?

**A**: My standard MCP stack:

1. **Database MCP** (custom)
   - Postgres, Snowflake, BigQuery connectors
   - Unified query interface across warehouses

2. **Filesystem MCP**
   - Read/write project files
   - Navigate codebases
   - Essential for Claude Code integration

3. **Git MCP**
   - Commit, branch, PR operations
   - Analyze git history
   - Automated code archaeology

4. **Kubernetes MCP** (custom)
   - Query pod status, logs
   - Trigger jobs, scale deployments
   - Debug production issues

5. **Airflow MCP** (custom)
   - Trigger DAGs, check status
   - Parse logs, analyze task duration
   - Auto-retry failed tasks

6. **S3 MCP**
   - List objects, read files
   - Useful for analyzing data lake contents

7. **Slack MCP**
   - Post notifications
   - Search conversation history for context

**Q**: Can you describe a workflow that chains multiple MCP servers?

**A**: Sure. Here's a real incident response workflow:

**Scenario**: Dashboard shows data freshness issue—fact_sales table hasn't updated in 3 hours.

**AI-Orchestrated Investigation (using multiple MCP servers):**

```
1. Airflow MCP - Check DAG status
   → Query: "Get status of sales_etl_dag"
   → Result: Last run failed at task 'load_sales_data'

2. Kubernetes MCP - Get pod logs
   → Query: "Fetch logs for airflow-worker-* pods, filter for sales_etl_dag"
   → Result: Error: "psycopg2.errors.InsufficientPrivilege: permission denied for table raw_sales"

3. Database MCP - Check permissions
   → Query: "SELECT * FROM information_schema.table_privileges WHERE table_name='raw_sales' AND grantee='etl_user'"
   → Result: SELECT privilege exists, but not INSERT (was revoked accidentally)

4. Git MCP - Find who changed permissions
   → Query: "Search git log for REVOKE commands on raw_sales"
   → Result: Commit abc123 by DBA during security audit

5. Slack MCP - Notify team
   → Action: Post to #data-incidents channel with full diagnosis

6. Database MCP - Suggest fix
   → Action: Generate GRANT statement, request approval

7. Airflow MCP - Retry pipeline
   → Action: Clear failed task, trigger re-run
```

**Outcome:** Issue diagnosed in 3 minutes (vs. 30+ minutes manual), root cause identified, fix proposed. Human engineer approves and applies fix.

---

## Part 5: RAG (Retrieval-Augmented Generation)

**Q**: Let's talk about RAG. How do you think about when to use RAG versus native LLM knowledge?

**A**: RAG is essential when:
1. Information is proprietary (company docs, internal codebases)
2. Data changes frequently (metrics, logs, configurations)
3. Context is too large for the context window
4. Verification requires source attribution

For data engineering specifically, RAG is critical for:
- Querying data catalogs and metadata repositories
- Searching operational runbooks and incident histories
- Analyzing schema evolution and migration history
- Referencing internal data quality rules and business logic

**Q**: Walk me through your RAG architecture for a data engineering use case.

**A**: Let me describe our "Data Knowledge RAG System":

**Architecture:**

```
Query: "What's the business definition of MRR?"

1. Query Understanding Layer
   ├── Claude analyzes query intent
   ├── Extracts key entities: [MRR, metric, definition]
   └── Determines required sources: [data_catalog, business_glossary]

2. Retrieval Layer
   ├── Vector Search (embeddings)
   │   ├── Embed query with voyage-2
   │   ├── Search vector DB (Pinecone)
   │   └── Retrieve top 10 similar documents
   │
   ├── Metadata Search (structured)
   │   ├── Query data catalog API
   │   └── Fetch MRR metric metadata
   │
   └── Hybrid Ranking
       ├── Re-rank with cross-encoder
       └── Select top 5 most relevant

3. Context Assembly
   ├── Deduplicate results
   ├── Add source citations
   ├── Format for LLM consumption
   └── Truncate to fit context window

4. Generation Layer
   ├── Claude synthesizes answer
   ├── Cites specific sources
   └── Flags conflicting definitions

5. Post-Processing
   ├── Verify factual consistency
   ├── Check for hallucinations
   └── Format with markdown links
```

**Example Output:**
```markdown
**MRR (Monthly Recurring Revenue)** is defined as the normalized monthly revenue from all active subscriptions.

**Calculation**:
SUM(subscription_amount / billing_period_months)
WHERE status = 'active'

**Sources**:
- [Business Glossary: MRR](link) - Updated 2025-11-15
- [Data Catalog: fact_subscriptions.mrr](link) - Owner: Finance Team
- [dbt Model: monthly_recurring_revenue.sql](link) - Last modified 2025-12-01

**Notes**: The finance team uses gross MRR (before churn), while the product team reports net MRR (after churn). See [Revenue Metrics Standards](link) for details.
```

**Q**: What embedding models and vector databases do you use?

**A**: My choices depend on requirements:

**Embedding Models:**
1. **Voyage-2** - Best overall for text, what I use for documentation
2. **OpenAI text-embedding-3-large** - Great for code and mixed content
3. **Cohere embed-english-v3** - Excellent retrieval quality, fast
4. **BGE-M3** - Self-hosted option for sensitive data

For data engineering, I often use domain-specific models:
- **CodeBERT** for SQL queries and data transformation code
- **Fine-tuned Voyage** on our internal docs for better domain accuracy

**Vector Databases:**
1. **Pinecone** - Production workhorse, managed, scales well
2. **Weaviate** - Great for multi-tenancy, hybrid search
3. **pgvector** - When I want vectors in Postgres, simple deployments
4. **Qdrant** - Fast, self-hosted, good for high-throughput

**Selection criteria:**
- <100K vectors: pgvector (simple)
- 100K-10M vectors: Pinecone (managed)
- >10M vectors or complex filtering: Weaviate
- Need on-prem/air-gapped: Qdrant

**Q**: How do you handle data freshness in RAG systems?

**A**: Data freshness is critical. My strategies:

1. **Incremental Updates**
   ```python
   # Update pipeline (runs every 15 minutes)
   def update_knowledge_base():
       # Get documents modified since last update
       new_docs = fetch_documents(since=last_update_time)

       # Generate embeddings
       embeddings = embed_batch(new_docs)

       # Upsert to vector DB (overwrites old versions)
       vector_db.upsert(embeddings, metadata={
           'document_id': doc.id,
           'version': doc.version,
           'updated_at': doc.updated_at
       })

       # Remove deleted documents
       deleted_ids = fetch_deleted_documents()
       vector_db.delete(deleted_ids)
   ```

2. **Time-aware Retrieval**
   - Boost recent documents in ranking
   - Filter out stale content (configurable threshold)
   - Display last-updated timestamp in results

3. **Cache Invalidation**
   - Clear query cache when source docs update
   - Use TTL-based caching (e.g., 1 hour for docs, 5 min for metrics)

4. **Hybrid Approach**
   - Use RAG for historical/stable knowledge
   - Use direct API calls for real-time data (current metrics, live system status)

5. **Freshness Indicators**
   ```markdown
   Source: Data Catalog - fact_orders
   Last Updated: 2 hours ago ✓ Fresh

   Source: Migration Runbook v2.1
   Last Updated: 45 days ago ⚠️ May be outdated
   ```

**Q**: How do you evaluate RAG system performance?

**A**: I use a comprehensive evaluation framework:

**1. Retrieval Quality Metrics:**
- **Recall@k**: Are relevant docs in top-k results?
- **Precision@k**: Are top-k results relevant?
- **MRR (Mean Reciprocal Rank)**: Position of first relevant result
- **NDCG**: Ranking quality with graded relevance

**2. Generation Quality Metrics:**
- **Faithfulness**: Does answer match retrieved content?
- **Answer Relevance**: Does answer address the question?
- **Context Relevance**: Are retrieved docs relevant to query?
- **Groundedness**: Are facts supported by sources?

**3. End-to-End Metrics:**
- **User Satisfaction**: Thumbs up/down on answers
- **Task Success Rate**: Did user accomplish their goal?
- **Source Click Rate**: Do users verify sources?
- **Abandonment Rate**: Do users reformulate queries?

**Evaluation Pipeline:**
```python
# Golden dataset: 500 question-answer pairs with labeled sources
golden_set = load_golden_dataset()

for question, expected_answer, expected_sources in golden_set:
    # Run RAG pipeline
    retrieved_docs = retrieval_system.retrieve(question)
    generated_answer = llm.generate(question, retrieved_docs)

    # Evaluate retrieval
    recall = compute_recall(retrieved_docs, expected_sources)
    precision = compute_precision(retrieved_docs, expected_sources)

    # Evaluate generation (using Claude as judge)
    faithfulness = evaluate_faithfulness(generated_answer, retrieved_docs)
    relevance = evaluate_relevance(generated_answer, question)

    # Compare to expected answer
    semantic_similarity = compute_similarity(generated_answer, expected_answer)

    # Log metrics
    metrics_db.insert({
        'question_id': question.id,
        'recall@5': recall,
        'precision@5': precision,
        'faithfulness': faithfulness,
        'relevance': relevance,
        'similarity': semantic_similarity,
        'timestamp': now()
    })
```

**Continuous Improvement:**
- Weekly review of low-scoring queries
- A/B test embedding models, chunk sizes, retrieval strategies
- Fine-tune retrieval based on user feedback

**Q**: What about RAG for code? How does that differ from document RAG?

**A**: Code RAG has unique challenges:

**Differences:**

1. **Structure Matters**
   - Code has syntax, semantics, dependencies
   - Can't just chunk by tokens—need to respect function/class boundaries
   - Parse AST to create meaningful chunks

2. **Multiple Representations**
   - Raw code
   - Docstrings/comments
   - Function signatures
   - Call graphs
   - Git history

3. **Granularity**
   - Function-level: Good for "how does X work?"
   - File-level: Good for "where is feature Y?"
   - Repository-level: Good for architecture questions

**My Code RAG Approach:**

```python
def index_codebase(repo_path):
    for file in repo_path.glob('**/*.py'):
        # Parse AST
        tree = ast.parse(file.read_text())

        # Extract functions/classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Create rich representation
                chunk = {
                    'code': ast.unparse(node),
                    'signature': get_signature(node),
                    'docstring': ast.get_docstring(node),
                    'calls': extract_function_calls(node),
                    'file_path': file,
                    'line_number': node.lineno,
                    'complexity': compute_complexity(node),
                    'git_blame': get_last_modified(file, node.lineno)
                }

                # Embed multiple representations
                embeddings = {
                    'code': embed(chunk['code']),
                    'docstring': embed(chunk['docstring']),
                    'semantic': embed(f"{chunk['signature']} - {chunk['docstring']}")
                }

                # Store with metadata
                vector_db.insert(embeddings, metadata=chunk)
```

**Query Strategy:**
- "How does authentication work?" → Semantic search on docstrings
- "Find SQL injection vulnerabilities" → Code pattern search + embedding
- "Who wrote the billing logic?" → Git blame metadata filter + search

**Benefits for Data Engineering:**
- Find all data transformations on a specific table
- Discover unused ETL jobs
- Identify code that needs migration after schema change
- Generate documentation from code + git history

---

## Part 6: Integration & Workflows (20 minutes)

**Q**: How do you integrate all these technologies—Claude, agents, MCP, RAG—into a cohesive workflow?

**A**: Great question. Here's my "AI-Native Data Engineering Workflow":

**Morning Routine: Pipeline Health Check**
```bash
# Run via Claude Code with MCP integrations
claude-code "Good morning analysis:
1. Check all Airflow DAGs - any failures overnight?
2. Review data quality metrics - any anomalies?
3. Summarize Slack #data-incidents - any unresolved issues?
4. Check warehouse costs - any unexpected spikes?
5. Create prioritized todo list for today"
```

**Claude Code orchestrates:**
- Airflow MCP: Query DAG status
- Database MCP: Pull quality metrics
- Slack MCP: Analyze incidents
- Snowflake MCP: Get cost reports
- RAG: Search runbooks for incident remediation steps

**Output:**
```markdown
## Pipeline Health Report - Dec 29, 2025

🔴 CRITICAL:
- user_events_etl failed at 2:14 AM
  - Error: Timeout connecting to events API
  - Runbook: [API Timeout Troubleshooting](link)
  - Suggested fix: Increase timeout, add retry logic
  - Owner: @data-eng-oncall

🟡 WARNINGS:
- customer_churn_model took 2.3x longer than usual (1.2h vs 30m)
  - Likely cause: Data volume increased 40%
  - Suggestion: Optimize feature engineering queries

✅ ALL CLEAR:
- 43/45 DAGs completed successfully
- Data quality: 99.7% checks passed
- Warehouse costs: $1,234 (-5% vs yesterday)

📋 TODAY'S PRIORITIES:
1. Fix user_events_etl timeout issue
2. Optimize customer_churn_model performance
3. Review pending schema change PRs (3 open)
```

**Development Task: Schema Change**
```bash
claude-code "I need to add a 'subscription_tier' column to the users table.
1. Analyze impact - what queries and downstream dependencies will break?
2. Generate migration with backward compatibility
3. Update affected dbt models
4. Generate unit tests
5. Create rollback plan
6. Draft PR with full documentation"
```

**Claude Code with RAG + MCP:**
1. **RAG**: Search codebase for `users` table references
2. **Database MCP**: Query current schema, table size, index info
3. **Git MCP**: Find recent migrations for pattern matching
4. **Agent**: Generate migration, update dbt models, write tests
5. **Validation**: Run tests in staging environment
6. **Git MCP**: Create PR with change summary

**Result:** Complete, production-ready schema change in 15 minutes vs. 2 hours manually.

**Q**: How do you ensure consistency across the team when using AI tools?

**A**: Standardization is key:

**1. Shared Knowledge Base (RAG)**
```
docs/
├── runbooks/           # Operational procedures
├── architecture/       # System designs, ADRs
├── data-catalog/       # Table schemas, business logic
├── conventions/        # Coding standards, patterns
└── troubleshooting/    # Common issues, solutions
```

All team members' AI assistants query the same RAG system, ensuring consistent answers.

**2. Custom Skills Library**
```
.claude/skills/
├── schema-change          # Standard migration workflow
├── pipeline-create        # New DAG scaffolding
├── incident-response      # Triage and remediation
└── data-quality-check     # Validation procedures
```

Everyone uses the same skills, promoting best practices.

**3. Prompt Library**
```yaml
# .claude/prompts.yaml
diagnose_slow_query: |
  Analyze this slow query: {query}
  1. Run EXPLAIN ANALYZE
  2. Identify bottlenecks (seq scans, missing indexes)
  3. Suggest optimizations
  4. Estimate performance improvement
  5. Consider trade-offs (index maintenance cost)
  Context: {table_metadata}
```

**4. Review Guidelines**
- All AI-generated PRs tagged with `ai-assisted`
- Required: Human review + explanation of AI's reasoning
- Checklist: Security, performance, backward compatibility

**5. Metrics Dashboard**
- Track AI tool usage, cost, time saved per engineer
- Measure code quality (bug rate, performance) of AI-assisted vs. manual code
- Share best practices from top performers

**Q**: What about onboarding new team members with AI tools?

**A**: AI-accelerated onboarding is a game-changer:

**Week 1: Codebase Exploration**
```
New Engineer: "Help me understand the data architecture"

Claude Code (with RAG + MCP):
1. Generate architecture diagram from codebase
2. Explain data flow: sources → ETL → warehouse → analytics
3. Walk through key pipelines with annotated code
4. Quiz on architectural concepts, adapt explanations based on answers
```

**Week 2: Hands-on Tasks**
```
Tasks (progressively harder):
1. "Fix this data quality test" - AI provides hints, not solutions
2. "Add a new column to reporting table" - AI guides through workflow
3. "Optimize this slow query" - AI reviews proposed solution
```

**Week 3: Autonomous Development**
```
Task: "Build a new dashboard data pipeline"

AI Role: Pair programming partner
- Answers questions about conventions
- Reviews code for quality, security
- Suggests improvements based on team patterns
```

**Outcome:** New engineers productive in 2 weeks vs. 6 weeks traditional onboarding.

---

## Part 7: Advanced Topics & Future (15 minutes)

**Q**: What advanced AI techniques are you excited about for data engineering?

**A**: Several emerging areas:

**1. Agentic Data Quality**
- Agents that learn data quality rules by observing production data
- Auto-generate dbt tests based on inferred constraints
- Anomaly detection with self-healing (agent investigates and fixes)

**2. Natural Language to SQL (Advanced)**
- Move beyond simple text-to-SQL to complex analytical queries
- Agents that understand business context, not just schema
- Multi-step analysis: "Compare Q4 2025 revenue by cohort, identify trends, explain drivers"

**3. Automated Pipeline Optimization**
- Agents that continuously profile pipelines, suggest optimizations
- Automatic A/B testing of query rewrites
- Cost-performance trade-off recommendations

**4. Intelligent Data Governance**
- RAG over compliance requirements + data catalog
- Auto-tag PII, suggest anonymization strategies
- Generate audit reports for regulatory compliance

**5. Multi-Modal Data Understanding**
- Analyze dashboard screenshots to auto-generate SQL
- OCR + LLM to extract metadata from legacy documentation
- Image embeddings for visual data quality checks

**Q**: What's your take on AI-generated code quality? Are there areas where AI struggles?

**A**: AI excels at:
- Boilerplate (CRUD operations, test scaffolding)
- Pattern replication (if the pattern exists in training data)
- Refactoring (rename variables, extract functions)
- Documentation (explaining existing code)

AI struggles with:
- **Novel algorithms** - For unique business logic, AI often produces suboptimal solutions
- **Performance optimization** - May miss domain-specific optimizations (e.g., Postgres-specific tricks)
- **Error handling edge cases** - Focuses on happy path, misses rare failure modes
- **Security** - Can introduce vulnerabilities (SQL injection, improper auth)
- **Distributed systems** - Race conditions, deadlocks, consistency issues

**My Rule:** Use AI for the "mechanical" parts of coding, but design and critical logic are human-led.

**Q**: How do you stay current with rapidly evolving AI tools?

**A**: My learning framework:

**1. Weekly Experimentation (4 hours)**
- Test new models, frameworks, tools
- Reproduce benchmark results on my own data
- Share findings with team

**2. Community Engagement**
- Active in AI engineering communities (Twitter/X, Discord servers)
- Follow key researchers (Anthropic, OpenAI, academic labs)
- Read preprints on arXiv (focus on applied AI)

**3. Production Pilots**
- Always have 1-2 experimental AI projects running
- Measure impact rigorously
- Scale winners, kill losers quickly

**4. Vendor Relationships**
- Participate in early access programs (Anthropic Claude, Databricks AI)
- Attend vendor conferences, workshops
- Provide feedback to shape product direction

**5. Internal Knowledge Sharing**
- Monthly "AI Show & Tell" - team members demo new techniques
- Maintain shared doc of AI tool evaluations
- Run occasional hackathons focused on AI productivity

**Q**: Any concerns about over-reliance on AI in engineering?

**A**: Absolutely. I worry about:

**1. Skill Atrophy**
- Junior engineers may never learn fundamentals if AI does everything
- Solution: Mandate "manual mode" for learning tasks, require understanding before using AI

**2. Monoculture**
- If everyone uses the same AI, we all make similar mistakes
- Solution: Encourage diverse tools, human code review catches AI blindspots

**3. Black Box Decisions**
- Agents making production changes without clear reasoning
- Solution: Require explainability, human-in-the-loop for critical decisions

**4. Security Risks**
- Sensitive data in prompts, credentials in AI-generated code
- Solution: Data sanitization, secret scanning, security training

**5. Complacency**
- Over-trusting AI outputs, skipping validation
- Solution: Culture of "trust but verify," metrics on AI errors

**My Philosophy:** AI should make good engineers great, not make mediocre engineers dependent.

---

## Part 8: Scenario-Based Questions (10 minutes)

**Q**: Let's do some rapid-fire scenarios. How would you use AI tools to handle these?

**Scenario 1: Production down. Dashboard shows no data for the past hour.**

**A**:
1. **Claude Code + MCP**: "Emergency diagnosis - dashboard_revenue shows no data since 10 AM"
2. **Airflow MCP**: Check revenue_pipeline DAG status → Failed at transform step
3. **Kubernetes MCP**: Get pod logs → OOMKilled error
4. **Database MCP**: Check source data → Data exists, pipeline didn't run
5. **Agent Decision**: Increase pod memory limit, restart pipeline
6. **Validation**: Monitor data flow resumption
7. **Slack MCP**: Notify team with RCA

**Time:** 5 minutes with AI vs. 20+ minutes manual

**Scenario 2: CEO asks "Why did sign-ups drop 15% last week?"**

**A**:
1. **Claude + RAG**: "Analyze sign-up trends, factors, hypotheses"
2. **RAG retrieves**: Recent deployments, marketing campaigns, seasonal patterns
3. **Database MCP**: Pull hourly sign-up data, segment by source/region
4. **Analysis Agent**: Correlation analysis with external factors
5. **Hypothesis**: Code deployment on Tuesday coincided with drop
6. **Git MCP**: Review that deployment's changes → Bug in sign-up form validation
7. **Report**: Generate executive summary with root cause, fix timeline

**Time:** 30 minutes with AI vs. 4+ hours manual

**Scenario 3: New regulation requires data retention changes. Need to audit entire data warehouse.**

**A**:
1. **RAG**: Search compliance docs, data governance policies
2. **Database MCP**: Query all tables, get metadata (row counts, columns, owners)
3. **Agent**: Classify tables by retention requirements, identify gaps
4. **Code RAG**: Find all ETL jobs writing to affected tables
5. **Agent**: Generate migration plan (archive policies, cleanup scripts)
6. **Human Review**: Validate classification, approve plan
7. **Git MCP**: Create PRs for policy changes, documentation updates

**Time:** 2 days with AI vs. 2+ weeks manual

**Q**: Impressive. Last scenario: You're starting a greenfield data platform. How do you leverage AI from day one?

**A**:
**Phase 1: Architecture Design (with Claude + RAG)**
```
Prompt: "Design a modern data platform for a B2B SaaS company with:
- 500K daily active users
- Real-time analytics requirements
- Compliance: GDPR, SOC 2
- Budget: $10K/month
- Team: 3 data engineers

RAG sources: Industry best practices, vendor docs, internal ADRs from previous projects

Output: Architecture proposal with trade-offs"
```

**Phase 2: Infrastructure as Code (with Claude Code + agents)**
```
Agent tasks:
1. Generate Terraform for AWS data infrastructure
2. Create Docker configs for services
3. Set up CI/CD pipelines (GitHub Actions)
4. Write monitoring and alerting rules (Datadog)

Human role: Review, adjust for org standards, approve
```

**Phase 3: Pipeline Development (with MCP + agents)**
```
1. Set up MCP servers for all data sources
2. Create agent-assisted pipeline generator skill
3. Use agents to scaffold first 10 pipelines
4. Human engineers customize for business logic
```

**Phase 4: Knowledge System (RAG)**
```
1. Index all generated code, docs, configs
2. Set up RAG for team Q&A
3. Build custom skills for common operations
4. Create onboarding guide with interactive AI tutor
```

**Outcome:** Platform operational in 3 weeks vs. 12+ weeks traditional approach. AI handles "undifferentiated heavy lifting," humans focus on business logic and strategy.

---

## Conclusion (5 minutes)

**Q**: This has been excellent. Last question: What advice would you give to data engineers who want to level up their AI tool usage?

**A**: Five key principles:

**1. Start Small, Learn Deeply**
- Don't try to use every AI tool at once
- Pick one (e.g., Claude Code), master it, then expand
- Understand how it works, not just how to use it

**2. Build a Feedback Loop**
- Measure time saved, code quality, errors introduced
- Adjust usage based on data, not hype
- Share learnings with team

**3. Maintain Engineering Rigor**
- AI is a tool, not a replacement for thinking
- Always understand generated code
- Never skip testing and review

**4. Invest in Infrastructure**
- Set up RAG for your docs
- Build reusable MCP servers
- Create shared skills library
- Good tooling multiplies AI effectiveness

**5. Stay Curious, Stay Critical**
- Experiment with new tools, but evaluate skeptically
- Question AI outputs, especially for critical systems
- Balance automation with human judgment

**Remember:** The goal isn't to replace engineers with AI, but to augment engineers so they can focus on high-value, creative work—architecture, optimization, innovation—instead of toil.

**Q**: Perfect. Thank you so much for your time. We'll be in touch soon!

**A**: Thank you! This was a great conversation. Looking forward to hearing from you.

---

## Interview Scorecard

**Technical Knowledge: 9/10**
- Deep understanding of Claude, MCP, agents, RAG
- Practical experience with production systems
- Strong grasp of architectural trade-offs

**Problem-Solving: 9/10**
- Systematic approach to complex scenarios
- Good balance of AI automation and human judgment
- Creative solutions to real-world problems

**Communication: 10/10**
- Clear explanations of complex topics
- Good use of examples and analogies
- Structured thinking

**Pragmatism: 9/10**
- Focuses on measurable impact, not hype
- Considers cost, security, maintainability
- Realistic about AI limitations

**Overall Recommendation: STRONG HIRE**

**Rationale**: Candidate demonstrates exceptional proficiency with modern AI tools while maintaining strong engineering fundamentals. Shows maturity in balancing automation with human oversight. Would be a force multiplier for the team and elevate overall AI tool adoption.
