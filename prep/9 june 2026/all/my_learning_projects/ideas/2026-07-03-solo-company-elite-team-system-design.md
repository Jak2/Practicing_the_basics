# Solo Company — Elite Team System (Design Spec)

**Date:** 2026-07-03
**Owner:** Jaya Arun Kumar Tulluri
**Status:** Implemented 2026-07-03 at `my_learning_projects/tools/solo-company/` (plan: `2026-07-03-solo-company-implementation-plan.md`)
**Related:** Life Reshape System (`2026-07-03-life-reshape-system-design.md`) — this system is infrastructure for the quarter's primary (portfolio proof + job search), and its coaching rules apply here too.

## Context for a fresh Claude session (read this first)

Jaya is a solo AI engineer who wants to build projects as if he had an elite software-company team behind him. His known failure modes: getting sidetracked, overthinking during implementation, redesigning mid-build, and shipping nothing because polish/ideas never end. The cure is the same as his life-reshape system: **hard structure, subtraction, one thing at a time**. This system is a stage-gated pipeline where Claude wears a different company "hat" (role) at each stage and **enforces exit gates**. The pipeline is the boss, not the roles.

**How Claude must behave when running this system:**
- Enforce the gates. Refuse to skip a stage forward. Going backward requires a written reason in `decisions.md`.
- During Build: new feature ideas → `backlog.md`, no exceptions. Redesign urges → logged and deferred. Push back warmly but firmly.
- Anti-overthink rule: any decision considers **max 2 alternatives**, gets recorded in 3 lines, and is final unless *new information* arrives (which must be written down).
- "What's next?" is always answered with **exactly one task**.
- Refuse polish-loops past the gate criteria. Done > perfect.
- Tone: direct peer / senior colleague, explain the why behind pushback.

## The pipeline (hard gates)

Every project moves through these stages in order. Each stage has an owner role and an exit checklist.

| Stage | Role (hat) | Exit gate |
|---|---|---|
| 0. Intake | **CEO (Jaya) + Chief of Staff** | Frozen-list check (is this the quarter's work?); one-line goal + definition of done written |
| 1. Product | **Product Manager** | Problem, target user, success metric, MVP cut to smallest shippable, explicit out-of-scope list |
| 2. Business | **Monetization Strategist + CFO** | Revenue/portfolio value stated, pricing model, 3-competitor scan, cost budget opened in `costs.md` — before building |
| 2.5 Validate | **User Researcher** | 3–5 real potential users spoken to (Claude drafts the questions + where to find them; Jaya does the talking); demand signal recorded, or an explicit logged decision to build anyway (e.g., pure portfolio piece) |
| 3. Design | **Architect** | Tech choices (max 2 options considered), architecture sketch, risk list (use superpowers brainstorm → spec) |
| 4. Plan | **Engineering Manager** | Task breakdown with estimates; anything off-plan goes to backlog during build |
| 5. Build | **Senior Engineer** | Plan executed; mid-build ideas → backlog; redesigns deferred |
| 6. Quality | **QA + Security Engineer** | Tests pass, edge cases listed, secrets/licenses/privacy checked |
| 7. Ship | **DevOps + Docs** | Deployed/packaged, README, demo-able in 2 minutes (portfolio proof) |
| 8. Grow | **Marketing + Support + Data Analyst** | Launch post/demo published, feedback channel exists, basic usage instrumentation live (even a counter/log), next-iteration triage driven by data not vibes |
| 9. Retro | **Board review** | What worked/failed → feeds the weekly life-reshape review |

Roles solo devs forget, deliberately built in: monetization **before** build (stage 2), user research **before** design (stage 2.5), finance/cost tracking (CFO ledger, `costs.md`), security/legal-lite (stage 6), marketing/distribution + usage analytics (stage 8 — most solo projects die unshipped and unannounced), support/feedback triage (stage 8). HR has no solo equivalent.

**Division of labor:** Claude provides the guidance, drafts, checklists, and pushback for every role; Jaya personally executes the human-only parts (talking to users, publishing, paying for things) with that guidance.

## Anti-sidetrack machinery (per project: `project-board/`)

| File | Purpose |
|---|---|
| `STATE.md` | Current stage, current task, next gate. Every session starts by reading it — "where was I" is never a question. |
| `backlog.md` | Every mid-build idea lands here. Same psychology as the life-reshape frozen list. |
| `decisions.md` | Each decision in 3 lines: choice / why / alternatives dropped. Revisiting needs new written information. |
| `gates.md` | The stage checklists, checked off as evidence, with dates. The audit trail. |
| `costs.md` | CFO ledger: API spend, hosting, domains, tools — per project, updated at each gate; stage 9 compares real cost vs. value. |

## Where it lives

```
my_learning_projects/tools/solo-company/
  CLAUDE.md          # session instructions for this system (NOT in workspace CLAUDE.md)
  protocol.md        # the pipeline + gates + standing orders (source of truth)
  roles/             # one file per role: charter, questions it asks, gate it owns
  templates/         # STATE.md, backlog.md, decisions.md, gates.md templates
```

Each project gets its own `project-board/` folder created at Intake (stage 0). The workspace `CLAUDE.md` is **not** modified; the system's own `CLAUDE.md` inside the folder carries the instructions, and Claude reads it when working under that folder or when Jaya says "run solo-company on <project>".

## First real use

The system's first customer is the quarter's primary: run the portfolio-polish project through the pipeline end-to-end. Building the system and doing the quarter's work must be the same act.

## Phase 2 — extend to CrewAI / LangGraph (detailed next steps; FROZEN until phase 1 has shipped 1–2 projects)

The proven `protocol.md` + `roles/` become the spec for a real multi-agent implementation — a strong portfolio piece: *"I built the agent company I actually use."*

**Step-by-step when promoted:**

1. **Framework choice (max 2 options, per our own rule):** LangGraph vs CrewAI.
   - **LangGraph (recommended):** the pipeline is literally a state machine — stages map to nodes, gates map to conditional edges, `STATE.md` maps to the graph's persisted state/checkpointer. Better fit + Jaya already knows LangChain. Interview-relevant.
   - **CrewAI:** faster role scaffolding (Agent/Task/Crew), weaker gate enforcement; hierarchical process can emulate the pipeline but with less control.
2. **Port the artifacts:** `protocol.md` → graph definition (nodes = stages, edges = gate checks); each `roles/*.md` → an agent's system prompt; `templates/` → pydantic state models (ProjectState: stage, task, backlog, decisions, gate_evidence).
3. **Gate enforcement as code:** each gate = a validator function on the state; the graph cannot transition until the validator passes; backward transitions require a `reason` field appended to decisions.
4. **Human-in-the-loop nodes:** stage 0 (CEO approval) and each gate sign-off use LangGraph `interrupt()` — Jaya stays the CEO, agents don't ship without him.
5. **Persistence:** SQLite checkpointer so a project survives restarts; the `project-board/` markdown files remain the human-readable mirror (agents write to both).
6. **Tools for agents:** file I/O on the project repo, web search (competitor scan for stage 2), test runner (stage 6), git ops (stage 7).
7. **Eval before trust:** replay a completed phase-1 project through the agent version and diff the outputs against what the manual run produced — that's the acceptance test.
8. **Ship it as portfolio:** README with architecture diagram, 2-minute demo video, blog/LinkedIn post — i.e., run the solo-company pipeline *on itself* (stages 7–8).

**Cost note:** runs locally with API keys / existing Claude plan via Claude Agent SDK as an alternative backend; no cloud agent infra required (budget constraint recorded 2026-07-03).

## Error handling

- **Session amnesia:** `STATE.md` is the recovery point; the folder `CLAUDE.md` instructs every session to read it first.
- **Gate dispute (Jaya wants to skip):** Claude states which gate items are unmet, offers the smallest path to meet them; skip only with a logged decision entry marked `OVERRIDE`.
- **Stalled project (no progress 2+ weeks):** weekly life-reshape review flags it; Retro runs early — kill, shrink, or freeze.
- **Backlog overflow:** backlog is triaged only at stage 8/9, never mid-build.

## Success criteria

- One real project taken from Intake to Ship through all gates within the quarter.
- Zero mid-build feature additions outside backlog (audit via `backlog.md` + git history).
- Every project folder answers "what's the current state" in one file read.
- Phase 2 promoted only after phase 1 proves itself.

## Rejected alternatives

- **Role-first agent roster (no pipeline):** more opinions to overthink, no enforcement — recreates the failure mode.
- **Build CrewAI app first:** weeks of building before any benefit; the "build the system instead of the work" trap (same reason Life-OS-first was rejected in the life-reshape design).
- **Checklist-only:** loses the specialist-challenges-your-thinking value.
