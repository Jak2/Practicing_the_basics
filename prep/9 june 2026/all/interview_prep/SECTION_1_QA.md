# Section 1 — Matched Skills: 20 Real Interview Questions Per Topic

*This is the version that gets me past the interview. For every matched topic, 20 questions of the kind a team that actually runs this in production asks — the failures they hit, the fix they landed on, and the follow-up that separates "read a blog" from "shipped it." Answers are written the way I'd speak them, and I lead with the problem, not the definition.*

**Topics:** 1.1 Python · 1.2 FastAPI/REST · 1.3 asyncio · 1.4 Pydantic · 1.5 pytest/testing · 1.6 LangChain/RAG · 1.7 Vector DBs · 1.8 Prompt eng/eval/hallucination · 1.9 Agentic AI · 1.10 gRPC/microservices · 1.11 Redis/caching · 1.12 PostgreSQL/SQL · 1.13 SQLAlchemy/Celery/Streamlit/GraphQL · 1.14 Docker/K8s/CI-CD · 1.15 Auth/RBAC/security · 1.16 Doc ingestion/OCR · 1.17 LLM APIs/routing/economics · 1.18 Claude Code/AI-assisted dev · 1.19 React/frontend · 1.20 Git/Agile/mentoring · 1.21 Node.js/AWS

---

## 1.1 Python (core language)

**Q1. Your service handles 50 concurrent requests fine, then falls over at 200. CPU is low, memory is fine. What's happening?**
Almost always blocking I/O on the event loop or thread starvation, not raw resource limits. If it's an async service, something synchronous — a `requests.get()`, a `time.sleep`, a sync DB driver — is inside an `async def` and stalling the whole loop; every request queues behind it. If it's threaded, the thread pool is exhausted because each request holds a thread while waiting on I/O. Fix: move blocking calls off the loop (`httpx.AsyncClient` or a threadpool via `run_in_executor`), and size the pool for I/O wait, not CPU.

**Q2. A background job processes a 2-million-row query and the box OOMs. The code "looks fine." What's the bug?**
It's materialising the whole result set into a list — `rows = cursor.fetchall()` or `list(query)` — so 2M rows sit in memory at once. The fix is a generator / server-side cursor: iterate row by row with `yield`, so memory stays flat regardless of table size. I've used exactly this pattern for large query processing — the difference is holding one row versus 4GB.

**Q3. Two engineers debug a function where a default list "remembers" values between calls. What did they hit?**
The mutable default argument trap — `def f(x=[])`. The list is created once at function definition and shared across every call, so it accumulates state. The fix is `def f(x=None)` and create a fresh list inside. The nastier cousin is the same bug as a class attribute — `class Foo: items=[]` is shared across all instances; you fix it by initialising in `__init__` with `self.items=[]`.

**Q4. When does threading actually help in Python, given the GIL?**
For I/O-bound work. A thread releases the GIL while it waits on network or disk, so other threads run — you get real concurrency for waiting, just not for CPU. For CPU-bound work threading buys nothing because only one thread runs bytecode at a time; there you use multiprocessing to get separate interpreters and true parallelism. The one-liner: I/O → threads or async, CPU → multiprocessing.

**Q5. You need to start captures on 8 machines at the exact same instant. Threads or processes? Why?**
I used `multiprocessing.Pool.starmap` for this in NFTRACE. If you start sequentially you miss the opening messages on the later nodes — they must fire simultaneously. Threads would be gated by the GIL during the Python-side work, and the XML-RPC client I was calling was synchronous anyway; multiprocessing gives true parallel execution across cores with the standard library, no async dependency.

**Q6. `is` vs `==` — give me a bug this causes.**
`==` compares value, `is` compares identity (same object in memory). The classic bug is `if x is True` or comparing small integers/strings with `is` and relying on interning — it works by accident for cached small ints and breaks for larger ones. Rule: `==` for value comparison, `is` only for singletons like `None`.

**Q7. How does Python free memory, and what does reference counting miss?**
Primarily reference counting — each object tracks its references, freed at zero. It misses reference cycles (A points to B, B points to A) because their counts never reach zero; that's why CPython also runs a cycle-detecting garbage collector. Practical consequence: a big object graph with cycles won't free on the spot — it waits for a GC pass.

**Q8. What's a decorator and where have you used one that mattered?**
A function that wraps another to add behaviour without touching its code. Real uses: `lru_cache` for memoising an expensive pure function (I cache the sentence-transformer model load as a process-level singleton this way), retry wrappers, timing/logging, and FastAPI's `Depends` under the hood. The mental model: `@d` means `func = d(func)`.

**Q9. Context managers — why not just call `.close()`?**
Because `.close()` doesn't run if an exception fires between open and close — you leak the resource. `with` guarantees cleanup via `__enter__`/`__exit__` even on error. I use them for DB sessions, files, and locks — anything that must be released. You can build one quickly with `@contextlib.contextmanager` and a `yield`.

**Q10. Generator vs list comprehension — when does the choice actually bite you?**
When the dataset is large or infinite. A list comp builds everything in memory; a generator produces on demand. It bites when someone writes `[x for x in huge_query]` and OOMs, or iterates a generator twice expecting data the second time (generators exhaust). If you need to reuse the results, materialise once; if you're streaming, keep it lazy.

**Q11. A colleague's code does `for i in range(len(items)): items.append(...)`. What breaks?**
Mutating a list while iterating over indices tied to its length — the loop can run forever or skip elements. General rule: don't mutate a collection you're iterating. Iterate a copy (`items[:]`) or build a new list. Same class of bug with modifying a dict during iteration, which actually raises `RuntimeError`.

**Q12. What's the difference between shallow and deep copy, and when did it matter?**
Shallow copy duplicates the top container but shares nested objects; deep copy recurses. It matters when I snapshot state before an async loop — in the Financial Parser I did `currentTransactions = [...transactions]` (JS equivalent) precisely to avoid the shared-reference/closure-staleness bug where the async processing mutated the data mid-flight. In Python that's `copy.copy` vs `copy.deepcopy`; a shallow copy of a list of dicts still shares the dicts.

**Q13. How do you handle configuration and secrets in a Python service?**
Never hardcoded, never committed. Environment variables loaded through `pydantic-settings` into a typed, validated Settings object, cached with a single `get_settings()`. Secrets come from the environment or a secret manager at runtime — not baked into the image (that's visible in `docker history`). One source of truth, type-checked at startup so a missing var fails fast instead of at 3am.

**Q14. `*args`/`**kwargs` — legitimate use vs code smell?**
Legit for decorators and wrappers that must forward arbitrary arguments transparently, and for genuinely variadic APIs. Smell when they hide a function's real signature — you lose type hints, IDE help, and validation, and callers can't tell what's accepted. I keep public function signatures explicit and reserve `**kwargs` for pass-through.

**Q15. What's an f-string gotcha you've actually hit?**
Curly-brace escaping when the output itself needs literal braces — in the RF generator, Robot Framework uses `${var}` syntax, and inside a Python `.format()`/f-string template you must double them to `${{var}}` or the formatter tries to interpolate and throws `KeyError`. Forgetting it silently produces malformed output. It's a real bug I designed around.

**Q16. Type hints — do they do anything at runtime?**
Not by themselves — CPython ignores them at runtime; they're for tooling (mypy, IDEs) and documentation. The exception is libraries that *read* them: Pydantic and FastAPI use hints to actually validate and coerce data at runtime. So the same annotation is inert on a plain function but load-bearing on a Pydantic model field.

**Q17. How do you make an expensive computation run once and be reused across a process?**
`functools.lru_cache` (or `@cache`) for a pure function keyed by arguments, or a module-level singleton loaded lazily on first use. I lazy-load the sentence-transformer model this way — first call pays ~0.5s, every subsequent call is instant, and I don't import torch on startup for services that may never need it. The key is *lazy* — don't pay the cost until something actually needs it.

**Q18. Exception handling — what's the anti-pattern you look for in review?**
Bare `except:` or `except Exception: pass` that swallows everything, including the errors you needed to see, and hides bugs. I want narrow exceptions, logging with context, and re-raising or converting to a domain error. In the RF generator the LLM-JSON parse is wrapped in a *specific* `json.JSONDecodeError` catch that falls back to regex — targeted, not a blanket swallow.

**Q19. Walk me through the difference between `@staticmethod`, `@classmethod`, and an instance method.**
Instance method takes `self` and works on the instance. `@classmethod` takes `cls` and is the idiomatic way to write alternative constructors (`from_config`, `from_existing_collection` — LangChain's Qdrant store uses exactly this). `@staticmethod` takes neither — it's a plain function namespaced on the class, for logically-related helpers that don't touch instance or class state.

**Q20. How do you profile a slow Python function before optimising it?**
Measure first — `cProfile` for where time goes, `line_profiler` for hotspots inside a function, `tracemalloc` for memory. The rule is don't guess: I've seen people "optimise" a loop that was 2% of runtime while a synchronous network call in the middle was 90%. Profile, find the real cost, fix that, re-measure to confirm.

---

## 1.2 FastAPI and REST API design

**Q1. Your team ships `async def` endpoints and everything freezes under load even though the code is "async." First thing you check?**
Whether a *blocking* call snuck into an async endpoint — `requests`, a sync DB driver, `time.sleep`, a heavy CPU loop. One blocking call in `async def` stalls the entire event loop, so every concurrent request waits. It passes local testing with one user and dies at 50. Fix: `httpx.AsyncClient` and an async DB driver, or make the endpoint plain `def` so FastAPI runs it in a threadpool.

**Q2. When do you deliberately use `def` instead of `async def` in FastAPI?**
When the work is blocking and I can't make it async — a sync-only library, CPU-bound work. FastAPI runs plain `def` endpoints in a threadpool, so they don't block the loop. The mistake is the middle ground: `async def` that then calls blocking code. So it's async endpoint + async libraries, or sync endpoint for blocking work — never mix.

**Q3. You have a `yield`-based DB session dependency and a BackgroundTask that uses it. Users report intermittent "session closed" errors. Why?**
The `yield` dependency's cleanup runs at response time, which is *before* the BackgroundTask executes — so the session is already closed when the task tries to use it. This is a classic FastAPI gotcha. Fix: don't pass the session into the task; pass the plain data the task needs, and open a fresh session inside the task if it must hit the DB.

**Q4. The React team says "auth calls are being blocked" but unauthenticated calls work. What's your first guess?**
CORS on the preflight. Two usual suspects: `Authorization` isn't in `allow_headers`, so the OPTIONS preflight passes but the real authenticated request fails silently; or someone set `allow_origins=['*']` with `allow_credentials=True`, which browsers reject outright. I check those two before anything else — it's almost always one of them.

**Q5. How does `Depends` actually help beyond "less code"?**
Testability is the real win. My DB-session and current-user logic live in dependency functions, so in tests I override them — swap the real DB for a test one, inject a fake user — without touching endpoint code. It also centralises cross-cutting concerns (auth, pagination params) so they're written once and reused, and it makes the dependency graph explicit.

**Q6. A validation error returns a 422 with an ugly nested body the frontend can't parse consistently. How do you fix it across the whole API?**
Register a custom exception handler for `RequestValidationError` (and for my `HTTPException`s) so every error comes back in one shape — an `error` object with a code and a message. The frontend then handles errors uniformly instead of special-casing each endpoint. Consistency of the error contract is as important as the success contract.

**Q7. How do you structure a FastAPI app so it doesn't become one 4000-line file?**
Layers: `APIRouter` per domain, Pydantic schemas separate from ORM models, a services layer for business logic, a database layer with sessions and Alembic migrations, and a core module for config and security. Config from env via `pydantic-settings`. I learned the cost of *not* doing this from EMS, where the chat handler grew to 4400 lines because every query type needed its own path — that's the anti-pattern.

**Q8. Someone requests a 100,000-row list endpoint and the API times out. Fix?**
Pagination — never return unbounded lists. Offset/limit or, better, keyset (cursor) pagination for large tables since offset gets slow deep into the data. Add filtering and sorting via query params so the client fetches only what it needs, and cache hot pages. The API contract should make it impossible to ask for everything at once.

**Q9. How do you keep a FastAPI service responsive when one endpoint does slow work?**
Don't do the slow work in the request. Validate, enqueue it on Celery, return a job ID immediately (202-style), and let the client poll a status endpoint or receive a webhook. The API stays fast, and I scale the workers independently of the web tier. I've built exactly this for slow processing pipelines.

**Q10. How do you scale a FastAPI service horizontally?**
Keep it stateless so any instance handles any request — that means JWT auth over server-side sessions, and no local in-memory state that a second instance wouldn't see. Then run multiple Uvicorn workers under Gunicorn to use all cores, put it behind a load balancer, pool DB connections, cache hot reads in Redis, and push heavy work to a queue. Statelessness is the enabler for everything else.

**Q11. Rule of thumb for worker count, and how do you refine it?**
Start around 2 × CPU cores + 1, then measure. If workers spend most time blocked on I/O, you can add more; if they're CPU-saturated, more workers just add context-switching overhead and don't help. It's measure-driven, not a fixed number — the starting formula is only a starting point.

**Q12. How do you test a FastAPI app without spinning up a real server?**
`TestClient` (or `httpx.AsyncClient` for async) calls endpoints in-process. I override dependencies to swap the real DB for a test DB and mock external services, so tests are fast and deterministic. Shape: mostly fast unit tests on the service layer, some integration tests through the API, a few end-to-end.

**Q13. FastAPI, Flask, or Django — defend your default.**
FastAPI for API services: async-native on ASGI, Pydantic validation and OpenAPI docs for free. Flask is lighter but synchronous with no built-in validation/docs; Django is batteries-included and great for CRUD-with-admin but heavier than a pure API needs and synchronous-first. I pick Django when I actually want the ORM/admin/templates; otherwise FastAPI.

**Q14. What does `response_model` buy you, and what's the trap?**
It validates and *filters* the response to the declared schema — so internal fields (a password hash, internal flags) don't leak even if your ORM object has them. The trap is assuming it validates input too; it's the response contract. Also, returning a field the model doesn't declare silently drops it, which can confuse the frontend if the schema drifts from intent.

**Q15. How do you version an API so you don't break existing consumers?**
A `/v1` prefix (URL versioning is the simplest and most explicit), and never make breaking changes within a version — add fields, don't remove or repurpose them. When a breaking change is unavoidable, ship `/v2` and keep `/v1` alive during migration. FastAPI's auto-generated OpenAPI docs give each version a live contract.

**Q16. What are idempotent methods and why does it matter for retries?**
GET, PUT, DELETE are idempotent — doing them twice has the same effect as once; POST isn't. It matters because clients and load balancers retry on network failures — a retried POST can double-charge or double-create. For non-idempotent mutations I take an idempotency key from the client and check it atomically (Redis `SETNX`) so a retry is a no-op.

**Q17. How do you handle a slow or flaky third-party API from inside your endpoint?**
Timeout on every outbound call so it can't hang my service; retries with exponential backoff and jitter for transient failures; a circuit breaker to stop hammering a dependency that's down; and a graceful fallback so a failure degrades instead of cascading. I did exactly this with an LLM API — a regex fallback kept a tool at 100% uptime when the model call failed.

**Q18. Middleware vs dependency — when do you reach for each?**
Middleware wraps every request/response for truly cross-cutting concerns — request-ID injection, timing, global logging, CORS. Dependencies are per-endpoint and can return values into the handler — auth, DB sessions, pagination. Rule: if it needs to produce a value the endpoint uses, it's a dependency; if it's a blanket wrap with no return into the handler, it's middleware.

**Q19. How do you stream a large or long-running response instead of buffering it?**
`StreamingResponse` with an async generator that yields chunks — for large file downloads or, importantly, for LLM token streaming via SSE so the user sees output as it's generated instead of waiting for the full completion. My endpoints are already async, so swapping a buffered call for a streamed generator is a bounded change (this is my one honest streaming gap I'm closing).

**Q20. What's the single most common API security bug you actively look for?**
Broken object-level authorization (BOLA) — the code authenticates correctly (valid JWT, real user) but never checks the user actually *owns* the resource. `GET /orders/{id}` verifies the token but not that the order belongs to this user, so any authenticated user reads anyone's data. It's OWASP's top API risk, and the fix is an ownership check on every resource access, not just an auth check.

---

## 1.3 Async programming (asyncio)

**Q1. You fire 500 LLM calls with `asyncio.gather` and immediately get rate-limit errors. Fix?**
Cap concurrency with an `asyncio.Semaphore`. `gather` launches all 500 at once and blows the provider's limit instantly. I wrap each call in `async with semaphore:` so only N (say 10) are in flight at a time — enough to stay fast, few enough to stay under the quota. I use this exact pattern in the bias auditor: a 100-variant × 5-run audit is 500 calls, and the semaphore is the only thing keeping it alive.

**Q2. What actually happens at an `await` point?**
The coroutine yields control back to the event loop instead of blocking. The loop is free to run other ready tasks; when the awaited I/O completes, the loop resumes this coroutine where it left off. That cooperative yielding is why one thread can juggle thousands of in-flight I/O operations — nothing sits blocked.

**Q3. Async is single-threaded — so how does it give concurrency without the GIL fight?**
Exactly because it's single-threaded and cooperative. You're not running Python bytecode in parallel, so the GIL is irrelevant; you're interleaving *waiting*. While one task waits on the network, others run. That's why async is ideal for I/O-bound work and useless for CPU-bound work — there's no parallel computation, just no idle waiting.

**Q4. A CPU-heavy function inside an async handler tanks throughput. Why, and what do you do?**
Because it never hits an `await`, so it never yields — it monopolises the single event-loop thread and every other task stalls until it finishes. Async only helps when tasks yield at I/O. For CPU work, offload to a process pool (`run_in_executor` with a `ProcessPoolExecutor`) or a separate worker so the loop stays free.

**Q5. `asyncio.gather` vs `asyncio.as_completed` — when does the choice matter?**
`gather` waits for all and returns results in order — good when you need everything. `as_completed` yields results as each finishes — good when you want to process the fastest responses first or show progressive results. Also watch `gather`'s error behaviour: by default one exception cancels the rest; `return_exceptions=True` lets the rest finish and hands you the exceptions to inspect.

**Q6. One task in a `gather` throws and silently kills the batch. How do you make it robust?**
`return_exceptions=True` so `gather` collects exceptions instead of cancelling the whole group, then I inspect each result and handle failures individually. For fan-out over many LLM calls that's essential — one malformed response shouldn't lose the other 499. It mirrors what I do in the eval framework: one judge failure returns an error result, the suite continues.

**Q7. Why is `asyncpg` the choice over `psycopg2` in an async FastAPI app?**
`psycopg2` is synchronous — calling it in an async handler blocks the event loop, defeating the whole point. `asyncpg` is async-native (and the fastest Postgres driver), so DB waits yield to the loop like any other I/O. I pair it with SQLAlchemy 2.0 async so the ORM layer is non-blocking end to end.

**Q8. How do you put a hard timeout on an async operation?**
`asyncio.wait_for(coro, timeout=...)` or `async with asyncio.timeout(...)`. Never let an outbound call hang forever — a slow dependency shouldn't be able to tie up a task indefinitely. On timeout I catch `TimeoutError` and apply the fallback/retry policy. Every external await in production gets a timeout.

**Q9. Connection pool sized at 10, but under load you get "pool exhausted." What went wrong?**
More concurrent tasks are holding connections than the pool has slots — often because a task acquires a connection and then does something slow (an LLM call, external I/O) while holding it. Fix: size the pool for real concurrency (I run pool_size 10 + overflow 5), and don't hold a DB connection across a long non-DB await — acquire late, release early.

**Q10. What's `run_in_executor` for?**
Running blocking code from an async context without stalling the loop — it hands the work to a thread (or process) pool and awaits the result. I use it to call a sync-only library or CPU work from inside an async handler. Threadpool for blocking I/O, process pool for CPU-bound, so the GIL doesn't bottleneck the CPU case.

**Q11. Why can't you just call an `async def` function normally?**
Calling it returns a coroutine object; it doesn't run until awaited or scheduled on the loop. A frequent bug is forgetting the `await` — the coroutine is created, never executed, and you get a "coroutine was never awaited" warning with silently missing work. Every async call needs `await` or `asyncio.create_task`.

**Q12. `await`ing tasks sequentially vs concurrently — show the difference.**
`await a(); await b()` runs them one after another — total time is the sum. `await asyncio.gather(a(), b())` runs them concurrently — total time is roughly the slowest. People accidentally write the sequential version in a loop and wonder why "async" is slow; the fix is to create the tasks first, then gather. Concurrency only happens when multiple awaitables are in flight together.

**Q13. How do you run a background task in asyncio and not lose it?**
`asyncio.create_task` schedules it, but you must keep a reference — if the task object is garbage-collected, the task can be cancelled mid-flight. For anything that must survive a restart, asyncio background tasks aren't enough; that's exactly why I use Celery for durable work in the eval framework. In-process async tasks are fire-and-forget within one process only.

**Q14. What's a race condition in async code if it's single-threaded?**
It's not a data race on CPU, but you can still corrupt shared state across `await` points — task A reads a value, awaits (yielding to task B, which modifies it), then resumes with a stale value. The fix is an `asyncio.Lock` around the read-modify-write, or designing so shared mutable state isn't touched across awaits. Single-threaded doesn't mean interleaving-safe.

**Q15. When would you pick threading over asyncio for I/O?**
When the libraries I must use are synchronous and there's no async equivalent — threads let blocking calls run without me rewriting everything to async. Asyncio needs the whole call chain to be non-blocking; if a key dependency is sync-only, threads (or `run_in_executor`) are more pragmatic. In NFTRACE I used multiprocessing for parallel sync XML-RPC precisely because the client was sync.

**Q16. How do you cancel an in-flight async operation cleanly?**
`task.cancel()` raises `CancelledError` inside the coroutine at its next await; I catch it to release resources (close connections, roll back) and then re-raise so cancellation actually propagates. The anti-pattern is swallowing `CancelledError`, which leaves the task running when the caller thinks it's gone. Cleanup on cancel, then let it propagate.

**Q17. What's backpressure and how do you apply it in async fan-out?**
Backpressure is limiting how fast you accept/dispatch work so you don't overwhelm a downstream. The Semaphore is the simplest form — it bounds in-flight work. For streaming producers/consumers, bounded `asyncio.Queue`s apply backpressure: producers block when the queue is full. Without it, an async system will happily launch a million tasks and exhaust memory or a downstream quota.

**Q18. Async context managers — when do you actually need `async with`?**
When setup/teardown themselves do I/O — opening an async DB session, an `httpx.AsyncClient`, an async lock. `async with` awaits `__aenter__`/`__aexit__` so the acquire/release don't block the loop. I use `async with client:` for the HTTP client so connection pooling is set up and torn down without blocking.

**Q19. You mix sync and async DB calls and get subtle bugs. What's the guidance?**
Don't mix in the same path. Pick async end-to-end (async engine, asyncpg, async sessions) or sync end-to-end; a sync session inside an async handler blocks the loop, and an async session used without `await` silently does nothing. I keep a service either fully async or fully sync at the data layer, not half-and-half.

**Q20. Give me a concrete before/after where async changed real performance.**
The bias auditor and eval framework: the workload is hundreds of independent LLM calls that each spend seconds waiting on the network. Sequentially that's minutes; with async + semaphore-bounded `gather` it's the slowest-few calls' worth of time — a 6–8× speedup on a mixed batch — while staying under the provider's rate limit. Pure I/O-bound fan-out is the textbook case where async pays off, and it did.

---

## 1.4 Pydantic (v2)

**Q1. Your LLM returns "almost JSON" and your pipeline crashes 15% of the time. How does Pydantic fit the fix?**
Pydantic is the validation gate *after* I salvage the JSON, not the salvage itself. In EMS raw Ollama output failed to parse 10–20% of the time, so the flow is: multi-strategy parse (direct → regex extraction → key-value fallback) to get *a* dict, then Pydantic validates it against the employee schema and coerces types; if it fails (e.g. name missing), I retry the LLM. Pydantic turns "maybe-valid dict" into "guaranteed-shape object or a clear error before the DB write."

**Q2. What does Pydantic v2 do at runtime that plain type hints don't?**
Type hints are inert at runtime; Pydantic *reads* them and actually validates and coerces incoming data, raising structured errors on mismatch. So `age: int` on a plain function does nothing, but on a Pydantic model it rejects or coerces `"42"`. That's the whole reason it's the backbone of FastAPI request/response handling.

**Q3. v1 to v2 — what actually changed that matters?**
v2's core is rewritten in Rust, so validation is roughly 10× faster — meaningful when you validate every request and every LLM output. API changes I watch for: `@validator` → `@field_validator`, `@root_validator` → `@model_validator`, `.dict()` → `.model_dump()`, `Config` class → `model_config`. It's a breaking upgrade, so I don't mix v1/v2 patterns in one model.

**Q4. How do you validate a field against another field — cross-field rules?**
`@model_validator(mode="after")` — it runs once the individual fields are validated and sees the whole model, so I can enforce invariants like "end_date must be after start_date" or "if type is X, field Y is required." I used this pattern in the prompt-regression suite for parse-time invariants. Single-field constraints go on `Field` or a `@field_validator`.

**Q5. Where does Pydantic sit in your architecture beyond request bodies?**
Three places: FastAPI request/response models, schema enforcement on LLM JSON before persistence, and typed configuration via `pydantic-settings` loading env vars into a validated Settings object. The config use is underrated — a missing or malformed env var fails at startup with a clear message instead of blowing up in production at request time.

**Q6. What's the "universal contract" pattern and why is it powerful?**
One Pydantic model consumed by every layer with zero translation. In the bias auditor `BiasReport` is consumed by the CLI, REST API, Streamlit dashboard, and PDF generator — add a field once and it propagates to all consumers, and any type mismatch is caught at validation time, not silently at runtime. It kills a whole class of "the API and the UI disagree about the shape" bugs.

**Q7. `Field` — give me constraints you actually use.**
`min_length`/`max_length` on strings, `ge`/`le` for numeric ranges (a score must be 0–1), `default`/`default_factory` (use `default_factory=list` — never a mutable default), and `alias` for mapping an external key name to a clean field name. Constraints live on the model so validation is declarative, not scattered `if` checks in the handler.

**Q8. How do you enforce that an LLM returns *only* JSON and nothing else?**
Two layers: instruct the model (system prompt: "return ONLY the JSON object, begin with `{`") and validate defensively. In the prompt-regression judge the prompt ends with "begin your response with the opening brace" because free-text preamble like "Sure, here's my evaluation: {" is a common silent failure — constraining the start makes any malformed response immediately detectable. Then Pydantic validates the parsed result.

**Q9. Pydantic model vs dataclass — when each?**
Dataclass for a plain internal data holder with no validation need — it's lighter, standard library. Pydantic when the data crosses a trust boundary (request body, LLM output, config from env) and must be validated/coerced. Rule: untrusted input or serialization → Pydantic; trusted internal struct → dataclass.

**Q10. `model_dump()` vs `model_dump_json()` — and a serialization gotcha?**
`model_dump()` gives a dict, `model_dump_json()` gives a JSON string. The gotcha is types JSON doesn't natively support — `datetime`, `Decimal`, `UUID`, enums — where `model_dump()` may keep Python objects but the JSON path serialises them; I make sure the output shape matches what the consumer expects. Also `by_alias=True` when the external contract uses aliased names.

**Q11. How do you handle optional vs required fields cleanly?**
Required = annotate the type with no default. Optional = `Optional[X]` (or `X | None`) with a default. The subtlety: `Optional[X]` without a default is still *required but nullable* — the client must send it, even if null. I'm explicit about "may be omitted" (has a default) vs "may be null" (Optional) because frontends trip on the difference.

**Q12. A field should accept multiple input types and normalise them. How?**
A `@field_validator` that coerces — e.g. accept a string or list for a "tags" field and always store a list, or parse a date from several formats into a `date`. Pydantic does basic coercion automatically (`"42"` → `42`); the validator is for domain-specific normalisation the built-in coercion won't do.

**Q13. How do you catch and surface validation errors usefully?**
`ValidationError` carries structured, per-field detail. In the prompt-regression registry I catch it *per file* during load — an invalid YAML is logged with the full error and skipped, and the rest of the suite still runs. The principle: one bad input shouldn't crash the batch; validate, isolate the failure, report it precisely, continue.

**Q14. What's `ConfigDict`/`model_config` used for?**
Per-model behaviour: `extra="forbid"` to reject unexpected fields (strict contracts), `frozen=True` for immutability, `populate_by_name` to accept both field name and alias, `str_strip_whitespace`. I use `extra="forbid"` on external-facing models so a typo'd field name is a loud error rather than silently ignored.

**Q15. How do you validate deeply nested data — a list of objects inside an object?**
Compose models — the outer model has a field typed as `list[InnerModel]`, and Pydantic validates recursively all the way down. The employee model in EMS does this: work_experience and education are lists of structured sub-objects, each validated. Nested validation is free once the models are composed; you don't hand-write the recursion.

**Q16. Coercion can be dangerous — where does automatic type coercion bite?**
When it silently accepts something you meant to reject — `"1"`/`"true"` coercing to `bool`, or a float truncating. In v2 you can opt into strict mode (`Strict` types or `model_config strict=True`) so `"42"` is rejected for an `int` field rather than coerced. For financial or safety-critical fields I go strict; for lenient user input I let coercion help.

**Q17. How do settings management with pydantic-settings actually work in practice?**
A `BaseSettings` subclass declares typed fields; it reads from environment variables (and `.env`) and validates them into one object, cached via `lru_cache` so it's parsed once. Every module calls `get_settings()`. Benefits: no scattered `os.getenv`, typed and validated at startup, and secrets/config in one auditable place.

**Q18. Computed/derived fields — how do you expose a value calculated from others?**
`@computed_field` with a property so it's included in serialization, or a `@model_validator(mode="after")` that sets a derived field. Example: expose `overall_passed` derived from individual evaluator results (AND logic) rather than trusting an input value. Deriving on the model keeps the invariant in one place instead of recomputing in every consumer.

**Q19. You need the same model with slightly different rules for input vs output. Approach?**
Separate models — an input/create model (client sends, no server-set fields) and a response model (includes server-generated fields like id/timestamps, excludes secrets). FastAPI's `response_model` filters output to its schema. Trying to make one model do both leads to optional-everything soup and accidental field leakage.

**Q20. Give me a real bug Pydantic caught that would've reached production otherwise.**
LLM output shape drift. When a model update subtly changed a returned key or nested a field differently, Pydantic validation failed loudly at the boundary instead of writing malformed data to the DB and surfacing as a mystery bug days later. That "fail at the edge with a precise field error" behaviour is exactly why I validate every LLM output — it converts silent data corruption into an immediate, located error.

---

## 1.5 pytest and testing discipline

**Q1. How do you test code that calls an LLM, given the output is non-deterministic?**
Don't assert exact strings. I mock the LLM client for unit tests so the response is fixed and I test *my* logic — parsing, fallback, validation — deterministically. For the model itself I don't unit-test its wording; I test behaviour with tolerant assertions (valid JSON, required keys present, score in range) and push quality checks into a separate eval suite. The prompt-regression suite exists precisely because you test prompt *quality* differently from code logic.

**Q2. Your tests pass locally and fail in CI. Common causes you check?**
Hidden dependencies on local state: a real DB or Redis that's absent in CI, environment variables not set, timezone/locale differences, test-order dependence (a test that only passes because a previous one left state), and network calls that aren't mocked. Fix: hermetic tests — spin up ephemeral services or mock them, set env explicitly, and make each test independent so order doesn't matter.

**Q3. What's a fixture and how do you avoid fixture-induced coupling?**
A fixture provides setup/teardown and shared test dependencies (a test DB session, a client, sample data). The coupling trap is a big "god fixture" every test depends on, so one change breaks hundreds of tests. I keep fixtures small and composable, scope them appropriately (`function` for isolation, `session` for expensive shared setup), and use `yield` fixtures so teardown always runs even on failure.

**Q4. How do you structure tests for a FastAPI service?**
Three levels. Unit tests on the service layer with external deps mocked. Integration tests through the API with `TestClient`/`httpx`, overriding the DB dependency to a test DB and mocking third parties. A few end-to-end against a real stack. Most tests are fast unit tests; the expensive ones are few. That's the shape I used for NFTRACE and the RF generator.

**Q5. You mock the database in a test and the test passes, but the code breaks in prod. What went wrong?**
Over-mocking — you mocked the thing you were supposed to test, so the test verified the mock, not reality. If the bug is in the actual query/ORM behaviour, a mocked DB won't catch it. Fix: integration-test the data layer against a real (test) database — SQLite or a disposable Postgres — for anything where the DB behaviour itself matters.

**Q6. How do you test the *failure* paths, not just the happy path?**
Deliberately inject failures. In the RF generator I fed the RF-parser validation deliberately-broken templates to confirm it *rejects* them — testing that the guardrail works, not just that valid input passes. I test timeouts, malformed LLM JSON (does the regex fallback fire?), DB errors, and unauthorized access. The failure paths are where production breaks, so they need the most tests.

**Q7. `pytest.mark.parametrize` — when does it earn its keep?**
When one logic path has many input/output cases — boundary values, each enum variant, valid/invalid combinations. In the RF generator I parametrized entity extraction with IMSI at the start/middle/end of the string and with none present, so one test function covers all edge cases cleanly instead of copy-pasted tests. It also makes each case a separately-named failure so you see exactly which input broke.

**Q8. How do you handle tests for async code?**
`pytest-asyncio` with `async def` tests and an `httpx.AsyncClient` for async endpoints. The gotcha is forgetting the async plumbing and having the coroutine never awaited, so the test passes without actually running anything. I make sure the async fixtures and client are set up so awaits genuinely execute.

**Q9. What's the difference between a mock, a stub, and a fake, and when do you use each?**
A stub returns canned values; a mock also asserts it was called correctly (interaction testing); a fake is a working lightweight implementation (in-memory DB, mock XML-RPC server). In NFTRACE I used a *fake* — mock XML-RPC servers — plus synthetic pcap fixtures, because I wanted realistic behaviour, not just canned returns. I reach for a fake when interaction with a real-ish component matters, a stub when I just need a value.

**Q10. How do you decide what NOT to test?**
Third-party library internals, trivial getters, and framework behaviour I don't own. I test *my* logic and my integration points, not that FastAPI routes or that Pydantic validates — those are the framework's tests. Chasing 100% coverage on trivia wastes time; I aim coverage at business logic, edge cases, and failure handling.

**Q11. Your test suite is slow and people stop running it. How do you fix that?**
Separate fast from slow: unit tests run on every save, integration/e2e run in CI or on demand (markers like `@pytest.mark.slow`). Parallelise with `pytest-xdist`. Mock network/LLM calls in the fast tier so nothing waits on I/O. The goal is a sub-second inner loop; if the fast suite takes minutes, people skip it and it stops protecting you.

**Q12. How do you test something that depends on the current time or a UUID?**
Inject them or freeze them — pass a clock/id generator as a dependency, or use `freezegun`/monkeypatch to pin `datetime.now()` and seed/patch UUID generation. Hidden calls to `now()` and `uuid4()` make tests non-deterministic and flaky. Making time and identity injectable is the clean fix.

**Q13. What's flakiness, and how did you handle it in an LLM context?**
A flaky test passes and fails without code changes — usually from nondeterminism, shared state, or timing. For LLM output specifically, I don't assert exact text; and in the prompt-regression suite I run each case multiple times and flag std-dev > 0.05 as flaky rather than treating a single noisy score as signal. You handle LLM flakiness statistically, not with one brittle assertion.

**Q14. How do you test a background/Celery task?**
Test the task function directly as a plain function with its inputs — the task logic is separate from the queue. For integration, run Celery in eager mode (`task_always_eager`) so it executes synchronously in-process, or test enqueue-and-poll against a test broker. I keep the business logic in a testable function and the task as a thin wrapper.

**Q15. `conftest.py` — what belongs there?**
Shared fixtures and hooks available across a test directory without importing — the test DB session, the app client, common sample data, and plugin config. It's the place for cross-test setup. I keep it lean; a bloated conftest becomes the god-fixture problem where everything implicitly depends on it.

**Q16. How do you get meaningful coverage without gaming the metric?**
Coverage tells you what's *unexecuted*, not what's *well-tested* — you can hit 100% and assert nothing. I use it to find untested branches (especially error paths), not as a target to chase. A line executed by a test with no meaningful assertion is coverage theatre; I look for tested behaviour, not just touched lines.

**Q17. How did you test NFTRACE's distributed pieces?**
Layered. Unit tests for each component: Redis ops against a test Redis, SQLite CRUD, NodeManager against mock XML-RPC servers, the validator against synthetic pcap fixtures with known content. Integration tests with `httpx` through the full FastAPI stack — start a session, assert Redis state, simulate a node, stop/merge/validate, check SQLite history. And real-node end-to-end runs weekly in the pipeline. You can't unit-test real telecom nodes, so you fake them and reserve real hardware for scheduled e2e.

**Q18. How do you test error handling for a flaky third-party API?**
Mock the client to raise/timeout on cue, then assert my retry, backoff, circuit-breaker, and fallback logic behave — e.g. after N failures the circuit opens, or the regex fallback produces a valid result when the LLM call raises. I test the resilience machinery deterministically by controlling the failure, which you can't do against the real flaky service.

**Q19. TDD — do you actually use it, and where does it fit?**
Where the spec is clear and logic-heavy — parsers, validators, scoring functions — writing the failing test first sharpens the contract and gives instant regression protection. Where I'm exploring an unknown (a new LLM prompt, an integration I don't fully understand yet), I spike first then backfill tests. It's a tool, not a religion: TDD for well-specified logic, exploratory for the fuzzy edges.

**Q20. How do you test that a prompt change didn't silently degrade quality — the thing unit tests can't catch?**
That's exactly what the Prompt Regression Suite does. Each prompt gets a YAML behavioural test suite; every change runs tiered assertions (deterministic rules → semantic similarity → LLM judge) and compares the score against a stored baseline. If it drops more than the delta threshold, the PR is blocked. Unit tests verify logic; this verifies *meaning* — the silent-shortening or citation-drop failures that pass every normal test and only surface as user complaints.

---

## 1.6 LangChain and RAG (end-to-end)

**Q1. A team's RAG gives confident but wrong answers. How do you diagnose whether it's retrieval or generation?**
Separate the two with evaluation — this is the single most useful RAG debugging move. I score faithfulness (did the answer stay inside retrieved context) against accuracy. High faithfulness + wrong answer means the retriever fed bad or incomplete documents — fix chunking/retrieval. Low faithfulness means the model is ignoring the context and answering from parametric memory — context leakage, fix the prompt/grounding. Without that split you're guessing; with it you know which half to fix.

**Q2. Walk me through your RAG pipeline end to end.**
Knowledge base of ~200 curated 5G error patterns, each an embeddable text plus metadata (vendor, layer, severity, fix). At query time: extract the error, embed it, do a *filtered* semantic search in Qdrant (vendor + layer filter before ranking), pull top-5, feed them via LangChain RetrievalQA to Claude with `return_source_documents=True`, and Claude synthesises a contextual fix. Then a separate eval layer scores faithfulness and hallucination. Chunk → embed → store → retrieve → generate → evaluate, all in production.

**Q3. Why LangChain RetrievalQA instead of calling the vector DB and the LLM directly?**
Three concrete wins: `return_source_documents=True` gives me *which* patterns matched, not just the answer — critical for engineer trust when they're about to act on it; one-line swappability of vector store and LLM (I tested FAISS before settling on Qdrant, a one-line change); and clean prompt-template management. The trade-off I name: LangChain hides the final assembled prompt, so I run `verbose=True` in dev to see exactly what Claude receives, and turn it off in prod.

**Q4. Chunking — your answers miss information that's clearly in the docs. What's likely wrong?**
Bad chunk boundaries splitting a coherent unit, or chunks too small to hold the answer, or no overlap so context is lost at the seam. Fixed 500-char chunks (what I used in EMS) can slice mid-sentence; the upgrade is structure-aware chunking that splits on headings/sections so each chunk is a self-contained idea, with overlap (100 chars) to preserve context across boundaries. Chunking quality is often the real bottleneck people blame on the model.

**Q5. How do you decide chunk size and overlap?**
Trade-off between precision and context. Small chunks = precise retrieval but may lack surrounding context; large chunks = more context but noisier embeddings and you retrieve irrelevant text alongside the relevant. I start around 500 chars with ~20% overlap and tune against retrieval quality on real queries. There's no universal number — it depends on document structure and query type, so I measure retrieval hit-rate rather than guess.

**Q6. Why did you return source documents, and what does it change operationally?**
Trust and debuggability. An ops engineer is about to restart a service based on the suggested fix, so they need to see *why* — "based on pattern AUTH_TIMEOUT_T3560, matched at 0.94 similarity" — not a black box. Operationally it also gives me the debugging signal from Q1: I can see whether the right documents were retrieved, which tells me if a bad answer is a retrieval or generation problem.

**Q7. Embeddings — how do you choose a model, and does dimension matter?**
Match the model to the domain and cost. I've used OpenAI embeddings (1536-dim) and local `all-MiniLM-L6-v2` (384-dim, 80MB, ~5ms, zero API cost). Higher dimensions can capture more nuance but cost more storage and compute; for regression-detection and semantic comparison the small local model is accurate enough and far cheaper. Critically, the embedding model that indexed the data must be the one that embeds the query — mismatched models produce garbage similarity.

**Q8. What breaks if the query embedding model differs from the indexing model?**
The vectors live in different spaces, so cosine similarity is meaningless — you get random-looking retrievals even for obviously relevant queries. It's a subtle, silent failure: no error, just bad results. I make the embedding model a single config value used for both indexing and querying so they can't drift apart.

**Q9. Your knowledge base grows and retrieval quality drops. What levers do you pull?**
Add metadata filtering to shrink the search space to the relevant subset (my Qdrant vendor/layer filter), add a reranker so a cross-encoder re-scores the top-50 down to a precise top-5, move to hybrid retrieval (BM25 + dense) so exact identifiers aren't missed, and tighten chunking. More data means more noise, so the fix is better *precision* mechanisms, not just a bigger index.

**Q10. How do you handle a query that has no good match in the knowledge base?**
Threshold on similarity and refuse to hallucinate. In the 5G pipeline, below 0.65 similarity I return "unknown — manual review required" instead of generating a fix from a bad match, and I log those unknowns so the team can add new patterns — the system improves with use. Returning a confident answer from a 0.4-similarity match is worse than admitting there's no known pattern.

**Q11. What's the "stuff" chain type and when does it break?**
"Stuff" puts all retrieved docs into one prompt — simplest and what I use with top-5. It breaks when retrieved context exceeds the model's context window (too many or too large chunks), at which point you truncate and lose information silently. Alternatives are map-reduce or refine chains that process docs in batches, at higher cost/latency. I keep top-k small enough to fit rather than reaching for those.

**Q12. How do you evaluate a RAG system's quality, concretely?**
Golden question set with known answers, run through faithfulness (grounded in context) and hallucination (claims supported by reference) evaluators, plus retrieval hit-rate (did the right doc come back at all). The combination localises problems: high faithfulness + high hallucination-vs-reference means the retrieved docs are wrong; low faithfulness means the model bypasses retrieval. That's my LLM-eval framework applied to RAG.

**Q13. Why did LangChain make swapping FAISS for Qdrant a one-line change, and why does that matter?**
Because the vector store sits behind a common retriever interface — `QdrantVectorStore.from_existing_collection(...).as_retriever()` vs the FAISS equivalent, and the chain doesn't care which. It matters because during development I could A/B the two without rewriting the pipeline; I chose Qdrant for metadata filtering after actually comparing. Abstraction that lets you defer and revisit infrastructure decisions is worth the dependency.

**Q14. What's the risk of LangChain hiding the prompt, and how do you manage it?**
When fix quality was poor, I couldn't immediately see what text Claude received because the chain assembled it internally. The fix is `verbose=True` in development to print the exact assembled prompt, then disable in production. I treat the hidden prompt as a debugging blind spot to be turned on when needed, not a reason to avoid the abstraction.

**Q15. How do you keep RAG costs down at scale?**
Model routing (cheap model for easy cases, strong model for hard — Haiku vs Sonnet cut my cost ~60%), local embeddings instead of paid ones where accuracy allows, caching frequent lookups in Redis, and a similarity threshold so I don't spend a generation call on a no-match. Cost discipline in RAG is mostly "don't call the expensive model or API when you don't have to."

**Q16. Temperature for a RAG answer — what do you set and why?**
Low — I used 0.1 for the 5G fixes. The answer must be consistent and grounded, not creative: same input, same fix. Higher temperature introduces variation that's fine for writing but wrong for operational or factual output where two different answers to the same question erode trust. For grounded RAG I want near-deterministic.

**Q17. How does the LLM add value over just returning the top retrieved document?**
The retrieved document is generic — written for the general case. The LLM contextualises it to the specific instance (this timing, this node, this retry count), synthesises across multiple partially-matching patterns, and phrases it as an actionable step. Concretely: the raw doc says "check timer T3560"; Claude says "this fired at 1s during a traffic spike, the UE was likely on poor signal — increase to 3s and monitor." Same source, far more actionable.

**Q18. Multi-hop questions — how would you handle "compare X's approach with Y's"?**
Decompose into sub-queries, retrieve for each, then synthesise — the same compound-query decomposition I built in EMS for CRUD ("what does John know and compare with Sarah's DevOps"). Single-shot retrieval on a multi-hop question retrieves for a blurred average of both and misses each. Break it, retrieve per sub-question, aggregate. For deeper multi-hop, Graph-RAG traversal is the next step.

**Q19. How do you keep the knowledge base fresh without re-indexing everything?**
Incremental upserts — embed and add only new/changed patterns rather than rebuilding the whole collection (my `/index` endpoint re-indexes on demand). Capture novel cases automatically: unknowns that fall below threshold get logged, reviewed, and added as new patterns, so the KB grows from real gaps. Full re-index only when the embedding model or chunking strategy changes.

**Q20. If you were told "just fine-tune the model on our docs instead of RAG," how would you respond?**
Push back with the trade-offs. RAG injects knowledge at inference — cheap to update (add a document), transparent (you see the sources), and no training pipeline. Fine-tuning bakes knowledge into weights — expensive, opaque, and stale the moment the docs change; you'd retrain on every update. Fine-tune for *behaviour/format/style*, RAG for *knowledge*. For a docs-QA system that changes over time, RAG is almost always the right call — and I've shipped it, so I can speak to why.

---

## 1.7 Vector databases (Qdrant, FAISS)

**Q1. Your RAG returns semantically similar but wrong-context results — e.g. a competitor's fix for your vendor's error. Root cause and fix?**
Pure semantic search with no metadata filtering. Nokia and Ericsson errors are semantically similar but the fixes are vendor-specific and not interchangeable. The fix that made this production-grade: Qdrant's `must` filter on vendor and layer, which runs *at the database level before* similarity ranking, so only same-vendor vectors are even considered. FAISS can't do this natively — you'd filter in Python after retrieving, so wrong-vendor patterns are still in the ranking and can win.

**Q2. Why Qdrant over FAISS, Chroma, and pgvector — defend the choice.**
The decisive requirement was metadata filtering at the DB level. FAISS has no native filtering — filter post-retrieval in Python, so you search the whole corpus first. Chroma filters, but post-retrieval, less production-ready. pgvector would mean adding Postgres purely for vector search — infra I didn't need. Qdrant is purpose-built, filters before ranking, runs as a Docker container with a persistent volume. Faster and never surfaces a cross-vendor result.

**Q3. Why cosine similarity and not dot product or Euclidean distance?**
Cosine measures the angle between vectors, ignoring magnitude. A terse "T3560 timeout" and a verbose paragraph describing the same error point the same direction but have different magnitudes — cosine scores them as highly similar, Euclidean would penalise the length difference. For text similarity where the same meaning comes in different lengths, cosine is correct. Dot product conflates magnitude with relevance unless vectors are normalised.

**Q4. What does the similarity score threshold do and how did you pick it?**
Below the threshold, the match is too weak to trust. I set 0.65 — below it I return "unknown, manual review" rather than generating a fix from a poor match, because a low-similarity match plus generation produces hallucinated advice. I picked it empirically against real errors: high enough to reject noise, low enough not to discard genuine matches. It's the guardrail that stops confident-but-wrong output.

**Q5. When is FAISS the *right* choice over Qdrant?**
When you don't need metadata filtering, you're single-node and in-memory, and you want zero infrastructure. EMS uses FAISS for exactly this — employee semantic search on one machine, no vendor/layer filtering, no server to run. FAISS is a library, not a service; for a simple local index it's the leaner choice. I match the tool to the requirement rather than always reaching for the heavier DB.

**Q6. What's HNSW and what knobs would you tune?**
Hierarchical Navigable Small World — the graph-based approximate-nearest-neighbour index most vector DBs use. Key params: `M` (edges per node — higher improves recall but costs memory), `ef_construction` (build-time thoroughness — higher = better index, slower build), and `ef_search` (query-time candidates — higher = better recall, higher latency). Tuning trades recall against speed and memory. I've used it at Qdrant defaults; tuning these is the lever when recall or latency isn't meeting target.

**Q7. Approximate vs exact nearest neighbour — what are you giving up?**
Exact search compares the query to every vector — perfectly accurate, but O(N) and too slow at scale. ANN (HNSW) trades a small amount of recall for massive speed by searching a navigable graph instead of the whole set. You might occasionally miss a true top-k result, but at millions of vectors it's the only practical option. For most RAG the recall loss is negligible against the latency win.

**Q8. How does metadata filtering interact with ANN performance?**
This is the subtlety. Naive post-filtering retrieves top-k by similarity then drops non-matching — but if the filter is selective, you might retrieve k results and have none survive the filter. Qdrant does filtered search properly at the DB level, constraining the candidate set to matching payloads before/within the ANN traversal. That's why "only Nokia NAS vectors are even considered" — it's not filter-after, it's filter-aware search.

**Q9. Your vector collection grew to millions and latency climbed. Options?**
Horizontal scaling — Qdrant supports sharding/distributed deployment, so I shard the collection to keep per-node search fast. Also: tighten `ef_search` vs recall, use metadata filters to shrink the effective search space, and quantize vectors (e.g. scalar/product quantization) to cut memory and speed search at a small accuracy cost. The 5G pipeline's scale-out plan was exactly Qdrant sharding as the pattern count grew.

**Q10. What metadata do you store alongside vectors and why?**
In the 5G collection: the embeddable text (what's compared), vendor/layer/severity (the filter fields), error_code (canonical id), and the known fix, protocol, component. The filter fields enable pre-ranking constraints; the fix is stored *and* included in the retrieved text so Claude refines a known fix rather than starting from scratch. Metadata is what turns a similarity engine into a filtered, context-rich retriever.

**Q11. How do you keep the index in sync when the source data changes?**
Upsert by stable ID — re-embedding and upserting changed records rather than rebuilding, and deleting vectors when the source is deleted (EMS removes an employee's vectors from FAISS on delete). The consistency risk is a write to the primary DB succeeding while the vector upsert fails, leaving them out of sync — a real distributed-systems problem I flag, ideally handled with a transaction or a reconciliation job.

**Q12. Pinecone vs Weaviate vs Milvus — how do you reason about them without having shipped all three?**
On a few axes: managed vs self-hosted (Pinecone is fully managed/serverless; Weaviate/Milvus/Qdrant self-hostable), native hybrid support (Weaviate and OpenSearch do BM25+dense in one engine), scale ceiling (Milvus targets billions, GPU indexing), and whether vectors sit beside relational/keyword data (pgvector in Postgres, OpenSearch alongside BM25). Because I chose Qdrant *specifically for filtering* over the alternatives, I can place any of them on those axes even where I haven't run them.

**Q13. When would you actually pick pgvector?**
When you're already on Postgres, scale is moderate, and you want vectors transactional and co-located with relational data — one database, ACID, no extra service. The "why not pgvector" I answered for the 5G pipeline was "no Postgres in that stack, adding it just for vectors is unnecessary infra" — but flip that (already on Postgres, moderate scale) and pgvector becomes the pragmatic choice.

**Q14. How do you handle multi-tenancy in a vector store?**
Metadata filtering on a tenant_id — every vector carries its tenant, every query filters to it at the DB level, so tenants never see each other's data. This is the same mechanism as my vendor filter, applied to isolation. For strong isolation or very large tenants you might use separate collections per tenant; for many small tenants, a shared collection with a mandatory tenant filter is efficient.

**Q15. What's the cost of embedding everything, and how do you control it?**
Embedding a large corpus with a paid API is a real cost and a recurring one on re-index. I control it by batching embeds (embed many texts per call, not one-by-one), using a local model (`all-MiniLM-L6-v2`) where API-grade accuracy isn't needed, and only re-embedding changed records. In the 5G indexer I batch-embed all patterns at once precisely because per-item calls are wasteful.

**Q16. How do you verify retrieval quality, not just that it returns *something*?**
A labelled query set with known-correct documents, measuring recall@k (is the right doc in the top-k) and precision. If recall is low, the problem is embeddings/chunking/index; if recall is fine but answers are wrong, it's generation. I tie this into the eval framework so retrieval quality is a measured number, not a vibe.

**Q17. Cross-encoder reranking — where does it sit and why bother?**
After first-stage vector retrieval. The bi-encoder (embeddings) is fast but coarse — it embeds query and doc separately. A cross-encoder reads query and doc *together* and scores relevance precisely, but it's slow, so you only run it on the top-50 candidates to pick a precise top-5. It's the highest-ROI RAG precision upgrade; I haven't shipped it but I know exactly where it slots into the pipeline I built.

**Q18. What happens to similarity search when vectors aren't normalised?**
Dot-product similarity gets dominated by vector magnitude rather than direction, so longer/denser texts score artificially high regardless of relevance. Cosine implicitly normalises (it's magnitude-invariant), which is one reason I chose it. If you use dot product you must normalise vectors first; forgetting to is a subtle relevance bug.

**Q19. How do you decide top-k?**
Trade-off between recall and prompt size/noise. Too small and you miss relevant context; too large and you stuff the prompt with noise, raise cost, and risk exceeding the context window. I used k=5 for the 5G pipeline — enough to synthesise across patterns, small enough to fit the "stuff" chain. I'd tune k against answer quality on real queries rather than fix it arbitrarily.

**Q20. A stakeholder says "vector search is just fuzzy keyword search." How do you correct that?**
Keyword search matches tokens; vector search matches *meaning*. "T3560 timer expired" and "NAS authentication timeout after registration" share almost no keywords but describe the same error — keyword search misses it, semantic search finds it because their embeddings point the same direction. The flip side is exact identifiers (an error code) where keyword/BM25 is actually better — which is why hybrid retrieval combines both. They're complementary, not the same thing.

---

## 1.8 Prompt engineering, evaluation, and hallucination detection

**Q1. A prompt that scored 92% last month is silently at 61% now with no code change. What happened and how would you have caught it?**
Model provider drift — the provider updated the base model behind the same endpoint, and behaviour shifted without any changelog. You catch it with a scheduled evaluation against the live model, not PR-triggered tests, because drift doesn't arrive in a PR — it arrives through the API. My prompt-regression suite runs a weekly full-suite drift monitor for exactly this, alerting on the worst-regressing case before users file tickets.

**Q2. How do you measure hallucination concretely, not hand-wavily?**
Decompose the response into atomic factual claims, classify each against a reference as SUPPORTED, UNSUPPORTED, or CONTRADICTED, then score = 1 − (unsupported + contradicted)/total. That gives a number with an explanation, not a vibe. It requires a reference or context to check against; if neither is provided the evaluator skips with a neutral pass rather than guessing.

**Q3. Explain faithfulness vs accuracy — why does the distinction matter?**
Faithfulness = did the answer stay inside the retrieved context, independent of whether the context was correct. Accuracy = is the answer actually true. They diverge usefully: high faithfulness + wrong answer means your retriever fed bad docs (fix retrieval); low faithfulness means the model ignored the retriever and used parametric memory — context leakage (fix grounding/prompt). Measuring both localises the failure to retrieval vs generation, which accuracy alone can't do.

**Q4. How do you stop an LLM judge from being biased toward its own outputs?**
Never let a model judge its own family. In the prompt-regression suite the judge is always a *different provider* than the model under test — claude-* models are judged by OpenAI, gpt-* by Anthropic — and it's enforced structurally at construction time in the runner, not documented as a guideline. A model grading its own generation style systematically favours responses that match its own patterns; cross-provider judging removes that.

**Q5. Your LLM-as-judge reports an "overall" score that doesn't match its own dimension scores. What do you do?**
Discard the model's reported overall and recompute it client-side from the dimension scores and fixed weights. LLM arithmetic is unreliable — it'll score instruction_following 0.9 and factual_accuracy 0.2 and then report 0.82. I never trust the model's math for a gating decision; I take its judgments per dimension and compute the weighted score myself. That's a real safety measure in the suite.

**Q6. How do you make an LLM reliably return only JSON?**
Constrain and detect. Instruct it explicitly ("return ONLY the JSON object, begin your response with `{`"), because free-text preamble — "Sure, here's my evaluation: {" — is a common silent failure; forcing the first character to be a brace makes any violation immediately detectable. Use the provider's JSON/structured-output mode where available (`responseMimeType: application/json`). Then parse defensively with a fallback, because it'll still occasionally break.

**Q7. What's a hallucination that's invisible to a naive "is this true?" check?**
RAG context leakage. The answer is factually correct — because the model's training data happens to agree — but it isn't grounded in the retrieved context; the retriever never returned it. A truth-check passes, but the system is fabricating grounding, which fails the moment the answer *should* have come from context that says otherwise. That's why I measure faithfulness (stayed in context) separately from accuracy (true).

**Q8. How do you test whether a prompt is *reliable*, not just correct once?**
Consistency checking — run the same prompt N times at temperature 0.7 and compute mean pairwise cosine similarity across responses. A prompt can score well on a single judge run and still be unreliable, giving structurally different answers on consecutive calls (one mentions a key fact, another omits it). Below the similarity threshold it's flagged INCONSISTENT. Single-run scoring hides this whole class of failure.

**Q9. How do you turn prompt quality into a CI gate that blocks bad merges?**
Each prompt gets a version-controlled YAML behavioural test suite; a PR that touches a prompt runs the affected tests, scores them, and compares against a stored baseline. If the score drops more than the delta threshold, the workflow exits non-zero and the merge is blocked, with a PR comment showing current vs baseline and the judge's verdict. It's unit-testing for meaning, wired into GitHub Actions.

**Q10. Why delta-based regression against a baseline instead of a fixed pass threshold?**
Fixed thresholds break as prompts improve — a prompt that legitimately improves from 0.82 to 0.91 should ratchet its baseline up, and a fixed cutoff can't tell improvement from noise. Delta compares against the stored baseline: regression fires only on a drop relative to the known-good score. Baselines update automatically on merge to main (improvements recognised) and never on PR runs (so regressions aren't forgotten mid-review). Absolute score level doesn't matter; the *drop* does.

**Q11. How do you control the cost of running an LLM judge on every test?**
Tiered, fail-fast assertions. Cheap deterministic rules first (keyword, JSON validity — zero cost), then local semantic similarity (~5ms, zero API cost), and the paid judge *only* if the cheaper tiers pass. A test that fails a keyword check costs zero API budget. Across a mixed suite that's ~50% cost reduction. The judge is the last resort, not the first check.

**Q12. Zero-shot vs few-shot vs chain-of-thought — when do you reach for each?**
Zero-shot for simple, well-understood tasks (extraction, classification the model already handles). Few-shot when the task needs a specific format or edge-case handling the model won't infer — I show 2-3 examples. Chain-of-thought ("think step by step") when the task needs multi-step reasoning and the intermediate steps improve the answer. I default to the cheapest that works — zero-shot — and add examples or reasoning only when quality demands it, because they cost tokens.

**Q13. How do you write a prompt that's robust to weird user phrasing?**
Give the model a clear role, the exact output schema, explicit rules ("return null for missing fields, don't invent values"), and let it handle the natural-language variation — that's what LLMs are good at, versus regex which breaks on unseen phrasing. In the RF generator the LLM extractor handles "mobile identity" = IMSI and "subscriber wants to authenticate" that regex missed. And I keep a deterministic fallback for when the model still fails.

**Q14. How do you evaluate quality across five dimensions instead of one number?**
A rubric — in the eval framework the judge scores accuracy, relevance, completeness, clarity, and safety, each 1-5, normalised to 0-1. Different dimensions catch different failures: accuracy catches factual errors, safety catches harmful output, completeness catches under-answering. A single "quality" score averages these and can mask a critical failure — which is why I also flag `critical_failure` if any single dimension drops below a hard floor regardless of the average.

**Q15. A response scores 0.75 overall but is factually wrong. How does your system not pass it?**
Two mechanisms. AND logic on multi-evaluator pass — a response that's well-written and relevant but hallucinates a fact fails because the hallucination evaluator fails independently, and any single failure blocks the case; no averaging rescues it. And a critical-failure flag — if factual_accuracy alone drops below 0.40, it's flagged regardless of the weighted overall. A quality gate must not let a high average paper over a critical dimension.

**Q16. How do you reduce hallucination in a production system, in order of what you'd try?**
Ground it: RAG with good retrieval so the model answers from provided context, and a prompt that says "answer only from the context, say you don't know otherwise." Lower temperature for factual tasks. Return sources so it's checkable. Add a faithfulness evaluator to catch context leakage. Threshold retrieval so a no-match returns "unknown" instead of fabrication. I reach for grounding and refusal-on-no-match before anything exotic — most hallucination is ungrounded generation.

**Q17. What's prompt injection and how do you defend against it in an agent/tool system?**
When user input contains instructions that hijack the prompt ("ignore previous instructions and..."). Defenses: separate system instructions from user content clearly, treat retrieved/user text as data not instructions, validate and constrain tool inputs, least-privilege on what tools can do, and never let model output directly trigger a dangerous action without validation. In EMS the anti-hallucination guards and the AI-consultation review specifically surfaced prompt-injection as an edge case to handle.

**Q18. How do you A/B two prompts objectively instead of arguing about which "feels" better?**
Submit both as separate test cases with the same evaluators; the one with higher judge scores and lower consistency variance is objectively better. This removes subjective debate from prompt engineering — it becomes a measured comparison. My eval framework's use case for this is exactly A/B prompt comparison; the numbers settle it.

**Q19. How do you build a golden test set for prompt evaluation?**
A fixed set of representative prompts with known-good reference answers, covering the common cases and the known failure modes (the silent-shortening, citation-drop, tone-drift patterns). It's version-controlled alongside the prompts. On every change I run the golden set; on a schedule I run it against the live model for drift. The set is the shared, auditable definition of "good enough to ship" — without it, quality is opinion.

**Q20. You built prompt assembly for a real agent loop — what goes into a production system prompt?**
At Brane the assembly was: the system prompt (role and rules), grounded input injection (anchor the agent to real data so it doesn't free-associate), tool-registry context (what it can call and how), and retry-with-feedback construction for the verifier correction loop (on failed validation, feed the failure back and re-prompt). The non-obvious part is the correction loop — the prompt isn't static, it's reconstructed with the verifier's feedback so the agent self-heals rather than failing outright. Production prompting is assembly and iteration, not one clever string.

---

## 1.9 Agentic AI (agent loop, tool-calling)

**Q1. Your agent occasionally loops forever calling the same tool. How do you stop it?**
A hard step/recursion cap on the loop plus a stop condition in the routing logic. At Brane the verifier correction loop had a retry cap — after N failed attempts it stops and surfaces the failure rather than looping. In graph terms it's a conditional edge that must eventually route to "finish"; without a bound, a model that keeps deciding to call a tool never terminates. Cap the iterations, define the exit, and treat hitting the cap as a handled outcome, not a crash.

**Q2. Walk me through what actually happens in one iteration of an agent loop.**
Assemble the prompt (system + grounded input + tool-registry context + history), send to the model, parse its output. If it requested a tool, invoke the tool, capture the result, feed it back into context, and loop. If it produced a final answer, validate it — and if validation fails, reconstruct the prompt with the failure feedback and retry (the verifier loop). Exit when the answer validates or the step cap is hit. That's the plan→act→observe→decide cycle I built.

**Q3. The model returns "almost JSON" for a tool call and your parser crashes. How do you harden it?**
Defensive parsing plus a correction loop. At Brane I hardened the response parser for malformed LLM output — strip code fences, extract the outermost braces, tolerate common malformations — and when it still fails, the verifier loop feeds the parse failure back to the model to retry. Malformed output isn't an edge case, it's constant, so the parser assumes imperfection and the loop provides a second chance rather than failing the whole run.

**Q4. How do you give an agent memory across steps and across runs?**
Two layers. Within a run, the conversation/scratch state accumulates in the prompt context. Across steps and for durability, persist it — at Brane `agent_run_scratch` and `agent_episodes` in PostgreSQL are effectively a hand-rolled checkpointer, storing working state and episodic history so a run is resumable and inspectable. In-memory context alone dies on restart; persisting state is what makes an agent durable and auditable.

**Q5. What's a tool registry and why not just hardcode the tools in the prompt?**
The registry is the structured catalog of what the agent can call — each tool's name, purpose, and input schema — injected into context so the model knows its options and how to call them. Decoupling it from the prompt means you add or remove a tool without rewriting the loop, and you can scope which tools an agent gets. At Brane the tool-registry context was a distinct assembly step, and I also cut tool-invocation overhead — the registry is data, the loop is logic.

**Q6. How does a verifier/correction loop work and why is it worth the extra calls?**
After the agent produces output, a verifier checks it (schema valid? constraints met?); on failure, instead of returning garbage, it reconstructs the prompt with the specific failure as feedback and re-prompts. It's self-healing — the agent fixes its own mistake using concrete feedback rather than a vague retry. The extra calls buy reliability: the difference between an agent that fails 15% of the time and one that recovers most of those failures. You cap the retries so it can't loop.

**Q7. Single agent vs multi-agent — when is multi-agent actually justified?**
When the task genuinely decomposes into specialised, independently-verifiable subtasks — a planner, a researcher, a critic — where specialisation plus review beats one giant prompt. It's *not* justified for most tasks: multi-agent multiplies token cost, latency, and failure surface (inter-agent loops, shared-state consistency). My honest position — I built a single-agent loop at Brane — is start single-agent with good tools, and reach for multi-agent only when the decomposition is real. I won't oversell multi-agent I haven't shipped.

**Q8. How do you handle a tool call that fails or times out mid-loop?**
Timeout on the tool call, catch the failure, and feed it back into the loop as an observation the agent can react to — retry, try an alternative tool, or degrade gracefully — rather than crashing the whole run. It's the same resilience I apply to any external call: timeout, retry with backoff, fallback. The agent should treat a tool failure as information to act on, not a fatal error.

**Q9. What's human-in-the-loop and where would you insert it?**
Pausing the agent at a decision point for human approval before a consequential or irreversible action — a payment, a delete, a production change. You checkpoint the state, surface the proposed action, and resume on approval. It's the safety valve for autonomous agents: full autonomy for reversible low-stakes steps, human gate for high-stakes ones. My state-persistence work is exactly what makes pausing and resuming possible.

**Q10. How do you evaluate whether an agent is actually doing a good job?**
Agent output is itself an evaluation problem — this is where my eval background directly applies. I'd measure task success rate on a golden set of tasks, faithfulness/correctness of the final answer, tool-call accuracy (did it call the right tool with right args), step efficiency (did it solve it in reasonable steps or thrash), and cost per task. Judging a multi-step agent needs the same rubric-and-golden-set discipline as judging a single prompt, applied to the trajectory not just the answer.

**Q11. How do you keep agent costs from exploding?**
Cap steps (each step is tokens), route to cheaper models for simple sub-decisions and the strong model only where reasoning is needed, cache tool results and repeated sub-queries, and trim the context you carry forward rather than re-sending the whole history every step. An unbounded agent is a cost incident waiting to happen — the step cap and model routing are the primary levers, the same routing discipline I used in the 5G pipeline.

**Q12. How does the model actually "decide" to call a tool?**
Via structured tool/function-calling — the model is given the tool schemas and, instead of prose, emits a structured call (tool name + arguments) that your loop detects and executes. Modern APIs support this natively (function calling / tool use). The routing logic then branches: tool call → invoke and loop; final answer → validate and finish. The registry provides the schemas; the model chooses; your loop dispatches.

**Q13. What did the gRPC model gateway do for the agent runtime?**
It was the inferencing layer — the agent loop called models through a gRPC gateway that did multi-provider routing across instruct, thinking, and vision variants, stateless so it scaled horizontally. The value is decoupling: the agent loop asks for "a thinking-model completion" and the gateway routes to the right provider/variant, so the agent isn't wired to a specific vendor. Provider changes and horizontal scaling happen at the gateway, not in the loop.

**Q14. How do you ground an agent so it doesn't confidently make things up?**
Grounded input injection — anchor the agent to real, retrieved data in the prompt and instruct it to work from that, not free-associate. Combined with the verifier loop (validate output) and tool results feeding back as ground truth, the agent's decisions are tied to actual data. Ungrounded agents hallucinate steps and facts; the fix is the same as RAG — provide and enforce context.

**Q15. Planning vs reactive agents — what's the difference?**
A reactive agent decides one step at a time based on the latest observation (ReAct-style: reason, act, observe, repeat). A planning agent first produces a multi-step plan, then executes it, possibly re-planning on failure. Reactive is simpler and robust to surprises; planning is better for complex tasks with dependencies but can commit to a bad plan. Many production agents are reactive with a bounded loop — which is essentially what I built, with the verifier providing the re-plan-on-failure behaviour.

**Q16. How do you make an agent's behaviour reproducible for debugging?**
Persist the full trajectory — every prompt, tool call, and observation (my `agent_episodes`/`agent_run_scratch` do this), and pin temperature low for the decision steps. When something goes wrong you replay the episode and see exactly what the agent saw and chose. Without persisted trajectories, agent bugs are unreproducible ghosts; with them, debugging is reading the trace.

**Q17. What's the biggest reliability risk in an agent system and how do you mitigate it?**
Compounding errors — a wrong step early leads to wrong observations that lead to more wrong steps, and it snowballs. Mitigations: the verifier loop catches bad output before it propagates, grounding keeps steps anchored to real data, step caps limit how far a bad trajectory runs, and human-in-the-loop gates the irreversible actions. You assume any single step can be wrong and build checks so one error doesn't cascade into a ruined run.

**Q18. How would you add a new capability (tool) to an existing agent?**
Define the tool function and its input schema, register it in the tool registry, and — if it does anything sensitive — scope which agents/roles can use it (RBAC). The loop needs no change because it's registry-driven. That's the payoff of decoupling tools from the loop: extending capability is adding data + a function, not rewriting the agent. At Brane the registry and attribute-level RBAC together governed exactly this.

**Q19. How do you handle concurrency — many agent runs at once — safely?**
Isolate each run's state under a unique id (like NFTRACE's per-session Redis keys), make the inference layer stateless so it scales horizontally (the gRPC gateway), and ensure shared resources (DB, tools) handle concurrent access. Attribute-RBAC caching at Brane kept per-run permission checks fast under concurrency. The pattern is the same as any concurrent backend: isolate mutable state per run, keep the hot path stateless, guard shared resources.

**Q20. Honestly, where's the line between what you've built and what these agentic JDs ask for?**
I've built the *primitives* in production — tool-calling, prompt assembly, a verifier/self-healing loop, durable state persistence, RBAC-governed tool access, and a multi-provider gRPC inference gateway — on a single-agent runtime. What I haven't shipped is multi-agent orchestration or the named frameworks (CrewAI, AutoGen, LangGraph). But multi-agent is composing single agents under a supervisor, and I own every building block plus the evaluation skill to judge whether the composition works. That's the honest, defensible position — deep on the fundamentals, framework-adjacent, and fast to close the gap.

---

## 1.10 gRPC and microservices

**Q1. Why did you use gRPC for the model gateway instead of REST?**
It's internal service-to-service inferencing, which is exactly gRPC's sweet spot: binary protobuf over HTTP/2, strongly typed via a schema, low serialization overhead, and streaming support. REST/JSON's human-readability and universality don't buy you anything between two internal services, and the JSON overhead is pure cost on a hot inference path. So REST for public/browser-facing, gRPC for high-performance internal calls — and the model gateway was internal.

**Q2. What does the protobuf schema buy you over a JSON contract?**
A strongly-typed, versioned contract enforced at both ends — the client and server generate code from the same `.proto`, so a shape mismatch is a compile-time error, not a runtime surprise. JSON contracts drift silently until something breaks in production. Protobuf is also compact on the wire and fast to serialize. The trade-off is you need the schema and codegen step, and it's not human-readable in transit.

**Q3. gRPC runs on HTTP/2 — why does that matter?**
HTTP/2 gives multiplexing (many concurrent calls over one connection without head-of-line blocking), binary framing, and bidirectional streaming. For a model gateway handling many concurrent inference requests, multiplexing over a persistent connection is far more efficient than REST's connection-per-request-ish model. Streaming over HTTP/2 is also what makes gRPC good for token-streaming-style workloads.

**Q4. When would you NOT use gRPC?**
Public or browser-facing APIs — browsers can't speak raw gRPC without a proxy (grpc-web), and external consumers expect REST/JSON. Also when human-readability and easy debugging with curl matter, or when the ecosystem you're integrating with is REST-only. gRPC shines internally between services you control; at the edge, REST is usually the right call.

**Q5. Your gateway needs to scale — how do you design it?**
Stateless, so you scale horizontally behind a load balancer — which is exactly how I built the Brane gateway: stateless multi-provider routing so any instance handles any request. State (sessions, history) lives elsewhere (DB/Redis), not in the gateway. gRPC load balancing needs L7 awareness (HTTP/2 connections are long-lived, so naive L4 balancing pins traffic) — a gRPC-aware proxy or client-side balancing distributes properly.

**Q6. Monolith or microservices for a new product — what's your honest default?**
Start with a modular monolith and split only when there's a concrete reason — different scaling needs, different deployment cadence, or different team ownership. The real cost of microservices nobody mentions in interviews is distributed transactions, cross-service debugging, and data consistency across boundaries. I've seen teams go microservices-first and spend six months building service mesh and tracing instead of the product. Split when justified, not by default.

**Q7. How do services communicate in a microservices setup, and how do you choose?**
Synchronous (REST for external, gRPC for internal high-performance) or asynchronous (message queue — RabbitMQ, Kafka, Redis — via events). Sync is simple and direct but couples availability (if the callee is down, the caller fails). Async decouples, absorbs spikes, and lets you retry, at the cost of eventual consistency and more moving parts. I use sync for request/response that needs an immediate answer, async for work that can be decoupled or is spiky.

**Q8. Two services need the same data and it's getting inconsistent. What patterns help?**
Own-your-data (each service owns its data, others ask via API, no shared DB), and for consistency across a workflow, the saga pattern (a sequence of local transactions with compensating actions on failure) instead of a distributed transaction. The outbox pattern reliably publishes events: write the DB change and the outbound event in one local transaction, and a poller publishes the event, so you don't lose events if the broker is down. Distributed data consistency is the hard part of microservices — these are the tools.

**Q9. How do you handle a downstream service being slow or down?**
Timeout on every call, retry with exponential backoff and jitter for transient failures, and a circuit breaker that opens after N consecutive failures so you fail fast instead of stacking requests and exhausting your own resources. Plus graceful degradation — return partial or cached results rather than cascading the failure. I apply this to any external dependency, LLM APIs included, where a regex fallback kept a tool at 100% uptime.

**Q10. What's a circuit breaker and what are its states?**
A resilience pattern that stops calling a failing dependency. Closed = calls flow normally. After N consecutive failures it trips Open = calls fail fast immediately without hitting the dependency, giving it room to recover. After a cooldown it goes Half-Open = lets a trial request through; success closes it, failure re-opens. It prevents a slow dependency from consuming all your threads/connections and cascading the outage upstream.

**Q11. How do you trace a request across multiple services?**
Distributed tracing — inject a unique trace/request id at the gateway and propagate it through every service call, queue message, and DB operation via headers, so you can reconstruct the full path of one request end-to-end. Combined with structured logging keyed on that id, you can answer "what happened to *this* request" across service boundaries. Without it, cross-service debugging is guesswork.

**Q12. gRPC supports four call types — when do you use streaming?**
Unary (one request, one response — normal RPC), server-streaming (one request, a stream of responses — think token streaming from a model), client-streaming (a stream of requests, one response — uploading chunks), and bidirectional. For a model gateway, server-streaming maps naturally to streaming generated tokens back. Streaming avoids buffering a large response and improves perceived latency, which is why gRPC/HTTP/2 fits inference well.

**Q13. How do you version a gRPC service without breaking clients?**
Protobuf is designed for it: add new fields with new tag numbers (old clients ignore them), never reuse or renumber existing tags, never change a field's type, and mark removed fields `reserved`. Backward and forward compatibility come from the tag-number contract. For breaking changes, version the service/package. It's more disciplined than REST versioning but the compatibility rules are explicit.

**Q14. What's service discovery and why do you need it?**
Services scale up/down and move, so hardcoding host:port breaks. Service discovery (a registry like Consul, or Kubernetes DNS/Services) lets a service find healthy instances of another by name. The caller asks "where is the model gateway" and gets a current, healthy address. In Kubernetes this is largely built in — a Service name resolves to healthy pods.

**Q15. How do you secure internal service-to-service calls?**
mTLS (mutual TLS) so both sides authenticate each other, network policies restricting who can call whom, and a trust boundary at the gateway — the gateway authenticates external requests and forwards verified identity (e.g. `X-User-Id` headers) so internal services don't re-verify JWTs. Internal services trust the gateway-injected identity *because* external traffic can only reach them through the gateway. That's the pattern from my system-design notes.

**Q16. What's the API gateway's role in a microservices system?**
Single entry point handling cross-cutting edge concerns — authentication, rate limiting, SSL termination, routing, and often request-id injection — so individual services don't each re-implement them. It verifies the JWT once at the edge, checks the Redis blacklist for revocation, and forwards clean, trusted headers downstream. Expired/forged tokens are rejected at the edge and never reach your app servers, saving them CPU.

**Q17. How do you handle configuration across many services?**
Externalised config from environment/secret managers, not baked into images, loaded through typed settings (pydantic-settings) so each service validates its config at startup. Centralised config or a config service for shared values. The principle is the same as a monolith but enforced per service: no hardcoded config, fail-fast on missing values, secrets injected at runtime.

**Q18. A single request now fans out to five services and latency is bad. What do you do?**
Parallelise independent calls instead of chaining them sequentially (fan out concurrently, gather), cache what's cacheable, and question whether it should be five calls — sometimes it's a sign the service boundaries are wrong and chatty. For truly independent data, async aggregation; for a workflow, consider whether an async job + polling fits better than holding a synchronous request across five hops. Chatty synchronous fan-out is a common microservices latency trap.

**Q19. How do you deploy a microservice update without downtime?**
Rolling deployment (replace instances gradually so some always serve), or blue-green (stand up the new version, switch traffic, keep the old for instant rollback), or canary (route a small % to the new version, watch metrics, then ramp). Health/readiness probes gate traffic so a starting instance doesn't receive requests before it's ready. The goal is zero-downtime with an easy rollback path.

**Q20. Given all that, why did NFTRACE stay a single service instead of microservices?**
Because splitting it would have been complexity with no benefit — single-server internal tool, sequential writes, low concurrency, one team. I made the *right-sized* decision: a single FastAPI service with Redis for hot state and SQLite for history, and I can articulate exactly when I'd split it (multi-server, failover, hundreds of concurrent writes). Knowing when *not* to do microservices is as important as knowing how — I applied the same judgment I'd defend in Q6.

---

## 1.11 Redis and caching

**Q1. You add Redis caching and now users occasionally see stale data. What's the bug and fix?**
Missing cache invalidation on writes. Cache-aside reads populate Redis, but when the underlying data is updated the cache still holds the old value. The fix: on every write/update to the DB, actively delete the corresponding cache key (`DEL resource:id`), so the next read misses, fetches fresh data, and repopulates. Stale reads are almost always a write path that updates the DB but forgets to evict the cache.

**Q2. Explain cache-aside and why it's the default pattern.**
On read: check Redis first; on hit return it (sub-10ms, DB untouched); on miss, query the DB, write the result to Redis with a TTL, return it. It's the default because it's resilient — if Redis dies, reads fall back to the DB (fail-open, site slows but stays up) — and it's lazy — you only cache what's actually requested, preserving memory. That's the pattern I used in the 5G pipeline for frequent error lookups.

**Q3. A cache key for a hot item expires and your DB gets hammered by a thousand simultaneous requests. What's this and how do you fix it?**
The thundering herd (or cache stampede). The key expires, thousands of concurrent requests all miss, all hit the DB at once, and the DB falls over. Fix: a distributed lock — the first request acquires it (Redis `SETNX`), rebuilds the cache, and releases; the others wait for the rebuild instead of all stampeding the DB. Alternatively, probabilistic early expiration so one request refreshes before the hard expiry.

**Q4. You used Redis in two projects for different reasons — contrast them.**
In the 5G pipeline Redis is a *response cache* — cache-aside for frequent error lookups to avoid recomputation. In NFTRACE it's *parallel-execution isolation* — each trace session stored under a unique key with a TTL so N concurrent workers never collide and orphaned sessions from crashed workers auto-expire. Same tool, completely different job: one is about speed, the other about concurrency-safe ephemeral state.

**Q5. Why Redis for session state instead of an in-memory dict?**
An in-memory dict doesn't survive a process restart and isn't shared across instances. In NFTRACE, if the server restarted mid-test, an in-memory dict would strand every running worker with no way to stop or collect their traces. Redis persists across restarts and is shared, so any instance sees the session. It's also what makes the service horizontally scalable — no local state pinned to one process.

**Q6. Why Redis for hot session state but SQLite for history — why not one store?**
Different access patterns. Active sessions change state rapidly (STARTING→ACTIVE→STOPPED) and need sub-millisecond concurrent-safe read/write — Redis. Completed history needs durability and is queried infrequently — SQLite. Using only SQLite would bottleneck on write serialization under concurrent session updates; using only Redis would lose history on eviction/restart. Two layers, each the right tool for its pattern.

**Q7. What's a TTL and how do you choose it?**
Time-to-live — the key auto-expires after it. It's your primary staleness bound and your cleanup mechanism. Choose it by how tolerant the data is of being stale vs how expensive it is to recompute: hot, rarely-changing data gets a longer TTL; volatile data a short one. NFTRACE sessions get 1 hour (long enough for a test, short enough to auto-clean a crashed worker). TTL plus explicit eviction on write is the belt-and-suspenders approach.

**Q8. Redis is single-threaded — is that a problem?**
Usually a feature. Single-threaded command execution means operations are atomic and there are no lock contention issues, and it's still extremely fast because it's in-memory. The caveat: a single slow command (a big `KEYS` scan, a huge sorted-set operation) blocks everything, so you avoid O(N) commands on large datasets in the hot path (use `SCAN` not `KEYS`). For throughput beyond one core you scale with Redis Cluster or replicas.

**Q9. What happens when Redis runs out of memory?**
It applies its maxmemory eviction policy — e.g. `allkeys-lru` (evict least-recently-used), `volatile-ttl` (evict soonest-to-expire among keys with TTLs), or `noeviction` (reject writes). For a cache you want an LRU/LFU policy so cold data is evicted to make room. The risk is evicting something you assumed was durable — which is why Redis is for cache/ephemeral state, and the durable copy lives in the primary DB.

**Q10. How do you use Redis as a Celery broker, and why Redis vs RabbitMQ?**
Celery pushes task messages to Redis and workers pull them; I used Redis as the broker and result backend in the eval framework. Redis is simple, fast, and often already in the stack. RabbitMQ is a purpose-built message broker with stronger delivery guarantees and routing; for heavy, mission-critical queuing it's more robust. For most app-level task queuing Redis is sufficient and one less system to run.

**Q11. What Redis data structures have you used beyond simple key-value?**
Strings for cached JSON and session blobs (with TTL via `SETEX`), and I'd reach for hashes for structured records, sorted sets for leaderboards/ranked data or rate-limiting windows, and sets for membership (like a JWT blacklist — `EXISTS blacklist:jti`). Picking the right structure matters: a sorted set for a sliding-window rate limiter is far better than manual key juggling.

**Q12. How would you implement rate limiting with Redis?**
Simplest: a counter key per client with a TTL (fixed window) — `INCR` and reject over the limit, key expires each window. Better: a sliding-window log using a sorted set of timestamps, trimming old entries, for smoother limiting without the window-boundary burst problem. Redis atomicity makes the increment-and-check safe under concurrency, which is the whole point.

**Q13. How do you implement token revocation with Redis (the JWT logout problem)?**
JWTs are stateless, so you can't "delete" one — instead, on logout store the token's unique `jti` claim in a Redis blacklist with a TTL matching the token's remaining life. The gateway checks `EXISTS blacklist:jti` on each request (<1ms) and rejects if present. It's stateless scale with stateful control — you get near-instant revocation without a DB lookup per request. The TTL means the blacklist self-cleans when the token would have expired anyway.

**Q14. Write-through vs write-back vs cache-aside — do you know the difference?**
Cache-aside: app manages the cache, DB is source of truth, populate on miss (what I use). Write-through: writes go through the cache to the DB synchronously, so cache is always fresh but writes are slower. Write-back: writes hit the cache and flush to the DB asynchronously — fast writes but risk of data loss if the cache dies before flush. Cache-aside is the safe default; write-back trades durability for write speed and I'd only use it where that loss is acceptable.

**Q15. Your cache hit rate is low and it's not helping. How do you diagnose?**
Check whether keys expire faster than they're reused, whether the key space is too granular (every request has a unique key so nothing's ever a hit), or whether the cached data changes so often that invalidation wipes it constantly. Measure hit/miss ratio. Sometimes the honest answer is the workload isn't cacheable — unique per-request data won't benefit, and caching it just adds complexity and staleness risk.

**Q16. What did caching actually change in your 5G pipeline, measurably?**
Frequent error lookups went from recomputation to near-instant cache hits, contributing to the "hours to seconds" analysis time and supporting the 70% auto-resolution — repeated errors don't re-run the full retrieval+LLM path, they serve from cache. The value shows up when the same routine errors recur, which they do constantly in operations; caching turns the common case into a sub-10ms lookup.

**Q17. How do you cache LLM responses safely, given prompts vary slightly?**
Key on a normalised hash of the input (the exact prompt + relevant params), so identical requests hit the cache — in the RF generator, caching on (description, procedure) means the same description from 20 testers hits the LLM once and serves cached 19 times. The care needed: normalise the key (whitespace, casing) so trivially-different-but-semantically-identical prompts still hit, and set a TTL so cached answers don't outlive model updates.

**Q18. What's the risk of caching too aggressively?**
Serving stale or wrong data, and masking real data changes — plus memory bloat and eviction of genuinely hot keys. Aggressive caching with weak invalidation is how "why is the user seeing old data" bugs happen. I cache what's expensive and reasonably stable, invalidate on write, and set TTLs so staleness is bounded. Correctness first, then speed — a fast wrong answer is worse than a slightly slower right one.

**Q19. How does Redis persistence work, and do you rely on it?**
Redis offers RDB (point-in-time snapshots) and AOF (append-only log of writes) for durability, so it *can* survive a restart. But for cache use I don't rely on it for correctness — the DB is the source of truth and the cache can always be rebuilt. Where I use Redis for ephemeral state (sessions), persistence + TTL gives restart survival, but the design assumes the durable copy lives elsewhere. Treat Redis as fast and mostly-durable, not as your system of record.

**Q20. When would you NOT add a cache?**
When the data changes constantly (invalidation churn kills the benefit), when the access pattern is unique-per-request (no reuse, no hits), when strong consistency is required and staleness is unacceptable, or when the DB is already fast enough — premature caching adds a stale-data failure mode for no gain. I add a cache to a measured hot read path, not reflexively. The 5G lookups were a genuine hot, repetitive path; that's why caching earned its place there.

---

## 1.12 PostgreSQL and SQL

**Q1. A query that ran in milliseconds is now taking seconds after the table grew. First thing you do?**
`EXPLAIN ANALYZE` to see the plan. The red flag is a `Seq Scan` on a large table where an index should be used — it means the query is scanning every row. Then I check whether the filtered/joined columns are indexed, and whether something in the query prevents the index from being used. Measure the plan before touching anything; guessing at query optimization wastes time.

**Q2. The date filter `WHERE DATE(created_at) = '2026-01-01'` is doing a full scan despite an index on created_at. Why?**
Wrapping the column in a function (`DATE(...)`) prevents the B-tree index from being used — the index is on the raw column, not the function output. Rewrite it as a range: `WHERE created_at >= '2026-01-01' AND created_at < '2026-01-02'`. Now the index applies and it goes from seconds to milliseconds. This is one of the most common real-world slow-query causes — a function on an indexed column.

**Q3. Explain the JOINs and give me a real use for a LEFT JOIN + NULL check.**
INNER returns only matching rows both sides; LEFT returns all left rows plus matches (NULL where none); RIGHT is the mirror; FULL OUTER returns everything. The LEFT + NULL trick finds records with *no* related row — e.g. `LEFT JOIN orders ... WHERE orders.id IS NULL` finds customers who never ordered. It's the standard way to find "things missing a relationship."

**Q4. WHERE vs HAVING — why can't you just use WHERE everywhere?**
WHERE filters individual rows *before* grouping; HAVING filters *after* grouping, on aggregated results. You can't put an aggregate in WHERE — `WHERE SUM(amount) > 1000` is invalid because grouping hasn't happened yet. `HAVING SUM(amount) > 1000` works. It comes down to execution order: filter rows, then group, then filter groups with HAVING.

**Q5. What's an index really, and what's the cost of adding one?**
Usually a B-tree that lets the DB find rows without scanning the table — speeds up lookups, joins, and sorts on the indexed columns. The cost: every write (insert/update/delete) must also update the index, so writes get slower, and it uses storage. So I index columns I frequently filter, join, or sort on, and I don't over-index — an unused index is pure write-tax. Verify usage with `EXPLAIN ANALYZE`.

**Q6. You add a composite index on (a, b) — does it help a query filtering only on b?**
No — a composite index is usable left-to-right (leftmost-prefix rule). `(a, b)` helps queries filtering on `a`, or `a` and `b`, but not `b` alone; for that you'd need an index leading with `b`. Column order in a composite index is a real decision: put the most selective / most-commonly-filtered column first, and match the order to your query patterns.

**Q7. What's the N+1 query problem and how do you spot it?**
Fetching a list with one query, then firing an extra query per row for related data — N items = N+1 queries, brutally slow. You spot it in logs as hundreds of near-identical queries, or in an ORM when you access a lazy relationship inside a loop. Fix: eager-load the related data with a JOIN or the ORM's eager-loading, so it's one or two queries total instead of hundreds.

**Q8. How do you model a many-to-many relationship? Give a real example.**
A junction (bridge) table holding foreign keys to both sides. At Brane I built multi-agent LO junction tables — agents can belong to many logical objects and vice versa, so a junction row is (agent_id, lo_id). You never model many-to-many with a column-list; the junction table makes each pairing a row, queryable and indexable. Add a composite primary key or unique constraint on the pair to prevent duplicates.

**Q9. Explain ACID with a concrete failure each guarantee prevents.**
Atomicity — a transfer debits one account and credits another; either both happen or neither, so a crash mid-transfer doesn't lose money. Consistency — constraints hold across the transaction, so you can't leave the DB in an invalid state. Isolation — two concurrent transactions don't corrupt each other's view. Durability — once committed, a crash doesn't lose it. Each maps to a real data-integrity disaster it prevents.

**Q10. How do you prevent SQL injection?**
Parameterized queries — values passed separately from the SQL text so user input is always data, never executable SQL — or an ORM that parameterizes for you. Never build SQL by string-concatenating user input. It's the single most important database security practice, and it's not optional. The ORM handles it by default, which is one reason to use SQLAlchemy over raw string queries.

**Q11. What's database normalization and when do you deliberately break it?**
Normalization organizes tables to remove redundancy — each fact stored once — so updates don't create inconsistencies. The trade-off is more joins to read. You deliberately denormalize (duplicate some data) to speed up read-heavy paths, accepting the redundancy and the extra care on writes. It's a read-performance vs consistency trade-off; I normalize by default and denormalize only where read performance demands it and I can manage the duplication.

**Q12. Two transactions update the same row concurrently and one update is lost. What happened and how do you prevent it?**
Lost update — both read the old value, both write based on it, the second overwrites the first. Prevent it with optimistic locking (a version column checked on update — if it changed, retry) or pessimistic locking (`SELECT ... FOR UPDATE` to lock the row for the transaction). For a read-modify-write on contended data, one of these is required; without it, concurrent updates silently clobber each other.

**Q13. What are transaction isolation levels and which causes phantom reads?**
Read Uncommitted (sees uncommitted data — dirty reads), Read Committed (sees only committed — Postgres default), Repeatable Read (same rows re-read identically within the transaction), Serializable (full isolation, as if serial). Phantom reads — new rows appearing in a repeated range query — are prevented at Serializable. Higher isolation means more correctness but more locking/contention; you pick the lowest level that's safe for the workload.

**Q14. How do you debug a slow query systematically?**
`EXPLAIN ANALYZE` for the plan (seq scan vs index scan, actual vs estimated rows), check for missing indexes on filtered/joined columns, look for the N+1 pattern in the calling code, and check for functions wrapping indexed columns. Then decide: add an index, rewrite the query, or cache if it's read-heavy and stable. Also, a big gap between estimated and actual rows means stale statistics — run `ANALYZE` to update them.

**Q15. What does reading EXPLAIN ANALYZE output actually tell you?**
`Seq Scan` on a big table = no index used (red flag). `Index Scan`/`Index Only Scan` = index working. Compare *actual* rows vs *estimated* rows — a large discrepancy means the planner has stale statistics and may be choosing a bad plan; `ANALYZE` fixes that. The timing per node shows where the cost concentrates. It's the difference between knowing why a query is slow and guessing.

**Q16. When would you choose PostgreSQL over MySQL, and does it matter for your skills?**
Postgres is more feature-rich and standards-compliant — JSONB for semi-structured data, better support for complex queries, extensions like pgvector. My deepest hands-on is Postgres (schema design at Brane, SQLAlchemy work). But the fundamentals — joins, indexing, transactions, ACID — transfer directly across MySQL and SQL Server with minor syntax differences, so the core skill is portable; the engine choice is about specific features and ecosystem.

**Q17. How do you handle schema migrations safely in production?**
Alembic for versioned, reviewable migrations. The safety rules: make migrations backward-compatible where possible (add columns nullable or with defaults, don't drop a column the running code still uses), do expand-then-contract for renames (add new, migrate, switch code, remove old in a later release), and avoid long table locks on big tables. A migration that locks a large table or breaks the currently-deployed code is how you cause an outage.

**Q18. What's a connection pool and why does it matter for a Python API?**
Opening a DB connection is expensive; a pool keeps a set of connections open and reuses them across requests instead of connecting per request. I run pool_size 10 with 5 overflow so concurrent workers share connections without exhausting the DB's connection limit. Without pooling, a burst of requests each opening a connection can exhaust Postgres's max_connections and take the DB down.

**Q19. How would you paginate a large result set efficiently?**
Keyset (cursor) pagination over offset for large tables — `WHERE id > last_seen_id ORDER BY id LIMIT n` uses the index and stays fast at any depth, whereas `OFFSET 100000` makes Postgres scan and discard 100k rows and gets slower the deeper you go. Offset is fine for small/shallow lists; keyset is the scalable choice. Either way, never return an unbounded result set.

**Q20. Where does your real Postgres schema-design experience show, concretely?**
At Brane I designed the agent-system schema: agent identity tables, multi-agent LO junction tables (many-to-many), attribute-level RBAC permission rows, and execution sibling tables (`lo_input_execution_agent`, `agent_run_scratch`, `agent_episodes`) that track a run's working state and episodic history. That's real production schema design — modeling identity, permissions, relationships, and execution state — plus I added RBAC caching so permission checks don't hit the DB every time. Not textbook SQL; a schema powering a production AI-agent runtime.

---

## 1.13 SQLAlchemy, Celery, Streamlit, GraphQL

**Q1. Why SQLAlchemy async over the sync ORM in a FastAPI app?**
Because a sync session inside an async handler blocks the event loop — you lose the whole point of async FastAPI. SQLAlchemy 2.0 async sessions with asyncpg make DB calls yield to the loop like any other I/O, so the API stays responsive during DB waits. I use it in the eval framework, prompt-regression, and bias auditor precisely so the async web layer isn't undermined by a blocking data layer.

**Q2. How does one set of ORM models work across SQLite and PostgreSQL?**
The models are backend-agnostic; only the connection string changes. In prompt-regression, SQLite is the zero-setup default and Postgres is one `DATABASE_URL` env swap away — no model changes. That gives frictionless local dev (clone, run, no Docker) with a production-grade DB one variable away. The caveat is not leaning on backend-specific features in the models so portability holds.

**Q3. What's the SQLAlchemy session and the classic mistake around it?**
The session is the unit-of-work — it tracks objects and flushes changes in a transaction. The classic mistake is sharing one session across requests or threads (it's not thread-safe) or holding it too long. In FastAPI I use a per-request session via a `yield` dependency that opens before and closes after the request. And the gotcha from earlier: that session closes at response time, before a BackgroundTask runs.

**Q4. Lazy vs eager loading in the ORM — why does it matter?**
Lazy loading fetches a relationship only when accessed, which causes the N+1 problem inside loops — one query per row. Eager loading (`selectinload`/`joinedload`) fetches related data up front in one or two queries. For a list endpoint that touches each row's relationships, eager loading is the difference between 2 queries and 200. I choose loading strategy based on whether I'll actually access the relationship.

**Q5. When do you drop to raw SQL instead of the ORM?**
For complex analytical queries, bulk operations, or DB-specific features where the ORM is awkward or generates inefficient SQL — I'll write parameterized raw SQL (still parameterized, never concatenated). The ORM is great for CRUD and relationships and safety; it's not always the right tool for a heavy reporting query. Use the ORM by default, raw SQL where it's genuinely better, both parameterized.

**Q6. Why Celery over FastAPI BackgroundTasks — give the failure that forces the choice.**
BackgroundTasks are in-process: if the server restarts mid-task, the task is silently lost with no recovery. For a CI quality gate in the eval framework, a lost evaluation would silently pass a PR that should have been blocked — unacceptable. Celery persists tasks in Redis and retries failed jobs (up to 3, 30s delay), so durability is guaranteed. Fire-and-forget trivial stuff → BackgroundTasks; anything that must not be lost → Celery.

**Q7. How does Celery actually work — broker, worker, backend?**
The app enqueues a task message to a broker (Redis/RabbitMQ); a separate worker process pulls and executes it; the result backend (Redis) stores the outcome. It decouples the API response time from the task runtime — the API returns immediately with a job id, the worker does the slow work independently, and you scale workers separately from the web tier. That's the async-write pattern behind my long-running-job endpoints.

**Q8. How do you make Celery tasks reliable — retries, idempotency?**
Configure retries with backoff for transient failures, make tasks idempotent so a retry doesn't double-process (check-and-set on a job id), and set time limits so a hung task doesn't block a worker forever. Persist task state so the client can poll status. In the eval framework tasks retry up to 3 times; the key is that retried tasks must be safe to re-run, which means designing for idempotency up front.

**Q9. A Celery task hangs and blocks a worker. How do you prevent one bad task killing throughput?**
Task-level time limits (soft and hard) so a stuck task is terminated, adequate worker concurrency/prefetch tuning so one slow task doesn't starve others, and routing heavy tasks to a dedicated queue/worker pool so they don't block light tasks. The principle mirrors the API: isolate slow work so it can't degrade everything else.

**Q10. Why Streamlit for your tools, and what's its honest limitation?**
Streamlit turns a Python script into a web UI in ~20 lines — no HTML/CSS/JS — so I get a working dashboard for an internal tool in an hour (RF generator UI, all four eval/audit dashboards). The limitation: it's functional, not beautiful or highly customisable, and testing pure Streamlit logic needs browser automation. For customer-facing UIs I'd use React; for internal tooling, functional is enough and the speed wins.

**Q11. Why did you split Streamlit + FastAPI instead of doing everything in Streamlit?**
Testability, reusability, separation of concerns. With a FastAPI backend I test the generation logic with pytest+httpx without touching the UI; the `/generate` endpoint is reusable from a CLI or CI pipeline, not locked in the UI; and I can redesign the UI without touching the engine. Pure Streamlit couples logic to the UI and makes it hard to test. For anything that might grow, the split is the right pattern even if slightly over-engineered for 20 users.

**Q12. How does your Streamlit dashboard get data without coupling to the API being up?**
In prompt-regression the dashboard reads directly from the database via SQLAlchemy, deliberately independent of the FastAPI service — it's an analytics tool that should work whether or not the API process is running. That's a conscious decoupling: the dashboard's job is to visualise stored results, so it goes straight to the source of truth rather than depending on another running service.

**Q13. Streamlit reruns the whole script on every interaction — how do you handle expensive work?**
Cache it. Streamlit re-executes top-to-bottom on each interaction, so expensive operations (model loads, DB queries) must be cached (`@st.cache_data`/`@st.cache_resource`) or they re-run every click. Session state holds values across reruns. Understanding the rerun model is essential — people write a Streamlit app that reloads a model on every button press and wonder why it's slow.

**Q14. What is GraphQL and when is it better than REST?**
GraphQL exposes a single endpoint where the client specifies exactly the fields it wants in one query, avoiding over-fetching and under-fetching. It's better when clients have varied data needs and you'd otherwise build many bespoke REST endpoints or make multiple round-trips. I built and optimised GraphQL APIs at Abjayon with AWS AppSync. The trade-off vs REST is complexity — caching, rate-limiting, and query-cost control are harder.

**Q15. What's the N+1 problem in GraphQL and how is it solved?**
A query for a list where each item resolves a related field can trigger one resolver call (and DB query) per item — N+1, same shape as the ORM problem but at the resolver layer. The standard fix is DataLoader — it batches and caches the per-item requests within a single query into one batched fetch. GraphQL's flexibility makes N+1 easy to introduce, so batching at the resolver is essential.

**Q16. What are the downsides of GraphQL you'd flag to a team considering it?**
Caching is harder than REST (no simple URL-based HTTP caching since it's one endpoint with POST bodies), a malicious or careless client can craft an expensive deeply-nested query (needs query cost/depth limiting), rate-limiting is trickier, and the schema/resolver layer adds complexity. For a simple, well-defined API, REST is often the pragmatic choice; GraphQL earns its keep when client data needs are genuinely diverse.

**Q17. How do you handle DB migrations with SQLAlchemy?**
Alembic — it autogenerates migration scripts from model changes, which I review (autogenerate isn't perfect), version them, and apply in order. The discipline is the same as any migration: backward-compatible changes, expand-then-contract for renames, and never a migration that breaks the currently-running code or locks a big table. Alembic gives the versioned, reviewable trail; the safety comes from how you write the migrations.

**Q18. How do you test code that uses SQLAlchemy?**
Integration tests against a real test database (SQLite in-memory for speed, or a disposable Postgres when I need Postgres-specific behaviour), with the session dependency overridden to the test DB and rolled back between tests for isolation. I avoid mocking the ORM itself because that tests the mock, not the actual query behaviour — the whole point is to verify the queries work against a real engine.

**Q19. Celery, RabbitMQ, Redis, Kafka — how do you choose a queue?**
Celery is the task-queue framework; the broker underneath is Redis or RabbitMQ. Redis broker: simple, fast, often already present — good default for app task queuing. RabbitMQ: purpose-built broker with stronger delivery guarantees and routing — for mission-critical queuing. Kafka: a distributed log for high-throughput event streaming and replay, not really a task queue. I match to the job: Celery+Redis for background jobs, Kafka for event streams.

**Q20. How do these pieces fit together in your eval framework, end to end?**
FastAPI (async) accepts a test case, validates with Pydantic, writes it to Postgres via SQLAlchemy async, and enqueues a Celery task on Redis, returning immediately. A Celery worker pulls the task, calls the LLM, runs the evaluators, writes results back to Postgres, and fires a Slack alert on failure. Streamlit reads Postgres directly and shows trends, refreshing every 30s. Each tool does one job — API for intake, Celery for durable async work, Postgres for truth, Streamlit for visibility — and the whole thing is one `docker-compose up`.

---

## 1.14 Docker, Kubernetes, CI/CD

**Q1. Your image works locally but something breaks in production after a rebuild. Base image is `python:latest`. What's wrong?**
`latest` is a mutable tag — a new Python version shipped and your image silently changed under you, breaking something. Pin it: `FROM python:3.11-slim`. This is the Docker mistake that trips up AI-assisted developers especially. Reproducible builds require pinned, immutable base image versions; `latest` is a time bomb that makes "works today, breaks tomorrow" builds.

**Q2. A security review finds your API key in the built image. How did it get there and how do you fix it?**
It was passed as `ENV` or baked in at build time, and it's now visible in `docker history` to anyone with image access. Never put secrets in the Dockerfile. Inject them at runtime via environment variables (or a secret manager / mounted secret), not at build time. Build-time secrets persist in image layers even if you "remove" them later. This is on the Docker best-practice checklist I authored at Nokia.

**Q3. Your Docker build is slow because it reinstalls dependencies on every code change. Fix?**
Layer ordering for cache reuse. Copy the dependency manifest (`requirements.txt`/`pyproject.toml`) and install *before* copying the application code, so the dependency layer is cached and only rebuilds when dependencies change — a code edit then reuses the cached deps layer. People copy everything first and reinstall deps on every code change, killing build cache. Order layers from least-frequently-changed to most.

**Q4. What's a multi-stage build and why use it?**
Use one stage to build (compile, install build tools, produce artifacts) and a second slim stage that copies only the final artifacts, discarding build dependencies. The result is a much smaller, more secure production image — no compilers or build tooling in the shipped image. The Financial Parser Dockerfile does exactly this: a Node build stage, then an nginx stage that copies only `dist/`.

**Q5. Give me your Dockerfile best-practices checklist.**
Slim pinned base image (`python:3.11-slim`, never `latest`), run as a non-root user, order layers so dependencies cache separately from code, use `.dockerignore` to keep build context small, pin dependency versions, never bake secrets (inject at runtime), and multi-stage to keep the final image small. I literally wrote this checklist at Nokia and it became team standard — it's the difference between a reproducible, secure image and a fragile one.

**Q6. Why run as a non-root user in a container?**
Defense in depth — if the app is compromised, a non-root process limits what the attacker can do inside the container and reduces the blast radius if they escape it. Containers default to root, which is unnecessary privilege for most apps. Add a user and `USER appuser` before the run command. It's low-effort, real security hardening.

**Q7. What's the difference between Docker and Kubernetes, and when do you need K8s?**
Docker packages and runs a container; Kubernetes orchestrates many containers across many machines — scheduling, scaling, self-healing, service discovery, rolling updates. You need K8s when you have multiple services that must scale independently, survive node failures, and deploy without downtime. For a single container or a small app, Docker (or docker-compose) is enough — K8s is orchestration you adopt when the operational complexity justifies it.

**Q8. What did you actually do with Kubernetes?**
During 5G Core UDM/AUSF testing I validated K8s pod health and real-time cluster dashboards — checking that network-function pods were healthy, watching cluster state, in the context of carrier-grade deployment validation. So my K8s is operational/validation depth in a production telecom context rather than writing Helm charts from scratch — I'm honest that it's the operations side, and it's real.

**Q9. What's the difference between liveness and readiness probes?**
Liveness = "is the process alive?" — if it fails, K8s restarts the pod. Readiness = "is it ready to serve traffic?" — if it fails, K8s stops routing to it but doesn't kill it. The distinction matters at startup: a pod may be alive but not yet ready (still connecting to the DB), and you don't want traffic until it's ready. My health endpoints distinguish `/health` (liveness) from `/ready` (readiness) for exactly this.

**Q10. How does docker-compose help in development, and where does it stop being enough?**
Compose brings up multiple dependent services with one command and defined dependencies — the eval framework's `docker-compose up -d` starts Postgres, Redis, the API, the Celery worker, and Streamlit, with health-check ordering so the API waits for Postgres/Redis. It's perfect for local multi-service dev. It stops being enough for production scale/resilience — multi-node scheduling, self-healing, rolling deploys — which is where you move to Kubernetes.

**Q11. What is CI/CD, concretely, in a pipeline you've built?**
CI runs on every push — lint, tests, build — catching problems early; CD extends that to packaging and deploying once it passes. Prompt-regression ships a PR workflow that detects affected tests, runs them, posts a PR comment with scores vs baseline, and blocks merge on regression — CI for prompt quality. A typical pipeline: checkout, install, lint, test, build image, push to registry, deploy. It's automation that makes "it passes on my machine" irrelevant.

**Q12. How do you make CI fast as the test suite grows?**
Run only what's affected. In prompt-regression, a git-diff plus a reverse index runs only the test cases referencing changed prompt files — a PR touching 3 of 80 prompts runs ~12 tests, not 80. Plus parallelize, cache dependencies between runs, and split fast unit tests from slow integration. Selective execution is the key lever; without it CI time grows linearly with the suite and people route around it.

**Q13. How do you catch a problem that never shows up in a PR?**
A scheduled run. Model drift doesn't arrive in a PR — it arrives through the API when a provider updates their model. Prompt-regression runs a weekly full-suite drift monitor against the live model and alerts on regressions. Some failure classes are time-based or external, not change-based, so you need scheduled checks in addition to PR-triggered ones. Same idea as a nightly integration run catching environmental drift.

**Q14. How do you deploy without downtime?**
Rolling (replace instances gradually, some always serving), blue-green (stand up the new version fully, switch traffic, keep old for instant rollback), or canary (route a small % to the new version, watch metrics, then ramp). Readiness probes gate traffic so a starting instance isn't hit before ready. All aim for zero downtime and a fast rollback. I pick based on risk — canary for a risky change, rolling for routine.

**Q15. A deploy goes bad in production. How do you roll back safely?**
With blue-green, switch traffic back to the old environment instantly. With rolling, redeploy the previous known-good image. The prerequisites are immutable, versioned images (so "the previous version" is precisely identifiable — another reason to pin, not use `latest`) and backward-compatible DB migrations (so the old code still works against the migrated schema). Rollback is only safe if you designed for it before the deploy.

**Q16. How do you handle secrets in CI/CD?**
CI secrets stored in the platform's secret store (GitHub Actions secrets), injected as environment variables at runtime, never committed and never echoed into logs. In the image, secrets are injected at runtime, not baked in. The rule is consistent everywhere: secrets live in a secret store and are injected at the last moment, never in source, never in image layers, never in logs.

**Q17. How do you monitor and log a production service?**
Structured logging — JSON logs with a request id so I can trace one request across services — to a central system. RED metrics: request Rate, Error rate (5xx), Duration (p95/p99 latency for long-tail pain). Health/readiness endpoints. Alerting on thresholds so the team is paged when error rate or latency spikes. And the hard rule: never log secrets, tokens, or PII.

**Q18. Walk me through debugging a production incident.**
Data first: check metrics to see *when* the error rate spiked — after a deploy? Correlated with traffic? That tells you what *kind* of problem before you touch code. Then logs with a failing request id to trace it end-to-end. Form a hypothesis, verify it before changing anything — don't guess-and-poke. Fix, then add a test or alert so it can't silently recur. The order (metrics → logs → hypothesis → verify → fix → prevent) matters more than people realise.

**Q19. What's your container image size strategy and why care?**
Smaller images pull faster (quicker deploys and scaling), have a smaller attack surface, and use less registry storage. Levers: slim base images, multi-stage builds to drop build tooling, `.dockerignore` to shrink build context, and not installing dev dependencies in the production image. A 1GB image full of build tools is slower and less secure than a 150MB slim runtime image doing the same job.

**Q20. How does NFTRACE's NCD integration exemplify real CI/CD thinking?**
I integrated NFTRACE into Nokia Continuous Delivery with pre/post-test hooks: when a tagged test starts, it auto-starts a trace; when it ends, it stops, merges, validates the protocol, and feeds the result back into the pipeline report — automatically blocking on trace-validation failure. The insight is that a test could *pass* its assertions but *fail* trace validation, catching a bug class that was invisible before. That's CI/CD done right — automated verification wired into the pipeline that catches what manual steps missed.

---

## 1.15 Authentication, RBAC, API security

**Q1. A developer put the user's email and role in the JWT "for convenience." Why is that a problem?**
A JWT is signed, not encrypted — anyone can base64-decode the payload and read it in browser DevTools' Network tab. Signing guarantees integrity (it wasn't tampered with), not confidentiality. So email, roles, any PII in the payload is exposed. The fix: keep only non-sensitive claims (user id, expiry) in the token, and never treat "signed" as "secret." This is a real mistake I've seen and it's exactly the confusion the question tests.

**Q2. Explain a JWT and why it scales.**
Three dot-separated parts: header (algorithm), payload (claims — user id, expiry, roles), signature (header+payload signed with a secret). The flow: user logs in, server issues the JWT, client sends it in `Authorization: Bearer` on every request, server verifies the signature and expiry — no database lookup. That statelessness is why it scales: any server instance can verify any request without shared session storage.

**Q3. How do you revoke a JWT before it expires — the logout problem?**
JWTs are stateless, so you can't delete one from the client. First line: short expiry (15–30 min) so the window is small. For explicit revocation (logout, compromised account), store the token's `jti` (unique id) claim in a Redis blacklist with a TTL matching the token's remaining life, and check `EXISTS blacklist:jti` on each request (<1ms). That's stateless scale with stateful control — near-instant revocation without a DB hit per request.

**Q4. JWT vs session-based auth — the real trade-off?**
Sessions: server stores state, client holds a session id, server looks it up — easy to revoke (delete the session) but needs shared session storage to scale horizontally. JWTs: stateless, the token carries identity, verified by signature — scales without shared state but is hard to revoke before expiry. So JWT trades easy revocation for stateless scale; you mitigate the revocation gap with short expiry plus a blacklist.

**Q5. Access token vs refresh token — why two?**
The access token is short-lived (say 15 min) and sent with every request — so if it leaks, the damage window is small. The refresh token is long-lived, stored more securely, and used only to get a new access token when it expires, without forcing re-login. It limits blast radius (short-lived access) while keeping the user logged in (long-lived refresh). If the access token leaks, it expires fast; the refresh token isn't exposed on every request.

**Q6. Authentication vs authorization — and where have you done real authorization?**
Authentication is *who you are* (proving identity — logging in); authorization is *what you're allowed to do* (permissions). I implemented attribute-level RBAC at Brane — permissions defined down to individual attributes, not just broad roles — which is authorization, and the harder, finer-grained kind. Most systems do role-level; attribute-level means checking access per attribute, which is more precise and more work.

**Q7. What's the #1 API security bug you actively look for?**
Broken object-level authorization (BOLA). The code authenticates correctly — valid JWT, real user — but never checks the user actually *owns* the requested resource. `GET /ads/{id}` verifies the token but not that the ad belongs to this user, so any authenticated user reads anyone's data. It's OWASP's top API risk. The fix is an ownership/permission check on every resource access, not just an authentication check at the door.

**Q8. What is OAuth2 and its most common flow?**
OAuth2 is a framework for *delegated authorization* — one app accesses resources on behalf of a user without the user sharing their password ("Log in with Google"). Players: user (resource owner), client app, authorization server (Google), resource server. The common web flow is authorization-code: redirect the user to the auth server, they consent, you get a code, you exchange it server-side for an access token. I can explain it thoroughly; I flag that I've built more JWT/RBAC than full OAuth flows.

**Q9. What's OIDC and how does it relate to OAuth2?**
OIDC (OpenID Connect) is a thin identity layer on top of OAuth2. OAuth2 handles authorization (what you can access); OIDC adds authentication (who you are) via an ID token — a JWT with identity claims like `sub` and email. So "log in with Google" for identity is OIDC; granting an app access to your Google Drive is OAuth2. SSO builds on OIDC — one identity provider, many apps.

**Q10. How do you secure an API — give me the layers?**
HTTPS everywhere; validate and sanitize all input (Pydantic); parameterized queries against SQL injection; authenticate every protected endpoint *and* check authorization per resource (BOLA); rate-limit to prevent abuse; lock CORS to known origins; never leak stack traces or internal detail in errors (log internally, return generic); secrets in a secret manager with least privilege. Security is layered — no single control is enough, and the authorization-per-resource layer is the one most often missed.

**Q11. How does attribute-level RBAC differ from role-based, and why did it need caching?**
Role-based grants permissions by broad role (admin, editor). Attribute-level defines permissions down to individual attributes — finer-grained, so a user might access some attributes of an object but not others. It needs caching because checking fine-grained permissions on every access would hit the DB constantly and slow the hot path — so at Brane I cached the attribute-RBAC checks so permission evaluation didn't require a DB round-trip each time. Finer authorization is more checks, so you cache to keep it fast.

**Q12. How do you propagate identity cleanly through a microservices system?**
Verify the JWT once at the API gateway (signature, expiry, blacklist), then strip the raw token and inject simple trusted headers downstream — `X-User-Id`, `X-User-Roles`. Internal services trust these headers because external traffic can only reach them through the gateway. This means internal services don't each re-decode and re-verify JWTs, and expired/forged tokens are rejected at the edge before consuming any app-server resources.

**Q13. Where do you store the JWT on the client, and what are the trade-offs?**
Options are memory, localStorage, or an httpOnly cookie. localStorage is vulnerable to XSS (script can read it); an httpOnly cookie can't be read by JS (XSS-safe) but is vulnerable to CSRF unless you add CSRF protection/SameSite. There's no free lunch — httpOnly cookie + SameSite + CSRF token is the more defensive setup for web apps. The point is knowing the trade-off, not that one is universally right.

**Q14. How do you prevent SQL injection and what's the non-negotiable rule?**
Parameterized queries — values passed separately from the SQL so input is always data, never executable — or an ORM that parameterizes. Never concatenate user input into SQL strings. It's non-negotiable because injection is catastrophic (full data exfiltration/destruction) and the fix is trivial. SQLAlchemy does it by default, which is one more reason to prefer the ORM over hand-built query strings.

**Q15. What secrets-management mistakes do you watch for?**
Secrets in source control, secrets baked into Docker images (visible in `docker history`), secrets logged, and over-privileged credentials. The fixes: secrets in environment variables or a secret manager, injected at runtime; least-privilege on every credential; and never logging tokens/keys. This ties to the Docker checklist — build-time `ENV` secrets are a classic leak. Secrets live in a vault and are injected at the last possible moment.

**Q16. How do you rate-limit an API and why?**
To prevent abuse and protect resources — a counter per client with a TTL (fixed window) or a sliding-window log in Redis for smoother limiting. Redis atomicity makes the increment-and-check safe under concurrency. You especially rate-limit expensive endpoints (an LLM-generation endpoint) so one client can't exhaust your budget or capacity. It's both a security and a cost control.

**Q17. What should an error response NOT contain, and why?**
No stack traces, no internal paths, no SQL errors, no framework detail — those hand an attacker a map of your system and can leak data. Log the full detail internally (with a request id), return a generic message and a correlation id to the client. The consistent error shape I use returns a code and a safe message; the sensitive detail stays in the logs where only the team sees it.

**Q18. How would you design auth for the ad-generation API in your client's domain?**
JWT auth with RBAC — the user logs in, gets a token, and every endpoint verifies it via a dependency that extracts the current user. Authorization checks ownership on each resource (a user only sees their own generations — no BOLA). Rate-limit the expensive generation endpoint. Short-lived access tokens with refresh, and a Redis blacklist for revocation. It's the same pattern I've implemented — JWT for identity, RBAC for permissions, ownership checks per resource.

**Q19. What's the difference between hashing and encryption for stored credentials?**
Hashing is one-way (you can't recover the original) — used for passwords, with a slow salted algorithm (bcrypt/argon2) so brute-force is expensive. Encryption is two-way (decryptable with a key) — used for data you need to read back. The classic mistake is encrypting (or worse, plaintext-storing) passwords instead of hashing them. Passwords: salted slow hash. Secrets you must read back: encryption with a managed key.

**Q20. How do you think about security in an LLM/agent system specifically?**
Additional attack surface: prompt injection (user input hijacking instructions — separate system from user content, treat retrieved text as data), tool-access control (least privilege on what tools an agent can invoke — RBAC-gate the sensitive ones, which I did at Brane), PII in prompts/logs (don't send or log sensitive data — the bias auditor strips demographic labels before the judge sees them), and output validation before any consequential action. LLM security is classic API security plus injection and tool-privilege concerns.

---

## 1.16 Document ingestion (PDF, OCR, images)

**Q1. Your OCR pipeline accepts garbage documents and wastes LLM calls on them. How do you fix that?**
Validate *before* the expensive step. In EMS I score an uploaded document for resume-ness (section headers, professional keywords, contact info, date patterns — threshold ≥40/100) *before* any LLM call. Documents below threshold are rejected up front, saving inference time and preventing garbage data. The principle: gate expensive processing behind a cheap validity check, so you don't spend LLM budget on inputs that can't produce useful output.

**Q2. How do you extract text from a PDF, and what's the fallback for scanned PDFs?**
For text-based PDFs, a library like `pdfplumber` extracts the embedded text directly — fast and accurate. For scanned/image PDFs there's no embedded text, so you rasterise each page to an image (pdf.js/pdf2image) and run OCR (Tesseract). In EMS I use pdfplumber with a pytesseract OCR fallback; in the Financial Parser, pdf.js renders pages to canvas and Tesseract.js OCRs them. Always handle both — a "PDF" might be real text or just a picture of text.

**Q3. Image resumes fail your resume-validation scorer. Why, and how do you handle it?**
OCR output from images is messy and often lacks clean structure, so the validation score falls below the threshold set for clean text. I applied a more lenient threshold for image files (accept at lower confidence if there's enough text). The general lesson: OCR text is noisier than extracted text, so downstream validation and parsing must tolerate more mess for the OCR path than the clean-text path — one threshold doesn't fit both.

**Q4. A regex for email/phone works in tests but never matches in real resumes. What's the bug?**
Anchors. The regex used `^...$`, which only matches if the *entire string* is an email/phone — but in a resume the email is embedded in a line of other text, so it never matches. Fix: remove the anchors and use `re.search()` (find anywhere) instead of `re.match()` (match from start). This was a real EMS bug — BUG-002 — rejecting valid resumes because the contact-info regex was over-anchored.

**Q5. Why send OCR text to the LLM instead of the image itself?**
Privacy, mostly. A multimodal call would upload the original document to the provider's servers; running OCR locally and sending only the extracted text (capped at 8k chars in the Financial Parser) keeps the original file on the user's device. It also controls token cost and stays within the model's budget. The trade-off is you lose layout/visual info OCR doesn't capture — acceptable when privacy is the priority, which for bank statements and resumes it is.

**Q6. How do you handle OCR that produces messy, broken text?**
Expect imperfection and design around it: lenient downstream validation for the OCR path, capping/cleaning the text before the LLM, and letting the LLM do the heavy lifting of interpreting noisy text (models are robust to OCR noise). If fewer than a minimum number of characters come out, fail early with a clear message ("use a clearer image") rather than passing junk downstream. OCR is best-effort; the pipeline must tolerate its noise, not assume clean output.

**Q7. How do you extract structured data from unstructured document text reliably?**
LLM extraction with a strict schema and validation. In EMS, Ollama receives the resume text plus a detailed extraction prompt and returns JSON for 22+ fields, which Pydantic then validates and coerces; if the name is missing it retries. The reliability comes from the schema + validation + retry loop, not from trusting the LLM's raw output. Give the model the exact fields you want, then validate what comes back.

**Q8. The LLM returns unparseable JSON ~15% of the time on extraction. How do you make it robust?**
Multi-strategy parsing plus validation. In EMS the parse chain is direct JSON parse → regex extraction of the JSON block → key-value fallback, then Pydantic validation, then retry if invalid. Raw LLM JSON fails 10–20% of the time, so a single `json.loads` is fragile. Layered salvage means most malformed-but-recoverable responses still yield valid data, and only genuinely broken ones fall through to retry.

**Q9. How do you handle a truncated LLM response when a document has more content than the output token limit?**
Salvage the partial result rather than failing. In the Financial Parser, when a big statement exceeds Gemini's output limit, a three-method JSON salvage runs: strip code fences, find the outermost braces by index, then find the last complete transaction object and close the structure — returning the transactions that did come through. Partial results are more useful than an error. You detect truncation and recover what you can.

**Q10. How do you chunk a document for RAG after extraction?**
Split into overlapping chunks sized for retrieval — in EMS, 500 chars with 100-char overlap — then embed each. The overlap preserves context across boundaries so an idea split mid-chunk is still retrievable. Fixed-size is simplest; structure-aware chunking (split on sections/headings) is better because each chunk is a coherent unit. Chunk size trades retrieval precision against context, and it's worth tuning against real queries.

**Q11. How does OCR run entirely in a browser with no server?**
Tesseract.js — the Tesseract OCR engine compiled to WebAssembly — runs OCR inside the browser tab at near-native speed, in a Web Worker so it doesn't freeze the UI. The Financial Parser uses this so the document never leaves the device. WASM is what makes heavy native tooling like an OCR engine run client-side; it's the enabler for the whole privacy-first, no-backend architecture.

**Q12. How do you show progress for a slow multi-page OCR job?**
Normalise progress across the pipeline stages and report it. In the Financial Parser, PDF-to-image conversion is 0–30% of the bar and OCR over all pages is 30–100%, so the user sees continuous progress across both phases rather than a stalled bar. For long client-side work, progress feedback is essential UX — you map each stage to a slice of the total and update as pages complete.

**Q13. Why run document processing in a background thread?**
So the API responds immediately and the user isn't blocked. In EMS, upload kicks off `process_cv()` in a daemon thread and the API returns `{job_id, status: queued}` right away; the frontend polls for status. OCR + LLM extraction takes seconds to tens of seconds — holding the HTTP connection open for that is bad UX and ties up the server. Background processing + polling is the async-write pattern applied to document ingestion.

**Q14. Why did EMS use a background thread instead of FastAPI BackgroundTasks?**
BackgroundTasks with blocking calls (subprocess to Ollama CLI, HTTP to the local model) caused subtle issues on some setups, so explicit `threading.Thread(daemon=True)` was more predictable. It's an honest, pragmatic call — for a heavier production system I'd use Celery for durability, but for this learning project explicit threads were more reliable than BackgroundTasks for the blocking workload. Knowing the trade-off is the point.

**Q15. How do you track job status for a background document job?**
In EMS each job writes its status to a flat JSON file at `data/jobs/{job_id}.json`, and the frontend polls `GET /api/job/{id}`. Flat files avoid DB connection overhead during frequent polling and are trivially debuggable (read the file). For a scaled system I'd use Redis or a DB status table, but the pattern — a pollable job-status resource keyed by id — is the same as any async-write flow.

**Q16. How do you validate that extracted structured data is correct before storing it?**
Pydantic schema enforcement plus domain checks — the extracted JSON must match the expected field types and shapes, and I retry the extraction if a critical field (like name) is missing. Field sanitization cleans values before the DB write. The layered validation (7 sequential layers in EMS before any DB write) ensures malformed or incomplete extractions don't corrupt the store. Validate at the boundary, never trust raw model output into the database.

**Q17. How do you keep multi-database writes consistent when indexing extracted data?**
This is a genuine distributed-systems problem I flag honestly. In EMS a write can succeed in PostgreSQL but fail when indexing into FAISS, leaving them inconsistent. The proper fix is transactional consistency — roll back the Postgres write if FAISS indexing fails, or use a reconciliation job to detect and repair drift. It's on my improvements list; I don't pretend it's solved, but I understand it's a real consistency problem, not a trivial bug.

**Q18. How do you categorise or classify extracted content?**
LLM classification with a fixed label set in the prompt. The Financial Parser has Gemini assign each transaction one of 14 categories and a fixed/variable cost type, using a low temperature and JSON output mode for consistency. Giving the model the exact allowed labels (not open-ended) keeps classifications consistent and usable downstream for analytics. Constrain the output space and validate it's within the allowed set.

**Q19. What temperature do you use for extraction/parsing and why?**
Low — 0 in EMS (with a fixed seed for reproducibility), 0.1 in the Financial Parser. Extraction and parsing must be deterministic and faithful: the same document should yield the same structured output, and I don't want the model creatively inventing values. Low temperature plus "don't invent values not in the text" in the prompt minimises hallucinated fields. Extraction is the opposite of a creative task — pin it down.

**Q20. Someone says "just use ChatGPT/Gemini's web UI to extract this." How do you justify a real pipeline?**
The web UI gives unstructured text you still reformat by hand, uploads your document to a third party, and has no automation, validation, or audit. My pipeline gives structured, schema-validated output directly usable as data, keeps the file private (in-browser OCR, only text sent), handles batches, salvages truncated responses, and categorises consistently. The LLM is one step; the value is the ingestion, validation, privacy, and structuring around it — the same "why not just use the browser LLM" defense I rehearsed for the RF generator.

---

## 1.17 LLM APIs, model routing, model selection, token economics

**Q1. Your LLM feature works but the API bill is unsustainable. Where do you cut without hurting quality?**
Model routing — send easy, high-confidence cases to a cheap model and only hard cases to the expensive one. In the 5G pipeline a threshold function routes high-confidence, non-critical matches to Claude Haiku and ambiguous or critical ones to Sonnet, cutting API cost ~60% with no accuracy loss on the hard cases. The insight: you don't need your best model for every request. Route by difficulty, and most traffic goes to the cheap path.

**Q2. How do you decide which model to use for a given task?**
Match model capability to task difficulty. Structured extraction needs no reasoning — I use Haiku (3–5× cheaper, ~500ms) in the RF generator. Synthesising across multiple retrieved patterns or explaining a failure chain needs reasoning — Sonnet. Privacy-critical or unlimited-dev work — local Ollama. The senior signal is *not* reaching for the biggest model reflexively; it's selecting the smallest model that does the job well, which is both cheaper and faster.

**Q3. What's "token economics" and how do you actually manage it?**
Cost scales with input + output tokens, so managing it means: routing to cheaper models, capping output length (`max_tokens`), trimming context you send (don't resend full history every turn), caching repeated calls (RF generator caches on description+procedure — one LLM call serves 20 identical requests), and using local models where accuracy allows. Also fail-fast tiering (prompt-regression runs cheap checks first, the paid judge only if they pass — ~50% saving). It's engineering discipline, not just "the model is expensive."

**Q4. How do you integrate multiple LLM providers cleanly?**
Behind a common interface so the rest of the code doesn't know or care which provider — a factory/registry that routes by model name and returns a standardized response object. In prompt-regression, `claude-*` routes to the Anthropic client, `gpt-*` to OpenAI, anything else to Ollama, all returning the same `LLMResponse` contract; adding a provider is one class + one routing rule. At Brane the gRPC gateway did this at the service level — multi-provider routing across instruct/thinking/vision variants. Abstract the provider so it's swappable.

**Q5. Why and when would you run a local model instead of a cloud API?**
Privacy (data never leaves the machine — EMS runs Ollama so resume data stays local), zero per-call cost for high-volume or dev work, and direct control of inference params (temperature, context, seed). The trade-off is slower inference on consumer hardware (2–5s) and you manage the infra. I use local when privacy is non-negotiable or API cost at volume is prohibitive, and cloud when I need top-tier capability or don't want to run infra.

**Q6. Your local model is slow and falling back to CPU. What do you check?**
VRAM fit. In EMS, qwen2.5:14b (18GB) didn't fit the RTX 3060's 6GB VRAM, so it fell back to CPU and responses took 30+ seconds. Switching to qwen2.5:7b-instruct (quantized) fit the GPU, restored ~100% GPU utilization, and dropped responses to 2–5s. The model must fit in VRAM to use the GPU; if it doesn't, it spills to CPU and crawls. Right-size the model (or quantize it) to the hardware.

**Q7. What's quantization and what does it trade?**
Quantization reduces the precision of model weights (e.g. FP16 → 4-bit), shrinking memory footprint and speeding inference, at a small accuracy cost. It's what let the qwen2.5:7b-instruct quant fit the 6GB GPU. The trade-off is precision for size/speed — usually acceptable for application use where the model doesn't need to be at full fidelity. It's the practical lever for running capable models on modest hardware.

**Q8. How do you handle an LLM API that's down or rate-limiting you?**
Timeout on the call, retry with exponential backoff for transient errors and 429s, a circuit breaker if it's persistently down, and a fallback so the feature degrades gracefully. In the RF generator, if the LLM call fails, a regex fallback handles extraction so the tool stays at 100% uptime — the LLM is an enhancement, not a hard dependency. And a semaphore caps concurrency so I don't self-inflict rate limits (bias auditor: 500 calls capped to 10 in-flight).

**Q9. What temperature do you use and how do you reason about it?**
Task-dependent. Low (0–0.1) for anything that must be consistent and factual — extraction, parsing, operational fix suggestions, judge scoring — because the same input should give the same output and I don't want creative variation. Higher (0.7) deliberately when I *want* variance — like the consistency checker, which runs at 0.7 to surface how much the model wavers. Temperature is a knob matched to whether the task wants determinism or diversity.

**Q10. How do you get structured/JSON output reliably from an LLM?**
Provider structured-output mode where available (`responseMimeType: application/json` for Gemini, tool/function calling for others), an explicit prompt ("return ONLY JSON, begin with `{`"), a low temperature, and defensive parsing with a fallback because it'll still occasionally break. The layers matter because no single one is reliable alone — I constrain the model *and* validate the output *and* have a salvage path.

**Q11. How do you evaluate whether a cheaper model is "good enough" to switch to?**
Run both through the same eval suite on a golden set and compare — my eval framework records each model's scores plus latency and token count per test case, so I get a data-driven quality/speed/cost comparison. The decision isn't "the cheap one feels fine"; it's "the cheap one scores within tolerance on the golden set at a fraction of the cost." Model selection becomes a measured trade-off, not a guess.

**Q12. What's the difference between prompt caching and response caching for cost?**
Response caching: identical requests return a stored answer without calling the model (RF generator caches on input hash). Prompt caching (provider feature): a large, reused prompt prefix (system prompt, context) is cached provider-side so you're not charged full input tokens for it on every call. Both cut cost; response caching avoids the call entirely, prompt caching cuts the per-call input cost for repeated context. I use response caching; prompt caching is the lever for large fixed contexts.

**Q13. How do you keep a system working when a provider updates their model and behaviour drifts?**
Detect it and be swappable. Detection: scheduled evaluation against the live model (prompt-regression's weekly drift monitor) alerts when scores shift. Swappability: the provider abstraction means switching models is a config change, not a rewrite. So when a model update degrades behaviour, I know within a week (not via user complaints) and can pin to a specific version or switch providers quickly. Drift is inevitable; the defense is monitoring plus loose coupling.

**Q14. How do you handle streaming responses, and where's your honest gap?**
Streaming yields tokens as generated (SSE / provider `stream=True`) so the user sees output immediately — better perceived latency. It's served via FastAPI `StreamingResponse` with an async generator. My honest gap: EMS buffers responses (5–30s wait, no streaming) and I haven't shipped token streaming yet. But my endpoints are already async, so it's a bounded upgrade — swap the buffered call for a streamed generator. I name it as a gap rather than overclaim.

**Q15. What's the context window and how do you work within it?**
The max tokens (input + output) a model handles per call. Exceed it and you truncate and lose information silently. I work within it by capping input (Financial Parser caps OCR text at 8k chars), keeping top-k retrieval small enough to fit ("stuff" chain with k=5), trimming conversation history, and chunking large documents. Managing the context window is both a correctness concern (don't silently drop content) and a cost concern (tokens cost money).

**Q16. Which providers have you actually integrated, and what does that breadth show?**
Anthropic (Claude Sonnet and Haiku), Google Gemini, and local models via Ollama (qwen2.5) — cloud and local, three ecosystems. That breadth shows I understand the integration patterns are similar (send messages, handle streaming, parse structured output) but the details differ (auth, model names, output modes), and that I choose providers by fit — Haiku for cheap extraction, Sonnet for reasoning, Ollama for privacy, Gemini for the browser tool's free tier. It's provider-agnostic thinking, not lock-in.

**Q17. How would you integrate Azure OpenAI if a role requires it (you haven't used it)?**
Honestly: I haven't used Azure OpenAI specifically, but it's the same OpenAI models behind Azure's endpoint, keys, and deployment-name convention, plus enterprise compliance wrapping. My OpenAI/Anthropic/Gemini integration experience transfers directly — it's a different endpoint and auth, same call pattern and message format. I'd be productive immediately. I don't bluff hands-on Azure; I map it to what I've done and show the transfer is trivial.

**Q18. How do you prevent an LLM from leaking sensitive data or being manipulated?**
Don't send sensitive data you don't need (strip PII — the bias auditor strips demographic labels before the judge sees them), don't log prompts/responses containing sensitive data, treat user/retrieved content as data not instructions (prompt-injection defense), and validate output before any consequential action. For the RF generator's audit trail I log generations for traceability without logging secrets. LLM data security is classic data-handling discipline plus injection awareness.

**Q19. How do you measure and reduce latency in an LLM feature?**
Measure per-stage (embedding, retrieval, generation) to find the bottleneck — usually the generation call. Reduce it by routing to a faster model where quality allows (Haiku ~500ms vs Sonnet's seconds), streaming so perceived latency drops, caching to skip the call entirely for repeats, and running independent calls concurrently (async gather) instead of sequentially. Latency is mostly the model call, so the levers are faster model, streaming, caching, and concurrency.

**Q20. What's the most important judgment call in LLM engineering that separates seniors from juniors?**
Knowing when *not* to use the LLM, or the big LLM. Juniors reach for the most powerful model for everything and put an LLM call in every path. The senior move is the hybrid split — LLM for genuine natural-language understanding, deterministic code for structure (RF generator: Haiku extracts, templates generate, RF parser validates); cheap model for easy cases, strong for hard; local for privacy; a fallback so the LLM isn't a hard dependency. It's engineering judgment about where the LLM adds value versus where it adds cost and unreliability.

---

## 1.18 Claude Code and AI-assisted development

**Q1. Fornax wants someone who can "drive multi-file changes through Claude Code and review the output critically." What does that look like for you?**
It means using Claude Code to make coordinated changes across several files — a refactor, a feature that touches the router, schema, service, and tests — and then *reviewing every diff critically* rather than accepting it blindly. I treat generated code as a draft: I read it, check it against the actual requirements and codebase conventions, run the tests, and correct what's wrong. The "review critically" part is the skill — AI accelerates the typing, but the engineering judgment stays with me.

**Q2. How do you review AI-generated code critically — what do you actually look for?**
Correctness against the real requirement (not just plausible-looking code), consistency with the codebase's existing patterns and naming, security issues (the AI-assisted Docker traps — `python:latest`, secrets in ENV — are things AI-generated code introduces), missing edge cases and error handling, and whether the tests actually test the behaviour. I've seen AI produce confident, wrong code, so I verify against reality — run it, test it — rather than trusting that it compiles-looking means correct.

**Q3. What's the risk of AI-assisted development and how do you mitigate it?**
The risk is accepting plausible-but-wrong code, subtle bugs, or insecure patterns because it *looks* right and came fast. Mitigation: treat it as a draft to verify, keep tests as the source of truth (generated code must pass real tests), review diffs the same way I'd review a colleague's PR, and never let it touch security-sensitive or irreversible code without careful scrutiny. The productivity is real; the discipline is not skipping review because the AI "seems confident."

**Q4. Have you used AI as more than a code generator — as a reviewer or consultant?**
Yes — in EMS I used a structured AI-consultation (`AI_CONSULTATION_PROMPT.md`) to do a robustness review, which surfaced a comprehensive edge-case list — encoding issues, overlapping job dates, prompt injection, bulk-operation safety — that would have taken much longer to find organically. So I use AI both to write code and to *critique* my system's design and find edge cases. It's a thinking tool, not just a typing tool.

**Q5. How does AI-assisted development change your workflow versus not using it?**
It compresses the mechanical work — boilerplate, cross-file refactors, test scaffolding — so I spend more time on design, review, and the hard judgment calls. The 5G pipeline was built with claude-sonnet in the loop. What doesn't change: I still own the architecture decisions, the trade-offs, and the verification. AI shifts where my time goes (less typing, more reviewing and deciding), it doesn't remove the engineering.

**Q6. Where do you NOT trust AI-generated code?**
Security-sensitive code (auth, crypto, input validation), anything irreversible (migrations, deletes), and domain-specific logic where the AI lacks context (it doesn't know our internal libraries — the exact reason the RF generator uses templates, because a browser LLM invents keyword names it doesn't know). For those I write or heavily scrutinise manually. AI is strongest on well-understood, verifiable patterns; weakest where correctness is critical or context is proprietary.

**Q7. How do you keep AI-generated code consistent with your codebase's conventions?**
Give it the context — point it at existing patterns, existing modules, the naming conventions — and then enforce in review that the diff matches. AI defaults to generic patterns; left unguided it'll introduce a different style, a different error-handling approach, an inconsistent structure. I review specifically for "does this look like the rest of our code," and correct drift. Consistency is a review responsibility, not something the AI guarantees.

**Q8. Fornax specifically pairs Claude Code with production LLM work. Why is that combination meaningful to you?**
Because I both *build* LLM systems and *use* LLM-powered dev tools, so I understand the tool from both sides — I know why its output needs critical review because I know how LLMs fail (hallucinated APIs, plausible-wrong code, the same failure modes I built evaluators to catch). That makes me a better critical reviewer of AI-generated code than someone who only consumes it — I know where to distrust it because I've measured where models go wrong.

**Q9. How do you use AI tools without your skills atrophying?**
By staying the decision-maker and reviewer — I understand every change before it merges, I can explain why it's correct, and I could have written it myself. The atrophy risk is accepting code you don't understand; I avoid it by treating AI output as a draft I must comprehend and verify. The skill that matters — judgment, architecture, knowing what "correct" means — is exercised *more* when you review critically, not less.

**Q10. Cursor, Cline, Copilot, Claude Code — do the specific tools matter?**
They're variations on the same capability — AI in the editor doing completion, multi-file edits, and agentic refactors. The underlying skill is identical: prompt it well, review the output critically, verify against tests. I use Claude Code (it's in my core skills) and the pattern transfers to Cursor/Cline/Copilot. The tool is interchangeable; the discipline — critical review, verification, owning the decisions — is what actually matters and it's tool-agnostic.

**Q11. How do you break a large multi-file change into AI-assistable pieces?**
Same as any good engineering: clarify the requirement, identify the files/layers involved, sequence the change so each step is coherent and reviewable, and drive each step with focused context rather than one giant vague prompt. Then review each diff, run tests, iterate. A big change done as one blind AI dump is unreviewable; broken into coherent steps, each is verifiable. The decomposition is the same skill whether or not AI does the typing.

**Q12. What's an example of AI-generated code you rejected or corrected?**
The kind I catch constantly: an AI suggesting `FROM python:latest` (mutable tag, silent breakage), or a secret passed as `ENV` in a Dockerfile (visible in `docker history`), or a `WHERE DATE(col)=...` query that kills an index. These look fine and are wrong — exactly the traps on my Docker checklist and in my SQL debugging. I correct them because I know the failure modes; someone accepting AI output uncritically would ship them.

**Q13. How do you verify AI-generated code actually works, not just looks right?**
Run it and test it — the same standard as my own code. Generated code must pass real tests (integration tests against a real test DB, not mocks that test the mock), and I exercise the actual behaviour, not just check it compiles. "Looks right" is not "works" — LLMs produce confident, plausible, subtly-wrong code, so verification is behavioural, not visual. Tests are the source of truth for AI code exactly as they are for mine.

**Q14. Does using AI to write code make you less able to explain it in an interview?**
No — because I only merge code I understand and could defend. If I can't explain why a change is correct, it doesn't ship. Everything in my projects I can walk through — the design decisions, the trade-offs, the failure modes — because I made those decisions and reviewed the implementation. AI helped type some of it; the understanding is entirely mine, which is the whole point of critical review.

**Q15. How do you use AI to accelerate learning a new technology?**
As a fast, interactive reference and a way to generate examples to study — but I verify against docs and by running things, because AI can be confidently wrong about APIs and versions. It's how I'd ramp on, say, LangGraph or an MCP server quickly: get a working example, understand it, verify it against the real library, then build. It compresses the learning curve without replacing the verification.

**Q16. What's the difference between using AI as autocomplete versus agentic multi-file editing?**
Autocomplete suggests the next line/block as you type — you stay in control line by line. Agentic multi-file editing (what Fornax means) is the AI making a coordinated change across many files from a higher-level instruction — more powerful, but the review burden is higher because more changed at once. I use agentic editing for coherent cross-file work and review the whole diff as a unit, the way I'd review a colleague's PR. More automation means more, not less, review rigour.

**Q17. How do you prompt an AI coding tool effectively?**
Clear intent, relevant context (the files, the conventions, the constraints), the exact requirement, and often the tests I want it to satisfy — the same skill as writing a good spec. Vague prompts get generic, wrong-context output. It's the same prompt-engineering discipline I apply to any LLM: role, constraints, examples, and validation. Good input, reviewable output; vague input, unreviewable mess.

**Q18. Where does AI-assisted development fit in a team, and what standards do you keep?**
It accelerates individual work, but the team standards hold: AI-generated code goes through the same PR review, the same CI (lint, tests), the same conventions. I authored code-review checklists at Nokia; AI code is reviewed against the same bar. The team's quality gates don't relax because the code came from an AI — if anything they matter more, because AI introduces its own class of subtle errors.

**Q19. What's your honest take on how much AI should be trusted in production code?**
Trust it to accelerate, not to decide. It's excellent for boilerplate, refactors, and first drafts on well-understood problems; it's unreliable on correctness-critical, security-sensitive, or proprietary-context code. The right level of trust is "verify everything, own every decision" — the productivity is real and I use it daily, but the accountability for what ships is mine, verified by tests and critical review. That's the balance Fornax's "review the output critically" is asking for.

**Q20. Why does your LLM-engineering background make you better at AI-assisted development specifically?**
Because I know *how* LLMs fail — I built hallucination detectors, faithfulness scorers, and prompt-regression gates precisely to catch confident-wrong output. So when Claude Code generates code, I have a trained instinct for where to distrust it: invented APIs, plausible-but-wrong logic, missing edge cases — the same failure modes I measure in my eval work. Someone who only consumes AI tools doesn't have that calibrated skepticism; I built systems whose entire job is catching where models go wrong.

---

## 1.19 React and frontend integration

**Q1. Ibridge wants "frontend integration awareness" — understanding API consumption from the frontend. How do you demonstrate that?**
I build the React frontends for my own tools, so I design the endpoint *and* consume it — EMS is React+Vite with a chat UI, file upload, and polling; the Financial Parser is React+Vite+Tailwind+Recharts. That means I understand both sides of the contract: what shape the frontend needs, how it handles async job status, error states, and CORS. When Ibridge asks me to "support/debug API issues impacting UI," I've lived both ends of that.

**Q2. Your frontend calls the API and the browser blocks it, but Postman works. What's happening?**
CORS. The browser enforces cross-origin rules that Postman doesn't — the frontend on one origin calling the API on another triggers a preflight, and if the API doesn't allow the frontend's origin (or `Authorization` isn't in allowed headers), the browser blocks it. Postman isn't a browser, so it skips CORS entirely. The fix is CORS middleware on the API allowing the specific frontend origin — a very common frontend-integration gotcha.

**Q3. How does a frontend handle a slow backend job without freezing?**
Async job pattern: the frontend POSTs, gets back a job id immediately, and polls a status endpoint until the job is done — EMS does exactly this, the frontend polls `GET /api/job/{id}` while a background thread processes the CV. The UI stays responsive with a progress indicator instead of a frozen spinner on a held connection. It's the client side of the async-write pattern — never make the user wait on a synchronous long call.

**Q4. React re-renders too often and the UI is janky. How do you diagnose?**
Look for new object/array/function references created inline on each render passed as props — a new reference every render makes children re-render even when data didn't change. Fixes: `useMemo`/`useCallback` to stabilise references, proper `key`s in lists, and lifting or splitting state so a change doesn't re-render the whole tree. The common root cause is unstable references, not actual data changes.

**Q5. What's the difference between state and props, and why does it matter?**
Props are passed in from a parent (read-only to the child); state is owned and mutable by the component. It matters for data flow: data flows down via props, changes flow up via callbacks. Getting this wrong — trying to mutate props, or duplicating state that should be derived — causes bugs where the UI and data disagree. In my tools the top component owns state (App.jsx owns everything in the Financial Parser) and passes it down.

**Q6. How do you manage state that many components need?**
Lift it to a common ancestor and pass down via props/callbacks for moderate needs — in the Financial Parser all state lives in App.jsx and orchestrates the pipeline. For larger apps, Context or a state library avoids prop-drilling. The principle: single source of truth for shared state, derive rather than duplicate, and don't scatter the same state across components where they can drift out of sync.

**Q7. A second file upload wipes out the first file's results. You've seen this — what was it?**
A state-machine collision. In the Financial Parser v1.3.0, processing a second file reset the global `status` to `'ocr'`, and since results only render when `status === 'complete'`, the existing results unmounted and disappeared. The fix (v1.3.1): an `updateStatus=false` flag so the "Add More" path processes silently without touching the global status, plus snapshotting current transactions into a local variable to avoid closure staleness during the async loop. A real React state bug with a real fix.

**Q8. What's closure staleness in React and how did it bite you?**
An async callback captures the value of state at the time it was created, not the current value — so during an async loop it can operate on stale data. In the Financial Parser's "Add More" flow I captured `const currentTransactions = [...transactions]` at the start specifically to snapshot the data and avoid losing existing transactions to a stale closure during async processing. It's a classic React async pitfall; the fix is snapshotting the value you need rather than reading through a stale closure.

**Q9. Why React + Vite over Create React App or plain HTML?**
Vite gives fast hot-module-reload in dev and native ES modules with minimal config — a much faster dev loop than CRA. React gives component structure and state management for anything interactive. For my tools (chat UI, upload, live-updating tables/charts) that interactivity justifies React; for a static docs site I used Astro instead (Blog) precisely because it didn't need a runtime framework. Match the tool to whether you actually need client-side interactivity.

**Q10. How do you keep the frontend and backend contract in sync?**
A shared, consistent data shape — in the Financial Parser every component and export path consumes transactions in one defined shape, so adding a field propagates everywhere. On the backend, FastAPI's auto-generated OpenAPI docs give the frontend a live contract to build against. Consistent response shapes and a live schema are what stop the frontend and backend from silently disagreeing about data.

**Q11. TypeScript — where do you actually stand?**
Honest answer: I use TypeScript types in Astro/Blog and I read TS fine, but my production frontends (EMS, Financial Parser) are JSX, not heavily-typed TS. So I'd call it working knowledge, not deep expertise — I understand the value (compile-time safety on the frontend, like Pydantic on the backend) and can work in a TS codebase, but I won't claim I've architected large TS applications. For a role that's TS-heavy on the frontend it's a ramp; for "React working knowledge" I'm solid.

**Q12. How do you handle errors from the API in the UI?**
Consistent error shapes from the backend (a code and a message) so the frontend handles them uniformly, mapped to user-facing messages — the Financial Parser maps HTTP 400 to "Invalid API key," 429 to "Rate limit exceeded, try again." The UI shows a clear error state, not a stack trace or a silent failure. Designing the error contract on the backend and handling it consistently on the frontend is what makes errors debuggable and the UX non-hostile.

**Q13. How does a component fetch data and manage loading/error/success states?**
A state machine of statuses — the Financial Parser drives the UI through idle → reading → ocr → extracting → complete, with an error branch reachable from any stage, and conditionally renders sections based on the status. That's cleaner than scattered boolean flags: the UI is a function of an explicit status value. Loading, error, and success are states, not afterthoughts, and modeling them explicitly prevents the "stuck spinner" and "error shown over stale data" bugs.

**Q14. What's the virtual DOM and why does it matter (briefly)?**
React maintains an in-memory representation of the UI, diffs it against the previous version on state change, and updates only the changed real DOM nodes — avoiding expensive full re-renders of the actual DOM. It matters because it's why React is efficient despite re-rendering components on every state change: the reconciliation only touches what actually changed. It's also why stable `key`s and reference stability matter — they help the diff work correctly.

**Q15. How do you capture a live chart into a PDF export (a real thing you did)?**
jsPDF can't render React components or SVG, so in the Financial Parser I use html2canvas to capture the live Recharts DOM nodes as PNG at 2× density and embed those into the jsPDF report. The constraint is the charts must be in the DOM at export time — which they always are, since export is only offered from the results screen. It's a concrete example of bridging React's rendered output into a non-React export format.

**Q16. How do you build responsive layouts?**
Relative units, flexbox/grid, and breakpoint-based layout changes — the Blog docs site goes single-column on mobile (hamburger menu), sidebar+content on large, and adds the right TOC column on extra-large. Tailwind's responsive prefixes make breakpoint styling declarative. The rule: content reflows and nothing overflows horizontally; wide content (tables, code) scrolls within its own container rather than breaking the page.

**Q17. Why did you use Astro instead of React for the Blog docs site?**
Because a docs site is content-heavy and read-only — it doesn't need a client-side runtime framework. Astro compiles to static HTML at build time with only tiny vanilla-JS scripts for interactivity (search, scroll-spy, dark mode), so the pages are fast and dependency-free. Using React there would ship an unnecessary runtime. It's the same "match the tool to the need" judgment — React for interactive apps, a static generator for content.

**Q18. How do you persist user preferences on the frontend?**
localStorage — the Blog persists dark-mode choice, the Financial Parser stores the (lightly obfuscated) Gemini API key. The dark-mode script reads localStorage *before* first paint to avoid a flash of the wrong theme. localStorage is the simple client-side persistence for preferences and non-sensitive local data; for anything sensitive you're honest that localStorage isn't secure (the Financial Parser's README explicitly says the key obfuscation is not encryption).

**Q19. How do you debug an API issue that's manifesting as a UI bug?**
Check the network tab first — is the request being sent, what's the status, what's the response shape? That immediately localises it: CORS/preflight failure, a 4xx/5xx from the backend, or the frontend mishandling a valid response. Because I build both sides, I can trace it across the boundary — is the endpoint wrong, or is the frontend consuming it wrong? That's exactly the "support/debug API issues impacting UI" Ibridge asks for.

**Q20. What frontend skills are you honest about not having, and how do you frame it?**
I'm honest that I'm not a specialist frontend engineer — I build functional React tools and understand integration deeply, but I haven't done heavy TypeScript architecture, complex state-management libraries at scale, or polished design systems. I frame it as: I'm a backend/AI engineer who is genuinely full-stack-capable — I ship working React frontends and understand the frontend-backend contract from both sides — rather than claiming frontend specialist depth I don't have. That honesty is more credible than overclaiming.

---

## 1.20 Git, Agile, code review, and mentoring

**Q1. Merge vs rebase — when do you use each and what's the rule you never break?**
Merge preserves full history with a merge commit; rebase replays your commits for a clean linear history. I use merge for shared branches and rebase to tidy my own local work before opening a PR. The rule I never break: don't rebase a branch others are working on or that's been pushed and shared — it rewrites history and breaks everyone else's copy. Rebase local/private, merge shared.

**Q2. Walk me through your Git workflow.**
Feature branch off main, small focused commits with clear messages, push, open a PR where CI runs lint and tests and a teammate reviews. Discuss, address feedback, and once approved and CI is green, merge. Small commits and clear messages make review and bisecting easy; the PR + CI gate means nothing merges without automated checks and a human review. It's the standard trunk-based-ish flow.

**Q3. You need to find which commit introduced a bug across hundreds of commits. What do you use?**
`git bisect` — a binary search over commits. You mark a known-good and known-bad commit, and Git checks out the midpoint; you test and mark good/bad, and it halves the range each time until it pins the exact commit that introduced the bug. It's O(log n) instead of checking every commit. Small, focused commits (my habit) make bisect precise — you land on a small change, not a giant one.

**Q4. Someone force-pushed and rewrote shared history. What's the damage and recovery?**
The damage: everyone else's local branch now diverges from the rewritten remote, causing conflicts and potentially lost work when they try to reconcile. Recovery: coordinate — either everyone resets to the rewritten remote (if their work is safe) or you use the reflog to recover the pre-rewrite state. It's exactly why the never-rebase-shared-history rule exists; the fix is prevention. `git reflog` is the safety net for recovering "lost" commits locally.

**Q5. How do you write a good commit message?**
A concise subject line (what changed, imperative mood, ~50 chars) and, when the "why" isn't obvious, a body explaining the reasoning — not just what but why. Good messages make history a narrative you can bisect and understand months later. I keep commits small and focused so each message describes one coherent change, rather than a giant "fixed stuff" dump that's useless for debugging.

**Q6. What did you actually do around code review, beyond participating?**
I authored Python code-review checklists at Nokia — covering thread safety and Docker best practices — that the team adopted as standard, improving code-quality scores ~25%. So I didn't just review PRs; I codified what good review looks like into a reusable standard the team used. That's turning individual review judgment into a team-level process improvement.

**Q7. How do you give code review feedback that's useful, not demoralising?**
Focus on the code not the person, explain the *why* (so it's a lesson, not a diktat), distinguish must-fix (bugs, security) from suggestions (style, preference), and acknowledge good work. I ran 1:1 review sessions mentoring 3 engineers to senior readiness — the goal is to level people up, not just catch mistakes. A good review teaches; a bad one just asserts authority. Concrete, reasoned, prioritised feedback.

**Q8. How did you mentor engineers to senior readiness?**
1:1 review sessions where I didn't just fix their code but explained the reasoning — why thread safety matters here, why this Docker pattern is unsafe, how to think about the failure modes — so they'd internalise the judgment, not just the fix. Mentoring 3 mid-levels to senior and supervising 19 interns taught me that the goal is transferring *how to think*, not handing over answers. You mentor by making your reasoning visible.

**Q9. Describe your Agile process and your track record in it.**
Scrum — sprints, daily standups, sprint planning, review/demo, retro, work tracked as stories in JIRA. My concrete track record: during 5G Core UDM/AUSF testing I delivered Agile sprint reports and kept strict deployment schedules with zero missed deliveries. So it's not theory — I've operated in Scrum under real deadlines with a clean delivery record, in a carrier-grade telecom context where missed deliveries have real consequences.

**Q10. How do you handle a PR that's too large to review well?**
Push back and ask to split it — a giant PR gets rubber-stamped, not reviewed, which defeats the purpose. Coherent, focused PRs (one logical change) are reviewable; a 2000-line grab-bag isn't. It ties to small commits: if the work was built as focused increments, the PRs stay reviewable. When I can't split it, I review it in logical sections rather than pretending I read all 2000 lines carefully.

**Q11. What goes in a good PR beyond the code?**
A description of what changed and why, how it was tested, and any trade-offs or follow-ups. Green CI (lint + tests). A reasonable size. Context so the reviewer isn't reverse-engineering intent from the diff. The PR is a communication artifact, not just a code drop — a good description makes review faster and the history more useful later.

**Q12. How do you resolve a merge conflict without breaking things?**
Understand both sides before resolving — what did each branch intend? — rather than blindly picking one. Resolve to preserve both intents where they're compatible, then run the tests to confirm the resolution is actually correct (a syntactically-clean merge can still be semantically broken). Conflicts are where subtle bugs sneak in, so I verify behaviourally after resolving, not just that it compiles.

**Q13. What's your branching strategy and why?**
Trunk-based-ish: short-lived feature branches off main, merged back quickly via PR, main always deployable. Long-lived branches drift and create painful merges; short-lived branches keep integration continuous and conflicts small. For release management you can add release branches, but the core is: branch small, integrate often, keep main green. It pairs with CI — every merge to main is tested.

**Q14. How do you handle a hotfix that needs to go to production urgently?**
Branch from the production state (main/release), make the minimal focused fix, run the critical tests, get an expedited review, and deploy — then ensure the fix is merged back so it's not lost in the next release. The discipline even under urgency: minimal change, still tested, still reviewed (even if fast), and backported. Urgency is not an excuse to skip verification — it's a reason to scope the change tightly.

**Q15. What's the value of CI in your Git workflow specifically?**
It catches problems before human review — lint, tests, build run automatically on every PR, so reviewers focus on design and correctness, not catching a broken build. It makes "it works on my machine" irrelevant and enforces the quality bar consistently. In prompt-regression I extended CI to gate *prompt quality*, not just code — the same principle, automated verification blocking bad merges.

**Q16. How do you keep a shared main branch stable?**
Every merge goes through PR + green CI, no direct pushes to main, and main stays deployable. Broken main blocks the whole team, so the gate (CI must pass, review required) protects everyone. Small, tested, reviewed changes keep it stable; large untested merges are how main breaks. It's a discipline enforced by branch protection, not just goodwill.

**Q17. How do you document your work so the team can maintain it?**
Clear commit messages and PR descriptions, README/architecture docs for projects (my project reports document architecture, decisions, and trade-offs), and good documentation practices generally — which several JDs explicitly ask for. The code-review checklists I authored are a form of team documentation too. Documentation is for the next person (often future-me); I write it so someone can understand not just what the code does but why it's built that way.

**Q18. How do you handle disagreement in a code review?**
Discuss the technical merits with reasoning, not authority — if I think a suggestion is wrong I explain why with evidence, and if I'm the one being reviewed I evaluate the feedback on its merits rather than defending reflexively or caving performatively. The goal is the best code, not winning. Sometimes I'm right, sometimes the reviewer is; either way it's resolved by reasoning about the actual trade-off, and escalated to a lead if genuinely deadlocked.

**Q19. What Agile anti-patterns have you seen and how do you avoid them?**
Standups that become status-report theatre instead of surfacing blockers, stories too big to finish in a sprint, and skipping retros so the same problems recur. I keep standups focused on blockers and coordination, break work into sprint-sized stories, and treat retros as real improvement opportunities. Agile is meant to make delivery predictable and adaptive; the anti-patterns turn its ceremonies into overhead — I keep them purposeful.

**Q20. How did your process discipline show up in a measurable result?**
Two concrete ones: the code-review checklists I authored drove a ~25% improvement in code-quality scores team-wide, and my Agile delivery record on 5G UDM/AUSF testing was zero missed deliveries under strict deployment schedules. So my process work isn't just "I follow Scrum" — it produced measurable quality improvement and a clean delivery record in a demanding carrier-grade environment. Process discipline that shows up in numbers, not just ceremony.

---

## 1.21 Node.js and AWS (honest scope)

**Q1. What's your actual Node.js and AWS experience — be specific.**
At Abjayon I was a Node.js backend + AWS developer: I integrated AWS AppSync and AppFlow to connect frontend/backend pipelines (15% data-retrieval improvement), built and optimised GraphQL and REST APIs, and managed IAM roles for secure resource access and compliance. So my hands-on AWS is AppSync, AppFlow, and IAM — I'm precise about that and don't claim the broader ECS/Lambda/Step Functions/Kinesis surface I haven't run.

**Q2. What is AppSync and what did you use it for?**
AppSync is AWS's managed GraphQL service — it hosts a GraphQL API, handles resolvers, connects to data sources, and manages things like real-time subscriptions. I used it to connect frontend and backend pipelines, building and optimising the GraphQL layer. It's why I have real GraphQL experience — AppSync was the managed GraphQL backend, and I worked with its resolver and schema model.

**Q3. What is AppFlow and where does it fit?**
AppFlow is a managed integration service for moving data between SaaS applications and AWS services without writing custom integration code. I integrated it to connect data pipelines — it handles the data transfer/sync between systems. Combined with AppSync, the two connected frontend/backend data flows, which is where the 15% data-retrieval efficiency improvement came from.

**Q4. What did managing IAM roles involve, and why does it matter?**
IAM (Identity and Access Management) controls who/what can access which AWS resources. I managed IAM roles for secure resource access and compliance — defining least-privilege permissions so services and users could access only what they needed. It matters because over-permissioned roles are a major cloud security risk; least-privilege IAM is foundational AWS security, and it's real hands-on experience I have.

**Q5. The JD lists ECS Fargate, Lambda, Step Functions, Kinesis — you haven't used those. How do you handle that?**
Honestly, and by mapping them to what I *have* done. I haven't run them in production, but I understand them as managed versions of patterns I've built: ECS/Fargate is running the Docker containers I already build; Lambda is event-driven serverless functions; Step Functions is a state-machine workflow (like my agent state machines and NFTRACE's lifecycle states); Kinesis is event streaming. So I ramp fast because the underlying concepts are ones I've implemented — but I won't claim production hours I don't have.

**Q6. Explain Lambda and its trade-offs.**
Lambda runs functions serverlessly — event-driven, auto-scaling, pay-per-invocation, no server management. Trade-offs: cold starts (first invocation after idle is slow), execution time and memory limits, and statelessness (state must live elsewhere). It's great for event-driven, bursty, or glue workloads; less suited to long-running or latency-sensitive-always-warm workloads. I understand the model conceptually and map it to my event-driven/async experience.

**Q7. When would you use ECS/Fargate vs Lambda?**
Fargate runs containers without managing servers — good for long-running services, workloads that don't fit Lambda's time/memory limits, or when you want container control and consistency with your Docker-based dev. Lambda for short, event-driven, bursty functions. Since I build and containerise with Docker already, Fargate is "run my existing containers managed"; Lambda is for the glue/event pieces. I'd choose based on workload shape — long-running service vs short event handler.

**Q8. What's S3 and where does it fit in a system you'd design?**
S3 is durable, cheap object storage for files/media/backups. In the ad-generation API design I sketched, the generated asset goes to S3 and the metadata to PostgreSQL — the classic pattern: binary blobs in object storage, structured metadata in the DB, the DB holds the S3 path. I know this pattern well conceptually (it's the same principle as NFTRACE storing pcap paths, not blobs, in SQLite); S3 is the managed cloud version.

**Q9. What is Step Functions and how does it map to what you've built?**
Step Functions orchestrates a workflow as a state machine — coordinating Lambdas and services with defined states, transitions, retries, and error handling. It maps directly to things I've built by hand: my agent loop is a state machine (states, transitions, a verifier retry edge), and NFTRACE's session lifecycle (STARTING→ACTIVE→STOPPED→MERGED→VALIDATED) is a state machine. So the concept is deeply familiar; Step Functions is the managed AWS way to express it.

**Q10. How does IAM least-privilege actually work in practice?**
You grant each role/user only the specific permissions it needs for specific resources — not broad wildcards. A service that reads one S3 bucket gets read on that bucket, nothing more. I managed IAM roles at Abjayon for exactly this — secure, compliant access. The failure mode it prevents: an over-permissioned role that, if compromised, exposes far more than it should. Least-privilege limits blast radius, which is core cloud security.

**Q11. Node.js is single-threaded with an event loop — how does that relate to what you know from Python async?**
It's the same fundamental model as Python's asyncio — a single-threaded event loop doing non-blocking I/O, where you avoid blocking the loop with synchronous work. Node was async-first from the start; the concepts transfer directly: don't block the event loop, use callbacks/promises/async-await, offload CPU work. My deep understanding of the ASGI event loop and async concurrency in Python maps straight onto Node's model — same principles, different syntax.

**Q12. REST vs GraphQL — you've built both. When each?**
REST for simple, well-defined resources and public/browser APIs — straightforward, cacheable, universal. GraphQL when clients have diverse data needs and you'd otherwise build many endpoints or make multiple round-trips — it lets the client request exactly the fields it wants in one query. I built both at Abjayon; GraphQL (via AppSync) suited the flexible-data-needs case. The trade-off is GraphQL's harder caching, rate-limiting, and query-cost control.

**Q13. How do you secure a Node.js/AWS backend?**
Same layered principles as any backend plus cloud specifics: IAM least-privilege for resource access (which I did), HTTPS, input validation, parameterized queries, authentication/authorization per resource, secrets in a secret manager (AWS Secrets Manager / not in code), and CloudWatch for monitoring. The API-security fundamentals (BOLA checks, rate limiting, no leaked errors) are language-agnostic; the AWS layer adds IAM and managed secrets.

**Q14. What's CloudWatch and how does it map to your monitoring knowledge?**
CloudWatch is AWS's monitoring — logs, metrics, alarms. It maps directly to my monitoring approach: structured logs with request ids, RED metrics (rate, errors, latency p95/p99), and alerting on thresholds. CloudWatch is the managed AWS implementation of what I described for production monitoring generally — I understand the *what* (structured logs, metrics, alarms) and CloudWatch is the *where* on AWS.

**Q15. How would you deploy a containerised app to AWS?**
Build and pin the Docker image (multi-stage, slim, non-root — my checklist), push to ECR (the registry), and run it on ECS/Fargate or EKS, with a load balancer in front, secrets injected at runtime from Secrets Manager, and CloudWatch for logs/metrics. I've done the containerisation and deployment-pattern half deeply; the AWS-specific orchestration (ECS/EKS/ECR) I understand as the managed target for the containers I already build. Honest about the ramp, clear on the fundamentals.

**Q16. What's API Gateway and how does it relate to what you've built?**
API Gateway is AWS's managed entry point — auth, rate limiting, routing, SSL termination at the edge. It maps to the API-gateway pattern from my system-design notes: verify the JWT once at the edge, check revocation, forward trusted headers downstream. I've built the equivalent as FastAPI middleware; API Gateway is the managed version. Same role — edge auth, rate limit, route — different implementation.

**Q17. How do you handle configuration and secrets on AWS?**
Secrets in AWS Secrets Manager or Parameter Store, injected at runtime, never in code or baked into images — the same principle as my Docker checklist (no build-time secrets, they're visible in `docker history`). IAM controls which service can read which secret (least-privilege). The rule is consistent everywhere: secrets in a managed store, injected at the last moment, access scoped by IAM.

**Q18. Kinesis / event streaming — honest gap, how do you frame it?**
I haven't used Kinesis. It's a managed stream for high-throughput event ingestion — producers write to a stream, consumers process it, with partitions and ordering. My experience is request/response and batch, not high-volume streaming, so I'm honest it's a gap. I understand the concepts (partitions, consumer groups, at-least-once delivery, backpressure) but haven't run a streaming pipeline in production — I'd frame it as a genuine growth area, not bluff it.

**Q19. Given your AWS is AppSync/AppFlow/IAM, how do you pitch yourself for a broader-AWS role?**
As someone with real AWS foundations (managed GraphQL, data integration, IAM security) plus deep experience in the patterns the other services manage — I containerise with Docker (→ ECS/EKS), build state machines (→ Step Functions), design object-storage-plus-metadata systems (→ S3+RDS), and know monitoring (→ CloudWatch). So I'm not starting from zero on the broader surface; I know the underlying patterns and have hands-on AWS security experience. I'd ramp on the specific services fast, and I'm honest about which I've run versus understand.

**Q20. Why does your Node.js/AWS background matter for an AI-engineering role that's mostly Python?**
It shows I'm not a one-language, one-cloud engineer — I've built backends in Node and Python, worked with AWS managed services and IAM security, and done GraphQL and REST. That breadth means I understand systems, not just a stack: the event-loop model transfers between Node and Python async, the security principles transfer across clouds, and the API-design skills are language-agnostic. For an AI role, that systems-engineering breadth is exactly the "brings systems engineering depth to AI integration" angle in my profile — I integrate AI into real production systems, whatever the stack.

---

*End of Section 1 Q&A — 420 questions across 21 matched topics. Each answer leads with the problem a real team hits, names the fix, and ties to concrete project evidence. Pair this with [MASTER_STUDY_NOTES.md](MASTER_STUDY_NOTES.md) Section 2 (gap deep-dives) and Section 3 (project discussions).*




