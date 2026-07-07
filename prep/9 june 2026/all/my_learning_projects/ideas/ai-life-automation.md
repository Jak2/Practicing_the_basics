# AI Life Automation — Research & Plan

*Researched 2026-07-03 with Claude Code (Fable 5).*

Goal: automate life with AI agents / LLMs to reclaim time for what truly matters.

## What people are actually doing (2026 landscape)

The pattern has converged on **three layers**:

1. **A "second brain"** — a folder of markdown (often Obsidian) that an agent reads and writes: goals, projects, decisions, contacts, journal. This is the memory layer that makes automation personal instead of generic.
   - [coleam00/second-brain-starter](https://github.com/coleam00/second-brain-starter)
   - [obsidian-second-brain](https://github.com/eugeniughelbur/obsidian-second-brain)
2. **Scheduled agents ("routines")** — recurring jobs that run unattended: morning briefing (calendar + email + news), inbox triage that drafts replies in your voice, weekly reviews, expense categorization, job-board scanning. Engines: Claude Code routines/`/loop` or self-hosted [n8n](https://n8n.io/ai-agents/).
   - [Claude Code routines guide](https://claudefa.st/blog/guide/development/routines-guide)
   - [Claude Code Life OS techniques](https://cc.deeptoai.com/docs/en/community-tips/claude-code-life-os)
3. **Tool connections (MCP / APIs)** — Gmail, Calendar, Drive, Slack, bank statements, browsers. The agent acts, not just chats.
   - [AI executive assistant with Claude Code + Google Workspace](https://www.mindstudio.ai/blog/ai-executive-assistant-claude-code-google-workspace)
   - [Personal AI OS setup guide](https://www.mindstudio.ai/blog/build-personal-ai-operating-system-claude-code-setup-guide)

Common concrete wins people report:
- Daily agenda + priority briefing
- Email drafted-not-sent triage
- Meeting prep docs auto-generated
- Subscription / expense audits
- Job application pipelines
- "Chief of staff" weekly planning — good developer-grade example: [Alex Honchar's AI Chief of Staff](https://medium.com/data-science-collective/claude-code-for-life-2-a-personal-ai-chief-of-staff-for-daily-work-357b6c35573f)

## My plan (tailored — I'm an AI engineer, skip no-code tools)

Verdict: skip consumer tools (Lindy, ClawBox, Zapier — [comparison](https://www.eweek.com/news/best-agentic-ai-tools-automate-your-life/)); I'd outgrow them in a week. Claude Code + Google Workspace MCP + scheduled routines + a markdown second brain covers 90%, and everything built becomes interview material.

### Week 1 — foundations (highest ROI, near-zero build)
- [ ] **Authorize Google connectors** (Gmail, Calendar, Drive) in claude.ai connector settings — the single unlock; email/calendar automation is blocked until then.
- [ ] **Write `me.md` / life-context folder**: goals (job search, Trend Engine, Roadmap to Millionaire), routines, priorities. Every agent run gets smarter for free.

### Week 2 — first routines
- [ ] Morning briefing routine (calendar + inbox summary + project statuses) via `/schedule`.
- [ ] Extend `my_learning_projects/tools/career-ops/` into a scheduled agent: scan postings, score against `cv.md`, draft tailored applications. Serves the job search AND doubles as a portfolio piece.

### Week 3+ — the flywheel
- [ ] Inbox triage agent (label + draft replies, never auto-send).
- [ ] Weekly review agent: reads journal/project notes, proposes next week's plan.
- [ ] Wire the Financial Statement Parser (already built) to a monthly routine.

**Rule of thumb:** automate *observation and drafting* first, *action* later. Summarize/draft agents are safe from day one; agents that send/spend need months of trust.

## Search queries for deeper research (see end of file for follow-up Q&A)
- `"life OS" Claude Code site:reddit.com` / `r/ClaudeAI personal automation routines`
- `n8n self-hosted personal assistant workflows gmail calendar` (always-on server alternative)
- `MCP servers list awesome-mcp` — catalog of pluggable tools
- `"second brain" Obsidian AI agent daily note automation`
- `home assistant LLM voice agent` — smart-home dimension

---

# Follow-up Q&A (2026-07-03)

## My question

> tell me what tools/funnels/systems/mcp connectors/loop engineering systems i should have to build/have to help me in building my projects efficiently, give me your thoughts and best results and cross check

## Claude's response

Here's my cross-checked recommendation, organized by what you already have, what to add, and what to build. The web consensus and my own assessment agree on the core; I'll flag where they differ.

### What you already have (don't duplicate)

- **Claude Code with the Superpowers plugin** — this *is* a loop-engineering system: brainstorm → write plan → execute with subagents → code review → verify. Most people bolt this on with third-party frameworks; you have it as skills already.
- **Two memory plugins (claude-mem + mempalace)** — honestly, that's one too many. Pick one (claude-mem is the more active project) and disable the other; each MCP server burns 2–5k tokens of context per session just on schemas, which the MCP roundups (https://techsy.io/en/blog/best-mcp-servers-2026) consistently flag as the hidden cost.
- **CLAUDE.md + `made_by_claude/` tools convention** — this is exactly the "reusable tooling registry" pattern; keep growing it.

### MCP connectors worth adding (cross-checked "core three")

Every 2026 ranking (Nimbalyst: https://nimbalyst.com/blog/best-claude-code-mcp-servers/, Bito: https://bito.ai/ai-tools/claude-code-mcp-servers/, dev.to: https://dev.to/jangwook_kim_e31e7291ad98/top-15-mcp-servers-every-developer-should-install-in-2026-3ak2) converges on the same three:

1. **Context7** — injects version-pinned library docs so the model stops hallucinating APIs. Highest-value single install for an engineer; stale docs are the #1 source of AI coding errors.
2. **Playwright MCP** (Microsoft official) — drives a real browser via the accessibility tree. This unlocks your career-ops job scraping, testing Streamlit/React UIs, and any web automation.
3. **GitHub MCP** — though note: the `gh` CLI already covers most of this in Claude Code, so this one is optional for you. The roundups also say **skip the Filesystem MCP** — built-in tools already do it.

Plus, from your last session: **authorize Gmail/Calendar/Drive connectors** in claude.ai settings — still the blocker for life automation.

### Loop / verification systems (the part most people underinvest)

The agentic workflow research (https://sourcegraph.com/blog/agentic-coding) is unanimous: gains come from **fast, closed feedback loops**, not from more agents. Concretely:

- **Spec-driven flow**: structure the request before executing — you have this via superpowers `brainstorming` → `writing-plans` → `executing-plans`. Use it for anything over ~1 hour of work; the data (https://www.teamday.ai/blog/complete-guide-agentic-coding-2026) shows the biggest gains go to people who invest in the spec.
- **Hooks** (via `/update-config`): auto-run `ruff`/`pytest` after every edit so the agent self-corrects without you asking. This is the cheapest "loop engineering" there is.
- **Scheduled routines** (`/schedule`): overnight/cron agents for career-ops scanning, dependency checks, weekly project digests.
- **Verification gate**: always end work with `/verify` or superpowers `verification-before-completion` — evidence before "done."

### What to *build* (your gaps, in priority order)

1. **A project-scaffold skill** — one command that creates your standard Python project (FastAPI/Streamlit, ruff, pytest, CLAUDE.md, README). You start projects constantly; this compounds fastest.
2. **Career-ops funnel completion** — scraper (Playwright MCP) → scorer (against cv.md) → drafter → daily digest routine. It's a funnel in the literal sense: wide intake, scored filtering, human decision at the bottom.
3. **A personal eval harness** — you built an LLM Evaluation Framework professionally; a slim version wired as a hook/CI step for your own projects turns every prompt change into a regression-tested change. Nobody else in the job market demos that.
4. **`me.md` + second-brain folder** — from the previous plan; it's the context layer all the routines read.

**Bottom line:** you don't need more frameworks — you need Context7 + Playwright installed, one memory plugin removed, hooks for lint/test auto-feedback, and the career-ops funnel finished. That's the whole efficient stack.

### Sources

- TECHSY MCP rankings: https://techsy.io/en/blog/best-mcp-servers-2026
- Nimbalyst Claude Code MCP guide: https://nimbalyst.com/blog/best-claude-code-mcp-servers/
- Bito top 12: https://bito.ai/ai-tools/claude-code-mcp-servers/
- dev.to top 15: https://dev.to/jangwook_kim_e31e7291ad98/top-15-mcp-servers-every-developer-should-install-in-2026-3ak2
- Sourcegraph agentic coding: https://sourcegraph.com/blog/agentic-coding
- Complete guide to agentic coding 2026: https://www.teamday.ai/blog/complete-guide-agentic-coding-2026
- Kilo agentic workflow: https://kilo.ai/articles/beyond-autocomplete
- Codegen workflows: https://codegen.com/how-to-build-agentic-coding-workflows/

---

# Follow-up Q&A #2 (2026-07-03) — Life Reshaping Structure

## My question

> tell me if want to reshape my life to be better, learn faster, focus better, improve my personality to achieve anything that i desire, what structure i should follow, what i should need and what can you do for me, provide suggestions use brainstorm skill to answer this

*(Clarifying answers I gave: bottleneck = all four — focus, consistency, direction, energy; time budget = unpredictable; "personality" = all four — confidence & communication, discipline & self-control, thinking quality, emotional steadiness.)*

## Claude's response

That's the full picture, and it's a coherent one: **everything feels like a bottleneck, time is unpredictable, and you want to grow on every axis at once.** That combination has a name — overload — and the cure is not more effort, it's *subtraction and structure*. Per the brainstorming process, here are three approaches with my recommendation:

### Three possible structures

**Option A — The Deep Fix (recommended): One keystone system, one focus per quarter.**
You don't attack all four bottlenecks. You build one minimal daily system (the "spine") that automatically improves focus, consistency, and energy as side effects, and you pick **one** primary focus per 12 weeks — right now that's obviously *land the job*. Everything else (Trend Engine, millionaire roadmap, personality work) gets a maintenance dose, not a growth dose. This is how people with unpredictable schedules actually compound: the spine is small enough to survive bad days.

**Option B — The Habit Stack:** classic Atomic Habits approach — build 5–6 small habits across all areas simultaneously (reading, exercise, journaling, deep work, communication practice). Broader, feels more complete, but with unpredictable time and a consistency problem, parallel habit-building historically fails — it's what produces your "start strong, drop off" pattern.

**Option C — The Full Life-OS:** design the complete second-brain + routines + tracking system first, then live inside it. Appeals to you as an engineer, but it's a trap for you specifically — building the system becomes the procrastination. You'd get a beautiful dashboard and no changed life.

**I recommend A**, with me (Claude) playing the roles that machines are good at so your willpower is spent only where it must be.

### The design (Option A, concretely)

**The spine — non-negotiable daily minimum (~45 min, survives chaos days):**
1. **Anchor block** (30 min): one deep-work session on the quarter's focus. On good days it extends to hours; on bad days 30 min still counts. Consistency is defined as "did the anchor," nothing else.
2. **Shutdown note** (5 min): three lines in a daily log — what I did, what I noticed, tomorrow's one thing. This single habit trains thinking quality, emotional steadiness, and gives me (Claude) the data to coach you.
3. **One physical act** (10 min): walk, pushups, anything. Energy floor.

**The quarter — one focus, three tiers:**
- **Primary (80%):** job search — interview prep, applications, portfolio proof.
- **Maintenance (15%):** one project (Trend Engine) moved forward in weekly sessions, not daily guilt.
- **Frozen (5%):** everything else goes on an "after the job" list — written down so your brain releases it.

**Personality, trained as a byproduct:** confidence via weekly mock interviews with me; discipline via the anchor-block streak; thinking via the shutdown notes + one book at a time; steadiness via the fact that a system with a visible floor kills the shame spiral that follows missed days.

**What I do for you:**
- **Morning routine** (scheduled agent): reads your log + goals, tells you today's *one thing* — you never decide from scratch.
- **Weekly review** (scheduled agent): reads the week's shutdown notes, shows patterns (when do you actually focus? what derails you?), proposes next week.
- **Mock interviewer / sparring partner** on demand.
- **Everything automatable gets automated** (career-ops funnel, briefings — the plan already in your ideas file), so your unpredictable hours go to the anchor, not to admin.

**What you need that I can't provide:** a fixed sleep/wake anchor (pick the wake time, that's the one hard rule), phone out of reach during the anchor block, and the honesty to log bad days instead of hiding them.

*(Follow-up: asked if this was Claude's best → yes. Given "all four bottlenecks + unpredictable time," any structure demanding more than a small daily floor would recreate the drop-off pattern. Option A approved; spec doc written.)*
