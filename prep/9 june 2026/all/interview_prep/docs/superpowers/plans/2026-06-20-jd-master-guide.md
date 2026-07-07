# JD Master Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Build `interview_pack/7.JD_MASTER_GUIDE.md` — a single document organized 1:1 against the IBridge JD, where every JD requirement gets a depth answer the candidate can deliver as someone who's done the work for years. Pulls the best of existing material for the strong areas; contains genuinely NEW depth for the two weak areas (React/Next.js frontend consumption, microservices inter-service concerns).

**Architecture:** Mirror the JD's exact section structure so the candidate can verify coverage line-by-line. Each JD bullet → a block with: the requirement (quoted), "What they're really checking," the proof answer (spoken, project-anchored, deep), and the likely probing follow-up + how to handle it. Self-contained answers (study from this one file), with pointers to deeper study_guide files. The two gap sections are authored IN this plan (below) so the agent reproduces them faithfully rather than inventing.

**Tech Stack:** Markdown prose. No code execution.

## Global Constraints

- **Metrics — use these exact values, never inflate:** NFTRACE −50% pipeline validation time; 5G pipeline 70% auto-resolution, −55% MTTR; code reviews +25%; mentored 3 engineers to senior (Nokia), 19 interns (Lakshya); zero missed deliveries.
- **Project anchors (real — never invent others):** Nokia NFTRACE (FastAPI lifecycle endpoints, Redis `session:{uuid}` isolation, SQLite, XML-RPC SDK); Nokia 5G failure pipeline (Pyshark → LangChain RetrievalQA → Chroma → LLM → Redis cache); Nokia RF Keyword Generator (Streamlit+FastAPI, LLM + template + regex 3-layer fallback, 100% uptime); Brane (PostgreSQL attribute-RBAC schema, multi-agent junction/execution tables, gRPC model gateway, parser hardening); Abjayon (AWS AppSync/AppFlow, IAM roles, GraphQL/REST); Lakshya Space (Python firmware, mentored 19 interns).
- **Honesty rule:** Where real experience is thin (React dev, large-scale microservices, Snowflake), give the honest bridging frame — never fake project experience. Depth of *understanding* is allowed and expected; faking *having built it* is forbidden.
- **Tone:** Spoken English, said aloud in ~60-90s, but precise. Senior = names failure modes and trade-offs, not just definitions.
- **Markers:** `⚠️` weak-answer trap, `→ Follow-up:` likely probe, `💀` danger zone (honesty required).
- **Interview is Monday 2026-06-22.** Study-ready immediately.
- **Do not duplicate** the full content of existing files — pull the sharpest 3-5 points per requirement and point to the deeper file. The two GAP sections are the exception: write them in full.

---

### Task 1: File header + how-to-use

**Files:**
- Create: `interview_pack/7.JD_MASTER_GUIDE.md`

- [ ] **Write header**

```markdown
# 7. JD MASTER GUIDE — Every Requirement, Proven

> This file is organized **exactly like the IBridge job description.** Every requirement they wrote down has a block here: what they're really checking, your depth answer, and the follow-up they'll probe with. If you can deliver every block in this file, you have covered the entire JD.

## How this file relates to the others
- **EXPERIENCE_PROOF.md** = "prove you've built it" (38 experience Q&As).
- **TECHNICAL_ANSWERS.md** = "what is X" (knowledge reference).
- **THIS file** = "does my experience satisfy each JD line?" — the verification layer that maps your proof onto their checklist. Study this last, the day before — it's the integration pass that makes you walk in knowing nothing on their list is unanswered.

## How to use it
1. Read the JD requirement. Cover the answer.
2. Say your answer out loud. Then check against the block.
3. Rehearse the `→ Follow-up:` — that's where the real interview goes.

## The one frame that wins this interview
"I'm a backend Python engineer — FastAPI, async, SQL — who designs APIs as products the frontend consumes, and who integrates AI as a backend service. That is exactly this role." Backend-first, every time.
```

---

### Task 2: JD Section "Backend Development"

**JD lines to cover (quote each):**
1. "Design, build, and maintain scalable RESTful backend APIs using FastAPI and Python."
2. "Implement microservices-based architecture and asynchronous processing where needed."
3. "Ensure high performance, reliability, maintainability and security of backend systems."
4. "Contribute to backend architecture and system design / Collaborate on application architecture."

- [ ] **Write block 1.1 — Scalable REST APIs in FastAPI.** Pull from EXPERIENCE_PROOF Q1.1/Q1.3 + TECHNICAL Q1/Q8/Q9. Key points: NFTRACE lifecycle endpoints + router-per-domain + Depends composition; stateless + Redis external state = horizontal scale; Gunicorn+Uvicorn workers (2×cores+1); pagination, connection pooling. What they check: can you build for scale, not just CRUD. `→ Follow-up:` "How many workers and why?" → 2×CPU+1, then measure I/O vs CPU bound. Point to study_guide/01_FastAPI.md.

- [ ] **Write block 1.2 — Microservices + async.** SHORT pointer here that says "full depth in the two deep-dive sections at the end of this file (Microservices Deep Dive) and in EXPERIENCE_PROOF Section 2 (async)." Give the headline: gRPC model gateway = real microservice (stateless, own scaling profile, provider routing); 5G pipeline = real async system (queue + worker + cache + backpressure). What they check: have you actually run distributed/async, or just read about it. Keep this block to the 90-second spoken version; defer mechanics to the deep dive.

- [ ] **Write block 1.3 — Performance, reliability, maintainability, security (the four pillars).** This is a synthesis block — one paragraph each:
  - *Performance:* Redis cache on 5G pipeline (normalized error-signature key), N+1 fix in NFTRACE (51→1 query), async for I/O. 
  - *Reliability:* 3-layer fallback (RF Generator, 100% uptime), circuit breaker, timeouts+retry+jitter.
  - *Maintainability:* router-per-domain structure, separate input/domain Pydantic models, decoupled test scenarios from validation (the −50% win), type hints + Pydantic as living contract.
  - *Security:* BOLA fix (UUID + ownership check), JWT signed-not-encrypted discipline, parameterized queries, secrets in env. 
  Note: maintainability is the pillar candidates forget — lead with it to stand out. Point to study_guide files per pillar.

- [ ] **Write block 1.4 — Contribute to architecture / system design.** Pull from EXPERIENCE_PROOF Q5.1 (centralized-vs-distributed LLM decision) + study_guide/06 §8 framework. Key points: the design framework (clarify NFRs → estimate → API → data → architecture → scale → failure → trade-offs); the centralization trade-off you actually made. What they check: do you think in trade-offs and failure modes. `→ Follow-up:` the ad-creative design question lives in study_guide/06 §9 — point there and summarize the 202-Accepted+queue+worker+cache+fallback skeleton in 5 lines.

---

### Task 3: JD Section "API Development & Integration (FastAPI Focus)"

**JD lines:**
1. "Integrate backend services with: Frontend applications and Third-party services."
2. "Handle: Authentication (JWT/OAuth), Error handling and validation, API performance and scalability."

- [ ] **Write block 2.1 — Third-party integration.** Pull from study_guide/03 §3 (4-layer playbook) + EXPERIENCE_PROOF Q6.x. Key points: timeout → retry w/ exponential backoff + jitter (name `tenacity`) → circuit breaker → degraded fallback; why jitter (thundering herd); the RF Generator regex fallback (real, 100% uptime); Redis cache to cut dependency. Webhook hardening 4 rules (signature, 202-fast, async, idempotency). What they check: have you made an unreliable dependency reliable. Point to study_guide/03 §3-4.

- [ ] **Write block 2.2 — Authentication (JWT/OAuth).** Pull from study_guide/03 §6-7 + EXPERIENCE_PROOF Q3.x. Key points: JWT signed≠encrypted (the PII-in-token near-miss); OAuth2 auth-code flow 5 steps + what breaks at each + PKCE; JTI Redis blacklist for revocation; HS256 vs RS256 (RS256 for multi-service — public-key verify); bcrypt/argon2. What they check: production scars, not doc knowledge. `→ Follow-up:` "logout with JWT?" → blacklist + jti, NOT "delete on client." Point to study_guide/03 §6-7.

- [ ] **Write block 2.3 — Error handling & validation.** Pull from EXPERIENCE_PROOF Q1.6 + TECHNICAL Q5/Q6 + study_guide/03 §8 mass-assignment. Key points: RFC 7807 structured errors + machine-readable `code` (the NFTRACE retrofit); Pydantic 422 auto-validation; separate input vs domain models (prevent mass-assignment / `is_admin` escalation); never leak stack traces. What they check: do your errors serve the frontend as a contract. 

- [ ] **Write block 2.4 — API performance & scalability.** Cross-reference block 1.1/1.3 (don't repeat) — add only the items not yet said: response_model to trim payload, pagination (cursor vs offset), Redis cache-aside + TTL, async I/O, push slow work to queue. Keep tight.

---

### Task 4: JD Section "Frontend Integration Awareness" — GAP SECTION (author in full, see Appendix A)

**JD lines:**
1. "Work closely with frontend teams (React/Next.js)."
2. "Understand API consumption patterns from frontend."
3. "Ensure smooth data exchange and endpoint design."
4. "Support/debug API issues impacting UI."

- [ ] **Write the full Frontend Integration block using Appendix A below, verbatim in substance.** This is the #1 depth gap. The candidate is NOT a React dev — the honest frame is "I design APIs as products React/Next.js teams consume; I understand their consumption model deeply even though I don't write the components." Cover: how React Query/SWR consume + cache; Next.js Server vs Client Components + BFF/route-handler proxy; where the JWT lives (memory vs localStorage vs httpOnly cookie) + the CORS/credentials/SameSite consequences for the backend; CORS preflight mechanics; data-exchange contract details (casing, dates, null-vs-missing, enums, pagination shape); the triage method for "the UI is broken." End with the honest bridging frame.

---

### Task 5: JD Section "Database & SQL Understanding"

**JD lines:**
1. "Write and understand SQL queries (joins, aggregations, filters)."
2. "Design and maintain relational database schemas using SQL (PostgreSQL/MySQL/SQL Server)."
3. "Ensure data accuracy, consistency, and integrity across systems."
4. "Troubleshoot and support database-related issues."

- [ ] **Write block 4.1 — SQL queries.** Pull from 4.SQL_WITH_SOLUTIONS.md. Key points: logical execution order (FROM→WHERE→GROUP BY→HAVING→SELECT→ORDER→LIMIT); the 5 must-nail patterns (Nth-per-group window, anti-join, duplicates, top-N-per-group, count-including-zeros); narrate while writing. What they check: likely a LIVE query — point hard to 4.SQL_WITH_SOLUTIONS.md as the Friday drill.

- [ ] **Write block 4.2 — Schema design.** Pull from EXPERIENCE_PROOF Q4.1/Q4.5 + TECHNICAL Q37/Q38. Key points: Brane multi-agent schema (junction `lo_input_execution_agent` + sibling execution tables); junction-models-relationship-not-mutable-state lesson; normalization + deliberate denormalization trade-off; PostgreSQL deepest, fundamentals transfer to MySQL/SQL Server. What they check: have you designed schemas under real constraints.

- [ ] **Write block 4.3 — Data accuracy/consistency/integrity.** Pull from EXPERIENCE_PROOF Q4.6 + TECHNICAL Q36. Key points: FK constraints (ON DELETE CASCADE for cleanup, RESTRICT for protection — the over-aggressive-cascade bug); ACID; transactions; app-logic-enforces-before-DB, FK is the safety net. 

- [ ] **Write block 4.4 — Troubleshoot DB issues.** Pull from EXPERIENCE_PROOF Q4.2/Q4.3 + TECHNICAL Q34. Key points: N+1 (query-logging middleware, 51→1 LEFT JOIN); slow query (EXPLAIN ANALYZE / EXPLAIN QUERY PLAN → Seq Scan → index → verify); the `WHERE DATE(col)=` function-defeats-index trap; index write-penalty trade-off. What they check: a repeatable process, not luck. Point to study_guide/04.

---

### Task 6: JD Section "Snowflake (Working Knowledge Only)"

**JD lines:** "Basic understanding of Snowflake data warehouse concepts / Read and understand queries / Support backend integrations with Snowflake."

- [ ] **Write block 5.1 — Snowflake honest depth.** Pull from TECHNICAL Q41-44 + study_guide/05. Key points: OLAP vs OLTP (Snowflake analytics, Postgres transactions); separated storage + compute → virtual warehouses scale independently, auto-suspend; columnar; standard SQL + `snowflake-connector-python`/SQLAlchemy dialect → integrate behind a clean data-access layer + cache hot reads; QUALIFY as the one Snowflake-specific flex (filter on window fn without subquery). `💀` Honesty: "hands-on warehouse work is primarily PostgreSQL; I understand Snowflake's model and it's standard SQL with a connector — I'd ramp fast; the JD asks working-knowledge and that's an honest match." Never bluff depth here — getting caught bluffing Snowflake taints everything.

---

### Task 7: JD Section "DevOps & CI/CD"

**JD line:** "Knowledge of CI/CD and API logging and Monitoring."

- [ ] **Write block 6.1 — CI/CD + logging/monitoring.** Pull from EXPERIENCE_PROOF Q8.x + TECHNICAL Q55/Q58 + study_guide/07. Key points: GitLab pipeline (lint→test→docker build→integration→approval→staging→smoke→prod); the Docker checklist you authored (pinned base, non-root, no build-time secrets) adopted team-wide; prompt-regression CI suite catching 70%→55% accuracy drop before ship; structured JSON logs + request_id; RED metrics; alert on symptoms (error rate >1%, p99 >2× baseline, DLQ depth, queue depth, background-job failures), not noise; K8s liveness vs readiness. What they check: have you operated a system, not just deployed once.

---

### Task 8: JD Section "Version Control & Collaboration"

**JD lines:** "Use Git for branching, merging, pull requests, and code reviews / Agile environment / technical discussions, architecture reviews, sprint planning."

- [ ] **Write block 7.1 — Git + code review.** Pull from TECHNICAL Q53/Q54 + EXPERIENCE_PROOF Q9.2/Q9.3. Key points: feature-branch → small commits → PR → CI green + review → merge; merge vs rebase + the golden rule (don't rebase shared/pushed history); the code-review checklist you authored (thread safety, Docker) → +25% quality, adopted team-wide; mentoring via review-as-teaching. 

- [ ] **Write block 7.2 — Agile / collaboration.** Pull from TECHNICAL Q60 + EXPERIENCE_PROOF Q9.1. Key points: Scrum (sprints, standups, planning, review, retro, JIRA), Agile sprint reports, zero missed deliveries; pushing back with data + an alternative (the WebSockets-vs-polling story); architecture reviews. What they check: senior = drives technical discussion, not just attends.

---

### Task 9: Microservices Deep Dive — GAP SECTION (author in full, see Appendix B)

- [ ] **Write the Microservices Deep Dive using Appendix B below.** study_guide/06 already covers monolith-vs-micro, saga, outbox, communication — DO NOT repeat those. This deep dive adds: (1) the gRPC model gateway as a genuine, fully-articulated microservice story (why separate, boundaries, statelessness, provider routing, deadline propagation); (2) inter-service authentication (the under-covered topic) — network trust/mTLS, service tokens via client-credentials, RS256 JWT public-key verification; (3) the honest scope frame. Point to study_guide/06 for saga/outbox/decomposition.

---

### Task 10: Closing — JD Coverage Checklist

- [ ] **Write a checklist** the candidate ticks the morning of: every JD line as a checkbox with a 3-word reminder of the anchor (e.g. "REST APIs → NFTRACE lifecycle ✓"). One screen. This is the "nothing on their list is unanswered" final scan.

---

### Task 11: Update START_HERE

- [ ] **Update `interview_pack/0.START_HERE.md`:** change "7 files" → "8 files"; add file 8 = JD_MASTER_GUIDE.md described as "the verification layer — every JD requirement mapped to your proof; study it the day before as the integration pass"; add to SUN evening in the cram plan ("skim JD_MASTER_GUIDE.md — confirm every JD line has an answer").

---

## APPENDIX A — Frontend Integration block (author this content in full in the file)

> Write this as spoken, study-ready prose under JD Section "Frontend Integration Awareness." Preserve all technical specifics below.

**Honest opening frame (say this first if asked about React/Next.js):**
"I'm backend, not a React developer — I want to be upfront about that. But I design every API as a product a frontend team consumes, and I've worked through the real friction points with frontend devs: CORS, auth token handling, pagination contracts, and response-shape stability. I understand their consumption model — how React Query caches, how Next.js fetches on the server versus the client — well enough to design endpoints they can integrate cleanly and to debug with them when something breaks."

**A1. How React/Next.js actually consumes your API.**
- Modern React rarely calls `fetch` raw in components. It uses **React Query (TanStack Query)** or **SWR** — libraries that wrap your endpoint in a cache keyed by a "query key," handle loading/error states, deduplicate concurrent requests, and **refetch on window focus or reconnect**. Why you (backend) care: they cache by key and expect a **stable response shape** for that key. If `GET /jobs/{id}` sometimes returns `result: null` and sometimes omits `result`, their cache and their TypeScript types break. Shape stability is a contract.
- **Next.js App Router** splits data fetching: **Server Components** (`async` components) fetch on the Next.js server — no CORS, the request originates server-side, and Next extends `fetch` with caching (`fetch(url, { next: { revalidate: 60 } })`). **Client Components** (`"use client"`) fetch in the browser — CORS applies. So "the frontend calling you" is sometimes the browser and sometimes the Next.js server; they have different CORS and auth behavior.
- The **BFF pattern**: Next.js **Route Handlers** (`app/api/.../route.ts`) often sit between the browser and your API as a backend-for-frontend — the browser calls Next, Next calls you server-to-server. This is why a frontend dev may say "no CORS issue on our side" — because the browser never hits your API directly.

**A2. Where the JWT lives — and why it's YOUR problem.**
- Three storage options, each a trade-off: **localStorage** (survives reload, simple, but XSS-readable — any injected script steals it); **in-memory** (XSS-safe-ish, lost on reload, needs silent refresh); **httpOnly cookie** (JS can't read it → XSS-safe, but CSRF-exposed → needs `SameSite` + sometimes a CSRF token).
- The modern Next.js answer: refresh token in an **httpOnly, Secure, SameSite cookie**; short-lived access token in memory — or the **BFF pattern where tokens live server-side in the Next session and the browser never sees a token at all.**
- Why backend cares: **if they use cookies, your CORS must set `allow_credentials=True`, the frontend must send `credentials: 'include'`, and you CANNOT use `allow_origins=['*']`** — that combination is illegal and the browser rejects it. If API and frontend are on different domains, the cookie needs `SameSite=None; Secure` or it won't be sent at all. These are backend config decisions driven by a frontend storage choice — so you decide them together.

**A3. CORS — the real mechanics (the #1 frontend-backend friction point).**
- The browser enforces same-origin policy; cross-origin calls trigger CORS. **Simple requests** (GET/POST, simple headers) just need `Access-Control-Allow-Origin` on the response. **Non-simple requests** — custom headers like `Authorization`, methods like PUT/DELETE, or `Content-Type: application/json` — trigger a **preflight OPTIONS** request first. Your API must answer the OPTIONS with `Allow-Origin`, `Allow-Methods`, `Allow-Headers`, and (for cookies) `Allow-Credentials`, before the browser will send the real request.
- The three classic failures: (1) `allow_origins=['*']` **with** `allow_credentials=True` → browser rejects, invalid combo; (2) forgetting `Authorization` in `allow_headers` → preflight passes but the real authenticated request is blocked, which looks like "auth randomly fails"; (3) no `Access-Control-Max-Age` → OPTIONS fires on every single request, adding latency.
- The tell to say out loud: **"A CORS error in the browser console is almost always a server-side config issue, not a frontend bug. The giveaway is 'works in Postman, fails in the browser' — Postman doesn't enforce CORS; browsers do. So when a frontend dev reports it, I check my CORS middleware first."**

**A4. Smooth data exchange — the contract details that cause friction.**
- **Casing:** backend snake_case vs frontend camelCase. Decide once — either emit camelCase via a Pydantic alias generator, or document that the frontend maps it. Don't be inconsistent across endpoints.
- **Dates:** always ISO 8601 UTC strings (`2026-06-22T09:00:00Z`). Never mix epoch ints and strings — the frontend feeds these straight into date-fns/dayjs.
- **Null vs missing:** pick one. A field that's sometimes `null` and sometimes absent breaks JS destructuring and TS types differently. Use `response_model` with explicit defaults so the shape is invariant.
- **Enums as strings,** not magic ints — the frontend switches on `"status": "processing"`, not `2`.
- **Pagination shape:** infinite-scroll UIs (React Query `useInfiniteQuery`) want a **stable cursor + `hasMore`**. Offset/limit breaks during infinite scroll when rows are inserted/deleted between pages — items duplicate or vanish. Cursor pagination is stable under change. Say this — it shows you've thought past the demo.
- **Error envelope:** one consistent shape (`{error:{code,message}}` or RFC 7807) lets the frontend write **one** axios interceptor / React Query `onError` handler instead of a special case per endpoint.

**A5. Supporting/debugging API issues impacting the UI.**
- Triage order: reproduce with **curl/Postman first** to isolate backend vs frontend. If it works there but not in the browser → CORS, cookies, or a client bug. If it fails there too → it's mine.
- The **Network tab is the shared language**: ask the frontend dev for the failing entry's status code, request/response headers, and payload. That one screenshot resolves most disputes.
- **OpenAPI is the contract:** FastAPI auto-generates it; the frontend can generate TypeScript types from it (`openapi-typescript`), so a shape change surfaces as a compile error instead of a runtime surprise. When I change a response, the spec changes, and `/v1` versioning means I never break their current build.

**A6. The honest close (if pushed on hands-on React):**
"I haven't built production React myself — my hands-on UI work is Streamlit front-ends for internal tools. But the API-design and debugging side of frontend collaboration I've done repeatedly: defining the contract up front (we wrote the OpenAPI spec with the SDK team before either side built), resolving CORS, designing error and pagination shapes the client can consume. That's the part of frontend integration this role actually needs from a backend engineer, and I'm strong there."

---

## APPENDIX B — Microservices Deep Dive (author this content in full in the file)

> study_guide/06 covers monolith-vs-micro, communication, saga, outbox, decomposition, and the full ad-API design. DO NOT repeat those — point to them. Write ONLY the three additions below.

**B1. Your real microservice — the gRPC model gateway (tell it as a designed service, not a footnote).**
"At Brane I built the gRPC model gateway — and it's a genuine microservice, not a module. It was a separate service for concrete reasons: its **scaling profile was different** from the application API — model calls are heavy and slow, the app API is light and fast, so they needed to scale independently; its **deploy cadence was different** — provider routing logic changed often without touching the app; and it **isolated a concern** — multi-provider routing across instruct, thinking, and vision models behind one typed contract. I made it **stateless** — no session state in memory, all routing config and provider health in PostgreSQL — so horizontal scaling was just adding instances behind a load balancer. The early mistake was an in-memory connection pool per instance, which multiplied connections and hit provider limits at 3+ instances; I moved connection management to per-request setup. I chose **gRPC over REST** because it's internal, high-throughput, strongly typed via protobuf, runs on HTTP/2, and supports **deadline propagation** — the caller's timeout flows through to the gateway so a slow provider can't outlive the request that wanted it."

**B2. Inter-service authentication (the topic interviews probe and most candidates miss).**
"Once you have services talking to each other, 'how does service A trust service B' is a real question. Three approaches, increasing in rigor:
- **Network trust / mTLS:** services live in a private network; mutual TLS means each side presents a certificate, so both authenticate each other at the transport layer. Common in a service mesh (Istio/Linkerd) where the mesh injects the certs.
- **Service tokens via OAuth2 client-credentials:** the machine-to-machine flow — service A presents its own `client_id`/`client_secret` to an auth server, gets a short-lived access token, and sends it to B. No user involved.
- **RS256 JWT with public-key verification:** the auth service signs tokens with a **private** key; every other service verifies with the **public** key. The win is that no service except the issuer holds the signing secret — a leaked service can't mint tokens. This is exactly why RS256 beats HS256 once you have more than one service: with HS256's shared secret, every service that can verify can also forge."

**B3. The honest scope frame.**
"I'll be straight about scope: my microservices experience is the gRPC model gateway plus designing service decomposition — not running a 50-service mesh. But I think that's the right instinct anyway. My rule is start with a well-structured modular monolith and extract a service only when there's a concrete reason — a different scaling profile, a different deploy cadence, separate team ownership, or a compliance boundary. The gateway met that bar — heavy, slow, independently scaled — so it earned being its own service. I've seen the alternative: teams that went microservices-first and spent six months on service-mesh and tracing infrastructure instead of shipping. Senior judgment here is knowing when *not* to split."

---

## Self-Review Checklist

- [ ] Every JD line from IBridge_Tech_soft.md has a block (cross-check against the JD file).
- [ ] Strong areas pull 3-5 sharp points + pointer; they do NOT duplicate whole files.
- [ ] Appendix A (frontend) and Appendix B (microservices) reproduced in full with all specifics.
- [ ] Honesty frames present for React, microservices scope, Snowflake — no faked project experience.
- [ ] Metrics exact; project anchors real.
- [ ] START_HERE updated to 8 files.
