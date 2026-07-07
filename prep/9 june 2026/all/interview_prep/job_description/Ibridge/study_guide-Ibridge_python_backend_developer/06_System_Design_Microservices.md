# 06 — System Design, Microservices & Async Architecture

JD: "microservices-based architecture", "asynchronous processing", "contribute to backend architecture and system design", "scalability". Senior signal lives here.

> **Mindset going in:** System design interviews test whether you think like someone who has been paged at 2am — not someone who read a blog post. Every answer needs failure modes, trade-offs stated explicitly, and monitoring. If you don't mention what breaks and how you'd know it broke, you sound junior regardless of what else you say.

---

## 1. Monolith vs Microservices

- **Monolith**: single deployable. Simpler, faster to build, easy transactions/debugging. Scales as one unit; large teams step on each other.
- **Microservices**: small services per business capability, independently deployable/scalable, own their data. Cost: distributed-systems complexity (network, consistency, observability, deployment).
- **Senior answer**: "Start monolith / modular monolith, split into services when team size, scaling needs, or domain boundaries justify it. Don't microservice prematurely."
- Your gRPC (Google Remote Procedure Call — binary, HTTP/2, strongly typed) model gateway with **stateless horizontal scaling** + multi-provider routing = a real microservice story.

### Veteran layer — what nobody says in interviews but every experienced engineer knows

The real cost of microservices nobody talks about in interviews: distributed transactions, cross-service debugging, data consistency, and the operational overhead of running and monitoring N services instead of 1.

I have seen teams go microservices-first and spend 6 months building service mesh infrastructure, distributed tracing, and Kubernetes YAML instead of shipping product features. The services were beautiful. The business was behind.

**My rule:** Start with a well-structured modular monolith — clean module boundaries, clear domain separation, but one deployable artifact. Split into services when you hit a *concrete, measurable* bottleneck:
- Different scaling needs (the AI generation worker needs 10x more compute than the auth service — split it)
- Different deployment cadence (the ML pipeline deploys every hour; the billing service deploys once a month — split them)
- Different team ownership (two separate teams cannot coordinate deploy windows — split it)
- A genuine data isolation requirement (PCI scope, HIPAA boundary)

If none of those are true, the microservice is a future-proofing bet you're paying for today with complexity. The modular monolith can be extracted later — the key is not coupling the modules internally.

**Interviewer is probing:** Can you weigh architectural trade-offs against business context? Can you push back on cargo-cult decisions?

**Senior signal:** You name the *specific* costs, not just "it's complex." Distributed transactions, eventual consistency, observability overhead, on-call blast radius when a shared dependency fails.

**Common weak answer:** "Microservices are better because they scale independently." That's not wrong — it's incomplete. What does independently scaling cost you?

**Follow-up questions to expect:**
- "When would you extract a service from an existing monolith?"
- "How would you decompose the Adwork platform into services?"
- "What's the first service you'd split out and why?"

---

## 2. Communication styles

- **Synchronous**: REST/HTTP, **gRPC** (you've used — binary, HTTP/2, fast, strongly-typed via protobuf, great service-to-service).
- **Asynchronous / messaging**: queues (RabbitMQ, Redis, Kafka, SQS) — decouple producer/consumer, absorb spikes, retry, durability.
- REST vs gRPC: REST = human-friendly/ubiquitous/browser; gRPC = perf, streaming, internal service mesh.
- **API Gateway**: single entry — auth, rate limit, routing, aggregation.

**Veteran layer:** Synchronous calls between internal services create coupling and cascade failures. If Service A calls Service B synchronously and B slows down, A slows down. If B times out, A needs a fallback or it fails too. Every sync hop is a failure blast radius. The circuit breaker pattern (Hystrix-style or manually implemented) exists specifically to prevent one slow downstream from taking out your entire call chain. In high-throughput internal paths, gRPC with connection pooling and deadline propagation is far superior to REST — but it requires shared protobuf schemas, which is its own operational cost.

---

## 3. Asynchronous processing patterns (JD calls this out)

- **Task queue (Celery + Redis/RabbitMQ)**: offload slow work (report generation, AI calls, emails) → API responds fast.
- **Event-driven / pub-sub**: services react to events; loose coupling.
- **Producer–consumer / worker pool**: scale workers independently.
- **Idempotent consumers + retries + dead-letter queue (DLQ — a queue for messages that failed processing)** for failed messages.
- When to go async: long-running, spiky, can tolerate eventual completion, or fan-out to many.

**Veteran layer — what actually breaks:**
- Workers die mid-job. Your job state must be persistent before you ACK the message, not after.
- Message visibility timeout: if your job takes 5 minutes and your queue visibility timeout is 30 seconds, the message will be redelivered to another worker while the first is still running. Always set visibility timeout to max expected job duration + buffer.
- DLQ is not optional. Without it, a poison-pill message will retry forever and block the queue. DLQ + alerting on DLQ depth is table stakes.
- Idempotency: if a worker crashes after completing work but before ACKing the message, the job reruns. Your handler must be safe to call twice with the same input.

---

## 4. Scalability building blocks

- **Horizontal scaling** (more stateless instances) behind a **load balancer** > vertical (bigger box). Statelessness (JWT — JSON Web Token, no local session) enables this.
- **Caching** (Redis): cache-aside pattern, TTLs, cache invalidation. You did this (5G pipeline, NFTRACE sessions).
- **Database scaling**: read replicas, connection pooling, partitioning/sharding, indexing.
- **CDN** for static; **message queues** to smooth load; **rate limiting** to protect.
- **CAP theorem**: in a partition, choose Consistency or Availability. Most web systems = AP with eventual consistency.

### Caching veteran layer — cache invalidation is the hard part

"There are only two hard things in Computer Science: cache invalidation and naming things." — This is a joke but it isn't.

Everyone knows to add a cache. The interview question is whether you know *how to keep it correct.*

**Three strategies, each with trade-offs:**

**1. TTL-only (Time-To-Live):**
- Set a TTL, let cache expire naturally. Simple. No invalidation logic.
- Trade-off: data is eventually consistent. Between write and TTL expiry, reads get stale data. Acceptable for: analytics dashboards, public content, product catalogs where seconds of staleness are fine.
- Use when: simplicity is more valuable than freshness, or the cost of stale data is low.

**2. Write-through invalidation:**
- On every write to the database, immediately delete or update the cache entry.
- Trade-off: writes are slower (two writes: DB + cache). Race condition risk if two writers invalidate and repopulate simultaneously. Cache stampede on a popular key if many readers hit the DB at once after invalidation.
- Use when: reads are much more frequent than writes, and you need near-real-time consistency. Mitigate stampede with probabilistic early expiration or a mutex lock on repopulation.

**3. Event-driven invalidation:**
- Services publish events (e.g., "ad_updated"). Cache listener consumes and invalidates.
- Trade-off: most complex. Requires reliable event delivery. If the event is lost, the cache is stale indefinitely. Need idempotent consumers and a fallback TTL as a safety net.
- Use when: data is owned by one service but read by many, and you need immediate consistency without coupling write paths.

**Interviewer is probing:** Do you know caching beyond "add Redis"? Can you reason about consistency?

**Senior signal:** You name which strategy fits which access pattern. You mention cache stampede prevention (mutex, probabilistic TTL). You have a fallback TTL even on event-driven invalidation because events can be lost.

---

## 5. Reliability & resilience

- **Timeouts, retries (with backoff+jitter), circuit breakers, bulkheads.**
- **Graceful degradation / fallbacks** (your regex fallback for LLM failure = perfect example of resilience thinking).
- **Health checks** (`/health`, readiness vs liveness), **idempotency**, **graceful shutdown** (drain in-flight requests).
- **Observability**: structured logging + correlation/request IDs, metrics (RED: Rate, Errors, Duration), tracing, alerting.

**Veteran layer — jitter is not optional on retries:**
Exponential backoff without jitter creates thundering herds. If 100 workers all fail at the same time and all retry at T+2, T+4, T+8 — they all hit the recovering service simultaneously and take it down again. Add random jitter to the backoff interval. This is the difference between "read it in a blog post" and "debugged it at 3am."

---

## 6. Data consistency across services

Each service owns its data (no shared DB). Cross-service consistency via:
- **Saga pattern** (sequence of local txns + compensating actions).
- **Outbox pattern** (write event + data in one txn, publish reliably).
- **Eventual consistency** is the norm in distributed systems.

### Saga pattern deep dive

A saga is how you handle a business workflow that spans multiple services when you cannot use a distributed transaction (which you shouldn't — they're slow, lock-heavy, and a distributed systems anti-pattern).

**Core idea:** Break the workflow into a sequence of local transactions. Each step publishes an event or sends a command to the next step. If a step fails, execute *compensating transactions* in reverse order to undo the work already done.

**Two implementation styles:**

**Choreography (event-driven):**
- Each service emits events and other services react.
- No central coordinator.
- Pro: loose coupling, services don't know about each other.
- Con: hard to trace the full workflow flow. Hard to answer "what is the state of saga X right now?"

**Orchestration (central coordinator):**
- A saga orchestrator sends commands to services and waits for replies.
- Pro: the full workflow is visible in one place. Easier to debug.
- Con: the orchestrator becomes a coupling point.

**Concrete example: Ad creation workflow across services**

```
Services involved: API, Payment Service, Content Generation Service, Storage Service

Steps:
1. API creates an ad record (status=PENDING) — local transaction, done
2. API sends command: "charge_user" to Payment Service
3. Payment Service charges the card — local transaction
4. If charge succeeds: Payment Service emits "payment_succeeded"
5. Content Generation Service receives event: generate creative assets
6. Generation Service emits "assets_generated" with asset URLs
7. Storage Service stores assets, emits "assets_stored"
8. API receives "assets_stored": updates ad record (status=ACTIVE)

Compensating transactions (if step 5 fails — generation fails):
- Emit "generation_failed"
- Payment Service compensating transaction: issue refund
- API compensating transaction: update ad (status=FAILED), notify user
```

**What makes this a senior answer:**
- You name that compensating transactions are not always reversible. A sent email cannot be unsent. A charge that partially executed needs idempotency keys to safely retry or undo. Design for this upfront.
- You mention idempotency at every step — each service must handle duplicate events gracefully.
- You mention the saga log — a persistent record of what step the saga is on, so you can resume or compensate after a crash.

**Outbox pattern (why it matters):**
The naive implementation: write to DB, then publish event. Problem: if the service crashes between the write and the publish, the event is lost and the saga stalls silently.

The outbox pattern: write both the domain object AND the event to the same DB transaction in an `outbox` table. A separate relay process reads the outbox and publishes events. Now the write and the event are atomically consistent. The relay can retry until the event is delivered.

---

## 7. System Design Interview Failure Modes

These are the patterns that get candidates rejected in senior system design rounds. Read these and consciously avoid them.

**1. Jumping to tech stack before clarifying requirements**
You hear "design an ad generation API" and immediately say "I'd use FastAPI + Celery + Redis + PostgreSQL + S3." Wrong. You don't know the scale, the latency requirements, the team size, the existing infrastructure. Requirements first. Tech stack follows. Interviewers specifically watch for this.

**2. Designing for billions of users when the question didn't ask for it**
Over-engineering is a real failure mode. If the interviewer says "a startup with 10,000 daily users," designing a globally sharded Cassandra cluster with multi-region active-active replication signals that you can't calibrate solution to problem. Match your design to the stated constraints.

**3. No mention of failure handling**
A design with no failure scenarios described is a junior design. What happens when the AI service is down? What happens when the queue is full? What happens when the DB write succeeds but the cache invalidation fails? Senior engineers think in failure paths as naturally as happy paths.

**4. No monitoring or observability**
If you design a system and never mention how you'd know it's broken, the interviewer concludes you've never operated a system. At minimum: structured logging with request IDs, metric dashboards (latency p50/p99, error rate, queue depth), and at least one specific alert (e.g., "alert if job queue depth > 1000 for 5 minutes").

**5. Saying "use Redis" without explaining what for and the trade-offs**
"I'd add Redis for caching" tells the interviewer nothing. *What* are you caching? *What's the TTL and why?* *What's the invalidation strategy?* *What happens to in-flight reads when you flush the cache?* State the problem you're solving with each technology choice, not just the technology.

**6. Missing the non-functional requirements discussion**
Latency (p99 target?), throughput (RPS?), availability (99.9%? 99.99%?), consistency (eventual or strong?), data retention. These shape every architectural decision. Not asking these questions signals you design in a vacuum. Always spend 3-5 minutes clarifying NFRs (Non-Functional Requirements) before drawing a single box.

**7. Never stating trade-offs**
Every design choice has a cost. Async queue: more responsive API, but eventual completion — user can't get the result immediately. Read replicas: lower read latency, but replication lag means slightly stale reads. State these explicitly. The interviewer already knows the trade-offs. They want to know *you* know them.

---

## 8. A reusable design-question framework (use for ANY "design X" prompt)

1. **Clarify requirements** (functional + non-functional: scale, latency, read/write ratio, consistency).
2. **Estimate** rough load (RPS, data size).
3. **API design** (endpoints, contracts).
4. **Data model** (tables/entities, indexes).
5. **High-level architecture** (client → gateway/LB → services → DB/cache/queue).
6. **Scale & bottlenecks** (cache, replicas, queue, sharding).
7. **Reliability** (failure modes, retries, monitoring).
8. **Trade-offs** — state them explicitly (this is what makes you sound senior).

---

## 9. Complete worked design: "Design the backend for an ad-creative generation API"

> This is the single most likely system design question you will get, given the JD maps directly to Adwork. Practice this out loud until you can walk through it in 35-40 minutes without notes.

---

### Step 1: Requirements clarification (speak this part out loud)

"Before I design anything, I want to make sure I understand the requirements. Can I ask a few questions?

- **Functional:** Users can submit an ad-creative generation request. They get back a status. When complete, they can retrieve the generated creative assets (copy, image URLs). Is that the core flow?
- **Scale:** How many generation requests per day? Let's say 50,000/day to start — that's roughly 35 RPS average, maybe 150 RPS at peak. Is that in the right ballpark?
- **Latency:** What's the acceptable wait time for generation? AI image generation can take 10-60 seconds. Is that acceptable, or do we need streaming/webhook?
- **Availability:** What SLA (Service Level Agreement — the uptime commitment) are we targeting? 99.9% means ~8 hours downtime/year. For a paid SaaS (Software as a Service) product, I'd target 99.9%.
- **Consistency:** If two requests come in simultaneously for the same brand, does it matter if they see each other's results instantly? I'll assume eventual consistency is fine.
- **Auth:** JWT + per-user rate limits?
- **Asset storage:** Where do generated images live? I'll assume object storage (S3-compatible).

OK — with those answers, let me design the system."

---

### Step 2: Scale estimates

```
Requests/day:        50,000
Peak RPS:            ~150 (assuming 10x average)
Avg generation time: 20 seconds (AI call)
Concurrent jobs:     150 RPS * 20s = ~3,000 concurrent in-flight jobs at peak
DB writes/day:       50,000 job records + metadata
Asset storage:       50,000 * ~2MB avg = ~100GB/day, so object storage, not the DB
Read RPS:            ~5x writes for status polling = ~750 RPS reads at peak
```

This tells me: I need a job queue to absorb spikes, a worker pool scaled to handle concurrency, and caching on the read path.

---

### Step 3: API design

```
POST   /v1/generations
  Body: { brand_id, brief, format, target_audience }
  Auth: Bearer JWT
  Rate limit: 100 req/min per user
  Response: 202 Accepted
  { job_id: "gen_abc123", status: "queued", poll_url: "/v1/generations/gen_abc123" }

GET    /v1/generations/{job_id}
  Auth: Bearer JWT
  Response: {
    job_id, status: "queued|processing|complete|failed",
    created_at, updated_at,
    result: {              # present only when status=complete
      copy: "...",
      image_url: "https://cdn.example.com/...",
      variants: [...]
    },
    error: "..."           # present only when status=failed
  }

GET    /v1/generations?brand_id=X&status=complete&page=1&limit=20
  Response: paginated list

DELETE /v1/generations/{job_id}   # cancel a queued job
```

**Why 202 Accepted and not 200?** Generation takes 10-60 seconds. Holding an HTTP connection open for 60 seconds is wasteful — it ties up a thread, hits proxy timeouts, and doesn't scale. The client polls or we push a webhook.

---

### Step 4: Data model

```sql
-- Core job table
CREATE TABLE generation_jobs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL,
    brand_id      UUID NOT NULL,
    status        VARCHAR(20) NOT NULL DEFAULT 'queued',
                  -- CHECK (status IN ('queued','processing','complete','failed','cancelled'))
    brief         JSONB NOT NULL,
    result        JSONB,          -- populated on completion
    error_message TEXT,
    attempts      INT NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at  TIMESTAMPTZ
);

CREATE INDEX idx_jobs_user_status    ON generation_jobs(user_id, status);
CREATE INDEX idx_jobs_brand_status   ON generation_jobs(brand_id, status);
CREATE INDEX idx_jobs_created_at     ON generation_jobs(created_at DESC);

-- Brands table (referenced)
CREATE TABLE brands (
    id          UUID PRIMARY KEY,
    user_id     UUID NOT NULL,
    name        TEXT NOT NULL,
    config      JSONB           -- tone, colors, fonts
);
```

**Why JSONB for brief and result?** The input schema varies by format type and will evolve. JSONB lets us query into it (e.g., `WHERE brief->>'format' = 'banner'`) without a schema migration every time we add a field.

**Why UUID (Universally Unique Identifier) not serial int?** UUIDs are safe to expose in URLs (no enumeration attack), and safe to generate client-side for idempotency.

---

### Step 5: Architecture

```
                        ┌─────────────────────────────────────┐
                        │           External Clients           │
                        │     (Web App / Mobile / API users)   │
                        └──────────────┬──────────────────────┘
                                       │ HTTPS
                        ┌──────────────▼──────────────────────┐
                        │           API Gateway                │
                        │   (Auth, Rate Limiting, Routing)     │
                        └──────────────┬──────────────────────┘
                                       │
                        ┌──────────────▼──────────────────────┐
                        │         FastAPI Application          │
                        │   (Stateless, horizontally scaled)   │
                        │   POST /generations → enqueue        │
                        │   GET  /generations/{id} → cache/DB  │
                        └───┬──────────────┬───────────────────┘
                            │              │
               ┌────────────▼───┐   ┌──────▼──────────────┐
               │   PostgreSQL   │   │    Redis             │
               │  (job records, │   │  (job queue via      │
               │   brand data)  │   │   Celery broker,     │
               │                │   │   read cache,        │
               │  Read replica  │   │   rate limit state)  │
               │  for GET reads │   └──────────────────────┘
               └────────────────┘
                                       │ Queue
                        ┌──────────────▼──────────────────────┐
                        │         Celery Worker Pool           │
                        │   (N workers, auto-scaled by queue   │
                        │    depth via KEDA or manual)         │
                        │                                      │
                        │  Worker flow:                        │
                        │  1. Dequeue job                      │
                        │  2. Update status → processing       │
                        │  3. Call AI Model Service            │
                        │  4. Upload assets to S3              │
                        │  5. Update job → complete + result   │
                        │  6. Invalidate cache for job_id      │
                        │  7. ACK message                      │
                        └───────────────┬─────────────────────┘
                                        │
              ┌─────────────────────────┼────────────────────┐
              │                         │                    │
 ┌────────────▼────────┐   ┌────────────▼──────┐  ┌─────────▼──────┐
 │  AI Model Service   │   │   S3 / Object     │  │  Dead Letter   │
 │  (OpenAI / internal │   │   Storage         │  │  Queue         │
 │   inference server) │   │   (asset storage) │  │  (failed jobs) │
 └─────────────────────┘   └───────────────────┘  └────────────────┘
```

---

### Step 6: Async job queue design

**Why Celery + Redis here and not Kafka?**
Kafka is better for high-throughput event streaming (millions/sec, fan-out to many consumers, replay). For a job queue where we need task routing, retries, result storage, and DLQ — Celery + Redis is operationally simpler and fits the scale (150 RPS peak). If we're at 50,000 RPS, we revisit.

**Worker configuration:**
```python
# celery_app.py
app = Celery('adwork', broker='redis://redis:6379/0')

app.conf.update(
    task_acks_late=True,           # ACK only after task completes
    task_reject_on_worker_lost=True,  # requeue if worker dies mid-task
    task_serializer='json',
    result_backend='redis://redis:6379/1',
    task_soft_time_limit=90,       # raise SoftTimeLimitExceeded at 90s
    task_time_limit=120,           # hard kill at 120s
)

@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,        # 30s between retries
    queue='generation',
)
def generate_ad_creative(self, job_id: str):
    try:
        job = db.get(job_id)
        db.update(job_id, status='processing', attempts=job.attempts + 1)
        
        result = ai_service.generate(job.brief)          # may raise
        asset_url = s3.upload(result.assets)             # may raise
        
        db.update(job_id, status='complete', result={
            'copy': result.copy,
            'image_url': asset_url,
        })
        cache.delete(f'job:{job_id}')                    # invalidate cache
        
    except AIServiceUnavailable as exc:
        # Retry with exponential backoff + jitter
        delay = 30 * (2 ** self.request.retries) + random.uniform(0, 10)
        raise self.retry(exc=exc, countdown=delay)
    except Exception as exc:
        db.update(job_id, status='failed', error_message=str(exc))
        raise  # goes to DLQ after max_retries
```

**Key decisions:**
- `task_acks_late=True`: message is NOT removed from queue until the task finishes. If the worker dies, the message is redelivered. Without this, a mid-task worker crash silently drops the job.
- Retry with jitter: prevents thundering herd on a recovering AI service.
- Soft time limit: gives the task 90s to clean up (mark job failed) before hard kill at 120s.

---

### Step 7: Cache strategy

```python
# GET /v1/generations/{job_id}
async def get_generation(job_id: str, user_id: str):
    cache_key = f'job:{job_id}'
    
    # Cache-aside: check cache first
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Cache miss: read from DB (read replica for GET)
    job = await db.get_job(job_id, user_id)  # includes ownership check
    if not job:
        raise HTTPException(404)
    
    # Cache strategy varies by status:
    # - complete/failed: cache long (24h), data won't change
    # - queued/processing: cache short (2s), state changes frequently
    ttl = 86400 if job.status in ('complete', 'failed') else 2
    await redis.setex(cache_key, ttl, json.dumps(job.dict()))
    
    return job
```

**Why TTL-only for terminal states?** Once a job is complete or failed, the data is immutable. A 24h TTL means 99% of reads for completed jobs never hit the DB. Write-through invalidation by the worker on completion handles the transition.

**Cache stampede protection for hot jobs:** If 1,000 clients poll the same job simultaneously when its TTL expires, 1,000 DB reads happen in parallel. Mitigation: use a Redis lock (SETNX) to allow only one reader to repopulate; others wait briefly and re-read the cache.

---

### Step 8: Auth and rate limiting

```python
# JWT middleware — every request
# Checks: valid signature, not expired, user exists
# Attaches: user_id, user_tier to request state

# Rate limiting (per user, using Redis sliding window)
RATE_LIMITS = {
    'free': {'generations': 10, 'window': 3600},    # 10/hour
    'pro':  {'generations': 100, 'window': 3600},   # 100/hour
}

# POST /generations also rate-limits at API Gateway level:
# - 100 req/min per IP (DDoS protection)
# - Per-user tier limits in application layer
```

**Why two layers of rate limiting?** IP-level at the gateway protects against unauthenticated DDoS. Per-user tier limits enforce business quotas. These solve different problems.

---

### Step 9: Failure handling

**"What if the AI service is down?"**

This is the most important question in this system. The AI service is a third-party dependency (OpenAI, or internal inference). It *will* be slow. It *will* be rate-limited. It *will* go down.

**Design decisions:**
1. **Circuit breaker on the AI client:** After N consecutive failures (e.g., 5), open the circuit. Workers immediately fail new jobs without waiting for timeouts. Circuit tries again after a cooldown period.
2. **Job stays queued, not failed, during AI outage:** If the circuit is open, the worker re-queues the job with a delay instead of marking it failed. Users see "queued" not "failed" — which is the correct status.
3. **Timeout on every AI call:** Never call an external service without a deadline. `httpx.AsyncClient(timeout=60.0)`. A hung AI request without a timeout holds the worker thread forever.
4. **Multi-provider fallback:** If OpenAI fails, route to Anthropic or an internal model. This was real in your gRPC model gateway — use that story.
5. **User notification on extended delay:** If a job is queued for >5 minutes, trigger a notification ("Your ad is taking longer than usual — we'll email you when it's ready."). This is a product design choice that prevents support tickets.
6. **Webhook / email on completion:** Instead of polling, let users register a webhook URL. Worker calls webhook on complete/failed. Reduces polling load and gives better UX.

```python
# Simplified circuit breaker
class AIServiceClient:
    def __init__(self):
        self.failures = 0
        self.last_failure = None
        self.circuit_open = False
        self.cooldown = 60  # seconds

    async def generate(self, brief):
        if self.circuit_open:
            if time.time() - self.last_failure > self.cooldown:
                self.circuit_open = False  # half-open: try again
            else:
                raise AIServiceUnavailable("Circuit open")

        try:
            result = await self._call_ai(brief)
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= 5:
                self.circuit_open = True
            raise
```

---

### Step 10: Monitoring and alerting

**Metrics to instrument (RED method):**
- **Rate:** requests/sec by endpoint, jobs enqueued/sec, jobs completed/sec
- **Errors:** HTTP 5xx rate, job failure rate, AI service error rate, DLQ depth
- **Duration:** API response latency (p50, p95, p99), job completion time (p50, p95, p99), AI service call duration

**Specific alerts (these are the ones that wake you up at 2am):**
```
ALERT: DLQ depth > 50 — jobs are failing, investigate
ALERT: Job queue depth > 2000 for 5min — workers not keeping up, scale out
ALERT: Job completion p95 > 120s — AI service degraded
ALERT: API 5xx rate > 1% — application error
ALERT: Worker count < 3 — workers crashing
ALERT: Redis memory > 80% — cache eviction risk
ALERT: DB connection pool utilization > 80% — connection exhaustion risk
```

**Structured logging:**
```python
logger.info("job_complete", extra={
    "job_id": job_id,
    "user_id": user_id,
    "duration_ms": elapsed,
    "ai_provider": "openai",
    "attempt": attempt_number,
    "trace_id": trace_id,       # propagated from incoming request
})
```

Every log line has a `trace_id` that flows from the original HTTP request through the queue message into the worker. Without this, debugging a failed job means correlating logs by job_id and timestamp — painful.

---

### Step 11: Trade-offs — state these explicitly

| Decision | Trade-off | Why this choice |
|---|---|---|
| Async job queue | User can't get result immediately (polling/webhook required) | Generation takes 10-60s; holding HTTP open wastes threads and hits timeouts |
| Redis queue (Celery) vs Kafka | Less durable, less replay, but simpler to operate | At 50K jobs/day, Kafka is over-engineered; revisit at 10M/day |
| PostgreSQL for job records | Not the fastest write path, but ACID guarantees | Job status must be consistent; an eventually-consistent store risks showing wrong status |
| Cache TTL=2s for in-progress jobs | Possible 2s stale reads during polling | Prevents DB hammering from polling clients; acceptable for UX |
| 3 retries with 30s backoff | Job may fail for up to ~3 minutes before giving up | Balances retry value against user wait time; tune based on AI service reliability |
| Single region initially | No geo-redundancy | Cost vs risk trade-off for MVP; add read replica in second region in v2 |

---

### Step 12: What I'd add in v2

1. **Webhooks:** POST to user-registered URL on job completion. Eliminates polling.
2. **Streaming status via SSE:** `GET /generations/{id}/stream` pushes status events. Better UX than polling.
3. **Worker autoscaling:** KEDA (Kubernetes Event-Driven Autoscaling) scales worker pods based on Redis queue depth. At low load: 2 workers. At peak: 50.
4. **Multi-region:** Read replicas in a second region, CDN for asset delivery, potentially active-active for the API layer.
5. **Job priority queue:** Pro-tier users get a high-priority queue; free-tier users join a lower-priority queue. Workers drain high-priority first.
6. **Result caching by brief hash:** If two users submit identical briefs, serve cached result. Hash the brief contents, check cache before calling AI. Major cost saver.
7. **Audit log:** Every status transition stored immutably for billing, debugging, and compliance.

---

## 10. Your own project as a system design example: 5G Pipeline

Use this when the interviewer asks "tell me about a system you designed."

**The system:** A 5G network data processing pipeline that ingests high-throughput telemetry data, processes it through a worker pool, and caches results for downstream consumers.

**Frame it as a design problem:**

"The challenge was ingesting bursty telemetry data from 5G network elements — the data rate could spike 10x during network events. We needed to process this without dropping data and without over-provisioning compute for average load.

The design I applied:

1. **Async queue as the shock absorber.** Producers write telemetry events into a queue. The queue absorbs spikes. Workers process at a steady rate. This decouples ingestion throughput from processing throughput — a classic producer-consumer separation.

2. **Worker pool with configurable concurrency.** Workers ran as async coroutines (asyncio), not threads, because the bottleneck was I/O (network calls, DB writes) not CPU. This let us run dozens of concurrent workers on a single machine.

3. **Caching for repeated lookups.** Network topology data (which cell is connected to which) was read thousands of times per second but changed rarely. Cache it in Redis with a TTL matching the config update frequency — dramatically reduced DB load.

4. **Fallback path for processing failures.** If the primary processing logic raised an exception (e.g., malformed data), we had a fallback parser that extracted the fields we could get and flagged the record for review, rather than dropping it. Dropping telemetry data silently was not acceptable — we'd lose visibility into network state.

5. **Monitoring:** Queue depth as the primary health signal. If the queue depth grew, workers weren't keeping up — either a processing bug or a traffic spike. Alert on queue depth > threshold triggered scale-out.

Trade-off I'd own: we used polling for queue reads initially, which added latency. We later switched to long-polling with a 1s timeout, which cut median processing latency by 400ms with no additional infrastructure cost.

This is the same pattern I'd use for any async processing system — the specific tech changes, but the queue-worker-cache-fallback structure is portable."

---

## 11. Likely interview questions

1. Monolith vs microservices — when each?
2. How do services communicate? REST vs gRPC vs messaging?
3. How do you handle long-running tasks in an API? (queue/Celery)
4. How do you scale a backend service? (§4)
5. How do you make a system resilient to a failing dependency? (§5, §9)
6. Design a [URL shortener / rate limiter / ad API / notification system]. (use §8)
7. How do you keep data consistent across microservices? (saga/outbox/eventual)
8. What's CAP theorem?
9. How do you do caching — invalidation strategy? (§4 veteran layer)
10. Stateless vs stateful services — why does it matter for scaling?
11. Walk me through a system you designed. (use §10 — your 5G pipeline)
12. What's the Saga pattern? (§6 deep dive)
13. How would you handle an AI service going down in production? (§9)
14. How do you know your system is healthy? (§10 monitoring)
