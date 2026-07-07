# 01 — FastAPI Deep Dive
**Interview: Monday June 22 | Role: Senior Backend Python Dev (IBridge)**

> **jak's honest warning:** You shipped with AI assistance and don't remember the internals. Senior interviewers probe with follow-ups until the story breaks. This guide gives you **mental models + production patterns** you can internalize — not surface definitions. For every section, the goal is: *"Would this answer make an interviewer trust this person with a production system?"*

---

## SECTION 1 — Why FastAPI (be ready for "why FastAPI over Flask/Django?")

### Interviewer is testing
They want to know if you **chose** FastAPI deliberately or just used it because the last project did. A senior engineer explains trade-offs. A junior recites the marketing page.

### Senior signal
You lead with the **problem space**, not the feature list. "We needed high-concurrency async I/O for external API calls — FastAPI's ASGI (Asynchronous Server Gateway Interface) model was the right fit. Flask would've required threads or greenlets, which we didn't want."

### The comparison table

| | Flask | Django | FastAPI |
|---|---|---|---|
| **Born** | 2010 | 2005 | 2018 |
| **Server model** | WSGI (sync) | WSGI (sync) | ASGI (async-native) |
| **Async support** | Bolt-on (Flask 2+, limited) | Bolt-on (3.1+, limited) | First-class — built for it |
| **Data validation** | None built-in | Forms + DRF serializers | Pydantic — automatic, type-driven |
| **Auto API docs** | None | None (DRF basic) | OpenAPI/Swagger at `/docs` out of the box |
| **ORM / "batteries"** | None | Full ORM, admin, auth | None (bring your own — stays lean) |
| **Performance** | Medium | Medium | Fastest of the three (near Node/Go benchmarks) |
| **Best for** | Small tools, quick prototypes | Full-stack web, content/CMS | High-throughput REST/async APIs |

### Ready-to-say spoken answer (3–4 sentences)
> "Flask is great for small services but it's sync-only with no built-in validation or docs — you're constantly bolting things on. Django gives you everything including the kitchen sink, which is powerful for full-stack apps but heavyweight if you just need an API. FastAPI was designed from scratch for async APIs: it's ASGI-native so it handles hundreds of concurrent I/O-bound requests without spawning threads, Pydantic validates every request automatically from your type hints, and you get live OpenAPI docs at `/docs` — which is critical when you're serving a React frontend because the contract is always current without any extra work."

### Veteran layer — what only someone who operated it would say
> "One thing that bites you early: FastAPI's startup and shutdown hooks matter more than people expect. We had a Redis connection pool that wasn't being initialized at startup — every first request paid the cold connection cost. And CORS (Cross-Origin Resource Sharing) configuration — the default `allow_origins=["*"]` is fine locally but gets you a security incident in production the moment someone figures out they can make credentialed cross-origin requests."

### Common weak answers that get candidates rejected
- "FastAPI is fast" — circular, means nothing
- "It has automatic documentation" — every interviewer has heard this; it's the minimum bar
- "Pydantic does validation" — OK but you need to explain *why that matters operationally*
- Reciting the benchmark numbers without context — shows you read the README, not ran the system

### Follow-up questions the interviewer WILL ask
1. "What happens when you mix sync and async endpoints in the same app?" → (see §4)
2. "How does ASGI differ from WSGI (Web Server Gateway Interface) at a runtime level?" → WSGI: one request per thread/process. ASGI: event loop handles many concurrent requests in one thread; uses coroutines to yield while waiting on I/O.
3. "Have you ever had to migrate a Flask service to FastAPI? What was the hardest part?" → async migration, dependency injection patterns, Pydantic schema design

---

## SECTION 2 — Core Building Blocks

### Interviewer is testing
Whether you understand the **contract** between FastAPI, Pydantic, and the HTTP layer — not just "write an endpoint."

```python
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, validator

app = FastAPI(title="Ads API")

class AdCreateRequest(BaseModel):
    title: str
    budget: float

    @validator('budget')
    def budget_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('budget must be positive')
        return v

class AdResponse(BaseModel):
    id: int
    title: str
    # NOTE: no budget_internal_cost here — response_model filters it out
    # This is a security boundary, not just serialization

@app.post("/ads", response_model=AdResponse, status_code=201)
async def create_ad(payload: AdCreateRequest, db=Depends(get_db)):
    ad = await db.create_ad(payload)
    return ad
```

### Senior signal — know WHY each piece exists
- **`response_model`**: Not just serialization — it's a **security boundary**. Without it, you can accidentally return `password_hash`, internal cost fields, system IDs. Say this explicitly.
- **Status codes to know cold**: 201 created, 204 no content (DELETE success, no body), 400 bad request (your business logic says no), 401 unauthenticated (no valid token), 403 unauthorized (valid token, wrong permissions), 404 not found, 409 conflict (duplicate resource), 422 validation error (FastAPI's automatic Pydantic failure), 500 server error.
- **`@validator` / `@field_validator` (v2)**: Input validation belongs in Pydantic, not your service layer. If you're doing `if payload.budget <= 0: raise HTTPException(400)` in a route handler, that's a red flag to an interviewer.

### Veteran layer
> "The thing that catches people is that `response_model` serialization happens *after* your route handler returns. If your SQLAlchemy model has lazy-loaded relationships and you return it directly, you get a `MissingGreenlet` error because the ORM (Object-Relational Mapper) tries to load relationships after the DB session is closed. You have to either use `response_model` with a Pydantic schema that excludes lazy relations, or explicitly load what you need before returning. We hit this in production on our first big SQLAlchemy + FastAPI integration and it was a confusing error."

### Follow-up questions
1. "What's the difference between `response_model` and `Response(content=...)`?" → `response_model` uses Pydantic serialization + filtering. `Response` gives you raw control (custom headers, streaming). Use `response_model` by default.
2. "How do you handle a 204 No Content response?" → `Response(status_code=204)` with no body, and set `response_model=None` to avoid FastAPI trying to serialize null.

---

## SECTION 3 — Dependency Injection (`Depends`) — they WILL ask this

### Interviewer is testing
Understand that DI (Dependency Injection) is not just "cleaner code." They want to hear **testability**, **lifecycle management**, and **scoped resources**.

### Core pattern
```python
async def get_db():
    db = SessionLocal()
    try:
        yield db          # generator — gives you the session
    finally:
        db.close()        # guaranteed cleanup even if handler raises

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_jwt(token)   # raises 401 if invalid/expired
    user = await db.get_user(payload["sub"])
    if not user:
        raise HTTPException(401, "User not found")
    return user

@app.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    return current_user
```

### Senior signal — three reasons to use Depends
1. **Lifecycle management**: `yield` deps get cleanup (`finally`) even on exceptions — DB sessions close, file handles close. This is why you use it for DB sessions instead of a global.
2. **Testability**: In tests you override deps: `app.dependency_overrides[get_db] = lambda: test_db`. Without this, you'd have to patch global state.
3. **Composability**: `get_current_user` itself depends on `get_db` — FastAPI resolves the tree. You don't wire it manually.

### Veteran layer
> "One production gotcha: if you use `Depends` with `yield` for DB sessions and your route handler spawns a background task (`BackgroundTasks`), the DB session may be closed *before* the background task runs — because the dependency cleanup happens when the response is sent, which is before background tasks complete. We had an intermittent 'session is closed' error in production that took a while to pin down. Solution: pass the data you need into the background task instead of passing the session."

### Common weak answers
- "Depends is for dependency injection" — says nothing
- "It's like a decorator" — wrong mental model
- Not mentioning testability — this is the senior signal interviewers look for

### Follow-up questions
1. "How do you test an endpoint that has authentication?" → `app.dependency_overrides[get_current_user] = lambda: mock_user`
2. "Can you have async and sync dependencies in the same chain?" → Yes. FastAPI handles both. Sync deps run in threadpool.
3. "What happens if a dependency raises an exception?" → FastAPI propagates it up; cleanup in `finally` still runs.

---

## SECTION 4 — Async in FastAPI (CRITICAL — high risk for you)

### Interviewer is testing
Whether you understand the **event loop model** at an operational level. This is the section most AI-assisted developers get wrong under follow-ups.

### Mental model first
```
Event Loop = single thread juggling many tasks
Each task runs until it hits an "await" (I/O wait)
While Task A waits for DB response, loop runs Task B, C, D...
When DB responds to Task A, loop comes back to it

This gives you concurrency WITHOUT threads
BUT: if any task blocks (no await), it freezes the ENTIRE loop
```

### Async vs sync endpoints
```python
# Use async def when: you await something (DB, HTTP, Redis)
@app.get("/users/{id}")
async def get_user(id: int, db=Depends(get_async_db)):
    return await db.fetch_user(id)    # yields to event loop while waiting

# Use def (sync) when: you call blocking libraries with no async version
@app.get("/report")
def generate_report():
    return heavy_pandas_computation()   # FastAPI runs this in threadpool
    # Do NOT make this async — it would block the event loop
```

### The blocking trap — the #1 production mistake
```python
# WRONG — kills concurrency for your entire app
@app.get("/data")
async def get_data():
    import requests
    response = requests.get("https://api.external.com/data")  # BLOCKS event loop
    return response.json()

# RIGHT
@app.get("/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.external.com/data")  # yields
    return response.json()
```

**Blocking culprits to know cold:**
- `requests` library → use `httpx.AsyncClient`
- `psycopg2` → use `asyncpg` or `databases` library
- `time.sleep()` → use `asyncio.sleep()`
- Heavy CPU work (pandas, ML inference) → offload to process pool or Celery worker

### Senior signal
> "Async doesn't make things *faster* — it makes the server handle more concurrent requests efficiently. If you have 100 users hitting the API simultaneously and each request spends 50ms waiting on a DB call, async means all 100 can be in-flight at the same time. With sync+threads you'd need 100 threads, which is expensive. But async is not a silver bullet for CPU-bound work — for that you need actual parallelism (multiprocessing, Celery workers)."

### Veteran layer
> "The failure mode that's hardest to debug: you have an `async def` endpoint that works fine in dev but occasionally stalls under load in production. The culprit is usually one dependency that's doing blocking I/O — maybe a third-party library that hasn't been updated to support async. Under low traffic you don't notice because requests don't pile up. Under load the event loop gets stuck for 200ms at a time and P99 latency spikes. We found it by adding per-dependency timing logs and looking for the outlier."

### Follow-up questions
1. "How do you run CPU-bound work without blocking?" → Offload to `ProcessPoolExecutor` via `asyncio.run_in_executor`, or push to Celery worker.
2. "What is the GIL (Global Interpreter Lock) and does it affect FastAPI async?" → GIL exists but async I/O doesn't release the GIL — it simply doesn't need to because I/O-bound async yields *voluntarily* at await points. GIL matters for CPU parallelism, not async I/O.
3. "How would you test that an endpoint doesn't accidentally block?" → Load test with `locust` or `k6`, watch event loop lag metrics, or use `asyncio-throttle` / `aiomonitor`.

---

## SECTION 5 — Middleware, CORS, Lifecycle

### Interviewer is testing
Production awareness: logging, tracing, startup/shutdown correctness.

### Middleware in production
```python
import time, uuid
from fastapi import Request

@app.middleware("http")
async def request_id_and_timing(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.monotonic()
    
    response = await call_next(request)
    
    duration_ms = (time.monotonic() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
    
    # structured log — parseable by Datadog/CloudWatch
    logger.info("request_complete", extra={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": duration_ms,
    })
    return response
```

### CORS — know the production config
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.yourcompany.com"],  # NEVER "*" in production with credentials
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Veteran layer**: `allow_origins=["*"]` with `allow_credentials=True` is **invalid** — browsers reject it. You will see this error in production when the React team asks why auth requests fail. The fix is specific origins. Know this cold.

### Lifespan (startup/shutdown)
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.db_pool = await create_db_pool()
    app.state.redis = await aioredis.create_redis_pool(REDIS_URL)
    yield
    # shutdown
    await app.state.db_pool.close()
    app.state.redis.close()

app = FastAPI(lifespan=lifespan)
```

**Why this matters**: if you initialize connection pools *inside* route handlers (per-request), you create a new pool on every request — connection exhaustion under load. Startup hook creates the pool once; route handlers reuse it via `app.state` or dependency injection.

---

## SECTION 6 — Error Handling & Validation

### Senior pattern: uniform error envelope
```python
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class AppError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}}
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "fields": exc.errors()}}
    )
```

### Senior signal
> "Consistent error shape is critical for frontend teams. If every endpoint returns errors differently — sometimes `{"detail": "..."}`, sometimes `{"message": "..."}`, sometimes raw 500 HTML — the React team has to write special-case error handling for every endpoint. A uniform `{"error": {"code": "...", "message": "..."}}` envelope means one error interceptor handles everything. We defined this contract before writing the first endpoint."

### Validation layers — know where each lives
1. **Pydantic** → input shape, types, basic constraints (field-level, at the HTTP boundary)
2. **Service layer** → business rules ("budget must not exceed campaign limit")
3. **Database** → integrity constraints, unique indexes (last line of defense)

Don't do business validation in Pydantic. Don't do field-type validation in the service layer. Each layer has its job.

---

## SECTION 7 — Background Tasks vs Celery

### When each
| | BackgroundTasks | Celery |
|---|---|---|
| **Execution** | In-process, after response | Separate worker process(es) |
| **Durability** | Lost if process restarts | Persisted in broker (Redis/RabbitMQ) |
| **Retry** | No | Yes (configurable backoff) |
| **Scheduling** | No | Yes (Celery Beat) |
| **Monitoring** | Nothing built-in | Flower, task state tracking |
| **Use for** | Quick, low-stakes fire-and-forget | Anything important, long, or retryable |

### Veteran layer
> "BackgroundTasks seems fine until your first deploy during high traffic. Process restarts drop all in-flight background tasks silently. We used BackgroundTasks for 'send welcome email' and found out during an incident that emails weren't being delivered because the server was doing a rolling restart. Moved it to Celery with a Redis broker — now tasks survive restarts and we can see exactly which ones failed."

### Senior signal
Be ready to say: "I'd use BackgroundTasks only for things where loss is acceptable — analytics pings, non-critical logs. Anything user-visible or revenue-critical goes to Celery."

---

## SECTION 8 — Performance & Scalability

### Deployment architecture (know this cold for the JD)
```
Internet
   ↓
Load Balancer (nginx / AWS ALB)
   ↓
[Gunicorn -k uvicorn.workers.UvicornWorker -w 4]
   ├── Uvicorn Worker 1 (event loop, handles async I/O)
   ├── Uvicorn Worker 2
   ├── Uvicorn Worker 3
   └── Uvicorn Worker 4
       ↓               ↓
   PostgreSQL       Redis
  (asyncpg pool)   (cache + broker)
```

**Why this setup?**
- **Gunicorn** manages worker lifecycle (spawns, restarts crashed workers, graceful shutdown)
- **Uvicorn workers** run the async event loop
- **`-w 4`**: rule of thumb is `2 * CPU_cores + 1`
- Single Uvicorn without Gunicorn: no process supervision — one crash takes down the service

### Connection pooling — mandatory
```python
# Wrong: new connection per request
@app.get("/data")
async def get_data():
    conn = await asyncpg.connect(DATABASE_URL)  # expensive! TCP handshake every time
    ...

# Right: pool at startup, reuse per request
# In lifespan:
app.state.db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
```

### Caching with Redis — the production gotcha
```python
# Naive cache
async def get_campaign(id: int):
    cached = await redis.get(f"campaign:{id}")
    if cached:
        return json.loads(cached)
    campaign = await db.fetch(id)
    await redis.set(f"campaign:{id}", json.dumps(campaign), ex=300)
    return campaign
```

**Veteran layer**: "The real question isn't whether to cache — it's cache invalidation. When does `campaign:{id}` become stale? If you update a campaign and the cache still serves the old version for 5 minutes, the frontend shows wrong data. We moved to event-driven invalidation: on any campaign write, the service publishes an event and the cache layer deletes the key. TTL becomes a safety net, not the primary expiry mechanism."

### Performance checklist
- [ ] Async DB driver (asyncpg, databases, SQLAlchemy async)
- [ ] Connection pooling (DB + Redis)
- [ ] Reusable `httpx.AsyncClient` (not per-request)
- [ ] Pagination on all list endpoints (limit/offset or cursor-based)
- [ ] Timeouts on all outbound HTTP calls (`httpx timeout=10.0`)
- [ ] Retries with exponential backoff for flaky third-party APIs
- [ ] Request ID in every log line (correlation)
- [ ] `/health` endpoint for load balancer checks

---

## SECTION 9 — Authentication (JWT/OAuth — in the JD)

### JWT implementation
```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token")
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")
    return await db.get_user(user_id)
```

### Senior signal — JWT trade-offs
> "JWT is stateless — no DB lookup on every request, which is great for performance. But you lose the ability to invalidate individual tokens before expiry. If a user logs out or gets compromised, the token is still valid until `exp`. Solutions: short expiry (15-30 min) + refresh tokens, or a token blacklist in Redis (reintroduces state but only for invalidated tokens). We used short-lived access tokens with refresh tokens stored as httpOnly cookies."

### Veteran layer
> "The subtle JWT mistake is putting too much data in the payload. JWT is signed, not encrypted — anyone can base64-decode the payload. We had a developer put the user's email and role in the token 'for convenience' and it was visible in the browser Network tab. Anything sensitive goes server-side. The token should carry only what you need to look up the user: the `sub` (user ID) and maybe `scope`."

---

## SECTION 10 — Project Structure (senior signal)

```
app/
  main.py              # app factory, lifespan, include_router
  api/
    routers/
      ads.py           # APIRouter for /ads domain
      campaigns.py
      auth.py
  schemas/             # Pydantic request/response models (ONLY these cross the HTTP boundary)
  models/              # SQLAlchemy ORM models (NEVER returned directly from routes)
  services/            # business logic — no HTTP concepts here
    ad_service.py
    campaign_service.py
  repositories/        # DB access — one per domain (optional but clean)
  core/
    config.py          # pydantic-settings, reads from env
    security.py        # JWT utils
  db/
    session.py         # engine, SessionLocal
    migrations/        # Alembic
  tests/
    test_ads.py
    conftest.py        # fixtures: test client, override deps
```

### Why this structure matters to an interviewer
- **Separation of concerns**: Routes don't contain business logic. Services don't know about HTTP. DB models never leave the repository layer.
- **Testability**: You can test services without spinning up FastAPI. You can test routes without a real DB (override deps).
- **Onboarding**: New dev finds the campaign endpoint in `api/routers/campaigns.py`, business logic in `services/campaign_service.py`. No hunting.

---

## SECTION 11 — Testing FastAPI (senior role expects this)

### Async test setup
```python
# conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import get_db

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture
def authenticated_client(client):
    # Override the auth dependency — test without real JWT
    app.dependency_overrides[get_current_user] = lambda: User(id=1, email="test@test.com")
    yield client
    app.dependency_overrides.clear()
```

```python
# test_ads.py
@pytest.mark.asyncio
async def test_create_ad_returns_201(authenticated_client, mock_db):
    response = await authenticated_client.post("/ads", json={"title": "Test Ad", "budget": 100.0})
    assert response.status_code == 201
    assert response.json()["title"] == "Test Ad"

async def test_create_ad_rejects_negative_budget(authenticated_client):
    response = await authenticated_client.post("/ads", json={"title": "Test", "budget": -50.0})
    assert response.status_code == 422
```

### Senior signal
> "The key testing principle is: override dependencies in tests, never patch internals. `app.dependency_overrides` gives you a clean seam — you swap the DB, auth, and external clients without touching production code. If you're using `unittest.mock.patch` to stub inside route handlers, that's a test structure problem, not a mock problem."

---

## SECTION 12 — API Versioning

### The three approaches
```python
# Option 1: URL prefix (most common, easiest)
app.include_router(v1_router, prefix="/v1")
app.include_router(v2_router, prefix="/v2")

# Option 2: Header-based (cleaner URLs, harder to test/cache)
# X-API-Version: 2

# Option 3: Query param (avoid — pollutes every URL, caching nightmares)
# GET /users?version=2
```

### Senior signal
> "URL prefix versioning is the pragmatic choice for most teams — it's explicit, easy to route in nginx, easy to test, and easy to document. Header versioning is cleaner but breaks browser testing, makes caching harder, and confuses most API consumers. We used `/v1/` prefix. When v2 came, we kept v1 running with a deprecation warning header (`Deprecation: true`, `Sunset: 2025-01-01`) and gave consumers 3 months to migrate."

---

## SECTION 13 — 15 Likely Interview Questions with Senior Answers

### Q1: Sync vs async endpoint — when each?
**Senior answer**: "Use `async def` when you're awaiting I/O — DB queries with an async driver, outbound HTTP with httpx, Redis reads. Use regular `def` for CPU-bound or blocking library calls — FastAPI runs those in a threadpool automatically so they don't block the event loop. The mistake is using `async def` with blocking calls like `requests.get()` — that freezes the event loop for every concurrent user."

---

### Q2: How does dependency injection work and why use it?
**Senior answer**: "FastAPI's `Depends` creates a dependency tree that it resolves before calling your route handler. The three reasons I use it: lifecycle management — yield deps get guaranteed cleanup even on exception, so DB sessions always close. Testability — `dependency_overrides` lets you swap real implementations in tests without patching internals. DRY — auth logic, pagination params, DB sessions are defined once and composed anywhere."

---

### Q3: How do you handle auth in FastAPI?
**Senior answer**: "JWT for stateless auth: the token carries a `sub` (user ID), we verify the signature and expiry in a `Depends(get_current_user)` dependency. For sensitive operations, short-lived access tokens (15-30 min) plus refresh tokens stored as httpOnly cookies — so they're not accessible to JavaScript. The trade-off with JWT is you can't invalidate individual tokens without a blacklist, so we keep expiry short and use a Redis blacklist for logout/revoke events."

---

### Q4: How do you validate requests?
**Senior answer**: "Validation is layered. Pydantic handles input shape and type constraints at the HTTP boundary — field types, required fields, string patterns, numeric ranges. Business rule validation — 'this campaign budget can't exceed account limit' — lives in the service layer and raises domain exceptions that get translated to HTTP errors by exception handlers. Database constraints are the last line of defense for integrity. You don't want business rules scattered across all three layers."

---

### Q5: How do you make a FastAPI service scale?
**Senior answer**: "Horizontal and vertical. Vertically: multiple Gunicorn/Uvicorn workers, async DB drivers with connection pooling, Redis for hot reads, timeouts and retries on outbound calls, paginated responses. Horizontally: stateless service design — no session state on the server, so any instance can handle any request — then you put it behind a load balancer and add instances. For async CPU-bound work like report generation, Celery workers that scale independently from the API tier."

---

### Q6: BackgroundTasks vs Celery?
**Senior answer**: "BackgroundTasks is in-process fire-and-forget — lightweight, no infrastructure, but lost on process restart, no retry, no monitoring. I use it for things where loss is acceptable: analytics pings, non-critical cache warming. Anything user-visible, financial, or that needs retry goes to Celery with a Redis broker — tasks are persisted, retried on failure, and visible in Flower. The production lesson: you find out BackgroundTasks drops tasks during deploys, which is exactly when you don't want to lose them."

---

### Q7: How do you handle CORS for the React frontend?
**Senior answer**: "CORSMiddleware in FastAPI, with explicit allowed origins — never `*` with credentials because browsers reject that combination. I configure it per environment: localhost:3000 in dev, the production domain in prod, both in staging. The common production gotcha is forgetting to allow the `Authorization` header in `allow_headers` — the preflight OPTIONS request gets blocked and auth calls silently fail."

---

### Q8: How do you version an API?
**Senior answer**: "URL prefix versioning — `/v1/`, `/v2/`. It's explicit, routes cleanly in nginx, easy to test, and works with every API client without special headers. When deprecating, add `Deprecation` and `Sunset` response headers and give consumers a migration window. I avoid header-based versioning — it's harder to test in a browser, complicates caching (Vary header), and most teams aren't set up to handle it cleanly."

---

### Q9: How do you test FastAPI endpoints?
**Senior answer**: "pytest with `httpx.AsyncClient` pointed at the ASGI app directly — no network overhead. The key pattern is `dependency_overrides`: I swap the real DB, auth, and external clients for test doubles without touching production code. That means tests are fast, isolated, and don't need a running database. For integration tests that actually hit the DB, I use a test database with transactions that roll back after each test."

---

### Q10: How do you structure a large FastAPI app?
**Senior answer**: "Domain-based routers: each business domain gets an `APIRouter` in `api/routers/`. Pydantic schemas live in `schemas/` — these are the only models that cross the HTTP boundary, never ORM models directly. Business logic in `services/`, DB access in `repositories/` or directly in services for simpler cases. The rule: routes are thin — they validate input, call a service, return the response. No business logic in route handlers."

---

### Q11: How do you handle third-party API integration failures?
**Senior answer**: "Three layers: timeout, retry, and circuit breaker. Timeout: every outbound httpx call gets an explicit timeout — if the third party hangs, you don't hang with it. Retry with exponential backoff for transient failures (5xx, network errors) using tenacity. Circuit breaker for persistent failures — after N consecutive failures, stop calling the service for a period and return a degraded response, to prevent your service from cascading into failure. I also structured external calls behind an interface so in tests I can swap them for fakes."

---

### Q12: How do you monitor a FastAPI service in production?
**Senior answer**: "Three pillars: structured logging with request IDs so you can trace a request across services; metrics (latency percentiles, error rate, throughput) exposed at `/metrics` for Prometheus or shipped to Datadog; and health checks at `/health` and `/ready` for the load balancer. The request ID middleware adds a UUID to every request and logs it at the start and end with status code and duration. When an error happens, you can pull all logs for that request ID instantly."

---

### Q13: Describe a production issue you debugged in FastAPI.
**Prepare this story** (adapt to be yours):
> "We had a service where P99 latency was spiking to 2 seconds under load while P50 was fine. The async endpoint was making calls to a third-party analytics service. I added per-step timing in the middleware and found the analytics call was taking 1.8s occasionally — the service was slow and we had no timeout. Under high concurrency, slow requests piled up and held event loop coroutines. Fix: added a 500ms timeout to the analytics call, moved it to a BackgroundTask (then later Celery) so it didn't block the response at all. Latency dropped to P99 < 100ms."

---

### Q14: How do you handle database migrations with FastAPI?
**Senior answer**: "Alembic for schema migrations, completely separate from the app startup. I don't run `Base.metadata.create_all()` in production — that bypasses migration history. The CI pipeline runs `alembic upgrade head` before deploying the new app version, or we use a Kubernetes init container that runs migrations before the app pods start. Rollback: each migration has a `downgrade()` function, and we test it in staging before deploying to prod."

---

### Q15: What's your approach to API security beyond auth?
**Senior answer**: "Five layers: Auth (JWT with short expiry). Rate limiting (per-IP and per-user, using Redis counters — blocks brute force and abuse). Input validation (Pydantic rejects malformed input at the boundary — prevents injection attempts from reaching business logic). `response_model` to prevent accidental data leakage. HTTPS everywhere with HSTS (HTTP Strict Transport Security) headers. And dependency auditing in CI — `safety check` on requirements to catch known CVEs in dependencies."

---

## Quick-Reference: Interview Day Cheat Sheet

| Topic | The 1-sentence senior signal |
|---|---|
| Why FastAPI | "ASGI async model for concurrent I/O, Pydantic for validated contracts, not just speed benchmarks" |
| Depends | "Lifecycle management, testability via overrides, composable auth chains" |
| async vs sync | "async def for awaitable I/O, sync def for CPU/blocking — mixing them wrong blocks the event loop" |
| JWT | "Stateless but non-revocable — short expiry + refresh tokens solves it" |
| Error handling | "Uniform error envelope defined upfront — one interceptor handles all errors on the frontend" |
| Performance | "Async drivers, connection pools, Redis for hot reads, Celery for durability" |
| Testing | "dependency_overrides, not patching internals — test doubles at the DI seam" |
| CORS | "Explicit origins, never * with credentials, Authorization in allow_headers" |
| Versioning | "URL prefix, Deprecation + Sunset headers for migration windows" |
| Scaling | "Stateless design → horizontal scaling, Gunicorn workers → vertical scaling" |

---

## GAP FILL: Custom Middleware

**Why this matters:** A senior FastAPI question — "how do you add observability/request IDs/timing to every request?" Middleware is the answer.

### What middleware does

Middleware wraps every request before it hits your routes and every response before it leaves. ASGI middleware is a callable that takes an app and returns an app.

### Request ID + timing middleware (production pattern)

```python
import time, uuid
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def add_request_id_and_timing(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()

    response = await call_next(request)

    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
    return response
```

`call_next(request)` invokes the next layer (your route). Everything before it runs on the way in; everything after runs on the way out.

### When to use middleware vs Depends

| Use middleware for | Use Depends for |
|---|---|
| Cross-cutting concerns on ALL routes | Per-route logic (auth, rate limit) |
| Timing, request IDs, access logs | Injecting DB sessions, current user |
| Adding response headers everywhere | Business-logic validation |
| Catching unhandled exceptions globally | Route-specific dependencies |

### Exception handler middleware

```python
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # log exc here
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "request_id": request.state.request_id}
    )
```

**Interview spoken answer:**
> "FastAPI middleware wraps every request before it reaches your routes and every response before it leaves. I use it for cross-cutting concerns — injecting request IDs, timing how long each request takes, and attaching those values to response headers so distributed traces can link logs. The middleware decorator takes a request and a `call_next` callable; you await `call_next(request)` to hand off to the route, and everything after that executes on the way out. The distinction I draw is: middleware for things that apply to all routes uniformly, and `Depends` for per-route logic that needs to know which user or which resource is involved."

---

## GAP FILL: Lifespan Events (Startup / Shutdown)

**Why this matters:** This is how production FastAPI services initialize DB connection pools, Redis clients, and ML models cleanly. The old `@app.on_event("startup")` is deprecated. Interviewers who run FastAPI teams will ask this.

### The modern pattern (`@asynccontextmanager` lifespan)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncpg, redis.asyncio as aioredis

db_pool = None
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    global db_pool, redis_client
    db_pool = await asyncpg.create_pool(dsn="postgresql://...")
    redis_client = await aioredis.from_url("redis://localhost")
    yield
    # --- SHUTDOWN ---
    await db_pool.close()
    await redis_client.close()

app = FastAPI(lifespan=lifespan)
```

Everything before `yield` = startup. Everything after `yield` = shutdown.

### Why lifespan > on_event

- `@app.on_event("startup")` is deprecated since FastAPI 0.93
- Lifespan uses a single context manager — startup and cleanup are co-located
- Works with pytest's `TestClient` — the lifecycle runs correctly in tests
- Catches startup exceptions cleanly (if the DB pool fails to connect, the app doesn't start silently broken)

### The cold-connection war story

The Redis cold-connection problem from the production story: service starts fine, first 100 requests timeout because the Redis client connection is being lazily established. Fix: establish the connection in the lifespan startup block so it's warm before the first request arrives.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = await aioredis.from_url("redis://localhost")
    await redis_client.ping()  # force connection establishment at startup
    app.state.redis = redis_client
    yield
    await app.state.redis.close()
```

**Interview spoken answer:**
> "The modern FastAPI pattern for startup and shutdown is the lifespan context manager — you pass it to `FastAPI(lifespan=lifespan)` and use `@asynccontextmanager`. Everything before the yield runs at startup, everything after the yield runs at shutdown. I use this to initialize database connection pools, Redis clients, and pre-load any ML models — so all connections are warm before the first request arrives. The old `@app.on_event('startup')` still works but it's deprecated. The lifespan approach is better because startup and teardown live together and the lifecycle integrates correctly with FastAPI's test client."
