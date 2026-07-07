# 🎯 INTERVIEW-DAY CHEAT SHEET — Senior Backend Python Dev (IBridge)
*Print this. Glance morning-of. You've done the work. Breathe.*

---

## OPENER — 2-min "tell me about yourself"
Backend Python engineer, 5+ yrs → FastAPI services, async pipelines, SQL schemas, reliability.
- **NFTRACE** → FastAPI lifecycle endpoints + Redis session isolation + SQLite persistence → **−50% pipeline validation time**
- **5G pipeline** → async Pyshark + semantic vector search + LLM + Redis caching → **70% auto-resolve, −55% MTTR (Mean Time To Resolution), hours→seconds**
- **Brane** → PostgreSQL RBAC (Role-Based Access Control) schema + gRPC (Google Remote Procedure Call) gateway (stateless, multi-provider) → **reliable multi-agent runtime**

**Core = API design, DBs, async, performance. AI is a tool I integrate AND a tool I code with — exactly this team's style. Immediate joiner.**

---

## THE REFRAME (always say it the backend way)
| Don't say | Say instead |
|---|---|
| "LLM pipeline" | "async pipeline integrating a 3rd-party inference service" |
| "prompt engineering" | "request assembly + response validation with retry" |
| "agent loop" | "stateful processing loop with verifier/correction retry" |
| "gRPC gateway" | "microservice, stateless horizontal scaling, provider routing" |
| "I'm an AI engineer" | "backend engineer who builds AI-integrated systems" |

---

## FASTAPI (the job's centrepiece)
- `async def` = awaitable I/O on event loop | `def` = runs in threadpool | **never block loop with sync I/O inside async**
- Blocking trap: `requests` → use `httpx.AsyncClient`; `psycopg2` → use `asyncpg`; `time.sleep` → `asyncio.sleep`
- `Depends` = DI: lifecycle (yield → cleanup), testability (`dependency_overrides`), composable auth chains
- `response_model` = security boundary, not just serialization — prevents leaking internal fields
- 422 = Pydantic auto-validation | 201 create | 204 no-content | 401 unauthn | 403 unauthorised | 409 conflict
- Multiple Uvicorn workers behind Gunicorn: `gunicorn -k uvicorn.workers.UvicornWorker -w 4`
- CORS (Cross-Origin Resource Sharing): **never `*` with credentials** → explicit origins + `Authorization` in `allow_headers`
- Testing: `httpx.AsyncClient` + `dependency_overrides` — not patching internals

---

## AUTH (JWT/OAuth — in the JD)
- JWT = `header.payload.signature`, base64url — **signed not encrypted** (payload visible in DevTools)
- Verify: signature + `exp`. Stateless = no DB lookup per request
- **Don't** put email/role/sensitive data in payload — it's readable by anyone
- Access token (15–30 min) + refresh token (httpOnly cookie) + Redis blacklist for logout/revoke
- AuthN = who you are | AuthZ = what you're allowed (RBAC)
- OAuth2 = delegated authorization | OIDC = adds identity (ID token) on top
- HS256 = symmetric shared secret | RS256 = asymmetric (gateway verifies without signing key)
- OWASP #1 = BOLA (broken object-level auth) — authenticate ✓, but check object ownership per route

---

## SQL (LIVE TEST — write by hand)
**Execution order:** FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT

| Pattern | SQL |
|---|---|
| 2nd highest per dept | `DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC)` then `WHERE rnk = 2` |
| No orders (anti-join) | `LEFT JOIN orders o ON ... WHERE o.id IS NULL` |
| Duplicates | `GROUP BY email HAVING COUNT(*) > 1` |
| Running total | `SUM(amt) OVER (ORDER BY month)` |

- WHERE pre-group / HAVING post-group
- Index = fast reads + slow writes; composite index: leftmost prefix rule
- EXPLAIN ANALYZE → look for Seq Scan on large table = missing index
- N+1 → eager load (`selectinload`/JOIN) | ACID | parameterized queries (never string-concat)
- **Under pressure:** state your approach first, narrate as you write, catch your own errors out loud

---

## SNOWFLAKE (basic — don't overclaim)
Cloud data warehouse (OLAP — Online Analytical Processing, not OLTP — Online Transaction Processing). **Key idea: separated storage & compute** (virtual warehouses).
- Columnar storage → fast aggregations, no manual indexes (micro-partition pruning instead)
- Time Travel, zero-copy cloning, standard SQL + `snowflake-connector-python`
- **Honest framing:** "PostgreSQL is my primary; Snowflake is standard SQL with a Python connector — I'd treat it as another SQL source behind a repository layer and ramp quickly."

---

## SYSTEM DESIGN (framework — use for any "design X")
1. Clarify requirements (functional + NFRs — Non-Functional Requirements: scale, latency, consistency)
2. Estimate load (RPS, data size)
3. API design
4. Data model
5. Architecture: client → LB/gateway → services → DB/cache/queue
6. Scale: cache, replicas, queue, shard
7. Reliability: timeout/retry/circuit-breaker/fallback
8. **State trade-offs explicitly** — this is what makes you sound senior

**Long task pattern:** POST → 202 Accepted + job_id → Celery worker → GET /jobs/{id} polls status
**Stateless → horizontal scaling | Celery + Redis = durable async | circuit breaker = stops cascade**

---

## PYTHON BACKEND
- GIL: one thread runs bytecode at a time — I/O async doesn't fight it; only CPU-bound threads do
- I/O-bound → asyncio or threads | CPU-bound → multiprocessing / Celery
- Mutable default arg trap: `def f(x=[])` — the list persists; use `None` sentinel
- Generator war story: stream 1M rows without loading into memory
- `response_model` is a security boundary; `Depends` yield for lifecycle; `@lru_cache` for pure functions

---

## DEVOPS / GIT
- Merge = keeps history | Rebase = linear — **never rebase after pushing to shared branch**
- CI = lint + test + build on PR | CD = auto deploy
- Docker: pin base image versions (no `latest`); never put secrets in ENV in Dockerfile (visible in history)
- Structured JSON logs + request IDs | RED metrics (Rate, Errors, Duration) | never log tokens/PII
- Incident response: alert → which service → error logs with request ID → metrics (when did it start?) → recent deploy

---

## DECISION ONE-LINERS ("why X not Y")
| Choice | One-line reason |
|---|---|
| gRPC vs REST | HTTP/2, binary protobuf, typed, streaming — internal service calls; REST for browser/public |
| Redis (NFTRACE) | Shared state across parallel workers — in-memory dict can't cross process boundaries |
| SQLite (NFTRACE) | Lightweight embedded local state; no DB server needed at that scope |
| PostgreSQL (Brane) | ACID + relational integrity for RBAC + junction tables + JSONB flexibility |
| Celery vs BackgroundTasks | Durable/retryable/monitored vs in-process fire-and-forget (lost on restart) |
| Hybrid LLM + templates | Deterministic output correctness; regex fallback = 100% uptime on LLM failure |
| Vector DB (5G) | Semantic fuzzy match of error patterns — brittle rules miss wording variations |
| Async vs threads vs multiprocessing | I/O → async/threads | CPU → multiprocessing |

---

## BEHAVIORAL (STAR + metric — 3 stories)
| Story | One-liner | Metric |
|---|---|---|
| NFTRACE | Decoupled test scenarios from validation with Redis session isolation | −50% validation time |
| 5G pipeline | Semantic vector search + LLM + Redis caching for auto-resolution | 70% auto-resolve, −55% MTTR |
| Brane | Attribute-level RBAC schema + gRPC stateless gateway | Reliable multi-agent execution |

- Mentored 3 → senior | Led 19 interns | Code review checklists → +25% quality | Zero missed deliveries
- **AI tools story:** "Claude as reviewed pair-programmer — I understand every line before it ships. It doubles throughput on boilerplate; design and edge cases are mine."

---

## DANGER ZONE — questions to not bluff
- **"What was the Redis key schema in NFTRACE?"** → `session:{uuid}` → JSON blob of scenario state
- **"What's YOUR specific contribution to Brane?"** → Schema design (identity/junction/RBAC tables), parser hardening, verifier-retry loop — 2 months, own exactly this
- **"How did you measure the 70%?"** → against the prior manual triage baseline — if estimated, say "roughly, observed over [period]"
- **"Walk me through the SQLAlchemy RBAC models"** → honest: "The ORM layer was part of a larger codebase; what I designed was the schema — [describe tables]. I'd need to look up the exact model syntax."

---

## RECOVERY SCRIPTS
- **Blank:** "Let me think through that." → reason aloud → "I haven't used X directly, but based on [related], I'd approach it by..."
- **Wrong answer corrected:** "You're right — I was thinking of [X], which is different. The correct answer is [Y]." Calm. Move on.
- **Mid-answer collapse:** "Actually let me reframe — the core issue is [one clear thing]..."
- **Knowledge gap:** "I don't remember the exact implementation, but the design reasoning was... and the trade-off was..."

---

## ASK THEM (shows seniority)
1. Monolith → microservices today, or already distributed?
2. Snowflake: does backend read from it or feed it?
3. CI/CD setup and where do APIs run?
4. How does the team use AI tools in their workflow?
5. What does success look like in the first 90 days?

---

## LOGISTICS
- **Immediate joiner** — say it early, it's your edge
- **UK shift** → yes, flexible (JD requirement)
- **Location** → confirm on-site/hybrid/remote in Hyderabad
- **Experience gap (5 vs 6-8 yrs)** → "Senior responsibilities: architecture ownership, mentoring to senior level, team-wide process standards. Weight depth and impact over year count."
- **Snowflake gap** → "Basic understanding — architecture is clear, Python connector is standard, ramp is fast."
- **Brane 2 months** → "Scoped engagement, available immediately — gives me focused production depth I'm actively building on."

---

*Backend-first. AI second. Honest on gaps. Confident on ramp. You've got this.*
