# ContentPilot — Next Steps

> Last updated: 2026-07-02 (implementation complete — only manual verification remains)
> Companion to `docs/superpowers/specs/2026-07-02-contentpilot-scheduling-drafts-design.md`
> (the design) and `decisions_and_issues.md` (bugs/decisions log — check there first if
> something below seems already fixed or contradicted by the code).

This file tracks what's **pending** for Phase 4 (non-interactive CLI + scheduler +
draft/approve workflow). It is a checklist, not a design doc — see the spec for reasoning.

---

## Already done (prep work, ahead of the implementation plan)

- [x] `PostEntry.status` updated to `Literal["draft", "published", "deleted", "failed"]`
      (`core/models.py`) — `"draft"` added, `"pushed"` renamed to `"published"` everywhere
      (orchestrator, dashboard server, templates, tests).
- [x] `GitPublisher.publish()` / `.delete()` fixed to use pathspec-scoped commits instead of
      committing the whole git index (BUG-3 in `decisions_and_issues.md`).
- [x] Regression test added: `test_publish_does_not_commit_unrelated_staged_changes`.
- [x] Full test suite passing (39/39) after both changes.
- [x] Design spec written and self-reviewed:
      `docs/superpowers/specs/2026-07-02-contentpilot-scheduling-drafts-design.md`.

---

## Pending — not yet implemented

### CLI
- [x] Add Typer options to `main.py`: `--topics`, `--prompts`, `--workflows`, `--categories`,
      `--publish`. No-flags path must keep today's interactive prompts working unchanged.
- [x] Validate flag values before any API call (non-negative ints, at least one valid category).
- [x] Document a cron / systemd-timer example in `README.md`.

### Draft/publish core
- [x] Add `drafts/` directory (git-ignored) as the default write target for `GitPublisher.publish()`
      when not in immediate-publish mode.
- [x] Implement `GitPublisher.publish_draft(slug)` — move draft file(s) into `target_repo`,
      pathspec-scoped commit, push, return commit SHA + push status.
- [x] Add `push_status: Literal["pushed", "failed", "no_remote"]` to `PostEntry`, populated by
      `GitPublisher` rather than inferred from the presence of a commit SHA (fixes the
      ambiguity described in `STORIES.md`, Story 4).
- [x] Reject flow: delete draft file(s) + manifest entry, no git operation against `target_repo`.

### Scheduling
- [x] Add `apscheduler` to `requirements.txt`.
- [x] Add `ScheduleConfig` Pydantic model to `core/models.py`, following the `PostEntry` /
      `ManifestState` pattern exactly.
- [x] Add `schedule.json` load/save in `core/`, reusing the `FileLock` pattern from
      `core/manifest.py`.
- [x] Wire `AsyncIOScheduler` into `dashboard/server.py` startup, reading `schedule.json`.
- [x] Ensure the scheduled/triggered `Orchestrator.run()` executes in a thread pool executor,
      not directly on the event loop (Orchestrator is synchronous — blocking the loop would
      freeze the dashboard for the duration of every run).

### Dashboard routes
- [x] `GET /drafts` — list pending drafts (reuse existing post-preview rendering).
- [x] `POST /drafts/{slug}/approve` (implemented as `/api/drafts/{slug}/approve`) — call `publish_draft()`.
- [x] `POST /drafts/{slug}/reject` (implemented as `/api/drafts/{slug}/reject`) — delete draft.
- [x] `POST /run-now` (implemented as `/api/run-now`) — trigger a pipeline run with user-supplied parameters, non-blocking.
- [x] `GET /schedule` + `POST /api/schedule` — view/edit recurring job config, enable/disable toggle.
- [x] Update `/`, `/pipeline`, `/post/{slug}` to surface `push_status` next to commit SHA.

### Tests
- [x] `tests/core/test_schedule.py` (new) — `ScheduleConfig` load/save round-trip + FileLock.
- [x] `tests/agents/test_git_publisher.py` — `publish_draft()` success + recoverable-failure cases.
- [x] `tests/core/test_manifest.py` — draft → published, draft → deleted transitions.
- [x] `tests/test_main.py` — flag-mode bypasses prompts; invalid flags fail fast.
- [x] `tests/dashboard/test_server.py` — `/drafts`, `/run-now`, `/schedule` routes (mocked).

### Manual verification (not automated — do before calling Phase 4 done)
- [x] One real cron-triggered run (verified 2026-07-05, flag-mode run produced draft only) (flags, no `--publish`) against a disposable target repo —
      confirm it produces drafts, not live commits, with zero keyboard interaction required.
- [x] One real dashboard-triggered run (verified 2026-07-05, /api/run-now -> draft -> approve -> commit 6cddea7): "Run Now" → review in `/drafts` → approve → confirm the
      commit lands in the disposable target repo and (if a remote exists) actually pushes.
- [x] One rejected draft (verified 2026-07-05, target repo untouched) — confirm the target repo is untouched.
- [x] Scheduled job registration verified (interval[1:00:00] from schedule.json); live interval fire not observed — _scheduled_run unit-tested. One scheduled run firing on its configured interval without manual intervention.

### Documentation (once the above is implemented)
- [x] Update `README.md`'s "Running the Agent" section with flag-mode usage.
- [x] Update `README.md`'s Project Structure tree to include `drafts/` and `schedule.json`.
- [x] Update `PROGRESS_TRACKER.md` Phase 4 row to ✅ Complete.
- [ ] Move resolved items out of this file (or mark this file superseded) once Phase 4 ships.

---

## Explicitly deferred (in the spec's Out of Scope, not forgotten — just not now)

- Multi-site adapters (Hugo, Gatsby, Astro) — Phase 3b
- Workflow pipeline generator sub-agent — Phase 3a
- Hermes skill integration — Phase 2
- Analytics/traffic feedback loop into topic selection
- Dashboard authentication
- Inline editing of draft content in the dashboard (reject-and-regenerate only)
