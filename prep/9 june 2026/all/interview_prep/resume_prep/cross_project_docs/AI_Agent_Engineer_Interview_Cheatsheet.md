# Senior AI Agent Developer — Interview Cheat Sheet
*Mapped to RightFit JD (UWM framework). Use this to drill, not to memorize verbatim — interviewers smell scripted answers.*

---

## 1. AGENT ARCHITECTURE FUNDAMENTALS

### 1.1 What is an "agent" (precise definition)
An LLM-based agent = LLM + memory + tools + a control loop that lets it decide *which* action to take next based on observation, not just generate one response. The defining feature vs a plain chatbot: **it can take multiple steps, observe results, and adapt** before returning to the user.

### 1.2 The core agent loop (ReAct-style)
```
1. Receive goal/task
2. LLM reasons about next step (Thought)
3. LLM selects a tool/action (Action)
4. System executes tool, returns result (Observation)
5. Loop back to step 2 until goal met or max steps hit
6. Return final answer
```
**Interview angle:** Be ready to draw this loop on a whiteboard cold. They will ask "what stops infinite looping?" → answer: max_iterations cap, cost/token budget, a verifier step that confirms task completion, or a timeout.

### 1.3 Single-agent vs Multi-agent — when to use which
| Single-agent | Multi-agent |
|---|---|
| Task fits in one context window | Task needs role specialization (researcher + coder + reviewer) |
| Sequential, simple tool use | Parallel sub-tasks, or adversarial roles (generator vs critic) |
| Lower cost, lower latency | Higher cost, but better quality on complex tasks |
| Easier to debug | Harder to debug — emergent failure modes |

**Your honest position:** Your Brane work is schema/runtime-level multi-agent support (junction tables, sibling tables for agent_run_scratch, agent_episodes) — NOT framework-level orchestration like CrewAI/AutoGen. State this distinction clearly if asked "have you used CrewAI?" Don't pretend you have.

### 1.4 Agent-to-Agent (A2A) Communication — the JD's specific ask
Core patterns you should be able to discuss even without hands-on A2A protocol experience:
- **Message passing** — agents exchange structured messages (often JSON) with sender/receiver/intent/payload.
- **Shared blackboard/state store** — agents read/write to common state instead of direct messaging (closer to what your junction-table design resembles).
- **Orchestrator-worker pattern** — a controller agent delegates to specialist agents and aggregates results (most common in production, easiest to reason about).
- **Hierarchical delegation** — manager agent → sub-manager agents → leaf agents.

**Honest answer if asked "have you implemented A2A protocol":** "I implemented the data layer that supports multi-agent coordination — junction tables linking agents to logic objects, execution sibling tables for agent state and episodes. I haven't implemented a formal A2A messaging protocol like Google's A2A spec or FIPA-ACL. I can speak to the architecture though." This is defensible. Claiming protocol-level expertise you don't have will collapse under 2 follow-up questions.

### 1.5 Memory & Context Management
- **Short-term/working memory** — current conversation/task context, lives in the prompt window.
- **Long-term memory** — persisted across sessions, usually a vector store or DB (your `agent_episodes` table is exactly this pattern).
- **Episodic memory** — record of past task executions (your `agent_episodes`, `agent_run_scratch` tables — be ready to explain these in depth, this is YOUR strongest material).
- **Context window management strategies:** summarization of old turns, sliding window, retrieval-based recall (pull only relevant past memory via embedding similarity), token budgeting.

**Drill question to expect:** "Walk me through what `agent_run_scratch` and `agent_episodes` actually store and why they're separate tables." → Practice this answer until fluent. This is your unique, defensible material — own it completely.

### 1.6 Human-in-the-Loop (HITL)
- Pattern: agent pauses execution at a defined checkpoint, surfaces a decision/output for human approval, resumes on approval/rejection.
- Implementation approaches: state machine with a "PENDING_APPROVAL" status persisted to DB (so it survives restarts), webhook/notification to human, resume via API call that re-hydrates agent state from DB.
- **Tradeoff to mention:** HITL kills latency/throughput but is mandatory for high-stakes domains (the JD mentions healthcare, fintech — HIPAA-adjacent). Tie this back to compliance reasoning if asked.

---

## 2. LLM INTEGRATION

### 2.1 Multi-provider routing (your gRPC gateway work — strongest section, drill hard)
Be ready to explain, in this order:
1. **Why gRPC over REST for model gateway** — binary protobuf serialization (smaller payload, faster parse than JSON), HTTP/2 multiplexing (multiple concurrent requests over one connection), strongly-typed contracts (protobuf schema catches mismatches at compile time vs runtime JSON errors), built-in streaming support (critical for token-by-token LLM output).
2. **Stateless horizontal scaling** — what makes a service stateless: no session/conversation state held in the gateway process itself; state lives in DB/cache (Redis), so any gateway instance can serve any request → you can scale by adding pods behind a load balancer with no sticky sessions needed.
3. **Routing logic** — how do you decide instruct vs thinking vs vision model? Likely: request metadata tags the required capability, router does a lookup/dispatch to the matching provider/model. Be ready to say what determined provider choice (cost, latency, capability) — if you don't fully recall the exact logic, say so and describe what you *do* recall precisely. Don't fabricate.

### 2.2 Prompt assembly pipeline (your Brane work)
Components you listed: system prompt, grounded input injection, tool registry context, retry-with-feedback (verifier correction loop). Be ready to explain EACH:
- **System prompt** — role/constraints/output format definition, usually static or templated.
- **Grounded input injection** — inserting retrieved/contextual data (RAG results, prior state) into the prompt so the model isn't hallucinating from parametric memory alone.
- **Tool registry context** — telling the model what tools exist, their schemas/params, so it can select correctly (function-calling style).
- **Retry-with-feedback / verifier correction loop** — when LLM output fails validation (malformed JSON, wrong schema, factually wrong), system feeds the error back to the LLM as a new turn ("your output failed because X, retry") instead of just failing. This is a strong, sophisticated talking point — drill it.

### 2.3 Response parser hardening (your bullet — expect deep drill)
What interviewers will probe: "LLMs don't always return clean JSON — what failure modes did you handle?"
- Markdown code fences wrapping JSON (```json ... ```)
- Trailing commas / single quotes instead of double
- Truncated output (hit max_tokens mid-object)
- Extra prose before/after the JSON object
- Field hallucination (model invents a field not in your schema)

Solid answer pattern: strip code fences → attempt strict JSON parse → fallback to a more lenient parser/regex extraction → validate against a schema (Pydantic) → if invalid, trigger the retry-with-feedback loop rather than silently failing.

### 2.4 RAG (Retrieval-Augmented Generation)
**Pipeline stages — know cold:**
1. Chunking (document → segments, typically 200-500 tokens, with overlap to avoid context loss at boundaries)
2. Embedding (chunk → vector, via embedding model)
3. Indexing (store vectors in vector DB with metadata)
4. Retrieval (query → embed → similarity search, usually cosine similarity or dot product → top-k chunks)
5. Augmentation (inject retrieved chunks into prompt)
6. Generation (LLM produces answer grounded in retrieved context)

**Tradeoffs to discuss:**
- Chunk size: too small = loses context; too large = dilutes relevance, wastes tokens.
- Top-k: too low = misses relevant info; too high = noisy context, higher cost.
- **Your honest gap:** you used LangChain `RetrievalQA` with a vector DB for 5G error matching — be ready to name what you actually know (was it FAISS, Pinecone, pgvector, Chroma?). If you don't remember exactly, say "I'd need to verify which vector store was used in that specific deployment" rather than guessing — a wrong guess here is worse than admitting uncertainty.
- **Hallucination mitigation in RAG:** citation/grounding checks, "answer only from context" system prompt constraints, confidence scoring, fallback to "I don't know" when retrieval confidence is low.

### 2.5 LLM Evaluation & Hallucination Detection (your project — own this)
Approaches to discuss:
- **Reference-based eval** — compare output to a known-correct answer (exact match, semantic similarity via embeddings, ROUGE/BLEU for text overlap — though these are weak for open-ended generation).
- **Reference-free eval (LLM-as-judge)** — use a second LLM call to score/critique the first output against a rubric. Cheap, scalable, but has its own bias/inconsistency.
- **Hallucination detection specifics** — check if claims in the output are entailed by the source/context (NLI-style entailment check), self-consistency checks (sample multiple generations, check agreement), citation verification (does claimed source actually contain the claim).
- Your project claims "4 minutes vs 3 days manually" — be ready to explain *what* the 3-day manual process was, and what exactly got automated. Vague performance claims are CRITICAL RISK if you can't defend the baseline.

---

## 3. BACKEND / SYSTEMS

### 3.1 FastAPI — know these cold
- Async by default — built on Starlette/ASGI, so I/O-bound endpoints (DB calls, external API calls) benefit hugely from `async def` + `await`.
- Pydantic integration — request/response validation is automatic from type hints; this is your strongest connective tissue between "Pydantic" and "response parser hardening" — interviewers will probe if you actually understand WHY Pydantic models prevent the malformed-output problems you described.
- Dependency injection via `Depends()` — used for auth, DB sessions, shared logic across endpoints.

### 3.2 AsyncIO vs Multiprocessing vs Celery — when to use which (you list all three, must distinguish cleanly)
| Tool | Use case | Why |
|---|---|---|
| **AsyncIO** | I/O-bound concurrency (many API calls, DB queries waiting on network) | Single thread, event loop, no GIL contention, lightweight |
| **Multiprocessing** | CPU-bound work (heavy computation, parsing large files) | Bypasses Python's GIL by using separate processes |
| **Celery** | Distributed task queue — background jobs, scheduled tasks, retries, cross-service work | Decouples task execution from request/response cycle, horizontally scalable workers |

**Drill question:** "Why not just use AsyncIO for everything?" → AsyncIO doesn't help CPU-bound work (GIL still blocks), and it doesn't give you durability/retry/distributed execution that Celery does.

### 3.3 gRPC vs REST vs GraphQL — comparative fluency required (you've used all three)
| | REST | GraphQL | gRPC |
|---|---|---|---|
| Payload | JSON, text | JSON, text | Protobuf, binary |
| Schema | Loose (OpenAPI optional) | Strict (GraphQL schema) | Strict (proto contract) |
| Best for | Simple CRUD, public APIs | Client needs flexible queries, avoid over/under-fetching | High-performance internal service-to-service, streaming |
| Streaming | Limited (SSE/websockets bolted on) | Limited | Native (bidirectional streaming) |

### 3.4 OAuth2 / JWT / Auth — JD explicitly requires this, be precise
- **OAuth2** — authorization framework/protocol; defines flows (authorization code, client credentials, etc.) for a client to get an access token without handling user passwords directly.
- **JWT** — a token *format* (header.payload.signature, base64-encoded, cryptographically signed) — often used as the access token in OAuth2 flows, but JWT itself is not an auth protocol, it's a credential format. **Do not conflate these two if asked to distinguish them — this is a classic trick question.**
- **Attribute-level RBAC (your Brane work)** — finer-grained than role-based access control; permissions checked per-attribute/field, not just per-endpoint/role. Be ready to explain: why attribute-level vs role-level? (Role-level = "can this user call this endpoint." Attribute-level = "can this user see/modify THIS field of THIS record" — needed when different agent roles need different visibility into the same data object.)

### 3.5 PostgreSQL deep dive (JD explicitly calls this out as core skill)
- **Indexing** — B-tree (default, good for equality/range), GIN (good for JSONB/array containment queries — relevant if your AI agent tables store JSONB payloads), partial indexes (index only a subset of rows matching a condition).
- **Stored procedures** — be ready to explain one you wrote, and why logic lived in DB vs application layer (usually: performance — avoid round-trips; or: enforce data integrity at the DB level regardless of which service writes to it).
- **Query optimization** — `EXPLAIN ANALYZE` to read query plans, identify sequential scans that should be index scans, N+1 query problems in ORMs (SQLAlchemy specifically).
- **Junction tables (your specific work)** — standard many-to-many relationship pattern; be ready to draw the schema for "multi-agent LO junction tables" on a whiteboard — what are the FKs, what's the cardinality, why junction table vs array column.

---

## 4. CLOUD / DEPLOYMENT

### 4.1 AWS services relevant to JD — minimum fluency required
| Service | Role in AI agent systems |
|---|---|
| EC2 | Raw compute, host services not containerized |
| Lambda | Event-driven, serverless — good for lightweight agent tool calls, webhooks |
| ECS/EKS | Container orchestration — ECS = AWS-native, EKS = managed Kubernetes |
| RDS (PostgreSQL) | Managed Postgres — backups, replication, failover handled by AWS |
| API Gateway | Front door for REST/HTTP APIs, handles throttling, auth |
| CloudWatch | Logging, metrics, alarms |
| IAM | Permissions — you have real experience here from Abjayon, lean on it |

**Your honest gap:** Your AWS experience (AppSync, AppFlow, IAM) is from Abjayon 2022, not recent, and not AI-workload specific. If asked "have you deployed an AI agent on EKS," be straight: "I have K8s exposure from 5G pod health monitoring at Nokia, and IAM/AppSync/AppFlow from Abjayon, but I haven't personally deployed an LLM-serving workload on EKS." Then pivot to what you DO know about why K8s suits AI workloads (autoscaling for variable LLM traffic, resource limits per pod for GPU/memory-heavy inference).

### 4.2 Docker/Kubernetes core concepts (be fluent even if not deep)
- Container vs image vs registry — basic vocabulary, will be assumed knowledge.
- K8s pod, deployment, service, ingress — the basic object hierarchy.
- Horizontal Pod Autoscaler — relevant to "stateless horizontal scaling" claim from your gRPC gateway work — connect these two topics if asked.

---

## 5. FRONTEND (lighter weight, but JD lists it)

- **React + Vite** — Vite = faster dev server/build tool vs CRA (uses native ES modules, esbuild for bundling — much faster cold start and HMR).
- **WebSockets vs polling for real-time agent monitoring** — WebSockets = persistent bidirectional connection, lower latency, better for live agent status updates; polling = simpler but wasteful/laggy. If JD wants real-time dashboards, expect "how would you architect a live agent execution monitor" — answer: WebSocket connection per dashboard session, backend pushes state changes as they occur (likely sourced from your `agent_episodes`/`agent_run_scratch` tables via a pub/sub or DB trigger → message broker → websocket push).

---

## 6. SYSTEM DESIGN — LIKELY WHITEBOARD PROMPT

Given the JD, expect something like: **"Design a multi-agent system that processes a customer support ticket end-to-end."**

Structure your answer:
1. **Ingestion** — ticket arrives via API, gets classified (intent detection — could be a lightweight LLM call or classifier).
2. **Orchestrator agent** — decides which specialist agent(s) handle it (billing agent, technical agent, refund agent).
3. **Tool layer** — each specialist agent has scoped tool access (billing agent can query payment DB, can't touch user PII tables — tie to attribute-level RBAC).
4. **Memory** — episodic log of every step (your `agent_episodes` pattern) for auditability — critical in regulated domains (healthcare/fintech per JD).
5. **HITL checkpoint** — if action is high-risk (refund > $X), pause for human approval before executing.
6. **Verifier loop** — before closing ticket, a verifier agent checks if resolution actually satisfies the original intent; if not, retry-with-feedback.
7. **Failure handling** — what happens if an agent's tool call fails? Retry with backoff, escalate to human, log to dead-letter queue.

This structure draws directly from things you've actually built — use it as your default system design template.

---

## 7. HARD QUESTIONS THEY WILL ASK YOU SPECIFICALLY (resume-driven)

1. **"Your Brane Enterprises role is 2 months — what did you actually ship in that time, not just design?"** → Be ready with concrete deliverables, not just architecture descriptions. If most of it was design/schema work without full production deployment, say that honestly.
2. **"You list LangChain but the JD wants LangGraph — what's the difference and have you used it?"** → LangChain = general LLM application framework (chains, retrievers, agents as a feature). LangGraph = graph-based orchestration layer built by the same team, specifically for stateful, multi-step, multi-agent workflows with explicit control flow (nodes/edges, cycles allowed unlike a simple DAG). If you haven't used it: say so directly, then say you understand the conceptual difference and could ramp quickly given LangChain familiarity.
3. **"Walk me through the gRPC model gateway end to end."** → This is your best material. Practice out loud, 90 seconds, no notes.
4. **"What's the difference between your 'vector DB' usage in the 5G project and what this role needs?"** → Be honest about scale/complexity gap if one exists.
5. **"70% auto-resolution, 55% MTTR reduction — how were these measured, what was the baseline, who validated the number?"** → If you can't give a precise methodology, say "approximately, based on team-tracked incident logs over [timeframe] — I'd want to verify the exact measurement methodology before citing it as a hard number in a high-stakes setting." Confident vague stats are CRITICAL RISK in interviews — better to show rigor about uncertainty than to bluff.

---

## 8. BRUTAL TRUTH

Your resume is strong on **systems/backend depth** (gRPC, schema design, async patterns, RBAC) — that's rare and will impress. But you are weak on **named-framework, hands-on multi-agent orchestration** (LangGraph/CrewAI/AutoGen) and **A2A protocol-level work**, which is literally what this JD's title leads with. If you walk in trying to perform expertise you don't have in those two areas, you will get caught within 2-3 follow-ups and it will taint everything else you say — including the parts that are genuinely excellent. Your winning strategy for Friday is not to fake gaps shut — it's to over-perform on what you've actually built (own the gRPC gateway and the agent state schema completely, cold, no hesitation) and handle the LangGraph/A2A gaps with one clean honest sentence each, then redirect to adjacent real experience. Confident honesty about a bounded gap reads as senior. A caught bluff reads as junior — permanently, for the rest of the interview.
