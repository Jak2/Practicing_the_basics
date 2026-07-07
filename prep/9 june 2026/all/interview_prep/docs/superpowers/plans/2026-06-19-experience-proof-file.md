# Experience Proof File Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `interview_pack/6.EXPERIENCE_PROOF.md` — a file of 35+ experience-validation Q&As that replaces `1.TECHNICAL_ANSWERS.md` as the primary study material, structured around JD requirements not topics, with every answer grounded in real project experience.

**Architecture:** Unlike `1.TECHNICAL_ANSWERS.md` (which answers "what is X"), this file answers "prove you've done X for 5 years at a senior level." Every question is what an interviewer asks to validate experience against the JD. Every answer references real projects with specific technical details, scar tissue (what failed), and seniority signals (what I'd do differently). The format is spoken English — say it out loud, not read silently.

**Answer format per question (4-beat structure):**
1. **Anchor** — name the specific project/situation immediately
2. **What I built** — concrete technical details (not abstract)
3. **What was hard / what failed** — scar tissue; this is what proves real experience
4. **Seniority signal** — what I learned, what I'd do differently, or how it connects to this role

## Global Constraints

- Spoken, natural English throughout — these are said aloud, not read
- Every answer MUST reference a real project by name (NFTRACE, 5G pipeline, Brane, RF Generator)
- No generic "best practice" answers — every answer has specific technical detail
- Honest about gaps — don't invent experience that isn't there
- `⚠️` for weak answer traps, `→ Follow-up:` for likely follow-up probes, `💀` for danger zones
- Interview is Monday June 22, 2026 — answers must be study-ready immediately
- Metrics: NFTRACE −50%, 5G pipeline 70%/−55%, Brane (no specific metric), code reviews +25%

## Candidate Context (agent must know this to write authentic answers)

**Projects:**
- Nokia Aug 2022–Jun 2025 (2y 10m):
  - NFTRACE: FastAPI lifecycle endpoints (start/stop/merge/validate), Redis session isolation (`session:{uuid}` → JSON blob), SQLite persistence, XML-RPC SDK, decoupled test scenarios from validation → −50% pipeline validation time
  - 5G failure pipeline: Pyshark → LangChain RetrievalQA → Chroma vector DB → LLM (claude-sonnet-4-6) → Redis cache → 70% auto-resolution, −55% MTTR, hours→seconds
  - RF Keyword Generator: Streamlit + FastAPI, LLM entity extraction + deterministic templates + regex fallback = 100% uptime, 50+ weekly generations
  - K8s pod health monitoring, Agile sprint reports, zero missed deliveries
  - Mentored 3 engineers to senior level, authored code review checklists (thread safety, Docker) → +25% code quality

- Infinite Computer Solutions/Nokia-Ext Jun 2025–Apr 2026 (10m):
  - Continued 5G pipeline work, UDM/AUSF testing continuity across employer transition

- Brane Apr 2026–Jun 2026 (2m):
  - PostgreSQL schema: identity tables, multi-agent LO junction tables, attribute-level RBAC (subjects/resources/attributes/permissions), execution sibling tables (`lo_input_execution_agent`, `agent_run_scratch`, `agent_episodes`)
  - gRPC model gateway: stateless horizontal, multi-provider (instruct/thinking/vision)
  - Parser hardening for malformed LLM outputs, verifier-with-retry loop
  - RBAC caching for hot-path permission checks

- Abjayon Jan 2022–Jul 2022 (7m): Node.js, AWS AppSync/AppFlow, GraphQL/REST APIs, IAM roles
- Lakshya Space Mar 2021–Jan 2022 (10m): Python firmware, mentored 19 interns

**JD requirements to cover:**
1. Scalable RESTful backend APIs using FastAPI
2. Microservices-based architecture + async processing
3. High performance, reliability, security
4. Backend architecture and system design contribution
5. Third-party API integration
6. Authentication (JWT/OAuth), error handling, validation
7. Frontend collaboration (React/Next.js)
8. SQL/database schema design and data integrity
9. Snowflake (basic)
10. CI/CD + logging/monitoring
11. Git + code reviews + Agile
12. AI tools usage

---

### Task 1: Build the complete `6.EXPERIENCE_PROOF.md` file

**Files:**
- Create: `interview_pack/6.EXPERIENCE_PROOF.md`

- [ ] **Write the file header and usage instructions**

```markdown
# 6. EXPERIENCE PROOF — Proving 5 Years of Senior Backend Experience

> This file REPLACES `1.TECHNICAL_ANSWERS.md` as your primary study material.
> `1.TECHNICAL_ANSWERS.md` tests knowledge ("what is X"). This tests experience ("prove you've done X").

## The interviewer's mindset
They've read your resume. They've read the JD. They're now asking:
*"This person claims 5 years of senior backend experience. Does that experience actually prove they can do what we need?"*

Every question here is one they'll ask to validate experience — not test knowledge.

## How to use this file
1. Read the model answer once for the shape.
2. Close the file. Say it in YOUR words, referencing YOUR actual projects.
3. It must sound like your experience, not a script you memorized.
4. Each answer: ~60-90 seconds spoken. Land the point and stop.

## Answer format (4 beats — internalize this)
1. **Anchor** — name the project/situation immediately ("At Nokia, when I built NFTRACE...")
2. **What I did** — specific technical detail, not generic description
3. **What was hard** — this is what proves real experience; interviewers listen for this
4. **Seniority signal** — what I learned, what I'd do differently, how it applies here

⚠️ **The tell that exposes shallow experience:** answers that describe the *concept* instead of *what happened*. "Async is good for I/O-bound work" is knowledge. "At Nokia, we had a blocking `requests.get()` inside an `async def` that looked fine but stalled the event loop under load — here's how we found it" is experience.
```

- [ ] **Write Section 1: FastAPI & Backend API Design (7 questions)**

Questions to answer:
1. "Walk me through the most complex FastAPI service you've designed from scratch."
2. "Tell me about a time your API had a performance problem in production. How did you find and fix it?"
3. "How have you structured large FastAPI applications? Walk me through a real example."
4. "What's the most subtle bug you've hit in an async FastAPI service?"
5. "Tell me about a time you had to design an API contract with a frontend team before either side started building."
6. "How do you handle error responses in production? Why does it matter to frontend teams?"
7. "How do you test FastAPI services? Walk me through your approach."

Each answer must: reference NFTRACE or 5G pipeline specifically, include at least one thing that went wrong, be 4-6 spoken sentences.

- [ ] **Write Section 2: Async & Concurrency (5 questions)**

Questions to answer:
1. "Tell me about a production async processing system you built. What were the key design decisions?"
2. "Have you ever hit the event loop blocking problem in production? Walk me through it."
3. "How have you handled long-running tasks in an API? What did you use and why?"
4. "Tell me about a time a background job failed silently. How did you detect it and what changed?"
5. "When would you choose Celery over FastAPI's BackgroundTasks? Give me a real example."

Each answer must: reference the 5G pipeline async work, include what could go wrong with BackgroundTasks in production, be honest about the Celery vs BackgroundTasks trade-off from real experience.

- [ ] **Write Section 3: Authentication & Security (5 questions)**

Questions to answer:
1. "Walk me through how you've implemented JWT authentication in a real production service."
2. "Tell me about the most complete authorization system you've built. How did you model permissions?"
3. "Have you ever found or fixed a security issue in an API? What was it?"
4. "How do you handle token revocation? What's the trade-off?"
5. "Tell me about a time you had to design for least-privilege access. What were the decisions?"

Each answer must: reference the Brane attribute-level RBAC work specifically (subjects/resources/attributes/permissions tables), include the JWT "signed not encrypted" production gotcha, reference IAM roles work at Abjayon for the least-privilege question.

- [ ] **Write Section 4: Database Design & SQL (6 questions)**

Questions to answer:
1. "Tell me about the most complex database schema you've designed. Walk me through the decisions."
2. "Have you hit an N+1 query problem in production? How did you find and fix it?"
3. "Tell me about a time you had to debug a slow query. What was your process?"
4. "How do you handle database migrations on a live system with active users?"
5. "Tell me about a time you had to model a many-to-many relationship. What were the trade-offs?"
6. "How do you ensure data integrity across related tables? Give me a real example."

Each answer must: reference the Brane RBAC schema design (the junction tables, the attribute/permission model), include an EXPLAIN ANALYZE war story, be honest about SQLite limitations in NFTRACE.

- [ ] **Write Section 5: System Design & Architecture (5 questions)**

Questions to answer:
1. "Tell me about the most significant architecture decision you've made. What were the options and why did you choose what you did?"
2. "Have you worked on a system that needed to scale horizontally? What did you do to enable that?"
3. "Tell me about a time you integrated with a flaky or slow third-party service. How did you make it reliable?"
4. "Walk me through how you'd approach designing the backend for an ad-creative generation API." (the JD's exact domain)
5. "Tell me about a time you had to choose between a simpler and a more complex architecture. How did you decide?"

Each answer must: reference the gRPC model gateway (stateless horizontal scaling), the regex fallback for 100% uptime, the 5G pipeline's Redis caching strategy. The ad-creative design question must be fully answered using the candidate's actual patterns.

- [ ] **Write Section 6: Third-Party Integration & Resilience (4 questions)**

Questions to answer:
1. "Tell me about a time a third-party API failure affected your service. How did you handle it?"
2. "What's your approach to making external API calls reliable? Walk me through the layers."
3. "Tell me about a time you implemented caching to reduce dependency on an external service."
4. "How have you handled webhook integrations? What were the gotchas?"

Each answer must: reference the regex fallback in the RF Generator (100% uptime despite LLM downtime), the Redis caching in the 5G pipeline (turned LLM calls from slow to near-instant for repeat errors), timeout/retry/circuit breaker pattern from real usage.

- [ ] **Write Section 7: Frontend Collaboration (3 questions)**

Questions to answer:
1. "How have you worked with a React/Next.js frontend team on API design? What worked and what didn't?"
2. "Tell me about a time a frontend team had a problem with your API. How did you debug and resolve it?"
3. "How do you design error responses for frontend consumers? What's your philosophy?"

Each answer must: reference NFTRACE's XML-RPC SDK (designing for client consumers), FastAPI's auto-generated OpenAPI docs as the collaboration tool, CORS as a real production gotcha. Be honest if direct React collaboration is limited — frame it around API contract design.

- [ ] **Write Section 8: CI/CD & Production Operations (4 questions)**

Questions to answer:
1. "Walk me through your deployment process. From code commit to production — what happens?"
2. "Tell me about a production incident you were involved in. What happened, what was your role, what changed?"
3. "How do you monitor and log a production API? What do you actually alert on?"
4. "Tell me about a time a CI pipeline you built caught something important before it reached production."

Each answer must: reference the GitLab CI pipeline work, the Docker checklists the candidate authored (and which the team adopted), the K8s pod health monitoring at Nokia, the zero-missed-deliveries record. The prompt regression CI suite counts as a CI pipeline story.

- [ ] **Write Section 9: Seniority, Leadership & Ownership (5 questions)**

Questions to answer:
1. "Tell me about a time you pushed back on a technical decision. How did you handle it?"
2. "How have you mentored junior engineers? What's your approach and what results did you see?"
3. "Tell me about a time you improved a process or standard for your whole team."
4. "What's the biggest technical mistake you've made? What did you learn from it?"
5. "Tell me about a time you had to ramp up on a new technology quickly for a project."

Each answer must: reference mentoring 3 engineers to senior level, the code review checklists (adopted team-wide, +25% quality), the Nokia→Infinite transition with zero disruption. The "mistake" question should reference a real failure (malformed LLM output parser, or the session isolation gap in NFTRACE).

- [ ] **Write Section 10: AI Tools (3 questions)**

Questions to answer:
1. "How do you use AI tools in your development workflow? Give me a concrete example."
2. "Has using AI assistance ever led you to ship code you didn't fully understand? How do you prevent that?"
3. "The JD asks for someone who leverages AI to improve efficiency — how have you done that in practice?"

Each answer must: frame AI as a multiplier for implementation speed (not a replacement for engineering judgment), reference the review-every-line discipline, explain the "I understand it before it ships" principle. Be honest that AI was used but own the design decisions, debugging, and production thinking.

- [ ] **Write the closing section: "The Experience Credibility Test"**

A self-check the candidate runs before the interview:
- Can you say each answer without reading it, referencing your actual project?
- For every answer, can you answer one follow-up question about a specific detail?
- Do your metrics stay consistent? (−50%, 70%, −55%, 3 engineers, 19 interns, +25%)
- Is there any answer where you're describing theory instead of your experience? Replace it.

- [ ] **Save the file to `interview_pack/6.EXPERIENCE_PROOF.md`**

- [ ] **Update `interview_pack/0.START_HERE.md`** to add a reference to the new file:
  - Change the "6 files" section to "7 files"
  - Add: `6. **EXPERIENCE_PROOF.md** — 35+ experience-validation Q&As. Replaces TECHNICAL_ANSWERS.md as primary study. Use this if you only have time for one file.`
  - Update the 4-day plan to reference this file on Thursday and Saturday instead of TECHNICAL_ANSWERS.md

---

## Self-Review Checklist

- [ ] Every question maps to at least one JD requirement
- [ ] Every answer references a real project by name
- [ ] Every answer has scar tissue (what went wrong or was hard)
- [ ] All metrics are consistent with resume
- [ ] No generic "best practice" answers that could be about anyone
- [ ] Spoken English throughout — no textbook definitions
- [ ] Danger zone questions have honest (not bluffing) answers
- [ ] Section 10 (AI tools) is honest about AI-assisted development without undermining credibility
