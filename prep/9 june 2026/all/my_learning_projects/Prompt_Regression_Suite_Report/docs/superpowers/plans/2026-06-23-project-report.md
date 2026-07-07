# Prompt Regression Suite — Project Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write `PROJECT_REPORT.md` in the project root — a complete, 8-section layered briefing document covering what the Prompt Regression Suite is, why it was built, and how it works technically.

**Architecture:** Single Markdown file written section by section. Each task writes one section and verifies its word count. A final review task audits the complete document for abbreviation discipline, word count, and cross-section consistency.

**Tech Stack:** Markdown, shell word count (`wc -w`), grep for abbreviation verification.

## Global Constraints

- Output file: `PROJECT_REPORT.md` at `/media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`
- Do NOT run `git add` or `git commit` at any point — write file only, per explicit user instruction
- Total document word count: 2,800–3,400 words
- Layered Briefing format: Sections 1–3 plain English, Sections 4–8 progressively technical
- Abbreviations expand on **first use only**, in the form `Full Term (ABBR)`. Never re-expand in subsequent sections
- Abbreviation assignment (must not appear expanded earlier than this section):
  - Section 1: LLM, CI/CD, API, PRS
  - Section 2: PR
  - Section 3: YAML
  - Section 5: ORM
  - Section 7: CLI, UI
- All technical values must be sourced from actual project code, not guessed
- Footer line on final document: `*Report generated: 2026-06-23 | Author: Jaya Arun Kumar Tulluri | Project version: 1.0.0*`
- Author line in document header: `Jaya Arun Kumar Tulluri — v1.0, June 2026`

---

### Task 1: Document scaffold + Section 1 (Executive Summary)

**Files:**
- Create: `PROJECT_REPORT.md`

**Section word target:** 150–200 words

- [ ] **Step 1: Write the file with document header and Section 1**

Write exactly the following content to `PROJECT_REPORT.md`:

```markdown
# Prompt Regression Suite — Project Report

*A technical and contextual account of design, motivation, and implementation*

**Author:** Jaya Arun Kumar Tulluri — v1.0, June 2026

---

## 1. Executive Summary

The Prompt Regression Suite (PRS) is an automated behavioral testing framework for Large Language Model (LLM) prompts — "pytest for prompts." Just as unit tests verify that code changes do not break software functionality, PRS verifies that prompt changes do not silently degrade the quality, tone, or structure of model responses.

Every time a developer edits a prompt file and opens a pull request, PRS automatically runs behavioral tests against the updated prompt and blocks the merge if quality drops. Three capabilities define the system: a tiered assertion engine that checks model responses against expected behaviors; a Continuous Integration / Continuous Delivery (CI/CD) deployment gate integrated with GitHub Actions; and a visual regression dashboard for tracking quality trends over time.

The tool supports Anthropic, OpenAI, and local Ollama models and exposes a REST Application Programming Interface (API) for programmatic access. The default setup requires no Docker, no cloud database, and no additional infrastructure — only Python 3.11 and an API key. PRS is designed for engineering teams shipping LLM-powered features who need prompt changes reviewed with the same rigor as code changes.
```

- [ ] **Step 2: Verify word count**

Run: `wc -w /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: Section 1 body is approximately 160–175 words (file total will be higher including headers).

- [ ] **Step 3: Verify abbreviation placement**

Run: `grep -n "Large Language Model\|Continuous Integration\|Application Programming Interface\|Prompt Regression Suite" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: All four expansions appear exactly once, all in Section 1.

---

### Task 2: Section 2 (Problem & Motivation)

**Files:**
- Modify: `PROJECT_REPORT.md` (append)

**Section word target:** 300–400 words

- [ ] **Step 1: Append Section 2 to PROJECT_REPORT.md**

Append exactly the following content (starting with a blank line after the current end of file):

```markdown

---

## 2. Problem & Motivation

Every engineering team shipping LLM-powered features eventually encounters the same invisible failure mode: a prompt change deploys cleanly. Unit tests are green, type checks pass, the CI pipeline reports success — and then something quietly breaks in production, discovered only through user complaints two or three weeks later.

Three failure modes recur across teams:

**The silent shortening.** A developer refactors a verbose system prompt to be more concise. The new prompt is cleaner, the tests still pass, and the model starts giving shorter, less detailed answers. No alert fires. Quality degrades invisibly.

**The citation drop.** A financial analyst prompt is updated to add a new instruction. The model, now attending to the new instruction, stops reliably citing sources it previously cited. Customer-facing summaries become unverified assertions. Nothing in the pipeline noticed.

**The model drift.** An AI provider silently updates their base model between API versions. Behavior that worked reliably for months shifts. Response tone changes, output length drifts, structured output keys appear in a different order. There was no code change — the problem arrived through the API.

None of these failures appear in traditional software tests. Unit tests verify logic, not LLM output. Type checkers verify signatures, not meaning. Integration tests rarely cover prompt semantics. And the failure is non-deterministic: the model does not always break; it becomes less reliable on average.

Existing alternatives fall short in different ways. Manual spot-checking does not scale past a handful of prompts. Ad-hoc evaluation scripts are not version-controlled, not integrated into CI, and not comparable across releases. Paid evaluation platforms require sensitive data to leave the organization.

The gap PRS fills: prompts treated as first-class software artifacts. Each prompt file gets a behavioral test suite defined in a version-controlled configuration file. Every Pull Request (PR) that modifies a prompt triggers those tests automatically. If scores drop below the stored baseline, the PR is blocked — before the change reaches users.
```

- [ ] **Step 2: Verify word count**

Run: `wc -w /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: Section 2 body is approximately 300–360 words. Running file total roughly 480–560 words.

- [ ] **Step 3: Verify PR expansion**

Run: `grep -n "Pull Request" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: Exactly one match, in Section 2.

---

### Task 3: Section 3 (How It Works — Plain English)

**Files:**
- Modify: `PROJECT_REPORT.md` (append)

**Section word target:** 350–450 words

- [ ] **Step 1: Append Section 3 to PROJECT_REPORT.md**

Append exactly the following content:

```markdown

---

## 3. How It Works (Plain English)

Think of PRS as an automated quality inspector for AI responses. Instead of checking whether code compiles or functions return the right type, it checks whether a prompt still makes the model behave the way the team specified.

The starting point is a YAML Ain't Markup Language (YAML) test file. A developer writes this file alongside their prompt to describe, in plain language and specific checks, exactly what a good response looks like. The financial analyst test case bundled with the project illustrates this clearly: the prompt asks for a summary of Apple's Q3 2024 revenue drivers. The test file specifies that a good response must contain the words "billion," "revenue," and "growth"; must not use speculative phrases like "might" or "I think"; must stay under 200 words; and must be semantically similar to a reference answer at a similarity score of at least 0.72.

With the test file written, the four-step pipeline runs automatically on every prompt change:

1. **Write** — a developer writes or updates a YAML test file next to their prompt, defining expected behavior and the checks to enforce it.
2. **Commit** — the developer edits the prompt file and opens a pull request against the main branch.
3. **Run** — GitHub Actions detects which prompts changed and runs only the test cases that reference those prompts, not the full suite.
4. **Gate** — if any test's score drops more than 0.05 below its stored baseline, the pull request is blocked and GitHub posts an automated comment naming the regressed test, its current score, its baseline, and the judge's one-line verdict.

What makes PRS efficient is how checking is structured. Three tiers run in order of cost:

**Tier 1 — Rule-based checks (free, instant).** Does the response contain required keywords? Does it avoid forbidden phrases? Is the word count within bounds? Is the output valid JSON? These checks are deterministic and cost nothing.

**Tier 2 — Semantic similarity (local, free).** A small local model — 80 megabytes on disk — compares the meaning of the response to a reference answer using cosine similarity. No API call, no cost.

**Tier 3 — AI judge (paid, only when needed).** Only if the first two tiers pass does PRS call an external AI model to evaluate the response on four dimensions: instruction-following, factual accuracy, format compliance, and tone. To avoid self-scoring bias, the judge is always a different provider than the model being tested.

A test that fails a rule check never reaches the AI judge — keeping evaluation costs low across large test suites.
```

- [ ] **Step 2: Verify word count**

Run: `wc -w /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: Section 3 body approximately 370–420 words. Running file total roughly 870–990 words.

- [ ] **Step 3: Verify YAML expansion**

Run: `grep -n "YAML Ain't Markup Language" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: Exactly one match, in Section 3.

---

### Task 4: Section 4 (System Architecture)

**Files:**
- Modify: `PROJECT_REPORT.md` (append)

**Section word target:** 400–500 words

- [ ] **Step 1: Append Section 4 to PROJECT_REPORT.md**

Append exactly the following content:

```markdown

---

## 4. System Architecture

PRS is organized into six clearly bounded layers: test discovery, async orchestration, assertion evaluation, LLM communication, storage, and interfaces. The table below maps every module to its responsibility.

| Module | Responsibility |
|---|---|
| `src/config.py` | Central Pydantic settings; single source of truth loaded once at startup via `lru_cache` |
| `src/registry.py` | Discovers `*.prompt-test.yaml` files; parses via Pydantic v2; builds reverse index (prompt file → test case IDs) |
| `src/runner.py` | Async test orchestration; `asyncio.Semaphore` caps concurrency; multi-run averaging; baseline comparison |
| `src/change_detector.py` | Calls `git diff --name-only` to identify changed prompt files for selective CI execution |
| `src/models/test_case.py` | Pydantic v2 `TestCase` and `AssertionConfig` schemas; `model_validator` enforces invariants at parse time |
| `src/models/result.py` | `TestResult` (per-case scores + assertion breakdown) and `SuiteRun` (suite-level summary with regression count) |
| `src/assertions/engine.py` | Orchestrates assertion tier order; fail-fast on rule failures; weighted mean aggregation |
| `src/assertions/rule_based.py` | 12 deterministic assertion handlers; zero API cost; runs first |
| `src/assertions/semantic.py` | `all-MiniLM-L6-v2` sentence-transformer; cosine similarity; module-level singleton via `lru_cache` |
| `src/assertions/judge.py` | LLM-as-judge; 4-dimension structured rubric; anti-self-bias routing; weighted overall recomputed client-side |
| `src/llm/factory.py` | Routes by model-name prefix: `claude-*` → Anthropic; `gpt-*/o1/o3/o4` → OpenAI; else → Ollama |
| `src/llm/anthropic_client.py` | Anthropic SDK wrapper; standardised `LLMResponse` data contract |
| `src/llm/openai_client.py` | OpenAI SDK wrapper; same `LLMResponse` contract |
| `src/llm/ollama_client.py` | `httpx`-based Ollama client; zero-cost local execution |
| `src/storage/database.py` | SQLAlchemy 2.0 async engine + session factory; SQLite default, PostgreSQL via one env-var swap |
| `src/storage/orm_models.py` | Four ORM tables: `test_cases`, `test_runs`, `test_results`, `baselines` |
| `src/storage/baseline_manager.py` | Three-rule baseline update policy; score history queries; regression feed for dashboard |
| `src/api/app.py` + `src/api/routers/` | FastAPI application root and REST routers (runs, baselines, test cases) |
| `dashboard/app.py` | Streamlit dashboard; reads database directly without FastAPI dependency; five views |
| `cli.py` | Typer CLI: `prs run`, `prs validate`, `prs serve`, `prs baselines update/reset` |
| `ci/` | Three CI scripts: detect affected tests, run suite, post GitHub PR comment |

**Core processing flow:**

```
Registry (YAML discovery + reverse index)
  → Runner (async dispatch, asyncio.Semaphore-limited)
    → AssertionEngine (tier 1: rules → tier 2: semantic → tier 3: judge)
      → BaselineManager (delta: current mean − stored baseline)
        → SuiteRun (aggregated results: passed / regressed / errored)
          → Storage (SQLite or PostgreSQL persistence)
```

**Two GitHub Actions workflows drive CI:**

- `pr-regression.yml` — triggers on changes to `prompts/**` or `tests/**/*.yaml`; runs detect → suite → post PR comment → exit non-zero if regressions detected
- `weekly-drift.yml` — every Monday at 09:00 UTC; full suite on `main`; Slack webhook alert with emoji-coded severity

The data contracts flowing between layers are fully typed: `TestCase` (parsed from YAML at load time) → `TestResult` (one per test case per run) → `SuiteRun` (suite-level aggregation, the final artifact persisted to the database).
```

- [ ] **Step 2: Verify word count**

Run: `wc -w /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: Section 4 body approximately 400–460 words. Running file total roughly 1,300–1,470 words.

---

### Task 5: Section 5 (Core Technical Components)

**Files:**
- Modify: `PROJECT_REPORT.md` (append)

**Section word target:** 500–700 words

- [ ] **Step 1: Append Section 5 to PROJECT_REPORT.md**

Append exactly the following content:

```markdown

---

## 5. Core Technical Components

### 5.1 Three-Tier Assertion Engine

The assertion engine (`src/assertions/engine.py`) sorts all assertions in a test case by cost tier before executing them: rule-based checks (tier 0) run first, semantic similarity (tier 1) runs second, and the LLM judge (tier 2) runs last. If any rule-based assertion fails, the engine skips all remaining assertions — the test result is already determined, and no API budget should be spent confirming it.

Twelve rule-based assertion types are available, each a pure Python function with zero external dependencies:

| Type | What it checks |
|---|---|
| `contains_keyword` | Response contains all listed keywords (case-insensitive) |
| `not_contains` | Response contains none of the listed forbidden phrases |
| `max_words` | Word count ≤ limit |
| `min_words` | Word count ≥ limit |
| `valid_json` | Response is parseable JSON |
| `json_contains_key` | JSON response contains all listed top-level keys |
| `starts_with` | Response begins with expected value |
| `not_starts_with` | Response does not begin with any forbidden phrase |
| `language_is` | Detected language matches expected code (e.g., `"en"`) |
| `regex_match` | Response matches a regular expression pattern |
| `response_time_under` | Latency ≤ `max_seconds` |
| `reading_level` | Flesch–Kincaid readability score within `[min, max]` range |

The final score is a weighted mean across all assertions that ran. Each assertion carries a configurable `weight` field — the financial analyst test assigns the LLM judge a weight of 2.0, double that of keyword checks, because judge quality is the most important signal for that test.

### 5.2 LLM-as-Judge

When rule and semantic checks pass, the judge (`src/assertions/judge.py`) sends the actual response to a different AI provider for structured evaluation. The judge prompt enforces JSON-only output — no preamble, no prose — to prevent silent parser failures at scale.

Four dimensions are scored between 0.0 and 1.0, with fixed weights that sum to 1.0:
- `instruction_following` (weight 0.40) — did the response follow all explicit instructions?
- `factual_accuracy` (weight 0.30) — are all factual claims correct and consistent with context?
- `format_compliance` (weight 0.20) — does the response match any specified format requirements?
- `tone_appropriateness` (weight 0.10) — is the tone appropriate for the context?

The weighted overall score is recomputed client-side after parsing the JSON — the judge model's arithmetic is not trusted. A `critical_failure` flag fires if any single dimension scores below 0.40; a `regression_risk` field ("low" | "medium" | "high") is surfaced in the dashboard and in the automated PR comment.

Anti-self-bias routing is enforced in `src/llm/factory.py` by model-name prefix: models starting with `claude-` are judged by OpenAI; models starting with `gpt-`, `o1`, `o3`, or `o4` are judged by Anthropic. The judge always runs at `temperature=0.0` for deterministic scoring.

### 5.3 Multi-Run Averaging & Flakiness Detection

A single model response at `temperature=0.7` is an unreliable regression signal — LLMs are stochastic, and a one-point score drop could be noise. PRS runs each test case `run_count` times (default 3) and averages the scores. Standard deviation across runs above 0.05 flags the test case as flaky in the results table.

Regression is declared when the mean score falls more than `delta_threshold` below the stored baseline (both default to 0.05). Delta-based comparison means absolute score levels do not matter — only drops relative to the baseline trigger a block.

### 5.4 Registry & Change Detection

`Registry` builds two indexes at load time: a forward map (`test_case_id → TestCase`) and a reverse map (`prompt_template_path → [test_case_ids]`). When CI calls `Registry.affected_by(changed_files)`, only the test cases referencing modified prompt files are returned — a PR touching 3 of 80 prompt files runs roughly 12 tests, not 80.

If more than 30% of all tracked prompt files changed in a single PR, `Registry.should_run_full_suite()` returns `True` and the complete suite runs. This catches systemic refactors — reorganizing the prompts directory, renaming shared prompt components — that would slip through selective execution. `TestCase.id` is derived from `file_path.stem + "::" + name`, stable across YAML file renames as long as the `name` field is unchanged.

### 5.5 Storage & Baseline Policy

Four async SQLAlchemy Object-Relational Mapper (ORM) tables persist all data: `test_cases` (registry), `test_runs` (suite-level headers), `test_results` (per-case scores, assertion breakdowns, regression flags, latency), and `baselines` (per-test score + reason + commit SHA).

The three-rule baseline update policy governs how stored baselines change:

- **Rule 1:** Baselines update automatically on every merge to `main`.
- **Rule 2:** PR runs never update baselines — they are comparison-only.
- **Rule 3:** Forced resets require a non-empty documented reason, stored as an audit trail in the `baselines` table. `BaselineManager.force_reset()` raises `ValueError` if the reason is empty, making undocumented resets impossible through any interface.

SQLite is the default (`sqlite:///./regression_suite.db`); switching to PostgreSQL for production requires one environment variable change (`DATABASE_URL=postgresql+asyncpg://...`). The same ORM models and async session factory work with both backends.
```

- [ ] **Step 2: Verify word count**

Run: `wc -w /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: Section 5 body approximately 550–660 words. Running file total roughly 1,880–2,150 words.

- [ ] **Step 3: Verify ORM expansion**

Run: `grep -n "Object-Relational Mapper" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: Exactly one match, in Section 5.5.

---

### Task 6: Section 6 (CI/CD Integration)

**Files:**
- Modify: `PROJECT_REPORT.md` (append)

**Section word target:** 200–250 words

- [ ] **Step 1: Append Section 6 to PROJECT_REPORT.md**

Append exactly the following content:

```markdown

---

## 6. CI/CD Integration

PRS ships with two GitHub Actions workflows that turn the assertion engine into an automated deployment gate.

`pr-regression.yml` triggers whenever a PR modifies a file under `prompts/**` or `tests/**/*.yaml`. It runs four steps in sequence:

1. `ci/detect_affected.py` — runs `git diff --name-only` against the base branch, then queries the registry reverse index to select affected test cases only.
2. `ci/run_suite.py` — executes the affected test cases and writes `ci_results.json`. The step is configured with `continue-on-error: true` so the comment step always runs even when regressions are found.
3. `ci/post_comment.py` — posts a formatted comment on the PR listing each test case's score, baseline, delta, and judge verdict.
4. A Python one-liner reads `ci_results.json` and exits with code 1 if `has_regressions` is `true`, blocking the merge.

PR results are retained as GitHub Actions artifacts for 30 days.

`weekly-drift.yml` runs the full test suite every Monday at 09:00 UTC on the `main` branch — regardless of whether any files changed that week. This catches model provider drift: a silent base model update that shifts behavior without any code change. A Slack webhook posts an emoji-coded summary — green circle (zero regressions), yellow (1–3), red (more than 3) — naming the worst-regressing test case. Weekly results are retained for 90 days.
```

- [ ] **Step 2: Verify word count**

Run: `wc -w /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: Section 6 body approximately 210–240 words. Running file total roughly 2,110–2,410 words.

---

### Task 7: Section 7 (Usage Guide)

**Files:**
- Modify: `PROJECT_REPORT.md` (append)

**Section word target:** 300–400 words

- [ ] **Step 1: Append Section 7 to PROJECT_REPORT.md**

Append exactly the following content:

```markdown

---

## 7. Usage Guide

**Prerequisites:** Python 3.11 or higher; at least one of `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or a running Ollama instance.

**Install:**

```bash
git clone <repo-url>
cd prompt-regression-suite
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # add API keys inside .env
```

**Write a test case** (annotated YAML):

```yaml
name: "My prompt — expected behaviour description"
prompt_template: "prompts/my_prompt.txt"   # {{variable}} placeholders substituted at runtime
variables:
  input: "The user input text"             # substituted for {{input}} in the prompt
expected_behavior: >
  Response must do X, avoid Y, and stay under Z words.
run_count: 3          # runs averaged to reduce temperature noise (default 3)
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

**Key Command-Line Interface (CLI) commands:**

```bash
prs validate                               # parse all YAMLs; report schema errors — no API cost
prs run                                    # run all test cases
prs run --affected                         # run only cases affected by git-changed prompt files
prs run --tag financial                    # filter by tag
prs run --update-baselines \
  --commit-sha $(git rev-parse HEAD)       # accept current scores as new baselines
prs baselines reset <test-case-id> \
  --score 0.85 \
  --reason "Intentional tone change per product decision"
```

**Launch the visual dashboard and API:**

```bash
streamlit run dashboard/app.py   # User Interface (UI) at http://localhost:8501
prs serve --reload                # FastAPI at http://localhost:8000/docs
```

The Streamlit dashboard provides five views: **Health Overview** (suite pass rate, regression count, 30-day heatmap); **Regression History** (filterable event feed with judge verdicts and raw LLM responses); **Score Trends** (per-test time series with 7-day rolling average and baseline reference line); **Model Comparison** (score distribution per prompt file; score-vs-latency scatter); **Baselines** (current baseline table with a force-reset form requiring a documented reason).
```

- [ ] **Step 2: Verify word count**

Run: `wc -w /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: Section 7 body approximately 290–360 words. Running file total roughly 2,430–2,790 words.

- [ ] **Step 3: Verify CLI and UI expansions**

Run: `grep -n "Command-Line Interface\|User Interface" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: Exactly one match each, both in Section 7.

---

### Task 8: Section 8 (Tech Stack & Key Design Decisions) + Footer

**Files:**
- Modify: `PROJECT_REPORT.md` (append)

**Section word target:** 300–400 words

- [ ] **Step 1: Append Section 8 and footer to PROJECT_REPORT.md**

Append exactly the following content:

```markdown

---

## 8. Tech Stack & Key Design Decisions

| Layer | Technology | Reason chosen |
|---|---|---|
| Language | Python 3.11 | `asyncio` task groups; match statements; required by sentence-transformers |
| CLI | Typer + Rich | Declarative command definitions; coloured terminal output without manual ANSI codes |
| API framework | FastAPI + Uvicorn | Async-native; automatic OpenAPI docs at `/docs`; minimal boilerplate |
| LLM clients | Anthropic SDK, OpenAI SDK, httpx | Official SDKs for managed providers; `httpx` for local Ollama (no SDK needed) |
| Embeddings | `all-MiniLM-L6-v2` via sentence-transformers | 80 MB, runs locally, zero API cost; cosine similarity sufficient for regression detection |
| Data validation | Pydantic v2 | Zero-cost validation at parse time; `model_validator` enforces invariants before any test runs |
| Database | SQLite → PostgreSQL | SQLite for zero-setup local dev; one env-var swap to PostgreSQL for production scale |
| ORM | SQLAlchemy 2.0 async | Async session support; same models work against both database backends |
| Dashboard | Streamlit + Plotly | Reads database directly (no FastAPI dependency); interactive charts with minimal boilerplate |
| Readability | textstat | Flesch–Kincaid score for `reading_level` assertion; pure Python, no external model |
| Language detection | langdetect | Optional dependency; skipped gracefully if not installed |

**Five non-obvious design decisions:**

1. **Tiered assertion engine for ~50% cost reduction.** Rule-based and semantic checks gate the expensive judge call. A test that fails `valid_json` or word-count limits never triggers an Anthropic or OpenAI API call — making large test suites economically viable.

2. **Anti-self-bias judge routing.** A model cannot reliably evaluate its own outputs — it tends to confirm its own reasoning style and tone. The LLM factory routes by model-name prefix so Claude-family models are always judged by OpenAI, and vice versa.

3. **Multi-run averaging instead of fixed thresholds.** A single response at `temperature=0.7` is too noisy to be a reliable regression signal. Averaging across `run_count` runs and comparing deltas (not absolute values) reduces test flakiness to below 5% of runs.

4. **Three-rule baseline update policy.** The policy balances two competing needs: baselines must advance with genuine improvements (so they stay useful), but they must never silently absorb regressions (so they stay trustworthy). The three rules — auto-update on main, never on PR, forced reset requires a documented reason — are the minimum viable solution.

5. **Registry reverse index + 30% heuristic for selective CI.** Without the reverse index, every PR runs all test cases. With it, a PR touching 3 of 80 prompt files runs roughly 12 tests. The 30% threshold prevents selective mode from missing systemic refactors that touch many prompt files at once.

---

*Report generated: 2026-06-23 | Author: Jaya Arun Kumar Tulluri | Project version: 1.0.0*
```

- [ ] **Step 2: Verify word count**

Run: `wc -w /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: Section 8 body approximately 310–370 words. Full document total: 2,800–3,400 words.

---

### Task 9: Final Review & Corrections

**Files:**
- Modify: `PROJECT_REPORT.md` (if corrections needed)

This task audits the complete document. No new sections are written — only fixes.

- [ ] **Step 1: Check total word count**

Run: `wc -w /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: 2,800–3,400 words. If over 3,400, trim the longest subsection (typically Section 5) by tightening prose. If under 2,800, expand the thinnest section (typically Section 2 or Section 6).

- [ ] **Step 2: Audit abbreviation discipline — no re-expansions**

Run each grep and confirm exactly ONE match per abbreviation across the entire document:

```bash
grep -c "Large Language Model" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md
grep -c "Continuous Integration" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md
grep -c "Application Programming Interface" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md
grep -c "Prompt Regression Suite" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md
grep -c "Pull Request" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md
grep -c "YAML Ain't Markup Language" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md
grep -c "Object-Relational Mapper" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md
grep -c "Command-Line Interface" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md
grep -c "User Interface" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md
```

Expected: Each command returns `1`. If any returns `0`, the expansion is missing — add it to the correct section. If any returns `2` or more, a duplicate expansion exists — remove all but the first.

- [ ] **Step 3: Confirm section count**

Run: `grep -c "^## " /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected: `8`

- [ ] **Step 4: Confirm footer**

Run: `tail -3 /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report/PROJECT_REPORT.md`

Expected last line: `*Report generated: 2026-06-23 | Author: Jaya Arun Kumar Tulluri | Project version: 1.0.0*`

- [ ] **Step 5: Confirm no git operations were performed**

Run: `git -C /media/asterisk/1722F6694CF9F147/project/my_learning_projects/Prompt_Regression_Suite_Report log --oneline -3`

The output should not include any new commits beyond the repository's existing history. The PROJECT_REPORT.md should be an untracked file only.
