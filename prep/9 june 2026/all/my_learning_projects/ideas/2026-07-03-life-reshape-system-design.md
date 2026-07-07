# Life Reshape System — Design Spec

**Date:** 2026-07-03
**Owner:** Jaya Arun Kumar Tulluri
**Status:** Approved design (Option A — "The Deep Fix"), pending implementation plan

## pesistent memory location
/home/asterisk/.claude/projects/-media-asterisk-windows-drive-project-learn/memory/MEMORY.md

## Context for a fresh Claude session (read this first)

This spec is self-contained: if Jaya hands you only this file, you have everything needed to coach him at full fidelity. Key context that produced this design:

**Who Jaya is:** AI Engineer / Python Developer, 5+ years (Nokia, Infinite, Brane — agentic AI pipelines, LangChain, FastAPI). Currently job-searching as an immediate joiner — that's why "land the job" is the quarter's primary. Resume: `interview_prep/resume_prep/Jaya_Arun_Kumar_Resume_Ai_Engineer_Python_Developer.pdf`. Job-search tooling: `my_learning_projects/tools/career-ops/`. Related automation research: `my_learning_projects/ideas/ai-life-automation.md`.

**The diagnosis (why the design looks like this):** When asked what his bottleneck was — focus, consistency, direction, or energy — he answered *all four*. His time is *unpredictable*. By "improve personality" he meant *all* of: confidence/communication, discipline, thinking quality, emotional steadiness. That combination is overload, and his known failure pattern is **starting strong and dropping off**. So the design is deliberately small: the cure is subtraction and structure, not more effort. Do not "improve" this system by adding habits, trackers, or ambition — that recreates the failure mode. Two alternatives were explicitly rejected: parallel habit-stacking (Option B) and building a full Life-OS first (Option C, an engineer's procrastination trap).

**How Claude should behave when coaching against this spec:**
- **Enforce the floor, not the ceiling.** A 30-min anchor on a bad day is full success. Never suggest doubling up after a missed day.
- **Guard the frozen list.** When Jaya brings a new project idea, default it to the frozen list; promotion happens only at quarter review. Push back warmly but firmly.
- **One thing per day.** Morning guidance always ends in a single concrete task, not a list.
- **Normalize bad days.** If the log shows missed days, respond with pattern analysis, not motivation speeches. Shame is the enemy; the shame spiral after missed days is what killed his past attempts.
- **Personality work is embedded, not scheduled.** Mock interviews train confidence; the streak trains discipline; shutdown notes train thinking; the visible floor trains steadiness. Don't create separate personality habits.
- **Tone:** direct peer, not cheerleader. He's an engineer — explain the *why* behind pushback.

## Problem

Jaya wants to learn faster, focus better, build discipline/confidence/thinking quality/emotional steadiness, and achieve his goals. Diagnosed constraints:

- All four bottlenecks present at once: focus, consistency, direction, energy → overload, not laziness.
- Available time is **unpredictable** — the system must survive chaos days, not assume routine.
- History of starting strong and dropping off → parallel habit-building (Option B) and build-the-perfect-system-first (Option C) were considered and rejected as failure modes for this profile.

## Design principle

**Subtraction and structure.** One minimal daily spine + one primary focus per quarter. Willpower is spent only on the spine; Claude automates or scaffolds everything else. Success = "did the spine today," nothing more.

## Component 1 — The Daily Spine (~45 min floor, non-negotiable)

| # | Habit | Time | Rule |
|---|-------|------|------|
| 1 | **Anchor block** | 30 min | One deep-work session on the quarter's primary focus. Phone out of reach. Good days extend it; bad days 30 min counts as full success. |
| 2 | **Shutdown note** | 5 min | Three lines in the daily log: what I did / what I noticed / tomorrow's one thing. Bad days get logged honestly, never skipped. |
| 3 | **Physical act** | 10 min | Walk, pushups, anything. Energy floor. |

Streak metric = consecutive days the spine was completed. Nothing else is tracked as a habit.

## Component 2 — The Quarter (12 weeks, current: Q3 2026)

| Tier | Share | Contents |
|------|-------|----------|
| **Primary** | 80% | **Land the job** — interview prep, applications, portfolio proof. All anchor blocks default here. |
| **Maintenance** | 15% | Trend Engine — one scheduled weekly session, no daily guilt. |
| **Frozen** | 5% | Everything else (Roadmap to Millionaire, new project ideas) → written to an "after the job" list so the brain releases it. |

At quarter end: review, pick next quarter's single primary.

## Component 3 — Personality, trained as byproduct (no separate habit slots)

- **Confidence & communication** → weekly mock interview with Claude.
- **Discipline & self-control** → anchor-block streak.
- **Thinking quality** → shutdown notes + one book at a time.
- **Emotional steadiness** → the visible daily floor kills the shame spiral after missed days; honest logging normalizes bad days.

## Component 4 — What Claude provides

1. **Morning routine (scheduled agent):** reads log + goals → outputs today's *one thing*. Jaya never decides from scratch.
2. **Weekly review (scheduled agent):** reads the week's shutdown notes → surfaces patterns (when focus actually happens, what derails) → proposes next week.
3. **Mock interviewer / sparring partner** on demand.
4. **Automation of admin:** career-ops funnel, briefings, and everything in `ideas/ai-life-automation.md` — unpredictable free hours go to the anchor, not admin.

## Component 5 — What only Jaya can provide

- A **fixed wake time** (the single hard scheduling rule; everything else floats).
- Phone physically out of reach during the anchor block.
- Honest logging of bad days.

## Data layout (created 2026-07-03)

```
my_learning_projects/ideas/life-reshape-daily-system/
  README-start-here.md       # how the folder + system works, how to prompt Claude
  me.md                      # who Jaya is, goals, constraints, coaching rules
  current-quarter-focus.md   # Q3 2026: primary / maintenance / frozen list
  daily-log/YYYY-MM-DD.md    # daily shutdown notes (3 lines)
  weekly-reviews/            # Claude's weekly pattern-analysis outputs
```

## Error handling (failure modes)

- **Missed day:** log it in the next shutdown note, restart streak, no compensation or doubling-up.
- **Chaos week (0 anchor blocks):** weekly review flags it and shrinks the anchor to 15 min the following week — floor lowers, never disappears.
- **Scope creep (new shiny project):** goes to the frozen list by default; can only be promoted at quarter review.

## Success criteria (first 4 weeks)

- ≥ 5 spine completions/week on average.
- Daily log exists and is honest (bad days present).
- Morning + weekly routines running.
- At least 2 mock interviews done.

## Rejected alternatives

- **Option B — Habit Stack:** 5–6 parallel habits; historically produces Jaya's start-strong/drop-off pattern.
- **Option C — Full Life-OS first:** building the system becomes the procrastination; dashboard without changed life.

## Routine setup — how it will work (deferred; decided 2026-07-03: local cron only, no cloud)

**Decision:** Jaya doesn't have budget for cloud agents on Anthropic's infra. When routines get set up, use the **local fallback**: system cron jobs running `claude -p "<prompt>"` on his machine. They only fire when the machine is on — acceptable trade-off. Do not propose cloud routines / `/schedule` unless he raises it.

**The two routines to create (when he says "set up the routines"):**

1. **Morning briefing** — daily, shortly after his wake time (the blank in `me.md` becomes the cron time). Prompt: read `me.md`, `current-quarter-focus.md`, and the last few files in `daily-log/`; output one short message — yesterday's status, current streak, and **today's one thing** (a single concrete task, per coaching rules).
2. **Weekly review** — Sunday evening. Prompt: read the week's seven log files; write pattern analysis to `weekly-reviews/YYYY-WW.md` — spine completions count, when anchor blocks actually happened, what derailed, proposal for next week (apply the "shrink anchor to 15 min after a chaos week" rule).

**Setup flow:** Jaya runs the spine manually first → fills wake time in `me.md` → says "set up the routines" → Claude writes the two cron entries (~10 min). Delivery note: the weekly review writes a file either way; the morning briefing reaches him via terminal/notification — email delivery would need the Gmail connector authorized in claude.ai settings.

**Prerequisite reminder:** don't automate before the manual habit exists — that's Option C sneaking back in.
