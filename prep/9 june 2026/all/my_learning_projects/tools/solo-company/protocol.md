# Solo Company Protocol — Source of Truth

Every project moves through these stages in order. Each stage has an owner role (file in `roles/`) and an exit gate. The pipeline is the boss, not the roles.

## The pipeline

| Stage | Role (hat) | Exit gate |
|---|---|---|
| 0. Intake | CEO (Jaya) + Chief of Staff (`roles/chief-of-staff.md`) | Frozen-list check passed (is this the quarter's work?); one-line goal + definition of done written in STATE.md |
| 1. Product | Product Manager (`roles/product-manager.md`) | Problem, target user, success metric, MVP cut to smallest shippable, explicit out-of-scope list |
| 2. Business | Monetization Strategist + CFO (`roles/monetization-cfo.md`) | Revenue/portfolio value stated, pricing model, 3-competitor scan, cost budget opened in `costs.md` |
| 2.5 Validate | User Researcher (`roles/user-researcher.md`) | 3–5 real potential users spoken to (Claude drafts questions + where to find them; Jaya talks); demand signal recorded, OR a logged decision to build anyway |
| 3. Design | Architect (`roles/architect.md`) | Tech choices (max 2 options considered), architecture sketch, risk list — use superpowers brainstorm → spec |
| 4. Plan | Engineering Manager (`roles/engineering-manager.md`) | Task breakdown with estimates; anything off-plan goes to backlog during build |
| 5. Build | Senior Engineer (`roles/senior-engineer.md`) | Plan executed; mid-build ideas → backlog; redesigns deferred |
| 6. Quality | QA + Security Engineer (`roles/qa-security.md`) | Tests pass, edge cases listed, secrets/licenses/privacy checked |
| 7. Ship | DevOps + Docs (`roles/devops-docs.md`) | Deployed/packaged, README, demo-able in 2 minutes (portfolio proof) |
| 8. Grow | Marketing + Support + Data Analyst (`roles/marketing-support-analyst.md`) | Launch post/demo published, feedback channel exists, basic usage instrumentation live, next-iteration triage driven by data |
| 9. Retro | Board (`roles/board.md`) | What worked/failed written; cost vs. value verdict from `costs.md`; feeds the weekly life-reshape review |

## Standing orders

1. **Hard gates.** Never move forward past an unmet gate. Moving backward requires a written reason in `decisions.md`.
2. **Anti-overthink.** Any decision: max 2 alternatives, recorded in 3 lines (choice / why / dropped), final unless *new information* arrives — which must be written down.
3. **One task.** "What's next?" is always answered with exactly one task, taken from STATE.md.
4. **Backlog discipline.** Every mid-build idea → `backlog.md`. Triage happens only at stage 8/9, never mid-build.
5. **No polish-loops.** Gate criteria define done. Done > perfect.
6. **Act elite, not agreeable.** In every role, behave as a senior specialist with strong opinions: challenge Jaya's assumptions, name the weakness in his answer before accepting it, and never rubber-stamp a gate item. If an answer to a role's questions is vague, push back once before recording it.

## Artifact convention (where stage outputs live)

- Every stage's work products (problem statement, competitor scan, research notes, risk list, retro, etc.) are written to `project-board/stage-notes/<stage-number>-<stage-name>.md` (e.g., `1-product.md`, `2.5-validate.md`) — created when the stage starts.
- Exceptions with a natural home elsewhere: costs → `costs.md`; decisions/overrides → `decisions.md`; design spec → a superpowers spec file; README/demo → the project itself. `gates.md` records only evidence pointers, not the content.
- STATE.md is updated at every stage transition and every task change.

## Gate dispute / override

If Jaya wants to skip a gate item: Claude states which items are unmet and offers the smallest path to meet them. Skip only with a decisions.md entry:

```
OVERRIDE [date] — stage X, item skipped: <item>. Reason: <reason>. Accepted risk: <risk>.
```

## Intake procedure (stage 0)

1. Frozen-list check against `../../ideas/life-reshape-daily-system/current-quarter-focus.md`. If it's not the quarter's work → it goes to the frozen list, not the pipeline. Push back warmly.
2. Create `project-board/` inside the project folder; copy all five files from `templates/`.
3. Fill STATE.md: project name, one-line goal, definition of done, stage = 0 → 1.

## Error handling

- **Session amnesia:** STATE.md is the recovery point; read it first, always.
- **Stalled project (no progress 2+ weeks):** the weekly life-reshape review flags it; run Retro early — kill, shrink, or freeze.
- **Backlog overflow:** still only triaged at 8/9. A long backlog is information for the Retro, not a to-do list.

## Phase 2 (FROZEN)

The CrewAI/LangGraph implementation of this protocol is a future portfolio project. Detailed steps live in the design spec. It stays frozen until phase 1 has shipped 1–2 projects. Do not start it earlier.
