---
name: superpowers-skills-reference
description: Reference guide to all 14 Superpowers skills — what each does, steps to use, how it functions, and use cases, plus the workflow that ties them together.
---

superpowers:

using-superpowers
brainstorming
writing-plans
executing-plans
subagent-driven-development
dispatching-parallel-agents
test-driven-development
systematic-debugging
verification-before-completion
requesting-code-review
receiving-code-review
using-git-worktrees
finishing-a-development-branch
writing-skills



---
# Superpowers — Complete Skills Reference

Superpowers (plugin `superpowers@superpowers-dev`, v6.0.2, by Jesse Vincent) is a
**pure skills library** — it ships **no slash commands**. Its 14 skills activate
automatically (via hooks / the `using-superpowers` meta-skill) or when you ask
Claude to "use the X skill".

**How to invoke:** In Claude Code, load skills through the `Skill` tool — never read
their `SKILL.md` files manually. Invoking them ensures they activate properly. On
other platforms (Codex, Copilot CLI, Gemini CLI) skills load natively or via an
`activate_skill`/`skill` tool.

**Instruction priority (built in):**
1. **User instructions** (CLAUDE.md / direct requests) — highest
2. **Superpowers skills** — override default behavior where they conflict
3. **Default system prompt** — lowest

If CLAUDE.md says "no TDD", that wins over the TDD skill. The user is always in control.

---

## Using Superpowers in Claude Code (important)

**There are NO slash commands.** Don't look for `/superpowers:brainstorming` — it doesn't
exist. Superpowers is a *pure skills library*; you trigger skills with plain English, not
commands. Two ways skills fire:

1. **Auto-activation** — a hook plus the `using-superpowers` meta-skill watches your message
   and loads the relevant skill on its own. Say *"let's build a rate limiter"* and
   brainstorming activates automatically.
2. **Explicit request** — name the skill in natural language: *"use the brainstorming skill"*
   or *"brainstorm this with me."* Claude then loads it via the `Skill` tool.

**You never** type a command, run the `Skill` tool yourself, or read `SKILL.md` files — Claude
handles loading. When a skill fires, Claude announces it ("Using brainstorming to…") and then
follows the skill's steps. After install, **restart Claude Code** so hooks/skills load.

### Quick trigger-phrase cheat sheet

| Skill | What you say in Claude Code |
|---|---|
| brainstorming | "Let's build X" / "brainstorm this feature" |
| writing-plans | "write a plan for this spec" |
| subagent-driven-development | "execute this plan" (subagents available) |
| executing-plans | "run this plan in a fresh session" |
| dispatching-parallel-agents | "investigate these 3 failures in parallel" |
| test-driven-development | auto-fires on "implement X"; or "use TDD" |
| systematic-debugging | "this test is failing" / "debug this" |
| verification-before-completion | auto-fires before "done/fixed" claims |
| requesting-code-review | "review my changes" |
| receiving-code-review | auto-fires when you paste review feedback |
| using-git-worktrees | "set up a worktree for this" |
| finishing-a-development-branch | "wrap up and merge/PR this branch" |
| writing-skills | "Screate a new skill for X" |

---

## The Core Workflow

The skills chain into one development loop — the path used ~90% of the time:

```
brainstorming  →  writing-plans  →  using-git-worktrees  →  execution  →  review  →  finishing
   (idea→spec)     (spec→plan)        (isolate work)       (TDD+debug)   (code review)  (merge/PR)
```

- **Execution** is either **subagent-driven-development** (same session, has subagents — preferred)
  or **executing-plans** (separate session / no subagents).
- Running continuously underneath everything: **test-driven-development**,
  **systematic-debugging**, and **verification-before-completion**.

**Most-used skills:** `brainstorming`, `writing-plans`, `subagent-driven-development`,
`test-driven-development`, `systematic-debugging`, `verification-before-completion`.

---

## 1. using-superpowers  *(meta / entry point)*
- **What it does:** Establishes how to find and invoke every other skill at the start
  of a conversation. Enforces: if there's even a ~1% chance a skill applies, you MUST invoke it.
- **How it functions:** Loaded early; routes you to the right skill and explains the
  platform's skill-loading mechanism.
- **Steps to use:** Nothing manual — it's the dispatcher. It fires at conversation start.
- **Try saying:** *(nothing — it loads automatically at the start of every session.)*
- **Use case:** Background routing that makes the rest of the skills trigger at the right moment.

## 2. brainstorming  *(idea → design/spec)*
- **What it does:** Turns a vague idea into a fully-formed design through collaborative,
  one-question-at-a-time dialogue.
- **How it functions:** Explores context → asks clarifying questions one at a time →
  proposes 2–3 approaches with trade-offs + a recommendation → presents the design
  section by section for approval → writes a spec to
  `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` → hands off to writing-plans.
- **Steps to use:** Invoke before any feature/creative work; answer questions; approve
  the design. **Hard gate:** no code/scaffolding until you approve — even for "simple" tasks.
- **Try saying:** *"Let's build a CSV export feature — brainstorm it with me first."*
- **Use case:** Start here before ANY creative/feature work; catches bad assumptions early.

## 3. writing-plans  *(spec → phased plan)*
- **What it does:** Produces a comprehensive, bite-sized implementation plan written for
  an engineer with zero codebase context.
- **How it functions:** Maps file structure first (one responsibility per file),
  right-sizes tasks (each = smallest unit with its own test cycle + reviewer gate),
  bakes in DRY/YAGNI/TDD/frequent commits. Saves to
  `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`; splits multi-subsystem specs into separate plans.
- **Steps to use:** Run after brainstorming (or with an existing spec), before touching code.
- **Try saying:** *"Write an implementation plan from the spec we just approved."*
- **Use case:** Any multi-step task once you have a spec.

## 4. executing-plans  *(run a plan, no subagents)*
- **What it does:** Loads a written plan, reviews it critically, executes every task, reports when done.
- **How it functions:** Read plan → raise concerns → create todos → execute each task
  step-by-step running verifications → finish via finishing-a-development-branch.
- **Steps to use:** Point it at a plan file; let it work through tasks.
- **Use case:** Executing a plan in a **separate session** or a platform **without subagents**.
  If subagents are available, prefer #5.
- **Try saying:** *"Open the plan at docs/superpowers/plans/… and execute it in this session."*

## 5. subagent-driven-development  *(run a plan, with subagents — preferred)*
- **What it does:** Executes a plan by dispatching a **fresh implementer subagent per task**,
  a task review after each, and a broad whole-branch review at the end.
- **How it functions:** Each subagent gets precisely crafted context — never your session
  history — so it stays focused and your context is preserved. Runs **continuously**, only
  stopping on a blocker, genuine ambiguity, or completion.
- **Steps to use:** Invoke with a plan; it dispatches and reviews automatically.
- **Use case:** Plan with mostly-independent tasks, same session, subagent-capable platform.
  The default high-quality execution path.
- **Try saying:** *"Execute this plan using subagents, reviewing after each task."*

## 6. dispatching-parallel-agents  *(fan-out)*
- **What it does:** Dispatches one agent per independent problem so they work concurrently.
- **How it functions:** Each agent gets isolated, purpose-built context; used only when
  problems share no state and can truly run in parallel.
- **Steps to use:** Identify 2+ independent tasks; invoke to fan them out.
- **Try saying:** *"These three test files fail for unrelated reasons — investigate them in parallel."*
- **Use case:** 3+ test files failing for different root causes, multiple independent broken
  subsystems, or several unrelated investigations at once.

## 7. test-driven-development  *(quality discipline)*
- **What it does:** Enforces write-test-first development.
- **How it functions:** **Iron Law — NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.**
  Write test → watch it fail (proves it tests the right thing) → write minimal code to pass →
  refactor. Wrote code first? Delete it, start over.
- **Steps to use:** Before writing any implementation code.
- **Try saying:** *"Implement the discount calculator using TDD."* (also auto-fires on "implement X")
- **Use case:** New features, bug fixes, refactoring, behavior changes. Exceptions
  (throwaway prototypes, generated code, config) require asking the user first.

## 8. systematic-debugging  *(quality discipline)*
- **What it does:** Forces root-cause analysis before any fix.
- **How it functions:** **Iron Law — NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**
  Phase 1 investigation must complete first. Techniques: root-cause tracing, defense-in-depth,
  condition-based waiting.
- **Steps to use:** Invoke the moment a bug/failure appears, before proposing fixes.
- **Try saying:** *"The login test started failing after my last change — debug it properly."*
- **Use case:** Any bug, test failure, unexpected behavior, perf/build/integration issue —
  especially under time pressure or after a failed fix.

## 9. verification-before-completion  *(quality discipline)*
- **What it does:** Blocks "it's done/fixed/passing" claims that lack fresh evidence.
- **How it functions:** **Iron Law — NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.**
  Gate: identify proving command → run the full command now → read full output + exit code →
  only then state the claim *with* evidence.
- **Steps to use:** Run right before committing, opening a PR, or telling the user something works.
- **Try saying:** *(auto-fires; or)* *"Verify this is actually fixed before you tell me it's done."*
- **Use case:** Treats unverified success claims as dishonesty, not efficiency.

## 10. requesting-code-review
- **What it does:** Dispatches a code-reviewer subagent to catch issues early.
- **How it functions:** Compute `BASE_SHA`/`HEAD_SHA`, dispatch a general-purpose subagent
  filled from the `code-reviewer.md` template with description, requirements, and SHA range.
- **Steps to use:** Invoke after a task/feature; provide the SHA range or let it compute one.
- **Try saying:** *"Get a code review of my changes before I merge."*
- **Use case:** Mandatory after each task in subagent-driven dev, after a major feature, and
  before merging to main. Optional when stuck or before refactoring.

## 11. receiving-code-review
- **What it does:** Governs how to process review feedback with technical rigor.
- **How it functions:** Read fully → restate the requirement → verify against the codebase →
  evaluate if it's sound *for this codebase* → respond (acknowledge or push back with reasoning) →
  implement one item at a time, testing each. **Forbidden:** "You're absolutely right!",
  "Great point!", implementing before verifying.
- **Steps to use:** Invoke whenever you receive review feedback.
- **Try saying:** *"Here's the review feedback — work through it carefully."* (paste the feedback)
- **Use case:** Especially when feedback seems unclear or technically questionable.

## 12. using-git-worktrees  *(isolation)*
- **What it does:** Ensures work happens in an isolated workspace.
- **How it functions:** Detect existing isolation first (with submodule guard) → prefer the
  platform's native worktree tooling → fall back to manual `git worktree` only if needed.
  "Never fight the harness."
- **Steps to use:** Invoke before starting isolated feature work or plan execution.
- **Try saying:** *"Set up an isolated worktree before we start this feature."*
- **Use case:** Keeping feature work isolated from your current workspace.

## 13. finishing-a-development-branch  *(integration)*
- **What it does:** Cleanly completes a branch once work is done.
- **How it functions:** Verify tests pass (stop if not) → detect environment → present
  structured options (merge / open PR / clean up) → execute the chosen workflow → clean up.
- **Steps to use:** Invoke when implementation is complete and tests are green.
- **Try saying:** *"Tests pass — wrap up this branch and open a PR."*
- **Use case:** Deciding how to integrate finished work. Called automatically at the end of
  the execution skills.

## 14. writing-skills  *(meta / authoring)*
- **What it does:** Guides creating, editing, and verifying skills — "TDD applied to process docs."
- **How it functions:** Write pressure-test scenarios with subagents → watch them fail without
  the skill (baseline RED) → write the SKILL.md → watch agents comply (GREEN) → refactor to close
  loopholes. Requires understanding the TDD skill; references Anthropic's skill-authoring best practices.
- **Steps to use:** Invoke when building or hardening your own reusable skills.
- **Try saying:** *"Create a new skill that captures our deployment checklist."*
- **Use case:** Authoring new skills or hardening existing ones before deployment.

---

## Extra Notes Worth Knowing

- **No slash commands.** Don't look for `/superpowers:*` — invoke skills by name or let hooks
  trigger them. Restart Claude Code after install so hooks/skills load.
- **Subagents dramatically improve quality.** Skills 5, 6, and 10 lean on subagents; on platforms
  without them, quality drops and you fall back to #4.
- **Artifacts are versioned in your repo:** specs under `docs/superpowers/specs/`, plans under
  `docs/superpowers/plans/` — design intent lives alongside code.
- **The "Iron Laws" are intentionally rigid** (TDD, debugging, verification). They resist
  rationalization under pressure; treat "skip just this once" as a red flag, and route genuine
  exceptions through the user.
- **Process skills before implementation skills.** When multiple skills apply: brainstorming /
  systematic-debugging decide HOW to approach; implementation skills guide execution.
  "Build X" → brainstorm first. "Fix bug" → systematic-debugging first.
- **Rigid vs. flexible:** Rigid skills (TDD, systematic-debugging) are followed exactly; flexible
  ones (patterns) adapt principles to context. The skill itself tells you which.
- **Cross-platform:** Superpowers also targets Codex, Copilot CLI, and Gemini CLI; per-platform
  tool references live in the `using-superpowers/references/` folder.
- **Personal skills** live in your runtime's skills dir (`~/.claude/skills/` for Claude Code;
  `~/.agents/skills/` is a cross-runtime alias).
