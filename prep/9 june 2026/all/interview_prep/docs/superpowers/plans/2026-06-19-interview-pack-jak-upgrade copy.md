# Interview Pack — jak Persona Upgrade Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade all 5 files in `interview_pack/` with the jak_ai_job_coach persona — veteran production layers, follow-up trap warnings, AI-honesty framework, danger zone scripts — while preserving the spoken, natural tone that makes this pack distinct from the reference study_guide.

**Architecture:** Each file is independent. The pack is written as spoken scripts (not reference material), so jak additions must be woven into the answers naturally — not bolted on as separate headers. The tone stays: clear, natural, spoken English. The substance becomes: scar tissue, not just knowledge.

**Tech Stack:** Markdown content files. No code, no tests. Each task = rewrite one file.

## Global Constraints

- Preserve spoken, natural English tone throughout — these are scripts to be said aloud, not read
- Do NOT add heavy section headers like "## Interviewer is Testing" — use inline callouts (`⚠️`, `→ Follow-up:`, `💀 Danger:`) that scan quickly
- Every veteran layer must be 1-3 sentences max woven into the answer — not a paragraph block
- Danger zone scripts must be HONEST — no bluffing scripts
- The candidate used AI to build their systems and doesn't remember all internals — every answer must be defensible under follow-up
- Keep file sizes manageable — these are study material, not exhaustive references
- `0.START_HERE.md` is NOT modified — it's the discussion context, leave it as-is

## Candidate context (all tasks need this)

**Projects:**
- Nokia/Infinite: NFTRACE (FastAPI + Redis session isolation key=`session:{uuid}` + SQLite + XML-RPC, −50% validation time)
- Nokia: 5G pipeline (Pyshark → LangChain RetrievalQA → Chroma vector DB → LLM → Redis cache, 70% auto-resolve, −55% MTTR)
- Nokia: RF Keyword Generator (hybrid LLM entity extraction + deterministic templates + regex fallback = 100% uptime)
- Brane (2 months): PostgreSQL schema (identity tables, junction tables for many-to-many agent↔LO, attribute-level RBAC rows, execution sibling tables), gRPC model gateway (stateless, multi-provider: instruct/thinking/vision), parser hardening + verifier-retry

**Critical risk:** AI-assisted dev who may not remember exact internals. Must be honest without bluffing.

---

### Task 1: Upgrade `1.TECHNICAL_ANSWERS.md`

**Files:**
- Modify: `interview_pack/1.TECHNICAL_ANSWERS.md`

**What to add (woven inline, preserving existing answers):**

For each section, add before risky questions: `⚠️ Weak answer trap:` (one line warning of what gets candidates rejected).
After answers that will draw follow-ups: `→ If they follow up: "[exact follow-up question]" — [one-sentence answer]`

**Specific additions per section:**

**Section 1 — FastAPI:**
- Q3 (async/sync): add veteran layer to the answer — "The production failure mode: you have `async def` with `requests.get()` inside. Works fine in dev, freezes under load because it blocks the entire event loop for every waiting user." Add follow-up: "What happens if you call a sync library inside async def?" → "It blocks the event loop — use `run_in_threadpool` or switch to an async equivalent."
- Q4 (Depends): add veteran layer — "The production gotcha: if you use yield deps for DB sessions and your route also has a BackgroundTask, the session closes before the task runs. Pass data into the task, not the session itself."
- Q8 (scale): add after answer — "→ If they follow up: 'What's the rule of thumb for worker count?' → `2 × CPU cores + 1` is the starting point, then tune based on profiling."
- Add NEW Q13 (CORS production gotcha): "`allow_origins=['*']` with `allow_credentials=True` is **invalid** — browsers reject it silently and your auth calls just fail. Always use explicit origins in production, and don't forget `Authorization` in `allow_headers`."

**Section 2 — Python:**
- Q13 (GIL): add veteran layer — "The thing that trips people up: async I/O doesn't fight the GIL at all. You're not threading — you're cooperatively yielding. GIL only matters for CPU-bound threading, which you shouldn't be doing anyway."
- Q16 (generators): add production example — "Real production use: streaming a 1M-row database result. With a list you load 4GB into memory. With a generator you hold one row at a time — memory stays flat."
- Add NEW Q22 (mutable class attribute trap): "Same problem as mutable default args, but at the class level. `class Foo: items = []` — all instances share the same list. Every instance you create appends to the same list. Use `def __init__(self): self.items = []` instead."

**Section 3 — Auth:**
- Q22 (JWT): add veteran layer inline — "One critical point: JWT is *signed*, not *encrypted* — anyone can base64-decode the payload and read it in DevTools. Never put sensitive data like passwords, internal IDs, or PII in the payload."
- Q22: add follow-up — "→ If they follow up: 'How do you revoke a JWT before it expires?' → Short expiry (15 min) plus a Redis blacklist for logout/compromise events. The blacklist stores the token's `jti` claim and checks it on each request."
- Q27 (secure API): add OWASP — "The #1 API security mistake is broken object-level authorization — you authenticate correctly but forget to check that the user actually owns the resource they're requesting. `GET /ads/{id}` should verify the ad belongs to the requesting user, not just that the user is logged in."

**Section 4 — Databases:**
- Q33 (indexes): add EXPLAIN ANALYZE — "→ If they follow up: 'How do you actually read EXPLAIN ANALYZE output?' → Look at the leftmost node first (that's the innermost operation). 'Seq Scan' on a large table is the red flag — it means no index is being used. 'Index Scan' or 'Index Only Scan' means it's working. Check the actual rows vs estimated rows — a big discrepancy means stale statistics, run ANALYZE."
- Q34 (slow query debug): add war story — "A real one: a date filter `WHERE DATE(created_at) = '2026-01-01'` looks fine but wraps the column in a function, which prevents the index on `created_at` from being used. The fix: `WHERE created_at >= '2026-01-01' AND created_at < '2026-01-02'`. EXPLAIN ANALYZE shows the difference immediately."
- Add `⚠️ Weak answer trap:` before Q33 — "Saying 'indexes make queries faster' is the minimum. The senior answer covers: the write penalty, leftmost prefix rule for composite indexes, covering indexes, and when NOT to add one."

**Section 5 — Snowflake:**
- Add honest framing script after Q44: "💀 If they push deeper than the JD scope: 'I want to be straight — my hands-on warehouse work is PostgreSQL. I understand Snowflake's architecture well: separated storage and compute, virtual warehouses, columnar storage for OLAP workloads. Since the JD asks for working-knowledge support, I'm confident I'd ramp quickly — it's standard SQL with a Python connector.' Honesty here beats bluffing."

**Section 6 — System Design:**
- Q45 (monolith vs micro): add veteran layer — "The real cost nobody talks about in interviews: distributed transactions, cross-service debugging, data consistency across service boundaries. Teams go microservices-first and spend 6 months building infrastructure instead of product. Split when you have a concrete reason — different scaling needs, different deployment cadence, different team ownership."
- Q51 (ad creative design — the most likely system design question): This answer is already good. Add at end: "→ Key follow-up: 'What happens if the AI generation service is down?' → Circuit breaker stops sending requests. Return a queued/pending status. Retry the job when the service recovers. The user gets their result later — degraded experience, not broken experience."

**Section 7 — DevOps:**
- Q57 (Docker): add AI-assisted dev trap — "⚠️ The Docker mistake that trips up AI-assisted devs: using `FROM python:latest` as the base image. The `latest` tag is mutable — it silently changes when a new version ships, breaking your build unexpectedly. Pin it: `FROM python:3.11-slim`. Also: secrets passed as `ENV` in a Dockerfile leak into `docker history` — inject at runtime via environment, not build time."
- Q59 (incident debug): add structure — "The order matters: first check metrics to see *when* it started and whether it correlates with a recent deploy. Then logs with a failing request ID. Hypothesis before fix — don't restart the service blindly hoping it goes away."

- [ ] Read current `1.TECHNICAL_ANSWERS.md`
- [ ] Write the upgraded version with all additions above woven in naturally
- [ ] Verify spoken tone is preserved throughout
- [ ] Save to `interview_pack/1.TECHNICAL_ANSWERS.md`

---

### Task 2: Upgrade `2.PROJECT_SCRIPTS.md`

**Files:**
- Modify: `interview_pack/2.PROJECT_SCRIPTS.md`

**What to add:**

**For each project, add a "💀 DANGER ZONE" subsection** — the follow-up questions that expose AI-assisted development. Each danger entry has: the exact question, the HONEST answer (not a bluff), and what NOT to say.

**Project 1 — 5G Pipeline danger zone:**
- "What was the Redis key schema for the cache?" → Honest: "The key was based on the error signature — something like `error:{hash_of_signature}` mapping to the cached resolution. I'd need to check the exact implementation, but the design was: content-addressable so the same error always hits the same cache entry."
- "How did you handle LLM rate limits?" → Honest: "The pipeline included retry logic with backoff. If I'm being precise, the rate limit handling was part of the LangChain layer — I didn't write custom rate limit logic, I configured the retry parameters. What I did own was the caching layer that reduced how often we hit the LLM at all."
- "How did you measure the 70%?" → "Against manual triage baseline over a sample period — it's an observed reduction, not a formal A/B test with statistical significance. If they press for more precision, I'd say 'roughly' and explain the measurement approach."

**Project 2 — NFTRACE danger zone:**
- "What was the Redis key schema for session isolation?" → "The key was `session:{uuid}` mapping to a JSON blob of the scenario's execution state — what nodes had run, their outputs, current status. The UUID was generated per test run so parallel runs each had their own isolated namespace."
- "What would happen if Redis was unavailable?" → Honest: "Honestly, I'd need to check whether we had a fallback for Redis unavailability — if Redis was down, parallel test isolation would break. That's a gap I'd close in production by adding a health check and graceful degradation path."
- "Why not use PostgreSQL for the session state instead of Redis?" → "Speed. Session state was read and written on every step of a test run — potentially hundreds of reads per second during parallel execution. PostgreSQL would've added latency on every step. Redis kept it sub-millisecond."

**Project 3 — Brane danger zone:**
- "Walk me through the exact RBAC table structure." → "The core tables were: a `subjects` table (agents/users), a `resources` table (the logical objects they could act on), an `attributes` table (the specific attributes of resources), and a `permissions` table linking subjects → resources → attributes → allowed actions. Junction tables handled the many-to-many agent↔logical-object relationships."
- "What exactly was YOUR contribution vs the team's?" → "I worked on specific schema components — the identity tables, the RBAC permission model, the junction tables for multi-agent relationships, and the execution sibling tables. I also did the parser hardening and helped build the verifier-retry loop. The broader runtime — the agent loop orchestration, the UI layer — was the wider team's work."
- "How did you handle the RBAC cache invalidation?" → Honest: "Cache invalidation was tied to permission change events — when a permission row was updated or deleted, the relevant cache keys were evicted. If I'm being honest, the exact invalidation strategy was something I worked on but I'd need to look at the code to give you the exact key pattern we used."

**Add AI Honesty Framework section** (after the three projects):
```
## The AI Tools Question (they WILL ask — the JD says it explicitly)

**Q. "How do you use AI tools in your development work?"**

Script:
"I use Claude Code as a pair programmer — for scaffolding FastAPI endpoints, writing test suites, drafting SQL, and reviewing my code before PRs. My workflow is: I describe the requirement, review what it generates line by line, understand it before committing it, and often modify it significantly to fit the actual constraints. It roughly doubles my throughput on boilerplate, which lets me focus on the design decisions, edge cases, and production considerations that the tool doesn't know about. I treat it as a very capable assistant whose suggestions I always review — not an authority."

⚠️ Do NOT say: "I use AI for everything" / "I just describe what I want and it builds it" / "I couldn't have done [project] without it." These destroy your credibility as a senior engineer.

The frame: AI is a multiplier for implementation speed. Design judgment, production thinking, debugging, and code review are still yours.
```

**Add "What I'd Do Differently" per project** (senior signal — shows growth):
- 5G pipeline: "I'd add more aggressive TTL strategy — cache the lookup result but also cache a 'no known fix' result to prevent hammering the vector DB for novel errors. And I'd add a queue depth alert so we'd know when the pipeline was backing up before users noticed."
- NFTRACE: "If write volume grew I'd replace SQLite with PostgreSQL. And I'd add a `/health` endpoint that checked Redis connectivity — the platform had no way to detect a silent Redis failure."
- Brane: "I'd build the RBAC cache invalidation more defensively — right now it invalidates on explicit permission changes, but if the cache got stale for any other reason, we'd serve wrong permissions until TTL expired. I'd add a shorter TTL as a safety net."

- [ ] Read current `2.PROJECT_SCRIPTS.md`
- [ ] Write upgraded version with DANGER ZONE per project, AI honesty framework, "What I'd do differently" sections
- [ ] Preserve the 90-second story format and "why" defenses
- [ ] Save to `interview_pack/2.PROJECT_SCRIPTS.md`

---

### Task 3: Upgrade `3.BEHAVIORAL_ANSWERS.md`

**Files:**
- Modify: `interview_pack/3.BEHAVIORAL_ANSWERS.md`

**What to add:**

**Follow-up attack questions after each STAR story** — what an experienced interviewer asks to verify you built it. Format: `→ If they probe deeper: "[question]" — [honest 1-sentence answer]`

**After NFTRACE story (performance improvement):**
- "Walk me through exactly how the Redis session isolation worked." → "Each test run got a UUID at start. The session key was `session:{uuid}` holding a JSON blob of execution state. Workers read and wrote their own key — no shared state between runs."
- "What was the failure mode if Redis went down mid-run?" → "Parallel isolation would break — tests could corrupt each other's state. We had a health check but not a clean fallback. That's one thing I'd improve today."

**After 5G pipeline story:**
- "How did Pyshark actually parse the packets — what did you get back?" → "Pyshark wraps tshark's dissectors. You iterate over packets in a capture file, each packet has layers accessible as attributes — like `packet['nas-5gs'].message_type` for 5G NAS signaling. I extracted the message type and relevant fields to build the error signature."
- "Was the 70% a measured result or an estimate?" → "Observed over a sample period against the prior manual baseline — not a formal A/B test, but a consistent and dramatic improvement. I'd say 'roughly 70%' if precision is pushed."

**Add "When you don't know something" script:**
```
**Q. What do you do when you don't know the answer to a technical question?**

"My honest approach: I say 'let me think through that' and reason out loud. If I genuinely don't know, I say 'I haven't worked with that directly, but based on [related thing I do know], I'd approach it by...' — and I give a real reasoning attempt, not a bluff. What I never do is invent a fact or a metric I can't back up. If they catch that, it destroys everything."
```

**Add Interview Recovery Scripts section:**
```
## Recovery Scripts (for when it goes wrong in the room)

**If the interviewer corrects a wrong answer:**
"You're right — I was conflating [X] with [Y]. The correct answer is [Z]." Calm, brief, move on. Don't over-apologize.

**If you start an answer and realize mid-sentence you're going wrong:**
"Actually, let me reframe — the core point is [one clear thing]..." Trail the old sentence cleanly and start fresh.

**If you go completely blank:**
"Let me think through that." [3-5 seconds of actual thinking, out loud if possible.] If still blank: "I'd need to think about that more carefully — what I do know is [related concept], which would point me toward..." Never freeze in silence for more than 5 seconds.

**If they ask about something on your resume you can't defend deeply:**
"That [library/tool/approach] was [part of the existing stack / something I used but didn't author / something I've worked with at the integration level rather than the internals]. What I can speak to with confidence is [the design decision / the integration pattern / what problem it solved]."
```

**Add seniority signal to behavioral answers:**
Before "Tell me about yourself" add:
`⚠️ Seniority signal: don't open with tech stack. Open with impact and ownership. "I architected..." not "I used FastAPI to build..."`

- [ ] Read current `3.BEHAVIORAL_ANSWERS.md`
- [ ] Write upgraded version with follow-up attack questions, recovery scripts, "don't know" answer, seniority signal callouts
- [ ] Preserve 60-90 second STAR format and spoken tone
- [ ] Save to `interview_pack/3.BEHAVIORAL_ANSWERS.md`

---

### Task 4: Upgrade `4.SQL_WITH_SOLUTIONS.md`

**Files:**
- Modify: `interview_pack/4.SQL_WITH_SOLUTIONS.md`

**What to add:**

**Live coding narration protocol** (add at top, after the execution order):
```
## How to Narrate While Writing SQL (more important than the answer)

Before you write a single character:
1. "So I need to [state what you're finding in plain English]."
2. "The pattern here is [name the pattern — anti-join / window rank / running total]."
3. "I'll [state your approach in one sentence]."

While writing:
- Say what each clause does: "FROM orders — that's my main table. LEFT JOIN users — I want all orders even if no user match..."
- When you use a window function: "PARTITION BY department means we rank within each department separately."
- When you write HAVING: "HAVING not WHERE because I'm filtering on the aggregate, not individual rows."

If you make a mistake:
"Actually — I need to think about that again. [Correct it out loud.] That's better."

The interviewer is scoring HOW you think, not just the final SQL.
```

**Add 3 new patterns:**

**Query 11 — Delete duplicate rows (keep one)**
```sql
DELETE FROM users
WHERE id NOT IN (
  SELECT MIN(id)
  FROM users
  GROUP BY email
);
```
Why: group by the duplicate column, keep the minimum ID per group (the "original"), delete everything else. Alternative using CTE for readability shown. Explain why `NOT IN` vs `NOT EXISTS` (EXISTS is safer with NULLs).

**Query 12 — Customers active in ALL months of a quarter**
```sql
SELECT customer_id
FROM orders
WHERE order_date BETWEEN '2026-01-01' AND '2026-03-31'
GROUP BY customer_id
HAVING COUNT(DISTINCT DATE_TRUNC('month', order_date)) = 3;
```
Why: `DATE_TRUNC` normalizes dates to month, `COUNT(DISTINCT ...)` counts unique months, HAVING = 3 means all three. Classic "every X" pattern.

**Query 13 — Rank + filter in one (with QUALIFY in Snowflake)**
Standard SQL:
```sql
SELECT name, department, salary FROM (
  SELECT name, department, salary,
         ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) rn
  FROM employees
) t WHERE rn = 1;
```
Snowflake shortcut:
```sql
SELECT name, department, salary,
       ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) rn
FROM employees
QUALIFY rn = 1;
```
Why: `QUALIFY` is Snowflake-specific — it filters on window functions directly without a subquery. Knowing this signals real Snowflake familiarity.

**Add AI-dev trap questions section:**
```
## ⚠️ AI-Dev Trap Questions (what interviewers use to test if you understand your own SQL)

These are follow-ups designed to expose copy-paste SQL. Practice answering each out loud.

1. "Why DENSE_RANK and not RANK for the Nth highest salary?"
   → RANK skips numbers on ties (1,1,3) so rank=2 would return nothing if two people are tied for first. DENSE_RANK never skips (1,1,2) so it always finds the Nth value.

2. "In the anti-join query, why `WHERE o.id IS NULL` and not `WHERE o.user_id IS NULL`?"
   → `o.id` is the primary key — it's never NULL for a real row. `o.user_id` could theoretically be NULL for other reasons. Filtering on the PK is the cleanest anti-join pattern.

3. "Why does `COUNT(o.id)` give 0 for users with no orders, but `COUNT(*)` gives 1?"
   → `COUNT(column)` skips NULLs. `COUNT(*)` counts every row including the NULL row that LEFT JOIN produces. Using `COUNT(*)` here would incorrectly count users with no orders as having 1 order.

4. "Your WHERE filter on `created_at` — would an index on `created_at` be used?"
   → Only if the filter doesn't wrap the column in a function. `WHERE DATE(created_at) = '2026-01-01'` defeats the index. `WHERE created_at >= '2026-01-01' AND created_at < '2026-01-02'` uses it.

5. "What's the difference between `EXISTS` and `IN` for a subquery?"
   → EXISTS short-circuits on the first match — fast for "is there any match." IN evaluates all subquery results. For large subqueries, EXISTS is usually faster. Also: IN can behave unexpectedly when the subquery returns NULLs; EXISTS handles them correctly.
```

- [ ] Read current `4.SQL_WITH_SOLUTIONS.md`
- [ ] Write upgraded version with narration protocol, 3 new patterns, AI-dev trap questions
- [ ] Preserve the cover-and-attempt format and worked explanation per query
- [ ] Save to `interview_pack/4.SQL_WITH_SOLUTIONS.md`

---

### Task 5: Rebuild `5.ONE_PAGE.md`

**Files:**
- Modify: `interview_pack/5.ONE_PAGE.md`

**What to add/update:**

The ONE_PAGE is a glance sheet — keep it tight. But it needs to reflect the jak upgrades:
- Add DANGER ZONE callouts (3-line section, not a full section)
- Add recovery scripts one-liners
- Add AI-tools answer one-liner
- Update FastAPI section with blocking trap callout
- Update Auth section with JWT encryption myth
- Add OWASP #1 to security section

Format rules: every line must be scannable in under 3 seconds. No sentences longer than 15 words. Use `→`, `✓`, `⚠️`, `💀` for fast scanning.

- [ ] Read current `5.ONE_PAGE.md`
- [ ] Rebuild with jak additions while preserving scan-speed
- [ ] Every section must fit within ~8 lines
- [ ] Save to `interview_pack/5.ONE_PAGE.md`

---

## Self-Review Checklist

- [ ] All 5 jak requirements present in each file: veteran layer, follow-up traps, weak answer warnings, honest AI framing, danger zone scripts
- [ ] Spoken tone preserved — no textbook language introduced
- [ ] No bluffing scripts — every danger zone answer is honest
- [ ] `0.START_HERE.md` untouched
- [ ] The candidate's specific project details (Redis key schema, table names, metrics) are correct throughout
- [ ] No contradiction between files (same metrics, same framing)
