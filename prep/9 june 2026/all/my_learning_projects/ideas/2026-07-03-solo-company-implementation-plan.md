# Solo Company System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the markdown-based Solo Company system at `my_learning_projects/tools/solo-company/` per the approved spec (`../ideas/2026-07-03-solo-company-elite-team-system-design.md`).

**Architecture:** Pure markdown, no code. `protocol.md` is the source of truth (pipeline + gates + standing orders); `roles/` holds one charter per role; `templates/` holds the four project-board files; folder-local `CLAUDE.md` wires it into any Claude session. Workspace CLAUDE.md is NOT modified (owner's instruction).

**Tech Stack:** Markdown only.

## Global Constraints (from spec)

- Stages: 0 Intake, 1 Product, 2 Business, 2.5 Validate, 3 Design, 4 Plan, 5 Build, 6 Quality, 7 Ship, 8 Grow, 9 Retro — exact gates as in the spec table.
- Standing orders: hard gates; backward moves need a written reason; max 2 alternatives per decision; one task at a time; backlog for all mid-build ideas; no polish past gate criteria; OVERRIDE entries for skipped gates.
- Project-board files: `STATE.md`, `backlog.md`, `decisions.md`, `gates.md`, `costs.md`.
- Phase 2 (CrewAI/LangGraph) stays frozen — referenced, not built.
- Workspace is not a git repo → no commits.

### Task 1: Folder + CLAUDE.md
**Files:** Create `my_learning_projects/tools/solo-company/CLAUDE.md`
- [ ] Write CLAUDE.md: what the system is, read `protocol.md` first, read the target project's `project-board/STATE.md` before anything, enforce standing orders, trigger phrases ("run solo-company on <project>", "what's next", "new idea:").
- [ ] Verify: file exists and references only files this plan creates.

### Task 2: protocol.md (source of truth)
**Files:** Create `my_learning_projects/tools/solo-company/protocol.md`
- [ ] Write the full pipeline table (all 11 stages, roles, exit gates verbatim from spec), standing orders, gate-dispute/override procedure, error handling (session amnesia, stalled project, backlog overflow), intake procedure (create project-board from templates).
- [ ] Verify: every stage in spec appears; every role named has a file planned in Task 3.

### Task 3: roles/
**Files:** Create `roles/chief-of-staff.md`, `roles/product-manager.md`, `roles/monetization-cfo.md`, `roles/user-researcher.md`, `roles/architect.md`, `roles/engineering-manager.md`, `roles/senior-engineer.md`, `roles/qa-security.md`, `roles/devops-docs.md`, `roles/marketing-support-analyst.md`, `roles/board.md`
- [ ] Each file: charter (one paragraph), the questions this role always asks Jaya, the gate it owns (checklist), division of labor (what Claude does vs what Jaya must do personally), handoff to next stage.
- [ ] Verify: 11 files; gates match protocol.md exactly.

### Task 4: templates/
**Files:** Create `templates/STATE.md`, `templates/backlog.md`, `templates/decisions.md`, `templates/gates.md`, `templates/costs.md`
- [ ] STATE.md: project, current stage, current single task, next gate, last updated. backlog.md: idea | date | stage-captured | triage-decision (triaged only at 8/9). decisions.md: 3-line entries (choice/why/dropped) + OVERRIDE format. gates.md: all stage checklists pre-listed with checkboxes + evidence + date. costs.md: ledger table (date, item, cost, running total) + retro verdict line.
- [ ] Verify: gates.md checklist identical to protocol.md table.

### Task 5: Wire-up + memory
- [ ] Update spec's status line to "Implemented 2026-07-03".
- [ ] Add memory file `project_solo_company_system.md` + MEMORY.md index line.
- [ ] Final cross-check: all internal references resolve; no mention of cloud agents.
