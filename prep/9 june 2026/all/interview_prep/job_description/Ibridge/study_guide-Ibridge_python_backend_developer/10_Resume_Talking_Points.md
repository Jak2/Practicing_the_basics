# 10 — Resume → JD Mapping & Talking Points

Every JD requirement mapped to a concrete thing on your resume. Walk in knowing you already check almost every box.

---

## JAK'S RISK LEGEND

Every claim on your resume has been rated:

- **SAFE** — You can defend this deeply under a 10-minute follow-up. Go confident.
- **MODERATE RISK** — Sounds good, needs specific prep. Know one level deeper.
- **HIGH RISK** — A senior interviewer will probe hard. Prep the exact answer or soften the claim.
- **CRITICAL RISK** — Claim cannot survive a direct follow-up question. Either prep it until it can, or stop making it.

---

## 1. Requirement → Your evidence

| JD requirement | Your proof | JAK Risk |
|---|---|---|
| Scalable RESTful APIs in FastAPI | NFTRACE (FastAPI lifecycle endpoints), Brane agent runtime | SAFE |
| Microservices architecture | gRPC model gateway — multi-provider routing, stateless horizontal scaling | MODERATE RISK |
| Asynchronous processing | AsyncIO, Celery, multiprocessing; 5G async remediation pipeline | MODERATE RISK |
| High performance/reliability | Redis caching (5G, NFTRACE), 70% auto-resolution, 55% MTTR, 50% validation cut | HIGH RISK |
| Backend architecture/system design | Architected NFTRACE distributed platform; agent runtime contributions | SAFE |
| Auth (JWT/OAuth) | Attribute-level RBAC at Brane; IAM roles at Abjayon | HIGH RISK |
| Error handling & validation | Pydantic; response parser hardening; regex fallback (100% uptime) | SAFE |
| Frontend integration (React/Next.js) | React + Vite, Tailwind on resume; FastAPI serving frontends | MODERATE RISK |
| SQL (joins/aggregations/schema) | PostgreSQL schema — identity tables, junction tables, RBAC rows, sibling tables; SQLAlchemy | MODERATE RISK |
| Data integrity | Relational schema design, RBAC permission rows, execution history persistence | MODERATE RISK |
| Snowflake (basic) | Gap — cover via file 05; data-warehouse-adjacent via AWS data pipelines | CRITICAL RISK if overclaimed |
| CI/CD | Prompt Regression CI/CD suite, GitLab; Docker/K8s | SAFE |
| Logging & monitoring | K8s pod health + real-time cluster dashboards (Nokia) | MODERATE RISK |
| Git (branch/merge/PR/review) | Git/GitLab daily; authored code review checklists adopted team-wide | SAFE |
| Agile / cross-functional | Agile sprint reports, zero missed deliveries, multi-vendor coordination | SAFE |
| Leverage AI tools | Claude Code on resume + entire AI-integrated portfolio | SAFE |
| Mentoring/seniority | Mentored 3 to senior readiness; led 19 interns; 25% code-quality gain | SAFE |

---

## 2. Technical claims that could become traps

These are the resume items that sound impressive and will draw a follow-up question. Know the answer cold.

### Trap 1: "Attribute-level RBAC" — HIGH RISK

**Why it's a trap:** Any backend engineer who has designed RBAC (Role-Based Access Control) will immediately ask what this means at the table level.

**Likely question:** "You mention attribute-level RBAC — walk me through how you modeled that in PostgreSQL. What tables, what queries?"

**Expected depth:** The interviewer wants: table names (or reasonable equivalents), how permissions are attached to attributes rather than just resources, how you'd query "does user X have permission Y on attribute Z of resource R?"

**What a strong answer looks like:**
> "We had a resources table, a resource_attributes table (attributes attached to resources, like fields of an agent config), a permissions table (what actions were possible — read, write, execute), a roles table, a role_permissions table linking roles to specific permissions on specific attributes, and a user_roles table. So to check if user X can write to the 'model_config' attribute of agent Y: join user_roles → role_permissions → resource_attributes → filter by attribute name and action. The key difference from resource-level RBAC is that permissions are scoped to individual attributes, not just the resource itself."

**Prep task:** Write out the table names and one example query before Monday. Even if the actual schema differed slightly, having a concrete answer is what matters.

---

### Trap 2: "50% validation time reduction" — HIGH RISK

**Why it's a trap:** A strong number on a resume invites the question "how did you measure that?"

**Likely question:** "How did you baseline and measure the 50% improvement? Was that automated or manual measurement?"

**Expected depth:** What was measured (wall clock of CI pipeline runs), what the baseline was, how you collected data, whether it was a one-time measurement or an ongoing metric.

**What a strong answer looks like:**
> "We measured wall-clock time of the CI pipeline runs in GitLab. Before NFTRACE, the full validation suite ran sequentially and we had concrete baseline numbers from the GitLab job logs. After the Redis-backed session isolation enabled parallel execution, we benchmarked over a week of pipeline runs and saw consistent halving of the end-to-end validation time. The number came from comparing average run times, not a single run."

**Prep task:** Know the approximate baseline number (e.g., "average runs were around X minutes, we got it to Y").

---

### Trap 3: "70% auto-resolution rate" — HIGH RISK

**Why it's a trap:** "Auto-resolution" is ambiguous. Did it mean the system fixed things automatically, or that it produced suggestions engineers accepted 70% of the time?

**Likely question:** "When you say 70% auto-resolution — was that fully automated, or engineer-assisted? How was that measured?"

**What a strong answer looks like:**
> "Engineer-assisted. The pipeline would analyze the pcap, identify the failure pattern, and produce a suggested remediation. An engineer would review and apply it. We tracked the acceptance rate — how often the suggested fix was used without modification — and that was 70%. The 55% MTTR (Mean Time To Resolution) reduction is what we measured on the clock: time from failure detection to resolved ticket."

**If the reality was different from this, use your actual answer. The point is: have a specific answer ready.**

---

### Trap 4: "gRPC model gateway with stateless horizontal scaling" — MODERATE RISK

**Likely question:** "How did you achieve stateless scaling? What state was being eliminated, and where did it go?"

**What a strong answer looks like:**
> "Session state — which model to route to, auth context, request metadata — was passed in the request itself or stored in a shared cache rather than in gateway instance memory. Each request was self-contained, so any gateway instance could handle it. That's the stateless property. Horizontal scaling meant spinning up additional gateway pods behind a load balancer with no coordination needed between instances."

---

### Trap 5: "Led 19 interns" — MODERATE RISK

**Likely question:** "What did leading 19 interns look like in practice — what did you actually do with them?"

**What a strong answer looks like:** Be specific about the structure. Did you run standups? Do 1:1s? Review their code? Define their project scope? "I scoped their projects, ran weekly milestone check-ins, reviewed their PRs, and gave structured feedback on both code quality and professional communication" is a real answer.

---

### Trap 6: Redis key schema (NFTRACE) — HIGH RISK

This will come up if you go deep on NFTRACE. Know it.

**Likely question:** "What did the Redis key schema look like for session isolation? What data structure — hash, string, sorted set?"

**Prep task before Monday:** Write down (or reconstruct) the key pattern and data structure. Example: `session:{session_uuid}:state` as a Redis Hash with fields for status, node_list, current_phase. Know the TTL policy. Know what happened if two clients tried to start the same session.

---

## 3. Your three flagship stories (lead with these)

**1. NFTRACE (architecture + API design + performance)**
- *S:* CI/CD test pipelines for network functions were slow and entangled — full reruns for isolated changes.
- *T:* Build a distributed tracing platform decoupling scenarios from validation, enabling parallel execution.
- *A:* FastAPI endpoints for lifecycle (start/stop/merge/validate), Redis-backed session caching for parallel-run isolation, SQLite persistence for node state/history, XML-RPC client SDK for toolchain integration.
- *R:* 50% reduction in pipeline validation time across CI/CD.

**2. 5G failure remediation pipeline (async + caching + integration)**
- *S:* Engineers spent hours manually analyzing pcap logs for 5G signaling errors.
- *T:* Auto-detect and suggest fixes for common failure patterns.
- *A:* Pyshark extracts errors → LangChain RetrievalQA against vector DB of known patterns → LLM suggests fixes → Redis caches frequent lookups → regex fallback for LLM unavailability.
- *R:* 70% auto-resolution rate, 55% MTTR reduction, hours → seconds.

**3. Brane agent runtime (schema design + microservices + RBAC)**
- *S:* No-code platform needed a production AI agent runtime with proper access control.
- *T:* Contribute to schema design, model-serving, and reliability.
- *A:* PostgreSQL schema contributions (identity, multi-agent junction tables, attribute-level RBAC permission tables, execution sibling tables); worked on gRPC (Google Remote Procedure Call) model gateway with stateless horizontal scaling + multi-provider routing; response-parser hardening for malformed LLM outputs.
- *R:* Reliable multi-agent execution; reduced tool-invocation overhead.

---

## 4. The 2-month Brane question — specific defensible claims

You were at Brane for approximately 2 months. A senior interviewer will ask a follow-up on anything you claim here. These are the things you can claim specifically and defend.

**What you can say you did:**
- Designed or contributed to the PostgreSQL schema for agent identity and versioning
- Implemented junction tables for multi-agent workflow membership (many-to-many: agents ↔ workflows)
- Contributed to the attribute-level RBAC model — specifically the permission and attribute mapping tables (see Trap 1 above for the table structure to know)
- Worked on execution history tables (sibling tables tracking concurrent runs separately to avoid contention)
- Contributed to response-parser hardening for the LLM gateway integration — Pydantic models catching malformed responses, retry logic

**What you should NOT claim without qualification:**
- "I built the RBAC system" → say "I contributed to the RBAC schema design, specifically..."
- "I architected the gRPC gateway" → say "I worked on the gateway and understood its design"
- Any infrastructure claims (K8s setup, deployment pipeline) unless you specifically did that work

**The framing for the short tenure:**
> "Two months is a short engagement. The work I focused on was schema design — the RBAC model and the multi-agent execution tables. I can go deep on that because it was my primary contribution. I also worked on response-parser hardening for the LLM integration. The tenure was short because [honest reason]. The schema work was real and I can walk you through it."

---

## 5. Snowflake gap — specific ramp plan

**Current state:** Zero hands-on Snowflake experience.

**What you actually know:**
- Snowflake separates compute (virtual warehouses) from storage (cloud object storage) — this is the core architecture distinction
- Virtual warehouses scale independently; you can have multiple warehouses querying the same data without contention
- Standard ANSI SQL — the query language is not a new skill
- Python connector (snowflake-connector-python) is the integration path — standard cursor interface
- Time Travel and Fail Safe are Snowflake's data recovery features
- Micro-partitioning is how Snowflake stores data (different from traditional row/column stores)

**What you do NOT know hands-on:**
- Warehouse sizing and cost optimization
- Snowflake-specific performance tuning (clustering keys, query profiling)
- Data sharing, Snowpark, or any Snowflake-specific features beyond basic SQL

**Week 1 ramp plan (say this in the interview if asked):**
> "My plan for week one would be: set up a trial account and run through the quickstart with real queries, build a Python connector integration against a sample schema, and read through the query profiling documentation. Given that my SQL fundamentals are strong and I've designed schemas in PostgreSQL, the main learning is Snowflake-specific behavior — warehouse management and cost controls. I'd expect to be productive on standard query work within a few days and operational on the platform within the first two weeks."

**What NOT to say:** "I have working knowledge of Snowflake" or any implication of hands-on experience. A single technical follow-up will expose this.

---

## 6. Talking-point reframes (say it the backend way)

- Don't say "I built an LLM pipeline." Say "I built an **async data-processing pipeline that integrates a third-party inference service**, with Redis caching and a vector store."
- Don't say "prompt engineering." Say "**request assembly and response parsing/validation** for an external service, with retry-on-failure and fallback logic."
- Don't say "agent loop." Say "a **stateful processing loop with a verifier/correction retry mechanism**."
- gRPC gateway = "**microservice with horizontal stateless scaling and provider routing**."
- Don't say "I used Claude to help build this." Say "I used AI tooling to accelerate scaffolding and test generation, reviewed and owned every line."

---

## 7. Handle the experience-number question

Resume says 5+ years; JD wants 6–8. Frame:
> "5+ years of hands-on backend, across telecom-grade systems at Nokia and production platforms at Brane — with senior responsibilities throughout: architecture ownership, mentoring three engineers to senior readiness, authoring team standards. The depth is there; the year count is close."

Don't dwell. Pivot to depth and impact.

---

## 8. Numbers to memorize — do not get these wrong

These are on your resume. If you say a different number in the interview, a careful interviewer will notice.

| Metric | Your number |
|---|---|
| NFTRACE validation time reduction | 50% |
| 5G auto-resolution rate | 70% |
| 5G MTTR reduction | 55% |
| Engineers mentored to senior | 3 |
| Interns led | 19 |
| Code quality improvement | 25% |

---

## 9. One-line self-summary to open and close with

> "Backend Python engineer — FastAPI, SQL, async architecture — who ships with measurable impact, is an immediate joiner, and already works the AI-assisted way your team values."
