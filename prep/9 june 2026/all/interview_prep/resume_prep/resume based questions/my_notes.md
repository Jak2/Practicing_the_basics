# System Design Fundamentals: Core Elements, Features, & Flows

This guide outlines the essential building blocks, design frameworks, and common flows required for modern software architecture. Use this as a reference cheat sheet alongside [1.TECHNICAL_ANSWERS.md](file:///media/asterisk/1722F6694CF9F147/project/interview_prep/interview_pack/1.TECHNICAL_ANSWERS.md#L222-L283) and [8.Birds-Eye View: Everything You Need to Crack This Interview.md](file:///media/asterisk/1722F6694CF9F147/project/interview_prep/interview_pack/8.Birds-Eye%20View:%20Everything%20You%20Need%20to%20Crack%20This%20Interview.md#L80-L94).

---

## 1. The System Design Framework (The Blueprint)

When approaching any system design question or architectural document, follow a structured sequence to ensure you cover both business goals and technical constraints:

```mermaid
graph TD
    A["1. Clarify Requirements (FRs & NFRs)"] --> B["2. Estimations (QPS, DB, Bandwidth)"]
    B --> C["3. API Design (HTTP Contracts)"]
    C --> D["4. Data Model Design (Schema & DB Choice)"]
    D --> E["5. High-Level Design (Core Architecture Diagram)"]
    E --> F["6. Deep Dive & Scaling (Sharding, Caching, CDN)"]
    F --> G["7. Failure Modes & Resiliency (Circuit Breakers, Retries)"]
```

### Step 1: Clarify Requirements
*   **Functional Requirements (FR):** Core features the system must support (e.g., "User can post ads", "User can query real-time analytics"). Limit to the top 2-3 essential features.
*   **Non-Functional Requirements (NFR):** The system's scale and constraints (e.g., "Availability prioritized over consistency (AP)", "P99 read latency < 200ms", "Support 10M Daily Active Users (DAU)").

### Step 2: Back-of-the-Envelope Estimations
*   **QPS (Queries Per Second):** 
    $$\text{Average QPS} = \frac{\text{Daily Active Users} \times \text{Requests Per User}}{\text{86400 seconds}}$$
    $$\text{Peak QPS} = \text{Average QPS} \times 2$$
*   **Storage capacity:** (e.g., $10\text{M writes/day} \times 500\text{ bytes/row} = 5\text{ GB/day} \approx 1.8\text{ TB/year}$). Estimate media/binary assets separately.
*   **Bandwidth:** Ingress and egress rates based on the average payload sizes.

---

## 2. Core Must-Have Building Blocks

Modern distributed systems leverage a standard set of infrastructure layers to achieve horizontal scaling and reliability:

| Component | Primary Purpose | Common Technologies / Implementations |
| :--- | :--- | :--- |
| **DNS / CDN** | Resolves domain names and caches static assets (images, JS/CSS) geographically close to users. | Cloudflare, AWS CloudFront |
| **Load Balancer (LB)** | Distributes incoming network requests across stateless application pools. | NGINX, HAProxy, AWS Application Load Balancer |
| **API Gateway** | Unified entry point handling authentication verification, rate limiting, SSL termination, and routing. | Kong, AWS API Gateway, Custom FastAPI middleware |
| **App Server Layer** | **Stateless** backend instances running the core business logic. | FastAPI, Gunicorn/Uvicorn, Node.js |
| **Cache Layer** | Offloads database query load and serves hot read requests with sub-millisecond latencies. | Redis, Memcached |
| **Primary Database** | **OLTP** (relational/NoSQL) for transactional writes; **OLAP** (columnar) for analytical/reporting workloads. | **OLTP:** PostgreSQL, MySQL, SQLite<br>**OLAP:** Snowflake, BigQuery |
| **Message Queue (MQ)** | Buffers write spikes, decouples backend processes, and manages asynchronous job states. | Celery, RabbitMQ, Kafka, Redis Pub/Sub |
| **Object Storage** | Durable, cost-effective storage for raw assets, images, media, or data backups. | AWS S3, Google Cloud Storage |

---

## 3. The 3 Universal System Flows

### Flow A: The Asynchronous Write Path ("202 Accepted" Pattern)
Use this flow for any task taking longer than ~100-200ms (e.g., generating AI assets, processing media uploads, generating reports). **Never hold an HTTP connection open for slow, CPU-bound computations.**

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Gateway as API Gateway / App
    participant Queue as Message Queue (Redis/RabbitMQ)
    participant Worker as Background Workers (Celery)
    participant DB as DB / S3 Storage

    Client->>Gateway: POST /tasks (payload)
    Gateway->>Gateway: Validate input (e.g. Pydantic)
    Gateway->>Queue: Enqueue task payload + generate job_id
    Gateway-->>Client: Return 202 Accepted + {job_id: "uuid"}
    Note over Client, Gateway: Connection closed. Client is free!
    
    Queue->>Worker: Pull job from queue
    Worker->>Worker: Run heavy computation (e.g. LLM/AI gen)
    Worker->>DB: Save status = COMPLETED & output URLs
    
    loop Polling (or Webhook push)
        Client->>Gateway: GET /tasks/{job_id}
        Gateway->>DB: Check task status
        DB-->>Gateway: Return status & output
        Gateway-->>Client: status: "COMPLETED" (with results)
    end
```

---

### Flow B: The Read-Heavy Cache-Aside Path
Protects the primary relational database from read saturation by checking a distributed cache first.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant API as App Instance
    participant Cache as Redis Cache
    participant DB as SQL DB

    Client->>API: GET /resource/{id}
    API->>Cache: Check key exists (cache-aside)
    
    alt Cache Hit
        Cache-->>API: Return cached JSON payload
        API-->>Client: 200 OK (latency < 10ms)
    else Cache Miss
        Cache-->>API: Key not found (null)
        API->>DB: Query row from table
        DB-->>API: Return record data
        API->>Cache: Populate key in Redis (with TTL)
        API-->>Client: 200 OK (latency ~50-100ms)
    end
```

*   **How it works:**
    1. **Cache Hit (Fast Path):** This happens when someone has requested this data recently. App checks Redis. If found, returns it immediately (latency < 10ms). The SQL database is never touched.
    2. **Cache Miss (Slow Path):** This happens the very first time the resource is requested, or after the cache has expired. If not found in Redis, App queries the SQL database, writes the result to Redis (with a Time-To-Live/TTL) so subsequent requests hit the cache, and returns the result to the client.
*   **Why Cache-Aside? Why is this the Industry Standard? (The Benefits)**
    * *Resiliency (Fail-Open):* If Redis crashes, requests fall back to the SQL database directly. The site slows down but remains up.
    * *Lazy Loading:* You only cache data that users actually request, preserving memory.
*   **Gotchas & Interview Depth Signals:**

    **Gotcha 1: Stale Data (Cache Invalidation)**
    The Problem: What happens if a user updates their ad details (PUT /ads/101)? The SQL database is updated, but Redis still has the old version.
    The Fix: Whenever the application writes or updates the DB, it must actively delete the corresponding key in Redis (DEL ad:101). This forces the next read request to get a Cache Miss, query the fresh DB data, and write it back to the cache.

    **Gotcha 2: Thundering Herd Problem**
    The Problem: If a cache key expires (e.g., a viral tweet with 1 million views), thousands of users request it simultaneously. All hit Redis -> all get Cache Miss -> all hammer the SQL DB at once -> DB crashes.
    The Fix: Implement a distributed lock (e.g., using Redis SETNX or a library like Redisson). Only the first request acquires the lock, queries the DB, and updates the cache. Other requests wait for the lock to be released.


---

### Flow C: Authenticated Gateway & Token Revocation Path
How authorization and security verification propagate cleanly through a distributed system.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Gateway as API Gateway
    participant Cache as Redis Blacklist
    participant Service as Internal Microservice

    Client->>Gateway: Request + Authorization: Bearer JWT
    Gateway->>Gateway: 1. Validate JWT signature locally (Header.Payload.Signature)
    Gateway->>Gateway: 2. Check JWT Expiry (exp claim)
    Gateway->>Cache: 3. Check JTI (Token ID) in Redis Blacklist
    
    alt Token is Blacklisted (e.g. user logged out)
        Cache-->>Gateway: Exists in blacklist
        Gateway-->>Client: 401 Unauthorized
    else Token is Valid
        Cache-->>Gateway: Does not exist
        Gateway->>Service: Forward request with verified user metadata headers
        Service-->>Gateway: Response
        Gateway-->>Client: 200 OK
    end
```

This flow explains how a modern distributed system verifies a user's identity at the edge of the network (**API Gateway**) and handles the tricky problem of **token revocation (logging users out before the token naturally expires)**.

Here is a step-by-step technical breakdown of how it works and why it is designed this way.

---

### The Problem: The "Stateless JWT" Dilemma
JSON Web Tokens (JWTs) are popular because they are **stateless**. The token contains all user details (like `user_id` and `roles`) in the payload, and it is cryptographically signed. 
* To verify it, the server only needs to check the signature using a public or secret key. It **does not need to query a database**.
* **The major flaw:** Because it's stateless, once a JWT is issued, it is valid until its expiration time (`exp` claim). If a user logs out, or their account is compromised, you cannot "delete" a JWT from their browser. They can still access your API until the token expires.

This flow solves that exact problem using a **Redis Blacklist** at the Gateway layer.

---

### Step-by-Step Breakdown of the Flow

#### 1. The Incoming Request
The client sends a request to the API Gateway with the token in the headers:
`Authorization: Bearer eyJhbGciOiJIUzI1NiIsIn...`

#### 2. Stateless Validation (Edge Checks)
The API Gateway receives the request and performs two fast, in-memory checks:
* **Signature Check:** It uses the signing key to ensure the token has not been tampered with.
* **Expiry Check:** It reads the `exp` timestamp in the token payload. If the current time is greater than `exp`, it immediately returns `401 Unauthorized` without doing any network lookups.

#### 3. Stateful Revocation Check (The Redis Blacklist)
To verify if the token was manually revoked (e.g., the user clicked "Log Out"):
* Every JWT is generated with a **`jti`** (a unique JWT ID uuid) claim in its payload.
* When a user logs out, the system takes their token's `jti` and saves it in **Redis** with a key like `blacklist:<jti>`, setting its Time-to-Live (TTL) to match the remaining life of the token.
* The API Gateway checks Redis: `EXISTS blacklist:<jti>`.
  * **If found:** The user logged out early. Return `401 Unauthorized`.
  * **If NOT found:** The token is active. Proceed to the next step.

#### 4. Clean Downstream Propagation (User Context Infiltration)
Now that the Gateway has proven the user is who they say they are, it forwards the request to internal microservices (e.g., Billing, Inventory).
* Instead of forwarding the raw JWT and forcing internal services to decode and verify it again, the API Gateway strips the JWT and injects simple HTTP headers:
  * `X-User-Id: 101`
  * `X-User-Roles: Admin, Editor`
* The internal service can now trust these headers blindly, because they are inside a private network, and all external traffic is forced through the Gateway.

---

### Why is this the Industry Standard? (The Benefits)
1. **Edge Protection:** Expired or forged tokens are rejected immediately at the load balancer/gateway level. They never reach your internal app servers, saving CPU and database resources.
2. **Stateless Scale with Stateful Control:** You don't hit your primary SQL database on every request to see if a session exists. Checking a key in Redis takes <1ms, giving you near-instant revocation at scale.
3. **Decoupled Microservices:** Your backend engineers don't need to write authentication code inside every single service. They just check for the `X-User-Id` header.


---

## 4. Cross-Cutting Non-Functional Requirements & Guardrails

### 1. Resiliency & Reliability
*   **Circuit Breakers:** Prevent cascading failure. If a third-party API or downstream service fails $N$ consecutive times, open the circuit and fail-fast instantly. This prevents incoming requests from stacking up and exhausting resource pools.
*   **Retry + Exponential Backoff + Jitter:** Introduce randomized delay (jitter) when retrying failed network requests to prevent a thundering herd from crashing recovering backend services.
*   **Idempotency Keys:** For any database mutations or payment transactions, require clients to pass a unique idempotency key. Check this key atomically in Redis (`SETNX`) to ensure duplicate or retried requests are ignored.

### 2. Observability & Monitoring
*   **RED Metrics:**
    *   **Rate:** Request count per second.
    *   **Errors:** Rate of HTTP 5xx responses.
    *   **Duration:** Latency tracking (focus on **p95** and **p99** to capture long-tail user pain).
*   **Distributed Tracing:** Inject a unique `trace_id` or `request_id` header at the gateway and propagate it across all queues, databases, and microservices to allow end-to-end trace correlation.
*   **Health Endpoints:** Distinguish between `/health` (liveness checks: "am I alive?") and `/ready` (readiness checks: "am I ready to serve traffic?").

### 3. Data Integrity & CAP Theorem
*   **CAP Theorem:** Choose between Strong Consistency (**CP** — where every read returns the most recent write, at the expense of availability during network partitions) and Eventual Consistency (**AP** — where reads may be stale, but the system is always available).
*   **Outbox Pattern:** Combine database updates and message queue event dispatches into a single database transaction. An outbox poller publishes messages asynchronously to avoid data loss if a message broker crashes mid-transaction.
