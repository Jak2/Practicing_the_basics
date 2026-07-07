# Life Reshape Daily System — Start Here

This folder is the living workspace for my life-reshape system (design spec: `../2026-07-03-life-reshape-system-design.md` — Claude must read that spec before coaching).

## What's in here

| File / folder | What it is |
|---------------|-----------|
| `me.md` | Who I am, my goals, values, constraints — the context every Claude session reads first |
| `current-quarter-focus.md` | This quarter's ONE primary focus + maintenance + frozen list |
| `health.md` | Health module: physical menu, 5 food anchors, honest verdict on `../health/` files |
| `daily-log/` | My 3-line shutdown notes, one file per day (`YYYY-MM-DD.md`) |
| `weekly-reviews/` | Claude's weekly pattern analysis of my logs |

## The daily spine (the only rules)

1. **Anchor block** — 30 min deep work on the quarter's primary. Phone in another room. 30 min on a bad day = full success.
2. **Shutdown note** — 3 lines in `daily-log/YYYY-MM-DD.md`: did / noticed / tomorrow's one thing. Bad days get logged too.
3. **Physical act** — 10 min of anything. (`health.md` defines what a *good* one looks like when there's more time; 10 min still = full success.)

Streak = days the spine was done. Nothing else is tracked.

## How to use Claude with this

- **Morning:** "Read my life-reshape system and tell me today's one thing."
- **Evening:** "Log my shutdown note: <3 lines>" (or write it yourself).
- **Weekly:** "Do my weekly review" → Claude reads the week's logs, writes to `weekly-reviews/`.
- **Anytime:** "Mock interview me" / "I have a new project idea" (→ it goes to the frozen list; that's the rule).

## Automation status (as of 2026-07-03)

**Nothing is scheduled yet — the system is fully manual for now, by design** (build the habit first, then automate).

- No cron jobs exist. Cloud routines are ruled out (no budget for cloud agents) — decision recorded in the spec.
- When ready, say "set up the routines" to Claude: it will add two **local system crontab** entries running `claude -p` on this machine — a daily morning briefing (reads this folder, outputs today's one thing) and a Sunday weekly review (writes to `weekly-reviews/`). Prerequisites (Claude Code CLI, prompts in the spec) are already in place; ~10-minute job. Local cron costs nothing beyond the existing Claude Code plan; it just requires the machine to be on when it fires.
- Until then, the manual equivalent: morning — "read my life-reshape system and tell me today's one thing"; evening — "log my shutdown note: <3 lines>".
