# Design Spec — Prompt Regression Suite Project Report

**Date:** 2026-06-23
**Author:** Claude Code (brainstorming skill)
**Deliverable:** `PROJECT_REPORT.md` in the project root
**Approach:** Layered Briefing — plain English opening, progressively technical, single document, mixed audience

---

## Document Identity

- **Title:** Prompt Regression Suite — Project Report
- **Subtitle:** A technical and contextual account of design, motivation, and implementation
- **Author:** Jaya Arun Kumar Tulluri — v1.0, June 2026
- **Format:** Markdown (`PROJECT_REPORT.md`)
- **Tone:** Plain English first, deepening technically; no jargon left unexplained in Sections 1–3
- **Length:** ~2,800–3,400 words

---

## Abbreviation Expansion List

Each abbreviation is expanded on its **first use only**, in the form `Full Term (ABBR)`. Never re-expand later.

| Abbreviation | Full form | First used in |
|---|---|---|
| LLM | Large Language Model | Section 1 |
| CI/CD | Continuous Integration / Continuous Delivery | Section 1 |
| API | Application Programming Interface | Section 1 |
| PRS | Prompt Regression Suite | Section 1 |
| PR | Pull Request | Section 2 |
| YAML | YAML Ain't Markup Language | Section 3 |
| ORM | Object-Relational Mapper | Section 5 |
| CLI | Command-Line Interface | Section 7 |
| UI | User Interface | Section 7 |

---

## Section Specifications

### Section 1 — Executive Summary
**Audience:** Non-technical (executives, compliance, recruiters)
**Length:** 150–200 words
**Content:**
- One-paragraph plain-English description: automated behavioral testing for LLM prompts; every time a developer edits a prompt and opens a pull request, the suite runs tests and blocks the merge if quality drops
- The tagline "pytest for prompts"
- Three capability highlights: tiered assertion engine, CI/CD deployment gate, visual regression dashboard
- Zero-server local setup (SQLite); free-tier LLM support via Ollama
- Abbreviations introduced: LLM, CI/CD, API, PRS

---

### Section 2 — Problem & Motivation
**Audience:** All
**Length:** 300–400 words
**Content:**
- The invisible failure mode: a prompt change deploys cleanly — unit tests pass, types check, CI is green — and something quietly breaks in production weeks later
- Three real-world examples: (1) the model starts giving shorter answers; (2) it stops citing sources properly; (3) a provider silently updates their base model, changing baseline behaviour
- Why traditional software testing misses all three: unit tests check logic, not LLM output; type checkers verify signatures, not meaning; integration tests rarely cover prompt semantics
- Why ad-hoc alternatives fall short: manual spot-checking does not scale; one-off eval scripts are not version-controlled or integrated into CI
- The specific gap PRS fills: prompts treated as first-class software artifacts — version-controlled, automatically tested on every PR, blocked before reaching users
- Abbreviation introduced: PR

---

### Section 3 — How It Works (Plain English)
**Audience:** Non-technical / general
**Length:** 350–450 words
**Content:**
- The "automated QA inspector" analogy: instead of checking whether code compiles, PRS checks whether a prompt still behaves the way you specified
- The YAML test file as a "behaviour contract": a developer writes down what they expect the model to do, in plain language, alongside specific checks
- The four-step pipeline in plain prose:
  1. **Write** — developer writes a YAML test file specifying expected prompt behaviour
  2. **Commit** — developer edits the prompt file and opens a pull request
  3. **Run** — CI detects which tests apply to the changed prompt and runs them automatically
  4. **Gate** — if scores drop below the stored baseline, the PR is blocked with a comment explaining what regressed and by how much
- What the three checking tiers mean to a non-technical reader: instant rule checks first (free, like a spellchecker), meaning-based similarity second (local, free, checks if the answer is semantically close to a reference), AI judge last (paid, only when the first two pass)
- Walk through the `qa_citation.prompt-test.yaml` example: the financial analyst prompt must mention "billion", "revenue", and "growth"; must not use speculative language like "might" or "I think"; must stay under 200 words; and must semantically resemble a reference answer at a similarity score ≥ 0.72
- Abbreviation introduced: YAML

---

### Section 4 — System Architecture
**Audience:** Engineers / technical reviewers
**Length:** 400–500 words
**Content:**

**Module map table** (path | responsibility):

| Module | Responsibility |
|---|---|
| `src/config.py` | Central Pydantic settings; single source of truth, loaded once at startup |
| `src/registry.py` | Discovers `*.prompt-test.yaml` files; parses via Pydantic; builds reverse index (prompt file → test case IDs) |
| `src/runner.py` | Async test orchestration; `asyncio.Semaphore` caps concurrency; multi-run averaging; baseline comparison |
| `src/change_detector.py` | Calls `git diff --name-only` to identify changed prompt files; used by CI for selective execution |
| `src/models/test_case.py` | Pydantic v2 `TestCase` and `AssertionConfig` schemas; `model_validator` enforces invariants at parse time |
| `src/models/result.py` | `TestResult` (per-case scores + assertion breakdown) and `SuiteRun` (suite-level summary) |
| `src/assertions/engine.py` | Orchestrates assertion tier order; fail-fast on rule failures; weighted mean aggregation |
| `src/assertions/rule_based.py` | 12 deterministic assertion handlers; zero API cost; runs first |
| `src/assertions/semantic.py` | `all-MiniLM-L6-v2` sentence-transformer; cosine similarity; module-level singleton via `lru_cache` |
| `src/assertions/judge.py` | LLM-as-judge; 4-dimension structured rubric; anti-self-bias routing; recomputes weighted overall client-side |
| `src/llm/factory.py` | Routes by model-name prefix: `claude-*` → Anthropic; `gpt-*/o1/o3/o4` → OpenAI; else → Ollama |
| `src/llm/anthropic_client.py` | Anthropic SDK wrapper; standardised `LLMResponse` contract |
| `src/llm/openai_client.py` | OpenAI SDK wrapper; same contract |
| `src/llm/ollama_client.py` | `httpx`-based Ollama client; zero-cost local execution |
| `src/storage/database.py` | SQLAlchemy 2.0 async engine + session factory; SQLite default, PostgreSQL via env swap |
| `src/storage/orm_models.py` | Four ORM tables: `test_cases`, `test_runs`, `test_results`, `baselines` |
| `src/storage/baseline_manager.py` | Three-rule baseline update policy; score history queries; regression feed for dashboard |
| `src/api/app.py` | FastAPI application root |
| `src/api/routers/runs.py` | REST endpoints for suite run history |
| `src/api/routers/baselines.py` | REST endpoints for baseline read/write/reset |
| `src/api/routers/test_cases.py` | REST endpoints for test case registry |
| `dashboard/app.py` | Streamlit dashboard; reads DB directly (no FastAPI dependency); 5 views |
| `cli.py` | Typer CLI; `prs run`, `prs validate`, `prs serve`, `prs baselines update/reset` |
| `ci/detect_affected.py` | CI entry point: detects affected test cases from git diff |
| `ci/run_suite.py` | CI entry point: runs suite and writes `ci_results.json` |
| `ci/post_comment.py` | Posts per-test regression breakdown as GitHub PR comment |

**Core processing flow:**
```
Registry (YAML discovery) → Runner (async orchestration)
  → AssertionEngine (tier evaluation) → BaselineManager (delta comparison)
  → SuiteRun (aggregated results) → Storage (persistence)
```

**Two GitHub Actions workflows:**
- `pr-regression.yml` — triggers on `prompts/**` or `tests/**/*.yaml` changes; runs detect → suite → comment → fail-if-regressions
- `weekly-drift.yml` — every Monday 09:00 UTC; full suite on `main`; Slack webhook alert

---

### Section 5 — Core Technical Components
**Audience:** Engineers
**Length:** 500–700 words
**Content — five subsections:**

**5.1 Three-Tier Assertion Engine**
- Assertions sorted by cost before execution: rule-based (tier 0) → semantic similarity (tier 1) → LLM judge (tier 2)
- Fail-fast: if any rule-based assertion fails, remaining tiers are skipped (marked as skipped, not failed)
- 12 rule-based types: `contains_keyword`, `not_contains`, `max_words`, `min_words`, `valid_json`, `json_contains_key`, `starts_with`, `not_starts_with`, `language_is`, `regex_match`, `response_time_under`, `reading_level` (Flesch–Kincaid score range)
- Final score: weighted mean across all assertion results that ran; each assertion carries a configurable `weight`
- Estimated cost saving: ~50% — rule and semantic checks eliminate the majority of judge calls

**5.2 LLM-as-Judge**
- Judge prompt enforces JSON-only output (no preamble) to prevent silent parser failures at scale
- Four scoring dimensions: `instruction_following` (weight 0.40), `factual_accuracy` (0.30), `format_compliance` (0.20), `tone_appropriateness` (0.10)
- Anti-self-bias routing: `claude-*` test model → OpenAI judge; `gpt-*` test model → Anthropic judge; enforced in `factory.py` by model-name prefix
- Judge runs at `temperature=0.0` for deterministic scoring; weighted overall recomputed client-side (model's arithmetic not trusted)
- `critical_failure` flag: true if any single dimension scores below 0.40
- `regression_risk` field: "low" | "medium" | "high" — surfaced in dashboard and PR comment

**5.3 Multi-Run Averaging & Flakiness Detection**
- Each test case runs `run_count` times (default 3) at `temperature=0.7` (configurable)
- Scores are averaged across runs; standard deviation > `flakiness_std_threshold` (default 0.05) flags the test case as flaky
- Regression is declared when `mean_score − baseline_score < −delta_threshold` (default −0.05)
- Delta-based comparison means absolute score levels do not matter — only score drops relative to the stored baseline

**5.4 Registry & Change Detection**
- `Registry` glob-walks `tests/` for `*.prompt-test.yaml`; parses each via Pydantic v2; validation errors surface at load time, not during a test run
- Reverse index: maps each `prompt_template` path to the list of test case IDs that reference it
- `Registry.affected_by(changed_files)` returns only matching test cases; powers selective CI execution
- 30% heuristic: if more than 30% of all prompt files changed, `Registry.should_run_full_suite()` returns True — catches systemic refactors
- `TestCase.id` is derived from `file_path.stem + "::" + name` — stable across renames of the YAML file if the name field is unchanged
- Abbreviation introduced: ORM

**5.5 Storage & Baseline Policy**
- Four async SQLAlchemy ORM tables: `test_cases` (registry), `test_runs` (suite-level header), `test_results` (per-case scores, assertion breakdowns, regression flags), `baselines` (per-test-case score + reason + commit SHA)
- Three-rule baseline update policy: Rule 1 — auto-update on every merge to `main`; Rule 2 — PR runs never update baselines; Rule 3 — forced resets require a non-empty documented reason (stored as audit trail)
- `BaselineManager.force_reset()` raises `ValueError` if reason is empty, making undocumented resets impossible via the API or CLI
- SQLite default (`sqlite:///./regression_suite.db`); PostgreSQL via one env var change (`DATABASE_URL=postgresql+asyncpg://...`)
- Score history (`get_score_history`) and regression feed (`get_recent_regressions`) power the Streamlit dashboard without going through the FastAPI layer

---

### Section 6 — CI/CD Integration
**Audience:** Compliance + engineers
**Length:** 200–250 words
**Content:**
- `pr-regression.yml` triggers only on changes to `prompts/**` or `tests/**/*.yaml` (not on every commit)
- Four-step CI sequence: `detect_affected.py` (git diff → affected test case list) → `run_suite.py` (executes suite, writes `ci_results.json`) → `post_comment.py` (posts per-test score table + delta + judge verdict to the PR) → exit-code gate (non-zero exit if `has_regressions == true`)
- `continue-on-error: true` on the suite step — results are collected even if regressions are detected, so the comment always posts before the gate fires
- PR results artifact retained for 30 days; weekly drift results retained for 90 days
- `weekly-drift.yml` runs the full suite every Monday at 09:00 UTC; Slack webhook posts emoji-coded severity: green circle (0 regressions), yellow (1–3), red (>3); worst-regressing test named in the message
- Environment variables needed in GitHub Secrets: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GITHUB_TOKEN`, `SLACK_WEBHOOK_URL` (optional)

---

### Section 7 — Usage Guide
**Audience:** Engineers, practitioners
**Length:** 300–400 words
**Content:**

**Prerequisites:**
- Python 3.11 or higher
- At least one of: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or a running Ollama instance

**Install:**
```bash
git clone <repo-url>
cd prompt-regression-suite
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your API keys
```

**Write a test case** (annotated YAML):
```yaml
name: "My prompt — expected behaviour description"
prompt_template: "prompts/my_prompt.txt"        # relative path to prompt file
variables:
  input: "The user's input text goes here"       # {{input}} is substituted in the prompt
expected_behavior: >
  Response must do X, avoid Y, and stay under Z words.
run_count: 3          # number of runs to average (reduces temperature noise)
delta_threshold: 0.05 # regression fires if mean score drops by more than this
assertions:
  - type: contains_keyword
    keywords: ["required", "term"]
    weight: 1.0
  - type: max_words
    limit: 200
    weight: 0.5
  - type: llm_judge
    threshold: 0.80
    weight: 2.0
tags: [my-domain, high-priority]
```

**Key CLI commands:**
```bash
prs validate                          # parse all YAMLs; report schema errors (no API cost)
prs run                               # run all test cases
prs run --affected                    # run only cases affected by git changes
prs run --tag financial               # filter by tag
prs run --update-baselines \
  --commit-sha $(git rev-parse HEAD)  # accept current scores as new baselines
prs baselines reset <id> \
  --score 0.85 --reason "Intentional tone change per product decision"
```

**Interfaces:**
```bash
streamlit run dashboard/app.py        # http://localhost:8501 — five views
prs serve --reload                    # http://localhost:8000/docs — FastAPI Swagger UI
```

**Five dashboard views:** Health Overview (headline metrics + 30-day heatmap), Regression History (filterable event feed with judge verdicts), Score Trends (per-test time series + 7-day rolling average + baseline line), Model Comparison (score distribution per prompt + score-vs-latency scatter), Baselines (table + force-reset form with required reason).

Abbreviations introduced: CLI, UI

---

### Section 8 — Tech Stack & Key Design Decisions
**Audience:** Portfolio / recruiters / engineers
**Length:** 300–400 words
**Content:**

**Tech stack table:**

| Layer | Technology | Reason chosen |
|---|---|---|
| Language | Python 3.11 | `asyncio` improvements; `TaskGroup`; match statements |
| CLI | Typer + Rich | Declarative commands; coloured terminal tables without manual formatting |
| API framework | FastAPI + Uvicorn | Async-native; automatic OpenAPI docs; minimal boilerplate |
| LLM clients | Anthropic SDK, OpenAI SDK, httpx (Ollama) | Official SDKs for managed providers; httpx for local Ollama (no SDK needed) |
| Embeddings | `all-MiniLM-L6-v2` via sentence-transformers | 80 MB, runs locally, no API cost; 384-dimensional cosine similarity sufficient for regression detection |
| Data validation | Pydantic v2 | Zero-cost validation at parse time; `model_validator` enforces invariants; YAML → typed model in one call |
| Database | SQLite → PostgreSQL | SQLite for zero-setup local dev; one env-var swap to PostgreSQL for production |
| ORM | SQLAlchemy 2.0 async | Async session support; same ORM models work with both SQLite and PostgreSQL |
| Dashboard | Streamlit + Plotly | Rapid data dashboard; reads DB directly without API server dependency |
| Language detection | langdetect | Optional import; graceful skip if not installed |
| Readability scoring | textstat | Flesch–Kincaid score for `reading_level` assertion; pure Python, no model needed |

**Five non-obvious design decisions:**

1. **Tiered assertion engine for ~50% cost reduction.** Rule-based and semantic checks gate the expensive judge call. A test that fails `valid_json` or word-count limits never triggers an Anthropic or OpenAI API call.

2. **Anti-self-bias judge routing.** A model cannot reliably score its own outputs — it is biased toward confirming its own style and reasoning. The factory routes by model-name prefix so Claude tests are always judged by OpenAI and vice versa.

3. **Multi-run averaging instead of fixed thresholds.** Single-run scores at `temperature=0.7` are too noisy to be reliable regression signals. Averaging across `run_count` runs and measuring deltas (not absolute values) makes detection statistically robust with a <5% flakiness target.

4. **Three-rule baseline update policy.** The policy balances two competing needs: baselines must advance with genuine improvements (so they stay useful), but they must not silently absorb regressions (so they stay trustworthy). PR runs never update baselines; forced resets require a documented reason to create an audit trail.

5. **Registry reverse index + 30% heuristic for selective CI.** The reverse index limits CI to only the test cases affected by changed prompt files — a PR touching 3 of 80 prompt files runs ~12 tests, not 80. The 30% threshold catches systemic refactors that touch many files at once, falling back to the full suite.

---

## Out of Scope

- API reference documentation (FastAPI auto-generates this at `/docs`)
- Automated unit/integration test suite for PRS itself (none exists in the current codebase)
- Deployment guide for hosted PostgreSQL (depends on provider)
- Prompt engineering guidance (use case-specific)

---

## File Output

- **Path:** `/media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`
- **Commit:** No — write file only, per user instruction (do not git add or commit)
