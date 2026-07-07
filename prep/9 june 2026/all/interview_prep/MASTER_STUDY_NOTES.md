# Master Interview Study Notes — Jaya Arun Kumar Tulluri

*Built by merging every job description in `interview_prep/job_description/` (excluding the Ibridge study-guide folder and the right_job.in/masterclass folder) against my resume, project deep-dives, and prep notes in `interview_prep/resume_prep/`. Written in my own voice, active tense, as a single revision document. No duplicate concepts — every skill lives in exactly one place and gets cross-referenced elsewhere.*

---

## How to read this document

Three sections:

- **Section 1 — Matched Skills.** Every job-description requirement I can already back with real project evidence. Each topic: what they're asking, how I answer it, and the exact project I point to. Question-driven, but tight — I already know this material, so I don't re-teach myself textbook basics.
- **Section 2 — Gap Analysis.** Every requirement that appears in the job descriptions but that I *cannot* yet back with hands-on evidence. These get the full deep-dive treatment — why the thing exists, how it works, the trade-offs, the interview follow-ups — because these are the topics that will expose me if I bluff.
- **Section 3 — Project Explanations for the Interviewer.** Each project told as a discussion, the way I'd actually walk someone through it — architecture, the decisions, what I'd change.

A running theme across every job description: **Python + FastAPI + LLM/RAG + agentic AI + a vector database + prompt/eval discipline, deployed with Docker/CI and backed by SQL.** That intersection is exactly where my resume sits, so Section 1 is large and Section 2 is the honest edge I need to shore up.

---

## The consolidated requirement map (semantic merge of all 16 JDs)

I collapsed synonyms before organising. These clusters recur across Fornax/Infosys, TCS, ValueLabs, Akamai (×2), Ibridge, Codvo, Gainwell, Huzzle, Infosys-direct, Jobright, NextGenPros, Sezzle, Siemens, Trinamix, and RightFit:

| Cluster | Appears as (different JDs' wording) | Status |
|---|---|---|
| Python core | "strong Python", "advanced Python", "extensive Python programming" | **Matched** |
| FastAPI / REST APIs | "FastAPI", "RESTful backend APIs", "REST API development" | **Matched** |
| Async programming | "asyncio", "asynchronous programming", "async execution" | **Matched** |
| Pydantic | "Pydantic v2", "Pydantic data validation" | **Matched** |
| Testing | "pytest", "unit tests", "integration tests" | **Matched** |
| LangChain / orchestration | "LangChain", "AI orchestration frameworks" | **Matched** |
| LangGraph agentic workflows | "LangGraph flows", "state machines, tool nodes, HITL" | **Gap (adjacent)** |
| LLM APIs | "OpenAI/Anthropic/Azure OpenAI/Gemini", "streaming", "token economics" | **Matched (streaming = partial)** |
| RAG end-to-end | "chunking, embeddings, vector store, evaluation" | **Matched** |
| Advanced retrieval | "reranking, hybrid BM25+dense, query rewriting, multi-hop, Graph-RAG, HNSW tuning" | **Gap** |
| Vector DBs | Qdrant, FAISS, Pinecone, Weaviate, Milvus, Chroma, OpenSearch, pgvector | **Matched (Qdrant/FAISS); rest = gap** |
| Prompt engineering & eval | "prompt optimization", "hallucination detection", "eval frameworks" | **Matched (this is a strength)** |
| Agentic AI | "AI agents", "agent loop", "multi-agent orchestration", "A2A", "CrewAI/AutoGen/Swarm" | **Matched (single-agent loop); multi-agent frameworks = gap** |
| MCP | "Model Context Protocol", "MCP servers/tools" | **Gap (familiar, no build)** |
| AI-assisted dev tools | "Claude Code", "Cursor/Cline", "GitHub Copilot" | **Matched** |
| SQL | "analytical queries", "joins/aggregations", "schema design" | **Matched** |
| Frontend (React/TS) | "React + TypeScript", "frontend integration awareness" | **Matched (React); TS = partial** |
| Microservices | "microservices architecture", "gRPC", "Flask microservices" | **Matched** |
| gRPC | "gRPC" | **Matched (strong differentiator)** |
| Redis / caching | "Redis", "caching, batching, streaming" | **Matched** |
| PostgreSQL | "PostgreSQL", "relational schemas" | **Matched** |
| SQLAlchemy / Celery / GraphQL / Streamlit | TCS preferred stack | **Matched** |
| Docker / Kubernetes | "containerize", "K8s deployment" | **Matched** |
| CI/CD | "CI/CD pipelines", "logging & monitoring" | **Matched** |
| Auth (JWT/OAuth2/OIDC) | "JWT/OAuth", "authorization" | **Matched (JWT/RBAC); OIDC/SSO = partial** |
| Security / PII / governance / audit | "guardrails", "PII safety", "audit trails", "RBAC" | **Matched (RBAC strong)** |
| Doc ingestion (PDF/DOCX/OCR) | "document parsing", "OCR, images" | **Matched** |
| Snowflake / Databricks | "Snowflake basics", "enterprise data platforms" | **Gap (honest ramp)** |
| Cloud breadth | "AWS ECS/Lambda/Step Functions/Kinesis", "Azure OpenAI", "GCP" | **Partial (AppSync/AppFlow/IAM only)** |
| ML/DL fundamentals | "PyTorch/TensorFlow", "transformers/attention/tokenization", "NLP/CV/time-series", "fine-tuning" | **Gap (big one)** |
| MLOps / LLMOps | "MLflow", "model monitoring", "LLMOps" | **Partial (eval discipline yes, tooling no)** |
| Django | ValueLabs, NextGenPros want Django | **Gap (adjacent — I use FastAPI)** |
| Golang / R / Node deep | Sezzle Golang, Siemens R/R-Shiny, RightFit Node | **Gap (Node = partial via Abjayon)** |
| Knowledge graphs / ontology | "Graph DB", "ontology modeling", "Graph-RAG" | **Gap** |
| Domain compliance | HIPAA (Gainwell/RightFit), fintech (Sezzle) | **Partial (EU AI Act + telecom instead)** |
| Leadership / mentoring | "team lead", "mentor", "stakeholder management" | **Matched (partial — mentored 3 + 19 interns)** |

---

# SECTION 1 — MATCHED SKILLS AND TECHNOLOGIES

*Everything here I can defend with a real project. For each, I answer the concept and name the evidence. Cross-references point to the full project stories in Section 3.*

---

## 1.1 Python (core language)

**What they want:** 3–10 years of production Python; ability to "implement complex solutions."

**How I handle it:** 5+ years, spanning embedded firmware (Lakshya), Node/AWS backends (Abjayon), telecom automation (Nokia), and production LLM runtime work (Brane). I lead with the language internals that separate a senior from a scripter:

- **GIL** — only one thread executes Python bytecode at a time in CPython. Practical consequence: threading gives no parallelism for CPU-bound work, but *does* help I/O-bound work because a thread releases the GIL while waiting. So: I/O-bound → threads or async; CPU-bound → multiprocessing. Async doesn't fight the GIL at all — it's cooperative yielding at `await`, not threading.
- **Concurrency model choice** — asyncio (single-thread, high-concurrency I/O), threading (I/O with blocking libs), multiprocessing (true parallelism, CPU-bound). I've used all three: `multiprocessing.Pool` in NFTRACE to start traces on N nodes simultaneously, asyncio across the LLM-eval and Bias-auditor executors.
- **The traps I name unprompted** — mutable default arguments (`def f(x=[])` shares one list across calls; default to `None`), the same bug as a class attribute (`class Foo: items=[]` shared across instances), `is` vs `==` (identity vs value; `is` only for `None`).
- **Generators** — lazy `yield` for streaming a million-row result without holding 4GB in memory. Flat memory regardless of table size.
- **Memory** — reference counting plus a cycle-detecting GC.

**Evidence:** every project. Deepest systems-Python in NFTRACE (multiprocessing, XML-RPC, context managers) and Brane (agent loop, parser hardening).

---

## 1.2 FastAPI and REST API design

**What they want:** FastAPI RESTful backends, Pydantic validation, sync/await patterns, scalable endpoints (Fornax, Ibridge, Codvo, Siemens, NextGenPros, Huzzle, Akamai-adjacent).

**How I handle it:** FastAPI is my default backend and I can justify *why* over Flask/Django:

- **Async-native on ASGI** vs Flask/Django's synchronous WSGI core — async there is bolt-on, patchy, and the ORM/middleware often don't cooperate. FastAPI was built on ASGI from day one.
- **Pydantic validation for free** — typed request/response models, automatic 422 with field-level errors, zero boilerplate.
- **Auto OpenAPI/Swagger** — a live contract for the frontend team.

The depth points I raise:
- **`async def` vs `def`** — `async def` runs on the event loop (use with awaitable I/O like async DB drivers, `httpx.AsyncClient`); plain `def` runs in a threadpool so blocking work doesn't stall the loop. **The production failure:** calling `requests.get()` inside `async def` freezes the whole event loop under load — every user waits. Fix: `httpx.AsyncClient` or a sync endpoint.
- **`Depends` / dependency injection** — reusable DB-session and current-user dependencies; overridable in tests. Gotcha: a `yield`-based DB session closes at response time, *before* a BackgroundTask runs — so pass data into the task, not the session.
- **`BackgroundTasks` vs Celery** — in-process fire-and-forget vs durable, retryable, distributed queue. [[section-3-llm-eval]] deliberately chose Celery so a CI-gate evaluation can't be lost on a server restart.
- **Structuring a large app** — routers by domain (`APIRouter`), schemas separate from ORM models, a services layer, a database layer with Alembic, config from `pydantic-settings` (never hardcoded).
- **CORS** — the two production bugs: `allow_origins=['*']` with `allow_credentials=True` is rejected by browsers; and forgetting `Authorization` in `allow_headers` makes the preflight pass but the real call fail silently.

**Evidence:** NFTRACE (lifecycle REST API), RF Keyword Generator (`/generate`), 5G pipeline (`/analyze`), EMS, LLM Eval, Bias auditor, Prompt Regression — every one exposes a FastAPI surface.

---

## 1.3 Async programming (asyncio)

**What they want:** "asyncio", "asynchronous programming", "async execution" (Fornax, Codvo, Jobright, Sezzle).

**How I handle it:** I frame async as cooperative concurrency for I/O-bound workloads — the event loop swaps tasks at `await` points instead of blocking a thread. I've used it two ways:
- **Concurrent LLM fan-out** — Bias auditor and LLM-eval dispatch hundreds of model calls with `asyncio.gather`, capped by an `asyncio.Semaphore` so I don't blow the provider's rate limit (a 100-variant × 5-run audit is 500 calls; without the semaphore the quota dies instantly).
- **Async web + async DB** — FastAPI with SQLAlchemy 2.0 async + asyncpg so a request never blocks the loop on a DB write.

The rule I state: async endpoint *plus* async libraries, or a sync endpoint for blocking work — never blocking code inside `async def`.

**Evidence:** LLM Eval Framework, Bias & Fairness Auditor, Prompt Regression Suite (all async-first with Semaphore concurrency caps).

---

## 1.4 Pydantic (v2)

**What they want:** "Pydantic v2", structured output handling, data validation.

**How I handle it:** Pydantic is the backbone of every service I build — typed models validate and coerce at parse time, raise clear errors, and cost effectively nothing at runtime (v2 is ~10× faster than v1). I use it three ways: request/response validation in FastAPI, **schema enforcement on LLM JSON output before it touches the database**, and typed config via `pydantic-settings` from env vars. The LLM-output use is the one that matters for AI roles — raw model JSON fails to parse 10–20% of the time, so I validate with Pydantic and retry/fallback on failure.

**Evidence:** EMS (Pydantic enforces the 22-field employee schema on Ollama output), LLM Eval (Pydantic v2 request/response schemas), Bias auditor (`BiasReport` as the universal Pydantic contract across CLI/API/dashboard/PDF), Prompt Regression (`TestCase`/`AssertionConfig` validated at load).

---

## 1.5 pytest and testing discipline

**What they want:** pytest, unit + integration tests (Fornax, Siemens, Akamai, ValueLabs).

**How I handle it:** Three levels, consistently: unit tests per component, integration tests hitting the FastAPI stack via `httpx`/TestClient with dependencies overridden (real DB swapped for a test DB, external services mocked), and a few end-to-end. Concrete examples I give: NFTRACE tested with mock XML-RPC servers and synthetic pcap fixtures; RF generator unit-tested each stage plus deliberately-broken templates to prove the RF parser catches them; Prompt Regression *is* "pytest for prompts."

**Evidence:** NFTRACE, RF Keyword Generator, Prompt Regression Suite.

---

## 1.6 LangChain and RAG end-to-end

**What they want:** LangChain, RAG (chunking → embeddings → vector store → retrieval → evaluation) shipped to production (Fornax, TCS, Codvo, Gainwell, Huzzle, NextGenPros, Trinamix, RightFit, Jobright, Siemens).

**How I handle it:** I built a production RAG pipeline, not a tutorial. The full chain in [[section-3-5g-pipeline]]:
- **Chunking / knowledge base** — ~200 curated 5G error patterns, each with an embeddable text field plus metadata (vendor, layer, severity, fix).
- **Embeddings** — OpenAIEmbeddings (1536-dim) / sentence-transformers.
- **Vector store** — Qdrant, cosine similarity, HNSW index.
- **Retrieval** — LangChain `QdrantVectorStore.as_retriever(k=5, filter=...)`, then `RetrievalQA.from_chain_type` with `return_source_documents=True`.
- **Generation** — Claude synthesises a contextual fix from the retrieved patterns.
- **Evaluation** — separately, my LLM-Eval framework scores *faithfulness* (did the answer stay inside retrieved context) vs *hallucination* (claims unsupported by reference) — the exact eval piece these JDs ask for.

Why LangChain over hand-rolling: `return_source_documents` for engineer trust, one-line swappability of vector DB/LLM (I tested FAISS before Qdrant), clean prompt-template management. The trade-off I name: LangChain hides the final prompt — enable `verbose=True` in dev, disable in prod.

**Evidence:** 5G Failure Detection Pipeline (LangChain RetrievalQA + Qdrant); EMS (FAISS RAG for employee semantic search); LLM Eval (faithfulness scorer). This is a core strength.

---

## 1.7 Vector databases (Qdrant, FAISS)

**What they want:** "Vector DB", Pinecone/Chroma/FAISS/Milvus/Weaviate/Qdrant/pgvector, semantic search (TCS, Codvo, Huzzle, Sezzle, Trinamix, Siemens, RightFit, Jobright).

**How I handle it:** I've shipped two: **Qdrant** in the 5G pipeline and **FAISS** in EMS. The decision story is the strongest part:

- **Why Qdrant over FAISS/Chroma/pgvector** — the requirement was *vendor + layer-specific* retrieval (Nokia errors must never match Ericsson patterns). FAISS has no native metadata filtering — you'd retrieve on similarity then filter in Python, so cross-vendor patterns are still in the ranking. Qdrant's `must` filter runs *at the database level* before semantic ranking — faster and never surfaces a wrong-vendor fix. Chroma filters post-retrieval; pgvector would add Postgres I didn't need.
- **Why cosine over dot/Euclidean** — cosine measures angle, not magnitude; a short and a long description of the same error point the same direction. Correct for text similarity.
- **Score threshold** — below 0.65 similarity I return "unknown — manual review" rather than generating a hallucinated fix from a bad match.
- **FAISS where it fits** — EMS is single-node, in-memory, no filtering need — FAISS is the right zero-infra choice there.

I can honestly say Qdrant and FAISS; Weaviate/Pinecone/Milvus I understand conceptually (see [[section-2-vector-db-breadth]]) but haven't shipped.

**Evidence:** 5G pipeline (Qdrant + metadata filtering), EMS (FAISS).

---

## 1.8 Prompt engineering, LLM evaluation, hallucination detection

**What they want:** prompt engineering/optimization, hallucination reduction, guardrails, automated evals, prompt regression testing (TCS, Codvo, Gainwell, Huzzle, Fornax "own prompt evaluation", Sezzle).

**How I handle it:** This is my sharpest edge — I've built *three* tools that live entirely in this space, which most candidates can't claim:

- **Prompt assembly for an agent loop** (Brane) — system prompt, grounded input injection, tool-registry context, and retry-with-feedback for a verifier correction loop.
- **LLM-as-Judge** — five-dimension rubric (accuracy, relevance, completeness, clarity, safety), scored 1–5, normalised to 0–1, returned as strict JSON. I discard the model's self-reported "overall" and recompute the weighted score client-side because LLM arithmetic is unreliable.
- **Hallucination detection** — decompose a response into atomic claims, classify each against a reference as SUPPORTED / UNSUPPORTED / CONTRADICTED, score = 1 − (unsupported+contradicted)/total.
- **Faithfulness vs accuracy** — the distinction I lead with: faithfulness = "did the answer stay inside retrieved context," independent of whether the context was correct. High faithfulness + wrong answer → the retriever is the problem; low faithfulness → the model is bypassing the retriever (context leakage).
- **Consistency** — re-run the same prompt N times at temperature 0.7, mean pairwise cosine similarity; catches prompts that are right once and unreliable on average.
- **Anti-self-bias** — the judge is always a *different provider* than the model under test (claude-* judged by OpenAI and vice-versa), enforced structurally at construction, not documented as a guideline.
- **Prompt regression as a CI gate** — tiered assertions (deterministic rules → local semantic similarity → paid judge), fail-fast for ~50% cost reduction, delta-based regression against a stored baseline, blocking PR merges.

**Evidence:** LLM Evaluation Framework, Prompt Regression Suite, Bias & Fairness Auditor, Brane prompt assembly. This trio is my differentiator for any AI-engineer JD.

---

## 1.9 Agentic AI (single-agent loop)

**What they want:** "AI agents", "agent loop", "tool-calling workflows", "multi-step task planning" (TCS, Codvo, Jobright, Trinamix, RightFit, Sezzle, Gainwell).

**How I handle it:** At Brane I contributed to a **production AI-agent runtime** for a no-code platform. I owned real parts of the loop:
- **Agent loop development** — prompt assembly, grounded input injection, tool-registry context, and a **verifier correction loop** (retry-with-feedback when the output fails validation).
- **Tool invocation** — reduced tool-invocation overhead; hardened the response parser for malformed LLM output.
- **Agent identity & execution state** in PostgreSQL — agent identity tables, multi-agent LO junction tables, attribute-level RBAC rows, and execution sibling tables (`lo_input_execution_agent`, `agent_run_scratch`, `agent_episodes`).

So I can speak concretely about tool-calling, planning/execution, memory/state persistence, and self-healing (the verifier loop). What I'm *honest* about: this was a **single-agent** loop, not a multi-agent orchestration framework — see [[section-2-multi-agent]].

**Evidence:** Brane AI Agent runtime ([[section-3-brane]]).

---

## 1.10 gRPC and microservices

**What they want:** gRPC, microservices architecture, service-to-service communication (TCS preferred, Akamai, Ibridge, RightFit).

**How I handle it:** gRPC is a genuine differentiator — I integrated an **LLM inferencing layer via a gRPC model gateway** at Brane, doing multi-provider model routing (instruct / thinking / vision variants) with stateless horizontal scaling. So I explain it from real use: binary protobuf over HTTP/2, strongly typed via schema, streaming support — ideal for *internal* service-to-service calls where REST/JSON overhead isn't worth it. REST for public/browser-facing, gRPC for high-performance internal.

On microservices generally, my honest senior take: start with a modular monolith, split only when team size / independent scaling / deployment cadence justify it — the real cost is distributed transactions, cross-service debugging, and consistency across boundaries. I've *seen* teams go microservices-first and spend six months on infra instead of product.

**Evidence:** Brane gRPC model gateway; NFTRACE (distributed REST service with an XML-RPC node layer).

---

## 1.11 Redis and caching

**What they want:** Redis, caching, batching (TCS preferred, Codvo, ValueLabs).

**How I handle it:** I've used Redis for two distinct patterns, and I make the distinction:
- **Response/lookup caching** — 5G pipeline caches frequent error lookups (cache-aside: check Redis, on miss hit the source and populate with a TTL).
- **Parallel-execution isolation** — NFTRACE stores each trace session under a unique key with a 1-hour TTL, so N concurrent test workers never collide and orphaned sessions (crashed worker) auto-expire. I explain *why Redis over an in-memory dict* (survives restarts) and *why Redis over SQLite for hot state* (sub-millisecond, concurrent-safe).

Caching depth I raise: cache invalidation (delete the key on write), and the thundering-herd problem on a hot key expiry (fix: distributed lock / `SETNX` so only one request rebuilds the cache).

**Evidence:** 5G pipeline (lookup cache), NFTRACE (session isolation), LLM Eval (Redis as Celery broker).

---

## 1.12 PostgreSQL, SQL, and schema design

**What they want:** SQL analytical queries, relational schema design, PostgreSQL (Fornax, Ibridge, Akamai, NextGenPros, Sezzle).

**How I handle it:** PostgreSQL is my deepest DB. I did real schema design at Brane (agent identity, junction, RBAC, execution tables). SQL depth I cover:
- **Joins** — inner/left/right/full/self; LEFT JOIN + NULL check to find records with no related row.
- **WHERE vs HAVING** — row filter before grouping vs group filter after (execution order).
- **Indexes and the trade-off** — B-tree speeds reads, slows writes, costs storage; index what you filter/join/sort on, don't over-index; verify with `EXPLAIN ANALYZE` (Seq Scan on a big table = red flag).
- **The classic slow-query bug** — `WHERE DATE(created_at)='...'` wraps the column in a function and kills the index; rewrite as a range (`>= AND <`) and it goes from seconds to milliseconds.
- **N+1** — one query per row instead of a join; fix with eager loading.
- **Many-to-many** — junction/bridge table with two foreign keys (I built exactly this at Brane).
- **ACID, normalization, parameterized queries** (SQL-injection prevention).

**Evidence:** Brane PSQL schema; SQL solutions in my prep notes; EMS (PostgreSQL + SQLAlchemy).

---

## 1.13 SQLAlchemy, Celery, Streamlit, GraphQL

**What they want:** TCS preferred stack + Gainwell (Streamlit "must") + Abjayon-era GraphQL.

**How I handle it:**
- **SQLAlchemy 2.0 async** — same ORM models across SQLite (dev) and PostgreSQL (prod) via one `DATABASE_URL` swap; async sessions match the async runner. Used in LLM Eval, Prompt Regression, Bias auditor, EMS.
- **Celery** — durable task queue (Redis broker) with retries; chosen over `BackgroundTasks` where losing a job is unacceptable (LLM-eval CI gate).
- **Streamlit** — my go-to internal-tool UI (RF generator, all four eval/audit dashboards). I know its trade-off: fast and Python-only, but functional-not-beautiful, so I pair it with a FastAPI backend for testability/reusability rather than locking logic in the UI.
- **GraphQL** — built and optimised GraphQL + REST APIs at Abjayon, with AWS AppSync (managed GraphQL).

**Evidence:** across LLM Eval, Prompt Regression, EMS, RF generator, Abjayon.

---

## 1.14 Docker, Kubernetes, CI/CD

**What they want:** containerize AI services, deploy on K8s, CI/CD pipelines, logging/monitoring (TCS, Akamai, Codvo, Huzzle, Trinamix, RightFit, Ibridge).

**How I handle it:**
- **Docker** — ran Qdrant as a container with a persistent volume; multi-stage builds; `docker-compose up -d` brings up the whole LLM-eval stack (Postgres, Redis, API, worker, dashboard) with health-check ordering. **Best-practice checklist I authored at Nokia and it became team standard**: slim pinned base image (never `python:latest` — mutable tag, silent breakage), non-root user, layer ordering for cache, `.dockerignore`, and **never bake secrets as ENV** (visible in `docker history`) — inject at runtime.
- **Kubernetes** — validated K8s pod health and real-time cluster dashboards during 5G Core UDM/AUSF testing; the resume lists Kubernetes as a core skill.
- **CI/CD** — Prompt Regression ships two GitHub Actions workflows (a PR merge-gate that blocks on quality regression, and a weekly full-suite drift monitor); NFTRACE integrates into Nokia Continuous Delivery (NCD) with pre/post-test hooks.

**Evidence:** LLM Eval (docker-compose), 5G pipeline (Qdrant container), Prompt Regression (GitHub Actions), NFTRACE (NCD), Nokia Docker checklist.

---

## 1.15 Authentication, RBAC, API security

**What they want:** JWT/OAuth, authorization, API security, guardrails, audit trails, RBAC (Ibridge, RightFit, Codvo, Sezzle).

**How I handle it:**
- **JWT** — three parts (header.payload.signature), signed-not-encrypted (so no secrets/PII in the payload — anyone can base64-decode it in DevTools), stateless verification with no DB lookup. Revocation: short expiry + a Redis blacklist keyed on the `jti` claim.
- **Access vs refresh tokens**, **authn vs authz**, **OAuth2 authorization-code flow**, and **OIDC** as the identity layer on top (ID token) — I can explain all four, though I flag SSO/OIDC as more read than built ([[section-2-oauth-oidc]]).
- **Attribute-level RBAC** — I *implemented* this at Brane: permissions defined down to individual attributes, not just broad roles, with a caching layer. This is real authorization work, not theory.
- **The #1 API vuln I name unprompted** — broken object-level authorization (BOLA): valid token, real user, but the code never checks the user *owns* the resource (`GET /ads/{id}` verifies the token, not ownership). OWASP's top API risk.

**Evidence:** Brane attribute-level RBAC + caching; the auth flows in my technical prep.

---

## 1.16 Document ingestion (PDF, OCR, images)

**What they want:** document parsing (PDF, DOCX, OCR, images), ingestion pipelines (Codvo, Gainwell healthcare docs).

**How I handle it:** Two shipped pipelines:
- **EMS** — `pdfplumber` for PDF text, `pytesseract` (Tesseract OCR) fallback for image resumes, a resume-validity scoring gate (≥40/100) *before* any LLM call to save inference and block garbage, then chunk (500 chars, 100 overlap) → embed → FAISS.
- **Financial Statement Parser** — Tesseract.js (WASM, in-browser) OCR, pdf.js to rasterise PDF pages to canvas, then only the *extracted text* (capped at 8k chars) goes to Gemini — the original file never leaves the browser.

**Evidence:** EMS, Financial Statement Parser.

---

## 1.17 LLM APIs, multi-provider routing, model selection, token economics

**What they want:** integrate OpenAI/Anthropic/Gemini/Llama/Qwen/Mistral, streaming, token economics, model optimization (Fornax, TCS, Huzzle, Gainwell, NextGenPros, many).

**How I handle it:** I've integrated Anthropic (Claude Sonnet/Haiku), Google Gemini, and local models via **Ollama (qwen2.5)** — cloud and local. The senior signal is **model *selection*, not always reaching for the biggest model**:
- **Haiku vs Sonnet routing** (5G pipeline) — a threshold function routes high-confidence, non-critical matches to Haiku (fast/cheap) and ambiguous/critical ones to Sonnet (deep reasoning), cutting API cost ~60% with no accuracy loss on hard cases.
- **Haiku for entity extraction** (RF generator) — structured extraction needs no reasoning, so Haiku at 3–5× lower cost and ~500ms.
- **Local Ollama** (EMS) — privacy (data never leaves the machine), zero API cost, direct control of temperature/context/seed; trade-off is 2–5s inference on a 6GB RTX 3060 (I switched qwen2.5:14b→7b-instruct to fit VRAM).
- **Cost discipline generally** — tiered fail-fast in Prompt Regression (~50% saving), semaphore-capped concurrency, local sentence-transformers instead of paid embeddings where accuracy allows.

**Token economics** I speak to via routing + tiering + local-model fallbacks. **Streaming** I flag as partial ([[section-2-streaming]]).

**Evidence:** 5G routing, RF Haiku extraction, EMS Ollama, Prompt Regression tiering.

---

## 1.18 Claude Code / AI-assisted development

**What they want:** "Drive multi-file changes through Claude Code and review output critically" (Fornax); GitHub Copilot / Claude Code for accelerated dev (Siemens).

**How I handle it:** Claude Code is in my resume's core skills and I use it for exactly what Fornax describes — multi-file changes with critical review of the output, not blind acceptance. I've also used AI-assisted robustness review as a *technique* (EMS's `AI_CONSULTATION_PROMPT.md` produced an edge-case list — encoding issues, prompt injection, bulk-operation safety — faster than discovering them organically). The "review critically" part is the point: I treat generated code as a draft to verify, not truth.

**Evidence:** resume core skill; EMS AI-assisted review; 5G pipeline built with claude-sonnet.

---

## 1.19 React and frontend integration

**What they want:** React + TypeScript working knowledge, frontend-integration awareness, "understand API consumption patterns from frontend" (Fornax, Ibridge, ValueLabs, Huzzle, Sezzle, RightFit).

**How I handle it:** I build the React frontends for my own tools (EMS is React + Vite with chat UI, upload, polling; Financial Parser is React + Vite + Tailwind + Recharts). So I understand API-consumption patterns from *both* sides — I design the endpoint and consume it. On the "frontend-integration awareness" Ibridge asks for (React/Next.js, smooth data exchange, debug API issues impacting UI), I've lived it: CORS, polling for async job status, consistent error shapes so the frontend handles errors uniformly. **TypeScript** specifically I mark partial ([[section-2-typescript]]) — I use TS types in Astro/Blog and read it fine, but my production frontends are JSX, not heavy TS.

**Evidence:** EMS (React+Vite), Financial Parser (React+Vite+Tailwind+Recharts), Abjayon (frontend/backend pipeline integration).

---

## 1.20 Git, Agile, code review, mentoring

**What they want:** Git branching/PRs, Agile/Scrum, collaboration, code reviews; some ask for team-lead/mentoring (all JDs; Gainwell/Sezzle/Trinamix leadership).

**How I handle it:**
- **Git** — feature branch → small focused commits → PR → CI runs lint+tests → review → merge. Merge vs rebase (rebase only local/unshared work; never rewrite shared history).
- **Agile** — Scrum with sprints, standups, planning, review, retro; JIRA; delivered sprint reports with zero missed deliveries during 5G UDM/AUSF testing.
- **Code review + mentoring** — I *authored* Python code-review checklists (thread safety, Docker best practices) adopted as team standard (25% code-quality improvement) and mentored 3 mid-level engineers to senior readiness plus supervised 19 interns.

**Evidence:** Nokia (checklists, mentoring, Agile), Prompt Regression / NFTRACE (CI).

---

## 1.21 Node.js and AWS (partial-matched, honest scope)

**What they want:** Node backend (RightFit, NextGenPros JS full-stack); AWS services (ValueLabs ECS/Lambda/Step Functions/Kinesis, Gainwell/Huzzle/Sezzle cloud, RightFit EC2/Lambda/ECS/S3/RDS).

**How I handle it:** I did **Node.js backend + AWS** at Abjayon — integrated AppSync and AppFlow (15% data-retrieval improvement), built/optimised GraphQL + REST APIs, managed IAM roles for secure access. So I can claim Node and AWS honestly — but I scope it: **AppSync, AppFlow, IAM** are my hands-on AWS surface, not ECS/Lambda/Step Functions/Kinesis. Those I understand conceptually and cover in [[section-2-cloud-breadth]]. I don't overclaim the breadth of the ValueLabs/RightFit AWS lists.

**Evidence:** Abjayon (Node + AWS AppSync/AppFlow/IAM + GraphQL).

---

# SECTION 2 — GAP ANALYSIS AND NON-MATCHED CONCEPTS

*Requirements that appear in the job descriptions but that I cannot yet back with hands-on evidence. Full deep-dive per topic — why it exists, how it works, the trade-offs, the follow-ups an interviewer will push on — plus my honest bridge from what I* do *know. These are the topics where bluffing gets caught, so I over-prepare them.*

---

## 2.1 LangGraph specifically (I have LangChain, not LangGraph) {#section-2-langgraph}

**Who asks:** Fornax, TCS, Gainwell, Trinamix, Siemens, RightFit (preferred), Codvo (LangGraph agentic workflows).

**The gap:** I've shipped LangChain RetrievalQA, but not LangGraph. Several JDs name LangGraph explicitly for *agentic* workflows.

**Deep dive — what LangGraph is and why it exists:**
- LangChain's original chains are largely linear (retrieve → stuff → generate). Agents need **cycles**: plan → call tool → observe → decide → maybe loop → finish. LangGraph models the agent as a **state graph** — nodes are functions (an LLM call, a tool call, a router), edges are transitions, and a shared **state object** flows through and accumulates.
- **Core primitives:** the `State` (a typed dict that each node reads/updates), **nodes** (including tool nodes and LLM nodes), **conditional edges** (route based on state — e.g. "if the model asked for a tool, go to the tool node; else finish"), and **cycles** (loop back until a stop condition).
- **Human-in-the-loop (HITL):** LangGraph can checkpoint state and pause at a node for human approval before continuing — exactly what Siemens/RightFit mean by "human-in-the-loop patterns."
- **Persistence / memory:** a checkpointer persists graph state between steps, giving durable, resumable agents.

**My honest bridge:** I built the *same concepts by hand* at Brane — an agent loop with tool-registry context, a verifier correction loop (retry-with-feedback = a conditional edge back to the generation node), and state persisted in PostgreSQL (`agent_run_scratch`, `agent_episodes` = a hand-rolled checkpointer). So I understand the execution model deeply; LangGraph is the framework that formalises what I implemented manually. I'd be productive fast.

**Follow-ups I prep for:**
- *"Difference between LangChain and LangGraph?"* — LangChain = composable chains/components, largely DAG/linear; LangGraph = stateful graphs with cycles and conditional routing, built for agents that loop.
- *"How do you stop an agent looping forever?"* — a recursion/step limit on the graph plus a stop condition in the router node (I did this at Brane with the verifier loop's retry cap).
- *"Where does state live?"* — the shared State object; persisted via a checkpointer for durability/HITL.

---

## 2.2 Multi-agent orchestration & frameworks (CrewAI, AutoGen, OpenAI Swarm, A2A) {#section-2-multi-agent}

**Who asks:** Gainwell, Codvo (multi-agent orchestration), Jobright (multi-agent frameworks), Trinamix, Sezzle, RightFit (A2A, CrewAI/AutoGen/OpenAI Agents SDK), TCS nice-to-have.

**The gap:** Brane was a *single*-agent loop. I haven't built multi-agent systems or used CrewAI/AutoGen/Swarm.

**Deep dive:**
- **Why multi-agent** — split a complex task across specialised agents (a planner, a researcher, a coder, a critic) so each has a focused prompt/toolset; a supervisor/orchestrator routes work and aggregates results. The bet is that specialisation + review beats one giant prompt.
- **Coordination patterns** — (a) **supervisor/hierarchical** (one orchestrator delegates to workers), (b) **peer/round-robin** (agents converse turn-by-turn, e.g. AutoGen group chat), (c) **A2A (agent-to-agent)** protocols for structured message passing between autonomous agents.
- **The frameworks:**
  - **CrewAI** — role-based "crew" of agents with defined roles/goals/tools and tasks; good for structured pipelines.
  - **AutoGen (Microsoft)** — conversational multi-agent; agents (including a human proxy) exchange messages until a termination condition; strong for code-gen + execution loops.
  - **OpenAI Swarm / Agents SDK** — lightweight handoffs between agents with shared context.
  - **LangGraph** — can also express multi-agent as a graph where nodes are whole agents.
- **The hard parts (what I'd raise to show depth):** cost blow-up (every agent turn is tokens), infinite loops between agents (need turn caps + termination checks), shared-state consistency, error propagation, and evaluation (how do you know the crew did better than one agent?).

**My honest bridge:** I own the *primitives* — tool-calling, a verifier/critic loop, state persistence, prompt assembly per role. Multi-agent is composing several of my single agents with a supervisor. My eval background ([[section-1]] 1.8) is directly useful here because judging multi-agent output is itself an eval problem. I'd start with CrewAI or LangGraph for structure.

**Follow-up:** *"When would you NOT use multi-agent?"* — when a single well-prompted agent with good tools suffices; multi-agent multiplies cost, latency, and failure surface. Reach for it only when tasks genuinely decompose into specialised, independently-verifiable subtasks.

---

## 2.3 Advanced retrieval — reranking, hybrid search, query rewriting, HNSW tuning, Graph-RAG {#section-2-advanced-retrieval}

**Who asks:** Codvo (chunking strategies, hybrid BM25+dense, reranking, Graph-RAG, query rewriting, multi-hop, HNSW tuning), Siemens (hybrid search), Fornax/TCS (RAG quality).

**The gap:** My 5G RAG used filtered dense semantic search — solid, but not the advanced retrieval stack these JDs list.

**Deep dive on each:**
- **Hybrid retrieval (BM25 + dense)** — BM25 is sparse/keyword (great for exact terms, IDs, rare tokens); dense embeddings capture semantics. Hybrid runs both and fuses scores (e.g. **Reciprocal Rank Fusion**) so you get exact-match precision *and* semantic recall. Why it matters: pure dense misses exact identifiers (an error code, a part number); pure BM25 misses paraphrases.
- **Reranking** — first-stage retrieval (fast, approximate) returns top-50; a **cross-encoder reranker** (e.g. a BERT-style model that reads query+doc *together*) re-scores them for precision and you keep top-5. Bi-encoders (embeddings) are fast but coarse; cross-encoders are slow but accurate — so you rerank only the shortlist. This is the single highest-ROI RAG upgrade.
- **Query rewriting / multi-hop** — rewrite a vague or conversational query into a retrieval-optimised one; for multi-hop questions, decompose into sub-queries, retrieve for each, then synthesise. (I did compound-query decomposition in EMS, which is the same idea applied to CRUD — an honest bridge.)
- **Chunking strategies** — fixed-size vs **semantic/structure-aware** (split on headings/sections so a chunk is a coherent unit), with overlap to preserve context across boundaries. I used 500/100 fixed chunking in EMS; the upgrade is structure-aware.
- **HNSW tuning** — HNSW (Hierarchical Navigable Small World) is the graph index most vector DBs use for approximate nearest neighbour. Key params: `M` (edges per node — higher = better recall, more memory), `ef_construction` (build-time accuracy), `ef_search` (query-time accuracy vs latency). Tuning trades recall against speed/memory. I've *used* HNSW (Qdrant default) but not tuned these knobs.
- **Graph-RAG** — instead of (or alongside) vector search, build a knowledge graph of entities/relations and retrieve by traversing it; strong for multi-hop reasoning and "connect facts across documents" questions. Ties to ontology modeling ([[section-2-knowledge-graphs]]).

**My honest bridge:** I understand the retrieval pipeline deeply (I built the filtered-dense version and the eval that measures whether retrieval is the failure point — [[section-1]] 1.8). Adding a reranker or hybrid fusion is a bounded upgrade to a pipeline I already own end-to-end.

**Follow-up:** *"Your RAG answers are wrong — how do you debug?"* — my faithfulness-vs-hallucination eval isolates it: high faithfulness + wrong answer → retrieval brought bad/incomplete docs → improve chunking, add hybrid + reranking; low faithfulness → the model is ignoring context → prompt/grounding fix.

---

## 2.4 Vector DB breadth — Weaviate, Pinecone, Milvus, OpenSearch, pgvector {#section-2-vector-db-breadth}

**Who asks:** Codvo (Qdrant/Weaviate/OpenSearch), Siemens (Weaviate), Sezzle (Pinecone/Weaviate/pgvector), TCS (Pinecone/Chroma/FAISS/Milvus/Weaviate), Huzzle (Pinecone/Weaviate/FAISS/Chroma).

**The gap:** shipped Qdrant + FAISS; the rest conceptual.

**Deep dive — how they differ (so I can speak to any of them):**
- **Pinecone** — fully-managed, serverless, zero-ops; you pay and it scales; no self-hosting. Pick when you want managed and don't want to run infra.
- **Weaviate** — open-source, supports hybrid search natively, has modules for built-in vectorisation; strong for hybrid + GraphQL-style queries.
- **Milvus** — open-source, built for *massive* scale (billions of vectors), GPU indexing; pick at very large scale.
- **OpenSearch/Elasticsearch** — you get BM25 keyword search *and* vector kNN in one engine → natural home for hybrid retrieval if you're already on Elastic.
- **pgvector** — a Postgres extension; vectors live *next to* your relational data, one DB, transactional. Pick when you're already on Postgres and scale is moderate (this is the "why not pgvector" I answered in reverse for the 5G pipeline).
- **Qdrant (mine)** — open-source, Rust, first-class metadata filtering at the DB level (my decisive reason), HNSW, Docker-friendly.

**The framing I use:** they all do ANN over HNSW-ish indexes; the differentiators are (1) managed vs self-hosted, (2) native hybrid support, (3) metadata-filtering quality, (4) scale ceiling, (5) whether vectors sit beside your relational/keyword data. Because I chose Qdrant *specifically for filtering* over FAISS/Chroma/pgvector, I can reason about any of these on those axes.

---

## 2.5 MCP (Model Context Protocol) — building servers/tools {#section-2-mcp}

**Who asks:** Codvo (MCP tools), Siemens (build MCP servers), RightFit (familiarity), TCS (nice-to-have). MCP is in my resume skills list.

**The gap:** I list MCP as a familiarity, but haven't built an MCP server.

**Deep dive:**
- **What MCP is** — an open protocol (Anthropic) that standardises how an LLM app connects to external tools, data, and context. Instead of bespoke integrations per tool, a model host speaks MCP to any MCP **server**, which exposes **tools** (callable functions), **resources** (readable data/context), and **prompts** (templates). Think "USB-C for LLM tools."
- **Why it exists** — before MCP, every agent hard-wired its own tool integrations; MCP decouples the model/host from the tools so a tool built once works with any MCP-speaking client.
- **Architecture** — host (the LLM app) ↔ client ↔ server(s); JSON-RPC message passing; a server advertises its tools/resources and the host's model can invoke them.
- **How it maps to what I know** — my Brane "tool registry context" is conceptually an in-house version of what MCP standardises. Building an MCP server = wrapping my existing tool functions behind the MCP interface (advertise schema, handle invoke calls). That's a bounded task given I've built tool-calling agents.

**My honest line:** "I've used the concept — tool registries feeding an agent loop — and I understand MCP's client/host/server model. I haven't published an MCP server yet, but wrapping existing tools in it is a small step from what I built at Brane."

---

## 2.6 ML/DL fundamentals — training, transformers, NLP, CV, time-series, fine-tuning {#section-2-ml-fundamentals}

**Who asks:** Gainwell (ML/DL, multimodal LLMs, NLP, CV, time-series, PyTorch/TensorFlow, fine-tuning), Sezzle (supervised/unsupervised, feature engineering, model eval, transformer architecture, attention, tokenization, fine-tuning, NER/text-classification), Huzzle (PyTorch/TensorFlow/HF), NextGenPros (zero/few-shot, fine-tuning), Codvo (fine-tuning retrievers/small LLMs).

**The gap — the biggest one:** I use LLMs as **APIs**, not as models I train. I haven't trained a neural net, fine-tuned an LLM, or done classical ML/CV/time-series. This is the honest boundary of "AI Engineer (application)" vs "ML Engineer/Data Scientist."

**Deep dive so I'm not blank on the theory:**
- **Transformer architecture** — the core is **self-attention**: every token attends to every other token, weighting relevance (Q·K softmax → weighted sum of V). Stacked attention + feed-forward layers, positional encodings for order, multi-head attention to capture different relation types. **Tokenization** — text → subword tokens (BPE/WordPiece); why it matters for token economics ([[section-1]] 1.17) and context limits.
- **BERT vs GPT** — BERT is an *encoder* (bidirectional, good for classification/NER/embeddings); GPT is a *decoder* (autoregressive, good for generation). Sezzle names both.
- **Fine-tuning spectrum** — full fine-tuning (update all weights, expensive) → **PEFT/LoRA** (freeze the base, train small low-rank adapter matrices — cheap, the standard now) → **instruction tuning** / **RLHF** (align behaviour). vs **zero/few-shot prompting** (no weight update — what I actually do) and **RAG** (inject knowledge at inference, no training). The senior framing: *prefer prompting/RAG before fine-tuning; fine-tune only when you need a behaviour/format/domain the base model won't do reliably and you have quality labelled data.*
- **Classical ML** — supervised (labelled → classify/regress) vs unsupervised (cluster/dimensionality-reduction); feature engineering; train/val/test split; overfitting/regularisation; model eval (precision/recall/F1, ROC-AUC, confusion matrix).
- **Where I DO have real footing** — my Bias & Fairness Auditor uses genuine statistics: **one-way ANOVA** (do group means differ significantly, p<0.05), **Cohen's d** (effect size), sentence-embeddings + cosine similarity, VADER + a DistilBERT transformer fallback. So I've done statistical rigour and used transformer models as components, even if I didn't train them. That's my bridge into "model evaluation" and "statistical inference."

**My honest positioning:** "My lane is applied LLM/AI engineering — RAG, agents, evaluation, production integration — not model training. I understand transformer internals, the fine-tuning spectrum, and I've done real statistical evaluation in my bias-auditor. For a role that's 80% building LLM applications and 20% light ML, I'm strong; for a role that's core model training or CV/time-series research, I'd be honest that that's a growth area." I never bluff a training project I didn't do.

---

## 2.7 Snowflake / Databricks / enterprise data platforms {#section-2-snowflake}

**Who asks:** Ibridge (Snowflake working knowledge), Trinamix (Snowflake/Databricks).

**The gap:** My warehouse work is PostgreSQL; no hands-on Snowflake/Databricks.

**Deep dive (enough to support, per Ibridge's "working knowledge only"):**
- **Snowflake** — cloud-native data warehouse for **OLAP** (analytics over big data), vs Postgres **OLTP** (app transactions). Headline architecture: **storage separated from compute** — data in one storage layer, compute in independent **virtual warehouses** you can size up for a heavy job and auto-suspend when idle (pay only for compute used); multiple teams query the same data without contention. Columnar storage. **Standard SQL** — so my SQL transfers directly.
- **Integration from Python** — official `snowflake-connector-python` + a SQLAlchemy dialect; from FastAPI I'd query it like any SQL source behind a clean data-access layer, map to Pydantic, cache hot reads in Redis.
- **Databricks** — Spark-based lakehouse (data lake + warehouse), notebooks, MLflow; for large-scale data/ML pipelines.

**My honest line (Ibridge-calibrated):** "My hands-on warehouse depth is PostgreSQL. I understand Snowflake's model — separated storage/compute, virtual warehouses, columnar OLAP — and since it's standard SQL with a Python connector, I can support integrations and read/understand queries day one, and ramp quickly. I won't bluff deep Snowflake tuning." Honesty here protects credibility on everything else.

---

## 2.8 Cloud breadth — AWS (ECS/Lambda/Step Functions/Kinesis), Azure OpenAI, GCP {#section-2-cloud-breadth}

**Who asks:** ValueLabs (ECS Fargate, API Gateway, Lambda, Step Functions, Kinesis), RightFit (EC2/Lambda/ECS/EKS/S3/RDS/API Gateway/CloudWatch/IAM), Fornax (Azure OpenAI), Gainwell/Huzzle/Sezzle (AWS/Azure/GCP), Codvo (cloud basics).

**The gap:** hands-on AWS = AppSync/AppFlow/IAM (Abjayon). Not ECS/Lambda/Step Functions/Kinesis; not Azure OpenAI hands-on.

**Deep dive (the services I'd be asked about):**
- **Compute** — **EC2** (VMs), **Lambda** (serverless functions, event-driven, pay-per-invocation, cold starts), **ECS/Fargate** (run containers without managing servers), **EKS** (managed Kubernetes). Map to what I know: I've containerised with Docker and know K8s concepts, so ECS/EKS is deploying what I already build.
- **Orchestration** — **Step Functions** (state-machine workflow of Lambdas — conceptually the same as my LangGraph/agent state machines and NFTRACE's lifecycle states).
- **Streaming** — **Kinesis / Kafka** (ingest high-volume event streams). This ties to [[section-2-streaming]] and is a genuine gap.
- **Storage/DB** — **S3** (object storage — the "store the asset, keep metadata in Postgres" pattern I described for the ad-generation design), **RDS** (managed Postgres — I know Postgres).
- **API Gateway / CloudWatch / IAM** — gateway (auth, rate-limit, routing — I've built the same as FastAPI middleware), CloudWatch (logs/metrics/alarms — maps to my structured-logging + RED-metrics knowledge), IAM (I've managed IAM roles at Abjayon — real).
- **Azure OpenAI** (Fornax) — same OpenAI models behind Azure's endpoint/keys/deployment names + enterprise compliance; my Anthropic/OpenAI/Gemini integration experience transfers directly — it's a different endpoint, same call pattern.

**My honest line:** "Hands-on AWS: AppSync, AppFlow, IAM. The rest — ECS/Lambda/Step Functions/S3/API Gateway — I understand as the managed versions of patterns I've already built (containers, state machines, object storage, gateways), so I ramp fast, but I'll be straight that I haven't run them in production."

---

## 2.9 Streaming (LLM token streaming + data streaming) {#section-2-streaming}

**Who asks:** Fornax ("streaming"), Codvo ("streaming"), ValueLabs/others (Kinesis-style data streaming).

**The gap:** EMS explicitly notes "no streaming — responses buffered." I haven't shipped token streaming or a data-streaming pipeline.

**Deep dive:**
- **LLM token streaming** — instead of waiting for the full completion, stream tokens as generated (SSE / Server-Sent Events or WebSockets) so the user sees output immediately (better perceived latency). Providers expose `stream=True`; FastAPI serves it via `StreamingResponse` / an async generator yielding chunks. This is a bounded add to services I already own — my endpoints are async, I'd swap the buffered call for a streamed generator.
- **Data streaming** — Kafka/Kinesis for high-throughput event pipelines (producers → topic/stream → consumers), vs my batch/request-response experience. Concepts: partitions, consumer groups, at-least-once delivery, backpressure.

**My honest line:** "Token streaming is a small upgrade to my async FastAPI endpoints — I'd use `StreamingResponse` with the provider's stream mode. Large-scale data streaming (Kafka/Kinesis) I understand conceptually but haven't run."

---

## 2.10 Django (JDs that want Django, I use FastAPI) {#section-2-django}

**Who asks:** ValueLabs (Django backend + Django test framework), NextGenPros (FastAPI/Django/Flask).

**The gap:** I'm FastAPI/Flask-adjacent, not Django.

**Merge-priority framing (resume tech ≠ JD tech):** I don't pretend Django experience. I map it: Django is batteries-included (ORM, admin, auth, migrations, template engine) and synchronous-first (WSGI, async bolted on); FastAPI is async-native, lighter, API-focused. Django's **ORM ≈ SQLAlchemy** (I know SQLAlchemy well), Django **migrations ≈ Alembic** (I use Alembic), Django **REST Framework serializers ≈ Pydantic** (I know Pydantic deeply), Django **test framework ≈ pytest + TestClient** (I know pytest). So every Django concept has a direct analogue in my stack — the transfer is syntax + conventions, not concepts. For a Django role I'd be productive in days, not months, and I'd say exactly that.

**Follow-up:** *"Why FastAPI over Django in your projects?"* — pure API services with async I/O and LLM calls; I didn't need the admin/template/ORM weight, and I wanted async-native concurrency. For a CRUD-heavy app with an admin panel, Django is the right tool — I'd pick it there.

---

## 2.11 MLOps / LLMOps tooling (MLflow, model monitoring, governance) {#section-2-mlops}

**Who asks:** Gainwell (MLOps + LLMOps, continuous monitoring, guardrails, Responsible AI), Trinamix (LLMOps, AI governance), Huzzle (MLOps tools, AI monitoring), TCS (AI governance, Responsible AI).

**The gap:** I have the *discipline* (evaluation, regression gating, drift monitoring) but not the named tooling (MLflow, dedicated model-monitoring platforms).

**Deep dive + strong bridge:**
- **What LLMOps covers** — versioning prompts/models, evaluation, monitoring quality/cost/latency in production, drift detection, guardrails, governance/audit.
- **What I've actually built that IS LLMOps** — this is my strongest "gap that isn't really a gap": my **Prompt Regression Suite** is a CI/CD quality gate with baseline governance, drift monitoring (weekly full-suite run catches silent provider model updates), and audit trails (baseline resets require a documented reason). My **LLM Eval Framework** does continuous evaluation with threshold alerts. My **Bias Auditor** produces regulatory (EU AI Act Article 13) documentation and guardrail recommendations. That's evaluation, monitoring, drift detection, governance, and Responsible AI — the substance of LLMOps.
- **What I lack** — **MLflow** specifically (experiment tracking / model registry) and packaged monitoring platforms (Arize, LangSmith, WhyLabs). MLflow's model registry / experiment tracking is conceptually simple; I'd pick it up fast because I've built the harder custom equivalents.

**My honest line:** "I've built LLMOps from first principles — eval, regression gating, drift monitoring, audit trails, bias/guardrail reporting. I haven't used MLflow or a commercial monitoring platform, but I've implemented what they do, so adopting the tooling is a shortcut, not a new skill."

---

## 2.12 Knowledge graphs, ontology modeling, Graph databases {#section-2-knowledge-graphs}

**Who asks:** Codvo (ontology modeling, Graph-RAG, multi-tenant ontology-driven knowledge layers), Gainwell (graph databases).

**The gap:** no graph DB / ontology work.

**Deep dive:**
- **Graph DB** (Neo4j, etc.) — data as nodes + relationships + properties; query traversals with Cypher. Strength: relationship-heavy queries ("find all X connected to Y within 3 hops") that would be painful multi-join SQL.
- **Ontology** — a formal schema of entity types and the relations allowed between them (a domain model). Drives structured, consistent knowledge layers.
- **Graph-RAG** — retrieve by traversing the graph (or graph + vectors) for multi-hop reasoning across documents — see [[section-2-advanced-retrieval]].
- **My bridge** — I've designed relational schemas with junction tables (many-to-many is a hand-drawn graph edge) and multi-agent LO junction tables at Brane. The mental model of entities + relationships transfers; the tooling (Cypher, Neo4j) is new.

**Honest line:** genuine gap in tooling; I understand the "why" (relationship/multi-hop queries) and have the data-modeling foundation.

---

## 2.13 OAuth2 / OIDC / SSO depth {#section-2-oauth-oidc}

**Who asks:** Ibridge (OAuth), RightFit (OAuth2/JWT).

**Partial gap:** I've *built* JWT + attribute-level RBAC (strong — [[section-1]] 1.15). OAuth2/OIDC/SSO I can explain thoroughly but have implemented less.

**Deep dive:** OAuth2 = delegated authorization (the app acts on the user's behalf without their password). Roles: resource owner (user), client (app), authorization server (Google), resource server (API). **Authorization-code flow** (web apps): redirect to auth server → user consents → get a `code` → exchange server-side for an access token (+ refresh token). **OIDC** = a thin identity layer on OAuth2 adding an **ID token** (a JWT with `sub`, email, etc.) so you know *who* the user is, not just what they can access. **SSO** builds on this — one identity provider, many apps. My JWT/RBAC implementation experience covers the token-verification and authorization half solidly; the full OAuth2 dance I've read more than built.

---

## 2.14 Golang, R / R Shiny, Hugging Face training {#section-2-misc-langs}

**Who asks:** Sezzle (Golang "a plus"), Siemens (R / R Shiny "bonus"/"advantage"), Huzzle (Hugging Face).

**These are explicitly optional** ("a plus", "bonus") in their JDs, so I don't over-invest, but I stay honest:
- **Golang** — I don't write Go; I understand it's used for high-performance concurrent services (goroutines/channels). I'm willing to learn (Sezzle literally says "or willingness to learn").
- **R / R Shiny** — statistical language + its dashboard framework; I do the equivalent analytics in Python/Streamlit. Direct conceptual analogue, different syntax.
- **Hugging Face Transformers** — I use `sentence-transformers` (part of the HF ecosystem) for embeddings and a DistilBERT model in the bias auditor, but I haven't used HF for *training/fine-tuning*. So partial — I consume HF models, don't train them ([[section-2-ml-fundamentals]]).

---

## 2.15 Domain compliance — HIPAA / healthcare / fintech {#section-2-domain}

**Who asks:** Gainwell (healthcare, HIPAA/CMS), RightFit (healthcare/insurance/fintech, HIPAA), NextGenPros (healthcare/banking data), Sezzle (fintech).

**Partial:** I haven't worked in HIPAA/healthcare or fintech, **but** I have real regulated/compliance experience that transfers: my **Bias & Fairness Auditor** is built around the **EU AI Act (Articles 9 & 13)**, EEOC, and RBI AI-governance guidelines — bias testing, audit documentation, guardrails, PII-awareness (the blind judge strips demographic labels). Plus telecom carrier-grade delivery discipline at Nokia. So I understand "build to a regulatory standard, produce audit evidence, handle sensitive-data carefully" — I'd map that muscle to HIPAA (PHI handling, minimum-necessary access, audit trails) quickly. Gainwell's role notably *excludes* PHI access ("application development only"), which fits me well.

---

## 2.16 Fine-tuning specifically (retrievers, small LLMs) {#section-2-finetuning}

Covered in depth under [[section-2-ml-fundamentals]]. Short version for the JDs that call it out (Codvo, Gainwell, NextGenPros, Sezzle): I haven't fine-tuned. I know the spectrum (full FT → LoRA/PEFT → instruction tuning) and, critically, **when not to** — prefer prompting + RAG first; fine-tune only for a stubborn behaviour/format/domain with good labelled data. My default is to reach for RAG (which I've shipped) before fine-tuning (which I haven't) — and that's usually the correct engineering call anyway.

---

# SECTION 3 — PROJECT EXPLANATIONS FOR THE INTERVIEWER

*Each project as a discussion, not a Q&A dump — the way I'd actually walk you through it: the problem, the architecture, the decisions I'd defend, and what I'd change. Ordered roughly by how impressive/relevant they are for an AI-engineer/Python-backend role.*

---

## 3.1 Brane AI Agent Runtime — production agentic AI + gRPC + RBAC {#section-3-brane}

Let me start with the most recent and most relevant one. At Brane I contributed to the **production AI-agent runtime that powers a no-code platform** — this is real agentic AI in production, not a side project.

I worked across five surfaces. On the **database side**, I designed PostgreSQL schema components for the agent system: agent identity tables, multi-agent LO junction tables (that's a many-to-many between agents and the logical objects they operate on), attribute-level RBAC permission rows, and the execution sibling tables that track a run — `lo_input_execution_agent`, `agent_run_scratch`, and `agent_episodes`. Those last two are effectively a hand-rolled checkpointer — the agent's working state and its episodic history persisted so a run is durable and inspectable.

On the **inferencing side**, I integrated the LLM layer through a **gRPC model gateway**. This is the part I'm proudest of technically — it does multi-provider model routing across instruct, thinking, and vision model variants, and it's stateless so it scales horizontally. gRPC because it's internal service-to-service: binary protobuf over HTTP/2, strongly typed, low overhead — exactly where you don't want REST/JSON cost.

On the **agent loop itself**, I engineered the prompt assembly — the system prompt, grounded input injection (so the agent is anchored to real data, not free-associating), the tool-registry context that tells the agent what it can call, and a **retry-with-feedback construction for a verifier correction loop**. That verifier loop is the interesting bit: when the agent's output fails validation, instead of just failing, it feeds the failure back and retries — a self-healing pattern. In LangGraph terms that's a conditional edge looping back to the generation node; I built it by hand.

Then **performance and hardening** — I added attribute-RBAC caching (so permission checks don't hit the DB every time), cut tool-invocation overhead, and hardened the response parser for malformed LLM output, which is constant reality — models return not-quite-JSON often enough that you need defensive parsing.

If you ask what I'd flag honestly: this was a *single*-agent loop, so I don't claim multi-agent orchestration from it — but every primitive multi-agent needs (tool-calling, a critic/verifier, state persistence, per-role prompt assembly) I've built. And the RBAC work is genuine attribute-level authorization, which is rarer and harder than role-level.

Why it matters for these roles: it hits agentic AI, gRPC, PostgreSQL schema design, prompt engineering, RBAC, and production hardening — the exact intersection Fornax, Codvo, Trinamix, Sezzle, and RightFit are hiring for.

---

## 3.2 5G Failure Detection & Remediation Pipeline — production RAG {#section-3-5g-pipeline}

This is my flagship RAG project, and it solved a real operational problem. In 5G operations, when something fails, the evidence is buried in pcap files — binary packet captures with every message on the network. An engineer used to open Wireshark, scroll thousands of packets, match what they saw against their mental model of known failures, and guess a fix. Hours per incident, dependent on individual expertise, no institutional memory.

I built a pipeline that automates it end to end. **Stage one**, Pyshark extracts the error packets — I apply a display filter so I'm only pulling NAS/NGAP/Diameter/SIP error packets, then parse each into a structured record: error text, vendor, network layer, severity, timestamp. **Stage two**, that error text gets embedded and I do a **filtered semantic search in Qdrant** against a knowledge base of ~200 curated known error patterns. **Stage three**, LangChain's RetrievalQA feeds the matched patterns to Claude, which synthesises a specific, contextual fix — and I return the source documents alongside it. The result: 70% auto-resolution of routine errors, 55% MTTR reduction, log analysis from hours to seconds, adopted by ops and cited in three internal audits.

The decision I most want to defend is **Qdrant over FAISS**. The hard requirement was vendor- and layer-specific retrieval — a Nokia error must *never* match an Ericsson pattern, because the fix is vendor-specific (different CLI, different parameter names; an Ericsson fix on a Nokia node is useless or dangerous). FAISS has no native metadata filtering — you retrieve on pure similarity and filter in Python afterward, so cross-vendor patterns are still in the ranking and can crowd out the right answer. Qdrant's `must` filter runs *at the database level* before similarity ranking, so only Nokia-NAS vectors are even considered. Faster and correct-by-construction.

A few other decisions I like talking about. **Cosine similarity** because it's magnitude-invariant — a terse "T3560 timeout" and a verbose description of the same error point the same direction. **Temperature 0.1** on Claude because a fix must be consistent — same pcap twice, same fix; I don't want creative variation in operational advice. **A 0.65 score threshold** below which I return "unknown — manual review" rather than hallucinating a fix from a bad match, and I log those unknowns so the ops team can add new patterns — the system improves with use. And **model routing** — a simple threshold function sends high-confidence, non-critical matches to Haiku (fast, cheap) and ambiguous or critical ones to Sonnet (deep reasoning), which cut cost ~60% with no accuracy loss on hard cases.

`return_source_documents=True` is a trust decision, not a technical one — an ops engineer is about to restart a service based on this, so they need to see *why* the system suggested it ("based on pattern AUTH_TIMEOUT_T3560, matched at 0.94"), not a black box.

What I'd change with more time: async FastAPI + a Celery queue to handle 1000 pcaps/day, and Qdrant horizontal sharding as the collection grows.

---

## 3.3 LLM Evaluation Framework — the eval discipline these roles want {#section-3-llm-eval}

This one directly answers the "hallucination detection / LLM evaluation / prompt evaluation" line that shows up in half the job descriptions. The problem it solves is *silent degradation*: a prompt that scores 92% today quietly drops to 61% next week after a provider ships a model update with no changelog — same endpoint, same price, worse output — and you find out through support tickets days later.

It's a quality gate that runs *before* failures reach users. You POST a prompt/response test case to a FastAPI endpoint; it records it and immediately returns (202-style), then a **Celery worker** picks it up, calls the target LLM, and runs four independent evaluators. The results land in PostgreSQL and show on a Streamlit dashboard, and if any score drops below threshold a Slack alert fires. In a simulated test, a 14-point faithfulness drop from a provider update was flagged in under 4 minutes versus an estimated 2–3 days of manual review.

The four evaluators are the substance. **LLM-as-Judge** — a five-dimension rubric (accuracy, relevance, completeness, clarity, safety), scored 1–5, normalised to 0–1. **Hallucination detector** — decompose the response into atomic claims, classify each against a reference as SUPPORTED / UNSUPPORTED / CONTRADICTED, score = 1 − hallucination rate. **Faithfulness scorer** — the RAG-specific one, and the distinction I always lead with: faithfulness is *not* accuracy. It measures whether the answer stayed inside the retrieved context, regardless of whether the context was right. So high faithfulness + wrong answer means your retriever fed bad docs; low faithfulness means the model is ignoring the retriever and leaning on parametric memory — context leakage. That single distinction is a precise RAG diagnostic. And **consistency** — re-run the same prompt five times at temperature 0.7 and take the mean pairwise cosine similarity, to catch prompts that are right once and unreliable on average.

The engineering decisions I'd defend: **Celery over BackgroundTasks** because a CI-gate evaluation that's silently lost on a server restart would pass a PR that should've been blocked — durability is non-negotiable there. **Async-first** (FastAPI + SQLAlchemy async + asyncpg) so the API stays responsive while evals run 5–30 seconds. A **registry/factory pattern** for evaluators and LLM clients so adding one is writing a class + a registry line, no changes to the worker. A **local-model fallback** (swap the judge LLM for a local NLI cross-encoder) so cost is a deployment config, not a code change. And **AND logic for pass/fail** — not a weighted average — because a response that's 95% faithful but contains one hallucinated claim should still fail; a gate, not a summary.

---

## 3.4 Prompt Regression Suite — "pytest for prompts" / LLMOps {#section-3-prompt-regression}

This is the sibling to the eval framework and my answer to "prompt regression testing" and, honestly, most of what LLMOps means. The idea: treat prompts as first-class software artifacts. Every prompt file gets a behavioral test suite in a version-controlled YAML, every PR that touches a prompt runs those tests, and if quality drops below a stored baseline the PR is blocked — the same rigor as unit tests, but for *meaning* instead of logic.

The centerpiece is the **tiered assertion engine**, which is really a cost-engineering decision. Tier 0 is deterministic rules (contains-keyword, max-words, valid-JSON, regex — zero API cost). Tier 1 is local semantic similarity via a sentence-transformer (5ms, zero API cost). Tier 2 is the paid LLM-as-judge, and it *only fires if tiers 0 and 1 pass*. So a test that fails a cheap keyword check costs exactly zero in API budget — that fail-fast ordering gives ~50% cost reduction across a mixed suite.

Three decisions I especially like. **Delta-based regression** — I don't use a fixed absolute threshold; regression fires when the score drops more than 0.05 *below the stored baseline*. Fixed thresholds break as prompts improve; delta lets baselines ratchet upward on merge to main while still catching drops. **Client-side score recomputation** — I discard the judge's self-reported overall and recompute the weighted score myself, because LLM arithmetic is unreliable (it'll report 0.82 when the weights say 0.71). **Anti-self-bias routing** — the judge is always a different provider than the model under test, enforced structurally at construction, because a model grading its own output style is biased toward its own patterns.

And it's a real CI system: a PR workflow that uses a git-diff + a reverse index to run only the *affected* test cases (a PR touching 3 of 80 prompts runs ~12 tests, not 80), plus a **weekly full-suite drift monitor** — because model drift doesn't arrive in a PR, it arrives silently through the API when a provider updates their base model, so you need a scheduled run against the live model to catch it. Baseline resets require a documented reason stored with the commit SHA — an audit trail so teams can't silently paper over regressions.

When Gainwell/Trinamix ask about LLMOps and governance, this is what I point to — I built the substance from first principles.

---

## 3.5 LLM Bias & Fairness Auditor — statistics + regulatory compliance {#section-3-bias-auditor}

This one shows a different muscle: statistical rigor and regulatory compliance. It tests whether an LLM treats people of different demographics equally on the same task. The technique is **counterfactual fairness testing** — take a prompt with a placeholder like `{{candidate_name}}`, swap in every name in a demographic matrix (Arjun Sharma, Priya Sharma, James Williams…), run each variant multiple times, hold everything else identical, so any difference in output can only come from the demographic signal. It's A/B testing for fairness.

I analyze each batch through four independent lenses. **Sentiment** (VADER, with a DistilBERT transformer fallback when scores cluster ambiguously neutral) — is the tone warmer for some groups? **Semantic similarity** (sentence-embeddings) — is the *content* substantively different, not just the tone? **Structural quality** (word count, specificity, completeness heuristics) — does it write more detailed answers for some groups? And a **blind LLM judge** — a second model reads response pairs with all demographic labels stripped, so it can't import its own biases. Each lens gives a 0–100 score, combined into a weighted composite with a four-band verdict (Pass / Review / Concern / Fail).

The part I most want to highlight is the **real statistics**: one-way ANOVA to test whether group means differ significantly (p<0.05), and Cohen's d for effect size — the practical magnitude, not just statistical significance. That's genuine statistical inference, which matters when interviewers probe the "model evaluation / statistics" line (Sezzle especially). And the output is **regulatory** — it generates a PDF audit report structured for **EU AI Act Article 13** (the transparency requirement for high-risk AI in hiring/lending), with a methodology section, per-dimension statistical breakdown, and remediation recommendations. So it's the bridge to any compliance/governance question ([[section-2-domain]]).

Design decisions: a single `BiasReport` Pydantic model as the universal contract across CLI/API/dashboard/PDF (change a field once, it propagates everywhere, type-checked); async-first with a semaphore cap because a 100-variant × 5-run audit is 500 concurrent calls that would blow the rate limit unthrottled; and the blind judge as a structural anti-bias measure.

---

## 3.6 NFTRACE — distributed systems + FastAPI + the "why each tech" story {#section-3-nftrace}

NFTRACE is my strongest pure-backend/distributed-systems story, and it's good because every technology choice has a defensible reason. The problem: validating 5G network-function behavior in CI/CD meant manually starting traces on distributed nodes (gNBs, AMFs, UPFs), waiting, stopping, collecting and merging trace files, and validating protocol behavior by hand — hours per scenario, non-repeatable, blocking automated CI.

I built it as a distributed REST platform with three layers. **Server**: a FastAPI REST API managing the trace lifecycle — start/stop/merge/validate endpoints. **Session state**: Redis. **Persistence**: SQLite. **Node communication**: XML-RPC via multiprocessing. A test worker makes four clean REST calls and gets a structured validation report; it took pipeline validation time down 50%.

The tech-choice reasoning is the whole point. **FastAPI over Flask/Django** — Pydantic validation on every request (matters when multiple workers hit it concurrently), auto OpenAPI docs so engineers self-serve, ASGI concurrency. **Redis for session state, not SQLite** — because active sessions change state rapidly (STARTING→ACTIVE→STOPPED) and need sub-millisecond concurrent-safe access, plus a TTL so a crashed worker's orphaned session auto-expires; SQLite's write serialization would bottleneck under 20 concurrent workers. But **SQLite for history, not Redis** — completed sessions need to survive restarts and are queried infrequently; the two-layer split gives each access pattern the right tool. **SQLite over Postgres** — single-server internal tool, sequential writes, no DBA; adding Postgres would be infrastructure with no benefit (and I can say exactly when I'd migrate: multi-server, failover, hundreds of concurrent writes). **XML-RPC** wasn't a choice — the telecom nodes expose it, it's a legacy industry standard; the *design* decision was abstracting it behind the REST API so workers never touch it, and only the NodeManager changes if the industry moves to gRPC. **Multiprocessing over asyncio** for node ops because traces must start on all nodes *simultaneously* (start sequentially and you miss the opening messages on later nodes), and `xmlrpc.client` is synchronous — `multiprocessing.Pool.starmap` gives true parallelism without an async-XML-RPC dependency.

The bit that earned onsite recognition was integrating it into **Nokia Continuous Delivery** — pre/post-test hooks that auto-start a trace for tagged tests and feed validation back into the pipeline. The payoff: a test could *pass* its assertions but *fail* trace validation, meaning the network behavior was wrong even though the app-level test was green — a class of bug that was invisible before.

What I'd change: async node ops to scale past ~10 concurrent sessions, and real-time streaming validation to abort a test mid-run on a critical protocol violation.

---

## 3.7 RF Keyword Generator — the hybrid LLM/deterministic pattern {#section-3-rf-generator}

This is a small tool with a big lesson: **when to use an LLM and when not to.** Testers needed to write Robot Framework keywords for 5G procedures — repetitive, boilerplate-heavy work. They type a plain-English description ("Register a UE with IMSI … on AMF"), pick a procedure from a dropdown, and get back a ready-to-use, syntactically-valid `.robot` file in under two seconds. It hit 50+ generations a week organically.

The architecture is a four-stage pipeline, and the design insight is the **split of responsibility**: the LLM handles only what's genuinely variable and unpredictable — extracting entities from natural language (Claude Haiku, because extraction is structured and needs no reasoning, so I use the cheap fast model). Everything structured is *deterministic*: procedure detection by keyword match, template filling from pre-built RF templates, and — critically — **validation through Robot Framework's own parser** (`robot.api.get_model()`) before anything is returned. The tester can never receive a broken file.

That hybrid is the whole point, and it's what I'd stress in an interview: an LLM generating RF syntax from scratch produces subtle breakage (wrong indentation, `Return` vs `RETURN`, unclosed `${}`); templates are correct by construction and free. So the LLM does understanding, templates do structure. And there's a **regex fallback** on the extraction step — if the LLM returns bad JSON, regex handles it, which is why the tool claims 100% uptime: the LLM is an enhancement, not a dependency.

There's a defense I've rehearsed because it's the obvious challenge — *"why not just use Claude.ai in a browser?"* The honest answer: for a one-off keyword, you could. The value is everything around the LLM. Claude.ai doesn't know our internal `5GCoreLibrary` names or the `/namf-comm/v1/ue-contexts` endpoints, so its output needs manual fixup; my tool uses the team's actual conventions so it works first try. It validates syntax before output. It enforces deterministic, consistent naming so the test suite doesn't fragment. It removes the prompt-engineering burden — testers type one sentence, not a paragraph of instructions. And it logs every generation for audit. The strongest version: Claude.ai was free and available to every tester, and the tool still won 50+ weekly generations on merit — revealed preference is the best evaluation.

---

## 3.8 AI Employee Management System (EMS 2.0) — local LLM + multi-DB RAG {#section-3-ems}

EMS is my "many concepts in one system" project, and it's a good chat-driven RAG story. Instead of forms, you talk to it: upload a PDF or image resume and it auto-extracts 22+ structured fields; then everything is natural language — "show me employees who know Python", "update John's email", "delete employee 000003". It's deliberately **privacy-first**: the LLM runs *locally* via Ollama (qwen2.5:7b-instruct), so resume data never leaves the machine.

It's a genuine multi-database architecture, each DB for what it's good at: **PostgreSQL** for structured employee records, **MongoDB GridFS** for the raw PDF/image files, and **FAISS** for vector search over employee text. The upload flow runs in a background thread so the frontend gets an instant response and polls for status: extract text (pdfplumber, with pytesseract OCR fallback for images) → validate it's actually a resume via a scoring gate → Ollama extracts JSON → **Pydantic enforces the schema** → write to Postgres → chunk and embed into FAISS.

The lessons I'd talk about are the production-reality ones. **LLM output is unreliable without guardrails** — raw JSON failed to parse 10–20% of the time, so I built multi-strategy parsing (direct → regex extraction → key-value fallback) plus Pydantic validation with retry. **Anti-hallucination guards** — five of them (ambiguous query, non-existent employee, leading questions like "confirm John has 20 years' experience" when he doesn't, pressure prompts) that route through the LLM with a special context so it responds naturally instead of fabricating. **RAG for semantic search** — "experienced DevOps engineer" finds relevant people without exact keyword matches, falling back to FAISS top-5 when no employee is named. And **model selection under hardware constraints** — qwen2.5:14b (18GB) didn't fit the 6GB RTX 3060 and fell back to CPU at 30+ seconds, so I switched to the 7b-instruct quant and got GPU utilization back with 2–5s responses.

I'm honest about its limits — it's a learning project: duplicate detection is disabled, no auth yet, in-memory sessions, single-node FAISS, no streaming. But the multi-DB consistency problem (Postgres write succeeds, FAISS indexing fails → inconsistent state) is a real distributed-systems issue I can discuss, not a toy bug.

---

## 3.9 Financial Statement Parser — privacy-first browser AI {#section-3-financial-parser}

A tight, product-minded one. It turns bank-statement PDFs and images into structured, exportable data (CSV / multi-sheet Excel / PDF report) with categorised transactions — and its defining property is that **the original file never leaves your browser.** OCR runs locally via Tesseract.js (compiled to WASM), pdf.js rasterises PDF pages to canvas, and only the *extracted text* (capped at 8k chars) goes to Google Gemini for transaction identification and categorisation. It's a **BYOK** (bring-your-own-key) model — no backend, no database, the user's Gemini key goes straight from localStorage to Google, so the app has zero hosting cost and zero data liability.

The engineering details I'd raise: **temperature 0.1** and `responseMimeType: 'application/json'` on Gemini for near-deterministic structured output; a **three-method JSON salvage** for when a big statement truncates the response (strip code fences → find outermost braces by index → find the last complete transaction and close the structure) because partial results beat a hard failure; and a neat state-machine bug I fixed in the "Add More files" flow where processing a second file reset the global status and unmounted the results — fixed with an `updateStatus=false` flag so a sub-process runs silently inside an active state. It shows I think about privacy architecture, graceful degradation, and React state, not just happy-path.

---

## 3.10 Blog / Markdown Documentation Engine — frontend/static-site depth {#section-3-blog}

The one non-AI project, and I keep it brief but it demonstrates frontend and build-time thinking. It turns a folder of Markdown into a full docs site — auto-generated sidebar, client-side search, table-of-contents scroll-spy, dark mode — with **no backend and no runtime server.** Astro compiles everything to static HTML at build time; the `dist/` folder deploys to any CDN.

The insight I'd share is Astro's **build-time vs runtime split**: anything you can do at build time, you should, because it's free at runtime. `import.meta.glob()` discovers all Markdown files at build to construct both the sidebar tree and the embedded search index; `getStaticPaths()` pre-generates every route (required for a catch-all `[...slug]` route in a static generator). The only runtime JS is small vanilla scripts — a from-scratch weighted search (title +10, heading +5, content +2), an `IntersectionObserver` scroll-spy for the TOC, and class-strategy dark mode persisted to localStorage. It's the project I point to for React/frontend-adjacent and TypeScript-tooling questions ([[section-2-typescript]]), and for "do you understand the browser platform," even though it's not where my depth is.

---

## Closing framing for any interview

The through-line across all ten: I build **production-grade AI/backend systems with engineering discipline** — evaluation, cost-awareness, failure handling, and honest scoping. My strongest, rarest cluster is **LLM evaluation + prompt regression + agentic runtime work** (Sections 3.1, 3.3, 3.4, 3.5) — most candidates have *used* an LLM API; far fewer have built the systems that keep LLM output trustworthy in production. My honest growth edges are model *training*/fine-tuning and cloud/data-platform breadth (Section 2) — and my answer there is always the same: I know the concepts, I've built the harder adjacent things, I don't bluff, and I ramp fast.
