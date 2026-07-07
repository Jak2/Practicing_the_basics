# Solo Company — Read Me First

**What this is:** My one-man software company. A stage-gated pipeline where Claude wears a different company role (PM, CFO, Architect, QA, Marketing…) at each stage and **enforces exit gates**, so I can't get sidetracked, overthink, redesign mid-build, or ship nothing. Built 2026-07-03.

**Why it exists:** My failure modes are sidetracking, mid-build feature ideas, and overthinking decisions. The fix is the same as my life-reshape system: hard structure, one thing at a time, ideas go to a backlog instead of derailing the build.

## How I use it

1. **Start a project:** say to Claude — **"run solo-company on \<project\>"**. Claude runs Intake (stage 0): checks the idea against my quarter's frozen list, creates a `project-board/` folder inside the project from `templates/`, and writes the one-line goal + definition of done.
2. **Work:** say **"what's next"** — Claude answers with exactly ONE task (from the project's `project-board/STATE.md`).
3. **Idea strikes mid-build:** say **"new idea: ..."** — it goes to `backlog.md`, discussed only at stage 8/9. That's the rule.
4. **Move stages:** each stage has an exit checklist in the project's `gates.md`; Claude refuses to skip forward. Skipping an item needs an OVERRIDE entry in `decisions.md`.
5. **Human-only parts are mine:** talking to users (stage 2.5), publishing the launch post (stage 8), paying for things. Claude drafts everything and tells me exactly what to do.

## The pipeline at a glance

Intake → Product → Business (money + costs) → Validate (talk to real users) → Design → Plan → Build → Quality (tests + security) → Ship (demo-able in 2 min) → Grow (launch + feedback + data) → Retro.

➡️ **Full pipeline table, standing orders, and error handling already exist in `protocol.md` — that's the source of truth, don't duplicate it.**

## Where everything is explained (already written — go there, don't rewrite)

| Want to know... | It's already in |
|---|---|
| The full stage/gate table, standing orders, override & intake procedure | `protocol.md` |
| What Claude must do every session + trigger phrases | `CLAUDE.md` (this folder) |
| Each role: its charter, the questions it asks me, the gate it owns | `roles/` (11 files, one per role) |
| The blank project-board files copied into each project | `templates/` (STATE, backlog, decisions, gates, costs) |
| Why the system is designed this way + the CrewAI/LangGraph phase-2 plan | `../../ideas/2026-07-03-solo-company-elite-team-system-design.md` |
| How it was built | `../../ideas/2026-07-03-solo-company-implementation-plan.md` |

## Rules I agreed to

- Hard gates — no skipping forward; going backward needs a written reason.
- Max 2 alternatives per decision, recorded in 3 lines, final unless new written information arrives.
- Mid-build ideas → backlog, always. New *projects* → the life-reshape frozen list.
- Phase 2 (turning this into a CrewAI/LangGraph portfolio app) stays **frozen** until this manual version has shipped 1–2 projects.

## First customer

The quarter's primary: run my portfolio-polish project through the pipeline end-to-end. Building proof for the job search and using this system are the same act.
