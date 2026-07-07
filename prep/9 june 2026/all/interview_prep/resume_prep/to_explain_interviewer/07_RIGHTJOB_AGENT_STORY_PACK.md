# Agent Story Pack — right_job.in "Senior AI Agent Developer" (Sat 11:30 AM)

> This is the ONLY new file for this interview. Everything else in your pack still applies —
> this file re-frames your existing stories for an AGENT role and gives you the
> user-facing error stories you were missing. Read this first, ONE_PAGE last.

---

## 1. The frame shift (memorize this — it replaces the IBridge anchor)

The IBridge pack told you to prove you're a *backend engineer who uses AI*.
**This JD wants the opposite emphasis.** They're hiring someone to architect autonomous
agents (UWM, multi-agent, A2A, RAG, HITL). Your new anchor sentence:

> *"I build production AI agent systems — RAG pipelines, LLM orchestration, evaluation
> gates, human-in-the-loop escalation — on a solid Python/FastAPI/PostgreSQL/AWS backend.
> The backend discipline is what makes my agents reliable enough for enterprise use."*

Same facts, reversed order. Lead with agents, close with backend as the credibility layer.

### Your full 60-second opener (they WILL ask "tell me about yourself" first — script it)

> "I'm a Python engineer who builds production AI agent systems. My most recent work is a
> pipeline that autonomously diagnoses 5G network failures — it perceives errors from
> packet captures, retrieves known patterns from a Qdrant vector database, reasons with
> Claude to synthesize a fix, and escalates to a human when confidence is low. It
> auto-resolves 70% of routine incidents. Around that I've built the supporting systems
> agents need in production: an LLM evaluation framework that catches model regressions
> in minutes instead of days, and a bias auditor that generates regulatory compliance
> documentation automatically. Under all of it is five years of backend engineering —
> FastAPI, PostgreSQL, Celery, Redis — which is what makes the agents reliable enough
> for enterprise use. That combination — agent architecture on production-grade backend —
> is exactly how this role reads, which is why I'm excited about it."

Practice until it's 55–65 seconds spoken, not read.

---

## 2. Speak their vocabulary (JD term → your proof)

| JD term | What you say (all true, from your projects) |
|---|---|
| Autonomous agents, multi-step planning | 5G pipeline: perceive (Pyshark) → retrieve (Qdrant) → reason (Claude) → act (fix suggestion) → escalate. That IS an agent loop. |
| Human-in-the-loop (HITL) | Below 0.65 confidence → "manual review required" + logged to `unknown_errors` for humans to curate. RF Generator: engineer reviews every generated keyword before commit. |
| RAG pipelines & vector DBs | Qdrant with DB-level `must` pre-filtering (vendor+layer), 0.65 threshold, LangChain RetrievalQA with source documents. |
| Agent evaluation / reliability | LLM Eval Framework: 4 independent evaluators, AND-logic gate, caught a 14-pt faithfulness drop in 4 min. This is how you'd QA any UWM agent. |
| Orchestration / lifecycle | Celery + Redis durable task queues; Redis hot state + SQLite cold history in NFTRACE = agent state/memory management. |
| Model routing / cost | Haiku for high-confidence, Sonnet for ambiguous — 60% API cost cut. |
| A2A / multi-agent | Honest framing: "My eval framework runs four independent evaluator agents whose verdicts are combined — a coordinator pattern. I haven't shipped peer-to-peer A2A protocols yet, but the coordination problems are the ones I already solve: shared state, failure isolation, verdict aggregation." |
| MCP | Know the concept: open standard for exposing tools/data to LLMs via typed servers. Say you've used Claude/MCP tooling day-to-day; frame it as "tool-use standardization — the natural next step from my LangChain tool integrations." |
| UWM | It's THEIR framework — nobody outside knows it. Ask about it in the interview ("How does UWM handle agent state and HITL checkpoints?"). Asking a sharp question here scores more than pretending. |
| HIPAA / healthcare | Bias Auditor = EU AI Act Article 13 compliance work → "I've built for regulated-AI documentation requirements; HIPAA is the same discipline: audit trails, data minimization, access control." |

---

## 3. The three hero stories (user-facing error scenario format)

Structure for each: **User story → the failure the user hits → what the agent does →
the design decision → the number.** Tell them in 90 seconds each. Practice out loud.

### Story A — The 3 AM incident (5G Failure Detection Pipeline) — YOUR LEAD STORY

> "As a network operations engineer, when a 5G node starts rejecting registrations at
> 3 AM, I need a diagnosis and fix in minutes, not hours of scrolling Wireshark.
>
> Before my system: an engineer opens a pcap with thousands of packets, and matches what
> they see against years of personal experience. Same error, rediscovered every time.
>
> I built an agent that does that loop autonomously: Pyshark extracts the signaling
> errors, Qdrant retrieves the top known patterns — pre-filtered by vendor and layer at
> the DB level so a Nokia error never pulls an Ericsson fix, which would have the wrong
> CLI syntax and could make the outage worse — and Claude synthesizes a contextual fix:
> not 'check T3560 timer' but 'this happened during a traffic spike, raise T3560 from 1s
> to 3s in the AMF config and monitor.'
>
> **The error scenario I'm proudest of handling:** what happens when the agent doesn't
> know. Below a 0.65 similarity score, a confident-sounding answer would be hallucinated
> advice — worse than no answer, because an engineer might apply it to a live network.
> So the agent says 'unknown pattern — manual review required,' escalates to a human,
> and logs the error to an unknown_errors collection that ops engineers curate into new
> patterns. The agent's failures literally become its training data.
>
> Result: 70% of routine errors auto-resolved with no human escalation, 55% MTTR
> reduction, cited in 3 internal audits."

Why this is your lead: it hits autonomy + RAG + HITL + escalation + self-improvement — five JD bullets in one story.

### Story B — The silent model update (LLM Eval Framework)

> "As a product owner of an LLM-powered app, when Anthropic or OpenAI ships a new model
> version, my users start getting subtly worse answers and nobody notices for days —
> slightly shorter responses, shifted edge-case handling. Users just feel the product
> got dumber, and support tickets are the first signal.
>
> I built an automated quality gate: every prompt/response pair runs through four
> independent evaluators — LLM-as-judge, hallucination detector, RAG faithfulness,
> consistency — results in PostgreSQL, Slack alert on failure, live dashboard.
>
> **Key design decision:** AND logic, not a weighted average. A response that's 95%
> faithful but hallucinates one claim still fails, because an average would mask exactly
> the failure that hurts a user. And the two RAG scores diagnose *where* the failure is:
> high faithfulness + wrong answer means the retriever fed bad documents; low
> faithfulness means the model ignored the retriever. Different failure, different fix.
>
> In a simulated provider update, it flagged a 14-point faithfulness drop in under
> 4 minutes — versus 2–3 days of manual human review."

This is your "how do you make agents trustworthy" answer — they WILL ask it.

### Story C — The wrong-but-confident generator (RF Keyword Generator, HITL)

> "As a test engineer, I describe a test in plain English and get a Robot Framework
> keyword in seconds instead of hours. But an LLM will happily generate syntactically
> beautiful, semantically wrong test code — and a wrong test that passes is worse than
> no test.
>
> So I split the job: the LLM only does what it's good at — understanding the
> engineer's intent and extracting entities — and deterministic templates generate the
> actual structure. And a human reviews every keyword before it enters the suite:
> human-in-the-loop by design, not as an afterthought. 50+ generations a week, and the
> fallback chain (LLM → regex → defaults) means it never crashes and always returns
> something reviewable."

Use this for "when should an agent NOT be autonomous?" — a senior-signal question.

### Story D — The regulated-domain story (Bias & Fairness Auditor) — USE WHEN HEALTHCARE/HIPAA COMES UP

> "As a compliance officer, when the EU AI Act requires me to prove my AI system isn't
> biased, I can't hand regulators a shrug — I need documented, reproducible evidence.
>
> I built an auditor that runs four blind pipelines over an LLM's responses. The design
> decision that matters: the LLM-as-judge never sees the demographics — they're stripped
> before judging, because otherwise you'd import the judge's own bias into the audit.
> Two-layer scoring, VADER then DistilBERT, and the output is EU AI Act Article 13
> compliant documentation, generated automatically.
>
> That's the same discipline healthcare and insurance domains need: audit trails,
> blind evaluation, data minimization. HIPAA changes *what* data is sensitive, not
> *how* you engineer for it."

This directly answers their "healthcare, insurance, fintech" preferred qualification.

### Story E — Agent memory in one minute (NFTRACE) — USE FOR "memory/context/lifecycle" QUESTIONS

> "Agent memory is a data-access-pattern problem. In NFTRACE I split state by
> temperature: Redis for hot, active-session state with TTL-based lifecycle — the
> agent's working memory — and SQLite for completed, cold history — its long-term
> memory. Add the Qdrant unknown_errors collection from my 5G pipeline and you have the
> third kind: semantic memory that grows from the agent's own failures. Working memory,
> episodic history, semantic knowledge — right store per access pattern."

---

## 4. Answers to the questions this JD will generate

**"Have you built multi-agent systems?"**
Honest + strong: "I've built coordinator-pattern systems — four evaluator agents with
independent verdicts aggregated by AND logic, and a pipeline agent that escalates to
humans. I haven't shipped peer-to-peer A2A protocols in production, but the hard parts —
shared state, failure isolation, who's allowed to decide what — are the problems I solve
daily. I'd love to hear how UWM structures A2A."

**"What's the hardest part of putting agents in production?"**
"Knowing when the agent should refuse to act. Every system I've shipped has an explicit
'I don't know' path — the 0.65 threshold, the AND-gate, the human review step. An agent
without a refusal path is a liability, not automation."

**"LangChain/LangGraph?"** — LangChain RetrievalQA in production (5G pipeline). LangGraph:
"I know it as LangChain's stateful graph orchestration — nodes as steps, edges as
control flow, checkpointing for HITL. My Celery pipelines follow the same DAG thinking."

**"AWS?"** — Lean on your pack's existing AWS answers (EXPERIENCE_PROOF); map your stack:
FastAPI → ECS/Lambda behind API Gateway, PostgreSQL → RDS, Redis → ElastiCache,
monitoring → CloudWatch. Say it as deployment mapping, don't over-claim.

**Questions YOU ask (pick 2):**
1. "How does UWM handle agent state and HITL checkpoints — is escalation built into the framework or per-application?"
2. "How do you evaluate agent quality before release — golden suites, canary testing?" (then connect to your eval framework)
3. "For the healthcare/insurance domains — how does HIPAA shape what the agents are allowed to touch?"

---

## 4b. Rapid-fire definitions (30-second answers — screeners love these)

- **Agent vs workflow:** A workflow is a fixed sequence you designed; an agent decides
  its next step at runtime based on state. "My 5G pipeline is agentic at the decision
  points — match confidence chooses between auto-fix, deep reasoning, or human
  escalation — and a workflow everywhere determinism is safer."
- **ReAct pattern:** Reason → Act → Observe loop; the LLM alternates between thinking
  and tool calls, feeding each observation back in. LangChain agents and most tool-use
  loops are ReAct under the hood.
- **Function/tool calling:** The LLM returns a structured call (name + JSON args) instead
  of prose; your code executes it and returns the result. Foundation of every agent
  framework; MCP standardizes how tools are exposed.
- **pgvector:** Vector similarity inside PostgreSQL — embeddings live next to relational
  data. "I chose Qdrant for DB-level metadata pre-filtering at scale, but for a team
  already on RDS PostgreSQL, pgvector removes an entire infrastructure component —
  I'd genuinely consider it here since the JD pairs Postgres with RAG."
- **Context window management:** Prioritize what enters the prompt: system persona +
  top-k retrieved chunks + recent turns; summarize or evict old history; put stable
  content first for prompt caching. "My RetrievalQA prompts do exactly this — top-5
  patterns above threshold, never the whole corpus."
- **WebSockets vs polling (their frontend bullet):** Agents have long-running tasks —
  return a job ID immediately (my Celery pattern), then push progress over a WebSocket
  or SSE instead of making the UI poll. Same architecture as my job-ID + poll design,
  upgraded to push.
- **Guardrails:** Input validation before the LLM, output schema validation after
  (Pydantic), confidence thresholds, and a refusal path. "Every system I ship has all
  four — the 0.65 threshold and AND-gate are guardrails by another name."

---

## 5. Two-day plan

**Thu/Fri (today + tomorrow):**
- Read this file out loud twice. Tell each hero story out loud, timed under 90s, until smooth.
- Skim JD_MASTER_GUIDE + EXPERIENCE_PROOF for the backend/AWS/Postgres questions — they still apply verbatim.
- 20 min: read one MCP overview + one LangGraph overview so §4 answers feel owned.

**Fri night / Sat morning:**
- MASTER_CHEATSHEET (numbers table) + this file's §2 mapping table + ONE_PAGE.
- Say the anchor sentence (§1) out loud 5 times. Open with it when they say "tell me about yourself."
- Sleep early. 11:30 AM — eat before, join 10 min early.

**In the room:** every technical answer ends with a user or a number. "Because otherwise
the engineer at 3 AM gets hallucinated advice" beats any architecture diagram.

---

## 6. Self-mock checklist (Friday evening — pass this before you sleep)

Say each of these out loud, cold, no notes. Check off only if smooth:

- [ ] 60-second opener (§1) — timed 55–65s
- [ ] Story A (3 AM incident) under 90s, ending on 70% / 55%
- [ ] Story B (silent model update) under 90s, ending on 14 points / 4 minutes
- [ ] One-liner: what happens when your agent doesn't know? (0.65 → refuse → escalate → learn)
- [ ] Agent vs workflow, in your own words (§4b)
- [ ] The honest multi-agent answer (§4) — no bluffing, ends with UWM question
- [ ] Your two questions for them, from memory
- [ ] Anchor sentence, 5 reps

Anything unchecked → reread that section once, retry. Two failures on the same item →
that's your Saturday-morning review item, nothing else.
