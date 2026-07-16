# Brane Enterprises — Interview Q&A (resume bullets)

Direct questions and answers, scoped to the five resume bullets. Source: [Brane_AI_Agent_Runtime_Deep_Dive.md](Brane_AI_Agent_Runtime_Deep_Dive.md).

---

**Q: What did you build at Brane?**
A: A production AI Agent runtime for a no-code workflow platform. The platform already ran two LO (Local Objective) types — HUMAN and DIGITAL, both deterministic. I contributed to a third type, AI_AGENT, where an LLM does the work. My slices: PostgreSQL schema design, LLM inferencing via a gRPC model gateway, agent loop development, prompt engineering, and performance optimization.

**Q: What tables did you design?**
A: Agent identity tables, multi-agent LO junction tables, attribute-level RBAC permission rows, and agent execution sibling tables — `lo_input_execution_agent`, `agent_run_scratch`, `agent_episodes`.

**Q: What's in the agent identity table?**
A: `agents` table: `agent_id` (primary key), `agent_name`, `agent_type` (HUMAN/DIGITAL/AI_AGENT), `tenant_id`, `model_class` (instruct/thinking/vision), `prompt_template_id`, a JSONB `config` column, `is_active`, `created_at`.

**Q: What is the multi-agent LO junction table, and why does it exist?**
A: `lo_agents` — a many-to-many join between LOs and agents. An LO can have a primary agent plus optional secondary and verifier agents; one agent can be reused across many LOs. Columns: `lo_id`, `agent_id`, `role` (primary/secondary/verifier), `priority`, `is_active`, with a unique constraint on `(lo_id, agent_id, role)`.

**Q: How do you guarantee exactly one primary agent per LO?**
A: A partial unique index: `UNIQUE (lo_id) WHERE role='primary' AND is_active=TRUE`. The database enforces it — two active primaries is unrepresentable.

**Q: What are attribute-level RBAC permission rows?**
A: Permissions scoped to individual data attributes, not just whole LOs. The platform's existing RBAC only answered "can this principal run this LO?" — too coarse for an agent, which might need to read one field but not another (e.g. read invoice line items but never see a salary field). I extended the existing `system_permissions` table with a new `attribute` resource_type and a new `source` permission_type alongside read/write/execute, plus an index on `(resource_type, resource_id, principal_id)`.

**Q: Why extend the existing permissions table instead of building a new one?**
A: Reuse over parallel systems. A new table would duplicate admin tooling, audit trails, and permission-check code that already existed. Adding a resource_type and permission_type kept the agent's grants visible in the same audit path as everything else.

**Q: When is the attribute filter applied?**
A: Before prompt assembly. The agent's input set is filtered through the RBAC check before it's ever placed in the prompt — so an out-of-scope attribute is never in context to begin with, not merely instructed to be ignored.

**Q: What are the three agent execution sibling tables, and why three separate ones?**
A: `lo_input_execution_agent` — one row per AI attempt (input values, raw model output, verdict, failure report, `attempt_seq`). `agent_run_scratch` — the reasoning trace and raw output for the current run only, pruned after 7 days, for debugging. `agent_episodes` — one row per completed run per (user × GO × LO): inputs, outputs, verdict, attempt count, kept 90 days, for analysis. Different lifetimes and different readers, so three tables rather than one with mixed retention.

**Q: Why are these "sibling" tables instead of changes to the existing execution tables?**
A: The platform already ran HUMAN and DIGITAL LOs in production against canonical tables. Structurally altering those risks every existing workflow. All new AI state lives in tables suffixed `_agent`, and the only touch to a canonical table is one nullable additive column (`lo_input_items.permitted_sources`, NULL = legacy behavior). The feature is fully additive and reversible — disable it and the platform behaves exactly as before.

**Q: What is the gRPC model gateway, and what does it integrate?**
A: A single gRPC service that fronts every model provider. Instead of each part of the runtime calling a provider SDK directly, it calls one gateway that routes by `model_class`.

**Q: Why gRPC instead of REST for this?**
A: It's an internal, high-frequency inference call — gRPC gives HTTP/2 with binary protobuf, lower latency and serialization overhead than JSON over HTTP/1.1, plus native streaming, which matters because the model streams tokens and tool calls back.

**Q: What is multi-provider model routing (instruct/thinking/vision)?**
A: The gateway routes each request to one of three model classes based on the task: `instruct` for straightforward generation, `thinking` for tasks needing deeper reasoning, `vision` for image inputs. Each agent's row carries a `model_class`, and the gateway dispatches accordingly — so the runtime isn't hardcoded to one model per task type.

**Q: What does "stateless horizontal scaling" mean here, concretely?**
A: The gateway holds no per-request state — no session memory. Every call carries everything the model needs: system prompt, user prompt, grounded inputs, tool specs. The actual state (attempt history, run state) lives in Postgres, not in the gateway. Because the gateway is stateless, you scale it by adding replicas behind a load balancer — no sticky sessions required.

**Q: What's the tradeoff of the gateway being stateless?**
A: Context has to be reconstructed from the database and resent on every call, instead of being cached in a session. You trade some redundant data transfer for the ability to have any replica serve any request.

**Q: Describe the prompt assembly for the agent loop.**
A: Four parts in order: system prompt (the stable role/instruction frame), grounded input injection (RBAC-filtered data from design-time NFs — fetch, calc, ai_with_rag), tool registry context (the schemas of tools this agent is granted), and retry-with-feedback construction (prior failure reports appended so the model sees why the last attempt was rejected).

**Q: What is "grounded input injection"?**
A: The design-time NF outputs (fetch/calc/ai_with_rag results) that feed the LO, filtered through attribute-level RBAC, inserted into the prompt as the factual context the agent works from — as data, not as instructions.

**Q: What is the tool registry context, and how is it scoped?**
A: The set of pre-registered platform NFs (nested functions) that this specific agent has been explicitly granted via `agent_tool_grants`, rendered into the prompt with their JSON-schema parameter contracts. The agent can only invoke functions on this whitelist — it cannot invent an action.

**Q: What happens when the agent calls a tool?**
A: The tool executor resolves the tool, checks the grant, validates the call's parameters against the tool's JSON schema, allocates an invocation sequence, writes an audit-in row, dispatches to the *existing* NF handler (not a reimplementation), and writes an audit-out row with the result or error.

**Q: What is the "retry-with-feedback construction for the verifier correction loop"?**
A: When a verifier rejects an attempt, its failure report (which rule failed, or what the AI/human verifier objected to) is stored and appended into the next iteration's prompt. The agent's next attempt is generated with explicit knowledge of why the previous one was rejected, rather than blindly re-sampling.

**Q: Walk through one full iteration of the correction loop.**
A: Assemble RBAC-filtered inputs → build the prompt (system + grounded inputs + tools + prior failure reports) → call the gRPC gateway, handling any tool calls → parse and schema-validate the response → if parsing fails, record it as a failed attempt (not a crash) → if it parses, persist the attempt and mirror the value to the canonical execution table → run the verifier stack → pass: commit the primary function and write an episode; fail: record the failure report and loop.

**Q: Why is the verifier a separate call from generation?**
A: Because a model can't reliably judge its own output — a confidently wrong answer would pass its own check. The verifier runs as an independent lane: deterministic business rules first (cheapest, short-circuits on failure), then optionally an AI verifier using a different model class, then optionally a human. The component that generates is never the component that certifies.

**Q: Why an in-place attempt counter instead of versioned LO ids like human recursion?**
A: Humans recurse by creating new versioned LO ids (LO4.1, LO4.2). An agent iterating several times in seconds can't spawn that many versioned LOs without polluting the design space and breaking downstream references. Instead, each attempt is a row with an incrementing `attempt_seq` in `lo_input_execution_agent`, and the latest accepted value is mirrored to the canonical `lo_input_execution` table that downstream code reads.

**Q: What stops the correction loop from running forever?**
A: A hard iteration cap (`max_iterations`, default 5). On exhaustion, the run state transitions to a configured fallback and an episode is written recording the outcome.

**Q: What bugs did you resolve and what did you optimize?**
A: Attribute RBAC caching, tool invocation overhead reduction, and response parser hardening for malformed LLM outputs.

**Q: What was the RBAC caching problem, and what was the fix?**
A: Checking attribute permissions naively meant a database round-trip per attribute per attempt, and the loop re-checks the same attributes every iteration — an N-queries-per-attempt pattern. I added a cache keyed on `(principal_type, principal_id, attribute_id, permission, tenant_id)`, scoped to the lifetime of a single run. First check hits the database; repeats hit the cache. It turned N queries per attempt into roughly one query per distinct attribute for the whole run.

**Q: Why scope the cache to a single run instead of a longer-lived shared cache?**
A: A shared, longer-lived cache would be faster, but it risks serving a revoked permission after it's been changed. A stale permission cache is a security bug, not just a performance one. Scoping the cache to the run means it's built fresh and discarded with the run, so a permission change can never be served stale across runs.

**Q: What was the tool invocation overhead, and what did you do about it?**
A: The tool-call path does several steps per call — resolve the tool, check the grant, validate parameters, allocate an invocation sequence, write audit-in rows, dispatch, write audit-out rows. On a tool-heavy attempt, most of the wall-clock time was going into that bookkeeping rather than the actual function. I reduced redundant lookups and round-trips — resolving tool metadata and its grant together instead of as separate queries, allocating the invocation sequence in one query instead of read-then-write.

**Q: What was the response parser hardening about?**
A: LLMs return malformed JSON a meaningful fraction of the time — wrapped in markdown code fences, trailing text after the closing brace, missing fields. Left unhandled, that's an exception that kills the run. The parser now handles the common malformation modes and schema-validates the result; if it still can't parse, that's recorded as a failed attempt with a `parse_failed` report — not a crash — so the correction loop can retry with that feedback instead of losing the run entirely.

**Q: How long were you at Brane, and what does that mean for what you can claim?**
A: Two months, on a large existing platform. The pieces above — the schema components, the gateway integration, the loop, the prompt assembly, and the two performance fixes — are the slices I built and own. The overall system design (the verifier-lane principle, the MCP-based agent router) was an existing team design I worked inside and understand, not something I authored solo.
