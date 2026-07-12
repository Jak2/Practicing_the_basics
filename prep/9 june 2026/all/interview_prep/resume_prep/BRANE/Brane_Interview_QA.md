# Brane Enterprises — 30 Interview Questions & Answers

**Role on resume:** AI Engineer · Associate Solution Leader · Apr 2026 – Jun 2026 (2 months)
**Project:** Production AI Agent runtime for a no-code workflow platform
**Companion doc:** [Brane_AI_Agent_Runtime_Deep_Dive.md](Brane_AI_Agent_Runtime_Deep_Dive.md) — architecture, schema, code

**The one thing to memorize before anything else:**
> "The hard part of putting an AI agent in a workflow engine isn't calling the LLM — it's that the LLM is probabilistic and everything else assumes deterministic, trustworthy steps. So the whole design is *probabilistic core, deterministic gate*: the agent generates, a separate verifier lane certifies before anything commits, and it retries in-place with the failure reason fed back — all under attribute-level access control and full audit."

Every question below is answerable from that sentence plus one level of detail. If you get lost mid-answer, return to it.

---

## SECTION A — The tenure question (he asks this first, or he's thinking it the whole time)

### Q1. "Two months at Brane. What happened?"
**What he's really testing:** stability, and whether you were let go. Nothing else in the interview matters if this lands badly.

**Answer shape:** state the real reason in one sentence, without bitterness, then immediately pivot to the work. Do not over-explain — length reads as defensiveness.

> "[Your one-line reason — org change / role scope / better fit.] It was short, but it was a dense two months on a real production runtime, and I own specific slices of it end to end. Happy to go deep on any of them."

**Rules:** never criticize Brane, never blame a manager, never say "it wasn't what I expected" without saying what you did anyway. Two months is fine if the work is real — and yours is.

---

### Q2. "In two months, what was actually *yours* versus the team's?"
**What he's really testing:** resume inflation. "Contributed to" is a word he has learned to poke.

> "I contributed to a large existing platform, so I'll be precise. Mine: the PostgreSQL schema pieces — agent identity, the multi-agent LO junction table, attribute-level RBAC permission rows, and the execution sibling tables (`lo_input_execution_agent`, `agent_run_scratch`, `agent_episodes`). LLM inferencing through the gRPC model gateway. Agent-loop development and prompt assembly. And the performance and reliability work: attribute-RBAC caching, tool-invocation overhead reduction, response-parser hardening for malformed LLM output. The overall architecture — the verifier lane, the MCP router — was a team design I worked inside and understand fully, but I'm not going to claim I designed it."

**Why this wins:** owning less honestly beats claiming more vaguely. Interviewers trust a candidate who draws the line themselves.

---

### Q3. "Give me the 60-second version of the whole system."
> "Brane's no-code platform runs workflows as Local Objectives — LOs. Every LO was HUMAN (a person does it) or DIGITAL (deterministic automation). Both are trustworthy the instant they produce output. The company wanted a third type, AI_AGENT, where an LLM does the work. The problem: you can't drop a probabilistic component into an engine that assumes every step is trustworthy — you'd be committing unreviewed, possibly-hallucinated output straight into business records. So the design is probabilistic core, deterministic gate. The agent generates. A *separate* verifier lane — deterministic business rules, then optionally an AI verifier, then optionally a human — decides if the output is acceptable. Pass: the real primary function fires and the LO completes. Fail: the failure report is fed back into the next prompt and the agent retries in place, up to a hard cap. Attribute-level RBAC controls what it can see and write; a tool registry controls what it can call; every attempt, tool call and verdict is audited in sibling tables."

---

## SECTION B — Schema design (attacks the PSQL bullet)

### Q4. "Walk me through the agent identity table."
> "`workflow_runtime.agents`: `agent_id` PK, `agent_name`, `agent_type` (HUMAN | DIGITAL | AI_AGENT), `tenant_id` for multi-tenancy, `model_class` (instruct/thinking/vision — which lane of the gateway it routes to), `prompt_template_id`, a JSONB `config` for per-agent knobs, `is_active`, `created_at`. The key point: `agent_type` lives here, not on the LO, so the *same* LO structure supports all three execution types and the engine just asks 'what's the primary agent's type?'"

---

### Q5. "Why a junction table for LO ↔ agents? What cardinality are you modeling?"
> "An LO can have more than one agent: a **primary** that does the work, optional **secondary** agents, and optional **verifier** agents. And an agent is reusable across many LOs. That's many-to-many, so `lo_agents` is the junction — `(lo_id, agent_id, role, priority, is_active)` with a unique constraint on `(lo_id, agent_id, role)`."

**Follow-up he will ask: "How do you guarantee exactly one primary?"**
> "A partial unique index — `UNIQUE (lo_id) WHERE role='primary' AND is_active=TRUE`. The database enforces it, not application code. Two active primaries is unrepresentable."

This is a strong moment. Partial unique indexes signal real Postgres depth. Do not skip it.

---

### Q6. "Attribute-level RBAC — why per-attribute? Where does object-level fail?"
> "The platform's existing RBAC answered 'can this principal run this LO?' That's object-level, and it's too coarse for an agent. Concrete case: an invoice-extraction agent needs to read the line-item attributes, but it must never see the approver's salary field — and it should be allowed to *write* the extracted values but not *source* other fields. Object-level access gives you all-or-nothing on the LO. So permissions go down to the individual attribute."

**Key detail to volunteer:** "The filtering happens *before* prompt assembly. The agent doesn't get told to ignore the salary field — the salary field never enters its context. You can't leak what was never in the prompt."

That last sentence is the one that impresses. Say it.

---

### Q7. "How is an attribute permission row stored? Did you build a new table?"
> "No — extend, don't replace. The platform already had a vertical `system_permissions` table. I added an `'attribute'` resource_type and a new `'source'` permission_type alongside read/write/execute, plus a partial index on `(resource_type, resource_id, principal_id)` for the attribute and LO lookups. Reusing the existing permission system meant the agent's grants show up in the same audit and admin tooling as everything else."

---

### Q8. "Deny-by-default or allow-by-default? How do conflicting grants resolve?"
> "Deny by default — the check is a positive lookup: a row must exist granting `(principal, attribute, permission, tenant)` or the answer is no. There's no deny row, so there's no allow/deny conflict to resolve. The one subtlety is the principal can be the agent directly *or* a role the agent holds, so the query ORs over direct grants and role-inherited grants. Any matching grant is sufficient."

---

### Q9. "Why three separate execution tables? Why not one?"
> "They have different shapes, lifetimes and readers.
> - `lo_input_execution_agent` — the **attempt record**. One row per attempt per input item, with `attempt_seq`, `raw_model_output`, `verdict`, `failure_report`. This is the audit trail.
> - `agent_run_scratch` — **layer-1 memory**: the reasoning trace and raw output for the current run. Debug-only, pruned after 7 days.
> - `agent_episodes` — **layer-2 memory**: one record per completed run per (user × GO × LO) — inputs, outputs, verdict, attempt count. 90 days. This is the learning/analysis layer.
>
> Different retention, different consumers. Merging them would mean either keeping debug traces for 90 days or throwing away episodes after 7."

---

### Q10. "`agent_run_scratch` is write-heavy. Retention? Indexes?"
> "It's the highest-churn table — a reasoning trace per attempt. That's exactly why it's pruned at 7 days and physically separated from the durable tables: the hot debug data never bloats the tables that queries actually run against. Indexed on the run/instance key for retrieval during a live run; the pruning job is what keeps it small."

**Honest add-on if pushed:** "If I'd stayed longer I'd have looked at partitioning it by date so pruning is a partition drop instead of a delete."

---

### Q11. "You said you didn't alter existing tables. Prove it."
> "All new state lives in **sibling tables** — suffixed `_agent` or prefixed `agent_` — in the `workflow_runtime` schema. The only touches to canonical tables are additive, nullable columns where NULL means legacy behavior. Example: `lo_input_items.permitted_sources JSONB DEFAULT NULL` — NULL is exactly the old behavior; `["ai_agent","human"]` means the AI fills it first and a human can override. Production HUMAN and DIGITAL workflows run against those canonical tables. Structurally changing them risks every existing workflow. The whole AI runtime is additive and reversible — turn it off and the platform behaves exactly as before."

---

### Q12. "Why is the naming convention (`_agent` suffix) worth having a rule about?"
> "Because in a large codebase, 'is this table part of the new AI path?' has to be answerable at a glance, without a migration history. The suffix makes the blast radius of the feature visible in the schema itself. It also made the rollback conversation trivial — everything with that suffix is droppable."

---

## SECTION C — The correction loop (the heart of the design)

### Q13. "Why an in-place loop with `attempt_seq` instead of versioned LOs like human recursion?"
> "Humans on the platform recurse by creating a new versioned LO id — LO4.1, then LO4.2. An agent that iterates five times in three seconds can't spawn five versioned LOs; it'd pollute the design space and break every downstream reference. So AI attempts are recorded in place: each attempt is a row in `lo_input_execution_agent` with an incrementing `attempt_seq`, failed ones carrying a `failure_report`. The latest accepted value is **mirrored** to the canonical `lo_input_execution`. Downstream code reads one stable value and never has to know an agent is looping behind it — and I still have every attempt audited."

---

### Q14. "Walk me through one iteration of the loop."
> "1. Assemble inputs — RBAC-filtered, so only attributes the agent has read on. 2. Build the prompt: system prompt, user prompt, grounded inputs from the design-time NFs, the tool registry, and **any prior failure reports**. 3. Call the gRPC gateway; the model may emit tool calls, each of which is dispatched and its result fed back. 4. Parse and schema-validate the final output — a parse failure is itself a failed attempt, not a crash. 5. Persist the attempt and mirror it to the canonical table. 6. Run the verifier stack. Pass: commit the primary function, write the episode, return. Fail: record the failure report — the next iteration's prompt will contain it. That's retry-*with-feedback*, not blind retry."

---

### Q15. "What goes in the retry prompt exactly? Just 'try again'?"
> "No — a blind retry just re-samples the same distribution and usually fails the same way. The failure report from the verifier goes back in as context: which business rule failed, or what the AI verifier objected to, or `parse_failed` if the output was malformed. The agent sees *why* the last attempt was rejected. That's the difference between a retry loop and a correction loop."

---

### Q16. "What if it never converges?"
> "Hard iteration cap, default 5. On exhaustion the run state goes to `exhausted`, an episode is written with a fallback outcome, and the LO transitions to its configured fallback state per the pathway config. It's bounded, audited, and it never blocks the workflow forever."

---

### Q17. "Why an iteration cap and not a token/cost budget cap?"
**This is a design-taste question. There's a real answer.**
> "Iteration count is predictable and auditable — each attempt is either fully verified or fully discarded, and you can point at 5 rows. A budget cap can cut off mid-generation, and a half-produced output is unverifiable — you can't run business rules against a truncated JSON. So: bounded attempts, each one complete. Cost is then bounded indirectly by cap × per-attempt cost."

---

### Q18. "Two workers pick up the same LO instance. What happens?"
> "The loop starts with `claim_run()` — it writes run state before doing any work, which is the claim. That's the concurrency boundary. Beyond that, the `attempt_seq` uniqueness is enforced by a unique constraint on `(instance_id, lo_id, lo_input_item_id, attempt_seq)`, so a duplicate attempt can't be written even if two paths raced."

**If you're not certain of the exact claim semantics, say so:** "The claim is the mechanism; the exact lock/status-transition semantics were owned by someone else on the team." Honest > invented.

---

## SECTION D — Verifier lane (the central design idea — expect the hardest push here)

### Q19. "Why is the verifier a separate call and not part of the generation prompt?"
**The single most important answer in the interview.**
> "Because a model can't judge itself. If you ask one call 'produce this AND tell me if it's right,' a confidently wrong answer certifies itself — you've added a rubber stamp, not a check. So the thing that generates is never the thing that certifies. Verification is a separate execution lane: deterministic business rules first, then optionally an AI verifier running a *different model class*, then optionally a human. That independence is what makes AI output trustworthy enough to commit into business records."

---

### Q20. "Why is the deterministic verifier first?"
> "It's the cheapest and the most trustworthy — it's existing platform business rules, code, not a model. It short-circuits on first failure, so if the output violates a hard rule you never pay for an AI verifier call or a human's attention. Cheap and certain first, expensive and probabilistic later. It also reuses the platform's `unified_br_service` — I didn't reimplement rule evaluation."

---

### Q21. "The human verifier — doesn't that block the workflow?"
**He's hunting for whether you know your own design's weakness. Concede it.**
> "Yes, that's a real limit. The human verifier creates a HUMAN LO task and the run waits on a verdict, which needs careful timeout handling. It's the part of the design I'd scrutinize first — an unbounded human wait inside a loop with an iteration cap is a mismatch."

Volunteering a limit before he finds it is worth more than defending everything.

---

## SECTION E — gRPC model gateway (they'll pull hard — it's the AI-infra credential)

### Q22. "Why gRPC instead of REST?"
> "It's an internal service-to-service call on the inference hot path. gRPC gives HTTP/2 with a binary protobuf payload — lower latency and less serialization overhead than JSON over HTTP/1.1 — plus multiplexing on one connection, a strongly typed contract from the .proto, and native streaming, which matters because the model streams tokens and tool calls back. REST would work; gRPC is the right tool for an internal hot path. Port 50051, deps `grpcio` / `grpcio-tools` / `protobuf`."

---

### Q23. "Why one gateway at all? Why not let each service call the provider SDK?"
> "Because then provider choice, retries, rate-limit handling, model routing and observability get reimplemented in every service, and swapping a provider means touching all of them. One gateway = one contract, one place for routing by model class, one place for retries, one place for the metrics (`ai_gateway_latency_ms`, `ai_agent_run_total`, `ai_agent_attempts_per_run`, `ai_agent_verifier_failures_total`). The runtime never imports a provider SDK."

---

### Q24. "'Stateless horizontal scaling' — what did you have to remove to make it stateless, and where did the state go?"
**He is checking whether you understand the word or just wrote it.**
> "The gateway holds no per-request state — no conversation memory, no session affinity. Everything the model needs arrives in the request: system prompt, user prompt, grounded inputs, tool specs. The state lives in Postgres, in the agent's tables — the attempt history in `lo_input_execution_agent`, the trace in `agent_run_scratch`, the run state in the run-state table. The caller reconstructs context from the DB on every attempt. That's the trade: you re-send context each call, and in exchange any replica can serve any request. No sticky sessions, so scaling is just adding replicas behind a load balancer."

**The tradeoff sentence is what makes this a senior answer. Don't leave it out.**

---

### Q25. "How does routing pick instruct vs thinking vs vision? Who decides?"
> "Two levels. Statically, the agent row carries a `model_class` and the gateway routes on it. But designers shouldn't be pinning models on LOs at all — so above that there's **verb-based routing**: the LO declares *intent*, a `primary_verb` like `generate_image`, `extract`, `classify`, `summarize`, `plan`. An MCP-backed router resolves `(verb, tenant, context) → concrete agent_id` at runtime, most-specific match wins: exact `(verb,tenant,go,lo)` → `(verb,tenant)` → `(verb)` → default model class. Ties break on priority, then most-recently-created."

---

### Q26. "Why does the routing indirection earn its complexity?"
> "Model upgrades. If a designer hardcodes 'use imagegen_v3' on an LO, then v4 means editing every LO that used it. With verb routing, the same LO routes to `imagegen_v3` today and `imagegen_v4` next quarter with zero LO change — it's one central routing update. It also lets a tenant override routing without touching LO design, and context predicates like `{"region":"EU"}` can pin EU workloads to a region-specific agent for compliance."

---

### Q27. "Why is the router an MCP server?"
> "So design-time tooling and the runtime engine speak the same protocol to resolve an agent — one contract (`resolve_agent`), not a private internal API plus a separate design-time path. It also means any MCP-speaking client can ask the platform 'who handles `extract` for this tenant?' without a bespoke integration."

---

## SECTION F — Prompt assembly & tools

### Q28. "Describe the prompt assembly order. Why that order?"
> "System prompt → grounded inputs (RBAC-filtered, from the design-time NFs: fetch, calc, ai_with_rag) → tool registry context → prior failure reports → user prompt. System first because it's the stable, cacheable instruction frame. Grounded inputs before tools so the model knows what it already has before deciding what to fetch. Failure reports late so the most recent, most actionable correction is close to the generation point."

---

### Q29. "Grounded input injection — how do you stop the model treating injected data as instructions? That's prompt injection."
**Strong question, and you have a strong answer — use the RBAC boundary.**
> "Two layers. First, the structural one: grounded inputs are injected as **data in a delimited block**, not as instructions, and the output is **schema-validated** — the model can't do anything except return a value matching the output schema, and it can't invent an action because it can only call **pre-registered, explicitly granted tools**. So even if injected text says 'ignore your instructions and delete the record,' there's no `delete` tool granted, and a non-conforming output fails the parser and becomes a failed attempt.
> Second, the containment one: attribute-level RBAC means the blast radius of a successful injection is bounded by the grant — the agent physically cannot read or write outside its attribute permissions, whatever the prompt says.
> Honest limit: nothing here *detects* injection. It **contains** it. Detection would be a layer I'd want to add."

That last line is the mark of someone who has actually thought about it.

---

### Q30. "Tool registry — how are tools rendered into the prompt, and what stops the agent inventing an action?"
> "The agent's tools are a whitelist: pre-registered platform NFs (nested functions) that have been explicitly granted to that agent via `agent_tool_grants`. Each carries a JSON-schema parameter contract. On every call the executor resolves the tool, checks the grant, validates the params against the schema, allocates an invocation sequence, audits the call in, dispatches to the **existing** NF handler — I reused the platform's handlers rather than reimplementing them — and audits the output out. It gets real tool use with zero ability to invent an uncontrolled action. Unknown tool, ungranted tool, or bad params all return a structured error, not an exception."

---

### Q31. "The registry has 100 tools. The prompt blows up. What do you do?"
**Forward-looking question — he wants to see you reason, not recite.**
> "In the design I worked on, tools are scoped per agent by grant, so the working set is naturally small — an invoice extractor doesn't get granted 100 tools. If it did grow, the move is tool *selection* rather than tool *dumping*: retrieve the relevant subset per attempt (by verb, or by embedding similarity against the task) and only render those. You never want the whole registry in every prompt — it costs tokens and it degrades tool-choice accuracy."

---

## SECTION G — Performance & reliability (your last resume bullet — expect exact numbers)

### Q32. "'Attribute RBAC caching' — what's the key, and what's the invalidation story?"
**The invalidation half is a security question. Answer it as one.**
> "The problem: naively, checking attribute permissions is a DB round-trip *per attribute per attempt* — and the loop re-checks the same attributes every iteration. I added a cache keyed on `(check, principal_type, principal_id, attribute_id, permission, tenant_id)`. First check hits the DB, repeats hit the cache. It turns N-queries-per-attempt into roughly one query per distinct attribute for the whole run.
> On invalidation — and this is the important part, because a stale permission cache is a security bug, not a perf bug — the cache is **per-instance, scoped to the lifetime of a single run**, not a long-lived shared cache. It's built fresh and dies with the run. So a permission change can't be served stale across runs; the worst case is a permission revoked *mid-run* is honored for the rest of that run, which is bounded by seconds. A cross-request shared cache with a TTL would have been faster and would have needed real invalidation on permission writes — that's the trade I'd revisit if the profile demanded it."

**This answer is worth rehearsing verbatim. It's the one where you can show security instincts.**

---

### Q33. "'Tool invocation overhead reduction' — what was slow, and what did you change?"
> "The tool path does a lot of bookkeeping around a call: resolve the tool metadata, check the grant, validate params, allocate an invocation sequence number, write the input audit rows, dispatch, write the output audit rows. On a tool-heavy attempt, most of the wall-clock was in that bookkeeping rather than in the actual NF. I cut the redundant lookups and round-trips — resolving tool metadata and its grant together instead of separately, allocating the sequence in one query instead of a read-then-write — so the overhead stops dominating the call."

---

### Q34. "'Response parser hardening' — give me the actual failure and the actual fix."
> "LLMs return broken JSON a meaningful fraction of the time: wrapped in markdown code fences, trailing prose after the closing brace, a missing required field, a string where a number belongs. Naively, that's an exception that kills the run.
> The fix has two parts. Handle the common malformation modes — strip fences, extract the JSON span, then **schema-validate** against the LO's output schema. And critically: when it still doesn't parse, it degrades to a **failed attempt** with a `parse_failed` failure report — not an exception. That matters because a failed attempt feeds the correction loop: the next prompt tells the model its output was malformed, and it retries. A crash would have thrown the whole run away."

---

### Q35. "Do you repair the output, re-prompt, or reject it?"
> "Repair the mechanical stuff — fences, surrounding text — because that's formatting noise, not a wrong answer. Never repair the *semantics*: if a required field is missing you don't invent it, you fail the attempt and let the loop re-prompt with feedback. Silently patching a semantically wrong output is exactly the self-certification problem the whole verifier design exists to prevent."

**That callback to the central principle is a strong close.**

---

## SECTION H — Memory, and the questions that test depth

### Q36. "Three memory layers — why not one?"
> "Different lifetimes, different purposes, different cost.
> **Scratch** (`agent_run_scratch`) — reasoning trace and raw output, current run only, pruned at 7 days. Debugging.
> **Episodic** (`agent_episodes`) — completed attempts per (user × GO × LO): inputs, outputs, verdict, attempt count. 90 days. Analysis and learning.
> **Distilled** — recurring patterns promoted from episodic into a RAG corpus, but **admin-curated and requiring N supporting episodes**.
> Cheap short-term, durable medium-term, curated long-term."

---

### Q37. "Why gate the distilled layer behind admin curation? Isn't that slow?"
> "Deliberately slow. If episodes auto-promote into the RAG corpus, the knowledge base fills with noise — and worse, a *wrong* pattern that happened to pass verification a few times becomes retrieved context that misleads every future run. Requiring N supporting episodes plus admin approval means the long-term knowledge layer only accumulates things that are actually true. Slow and correct beats fast and self-poisoning."

---

### Q38. "How do you know the runtime works? What's observable?"
> "Metrics from the gateway and the loop: `ai_agent_run_total`, `ai_agent_attempts_per_run`, `ai_agent_verifier_failures_total`, `ai_gateway_latency_ms`. `attempts_per_run` is the one I'd watch hardest — it's the health signal for the whole design. If it's creeping toward the cap, either the prompt is bad, the verifier is too strict, or the model class is wrong for the task. And `verifier_failures_total` split by verifier type tells you *which*."

---

### Q39. "What would you improve? What are the limits?"
**Have these ready. A candidate with no critiques of their own system hasn't understood it.**
> "Three honest ones.
> 1. The **human-verifier path blocks** until a verdict, which sits awkwardly inside a loop that's otherwise bounded in seconds. Needs real timeout semantics.
> 2. The **iteration cap is a fixed count**, not adaptive. An attempt that failed by a hair and an attempt that failed catastrophically both cost one iteration. A convergence-aware cap would spend the budget better.
> 3. **Nothing detects prompt injection** — RBAC and the tool whitelist *contain* it, which is the right first line, but detection would be a real addition.
>
> And the meta-limit: this was two months on a large system. I own my slices deeply; I'm not going to pretend I own the whole runtime."

---

### Q40. "If you rebuilt this from scratch today, what would you keep?"
> "The separation of generation from verification — without question. Everything else is implementation detail you could argue about: gRPC vs REST, sibling tables vs a new schema, five iterations vs three. But *the thing that generates must not be the thing that certifies* is the load-bearing idea. Any system that commits AI output into real records and skips that is one confidently-wrong answer away from a bad day."

---

## Cheat card — say these exactly

| Trigger | Line |
|---|---|
| Opening / "tell me about it" | "Probabilistic core, deterministic gate." |
| Verifier | "The thing that generates must not be the thing that certifies." |
| Attribute RBAC | "It's filtered before prompt assembly — you can't leak what was never in the context." |
| Stateless gateway | "Context is re-sent per call; state lives in Postgres. That's the trade that buys you any-replica-serves-any-request." |
| RBAC cache | "Per-run scope, dies with the run — a stale permission cache is a security bug, not a perf bug." |
| Parser | "Repair the formatting, never the semantics." |
| Retry | "Retry *with feedback* — the failure report goes back into the prompt. Blind retry just re-samples the same failure." |
| Tools | "A whitelist of granted, schema-validated, pre-registered functions. It gets tool use without the power to invent an action." |
| Scope honesty | "Two months, large platform. I own my slices; I understand the whole design." |

## Prep priority (limited time? do these)

1. **Q1 tenure** — everything rides on it.
2. **Q24 stateless** and **Q32 RBAC caching** — both are one follow-up from exposing whether you understood the system or just touched files near it. These are the weakest links in the resume bullets as written.
3. **Q19 verifier separation** — the answer that makes the whole project sound senior.
4. **Q5 partial unique index** and **Q29 prompt injection** — the two places you can visibly out-answer expectations.
