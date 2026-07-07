# Section 1 — Matched Skills: Explanation + Term Definitions

*Same format as Section 3. For each matched skill: **the explanation** — how I'd state my experience with it plainly, for the interviewer's ears. Then **the terms** — every concept I'll naturally say while explaining, each with a 2-line definition, so when they stop me on any word I have the crisp answer ready.*

**Topics:** 1.1 Python · 1.2 FastAPI/REST · 1.3 asyncio · 1.4 Pydantic · 1.5 pytest · 1.6 LangChain/RAG · 1.7 Vector DBs · 1.8 Prompt/eval · 1.9 Agentic AI · 1.10 gRPC/microservices · 1.11 Redis/caching · 1.12 PostgreSQL/SQL · 1.13 SQLAlchemy/Celery/Streamlit/GraphQL · 1.14 Docker/K8s/CI-CD · 1.15 Auth/RBAC/security · 1.16 Doc ingestion/OCR · 1.17 LLM APIs/routing · 1.18 Claude Code · 1.19 React/frontend · 1.20 Git/Agile · 1.21 Node.js/AWS

---

## 1.1 Python (core language)

### The explanation

I have 5+ years of Python across embedded firmware, Node/AWS backends, telecom automation, and production LLM systems. Day to day I lean on the concurrency model (knowing when to use threads, processes, or async), generators for memory-efficient streaming, and the common traps that bite teams — mutable defaults, the GIL, identity vs equality. My deepest systems-Python was NFTRACE (multiprocessing, context managers) and the Brane agent runtime (defensive parsing, the agent loop).

### The terms

- **GIL (Global Interpreter Lock)** — A lock in CPython that lets only one thread run Python bytecode at a time. So threading gives no speedup for CPU-bound work, but still helps I/O-bound work because a thread releases the GIL while waiting.
- **Threading vs multiprocessing vs asyncio** — Threading and asyncio are for I/O-bound work (waiting); multiprocessing gives true parallelism for CPU-bound work via separate processes. Async is single-threaded cooperative concurrency; multiprocessing sidesteps the GIL entirely.
- **Generator / yield** — A function that produces values lazily one at a time instead of building a whole list in memory. Lets you stream a million-row result holding one row at a time, so memory stays flat.
- **Decorator** — A function that wraps another to add behavior without changing its code (`@lru_cache`, retries, timing). Under the hood `@d` means `func = d(func)`.
- **Context manager (`with`)** — Guarantees setup and cleanup even if an exception fires — files, DB sessions, locks get released reliably. Defined with `__enter__`/`__exit__` or `@contextlib.contextmanager`.
- **Mutable default argument** — `def f(x=[])` creates one list shared across all calls, so it accumulates state between calls. Fix: default to `None` and create a fresh list inside.
- **`is` vs `==`** — `==` compares value; `is` compares identity (same object in memory). Use `==` for value, `is` only for singletons like `None`.
- **Reference counting / garbage collection** — Python frees objects when their reference count hits zero, plus a cycle-detecting GC for objects that reference each other. Reference counting alone can't free cycles.
- **`lru_cache`** — A decorator that memoizes a pure function's results keyed by arguments. I use it to load a heavy model once as a process-level singleton.
- **`*args` / `**kwargs`** — Capture arbitrary positional/keyword arguments, legitimate for decorators and wrappers that forward them. A smell when they hide a function's real signature and kill type hints.
- **Type hints** — Annotations that are inert at runtime in plain Python (used by mypy/IDEs), but read at runtime by Pydantic/FastAPI to actually validate data.
- **Shallow vs deep copy** — Shallow copies the top container but shares nested objects; deep recurses. I snapshot state (`[...items]`) before an async loop to avoid mutating shared references mid-flight.

---

## 1.2 FastAPI and REST API design

### The explanation

FastAPI is my default backend — I've built REST APIs with it for NFTRACE, the 5G pipeline, the RF generator, and my eval tools. I pick it for three reasons: it's async-native on ASGI, it validates every request with Pydantic for free, and it auto-generates OpenAPI docs so the frontend has a live contract. I can speak to the production gotchas — blocking calls in async endpoints, CORS misconfig, the yield-session-plus-background-task trap — because I've hit them.

### The terms

- **ASGI vs WSGI** — ASGI is the async server interface FastAPI is built on; WSGI is the older synchronous one behind Flask/Django. ASGI handles high concurrent I/O on one thread via an event loop; WSGI blocks a thread per request.
- **`async def` vs `def`** — `async def` runs on the event loop (use with async I/O); plain `def` runs in a threadpool so blocking work doesn't stall the loop. Blocking code inside `async def` freezes the whole loop under load.
- **Pydantic validation** — FastAPI validates request bodies against typed Pydantic models automatically, returning a 422 with field-level errors on mismatch. Zero boilerplate.
- **`Depends` / dependency injection** — Reusable dependencies (DB session, current user) injected into endpoints and overridable in tests. Cleaner code and testability.
- **BackgroundTasks vs Celery** — BackgroundTasks run after the response in-process (lost on restart); Celery is a durable, retryable, distributed queue. Fire-and-forget trivia vs work that must not be lost.
- **CORS** — Browser security controlling cross-origin calls; needs middleware allowing the frontend's origin. Two traps: `allow_origins=['*']` with credentials is rejected, and forgetting `Authorization` in allowed headers.
- **APIRouter** — Groups endpoints by domain into separate router modules. Keeps a large app from becoming one giant file.
- **`response_model`** — Declares and filters the response schema, so internal fields (password hash, flags) don't leak even if the object has them. The response contract.
- **OpenAPI / Swagger** — Auto-generated interactive API docs at `/docs`, giving the frontend a live contract to build against. No manual doc effort.
- **HTTPException** — The way to raise expected errors with a status code and message (404, 400). Custom handlers make every error come back in one consistent shape.
- **Middleware vs dependency** — Middleware wraps every request (request-id, timing, CORS); a dependency is per-endpoint and returns a value into the handler (auth, DB). Value-into-handler → dependency; blanket wrap → middleware.
- **StreamingResponse** — Streams a response in chunks via an async generator instead of buffering — for large downloads or LLM token streaming (SSE). Improves perceived latency.
- **Uvicorn / Gunicorn workers** — Uvicorn is the ASGI server; Gunicorn manages multiple worker processes to use all CPU cores. Start with ~2×cores+1, then measure.
- **Pagination** — Returning large lists in pages (offset or keyset/cursor) rather than unbounded. Keyset scales better than offset deep into the data.

---

## 1.3 Async programming (asyncio)

### The explanation

I use asyncio for I/O-bound concurrency — mainly fanning out hundreds of LLM calls in my eval and bias-auditor tools, capped by a semaphore so I don't blow the provider rate limit, and pairing async FastAPI with an async DB driver so a request never blocks on a DB write. The core mental model I explain is the event loop swapping tasks at `await` points instead of blocking a thread.

### The terms

- **Event loop** — The single-threaded scheduler that runs coroutines, switching to another task whenever the current one awaits I/O. It's what makes one thread juggle thousands of in-flight I/O operations.
- **`await`** — Yields control back to the event loop while waiting on I/O, so other tasks run; resumes where it left off when the I/O completes. The cooperative yield point.
- **`asyncio.gather`** — Runs multiple awaitables concurrently and returns their results; total time is roughly the slowest, not the sum. By default one exception cancels the rest.
- **`asyncio.Semaphore`** — Caps how many coroutines run concurrently, so 500 LLM calls run bounded at, say, 10 in flight. The control that prevents rate-limit errors on fan-out.
- **asyncpg** — The fastest async PostgreSQL driver; non-blocking, unlike psycopg2 which would block the loop. Pairs with SQLAlchemy async.
- **`run_in_executor`** — Runs blocking or CPU-bound code in a thread/process pool from an async context, so it doesn't stall the loop. Threadpool for blocking I/O, process pool for CPU work.
- **Coroutine** — What an `async def` returns when called; it doesn't run until awaited or scheduled. Forgetting the `await` is a common bug — the work silently never happens.
- **`create_task`** — Schedules a coroutine to run in the background on the loop; you must keep a reference or it can be garbage-collected and cancelled. In-process only, not durable across restarts.
- **`asyncio.Lock`** — Guards shared state across await points, since a task can be interrupted mid-read-modify-write by another. Prevents interleaving corruption even though it's single-threaded.
- **Backpressure** — Limiting how fast you accept/dispatch work so you don't overwhelm a downstream — the Semaphore, or bounded queues. Without it, async will happily launch a million tasks and exhaust memory.
- **`wait_for` / timeout** — Puts a hard time limit on an async operation so a slow dependency can't hang a task forever. Every external await gets one.
- **`async with`** — Async context manager for setup/teardown that itself does I/O (async DB session, httpx client). Awaits `__aenter__`/`__aexit__` so acquire/release don't block.
- **Cancellation** — `task.cancel()` raises `CancelledError` in the coroutine; you catch it to clean up, then re-raise so cancellation propagates. Swallowing it leaves the task running.

---

## 1.4 Pydantic (v2)

### The explanation

Pydantic is the backbone of every service I build — it validates and coerces data at parse time with clear errors. I use it three ways: FastAPI request/response models, schema enforcement on LLM JSON output before it hits the database (the critical one for AI work, since raw model JSON fails 10–20% of the time), and typed config from env vars.

### The terms

- **Model** — A class of typed fields that validates and coerces incoming data, raising structured errors on mismatch. The unit of validation.
- **`field_validator`** — A method that validates or normalizes a single field beyond basic type coercion — e.g. accept multiple date formats, always store one. Per-field custom rules.
- **`model_validator`** — Runs after individual fields are validated and sees the whole model, for cross-field invariants like "end_date after start_date." Enforces relationships between fields.
- **`Field` constraints** — Declarative constraints on a field — `min_length`, `ge`/`le` for ranges, `default_factory` for safe mutable defaults, `alias` for external key names.
- **`model_dump` / `model_dump_json`** — Serialize a model to a dict or a JSON string; `by_alias=True` uses aliased names. Watch types JSON doesn't support (datetime, Decimal).
- **BaseSettings (pydantic-settings)** — Loads and validates config from environment variables into one typed object, cached so it's parsed once. A missing var fails at startup, not at request time.
- **`model_config` / `extra`** — Per-model behavior: `extra="forbid"` rejects unexpected fields (strict contracts), `frozen=True` for immutability. Catches typo'd field names loudly.
- **Strict mode** — Opts out of automatic coercion so `"42"` is rejected for an int instead of coerced. Used for financial/safety-critical fields where silent coercion is dangerous.
- **`computed_field`** — Exposes a value derived from other fields in serialization, so the invariant lives on the model, not recomputed in every consumer.
- **ValidationError** — The structured, per-field error Pydantic raises; I catch it per-item so one bad input logs and is skipped, not crash the batch.
- **Coercion** — Pydantic's automatic type conversion (`"42"` → `42`); helpful for lenient input, dangerous where it silently accepts something you meant to reject (hence strict mode).
- **v2 rewrite** — Pydantic v2's core is Rust, ~10× faster than v1; API changes include `@field_validator`, `@model_validator`, `.model_dump()`. Don't mix v1/v2 patterns.

---

## 1.5 pytest and testing discipline

### The explanation

I test at three levels — unit tests per component, integration tests hitting the FastAPI stack with dependencies overridden and externals mocked, and a few end-to-end. For LLM code I don't assert exact strings; I mock the model to test my logic deterministically and push quality checks into a separate eval suite. Concrete examples: NFTRACE tested with mock XML-RPC servers and synthetic pcap fixtures, the RF generator tested with deliberately-broken templates to prove the parser rejects them.

### The terms

- **Fixture** — Reusable test setup/teardown (a test DB session, a client, sample data), ideally small and composable. A `yield` fixture guarantees teardown even on failure.
- **`parametrize`** — Runs one test function across many input/output cases (boundary values, each enum). Each case is a separately-named failure so you see exactly which input broke.
- **Mock / stub / fake** — A stub returns canned values; a mock also asserts it was called correctly; a fake is a working lightweight implementation (in-memory DB, mock server). I used fakes (mock XML-RPC) in NFTRACE.
- **TestClient / httpx.AsyncClient** — Call FastAPI endpoints in-process without a real server; async client for async endpoints. Fast, deterministic integration tests.
- **Dependency override** — Swapping a real dependency (the DB) for a test one in tests via FastAPI's override mechanism. Lets integration tests run against a test DB.
- **monkeypatch / freezegun** — Patch functions or pin the clock in tests, so `datetime.now()` and `uuid4()` don't make tests flaky. Makes time and identity deterministic.
- **conftest.py** — Holds shared fixtures and hooks available across a test directory without importing. Kept lean to avoid a "god fixture" everything depends on.
- **pytest-asyncio** — Enables `async def` test functions and awaiting inside tests. Needed so async code's awaits actually execute in tests.
- **Coverage** — Measures which lines/branches tests execute; used to find untested error paths, not chased as a target (you can hit 100% asserting nothing).
- **Markers** — Tags like `@pytest.mark.slow` to separate fast unit tests from slow integration ones, so the fast suite runs every save.
- **Flakiness** — A test that passes and fails without code changes, usually from nondeterminism or shared state. For LLM output I average multiple runs and flag high variance rather than trusting one score.
- **Over-mocking** — Mocking the thing you're supposed to test, so the test verifies the mock, not reality. For data-layer bugs, integration-test against a real test DB instead.

---

## 1.6 LangChain and RAG (end-to-end)

### The explanation

I built a production RAG pipeline — the 5G failure detector — end to end: a curated knowledge base, embeddings, a Qdrant vector store, LangChain RetrievalQA for retrieval-plus-generation, and a separate evaluation layer that scores faithfulness. I also did FAISS-based RAG for employee search in EMS. I can walk the whole chain and defend the choices — Qdrant for metadata filtering, returning source documents for trust, and how I diagnose whether a bad answer is a retrieval or generation problem.

### The terms

- **RAG (Retrieval-Augmented Generation)** — Retrieve relevant documents for a query, then have the LLM generate an answer grounded in them. Injects knowledge at inference instead of baking it into the model.
- **Chunking** — Splitting documents into retrieval-sized pieces (I used 500 chars, 100 overlap in EMS). Structure-aware chunking (split on sections) beats fixed-size because each chunk is a coherent unit.
- **Overlap** — Repeating some text between adjacent chunks so an idea split at a boundary is still retrievable. Preserves context across the seam.
- **Embeddings** — Vector representations of text so semantically similar text has similar vectors. The same model must embed both the indexed docs and the query, or similarity is meaningless.
- **Vector store** — A database for embeddings with fast nearest-neighbour search (Qdrant, FAISS). Where the knowledge base lives for retrieval.
- **Retriever** — The component that embeds the query, searches the vector store, and returns the top-k documents. In LangChain, `vectorstore.as_retriever(k=5, filter=...)`.
- **RetrievalQA** — A LangChain chain that ties retrieval and generation: retrieves docs, stuffs them into a prompt, calls the LLM, returns the answer plus source docs.
- **"Stuff" chain** — Puts all retrieved docs into one prompt (simplest). Breaks when the docs exceed the context window; alternatives are map-reduce/refine at higher cost.
- **`return_source_documents`** — Returns which documents matched alongside the answer, for user trust and for debugging whether a bad answer was retrieval or generation.
- **Top-k** — How many documents to retrieve (I used 5). Too few misses context, too many adds noise, cost, and risks the context window.
- **Faithfulness** — Whether the answer stayed inside the retrieved context, separate from whether it's true. High faithfulness + wrong answer = retrieval problem; low = model ignoring context.
- **Reranking** — A cross-encoder re-scores the top-50 first-stage results down to a precise top-5 (I know where it fits, haven't shipped it). The highest-ROI RAG precision upgrade.

---

## 1.7 Vector databases (Qdrant, FAISS)

### The explanation

I've shipped Qdrant (the 5G pipeline) and FAISS (EMS). My strongest story is the choice: I needed vendor/layer-specific retrieval so a Nokia error never matches an Ericsson pattern, and Qdrant filters by metadata at the database level before ranking, which FAISS can't do. I can reason about the others — Weaviate, Pinecone, pgvector — on the axes of managed-vs-self-hosted, native filtering, and scale, even though I've only shipped two.

### The terms

- **HNSW** — Hierarchical Navigable Small World, the graph index vector DBs use for approximate nearest-neighbour search. Navigating the graph is far faster than comparing the query to every vector.
- **ANN (approximate nearest neighbour)** — Trading a little recall for a massive speed win versus exact search, which is O(N) and too slow at scale. You might occasionally miss a true top-k result.
- **Cosine similarity** — Compares the angle between vectors, ignoring magnitude, so the same meaning in different lengths still matches. Correct for text similarity.
- **Metadata filtering** — Constraining the search to vectors matching tags (vendor, layer) before ranking. Qdrant does it at the DB level; FAISS forces post-retrieval filtering in Python.
- **Embedding dimension** — The length of the vector (e.g. 1536 for OpenAI, 384 for all-MiniLM). Higher can capture more nuance but costs more storage and compute.
- **Score threshold** — A minimum similarity below which a match is treated as "no good match," so you return "unknown" instead of a hallucinated answer. I used 0.65.
- **Quantization** — Reducing vector precision to cut memory and speed search at a small accuracy cost. A lever for scale.
- **Sharding** — Splitting a large collection across nodes to keep search latency stable as it grows. Qdrant's horizontal scale path.
- **Upsert** — Insert-or-update a vector by id, so you index only new/changed records incrementally rather than rebuilding. Keeps the index in sync with the source.
- **Multi-tenancy filtering** — A mandatory tenant_id filter so tenants never see each other's vectors. The same metadata-filter mechanism used for isolation.
- **pgvector** — A Postgres extension storing vectors next to relational data — one DB, transactional. Right when you're already on Postgres at moderate scale.

---

## 1.8 Prompt engineering, evaluation, hallucination detection

### The explanation

This is my sharpest edge — I've built three tools living entirely in this space: an LLM evaluation framework, a prompt regression suite, and a bias auditor, plus prompt assembly for the Brane agent loop. So I can speak concretely about LLM-as-judge scoring, hallucination and faithfulness detection, consistency, anti-self-bias, and turning prompt quality into a CI gate — not as theory but as things I've shipped.

### The terms

- **LLM-as-Judge** — Using a strong LLM to score another model's output against a rubric, returning structured JSON. Avoids brittle hand-written heuristics that break on novel prompts.
- **Hallucination detection** — Decompose the response into atomic claims, classify each against a reference as supported/unsupported/contradicted, score = fraction supported. Catches fabricated claims.
- **Faithfulness vs accuracy** — Faithfulness = did the answer stay inside retrieved context; accuracy = is it true. They diverge, which localizes a RAG failure to retrieval vs generation.
- **Consistency** — Run the same prompt several times at temperature 0.7 and measure response similarity. Catches prompts that are right once but unreliable on average.
- **Anti-self-bias routing** — The judge is always a different provider than the model under test, enforced in code. A model grading its own style is biased toward its own patterns.
- **Temperature** — The randomness knob; low (0–0.1) for deterministic/factual output, higher (0.7) when you deliberately want variance (like consistency checking).
- **Zero-shot / few-shot / chain-of-thought** — No examples / a few examples / "think step by step." Default to the cheapest that works; add examples or reasoning only when quality demands it (they cost tokens).
- **Prompt injection** — User/retrieved text containing instructions that hijack the prompt. Defend by separating system from user content, treating retrieved text as data, and validating output before any action.
- **Structured output** — Getting reliable JSON via provider JSON mode plus an explicit prompt ("begin with `{`") plus defensive parsing. No single layer is reliable alone.
- **Rubric** — Scoring across multiple dimensions (accuracy, relevance, completeness, clarity, safety) instead of one number, with a hard floor flagging any single dimension's critical failure.
- **Delta-based regression** — Fire a regression when the score drops below the stored baseline by a delta, not against a fixed threshold. Lets baselines rise as prompts improve.
- **Golden set** — A fixed set of representative prompts with known-good answers, run on every change and on a schedule. The shared, auditable definition of "good enough to ship."

---

## 1.9 Agentic AI (agent loop, tool-calling)

### The explanation

At Brane I contributed to a production single-agent runtime — I owned parts of the agent loop (prompt assembly, a verifier correction loop), the tool-registry integration, PostgreSQL state persistence, and RBAC-gated tool access. So I speak about tool-calling, planning/execution, memory/state, and self-healing from real work. I'm honest that it was a single agent, not multi-agent orchestration, but I built every primitive multi-agent composes.

### The terms

- **Agent loop** — The plan→act→observe→decide cycle: assemble prompt, call model, if it requests a tool invoke it and feed the result back, else validate and finish. Bounded by a step cap.
- **Tool registry** — The catalog of tools an agent can call — name, purpose, input schema — injected into context. Decoupled from the loop, so adding a tool is data plus a function.
- **Tool-calling / function calling** — The model emits a structured call (tool name + arguments) instead of prose; the loop detects and dispatches it. How the agent takes actions.
- **Verifier correction loop** — After output, a verifier validates it; on failure it feeds the specific failure back and re-prompts, so the agent self-corrects. Bounded by a retry cap.
- **Checkpointer / state persistence** — Persisting the agent's working state and step history (I used Postgres tables) so a run survives restarts and can be replayed for debugging.
- **Human-in-the-loop (HITL)** — Pausing at a decision point for human approval before a consequential action, checkpointing state and resuming on approval. The safety valve for autonomy.
- **Planning vs reactive** — A reactive agent decides one step at a time on the latest observation (ReAct); a planning agent makes a multi-step plan then executes, re-planning on failure.
- **Grounding** — Injecting real retrieved data into the prompt so the agent reasons from actual context, not invention. The anti-hallucination anchor for decisions.
- **Step cap** — A hard limit on loop iterations plus a stop condition in the router, so the agent can't loop forever. Hitting it is a handled failure, not a crash.
- **Multi-agent orchestration** — Coordinating several specialized agents under a supervisor (CrewAI, AutoGen). Justified only when a task genuinely decomposes into independently-verifiable subtasks.

---

## 1.10 gRPC and microservices

### The explanation

I integrated a gRPC model gateway at Brane — internal service-to-service inference with multi-provider routing and stateless horizontal scaling — so gRPC is real experience, not book knowledge. On microservices my honest take is start with a modular monolith and split only for concrete reasons (independent scaling, deployment cadence, team ownership), because the real cost is distributed transactions and cross-service debugging.

### The terms

- **gRPC** — A framework for service-to-service calls using binary protobuf over HTTP/2, strongly typed and low-overhead. Ideal for internal calls; browsers can't speak it without a proxy.
- **Protobuf** — The schema and binary serialization format gRPC uses; client and server generate code from one `.proto`, so shape mismatches are compile-time errors. Compact and versioned.
- **HTTP/2** — Gives multiplexing (many concurrent calls over one connection), binary framing, and streaming. Why gRPC handles many concurrent inference requests efficiently.
- **Streaming (gRPC)** — Unary / server-streaming / client-streaming / bidirectional call types; server-streaming maps to streaming model tokens back. Avoids buffering a large response.
- **Circuit breaker** — Stops calling a failing dependency after N consecutive failures (open), then trials recovery (half-open). Prevents a slow dependency from exhausting your resources and cascading.
- **Saga pattern** — A workflow as a sequence of local transactions with compensating actions on failure, instead of a distributed transaction. How you keep consistency across services.
- **Outbox pattern** — Write the DB change and the outbound event in one local transaction; a poller publishes the event. So you don't lose events if the broker is down.
- **API gateway** — The single entry point handling edge concerns — auth, rate limiting, routing, SSL termination. Verifies the JWT once so internal services don't re-verify.
- **Service discovery** — How a service finds healthy instances of another by name (Consul, Kubernetes DNS) as instances scale and move. Avoids hardcoded host:port.
- **mTLS** — Mutual TLS so both services authenticate each other on internal calls. Part of securing service-to-service traffic.
- **Monolith vs microservices** — A single deployable vs many independently-deployable services. Start monolith, split when scaling/cadence/ownership justify the added complexity.

---

## 1.11 Redis and caching

### The explanation

I've used Redis two ways: response caching in the 5G pipeline (cache-aside for frequent error lookups) and parallel-execution isolation in NFTRACE (each session under a unique key with a TTL so concurrent workers don't collide). I can speak to the caching hard parts — invalidation and the thundering-herd problem — and to why Redis over an in-memory dict or SQLite for hot state.

### The terms

- **Cache-aside** — Check the cache first; on a miss, hit the DB and populate the cache with a TTL. Resilient (falls back to DB if Redis dies) and lazy (only caches what's requested).
- **TTL (time-to-live)** — Auto-expiry on a key, bounding staleness and auto-cleaning ephemeral state (like a crashed worker's session). Chosen by staleness tolerance vs recompute cost.
- **Cache invalidation** — Deleting the cache key on every write to the underlying data, so the next read fetches fresh. The usual cause of stale-data bugs is forgetting this.
- **Thundering herd** — A hot key expires and thousands of concurrent requests all miss and hammer the DB at once. Fix with a distributed lock (`SETNX`) so only one request rebuilds the cache.
- **SETNX / distributed lock** — Set-if-not-exists, used so only the first request acquires the rebuild lock and the rest wait. Also the basis of idempotency keys.
- **Eviction policy** — What Redis drops when memory is full — `allkeys-lru` (least recently used), `volatile-ttl`, or `noeviction`. For a cache you want LRU/LFU.
- **Write-through vs write-back** — Write-through writes to cache and DB synchronously (always fresh, slower writes); write-back writes to cache and flushes later (fast, risk of loss). Cache-aside is the safe default.
- **Broker** — Redis as the message queue Celery pulls tasks from. Simple and fast; RabbitMQ for stronger delivery guarantees.
- **Sorted set** — A Redis structure for ranked data or sliding-window rate limiting. Right structure beats manual key juggling.
- **jti blacklist** — Storing a revoked JWT's unique id in Redis with a TTL, checked per request (<1ms) for token revocation. Stateless scale with stateful control.
- **Hit rate** — The fraction of reads served from cache; low hit rate means keys expire faster than reused or the key space is too granular. Sometimes the workload just isn't cacheable.

---

## 1.12 PostgreSQL and SQL

### The explanation

PostgreSQL is my deepest database — I did real schema design at Brane (agent identity, junction, RBAC, execution tables). On SQL I can go past "indexes make things faster" to the write penalty, composite-index column order, the functional-index bug, N+1, and reading EXPLAIN ANALYZE. My rule is measure the plan before optimizing.

### The terms

- **Joins** — INNER (matches both sides), LEFT (all left + matches, NULL otherwise), RIGHT, FULL OUTER, self-join. LEFT + `IS NULL` finds records with no related row.
- **WHERE vs HAVING** — WHERE filters rows before grouping; HAVING filters groups after aggregation. You can't put an aggregate in WHERE.
- **Index / B-tree** — A structure that finds rows without scanning the table, speeding lookups/joins/sorts. Costs write speed (index must update) and storage.
- **Composite index (leftmost-prefix)** — An index on (a, b) is usable for filters on `a` or `a,b`, but not `b` alone. Column order matters — most-selective/most-filtered first.
- **EXPLAIN ANALYZE** — Shows the query plan; `Seq Scan` on a big table means no index used, `Index Scan` means it works. Actual-vs-estimated row gaps mean stale statistics (run ANALYZE).
- **Functional-index bug** — `WHERE DATE(created_at)='...'` wraps the column in a function and disables the index. Rewrite as a range (`>= AND <`) and it goes from seconds to milliseconds.
- **N+1 query** — Fetching a list then one query per row for related data — N+1 queries, very slow. Fix with a JOIN or eager loading.
- **Junction table** — A bridge table with foreign keys to both sides, modeling many-to-many. I built multi-agent LO junction tables at Brane.
- **ACID** — Atomicity, Consistency, Isolation, Durability — the guarantees of a reliable transaction. Each prevents a specific data-integrity disaster.
- **Normalization** — Organizing tables so each fact is stored once, reducing redundancy. Denormalize deliberately for read performance, accepting the duplication.
- **Isolation levels** — Read Uncommitted → Read Committed (Postgres default) → Repeatable Read → Serializable, trading correctness against locking. Serializable prevents phantom reads.
- **Connection pool** — Reusing a set of open DB connections across requests instead of connecting per request. Prevents exhausting Postgres's connection limit under load.
- **Keyset pagination** — Paginating with `WHERE id > last_seen ORDER BY id LIMIT n` instead of OFFSET, which scans and discards rows and slows deep in the data.
- **Parameterized queries** — Passing values separately from SQL text so input is never executable SQL. The non-negotiable SQL-injection defense.

---

## 1.13 SQLAlchemy, Celery, Streamlit, GraphQL

### The explanation

SQLAlchemy async is in my eval, prompt-regression, and bias tools — same models across SQLite (dev) and Postgres (prod) via one env var. Celery gives me durable background work where losing a job is unacceptable. Streamlit is my go-to internal-tool UI, always paired with a FastAPI backend for testability. And I built GraphQL + REST at Abjayon with AWS AppSync.

### The terms

- **Session / unit-of-work** — SQLAlchemy's object that tracks changes and flushes them in a transaction. Per-request, not shared across threads; opened and closed via a dependency.
- **Lazy vs eager loading** — Lazy fetches a relationship on access (causes N+1 in loops); eager (`selectinload`/`joinedload`) fetches it up front in one query. Choose by whether you'll access the relationship.
- **Alembic** — SQLAlchemy's migration tool; autogenerates reviewable migration scripts from model changes. Write them backward-compatible (expand-then-contract) to avoid breaking running code.
- **Async ORM / asyncpg** — SQLAlchemy 2.0 async sessions over asyncpg so DB calls yield to the event loop. Keeps async FastAPI non-blocking end to end.
- **Celery broker / worker / result backend** — App enqueues to a broker (Redis), a worker pulls and runs it, the backend stores the result. Decouples API response time from task runtime.
- **Idempotency (tasks)** — Designing a task so a retry doesn't double-process (check-and-set on a job id). Required because retried tasks must be safe to re-run.
- **Streamlit rerun model** — Streamlit re-executes the whole script on every interaction, so expensive work must be cached (`@st.cache_data`/`@st.cache_resource`). Session state holds values across reruns.
- **Streamlit + FastAPI split** — UI in Streamlit, logic in FastAPI, so the logic is testable with pytest and reusable from a CLI/CI, not locked in the UI.
- **GraphQL** — A single endpoint where the client requests exactly the fields it wants, avoiding over/under-fetching. Better for diverse client data needs; harder to cache and rate-limit than REST.
- **DataLoader** — Batches and caches per-item resolver requests within one GraphQL query to solve the resolver-level N+1 problem.
- **AppSync** — AWS's managed GraphQL service (hosts the API, resolvers, real-time subscriptions). Where my GraphQL experience came from.

---

## 1.14 Docker, Kubernetes, CI/CD

### The explanation

I containerize with Docker (ran Qdrant as a container, the whole eval stack via docker-compose) and I authored the team's Docker best-practice checklist at Nokia. I validated K8s pod health during 5G Core testing. On CI/CD I built a GitHub Actions PR merge-gate plus a weekly drift monitor for the prompt-regression suite, and integrated NFTRACE into Nokia's pipeline.

### The terms

- **Base image pinning** — Using `python:3.11-slim`, never `python:latest` — a mutable tag that changes under you and breaks builds silently. Pin for reproducibility.
- **Multi-stage build** — A build stage produces artifacts, a slim final stage copies only them, dropping build tooling. Smaller, more secure production image.
- **Layer caching** — Copy the dependency manifest and install before copying code, so a code change reuses the cached deps layer. Order layers least-changed to most.
- **Non-root user** — Running the container as a non-root user to limit blast radius if the app is compromised. Low-effort real hardening.
- **Secrets injection** — Inject secrets at runtime via env/secret manager, never bake them in as `ENV` (visible in `docker history`). Build-time secrets persist in image layers.
- **Liveness vs readiness probes** — Liveness "is it alive?" (fail → restart); readiness "ready to serve?" (fail → stop routing, don't kill). A pod can be alive but not ready at startup.
- **docker-compose** — Brings up multiple dependent services with one command and health-check ordering. Perfect for local multi-service dev; K8s for production orchestration.
- **Rolling / blue-green / canary** — Zero-downtime deploy strategies: replace instances gradually / switch traffic to a fully-new environment / route a small % first then ramp. All with easy rollback.
- **Registry / ECR** — Where built images are stored and pulled from (Docker Hub, AWS ECR). Immutable pinned images make rollback precise.
- **RED metrics** — Rate, Errors, Duration (p95/p99 latency) — the core service health metrics to monitor and alert on.
- **Distributed tracing** — A request-id injected at the gateway and propagated across services/queues so you can trace one request end to end. Essential for cross-service debugging.

---

## 1.15 Authentication, RBAC, API security

### The explanation

I implemented attribute-level RBAC at Brane — authorization down to individual attributes with a caching layer — which is real, fine-grained authz. I can explain JWT (and the signed-not-encrypted trap), access/refresh tokens, OAuth2 and OIDC, and I name the #1 API vuln (broken object-level authorization) unprompted. My security framing is layered defense.

### The terms

- **JWT (header.payload.signature)** — A compact signed token carrying claims (user id, expiry); verified by signature with no DB lookup, which is why it scales. Three dot-separated base64 parts.
- **Signed vs encrypted** — A JWT is signed (integrity), not encrypted — anyone can base64-decode the payload and read it. So no secrets or PII in the payload.
- **Access vs refresh token** — Access is short-lived and sent every request (small leak window); refresh is long-lived, stored securely, used to mint new access tokens without re-login.
- **jti blacklist** — Revoking a JWT before expiry by storing its unique id in a Redis blacklist with a matching TTL, checked per request. Solves the stateless-revocation problem.
- **Authn vs authz** — Authentication is who you are (identity); authorization is what you're allowed to do (permissions). Attribute-level RBAC is authorization.
- **OAuth2 (authorization-code flow)** — Delegated authorization: redirect to the auth server, user consents, get a code, exchange it server-side for an access token. "Log in with Google."
- **OIDC** — An identity layer on OAuth2 adding an ID token (a JWT with identity claims) so you know who the user is, not just what they can access. SSO builds on it.
- **Attribute-level RBAC** — Permissions defined per individual attribute, not just broad roles, so a user can access some fields of an object but not others. Finer and harder than role-level.
- **BOLA (broken object-level authorization)** — Authenticating correctly but never checking the user owns the requested resource, so any user reads anyone's data. OWASP's top API risk.
- **Rate limiting** — Capping requests per client (a Redis counter or sliding window) to prevent abuse and protect budget. Especially on expensive endpoints.
- **Hashing vs encryption** — Hashing is one-way (passwords, salted slow bcrypt/argon2); encryption is two-way (data you must read back). Never store passwords with encryption or plaintext.
- **Secrets management** — Secrets in env/secret manager, injected at runtime, never in source, images, or logs; least-privilege on every credential.

---

## 1.16 Document ingestion (PDF, OCR, images)

### The explanation

I've shipped two ingestion pipelines: EMS (pdfplumber for PDF text, pytesseract OCR fallback for images, a resume-validity gate before any LLM call) and the Financial Parser (in-browser Tesseract.js OCR, only text sent to the model). The reliability comes from the scaffolding around the LLM — validation gates, multi-strategy JSON parsing, truncation salvage — not from trusting raw model output.

### The terms

- **pdfplumber** — A Python library that extracts embedded text from text-based PDFs directly. Fast and accurate for real-text PDFs.
- **Tesseract / pytesseract** — The Tesseract OCR engine (pytesseract is the Python wrapper) that reads text from images/scanned PDFs. The fallback when there's no embedded text.
- **WASM (Tesseract.js)** — Tesseract compiled to WebAssembly so OCR runs inside the browser at near-native speed. Enables in-browser OCR with no server.
- **OCR fallback** — Routing image/scanned documents through OCR when direct text extraction yields nothing. Always handle both — a "PDF" might be real text or a picture of text.
- **Resume scoring gate** — A cheap validity check (section headers, keywords, contact info) before any LLM call, rejecting garbage documents. Saves inference cost and blocks bad data.
- **Multi-strategy JSON parsing** — A parse chain (direct → regex extraction → key-value fallback) for LLM output, since raw JSON fails 10–20% of the time. Recovers salvageable responses before validation.
- **Truncation salvage** — Recovering a partial result when the model's response is cut off — find the last complete object and close the JSON. Partial results beat a hard failure.
- **Regex anchors bug** — `^...$` in an email/phone regex only matches the whole string, so it never matches an email embedded in resume text. Fix: drop anchors, use `re.search`.
- **Extraction temperature** — Pinning temperature to 0–0.1 for extraction/parsing so the same document yields the same structured output and the model doesn't invent values. Extraction is the opposite of creative.
- **Chunking (for RAG)** — After extraction, split text into overlapping chunks (500/100 in EMS) and embed for semantic search. Overlap preserves context across boundaries.

---

## 1.17 LLM APIs, model routing, token economics

### The explanation

I've integrated Anthropic (Sonnet/Haiku), Google Gemini, and local models via Ollama — cloud and local across three ecosystems. The senior signal I lead with is model selection, not always reaching for the biggest model: Haiku/Sonnet routing cut cost ~60% in the 5G pipeline, Haiku for cheap extraction in the RF generator, local Ollama for privacy in EMS. Cost discipline is routing, tiering, caching, and local fallbacks.

### The terms

- **Model routing** — Sending easy/high-confidence cases to a cheap model and hard/critical ones to a strong model. Cut API cost ~60% in the 5G pipeline with no accuracy loss on hard cases.
- **Model selection** — Matching model capability to task difficulty (Haiku for extraction, Sonnet for reasoning, local for privacy). Picking the smallest model that does the job well.
- **Token economics** — Cost scales with input+output tokens, managed via routing, capping output, trimming context, caching, and local models. Engineering discipline, not just "the model is expensive."
- **Context window** — The max tokens (input+output) a model handles per call; exceeding it truncates and silently loses content. Managed by capping input and keeping top-k small.
- **Quantization** — Reducing model weight precision to fit modest hardware (let qwen2.5:7b fit a 6GB GPU) at a small accuracy cost. The lever for running capable models locally.
- **Streaming** — Yielding tokens as generated (SSE / `stream=True`) so the user sees output immediately. A bounded upgrade to async endpoints; my honest gap (haven't shipped it).
- **Structured output mode** — Provider features (`responseMimeType: application/json`, function calling) that constrain the model to return valid JSON. One layer of reliable structured output.
- **Prompt caching vs response caching** — Prompt caching (provider-side) cuts the per-call cost of a reused prompt prefix; response caching skips the call entirely for identical requests. Both cut cost differently.
- **Local vs cloud** — Local (Ollama) for privacy, zero per-call cost, and inference control; cloud for top-tier capability without running infra. Chosen by whether privacy/cost or capability dominates.
- **Provider abstraction** — A factory/registry routing by model name to a common interface returning a standard response object. Makes providers swappable — adding one is a class plus a routing rule.

---

## 1.18 Claude Code and AI-assisted development

### The explanation

Claude Code is in my core skills, and I use it exactly as roles like Fornax describe — driving multi-file changes and reviewing the output critically, not accepting it blindly. I treat generated code as a draft to verify against reality and tests. My LLM-engineering background makes me a better critical reviewer, because I've built tools whose whole job is catching where models go wrong.

### The terms

- **Critical review** — Treating AI-generated code as a draft to verify — correctness against the real requirement, codebase consistency, security, missing edge cases — not accepting because it looks right.
- **Multi-file agentic editing** — The AI making coordinated changes across many files from a high-level instruction. Higher review burden — I review the whole diff as one unit, like a colleague's PR.
- **Verification** — Running and testing AI-generated code, not just checking it compiles-looking. "Looks right" isn't "works" — LLMs produce confident, subtly-wrong code.
- **Hallucinated APIs** — AI inventing plausible-but-nonexistent functions/libraries or, in my domain, keyword names it doesn't know. The exact failure the RF generator's templates avoid.
- **AI-assisted review** — Using AI to critique a system's design and find edge cases (EMS's consultation surfaced prompt injection, encoding issues). A thinking tool, not just a typing tool.
- **Autocomplete vs agentic** — Autocomplete suggests the next block line-by-line; agentic editing makes coordinated multi-file changes. More automation means more, not less, review rigor.
- **Calibrated skepticism** — Knowing where to distrust AI output (invented APIs, plausible-wrong logic) because I built hallucination detectors and prompt-regression gates. The trained instinct for AI failure modes.

---

## 1.19 React and frontend integration

### The explanation

I build the React frontends for my own tools — EMS (chat UI, upload, polling) and the Financial Parser (Tailwind, Recharts, exports) — so I understand the API contract from both sides: I design the endpoint and consume it. I'm honest that TypeScript is working knowledge, not deep expertise, and that I'm a backend/AI engineer who's genuinely full-stack-capable, not a frontend specialist.

### The terms

- **State vs props** — State is owned and mutable by a component; props are passed in read-only from a parent. Data flows down via props, changes flow up via callbacks.
- **useMemo / useCallback** — Stabilize object/function references across renders so children don't re-render on unchanged data. The fix for jank from new inline references.
- **CORS (frontend side)** — The browser blocks cross-origin API calls unless the API allows the origin; Postman skips it, so "works in Postman, blocked in browser" means CORS. A common integration gotcha.
- **Polling** — The frontend POSTs, gets a job id, and polls a status endpoint until done — how EMS handles async CV processing without freezing the UI. The client side of the async-write pattern.
- **Closure staleness** — An async callback captures state at creation time, so during a loop it can use stale data. Fixed by snapshotting the value (`[...transactions]`) — a real Financial Parser bug.
- **Virtual DOM** — React's in-memory UI representation, diffed on state change to update only the changed real DOM nodes. Why stable keys and reference stability matter.
- **localStorage** — Browser key-value storage for preferences and non-sensitive local data (dark mode, the obfuscated API key). Not secure — honest about that for the API key.
- **State-machine UI** — Driving the UI from an explicit status value (idle→reading→ocr→extracting→complete) with an error branch. Cleaner than scattered boolean flags.
- **Vite** — A fast build tool with hot-module-reload and native ES modules, minimal config. The dev-loop upgrade over Create React App.
- **html2canvas** — Captures live DOM chart elements as images so jsPDF can embed them (it can't render React/SVG). How the Financial Parser puts charts in the PDF.

---

## 1.20 Git, Agile, code review, mentoring

### The explanation

Standard trunk-based flow — feature branch, small commits, PR, CI runs lint+tests, review, merge. Beyond participating, I authored Python code-review checklists at Nokia (thread safety, Docker) adopted as team standard (~25% quality improvement) and mentored 3 engineers to senior readiness plus 19 interns. My Agile record: zero missed deliveries under strict schedules on 5G Core testing.

### The terms

- **Merge vs rebase** — Merge preserves history with a merge commit; rebase replays commits for a clean linear history. Never rebase shared/pushed branches — it rewrites history for everyone.
- **git bisect** — A binary search over commits to find which one introduced a bug — O(log n) instead of checking every commit. Small focused commits make it precise.
- **git reflog** — A log of where HEAD has been, the safety net for recovering "lost" commits after a bad reset or rewrite. Local recovery.
- **Feature branch / PR** — Short-lived branch off main, merged back via pull request where CI runs and a teammate reviews. Nothing merges without checks and review.
- **CI gate** — Automated lint/tests/build on every PR that must pass before merge, so reviewers focus on design not catching a broken build. I extended this to gate prompt quality.
- **Trunk-based development** — Short-lived branches, integrate to main often, main always deployable. Avoids long-lived branch drift and painful merges.
- **Commit message** — A concise imperative subject (~50 chars) and, when the why isn't obvious, a body explaining the reasoning. Makes history bisectable and understandable later.
- **Scrum ceremonies** — Sprints, daily standups (blockers, not status theatre), planning, review/demo, retro. Work tracked as stories in JIRA.
- **Code-review checklist** — A codified standard for what good review looks like (thread safety, Docker best practices) that I authored and the team adopted. Turned individual judgment into team process.
- **Mentoring** — 1:1 review sessions transferring how to think, not just fixing code — mentored 3 mid-levels to senior and supervised 19 interns. You mentor by making your reasoning visible.

---

## 1.21 Node.js and AWS (honest scope)

### The explanation

At Abjayon I was a Node.js + AWS developer — integrated AppSync and AppFlow (15% data-retrieval improvement), built GraphQL + REST APIs, managed IAM roles. So my hands-on AWS is AppSync, AppFlow, IAM — I'm precise about that and don't claim the broader ECS/Lambda/Step Functions/Kinesis surface, which I understand as managed versions of patterns I've built (containers, state machines, object storage).

### The terms

- **AppSync** — AWS's managed GraphQL service — hosts the API, resolvers, real-time subscriptions. Where my GraphQL experience came from.
- **AppFlow** — A managed service moving data between SaaS apps and AWS without custom integration code. I used it to connect data pipelines.
- **IAM** — Identity and Access Management, controlling who/what can access which AWS resources. I managed IAM roles with least-privilege permissions — real hands-on AWS security.
- **Least-privilege** — Granting each role only the specific permissions it needs, nothing more. Limits blast radius if a credential is compromised — core cloud security.
- **Lambda** — Serverless event-driven functions, auto-scaling, pay-per-invocation. Trade-offs: cold starts, time/memory limits, statelessness. I map it to my event-driven/async experience.
- **ECS / Fargate** — Running Docker containers without managing servers. Since I containerize already, it's "run my existing containers, managed."
- **S3** — Durable, cheap object storage for files/media. The "store the asset in S3, metadata in Postgres" pattern I sketched for the ad-generation design.
- **Step Functions** — Orchestrates a workflow as a state machine of services with retries/error handling. Maps directly to my agent loop and NFTRACE's lifecycle state machines.
- **CloudWatch** — AWS monitoring — logs, metrics, alarms. The managed version of my structured-logging + RED-metrics + alerting approach.
- **API Gateway** — AWS's managed edge entry point — auth, rate limiting, routing, SSL. The managed version of the gateway pattern I built as FastAPI middleware.
- **Node.js event loop** — The same single-threaded non-blocking model as Python's asyncio; don't block the loop, use promises/async-await. My async understanding transfers directly.
- **Kinesis** — Managed high-throughput event streaming (producers → stream → consumers). An honest gap — I understand the concepts (partitions, consumer groups) but haven't run a streaming pipeline.

---

*End of Section 1 terms. Each skill: a plain statement of how I handle it, then a 2-line definition for every term I'll say — so I'm never caught on a word I used. Pair with [SECTION_2_TERMS.md](SECTION_2_TERMS.md) (gaps) and [SECTION_3_DEEP.md](SECTION_3_DEEP.md) (projects). The deeper problem→fix Q&A lives in [SECTION_1_QA.md](SECTION_1_QA.md).*

