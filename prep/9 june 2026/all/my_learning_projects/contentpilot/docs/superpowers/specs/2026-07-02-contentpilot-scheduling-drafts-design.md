# ContentPilot — Phase 4: Non-Interactive Mode, Scheduling & Draft/Approve Workflow

> **Date:** 2026-07-02
> **Status:** Draft — architecture and data flow approved by user; error handling and testing
> sections drafted, pending final review before handoff to implementation planning.
> **Builds on:** `docs/superpowers/specs/2026-06-25-contentpilot-design.md` (Phase 1, approved
> and implemented). This spec assumes Phase 1's Orchestrator/Agent architecture as-is.
> **Related:** `decisions_and_issues.md` (bug/decision log), `STORIES.md` (motivating
> scenarios), `NEXT_STEPS.md` (pending implementation checklist).

---

## 1. Problem Statement

Phase 1 delivered a complete, working pipeline (trend discovery → content generation → image
generation → git publish), but two gaps stand between it and the automation the project's own
README promises:

1. **No non-interactive entry point.** `main.py` only knows how to ask four questions via
   `IntPrompt`/`Prompt`. It cannot be invoked from cron, systemd, or any headless scheduler —
   confirmed by testing (see `STORIES.md`, Story 1).
2. **No safety gate before publishing.** Every generated post goes straight from LLM output to
   a live git commit + push, with no review step. Confirmed as a real risk during manual
   testing: a local model (`phi3:mini`) produced a fully hallucinated post (a fake product
   "ZCode") that would have gone live unreviewed under a scheduled run (`STORIES.md`, Story 3).

A third issue was found and **already fixed** during testing, ahead of this spec: `GitPublisher`
was committing the entire git index rather than just the file it wrote, risking unrelated
staged changes being swept into a content commit and pushed. See `decisions_and_issues.md`,
BUG-3, and `STORIES.md`, Story 2. This spec's draft/approve design adds a second, independent
safety layer on top of that fix — the two are complementary, not redundant.

---

## 2. Goals

- Allow `main.py` to run fully non-interactively via CLI flags, so it can be invoked from cron
  or any external scheduler with zero keyboard input.
- Add a `draft` post status: scheduled/automated runs write to a local `drafts/` staging area
  by default, never touching the target repo, until a human approves them.
- Give the user one central control point — the existing FastAPI dashboard — to: view pending
  drafts and approve/reject them, trigger an on-demand run, and configure/enable a recurring
  scheduled run, without needing a separate cron entry or second process.
- Preserve today's behavior as an opt-in: `--publish` (CLI) or an auto-publish toggle
  (dashboard) skips the draft stage and publishes immediately, exactly as Phase 1 does today.
- Keep cron/systemd documented as a lightweight, dashboard-free alternative for headless setups.

### Out of Scope (this spec)

- Multi-site adapters (Phase 3b, unchanged, still not started)
- Workflow pipeline generator sub-agent (Phase 3a, unchanged)
- Hermes integration (Phase 2, unchanged)
- Analytics/traffic feedback loop into topic selection (noted as a future idea, not designed)
- Dashboard authentication (stays local-only, as in Phase 1)
- Editing draft content in the dashboard before approval (approve/reject only, no inline edit —
  if a draft is bad, reject it and let the next run try again, rather than hand-editing
  AI output through a web form)

---

## 3. Architecture

Three additions layered onto the existing Phase 1 structure. No existing module is rewritten.

```
main.py
  └── gains Typer options: --topics --prompts --workflows --categories --publish
      • No flags passed  → today's interactive prompts, unchanged
      • Any flag passed  → fully non-interactive run, suitable for cron

core/models.py
  └── PostEntry.status: Literal["draft", "published", "deleted", "failed"]
      (already updated 2026-07-02, ahead of this spec, see decisions_and_issues.md)
  └── new: ScheduleConfig(BaseModel) — same pattern as PostEntry/ManifestState

agents/git_publisher.py
  └── publish() writes to contentpilot/drafts/ instead of target_repo, when in draft mode
      (pathspec-scoped commit fix already applied — see BUG-3)
  └── new: publish_draft(slug) — moves a draft's file(s) from drafts/ into target_repo,
      commits (pathspec-scoped, same as publish()), pushes, returns commit SHA + push status

dashboard/server.py
  └── new: AsyncIOScheduler (APScheduler), started on app startup, reads schedule.json
  └── new route: GET/POST /drafts   — list pending drafts; approve/reject actions
  └── new route: POST /run-now       — trigger Orchestrator.run() in a thread pool executor
  └── new route: GET/POST /schedule  — view/edit recurring job config, enable/disable toggle
  └── existing routes (/,/pipeline,/post/{slug}) gain a push_status field per post,
      surfaced from GitPublisher instead of inferred from a commit SHA (Story 4 fix)
```

**Why the dashboard is the control point, not a separate scheduler process:** the user
explicitly asked for "a master control so that I can control it from a central point." The
dashboard is already the one thing meant to stay running and already owns post visibility;
adding the scheduler to the same FastAPI process means one thing to start, one place to look,
and one code path (`Orchestrator.run()`) regardless of what triggered it — CLI, button, or
timer. Cron remains available as a separate, simpler option for anyone who doesn't want to run
the dashboard at all.

---

## 4. Data Flow

**Non-interactive run:**
1. `main.py run --topics 2 --prompts 1 --workflows 1 --categories all` (no `--publish`)
2. `Orchestrator.run(...)` executes exactly as it does today through content/image generation
3. `GitPublisher.publish()` writes the file(s) into `contentpilot/drafts/` instead of
   `target_repo`, and the manifest entry is recorded with `status="draft"`
4. Nothing is committed or pushed to `target_repo`. Run ends. Dashboard's `/drafts` shows the
   new entries.

**Approval:**
5. Dashboard `/drafts` lists pending entries with content preview + image, same rendering as
   today's post detail page.
6. **Approve** → `GitPublisher.publish_draft(slug)`: move file from `drafts/` into
   `target_repo`, pathspec-scoped commit, push, update manifest `status="published"` and
   `push_status`.
7. **Reject** → delete the draft file(s) + manifest entry. No git operation on `target_repo`
   occurs at any point for a rejected draft.

**Immediate publish (opt-in, unchanged from Phase 1):**
- `--publish` flag or dashboard auto-publish toggle → `GitPublisher.publish()` targets
  `target_repo` directly, skipping the `drafts/` staging step entirely. Manifest status goes
  straight to `"published"`. This is today's Phase 1 behavior, preserved as an explicit choice.

**Scheduled run:**
- `schedule.json` (validated via `ScheduleConfig`, protected by the same `FileLock` pattern
  `manifest.json` uses) holds `{enabled, interval_hours, topics, prompts, workflows,
  categories, publish}`.
- Dashboard `/schedule` page edits this file. `AsyncIOScheduler` re-reads it and fires
  `Orchestrator.run(...)` in a thread pool executor (see Section 5 — must not block the event
  loop) at the configured interval, using the same draft/publish logic as any other trigger.

---

## 5. Error Handling

- **Scheduled run failures do not crash the dashboard or disable the schedule.** Exceptions
  are caught at the job level, logged into `run_log.json` (existing per-function error
  tracking, already built), and the next scheduled run still fires normally. No retry loop.
- **Push status is tracked explicitly, not inferred from a commit SHA.** `GitPublisher`
  distinguishes "committed locally" from "pushed to remote" and records
  `push_status: "pushed" | "failed" | "no_remote"` on the `PostEntry`. The dashboard shows this
  next to the commit SHA so success messaging can't be misread as "it's live" when it isn't —
  directly fixes the ambiguity in Story 4.
- **Draft approval is idempotent and non-destructive on failure.** If `publish_draft()` fails
  partway (e.g., commit succeeds but push fails), the entry stays in a recoverable state with
  the error surfaced in the dashboard and a retry action — never silently disappears, never
  double-commits on retry.
- **CLI flags are validated before any network/API call.** `n_topics`, `n_prompts`,
  `n_workflows` must be non-negative integers; `categories` must resolve to at least one known
  category. Fails fast with a clear message — no wasted API quota on a malformed invocation.

---

## 6. Testing Strategy

Extends the existing pattern: pytest, all externals mocked, no live API calls in the suite.

| Area | File | New coverage |
|---|---|---|
| Draft status transitions | `tests/core/test_manifest.py` | draft → published, draft → deleted (reject) |
| Draft publish/reject | `tests/agents/test_git_publisher.py` | `publish_draft()` success, push failure leaves state recoverable |
| Regression (already added) | `tests/agents/test_git_publisher.py` | `test_publish_does_not_commit_unrelated_staged_changes` — BUG-3 fix |
| Non-interactive CLI | `tests/test_main.py` | flags bypass prompts; invalid flag values fail fast |
| Dashboard: drafts | `tests/dashboard/test_server.py` | `/drafts` list, approve, reject routes |
| Dashboard: run-now | `tests/dashboard/test_server.py` | triggers Orchestrator (mocked), returns immediately (non-blocking) |
| Dashboard: schedule | `tests/dashboard/test_server.py` | `/schedule` GET/POST, persists via `ScheduleConfig` |
| Schedule config | `tests/core/test_schedule.py` (new) | load/save round-trip, FileLock behavior, matches `manifest.json` pattern |

**Manual verification (not automated, tracked in `NEXT_STEPS.md`):** one real end-to-end run
triggered via cron with `--publish` omitted (confirms draft path), and one real run triggered
via the dashboard's "Run Now" + manual approval through `/drafts` (confirms the full approval
loop against a disposable target repo, per the scratchpad-testing pattern documented in
`README.md`).

---

## 7. Decisions Log (summary — full detail in `decisions_and_issues.md`)

- **`schedule.json` follows the `manifest.json` pattern exactly** (Pydantic `BaseModel` +
  `FileLock`) rather than introducing a new config library — see README's "Design Standards for
  New Features."
- **APScheduler (`AsyncIOScheduler`), in-process with the FastAPI dashboard** — not Celery, not
  a separate scheduler service. Justified by single-user, local-tool scope.
- **`PostEntry.status` renamed `"pushed"` → `"published"`, `"draft"` added** — done ahead of
  this spec (2026-07-02) so the status vocabulary only changes once. Full suite (39 tests)
  green after the rename.
- **Draft approval has no inline-edit step** — deliberately out of scope; a bad draft is
  rejected, not patched through the UI, keeping the dashboard simple.
