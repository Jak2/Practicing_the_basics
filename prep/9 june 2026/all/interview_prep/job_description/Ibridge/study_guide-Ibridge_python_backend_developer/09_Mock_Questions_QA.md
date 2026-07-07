# 09 — Mock Interview Bank & Rapid-Fire Q&A

Use Sunday for a full timed mock. **Answer OUT LOUD.** Cover the answer, speak it, then check. Target: crisp 30–90 sec answers.

## A. Rapid-fire one-liners (drill until automatic)
1. **Why FastAPI?** Async-native (ASGI), Pydantic validation, auto OpenAPI docs, type safety, fast.
2. **async def vs def endpoint?** async for awaitable I/O on the event loop; sync runs in a threadpool; never block the loop with sync I/O inside async.
3. **Depends()?** Dependency injection — reusable DB/auth/pagination, testable via overrides.
4. **response_model?** Serializes + filters output so you never leak internal fields.
5. **422 vs 400?** 422 = Pydantic validation error (auto); 400 = generic bad request.
6. **GIL?** One thread runs Python bytecode at a time; use multiprocessing for CPU, async/threads for I/O.
7. **Threading vs multiprocessing vs asyncio?** I/O→threads/async; CPU→multiprocessing.
8. **JWT parts?** header.payload.signature; verified by signature + exp; stateless.
9. **Access vs refresh token?** Short-lived access + long-lived refresh to re-issue without re-login.
10. **AuthN vs AuthZ?** Identity vs permissions.
11. **OAuth2 vs OIDC?** OAuth2 = authorization; OIDC adds identity (ID token).
12. **INNER vs LEFT JOIN?** Inner = matches only; left = all left + nulls.
13. **WHERE vs HAVING?** WHERE pre-group rows; HAVING post-group aggregates.
14. **Index trade-off?** Faster reads, slower writes + storage; read EXPLAIN.
15. **ACID?** Atomicity, Consistency, Isolation, Durability.
16. **N+1 query?** Many lazy queries; fix with eager load / JOIN.
17. **Snowflake key idea?** Separated storage & compute; SQL warehouse for analytics (OLAP).
18. **OLTP vs OLAP?** Transactional row store vs analytical columnar.
19. **Monolith vs microservices?** Simplicity vs independent scale/deploy at complexity cost.
20. **REST vs gRPC?** REST human/ubiquitous; gRPC fast/typed/streaming for internal services.
21. **How handle long task in API?** Enqueue to Celery/Redis, respond fast, poll/webhook.
22. **Horizontal vs vertical scaling?** More instances (needs stateless) vs bigger box.
23. **Cache-aside?** Check cache → miss → DB → populate cache with TTL.
24. **Circuit breaker?** Stop calling a failing dependency to prevent cascade.
25. **Merge vs rebase?** Merge keeps history; rebase linearizes; don't rebase shared branches.
26. **CI vs CD?** CI = auto lint/test/build on push; CD = auto deploy.
27. **Idempotent methods?** GET, PUT, DELETE (and ideally retried POST via idempotency key).
28. **Stateless API benefit?** Any instance handles any request → easy horizontal scaling.
29. **Prevent SQL injection?** Parameterized queries / ORM, never string-concat.
30. **Pydantic role?** Validation + serialization + settings — the FastAPI contract layer.

---

## B. Deep questions — full model answers

> Speak each answer aloud. Target: 90–120 seconds. These are the answers interviewers remember.

---

### B1. Walk me through designing a scalable FastAPI service from request to DB.

A request hits a load balancer and lands on one of N stateless FastAPI workers running under Uvicorn or Gunicorn with Uvicorn workers. The first thing that happens inside the app is middleware — auth token validation, request ID injection, and structured logging so every downstream log line carries a correlation ID. Then it hits the router and into dependency injection: I use `Depends()` to attach a DB session, the current authenticated user, and any pagination params — that keeps the business logic clean and makes unit testing trivial because you just override the dependencies.

The endpoint calls a service layer that contains all the business logic, and the service talks to the DB through an async SQLAlchemy session using `asyncpg` under the hood. I never put raw queries in the route handler. For anything that could be slow — LLM calls, external APIs, heavy computation — I hand off to a task queue, return a 202 with a job ID, and let the client poll or receive a webhook.

The trade-off I always think about is connection pool sizing: too small and you queue requests; too large and you exhaust DB connections. I tune pool size based on actual concurrency profiling, not guesses. On the Nokia 5G remediation pipeline I learned this the hard way — we had async endpoints hammering an upstream service with hundreds of concurrent connections and had to add a semaphore to cap in-flight requests. Stateless workers plus a connection pool with circuit-breaker logic is the pattern that holds up under real load.

---

### B2. How do you implement JWT auth in FastAPI end to end?

At login, the server validates credentials, then mints two tokens: a short-lived access token — fifteen minutes is my default — and a longer-lived refresh token, typically seven days. Both are signed JWTs using python-jose or the newer PyJWT, with HS256 for internal services or RS256 if you need the public key exposed. The access token goes in the Authorization header as a Bearer; the refresh token goes in an HttpOnly Secure cookie so JavaScript can't touch it.

On every protected endpoint I have an OAuth2PasswordBearer dependency that pulls the token from the header, decodes it, checks the signature and expiry, and returns a CurrentUser object. That dependency gets injected via `Depends(get_current_user)`. If the token is expired or the signature is wrong, I raise a 401 immediately — no business logic runs.

The failure mode I watch for in production is token revocation. JWTs are stateless by design, which means if you need to log a user out server-side — say, after a password change or account compromise — you need a blocklist, typically in Redis with a TTL matching the token expiry. I keep the blocklist lean by only storing the token's JTI (JWT ID — unique per-token identifier) claim, not the whole token. The other thing that bites teams is clock skew: if your API servers' clocks drift, tokens look expired or not-yet-valid. NTP sync and a small leeway parameter on decode saves you there.

---

### B3. SQL — 2nd highest salary per department (window function approach)

The cleanest way to do this is with RANK or DENSE_RANK as a window function. Here's the pattern:

```sql
SELECT department, employee_name, salary
FROM (
    SELECT
        department,
        employee_name,
        salary,
        DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rnk
    FROM employees
) ranked
WHERE rnk = 2;
```

I use DENSE_RANK rather than RANK because RANK skips numbers on ties — if two people share the top salary, RANK gives them both rank 1 and no one gets rank 2. DENSE_RANK gives them both rank 1 and the next distinct salary gets rank 2, which is almost always what the business wants. ROW_NUMBER would arbitrarily pick one person if salaries tie, which is wrong for this problem.

The production consideration here is that window functions run after the WHERE clause but before the outer WHERE, which is why you have to wrap it in a subquery or CTE — you can't filter on a window alias in the same SELECT. On large tables I make sure there's an index on (department, salary DESC) or this PARTITION BY scan gets expensive. In Snowflake, which I used at Nokia, the query optimizer handles this well, but you still want to check the query profile for any full table scans.

---

### B4. SQL — customers with no orders in the last 30 days

```sql
-- Option 1: LEFT JOIN anti-join (most portable)
SELECT c.id, c.name, c.email
FROM customers c
LEFT JOIN orders o
    ON o.customer_id = c.id
    AND o.created_at >= NOW() - INTERVAL '30 days'
WHERE o.id IS NULL;

-- Option 2: NOT EXISTS (often better on large order tables)
SELECT c.id, c.name, c.email
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.id
      AND o.created_at >= NOW() - INTERVAL '30 days'
);
```

Both return the same result but behave differently under the optimizer. The LEFT JOIN anti-join is more readable but can produce a large intermediate result set when the orders table is huge. NOT EXISTS short-circuits — the DB stops scanning as soon as it finds one matching order, which is usually faster when most customers do have recent orders.

The trap people fall into is putting the date filter in the WHERE clause instead of the JOIN condition — `WHERE o.created_at >= ...` turns your LEFT JOIN into an INNER JOIN because it filters out the NULLs you were relying on. The date filter must be in the ON clause. Production-wise, this query is a classic candidate for a partial index on `orders(customer_id, created_at)` to avoid a full scan — especially if you're running it as a nightly job or for marketing segmentation at scale.

---

### B5. How would you debug a FastAPI endpoint that's slow under load?

I work from the outside in. First I check whether it's slow for all users or just some — that splits infrastructure problems from data problems. I look at p50 vs p95 vs p99 latency because averages lie; usually there's a small percentage of requests that are catastrophically slow, dragging up the mean.

Then I add timing instrumentation if it isn't there already — middleware that logs time-to-first-byte plus a trace span per logical step: auth check, DB query, external call, serialization. Nine times out of ten the DB query is the culprit. I run EXPLAIN ANALYZE against the slow query in isolation. Classic findings: missing index, N+1 from ORM lazy loading, or a sequential scan on a large table because the query planner chose wrong.

If the endpoint is async but blocking, that's another common trap. A single `requests.get()` call inside an async endpoint blocks the entire event loop — I've seen this cause ten-second cascading latency. The fix is `httpx.AsyncClient` or offloading to a threadpool. On the Nokia remediation pipeline I hit this with Pyshark's synchronous packet parsing — we wrapped it in `asyncio.run_in_executor` and got our throughput back immediately.

If it's a Redis or cache layer issue I check hit rate — a cold cache after a deploy will spike DB load. Circuit breakers help here too; if your cache is the bottleneck, you want to fail fast rather than pile up waiting requests.

---

### B6. Design the backend for an ad-creative generation platform.

I'll tell you what I'd actually build because I designed something close to this at Brane. The core entities are: users, organizations, projects, creative-generation jobs, and generated assets. The job table is central — a user submits a generation request with brand parameters, copy, format specs, the job goes into a queue, workers process it asynchronously, and the asset is stored with a pointer back to the job.

The API layer is FastAPI, stateless, horizontally scalable. Auth is JWT with RBAC (Role-Based Access Control) — organization-level and project-level permissions managed through junction tables, which I built at Brane. Generation jobs go onto a Redis-backed task queue; the API returns a job ID immediately with 202 Accepted. Workers pick up jobs, call the LLM or image generation service, store the result in object storage like S3, and write the asset record to Postgres. The client either polls the job endpoint or receives a webhook when done.

The failure mode I design for from day one is flaky LLM API calls. I build retry with exponential backoff and a dead-letter queue for jobs that fail repeatedly — you never want a failed generation to silently disappear. For scale, the workers are the only stateful-ish piece and they're stateless in terms of assignment, so I can run as many as needed. The Nokia RF Keyword Generator taught me to always keep a deterministic fallback: if the LLM call fails, fall back to template-based generation with regex so the system never returns nothing. Trade-off to discuss: sync generation for simple requests under a second versus async queue for complex multi-asset jobs — I'd support both with a threshold in the job configuration.

---

### B7. How do you integrate and harden calls to a flaky third-party API?

The first thing I do is wrap the third-party client in my own abstraction layer so the rest of the application doesn't know or care about the external API's quirks. That boundary also makes it easy to swap implementations or add caching without touching business logic.

Then I layer in resilience: retry with exponential backoff and jitter for transient failures — jitter is important because without it, all your retries synchronize and you DOS the provider when it comes back up. On top of retry, a circuit breaker that tracks failure rate over a rolling window. If failures exceed a threshold, the circuit opens and I return a cached or default response immediately instead of queuing up slow failing calls. On the Nokia 5G pipeline I used tenacity for retry policies and it handled the configuration cleanly.

I also cache aggressively where the data allows. If the external API returns keyword or classification data that's valid for minutes or hours, I cache in Redis with appropriate TTL. That was directly responsible for the 70% auto-resolution rate on the remediation pipeline — we reduced external calls from hundreds per incident to a handful by caching semantic match results.

The production consideration people miss is timeout configuration. The default httpx or requests timeout is often too long — if the external API hangs, your requests pile up and exhaust your connection pool. I set explicit connect and read timeouts, typically two and five seconds respectively, and treat a timeout as a retryable error. The other thing I add is observability: every external call gets logged with duration, status code, and the provider name as a structured field so I can chart failure rate per vendor in my dashboards.

---

### B8. Explain how you'd take a monolith toward microservices.

The first thing I say is: don't start with microservices as the goal. Start with identifying the specific pain points in the monolith — what's causing deploy risk, what's bottlenecking scale, what team boundary is getting tangled. The answer to those questions tells you which seam to extract first.

My approach is the strangler fig pattern: stand up a new service behind a facade, route traffic to the new service for one domain while the monolith still handles everything else. No big bang migration. On the Brane agent runtime we separated the gRPC gateway from the core execution engine specifically because the gateway needed to scale horizontally while the execution engine had different resource requirements — that was a clean seam because the interface was already well-defined.

The hard parts are shared data and shared auth. I prefer the new service to own its own database — even if it means some initial data duplication — because shared databases between services create hidden coupling that's worse than the original monolith. For auth I set up a central identity service with JWT that all services verify independently; no service calls another service's auth endpoint on the hot path.

The failure mode I've seen most is teams extracting too many services too fast. You end up with distributed monolith problems — services that can't function independently, a network call where a function call used to be, and distributed transactions that are much harder to reason about than a local DB transaction. I'd rather extract two or three well-scoped services and get the operational patterns right — deployment, observability, service discovery — before going further. The saga pattern for cross-service workflows is genuinely harder than a DB transaction; only accept that complexity when you need it.

---

### B9. How do you ensure data integrity across an order workflow?

For operations that live within a single database, I use database transactions — ACID guarantees give you atomicity, so if any step fails, the whole operation rolls back. In SQLAlchemy that's the session context manager with explicit commit and rollback. The pattern I use is: begin transaction, make all writes, then commit; any exception triggers rollback. I also rely on database-level constraints — foreign keys, unique constraints, check constraints — as the last line of defense, because application bugs happen and you don't want bad data in the DB.

When the workflow spans multiple services — say, order service, payment service, and inventory service — a single transaction isn't possible. That's where the saga pattern comes in. Each service performs its local transaction and publishes an event. If a downstream step fails, compensating transactions run to undo the earlier steps: cancel the payment, restore the inventory. You can implement sagas as choreography, where services react to each other's events, or orchestration, where a saga coordinator drives the sequence.

The failure mode I think about most in saga is the partial failure: payment succeeded but inventory update timed out. You need idempotency keys on every step so retries don't double-charge or double-decrement. You need the compensating transactions to also be idempotent. And you need a dead-letter mechanism for compensation failures — a saga that can't compensate needs human review, not silent data corruption. On the Brane platform we used PostgreSQL advisory locks for certain critical operations where we needed serializable isolation without full serializable isolation overhead — cheaper and more targeted.

---

### B10. How do you monitor and log a production API? What do you alert on?

I think about this in three layers: logs, metrics, and traces. Logs are structured JSON — every request gets a correlation ID in middleware, and every log line in that request carries it so I can reconstruct the full lifecycle of any request. I log at INFO for normal operations and ERROR with full stack traces for exceptions. I never log sensitive data — no passwords, no full tokens, no PII in log bodies.

Metrics I expose via a /metrics endpoint in Prometheus format. The core four for a web service: request rate, error rate, latency by percentile, and saturation — that's the USE method plus RED. I track p50, p95, and p99 latency separately because p50 being fine while p99 is ten seconds means a specific slow-query or a tail latency bug.

Alerts I set up on day one: error rate above one percent for five minutes — that's customer-facing breakage. p95 latency exceeding SLA for five minutes. Sudden drop in request rate — could mean a deploy went bad and traffic stopped arriving. DB connection pool saturation. For the Nokia remediation pipeline we also alerted on LLM response time and cache hit rate because those were leading indicators of incident resolution time.

Traces complete the picture — distributed tracing with OpenTelemetry lets you see exactly which DB query or external call inside a request is slow, which is otherwise impossible to diagnose from logs alone. The trade-off is sampling: tracing every request at high volume is expensive, so I trace a percentage plus one hundred percent of requests that hit an error or exceed a latency threshold. That catches the important stuff without burning budget on routine traffic.

---

## C. SQL hands-on set (write from scratch on Friday — no peeking)
```sql
-- 1. 2nd highest salary overall
SELECT MAX(salary) FROM emp WHERE salary < (SELECT MAX(salary) FROM emp);
-- 2. Nth highest per dept (window)
SELECT * FROM (
  SELECT name, dept, salary,
         DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) r
  FROM emp) t WHERE r = 2;
-- 3. Users with no orders
SELECT u.* FROM users u LEFT JOIN orders o ON o.user_id=u.id WHERE o.id IS NULL;
-- 4. Duplicates
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;
-- 5. Top 3 products by revenue per category
SELECT * FROM (
  SELECT p.category, p.name, SUM(oi.qty*oi.price) rev,
         ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(oi.qty*oi.price) DESC) rn
  FROM products p JOIN order_items oi ON oi.product_id=p.id
  GROUP BY p.category, p.name) t WHERE rn <= 3;
-- 6. Running monthly revenue
SELECT month, SUM(amt) OVER (ORDER BY month) running
FROM monthly_rev;
```

## D. Mock interview structure (Sunday, ~60 min, timed)
1. (5 min) "Tell me about yourself" + the AI-vs-backend reframe.
2. (15 min) FastAPI + Python + auth rapid-fire (Section A).
3. (15 min) Live SQL (Section C, write by hand).
4. (10 min) System design (Section B #6).
5. (10 min) Behavioral (2 STAR stories from file 08).
6. (5 min) Your questions for them + close.

**Self-score** each section 1–5. Anything ≤3 → revisit that file Sunday evening.

## E. If you get stuck on a question
Say: *"Let me think through that."* → reason out loud → if truly unknown: *"I haven't worked with X directly, but based on [related thing I know], I'd approach it by…"* Never freeze, never bluff a fake fact.

---

## F. The AI-tools question (JD-specific — this WILL come up)

The job description explicitly says "leverage AI tools to improve efficiency." They are not asking whether you use AI. They are asking whether you use it like an engineer or like someone who pastes answers from a chatbot.

### Model answer — how to talk about this

> "I treat AI tools the way I treat a senior engineer on the team — it's a thought partner, not an answer machine. On the Nokia 5G remediation pipeline I used Claude to help me think through the semantic matching architecture and to generate boilerplate for the vector DB integration, but the design decisions — what to cache, how to handle circuit breaking, when to fall back to rule-based matching — those came from understanding the failure modes, which no AI can do for you from the outside. On the RF Keyword Generator I also kept a deterministic fallback layer precisely because LLM outputs aren't fully predictable. I've found AI tools save me maybe forty percent of the time I'd otherwise spend on scaffolding and documentation, which I reinvest into the hard parts: data modeling, failure mode analysis, performance profiling. The output of an AI suggestion always goes through my mental model before it goes into production."

### How to frame AI usage as a senior engineering multiplier

- **Multiplier frame:** "AI handles the mechanical work; I focus on the judgment calls." Name specific tasks: boilerplate generation, first-draft API specs, regex prototyping, test scaffold. Never claim AI designed the system.
- **Taste and judgment frame:** Senior engineers are valuable for what they choose NOT to build, for the edge cases they anticipate, for knowing when a simple solution beats a clever one. AI can't do that; you can.
- **Verification frame:** "I read and understand every line before it ships." This matters. If you can't explain a piece of code in the codebase, you don't own it.
- **Concrete outcome frame:** Attach AI use to a real result. "Used AI-assisted code generation to get the Nokia NFTRACE validation pipeline from spec to working prototype in days instead of weeks — the fifty percent reduction in validation time was a real engineering outcome, not a shortcut."

### What NOT to say

- Do NOT say "AI did most of the heavy lifting" — instant credibility loss.
- Do NOT say "I just prompt it and it writes the code" — sounds like you can't code.
- Do NOT claim AI credit for architectural decisions you made.
- Do NOT be defensive or apologetic about using AI — it's a stated job requirement. Own it confidently.
- Do NOT say you use AI for everything — name the things you always do yourself: debugging live issues, data modeling, production incident response, security review.

---

## G. The question behind the question

For 10 common interview questions — what the interviewer is *really* testing.

| Question asked | What they're actually testing |
|---|---|
| **Why FastAPI over Flask or Django?** | Did you choose this deliberately with trade-offs in mind, or did you just use whatever was in the tutorial? They want deliberate engineering judgment. |
| **async def vs def — when do you use each?** | Do you actually understand the event loop and threading model, or do you just put async on everything? Misusing async is a common senior-dev red flag. |
| **Tell me about a time something broke in production.** | Can you stay calm under failure, diagnose systematically, and learn from it — or do you panic and blame? They're hiring for incident maturity, not perfection. |
| **How would you design X from scratch?** | Do you ask clarifying questions before diving in? Senior engineers scope before they build. Jumping straight to implementation signals junior thinking. |
| **How do you handle database migrations on a live system?** | Have you actually shipped to production? Zero-downtime migrations require real operational experience — you can't fake this from documentation. |
| **What's the trade-off between SQL and NoSQL?** | Do you have a nuanced view, or do you think one is always better? Dogmatic answers reveal inexperience with production systems at scale. |
| **How do you scale a service that's getting slow?** | Can you diagnose before you prescribe? The best engineers measure first, then optimize the actual bottleneck — not the imagined one. |
| **Walk me through your code review process.** | Are you a team player? Do you give feedback that makes people better, or do you nitpick style and miss the logic bugs? |
| **How do you handle a disagreement with a teammate on a technical decision?** | Interpersonal maturity. They want someone who can advocate for their position with data while still being able to commit to a team decision. |
| **What's something you built that you're proud of?** | Depth of ownership. They want to see if you can go three levels deep on something — not just describe a project, but explain why you made specific choices and what you'd do differently. |
