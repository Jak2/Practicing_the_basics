# 08 — Behavioral, HR & Non-Technical

Use **STAR**: Situation → Task → Action → Result (lead with context, end with a metric). Your resume is full of metrics — use them.

---

## JAK'S WARNING BEFORE YOU READ THIS FILE

You built real systems. The risk is not that you're lying — the risk is that an experienced interviewer will go two levels deeper than your STAR story, and you'll stall. Every section below includes "follow-up attack questions." **If you cannot answer those questions cold, do not tell that story.** A confident "I haven't used X directly" beats a stumbling answer about something you supposedly built.

---

## 1. "Tell me about yourself" (2-min script — memorize)

> "I'm a backend Python engineer with 5+ years building production systems. At Nokia/Infinite I architected NFTRACE — a distributed tracing platform in FastAPI with Redis-backed session isolation and SQLite persistence that cut pipeline validation time by 50%. I also built a 5G failure remediation pipeline using async processing, Redis caching, and vector search that drove a 70% auto-resolution rate and 55% MTTR (Mean Time To Resolution) reduction. At Brane I worked on a production AI agent runtime — PostgreSQL schema design including attribute-level RBAC (Role-Based Access Control), a gRPC (Google Remote Procedure Call) model gateway with stateless horizontal scaling, and response-parser hardening for reliability. Throughout my career I've mentored engineers and led teams — three engineers I mentored reached senior level, and I led 19 interns while authoring code-review standards the team adopted. My core is API design, databases, async processing, and reliability. This role is a strong fit because it's exactly that stack — scalable FastAPI APIs, solid SQL, and AI-assisted backend development."

---

## 2. Address the elephant: "Your resume says AI Engineer — this is strictly backend"

> "Fair point. Every one of those projects is fundamentally FastAPI services, PostgreSQL schemas, async pipelines, caching, and API integration. The 'AI' part is mostly integrating LLM services as just another backend dependency — you write the same retry logic, the same parsing, the same schema. I'm a backend engineer first; AI is a tool I integrate and a tool I use to code faster — which is exactly what this JD asks for."

---

## 3. The AI-usage story — CRITICAL, READ THIS CAREFULLY

The JD explicitly says "leverage AI tools to improve efficiency." This is not a trick — they want you to use AI. But your honest answer needs to be: (a) enthusiastic, (b) honest about how you use it, (c) not expose that you can't defend the code you've written with it.

**Model answer (memorize the shape, not word for word):**

> "I use Claude Code heavily — for scaffolding FastAPI endpoints, generating test suites, drafting SQL, and doing pre-PR code review. My workflow is: I describe the requirement clearly, review everything it generates line by line, understand the approach before committing, and often modify it significantly. It doubles my throughput on boilerplate so I spend my time on design decisions, edge cases, and production considerations. I treat it like a very capable pair programmer — one whose suggestions I always review rather than accept blindly. The output is mine to own; I make sure I can explain every line."

**Why this answer works:** It's honest. It signals you're thoughtful. It preempts the "can you actually code" concern. It matches exactly what a senior engineer using AI responsibly looks like.

**What NOT to say:** "It writes most of my code and I review it." Even if partly true, this tells the interviewer you might not be able to defend your own resume.

---

## 4. STAR stories — with follow-up attack questions

### Story A: NFTRACE — Technical Achievement + Architecture

**STAR:**
- *S:* CI/CD test pipelines for Nokia 5G network functions were slow, tightly coupled, and reran full validations even for isolated changes.
- *T:* Architect a distributed tracing platform to decouple scenario execution from validation and enable parallel-run isolation.
- *A:* Designed FastAPI lifecycle endpoints (start/stop/merge/validate), Redis-backed session caching for parallel-execution isolation so concurrent test runs couldn't bleed into each other, SQLite persistence for node state and execution history, and an XML-RPC client SDK for existing toolchain integration.
- *R:* 50% reduction in pipeline validation time across CI/CD.

**Potential follow-up attack questions — be ready for all of these:**

1. "Walk me through exactly how the Redis session isolation worked. What data structure did you use? What was the key schema?"
   - *You must know:* Hash or string per session ID, key pattern like `session:{uuid}:state`, TTL policies, what happened on session conflict.

2. "Why SQLite and not PostgreSQL for persistence? What were the trade-offs?"
   - *You must know:* SQLite = embedded, no server, suited for per-node local state; PostgreSQL would require a network hop per CI node; the use case was local node persistence, not shared state.

3. "How did you handle concurrent writes to the same session? Did you use Redis transactions or Lua scripts?"
   - *You must know:* Whether you used MULTI/EXEC, pipeline batching, or relied on Redis single-threaded guarantees. If the answer is "Redis is single-threaded so we used atomic operations," say that. Don't claim Lua if you didn't.

4. "What does the FastAPI lifecycle endpoint actually do — what's the request/response shape for a 'merge' operation?"
   - *You must know:* The concrete endpoint contract, even roughly. "I don't remember the exact schema" is okay if followed by "but the concept was…"

5. "50% validation time — how did you measure that? What was the baseline?"
   - *You must know:* How it was measured (wall clock, CI runtime logs), roughly what the baseline was (e.g., 40 minutes → 20 minutes, or 8 minutes → 4 minutes).

**JAK's note:** If you can't answer questions 1 and 2 confidently, this story is MODERATE RISK. Prep the Redis key schema answer specifically — interviewers love to probe that.

---

### Story B: 5G Failure Remediation Pipeline — Async + Performance + Reliability

**STAR:**
- *S:* 5G network engineers spent hours manually inspecting pcap logs to diagnose signaling failures and find remediation steps.
- *T:* Build an automated pipeline to extract, classify, and suggest fixes for common failure patterns.
- *A:* Pyshark to extract structured error events from pcaps, LangChain RetrievalQA against a vector DB of known failure patterns to classify and suggest fixes, Redis caching for frequent pattern lookups to avoid re-querying the vector DB, async processing so multiple pcaps could be analyzed concurrently. Added a regex fallback layer for the most common failure signatures so the system kept working if the LLM service was unavailable.
- *R:* 70% auto-resolution rate, 55% MTTR reduction, analysis time went from hours to seconds.

**Potential follow-up attack questions:**

1. "What vector DB did you use? How did you structure the documents in the index — what was a single document?"
   - *You must know:* Chroma / Pinecone / FAISS — whichever you used. A document = one known failure pattern with its remediation steps. Metadata = failure type, severity.

2. "Walk me through what happened when the LLM service was down. You mentioned 100% uptime — how?"
   - *You must know:* The regex fallback path. What triggered the fallback, which failure types it covered, how it was tested.

3. "How did you handle async coordination — if 10 pcaps came in at once, what's the concurrency model?"
   - *You must know:* asyncio with a task queue, Celery workers, or multiprocessing. Be specific. "We used asyncio with a semaphore to cap concurrent pcap parses at N" is a real answer. "It was async" is not.

4. "Redis caching — what was the cache key? How did you handle cache invalidation when failure patterns were updated?"
   - *You must know:* Cache key design (hash of error signature? error type string?), TTL policy, whether invalidation was manual or TTL-based.

5. "How did you define 'auto-resolution' — was that an engineer confirming the suggestion worked, or automated?"
   - *You must know:* The measurement methodology. If it was engineer-confirmed, say so. Don't let "70% auto-resolution" imply full automation if it wasn't.

**JAK's note:** The 70%/55% numbers are strong — make sure you can explain how they were measured. If asked "how do you know it was 70%?" you need a real answer.

---

### Story C: Mentoring & Leadership

**STAR:**
- *S:* Team had junior-to-mid engineers who were productive but not yet owning architecture decisions or code review quality.
- *T:* Develop their technical depth and review skills to move toward senior readiness.
- *A:* Ran 1:1 code review sessions to explain the "why" behind feedback (not just flag issues). Authored a code review checklist covering the categories that most commonly caused production issues — error handling, input validation, transaction boundaries, test coverage. Led the checklist adoption across the team. For interns (19 across multiple cycles), structured their projects with clear scope and weekly milestones so they had ownership and I had visibility.
- *R:* Three engineers reached senior readiness. Code review checklist adopted team-wide, 25% improvement in code quality metrics.

**Potential follow-up attack questions:**

1. "What was on the code review checklist? Give me 5 categories."
   - *You must know:* Real categories. Examples: error handling completeness, input validation, database transaction scope, test coverage for edge cases, logging/observability, security considerations (injection, auth).

2. "How did you measure 25% code quality improvement?"
   - *You must know:* PR rework rate, bug counts in QA, or a stated team metric. "It was an estimate based on fewer review cycles and bug reports" is honest if that's true.

3. "What's the hardest mentoring situation you dealt with — someone who wasn't progressing?"
   - *You must know:* A real story. Not "everyone did great." Pick one challenge.

**JAK's note:** This story is SAFE territory. You have the numbers, you have the artifact (the checklist). Go deep here — it's a senior signal.

---

### Story D: Handling Failure / Tight Deadline

**STAR:**
- *S:* During a 5G deployment sprint with hard infrastructure deadlines (network nodes had maintenance windows), a pipeline component started producing inconsistent outputs due to malformed LLM responses we hadn't seen in testing.
- *T:* Keep the pipeline running — missing the deployment window meant a week's delay.
- *A:* Added response validation with Pydantic to catch malformed outputs immediately rather than letting bad data propagate. Built a regex fallback for the most common failure signatures so the pipeline could keep working on known patterns while the LLM issue was investigated. Added circuit-breaker logic to route to fallback when LLM error rate exceeded a threshold.
- *R:* Zero downtime. The deployment window was met. The fallback became a permanent reliability layer.

**Potential follow-up attack questions:**

1. "What did 'malformed LLM response' actually look like? What was the Pydantic model expecting?"
   - *You must know:* The structure you expected (JSON with specific fields), what the LLM would sometimes return instead (truncated JSON, extra text, wrong schema).

2. "How did the circuit breaker work — library or hand-rolled?"
   - *You must know:* Whether it was a library (tenacity, pybreaker) or a simple counter-based implementation.

---

### Story E: Conflict / Disagreement

**Prepare this as your own story.** Framework:
- Pick a real design disagreement — e.g., choice of database, caching strategy, API design.
- Show you made your case with evidence (benchmarks, requirements), listened to the other view, and either changed your mind (great signal) or found a compromise.
- The senior signal: you cared about the outcome, not about being right.

**JAK's note:** Do not invent this story. Pick a real one. "We had a disagreement about whether to use Redis or a DB-level lock for session isolation" is a perfectly good setup if it's real.

---

## 5. "What do you do when you don't know something in an interview?"

This question is critical for AI-assisted developers who may hit knowledge gaps mid-interview. The honest, senior answer:

> "If I don't know something specifically, I say so directly — I've found that senior interviewers respect honesty far more than a confident-sounding wrong answer. But I don't stop there. I'll say what I do know that's adjacent, how I'd find the answer in practice, and if it's something I should know, I'll acknowledge it's a gap I need to close. I'd rather show you how I think than fake depth I don't have."

**In practice during the interview:**
- "I haven't used Snowflake hands-on, but I know the architecture — it separates compute from storage, uses virtual warehouses, and the Python connector is standard. I could be productive on it in days."
- "I don't remember the exact parameter name off the top of my head, but the pattern would be X."
- Never: "Yes, I know that" followed by a wrong answer. That ends interviews.

---

## 6. Common HR questions + angles

- **Why this role / company?** — See Section 7 below. Do NOT give the generic answer from the old version.
- **Why leaving / why a contract?** Frame positively — seeking a backend-focused senior role where the work is primarily systems and APIs, not AI research. Immediate availability is your advantage — lead with it.
- **Strengths**: backend architecture, SQL schema design, reliability mindset, fast delivery under pressure, mentoring junior engineers to senior level.
- **Weakness** (real but managed): "I used to over-engineer for edge cases — designing for scale before we needed it. I've learned to ship the simplest correct version first, measure, then optimize. The NFTRACE Redis caching is a good example — I designed it to be replaceable with a different store if we needed to scale, but we started with the simplest key schema and evolved it."
- **Where in 3–5 years?** Senior/lead backend engineer owning architecture decisions and developing the engineers around me.
- **Handling feedback / code review?** You authored review checklists. Lead with that.
- **Salary / rate:** Know your number. Give a range, not a single figure. Let them anchor if possible.
- **Notice period:** Immediate joiner — say it early, say it clearly. It's a genuine advantage.
- **UK shift flexibility:** Confirm you're comfortable. The JD requires it.
- **Questions for us?** Always have 3 prepared (see Master Plan §6).

---

## 7. "Why this role?" — make it specific, not generic

The old answer ("backend depth + AI-leverage culture") is not wrong but it's not memorable. This is what a senior candidate says:

> "A few reasons that are specific to this role. First, the stack — FastAPI, PostgreSQL, async Python — is exactly where I've built production systems, not where I'm learning. I can be useful from week one rather than ramping on new tools. Second, the AI-assistance angle is something I actually do, not something I'd be adopting. I already use Claude Code in my workflow. Third, the seniority level matches where I am — I want to own API design and schema decisions, not just implement tickets. And the contract structure is genuinely fine with me — I'd rather have a focused senior backend role on contract than a vague full-time one."

**Customize this with one specific thing you learn about the company/client before the interview.** If you can say "I read that IBridge is building X, and that's directly relevant to Y I did at Nokia" — that's a different interview than the generic version.

---

## 8. Behavioral red flags SPECIFIC TO THIS CANDIDATE

These are the specific things that will expose AI-assisted development to an experienced interviewer. Prepare against all of them.

**Red flag 1: Can't explain a technical detail from your own project.**
- Trigger: "Walk me through exactly how X worked."
- What it sounds like: "We used Redis for caching... the key was, uh... I'd have to look at the code."
- Fix: Know the Redis key schema for NFTRACE. Know the vector DB document structure for the 5G pipeline. Know three tables in the Brane PostgreSQL schema. These are the three projects on your resume — you must be able to go one level deeper on each.

**Red flag 2: Giving a different number than what's on the resume.**
- Your resume says 50%, 70%, 55%. If you say "about 60%" in the interview, a careful interviewer will notice and probe.
- Fix: Memorize your own numbers. 50% validation time, 70% auto-resolution, 55% MTTR, 3 engineers to senior, 19 interns, 25% quality gain.

**Red flag 3: Overclaiming the 2-month Brane role.**
- You were at Brane for approximately 2 months. A senior interviewer will ask a follow-up about anything you claim from Brane.
- What overclaiming sounds like: "I designed the entire production RBAC system" → "What tables specifically?" → stall.
- Fix: See Section 9 (The Brane Question) and File 10 for specific defensible claims. Be clear about what was your work versus what you contributed to.

**Red flag 4: Claiming deep Snowflake knowledge.**
- You have none. If you imply you do and get a follow-up question, the interview is over.
- Fix: "I haven't used Snowflake hands-on — my data warehouse experience is adjacent via AWS pipelines. I've studied the architecture and I'm confident I'd ramp in days. Happy to be tested on SQL and schema design, which is the transferable core."

**Red flag 5: Vague answers on async details.**
- "It was async" is not an answer. "We used asyncio with Celery workers, capped concurrency with a semaphore at N tasks" is an answer.
- Fix: Know the concurrency model for both the Nokia pipelines. Be specific about the library.

**Red flag 6: Inconsistency on the "AI tools" framing.**
- If you say "I review every line" but then can't explain a design decision in your own code, the interviewer will connect those dots.
- Fix: The AI tools answer you give must match your actual ability to defend the code. Don't overclaim the review process.

---

## 9. The Brane question — 2 months, what can you defend?

You spent approximately 2 months at Brane. An interviewer may ask "that seems short — what did you actually accomplish?" Here is what you can claim specifically and defend:

**PostgreSQL schema contributions (pick what is true for you):**
- Designed or contributed to the identity and agent tables (agents, agent versions, agent configurations)
- Implemented junction tables for multi-agent relationships (many-to-many agent participation in workflows)
- Modeled attribute-level RBAC: permissions table, resource-attribute table, role-to-permission mapping rows — the design where access control is at the attribute level, not just the resource level
- Designed execution sibling tables for tracking concurrent agent runs without row collisions

**gRPC gateway:**
- Contributed to or reviewed the gateway design for stateless horizontal scaling
- Understood and worked with the multi-provider routing logic (routing to different LLM providers based on request parameters)

**How to frame the short tenure:**
> "Two months is short. In that time I focused on schema design and the data model — I made meaningful contributions to the PostgreSQL RBAC model and the multi-agent execution tables. I also worked on response-parser hardening for the LLM integration. I left because [honest reason — it was a short contract / the scope shifted / I was looking for longer-term stability]. I can go deep on the schema work because that's where I spent most of my time."

**JAK's rule:** Only claim specific Brane work you can describe at the table level. "I built the RBAC system" requires you to name tables and queries. "I contributed to the RBAC schema design, specifically the permission and attribute mapping tables" is defensible and still strong.

---

## 10. Closing strong

> "To summarize — backend Python, FastAPI, SQL, and async architecture are my core. I have production metrics behind me from two serious engineering environments. I'm an immediate joiner, comfortable with the UK shift requirement, and I already work the AI-assisted way this team values. I'm excited about this specific role."
