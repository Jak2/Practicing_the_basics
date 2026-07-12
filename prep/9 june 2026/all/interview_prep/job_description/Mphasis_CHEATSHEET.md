# Mphasis / Wells Fargo — Python GenAI + FastAPI — Complete Interview Cheatsheet

> Role: Python Backend Engineer, AI-enabled apps, Commercial Lending. Primary skill: **Python GenAI with FastAPI**.
> This sheet = every topic the JD names + deep dives on the 3 primary areas + your resume projects mapped to their asks.

---

## 0. FIT SNAPSHOT — read this first

**What they want (from the JD):** Python + MongoDB backend · Agentic AI (Google ADK / LangChain / LangGraph, multi-agent) · RAG + prompt engineering + grounding + guardrails · FastAPI microservices · secure REST for React · **event-driven (Kafka/RabbitMQ/ActiveMQ)** · **MCP / FastMCP** · **complex MongoDB queries + aggregation** · NumPy/Pandas/PyMongo · cloud-native / **OpenShift** · CI/CD (GitHub Actions, Harness, JFrog, Sonar, K8s, Docker) · Pytest + MagicMock · ML/NLP + GCP Document AI · Agile · HA/scalability/resilience · multithreading/concurrency.

**Your strong hits (lead with these):** Python, FastAPI, RAG, LangChain, prompt engineering, **agentic AI (Brane runtime)**, **MCP (Brane router — real, rare)**, evaluations/guardrails (your LLM Eval framework), gRPC, Celery, asyncio, multiprocessing, MongoDB (EMS/GridFS), Pydantic, Redis, Docker, pytest+MagicMock, microservices.

**Gaps to close before the interview (priority order):**
1. **MongoDB aggregation pipeline** — you used GridFS; they want `$match/$group/$lookup`. STUDY.
2. **Event-driven / Kafka** — no resume evidence. Learn the mental model + one talking point.
3. **LangGraph / Google ADK** — you hand-rolled agents (Brane); learn the framework vocabulary.
4. **FastMCP** — you did MCP at Brane; learn the `FastMCP` library specifically.
5. **OpenShift (OCP)** — you know Docker/K8s-as-tester; learn OCP basics.
6. **Pandas/NumPy** — light in your projects; know the core ops.
7. **7 yrs vs your 5** — frame: depth + shipped production AI systems, not just tenure.

---

# PART A — PRIMARY SKILLS (deep) : PYTHON · GenAI · FastAPI

---

## A1. PYTHON (deep)

### Core language
- **Data structures:** list (ordered, mutable), tuple (immutable), dict (hash map, O(1) lookup, insertion-ordered 3.7+), set (unique, O(1) membership). Know time complexity of each op.
- **Comprehensions:** `[x for x in xs if cond]`, dict/set comps, nested. Generator expr `(x for x in xs)` = lazy, memory-cheap.
- **Generators:** `yield` — lazy iterator, holds state, streams large data without loading all. `yield from`.
- **Decorators:** function returning a wrapped function. `@wraps` to preserve metadata. Use: logging, caching (`@lru_cache`), auth, timing.
- **Context managers:** `with` + `__enter__/__exit__`, or `@contextmanager`. Guarantees cleanup (files, DB conns, locks).
- **Dunder methods:** `__init__`, `__repr__`, `__eq__`, `__hash__`, `__iter__`, `__enter__/__exit__`, `__call__`.
- **Args:** `*args`, `**kwargs`, keyword-only (`def f(*, x)`), positional-only (`def f(x, /)`).
- **Mutability trap:** default mutable args (`def f(x=[])`) — shared across calls. Use `None` default.
- **Typing:** `list[int]`, `dict[str,int]`, `Optional[X]` = `X | None`, `Union`, `Literal`, `TypedDict`, `Protocol`. Type hints don't enforce at runtime (Pydantic does).

### Concurrency & parallelism (JD explicitly asks)
| Model | Use for | Mechanism | Note |
|---|---|---|---|
| **threading** | I/O-bound | OS threads | GIL means no CPU parallelism; fine for I/O waits |
| **multiprocessing** | CPU-bound | separate processes | true parallelism, bypasses GIL, higher overhead |
| **asyncio** | high-concurrency I/O | single-thread event loop | `async/await`, best for many network calls |
- **GIL (Global Interpreter Lock):** only one thread executes Python bytecode at a time → threads don't give CPU parallelism; use multiprocessing for CPU work.
- **asyncio essentials:** `async def` (coroutine), `await`, `asyncio.gather()` (run concurrently), `asyncio.create_task()`, `asyncio.Semaphore(n)` (cap concurrency — you used this in Bias Auditor).
- **Rule of thumb:** many API/DB calls → asyncio. Heavy computation → multiprocessing. Simple background I/O → threading.

### Pydantic (v2) — you know this
- `BaseModel`, field types, validators (`@field_validator`, `@model_validator`), `model_validate_json()`, `model_dump()`. Runtime validation of untrusted input (LLM output, API bodies).

### Testing (JD: Pytest + MagicMock)
- **pytest:** test discovery (`test_*.py`), fixtures (`@pytest.fixture`, `tmp_path`), `@pytest.mark.parametrize`, markers, `assert` introspection.
- **MagicMock / unittest.mock:** `MagicMock()`, `patch("module.thing")`, `mocker` (pytest-mock), `.assert_called_once_with()`, `return_value`, `side_effect`. Mock external calls (LLM, DB, network) so tests are fast + deterministic.
- **Async tests:** `pytest-asyncio`, `@pytest.mark.asyncio`, `httpx.AsyncClient` for FastAPI.
- **You have this:** ContentPilot 39→98 tests, EMS tests use MagicMock. Talking point ready.

### NumPy / Pandas (JD asks — study, light in your projects)
- **NumPy:** `ndarray`, vectorized ops (no Python loops), broadcasting, `np.array/mean/sum/reshape`, dtype. Fast because C-backed contiguous memory.
- **Pandas:** `DataFrame`/`Series`, `read_csv`, `df.groupby().agg()`, `merge/join`, `df.loc/iloc`, filtering `df[df.x>5]`, `apply`, handling NaN. Aggregation mirrors SQL GROUP BY.

**Likely Python Qs:** GIL & when to use threads vs processes vs async · generator vs list (memory) · decorator use case · mutable default arg bug · `async def` vs `def` · how pytest fixtures work · mock an external API in a test.

---

## A2. GenAI (deep — this is the "GenAI" in the title)

### LLM fundamentals
- **Tokens** (text → tokens → embeddings), **context window** (max tokens in+out), **temperature** (0 = deterministic, high = creative), **top_p**, **max_tokens**, **system vs user vs assistant** roles.
- **Structured output:** force JSON (`response_format`/JSON mode), function/tool calling, schema-constrained. Always validate (Pydantic) — LLMs return malformed ~10-20%.

### Prompt engineering (JD: prompt engineering + grounding)
- **System prompt** = role/rules. **User prompt** = task + context.
- **Few-shot** (examples in prompt), **Chain-of-Thought** ("think step by step"), **zero-shot**.
- **Grounding** = give the model the facts to answer from (retrieved docs) so it can't rely on parametric memory → reduces hallucination. THE keyword for this JD (they say "grounding" explicitly).
- **Structured extraction:** per-field schema, retry with stricter prompt on missing fields.

### RAG (JD: RAG core requirement) — you have this
```
ingest: docs → chunk (e.g. 500/100 overlap) → embed → store in vector DB (+ metadata)
query : question → embed → (metadata filter) → semantic search top-k → inject as context → LLM answers grounded
```
- **Embeddings:** text → vector; similar meaning = close vectors. Model output dim (e.g. 1536).
- **Vector search:** cosine similarity, HNSW index (approximate NN, sub-ms). Metadata **pre-filtering** (Qdrant) vs post-filter (FAISS).
- **Chunking:** size vs meaning tradeoff; overlap prevents splitting a fact.
- **Advanced (know the words):** hybrid retrieval (BM25 + dense), cross-encoder **reranking**, query rewriting, recall@k eval.
- **RAG faithfulness vs accuracy:** faithful = answer stayed within retrieved context; accurate = actually true. Faithful-but-wrong = retrieval problem; unfaithful = context leakage.

### Agentic AI (JD: agentic frameworks + multi-agent — heavy weight)
- **Agent = LLM + tools + loop.** It plans, calls tools, observes results, loops until done (vs one-shot Q&A).
- **ReAct pattern:** Reason → Act (tool call) → Observe → repeat.
- **Tool/function calling:** model emits a structured call; your code runs it; result fed back.
- **Multi-agent:** multiple specialized agents collaborate (e.g. planner + executor + verifier). JD explicitly wants "multiple AI agents collaborate to achieve complex tasks."
- **Frameworks (learn vocabulary — you hand-rolled this at Brane):**
  - **LangGraph** — agents as a **state graph**: nodes (steps), edges (transitions), conditional edges (branching), cycles (retry/verifier loops), checkpointing (persist state), human-in-the-loop interrupts. "Graph, not chain" = supports branching + loops + shared state.
  - **Google ADK (Agent Development Kit)** — Google's framework (JD's preferred). Know: it's for building/deploying agents, multi-agent orchestration, tool integration, works with Gemini/Vertex AI. Even conceptual familiarity helps.
  - **LangChain** — chains, agents, retrievers, prompt templates (you used RetrievalQA).
- **YOUR EDGE:** you built an agent runtime by hand at Brane — agent loop, tool registry, retry-with-feedback verifier, RBAC. Say: "I built this from scratch; here's how it maps to LangGraph's state graph + conditional edges."

### Evaluations & guardrails (JD: evaluations + safety guardrails — you own this)
- **LLM-as-judge** (rubric scoring), **hallucination detection** (claim decomposition + NLI), **faithfulness**, **consistency** (multi-run). Your LLM Eval Framework = direct proof.
- **Guardrails:** input/output validation, PII redaction, refusal patterns, structured-output enforcement, human-approval gate. Critical for banking (Wells Fargo).

### MCP (JD: MCP servers/clients + FastMCP — you did MCP at Brane)
- **MCP (Model Context Protocol)** = standard "plug" to expose tools/data/prompts to LLMs. Server exposes capabilities; client (the LLM app) calls them. Primitives: **tools** (actions), **resources** (data), **prompts** (templates). Transport: stdio / HTTP.
- **FastMCP** = Python library to build MCP servers fast (decorator-based, like FastAPI for MCP). Learn: `@mcp.tool()`, `@mcp.resource()`, running a server.
- **Your Brane work:** the verb-based agent router was exposed as an MCP server (`resolve_agent` tool). Strong, rare evidence — lead with it.

**Likely GenAI Qs:** explain RAG end-to-end · how do you reduce hallucination (grounding + guardrails + faithfulness eval) · what's an agent vs a chain · design a multi-agent system for X · how does MCP work / why · fine-tune vs RAG vs prompt · how do you evaluate an LLM app.

---

## A3. FastAPI (deep — the "FastAPI" in the title)

### Core
- **App + routes:** `app = FastAPI()`, `@app.get/post/put/delete("/path")`. `APIRouter` for modular routes, `app.include_router()`.
- **Params:** path (`/items/{id}`), query (`?q=`), body (Pydantic model), headers, cookies. Auto-validated + coerced by type hints.
- **Pydantic request/response models:** `response_model=`, request body as `BaseModel`. Auto validation + OpenAPI docs.
- **Async:** `async def` endpoints for I/O (DB, LLM, HTTP). Sync `def` runs in a threadpool. **Never block the event loop** — offload CPU/blocking work (`run_in_executor`).
- **Dependency injection:** `Depends()` — reusable deps (DB session, auth user, settings). Great for testability + DRY.
- **Startup/shutdown:** `lifespan` context manager (modern) or `@app.on_event`. Init DB pools, load models, start schedulers.
- **Background tasks:** `BackgroundTasks` for fire-and-forget after response (light work). Heavy/durable → Celery/queue.
- **Errors:** `HTTPException(status_code, detail)`, custom exception handlers.
- **Middleware:** cross-cutting (logging, timing, CORS). `CORSMiddleware` for the React frontend (JD asks).

### Security (JD: secure REST APIs for React)
- **OAuth2 + JWT:** `OAuth2PasswordBearer`, token in `Authorization: Bearer`, verify + decode, dependency injects current user. **RBAC** on top (you built attribute-level RBAC at Brane — strong).
- **CORS** for browser (React) origins. **HTTPS**, input validation (Pydantic), rate limiting, secrets via env (never hardcode).

### Production concerns
- **ASGI server:** `uvicorn` (dev), `gunicorn` + uvicorn workers (prod), multiple workers for parallelism.
- **Streaming:** `StreamingResponse` (stream LLM tokens to client).
- **Files:** `UploadFile` (you used for pcap/resume upload).
- **OpenAPI:** auto `/docs` (Swagger) + `/redoc`.
- **Testing:** `TestClient` (sync) / `httpx.AsyncClient` (async) + pytest.

### Microservices / HA / resilience (JD asks)
- **Stateless services** (scale horizontally), health-check endpoints (`/health`), config via env (12-factor).
- **Resilience patterns:** retry with backoff, circuit breaker, timeouts, graceful degradation, idempotency.
- **Scaling:** load balancer + N replicas, connection pooling (DB), caching (Redis).

### FastAPI code skeleton (be able to write this)
```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

app = FastAPI()

class LoanReq(BaseModel):
    applicant_id: str
    amount: float

async def get_db():        # dependency
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/loans", response_model=LoanResp)
async def create_loan(req: LoanReq, db=Depends(get_db)):
    if req.amount <= 0:
        raise HTTPException(400, "amount must be positive")
    ...
    return result
```

**Likely FastAPI Qs:** async vs sync endpoint (event loop) · how does Depends work · how do you secure an endpoint (JWT+RBAC) · how do you handle a slow LLM call without blocking · CORS for React · how do you test a FastAPI route · lifespan vs on_event.

---

# PART B — EVERY OTHER JD TECH (study each)

## B1. MongoDB + PyMongo (JD: NoSQL primary + complex queries + aggregation — STUDY THE AGGREGATION)
- **Model:** documents (JSON/BSON) in collections. Schema-flexible. `_id` primary key.
- **CRUD:** `insert_one/many`, `find({filter})`, `update_one({filter},{$set:{}})`, `delete_one`.
- **Query operators:** `$eq $ne $gt $lt $gte $lte $in $nin $and $or $exists $regex`.
- **Aggregation pipeline (they emphasize this):** stages processed in order —
  - `$match` (filter, early = fast), `$group` (`{_id:"$field", total:{$sum:"$amt"}}`), `$project` (reshape/select fields), `$sort`, `$limit/$skip`, `$lookup` (join to another collection), `$unwind` (flatten arrays), `$addFields`.
  - Example: total loan amount per applicant → `[{$match:{status:"approved"}},{$group:{_id:"$applicant_id",total:{$sum:"$amount"}}},{$sort:{total:-1}}]`.
- **Indexes:** speed queries; compound indexes; `explain()`. Index the fields you `$match`/sort on.
- **PyMongo** (sync) / **Motor** (async, use with FastAPI). GridFS for large files (you used this in EMS).
- **Schema design:** embed (1-to-few, read together) vs reference (1-to-many, large). Denormalize for read speed.
**Likely Qs:** write an aggregation to group+sum · embed vs reference · what does $lookup do · how do indexes help · sync PyMongo vs async Motor in FastAPI.

## B2. Event-driven architecture (JD: Kafka / RabbitMQ / ActiveMQ — GAP, learn the model)
- **Why:** decouple services, async processing, buffering, scale. Producer publishes → broker → consumer(s) process independently.
- **Kafka:** distributed log. **Topics** split into **partitions** (parallelism + ordering per partition). Producers write, **consumer groups** read (each partition to one consumer in a group). **Offsets** track position. Durable, high-throughput, replayable. Use: event streaming, pipelines.
- **RabbitMQ:** traditional message queue/broker. **Exchanges** route messages to **queues** by binding/routing keys (direct/topic/fanout). Ack/nack. Use: task queues, request/reply, complex routing.
- **Kafka vs RabbitMQ:** Kafka = high-throughput event log, replayable, analytics/streaming. RabbitMQ = flexible routing, task distribution, lower latency small messages.
- **Pattern for this role:** document/data ingestion → publish event → workers process (LLM extraction) async → results to DB. (Your Celery/Redis broker experience is the transferable story — say "I've built async broker/worker pipelines with Celery+Redis; the same pattern applies with Kafka.")

## B3. MCP / FastMCP — (covered in A2; you have Brane evidence — this is a highlight, not a gap)

## B4. Testing — Pytest + MagicMock (covered in A1; you have evidence)

## B5. CI/CD + cloud-native (JD: GitHub Actions, Harness, JFrog, Sonar, OpenShift/K8s, Docker)
- **Docker:** image (`Dockerfile`), container, `docker build/run`, multi-stage builds (small images), `docker-compose` (multi-service — you did this in LLM Eval). Layers, `.dockerignore`.
- **GitHub Actions:** `.github/workflows/*.yml` — triggers (`on: push/pr`), jobs, steps, actions. Lint → test → build image → push → deploy. (You built a prompt-regression CI gate — strong CI story.)
- **Kubernetes / OpenShift:** **pod** (smallest unit), **deployment** (replicas + rollout), **service** (stable network endpoint), **ingress**, HPA (autoscale), configmap/secret. **OpenShift (OCP)** = enterprise K8s (Red Hat) + `oc` CLI, `Route` (their ingress), builds/image-streams, stricter security (SCC). Know: it's K8s with enterprise add-ons.
- **Tooling to name (know what each is):** **Harness** = CD/deployment automation platform. **JFrog Artifactory** = artifact/image registry. **SonarQube** = static code quality/security scanning. **JFrog Xray** = security scan.
- **Cloud-native (12-factor):** stateless, config in env, logs to stdout, disposable, health checks, horizontal scale.

## B6. ML / NLP + GCP (JD: Document AI, Information Retrieval, Summarization, LLMs)
- **GCP Document AI:** managed service to parse/extract structured data from documents (OCR + entity extraction) — relevant for "document-centric use cases" in lending. Know: it does form/invoice parsing, returns structured entities.
- **Information Retrieval:** search/ranking — TF-IDF/BM25 (lexical) vs embeddings (semantic) vs hybrid. Precision/recall, recall@k, MRR.
- **Summarization:** extractive (pick sentences) vs abstractive (LLM generates). Grounding matters for factual summaries.
- **NLP basics:** tokenization, embeddings, NER, classification, sentiment.

## B7. Microservices, HA, scalability, resilience (covered in A3 production section)
- HA = no single point of failure (replicas, health checks, failover). Scalability = horizontal (add instances). Resilience = retry, circuit breaker, timeout, bulkhead, graceful degradation.

## B8. Agile — sprints, standups, backlog, JIRA (you have Nokia Agile experience).

## B9. Banking/Lending domain (good-to-have) — commercial lending: loan origination, underwriting, risk, KYC/compliance, document processing (statements, applications). AI use: document extraction, risk analysis, summarization. Show awareness.

---

# PART C — YOUR RESUME PROJECTS → THEIR REQUIREMENTS (talking points)

Route every answer back to one of these. Left = their ask, right = your proof.

| JD requirement | Your proof (say this) |
|---|---|
| **Agentic AI / multi-agent** | **Brane AI-agent runtime** — agent loop, tool registry, verifier correction loop, multi-agent LOs (primary + verifier), RBAC. "I built a production agent runtime from scratch." |
| **MCP / FastMCP** | **Brane verb-based router exposed as an MCP server** (`resolve_agent`). Rare real MCP evidence. |
| **RAG + grounding** | **5G failure-detection pipeline** (Qdrant filtered retrieval → grounded Claude fix) + **EMS** (FAISS RAG over resumes). |
| **Prompt engineering** | Brane prompt assembly (system + grounded inputs + tool context + retry-with-feedback); RF-gen structured extraction. |
| **Evaluations + guardrails** | **LLM Evaluation Framework** (LLM-judge, hallucination, faithfulness) + **Prompt Regression Suite** (CI gate) + **Bias Auditor** (safety). Directly = "evaluations and safety guardrails." |
| **FastAPI microservices** | NFTRACE (distributed FastAPI REST), LLM Eval, 5G pipeline, RF-gen — all FastAPI. |
| **Secure REST + RBAC** | Brane attribute-level RBAC; FastAPI + JWT pattern. |
| **MongoDB** | EMS — MongoDB GridFS for documents (polyglot: Postgres + Mongo + FAISS). *(Study aggregation to strengthen.)* |
| **Async / concurrency / multithreading** | LLM Eval (Celery/Redis async), Bias Auditor (asyncio.Semaphore), NFTRACE (multiprocessing), EMS (daemon threads). Strong. |
| **Event-driven async processing** | Celery+Redis broker/worker in LLM Eval = the same decoupled-async pattern as Kafka. *(Bridge honestly.)* |
| **CI/CD** | Prompt Regression Suite = GitHub Actions gate; LLM Eval = Docker Compose. Nokia NCD/TAF CD. |
| **Testing (Pytest+MagicMock)** | ContentPilot 98 tests TDD; EMS uses MagicMock; 3-tier telecom testing. |
| **Document-centric / IR / summarization** | Financial Statement Parser (OCR→extract→structure), 5G pcap parsing, RAG retrieval. |
| **Microservices HA/resilience** | gRPC model gateway (stateless horizontal scale), graceful degradation (regex fallback, per-source isolation). |
| **Banking/lending fit** | Financial Statement Parser (bank statements), Bias Auditor (lending-fairness / EU AI Act) — you've touched financial + regulated AI. |

---

# PART D — GAP-CLOSING STUDY ORDER (before the interview)

1. **MongoDB aggregation pipeline** — practice 5 queries ($match/$group/$lookup/$project). Highest-value gap. (2h)
2. **LangGraph** — build one tiny StateGraph with a conditional edge + loop; map it to your Brane loop. (2h)
3. **FastMCP** — write one `@mcp.tool()` server; connect it. Turns Brane MCP into demonstrable. (1h)
4. **Kafka mental model** — topics/partitions/consumer-groups/offsets; the Celery→Kafka bridge sentence. (1h)
5. **OpenShift basics** — pod/deployment/service/Route/`oc`; "it's enterprise K8s." (1h)
6. **Google ADK** — read the docs, know what it is + one example. (1h)
7. **Pandas/NumPy** — groupby/agg, merge, vectorized ops. (1h)
8. **Rehearse the landmine answers** — 7yrs-vs-5 (depth + shipped production AI), "how did you measure X", "proposed not built" for scale claims.

---

# PART E — LIKELY INTERVIEW QUESTIONS (rapid-fire prep)

**Python:** GIL? threads vs processes vs async? generator vs list? decorator example? async def vs def? mock an API in pytest?
**FastAPI:** async endpoint + event loop? Depends()? secure with JWT+RBAC? slow LLM call without blocking? test a route? CORS for React?
**GenAI:** RAG end-to-end? reduce hallucination? agent vs chain? design a multi-agent doc-processing system? MCP — what/why? evaluate an LLM app? prompt engineering for grounding?
**MongoDB:** aggregation to group+sum per applicant? embed vs reference? $lookup? index strategy? Motor vs PyMongo?
**Architecture:** event-driven ingestion design? HA + resilience patterns? stateless scaling? Kafka vs RabbitMQ?
**Behavioral:** hardest bug? mentoring (you mentored 3 engineers)? disagreement with a design? working with US/onshore partners?

---

# PART F — PER-PROJECT CONCEPTS & TECHNIQUES CHEATSHEET (every resume project)

Every concept, technique, and library in each resume project — work experience first, then key projects. Study the row; if you can't explain a term, that's a gap. ★ = highest-value talking point for this JD.

## WORK EXPERIENCE

### Brane Enterprises — AI Agent Runtime ★★★ (your best fit for this role)
`agentic AI` · `agent loop / correction loop` · `verifier lane (deterministic → AI → human)` · ★`MCP server + verb-based routing` · `tool invocation (pre-registered NFs, grant-checked, JSON-schema validated)` · `retry-with-feedback prompt assembly` · `system prompt + grounded input injection + tool-registry context` · ★`attribute-level RBAC` (+ caching) · `gRPC model gateway` · `multi-provider routing (instruct/thinking/vision)` · `stateless horizontal scaling` · `PostgreSQL schema design` (identity, junction, sibling tables, partial unique index) · `three memory layers (scratch/episodic/distilled-RAG)` · `response parser hardening (malformed LLM JSON)` · `in-place attempt_seq audit` · `mirror-to-canonical` · `probabilistic core / deterministic gate` (the principle).
*Maps to JD: agentic + multi-agent, MCP/FastMCP, prompt engineering, guardrails, RBAC/secure, gRPC, microservices, Postgres.*

### Infinite/Nokia — 5G Failure-Detection Pipeline ★★ (RAG + document-centric)
`Pyshark pcap parsing` · `protocol-layer detection (NAS/NGAP/RRC/Diameter/SIP/GTP)` · ★`RAG` · `embeddings (ada-002, 1536-dim)` · `Qdrant vector DB (HNSW, cosine)` · ★`metadata pre-filtering (vendor/layer)` · `LangChain RetrievalQA + PromptTemplate` · `grounding` · `confidence-based model routing (Haiku/Sonnet)` · `score-threshold hallucination guard` · `self-improving KB (unknown-errors)` · `temperature=0.1 determinism` · `FastAPI UploadFile` · `Streamlit`.
*Maps to JD: RAG, grounding, prompt engineering, information retrieval, FastAPI, document-centric.*

### Nokia — NFTRACE (distributed microservice)
`FastAPI lifecycle REST` · `Redis session isolation (setex TTL)` · `two-tier hot/cold storage (Redis/SQLite)` · `XML-RPC legacy integration behind REST facade` · `multiprocessing.Pool fan-out` · `SIP/Diameter rule-engine validation` · `client SDK → Robot Framework` · `NCD/TAF CI/CD hooks` · `graceful degradation` · `3-tier testing (unit/integration/e2e)`.
*Maps to JD: microservices, FastAPI, concurrency/multithreading, HA/resilience, REST, CI/CD.*

### Nokia — RF Keyword Generator (hybrid LLM)
`hybrid regex + LLM extraction` · `Claude Haiku structured JSON` · `per-procedure schemas` · `regex fallback (100% uptime)` · `deterministic templates` · `real RF parser as validator` · `right-sized model selection` · `Streamlit/FastAPI split`.
*Maps to JD: prompt engineering, structured output, resilience, testing.*

### Nokia — 5G Core testing / mentoring
`5G Core (AMF/AUSF/gNB/UPF)` · `Diameter/SIP signaling validation` · `Kubernetes pod health (as tester)` · `Robot Framework` · `Agile sprints` · `code-review checklists (thread safety, Docker)` · `mentored 3 engineers`.
*Maps to JD: Agile, K8s, mentoring, concurrency.*

### Abjayon — Node.js / AWS
`Node.js backend` · `AWS AppSync (managed GraphQL)` · `AppFlow` · `IAM roles` · `GraphQL + REST APIs`.
*Maps to JD: REST APIs, cloud. (older — mention briefly.)*

### Lakshya Space — Python firmware
`Python firmware` · `embedded/resource-constrained` · `mentored 19 interns`.

## KEY PROJECTS

### LLM Evaluation Framework ★★★ (JD: "evaluations and safety guardrails")
★`LLM-as-judge (rubric, score normalization)` · ★`hallucination detection (claim decomposition + 3-way NLI)` · `RAG faithfulness ≠ accuracy` · `consistency (multi-run cosine, Jaccard fallback)` · ★`Celery + Redis broker/worker` (→ your Kafka bridge) · `SQLAlchemy 2.0 async + asyncpg + Alembic` · `Docker Compose (5 services, health-check ordering)` · `registry/factory extensibility` · `Postgres JSON column` · `AND-logic pass/fail` · `Slack alerting` · `Streamlit + Plotly`.
*Maps to JD: evaluations, guardrails, event-driven-ish async, FastAPI, Docker, microservices.*

### Prompt Regression Suite ★★ (JD: CI/CD + evaluations)
`tiered evaluation (rules → semantic → judge, fail-fast)` · `client-side judge-score recompute` · `anti-self-bias routing` · `multi-run averaging + flakiness (std-dev)` · `delta-vs-baseline regression` · `3-rule baseline governance (audit-logged)` · `reverse-index selective CI` · ★`GitHub Actions PR gate` · `asyncio.Semaphore` · `SQLAlchemy async` · `Typer CLI`.
*Maps to JD: CI/CD (GitHub Actions), evaluations, Pytest discipline.*

### Bias & Fairness Auditor ★ (JD: guardrails + banking/lending fairness)
`counterfactual fairness testing` · `ANOVA + Cohen's d (significance + effect size)` · `two-tier sentiment (VADER → DistilBERT)` · `semantic similarity + TF-IDF fallback` · `blind LLM-judge (label stripping)` · `asyncio.Semaphore rate cap` · `fpdf2 PDF` · `EU AI Act Art 9/13 / EEOC / RBI` · `weighted composite scoring`.
*Maps to JD: guardrails, ML/NLP, regulated/banking domain fit.*

### EMS 2.0 ★ (JD: MongoDB + RAG + document-centric)
`local LLM (Ollama qwen2.5)` · ★`polyglot persistence (PostgreSQL + MongoDB GridFS + FAISS)` · ★`RAG (chunk 500/100 → embed → top-k → grounded)` · `multi-strategy JSON repair` · `pdfplumber + pytesseract OCR` · `daemon threads over BackgroundTasks` · `2-stage intent (keyword → LLM)` · `session memory + pronoun resolution` · `temp=0/seed=42` · `VRAM-constrained model selection` · `MagicMock tests`.
*Maps to JD: MongoDB, RAG, document processing, concurrency, Pytest/MagicMock. (Study Mongo aggregation to deepen.)*

### Financial Statement Parser (JD: document-centric + banking)
`browser WASM OCR (Tesseract.js)` · `pdf.js canvas pipeline` · `Gemini JSON mode` · `3-method JSON truncation-repair cascade` · `privacy-by-design (client-side)` · `state machine` · `SheetJS + jsPDF export` · `React + Vite`.
*Maps to JD: document/OCR (Document AI parallel), summarization/extraction, React consumer.*

### Blog — Astro SSG
`Astro static-site generation` · `build-time vs runtime` · `import.meta.glob` · `hand-built weighted search` · `IntersectionObserver` · `escapeHtml XSS guard`.
*Maps to JD: frontend/React-adjacent, build pipelines. (least relevant — mention only if asked.)*

---

*Built from the Mphasis/Wells Fargo JD + your resume. Weight your prep: Python/FastAPI/GenAI are the spine; MongoDB-aggregation, LangGraph/ADK, Kafka, MCP/FastMCP, OpenShift are the study gaps. Lead every answer with a Brane / LLM-Eval / 5G-pipeline story — you have real evidence for most of what they want. Part F above is your per-project concept inventory — every term is something you can be asked to explain.*
