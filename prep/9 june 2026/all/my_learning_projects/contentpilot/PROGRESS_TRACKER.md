# ContentPilot — Progress Tracker

> Last updated: 2026-06-27
> Status: **Phase 1 MVP + Dashboard v2 Complete**

---

## What This File Is For

This is the single source of truth for what's been built, what's broken, and what's next.
If you're reading this as a new engineer, start here before touching any code.

---

## Overall Progress

| Phase | Description | Status |
|---|---|---|
| Phase 1 | CLI agent + basic dashboard | ✅ Complete |
| Dashboard v2 | Pipeline flow map + content display | ✅ Complete |
| Phase 2 | Hermes skill integration | ⏳ Not started (blocker: Hermes not configured) |
| Phase 3a | Workflow pipeline generator sub-agent | ⏳ Not started (needs design session) |
| Phase 3b | Multi-site adapter (Hugo, Gatsby, Astro) | ⏳ Not started |
| Phase 4 | Non-interactive CLI + scheduler + draft/approve workflow | ✅ Complete (2026-07-02). CLI flags (`--topics/--prompts/--workflows/--categories/--publish`), draft-by-default with `/drafts` approve/reject, APScheduler in the dashboard (`/schedule`), `/api/run-now`. Design change vs spec: push happens per-post with `push_status` tracked on each `PostEntry`, replacing the old end-of-run batch push. Manual verification still pending — see `NEXT_STEPS.md`. |

---

## What Has Been Built

### Core Layer (`core/`)

These are shared utilities that every other module depends on. Don't modify these without reading the tests first.

| Module | File | What It Does |
|---|---|---|
| Data Models | `core/models.py` | Pydantic v2 data models. `TopicResult` = one trending topic. `PostEntry` = one published post. `ManifestState` = the whole manifest. These are the shared "language" between all agents. |
| Config Loader | `core/config.py` | Reads `config.yaml` and validates it. Throws a `FileNotFoundError` if the file doesn't exist — so always run commands from the project root where `config.yaml` lives. |
| Manifest Manager | `core/manifest.py` | Reads and writes `manifest.json` — the database of every post ever published. Uses `filelock` to prevent two processes from writing at the same time (thread-safe). Supports: append a post, update a post's status, delete a post. |
| Run Log | `core/run_log.py` | **Added 2026-06-27.** Records function-level execution data into `run_log.json` after every `python main.py` run. Stores: which functions were called, how long each took, what they returned, and any errors. Keeps the last 20 runs. |

### Agent Layer (`agents/`)

Each agent does one specific job and has a `run()` method. This makes them easy to swap out.

| Agent | File | What It Does |
|---|---|---|
| TrendDiscovery | `agents/trend_discovery.py` | Fetches trending topics from up to 3 sources: Tavily (web search), Reddit (hot posts from configured subreddits), HackerNews (top stories). Deduplicates by title. Returns at most `n_topics` results. **Updated 2026-06-27:** Now stores per-source results in `self.source_results` so the orchestrator can log which sources succeeded or failed. |
| ContentGenerator | `agents/content_generator.py` | Takes a `TopicResult` and a type (`"prompt"` or `"workflow"`) and returns markdown with YAML frontmatter. Uses LangChain + Gemini 2.0 Flash. Prompt posts are 150–300 word AI prompts. Workflow posts are 4-step structured chains. |
| ImageGenerator | `agents/image_generator.py` | Generates a PNG image for prompt posts via Gemini Imagen 3. Saves the PNG into the target repo's `public/images/` folder. Uses a compatibility shim so tests can still mock the deprecated `google.generativeai` SDK. |
| GitPublisher | `agents/git_publisher.py` | Writes markdown files to the target repo, runs `git add` + `git commit`. The `push()` call at the end pushes all commits in one batch. Handles missing git remotes gracefully. |
| Orchestrator | `agents/orchestrator.py` | The coordinator. Calls all agents in order for each topic. **Updated 2026-06-27:** Now instruments every function call with timing and status using `core/run_log.py`. Saves a `RunLog` to `run_log.json` at the end of every run, even if some steps fail. |

### Interface Layer

| Component | File | What It Does |
|---|---|---|
| CLI | `main.py` | Entry point. Uses `typer` + `rich` for a styled terminal UI. Asks 4 questions, then kicks off `Orchestrator.run()`. |
| Dashboard server | `dashboard/server.py` | FastAPI web app. Reads `manifest.json` to serve the post list, and `run_log.json` to serve the pipeline page. Also serves images from the target repo's `public/` directory. |
| Templates | `dashboard/templates/` | Jinja2 HTML. Dark theme. No JS framework — all vanilla CSS and a few lines of `fetch()` for delete/re-push. |

### Dashboard Pages

| Page | Route | What It Shows |
|---|---|---|
| All Posts | `/` | Top: 4-step pipeline summary (Trend Discovery → Content Gen → Image Gen → Git Push) with status colors. Below: generated posts grouped by topic, each showing a content preview and image. |
| Pipeline | `/pipeline` | **Added 2026-06-27.** Full function call tree for the most recent run. Shows every function called, how long it took, what it returned, and the exact error message if it failed. Reads from `run_log.json`. |
| Post Detail | `/post/{slug}` | Full markdown content, image, source URL, git commit sha, delete and re-push buttons. |

---

## Files That Are Auto-Created at Runtime

You won't find these in the repo (they're in `.gitignore`), but the app creates them when it runs:

| File | Created by | What it contains |
|---|---|---|
| `manifest.json` | `core/manifest.py` via orchestrator | Every post ever published: slug, title, type, status, image path, commit SHA, source URL |
| `run_log.json` | `core/run_log.py` via orchestrator | Last 20 pipeline runs, with per-function timing and errors |
| `config.yaml` | You (copy from `config.yaml.example`) | Your settings: target repo path, API model, which sources are enabled |
| `.env` | You (copy from `.env.example`) | Your secret API keys — never commit this file |

---

## Test Coverage

```
38 tests passing, 0 failing
```

All external APIs (Gemini, Tavily, Reddit, HackerNews) are mocked. You can run the full test suite with no API keys:

```bash
PYTHONPATH=. .venv/bin/python -m pytest -v
```

| Test File | Tests | What It Covers |
|---|---|---|
| `tests/core/test_models.py` | 6 | Pydantic model validation, Literal enforcement, field defaults |
| `tests/core/test_config.py` | 6 | YAML loading, nested model parsing, FileNotFoundError on missing file |
| `tests/core/test_manifest.py` | 6 | Append, update status, delete, roundtrip, missing file handled |
| `tests/agents/test_trend_discovery.py` | 3 | Deduplication, n_topics limit, correct TopicResult shape |
| `tests/agents/test_content_generator.py` | 3 | Prompt markdown format, workflow step format, slug generation |
| `tests/agents/test_image_generator.py` | 2 | PNG written to disk, directory auto-created |
| `tests/agents/test_git_publisher.py` | 4 | Publish, delete, repush — uses a real temp git repo (no mock) |
| `tests/agents/test_orchestrator.py` | 2 | Post count, status=pushed with commit sha present |
| `tests/test_main.py` | 2 | CLI args correctly passed to Orchestrator.run() |
| `tests/dashboard/test_server.py` | 4 | GET /, GET /post/{slug}, DELETE /api/delete/{slug}, 404 handling |

> **Gap:** `core/run_log.py` and the `/pipeline` dashboard route have no tests yet — see Pending Work below.

---

## How to Run (Quick Reference)

```bash
cd my_learning_projects/contentpilot

# First time only: create venv and install deps
python3 -m venv --prompt venv .venv
source .venv/bin/activate.fish       # fish shell
pip install -r requirements.txt

# Configure (first time only)
cp config.yaml.example config.yaml   # edit: set target_repo to your Outflo path
cp .env.example .env                 # edit: add GEMINI_API_KEY at minimum

# Run the agent (generates and publishes posts)
PYTHONPATH=. python main.py

# Run the dashboard (separate terminal)
PYTHONPATH=. python dashboard/server.py
# → open http://localhost:8000

# Run tests (no API keys needed)
PYTHONPATH=. .venv/bin/python -m pytest -v
```

### Minimum viable setup (only Gemini key)

You don't need all 5 API keys to run. With only `GEMINI_API_KEY`:

1. Set `tavily: false` and `reddit.enabled: false` in `config.yaml`
2. Set `hackernews.enabled: true` (HackerNews needs no key)
3. Run `python main.py` — it will use HackerNews for topics and Gemini for content + images

---

## Pending Work

### Code Quality Cleanup (Option B — plan written 2026-06-27)

A full audit identified bugs, dead code, and code smells. Implementation plan:
`docs/superpowers/plans/2026-06-27-option-b-cleanup.md`

Issue tracking with reasoning: `decisions_and_issues.md`

- [ ] **Task 1 — Dead code removal:**
  - Remove `pydantic-settings` from `requirements.txt`
  - Remove duplicate `httpx` from `requirements.txt`
  - Delete `update_post()` from `core/manifest.py`
  - Remove `"pending"` from `PostEntry.status` Literal in `core/models.py`
  - Update `tests/core/test_manifest.py` accordingly
- [ ] **Task 2 — BUG: HackerNews exceptions silently swallowed** — remove inner `try/except` from `_fetch_hackernews()` in `agents/trend_discovery.py` so errors surface to the outer handler and show correctly on the pipeline dashboard
- [ ] **Task 3 — SMELL: `source_results` side-effect** — change `TrendDiscovery.run()` to return `(topics, source_results)` tuple instead of mutating `self.source_results`; update orchestrator and all trend discovery tests
- [ ] **Task 4 — BUG: ImageGenerator init crashes on startup in Ollama mode** — guard `self.image = ImageGenerator(...)` with `if provider == "google"` in `Orchestrator.__init__()`
- [ ] **Task 5 — SMELL: `_ImageGenerationModel` shim** — delete the 30-line wrapper class and monkey-patch from `agents/image_generator.py`; rewrite to use `google.genai.Client` directly; update test mocks

### Immediate (small, low risk)

- [ ] **Add tests for `core/run_log.py`** — create `tests/core/test_run_log.py`. Test: new_step, finish_step, append_run, load_run_log roundtrip, max 20 runs kept.
- [ ] **Add pipeline route to dashboard tests** — `tests/dashboard/test_server.py` should include `GET /pipeline` returning 200 with and without a run_log.json present.
- [ ] **Extend orchestrator tests** — after `orchestrator.run()`, assert that `run_log.json` was written and contains the expected structure.
- [ ] **Fix URL truncation bug** in `dashboard/templates/post.html` — currently truncates source URLs to 60 chars unconditionally, breaking short URLs.

### Medium (requires design decisions)

- [ ] **Migrate `google.generativeai` → `google.genai`** in `agents/image_generator.py`. The old SDK is end-of-life and will eventually stop receiving updates. Steps: (1) rewrite `ImageGenerator` to use `google.genai.Client` directly, (2) update the mock target in `tests/agents/test_image_generator.py` from `genai.ImageGenerationModel` to `google.genai.Client.models.generate_images`, (3) delete the `_ImageGenerationModel` shim class.
- [ ] **Dashboard image previews on the post grid** — the `/` page shows post cards but images only appear on the detail page. Add thumbnail images to the grid cards.
- [ ] **Dashboard bulk delete** — add checkboxes to post cards + a "Delete selected" button. Useful when a bad run generates 10 posts you want to clean up at once.
- [ ] **Dashboard category filter** — add a filter bar on `/` to show only `prompt` or `workflow` type posts, or filter by category.
- [ ] **Dashboard authentication** — currently the dashboard is open with no login. Fine for local use, but a risk if you ever expose it on a network. Add HTTP basic auth via FastAPI middleware.

### Future (Phase 2 / Phase 3)

- [ ] **Hermes Integration (Phase 2)** — wrap `main.py` as a Hermes skill so you can invoke ContentPilot from the Hermes TUI conversationally. **Blocker:** Hermes not yet configured — need to run `docker compose run --rm hermes setup` and add API keys first.
- [ ] **Workflow Pipeline Generator (Phase 3a)** — a dedicated sub-agent that takes a business goal ("generate leads for SaaS") and outputs a structured 6-step AI workflow post. This is a separate agent, not a tweak to the existing `ContentGenerator`. Needs its own design session.
- [ ] **Multi-Site Adapter (Phase 3b)** — right now `GitPublisher` writes files in Outflo's specific folder structure (`content/prompts/`, `content/workflows/`, `public/images/`). To support Hugo, Gatsby, Astro, or Jekyll, abstract this behind a site adapter. Config flag: `site_type: outflo | hugo | gatsby | custom`.
- [ ] **Scheduled runs** — add a cron/scheduler so `main.py` runs automatically (e.g., every Monday morning) without someone manually triggering it. Could use `crontab`, APScheduler, or GitHub Actions.
- [ ] **Outflo frontend updates** — Outflo's Next.js frontend was not updated to reflect agent-generated content patterns (no "AI generated" badge, no trending indicator, no category browse). This is separate work in the Outflo repo.

---

## Known Technical Debt

| Issue | File | Why It Exists | How to Fix |
|---|---|---|---|
| `google.generativeai` compatibility shim | `agents/image_generator.py` | The new `google.genai` SDK can't be patched easily by the existing tests, so a wrapper class was added to keep tests working without rewriting them | Rewrite `ImageGenerator` + update test mocks, then delete the shim |
| `datetime.utcnow()` in tests | `tests/` | Written before Python 3.12 deprecated `utcnow()` | Replace all `datetime.utcnow()` with `datetime.now(UTC)` |
| No test for `run_log.py` | `core/run_log.py` | Added after initial test suite was written | Write `tests/core/test_run_log.py` |
| No test for `/pipeline` route | `dashboard/server.py` | Same as above | Add test case in `tests/dashboard/test_server.py` |
| `httpx` listed twice | `requirements.txt` | Duplicate added accidentally | Remove one |

---

## Key Design Decisions (Why Things Are Built This Way)

If you're wondering why something was done a certain way, this table explains the reasoning.

| Decision | What We Did | Why |
|---|---|---|
| Standalone tool, not inside Outflo | ContentPilot lives in its own folder, points at Outflo via `config.yaml` | Makes it site-agnostic — it can target any git-backed site, not just Outflo |
| Python + LangChain | Used LangChain as the LLM wrapper | Swapping Gemini for Claude or GPT is one config line (`llm.provider`) — no code changes |
| Markdown output | Posts are written as `.md` files, not sent to an API | Matches Outflo's existing content format — no frontend changes needed, Vercel auto-deploys |
| Git commit (not a CMS API) | Content is committed directly to the git repo | Vercel watches the repo and auto-deploys on push — no webhook or CMS needed |
| Orchestrator + pluggable agents | Each agent has a standard `run()` interface | Easy to swap providers (e.g., replace Gemini with Claude just by changing the class) |
| FastAPI for dashboard | Lightweight Python web framework | No Node.js overhead — everything runs in the same Python venv |
| Jinja2 + inline CSS (no JS framework) | Templates with raw CSS | No build step, no `npm install`, no bundler — works anywhere Python runs |
| `run_log.json` separate from `manifest.json` | Pipeline execution data stored separately from post data | `manifest.json` is the record of published content. `run_log.json` is debug/observability data. Keeping them separate means you can delete run logs without affecting the content record. |
| Max 20 runs in run_log | `append_run()` keeps only the last 20 | Prevents `run_log.json` from growing unbounded on a server that runs daily |

---

## Git History

```
[2026-06-27] dashboard: pipeline function call tree + run logging
             - Added core/run_log.py (StepLog, RunLog, RunLogState models + file ops)
             - Instrumented agents/orchestrator.py to record every function call
             - Added source_results tracking to agents/trend_discovery.py
             - Added /pipeline route to dashboard/server.py
             - Added dashboard/templates/pipeline.html (function call tree with status/errors)
             - Redesigned dashboard/templates/index.html (pipeline stage overview + content cards)
             - Added static file serving for images in dashboard/server.py

[2026-06-25] Phase 1 MVP complete
             feat: FastAPI dashboard — post grid, detail, delete, re-push
             feat: CLI entry point (typer + rich)
             feat: Orchestrator — coordinates all agents
             feat: GitPublisher (GitPython)
             feat: ImageGenerator (Gemini Imagen)
             feat: ContentGenerator (LangChain + Gemini)
             feat: TrendDiscovery (Tavily + Reddit + HackerNews)
             feat: manifest manager, config loader, data models
```

---

## Docs

| Document | Path | Purpose |
|---|---|---|
| **README** | `README.md` | How to install, configure, and run ContentPilot |
| **This file** | `PROGRESS_TRACKER.md` | What's built, what's broken, what's next |
| **Decisions & Issues** | `decisions_and_issues.md` | Known bugs, dead code, code smells, and open design decisions with full reasoning |
| **Local LLM Setup** | `docs/LOCAL_LLM_SETUP.md` | How to run ContentPilot fully offline using Ollama + phi3:mini — hardware specs, installation, switching between local and cloud, troubleshooting |
| **Full Project Report** | `docs/CONTENTPILOT_FULL_REPORT.md` | Deep narrative — vision, architecture, all modules, data models |
| Design Spec | `docs/superpowers/specs/2026-06-25-contentpilot-design.md` | Original architecture and module breakdown |
| Phase 1 Implementation Plan | `docs/superpowers/plans/2026-06-25-contentpilot-implementation.md` | 11-task TDD plan that was used to build Phase 1 |
| Option B Cleanup Plan | `docs/superpowers/plans/2026-06-27-option-b-cleanup.md` | 5-task plan to fix bugs and remove dead code/smells identified in the 2026-06-27 audit |
