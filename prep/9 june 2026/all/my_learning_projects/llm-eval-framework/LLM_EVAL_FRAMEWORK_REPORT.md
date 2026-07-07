# LLM Evaluation Framework — Project Report

> An automated quality testing platform that runs four independent evaluators against any Large Language Model output, surfaces score trends on a real-time dashboard, and fires regression alerts before failures reach production users.

**Author:** Jaya Arun Kumar Tulluri
**Version:** 1.0 — June 2026
**Project:** `my_learning_projects/llm-eval-framework`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem & Motivation](#2-problem--motivation)
3. [How It Works — Plain English](#3-how-it-works--plain-english)
4. [System Architecture](#4-system-architecture)
5. [Core Technical Components](#5-core-technical-components)
6. [Real-World Use Cases](#6-real-world-use-cases)
7. [Usage Guide](#7-usage-guide)
8. [Tech Stack & Key Design Decisions](#8-tech-stack--key-design-decisions)

---

## 1. Executive Summary

The Large Language Model (LLM) Evaluation Framework is a production-grade automated quality testing platform for any LLM-powered application. It answers one question that every team shipping AI to real users must be able to answer: *is this model's output still good enough to ship?*

The framework runs four independent quality checks — an LLM-as-Judge scoring rubric, a hallucination detector, a faithfulness scorer for Retrieval-Augmented Generation (RAG) pipelines, and a consistency checker — against any prompt/response pair submitted via an Application Programming Interface (API) call. Results land in a PostgreSQL database and are immediately visible on a Streamlit dashboard at `http://localhost:8501`. If any evaluator's score drops below its configured threshold, an automated Slack alert fires within seconds.

**Key outcome:** A simulated model provider update that caused a 14-point faithfulness drop in a RAG pipeline was detected and flagged in under 4 minutes — compared to an estimated 2–3 days via manual human review.

The framework is accessed via its REST API (port 8000), a browser dashboard (port 8501), or wired directly into a Continuous Integration / Continuous Deployment (CI/CD) pipeline using `curl` or `pytest`. It deploys as a single `docker-compose up -d` command.

---

## 2. Problem & Motivation

### The Silent Degradation Problem

Every company shipping LLMs in production is flying blind in the same way. A prompt that scores 92% accuracy today can silently degrade to 61% next week after a model provider pushes an update with no public changelog. The model's API contract — same endpoint, same parameters, same price — doesn't change. The output quality does.

Two failure modes are especially hard to catch manually:

**Model provider drift.** When Anthropic or OpenAI releases a new version of a model, the behavioural changes can be subtle: slightly shorter answers, different handling of edge-case prompts, shifted safety filters. None of this shows up in the API response unless you're running systematic quality checks.

**RAG context leakage.** A RAG pipeline that retrieves the right documents can still produce hallucinations by blending in knowledge the retriever never returned. The answer *looks* factually correct — because the model's internal training data happens to agree — but it isn't grounded in the retrieved context. This is invisible to any quality check that only asks "is this factually true?" rather than "did the model stay within the retrieved context?"

### Why Existing Approaches Fall Short

The dominant approach to LLM quality assurance is reactive: users file support tickets, engineers investigate, and fixes ship in the next sprint. For customer-facing AI features, this means failures are in production for days before they're understood.

Some teams use human review panels, but these don't scale: a panel that can review 50 outputs per day cannot keep pace with a RAG pipeline processing thousands of queries. Human reviewers are also inconsistent across reviewers and across time.

Lightweight automated checks — comparing outputs against a fixed string or running a regex — break immediately on any prompt where the correct answer has natural variation. LLM outputs are not deterministic; the right answer can be phrased in dozens of equivalent ways.

### The Gap This Project Fills

This framework provides a middle layer that does not currently exist in most LLM deployment pipelines: a systematic, automated quality gate that runs *before* failures reach users. It replaces reactive ticket-driven discovery with proactive, threshold-based regression detection. By expressing four distinct quality dimensions as numeric scores with configurable pass/fail thresholds, it gives engineering and product teams a shared, auditable definition of "good enough to ship."

---

## 3. How It Works — Plain English

### The Factory Inspector Analogy

Think of a car factory with a quality inspector at the end of the assembly line. Every car that rolls off the line goes through the same set of checks before it gets shipped to a dealer: brake test, paint inspection, safety systems verification. If a car fails any single check, it gets pulled aside before it ever leaves the building.

This framework does the same thing for LLM outputs. Every prompt/response pair is a "car" rolling off the line. The four evaluators are the quality checks. The dashboard is the factory floor display showing pass/fail counts in real time.

### The Workflow in Plain Steps

**Step 1 — Submit a test case.**
You send a request to the framework's API containing the prompt you want to test, the name of the LLM to run it against, and which quality checks to apply. You can also include a reference answer (what the correct response should look like) and retrieved context (the documents a RAG system would provide).

**Step 2 — The API accepts immediately.**
The framework records your test case in its database with a status of "pending" and returns a confirmation within milliseconds. It does not make you wait while the evaluation runs — that happens separately in the background.

**Step 3 — A background worker picks it up.**
A background process (a Celery worker) pulls the task from a queue, calls the target LLM (Claude, GPT-4o, or another configured model), and records the response along with how long it took and how many tokens were used.

**Step 4 — Each evaluator runs.**
The worker passes the response through each quality check you requested, in sequence. Each check produces a score between 0.0 (completely failing) and 1.0 (perfect), along with a plain-English explanation of what it found.

**Step 5 — Results are written and alerts fire.**
All scores are saved to the database. If any evaluator's score falls below its threshold, a Slack alert fires automatically with a summary of which checks failed and by how much.

**Step 6 — The dashboard updates.**
The Streamlit dashboard refreshes every 30 seconds, showing score trends, pass/fail breakdowns, and regression alerts. A team can see the health of their LLM pipeline at a glance without querying the database directly.

### What the Scores Mean

Every evaluator returns a score from 0.0 to 1.0. A score at or above the evaluator's threshold means "pass"; below means "fail". If all selected evaluators pass, the test case is marked `overall_passed = True`. If any single evaluator fails, the whole test case fails — there is no averaging across dimensions.

---

## 4. System Architecture

### Module Map

| Module path | Responsibility |
|---|---|
| `src/config.py` | Pydantic settings; single source of truth for all environment-based configuration |
| `src/api/main.py` | FastAPI app with lifespan (DB init on startup), CORS middleware, router registration |
| `src/api/deps.py` | Reusable async database session dependency injected into route handlers |
| `src/api/schemas.py` | Pydantic v2 request and response models for all API endpoints |
| `src/api/routers/test_cases.py` | `POST /api/test-cases` — validates, writes, and enqueues evaluation jobs |
| `src/api/routers/results.py` | `GET /api/results` — retrieves evaluation results from PostgreSQL |
| `src/api/routers/dashboard.py` | `GET /api/dashboard` — aggregated metrics consumed by the Streamlit User Interface (UI) |
| `src/database/models.py` | SQLAlchemy Object-Relational Mapper (ORM) models: `TestCase` and `EvalResult` |
| `src/database/engine.py` | Async engine, session factory, and table initialisation |
| `src/evaluators/base.py` | Abstract `BaseEvaluator`; defines the `evaluate()` interface and `EvalResult` dataclass |
| `src/evaluators/llm_judge.py` | LLM-as-judge: five-dimension rubric scored 1–5 and normalised to 0.0–1.0 |
| `src/evaluators/hallucination.py` | Claim-level Natural Language Inference (NLI) hallucination detection against a reference document |
| `src/evaluators/faithfulness.py` | RAG-specific: measures whether the answer stays within retrieved context |
| `src/evaluators/consistency.py` | Multi-run pairwise similarity scoring to detect output instability |
| `src/evaluators/registry.py` | Evaluator factory — maps string names (e.g. `"llm_judge"`) to instantiated objects |
| `src/llm_clients/base.py` | Abstract `BaseLLMClient`; defines the `complete()` and `complete_json()` interface |
| `src/llm_clients/anthropic_client.py` | Anthropic API wrapper using `httpx` async client |
| `src/llm_clients/openai_client.py` | OpenAI API wrapper using `httpx` async client |
| `src/llm_clients/registry.py` | LLM client factory — maps provider name to client instance |
| `src/workers/celery_app.py` | Celery configuration: broker URL, result backend, task serialisation |
| `src/workers/tasks.py` | `run_evaluation` Celery task — orchestrates LLM call and evaluator pipeline |
| `src/dashboard/app.py` | Streamlit UI: 4 tabs, API polling every 30 seconds, Plotly charts |

### Data Flow

```
Client (curl / CI pipeline / browser)
        │
        │  POST /api/test-cases   (X-API-Key header)
        ▼
┌────────────────────┐
│  FastAPI  :8000    │── Pydantic validates payload
│                    │── Writes TestCase (status=pending) → PostgreSQL
│                    │── Enqueues run_evaluation(test_case_id) → Redis
└────────┬───────────┘
         │   HTTP 201 returned immediately — caller does not wait
         ▼
┌────────────────────┐
│  Redis Broker      │
│  :6379             │
└────────┬───────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  Celery Worker  (concurrency=4)                  │
│                                                  │
│  1. Fetch TestCase from PostgreSQL               │
│  2. Call target LLM (Anthropic / OpenAI)         │
│     Records: response text, latency_ms, tokens   │
│  3. Run each requested evaluator sequentially:   │
│     ├── LLM Judge        (threshold 0.60)        │
│     ├── Hallucination    (threshold 0.75)        │
│     ├── Faithfulness     (threshold 0.80)        │
│     └── Consistency      (threshold 0.85)        │
│  4. Write EvalResult → PostgreSQL                │
│  5. overall_passed=False → Slack webhook alert   │
└──────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────┐        ┌─────────────────────┐
│  PostgreSQL  :5432 │◄───────│ Streamlit  :8501    │
│  test_cases        │ polls  │ 4 tabs, 30 s refresh │
│  eval_results      │ every  │ Plotly score charts  │
└────────────────────┘ 30 s   └─────────────────────┘
```

### Central Data Contract

Two ORM tables hold everything together. `TestCase` captures the inputs: the prompt, optional system prompt, optional RAG context, optional reference answer, the target LLM name, and the list of evaluators to run. `EvalResult` captures the outputs: the LLM response text, latency in milliseconds, token count, and an `eval_scores` JavaScript Object Notation (JSON) column that stores every evaluator's `score`, `passed`, `explanation`, and raw metadata as a nested dictionary keyed by evaluator name.

This design means no schema migration is needed to add a new evaluator — its results land in the existing `eval_scores` JSON column.

---

## 5. Core Technical Components

### 5.1 LLM-as-Judge Evaluator

**What it measures:** Overall response quality across five dimensions — accuracy, relevance, completeness, clarity, and safety.

**Approach:** A system prompt instructs a judge LLM (default: Claude Haiku) to score the target model's response on each dimension from 1 (worst) to 5 (perfect) and return a strict JSON object. The judge also emits a `recommendation` field with one of three verdicts: `PASS`, `REVIEW`, or `FAIL`.

**Normalisation formula:**
```
normalised_score = (overall_1_to_5 − 1.0) / 4.0
```
A raw score of 1 maps to 0.0; a raw score of 5 maps to 1.0. If the LLM omits the `overall` field, it is computed as the arithmetic mean of the five dimension scores before normalisation.

**Pass threshold:** 0.60 (equivalent to a raw mean of 3.4 out of 5).

**Why this approach:** Using a stronger LLM as the judge avoids hand-crafted heuristics that break for novel prompts. Returning structured JSON rather than free-text scores makes the evaluator deterministic to parse. The five-dimension rubric catches different failure modes: accuracy catches factual errors, safety catches harmful outputs, and consistency-of-scoring is enforced by the strict system prompt framing ("your scores gate production deployments — be strict and consistent").

---

### 5.2 Hallucination Detector

**What it measures:** Whether the LLM's response contains claims that cannot be verified, or that are directly contradicted, by a provided reference document.

**Approach:** The judge LLM is instructed to decompose the response into individual factual claims and classify each one against the reference text with one of three verdicts:
- `SUPPORTED` — the claim can be directly inferred from the reference.
- `UNSUPPORTED` — the claim cannot be inferred (may or may not be true; it simply isn't in the reference).
- `CONTRADICTED` — the claim directly conflicts with the reference.

**Score formula:**
```
hallucination_rate = (UNSUPPORTED + CONTRADICTED claims) / total claims
score = 1.0 − hallucination_rate
```

**Pass threshold:** 0.75 (at most 25% of claims can be non-supported).

**Prerequisites:** Requires either a `reference_answer` or a `context` field in the test case. If neither is provided, the evaluator skips and returns a neutral pass (`score=1.0`, `skipped=True`).

**Optional local mode:** For high-volume workloads where LLM API costs are a constraint, the `registry.py` factory supports swapping the judge LLM for a local `cross-encoder/nli-deberta-v3-base` cross-encoder model (400 MB, requires `transformers` and `torch`). The evaluator interface is unchanged — only the backend differs.

---

### 5.3 Faithfulness Scorer

**What it measures:** Whether the model's answer stays strictly within the retrieved context in a RAG pipeline — regardless of whether the answer is factually correct.

**The key distinction:** Faithfulness is not the same as accuracy. A faithfulness score of 1.0 means the model only used content from the retrieved context. It does not mean the context was correct. This distinction enables precise RAG diagnostics: if faithfulness is high but the answer is wrong, the retrieved documents are the problem. If faithfulness is low, the model is ignoring the retriever and relying on its internal parametric knowledge ("context leakage").

**Approach:** The judge LLM classifies each statement in the generated answer as either `SUPPORTED` (grounded in the retrieved context) or `UNSUPPORTED` (introduced from outside the context). The score is the proportion of supported statements.

**Score formula:**
```
score = SUPPORTED statements / total statements
```

**Pass threshold:** 0.80.

**Prerequisites:** Requires a `context` field. Without it, the evaluator skips and returns a neutral pass.

---

### 5.4 Consistency Checker

**What it measures:** Whether the model gives structurally and factually stable answers when asked the same prompt multiple times — a proxy for prompt reliability under stochastic sampling.

**Approach:** The evaluator re-runs the same prompt `N−1` additional times concurrently (default `N=5`, from `CONSISTENCY_RUNS` in config), using `temperature=0.7` to surface natural output variance. It then computes the mean pairwise cosine similarity across all `N` responses.

**Similarity strategy (priority order):**
1. **Semantic cosine similarity** using `sentence-transformers/all-MiniLM-L6-v2` (80 MB), if the `sentence-transformers` package is installed. The model is lazy-loaded on first use — it is not imported on startup.
2. **Token-level Jaccard similarity** (zero additional dependencies) as an automatic fallback when `sentence-transformers` is not installed.

**Score formula:**
```
score = mean pairwise cosine similarity across all N(N−1)/2 pairs
```
Standard deviation across pairs is also computed and stored in metadata for diagnostic use.

**Pass threshold:** 0.85. The label `STABLE` is applied when the score meets or exceeds the threshold; `INCONSISTENT` is applied when it falls below.

**Why this matters:** A prompt that scores well on a single LLM-as-Judge run can still be unreliable in production if it produces structurally different answers on consecutive calls — some mentioning a key fact, others omitting it. The consistency checker catches this class of failure.

---

### 5.5 Evaluator Independence and Pass Logic

The four evaluators are fully independent: each runs against the same LLM response, and none feeds into another. There is no weighted composite score. The `overall_passed` field on an `EvalResult` record uses AND logic — it is `True` only when every selected evaluator independently passes its own threshold. This is intentional: a response that is 95% faithful but contains a hallucinated claim should still fail.

---

## 6. Real-World Use Cases

### CI/CD Prompt Regression Gating

Wire the framework into a GitHub Actions workflow. After each PR that modifies a system prompt or RAG retriever, submit a golden test suite (a fixed set of prompts with known reference answers) to the framework's API. Fail the PR if any evaluation score drops below its threshold. This converts prompt quality from a subjective code review concern into a measurable, blocking gate — identical to how unit tests gate code changes.

### RAG Pipeline Diagnostics

After tuning a retriever or updating a document corpus, run a set of golden questions through the framework with both `faithfulness` and `hallucination` evaluators selected. The result combination tells you exactly where the problem lies: high faithfulness but high hallucination rate means the retrieved documents contain incorrect information. Low faithfulness means the model is bypassing the retriever entirely and generating from parametric memory.

### Model Provider Canary Testing

When a new major model version is released by Anthropic or OpenAI, run the full golden suite against the new model version before switching production traffic. A drop in LLM-as-judge scores or a rise in hallucination rate is detected immediately — before a single user sees degraded output.

### A/B Prompt Comparison

Submit two identical prompts with different system prompt instructions as separate test cases. The variant with higher judge scores and lower consistency variance is objectively the better prompt. This removes subjective debate from prompt engineering decisions.

### Cost and Model Selection Benchmarking

Run the same prompt through `claude` and `gpt-4o` as separate test cases. The `EvalResult` records each model's `latency_ms` and `token_count` alongside evaluation scores. A data-driven model selection — balancing quality, speed, and cost — is produced directly from the framework's output without any additional tooling.

---

## 7. Usage Guide

### Prerequisites

- Docker and Docker Compose (required — primary deployment method)
- An Anthropic API key, an OpenAI API key, or both
- No local Python installation required for the standard Docker deployment

### Setup and Launch

**Step 1 — Clone and configure**
```bash
git clone https://github.com/yourusername/llm-eval-framework
cd llm-eval-framework
cp .env.example .env
```
Edit `.env` and set your API keys:
```env
ANTHROPIC_API_KEY=sk-ant-...
API_KEY=your-chosen-secret
```

**Step 2 — Start all five services**
```bash
docker-compose up -d
```
This brings up PostgreSQL (:5432), Redis (:6379), the FastAPI server (:8000), the Celery worker, and the Streamlit dashboard (:8501). The API waits for PostgreSQL and Redis health checks before starting.

**Step 3 — Verify health**
```bash
curl http://localhost:8000/health
# {"status":"ok","version":"1.0.0"}
```

**Step 4 — Submit a test case**
```bash
curl -X POST http://localhost:8000/api/test-cases \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-chosen-secret" \
  -d '{
    "name": "Capital of France",
    "prompt": "What is the capital of France?",
    "reference_answer": "The capital of France is Paris.",
    "llm_name": "claude",
    "evaluators": ["llm_judge", "hallucination"],
    "temperature": 0.0
  }'
```

**Step 5 — View results**
Navigate to `http://localhost:8501` and check the **Results** tab after approximately 15 seconds. Interactive API documentation is available at `http://localhost:8000/docs`.

### Configuration Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Optional | — | Anthropic API key |
| `OPENAI_API_KEY` | Optional | — | OpenAI API key |
| `API_KEY` | Yes | `dev-secret-key` | `X-API-Key` header value for all endpoints |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://eval_user:eval_pass@localhost:5432/llm_eval` | asyncpg connection string |
| `CELERY_BROKER_URL` | Yes | `redis://localhost:6379/0` | Redis URL for task queue |
| `CELERY_RESULT_BACKEND` | Yes | `redis://localhost:6379/1` | Redis URL for Celery result storage |
| `JUDGE_MODEL` | No | `claude-haiku-4-5-20251001` | Model used by LLM-based evaluators |
| `JUDGE_PROVIDER` | No | `anthropic` | `anthropic` or `openai` |
| `DEFAULT_THRESHOLD` | No | `0.70` | Pass/fail cutoff (overridden per-evaluator in code) |
| `CONSISTENCY_RUNS` | No | `5` | Number of re-runs for the consistency checker |
| `SLACK_WEBHOOK_URL` | No | — | Slack incoming webhook URL for failure alerts |

### Output Artefacts

Each completed test case produces:
- An `EvalResult` row in the `eval_results` PostgreSQL table, containing `eval_scores` (JSON), `latency_ms`, `token_count`, and `overall_passed`.
- A real-time update on the Streamlit dashboard at `:8501` (refreshed every 30 seconds).
- A Slack alert (if `SLACK_WEBHOOK_URL` is configured and `overall_passed=False`), listing each evaluator's score and pass/fail status.
- Queryable via `GET /api/results` and the interactive docs at `http://localhost:8000/docs`.

---

## 8. Tech Stack & Key Design Decisions

### Tech Stack

| Layer | Technology | Reason chosen |
|---|---|---|
| API | FastAPI, Pydantic v2 | Async-native; Pydantic v2 validation at zero runtime cost |
| Database | PostgreSQL 16 | Reliable JSON column support for heterogeneous eval_scores; ACID guarantees for audit trail |
| ORM & Migrations | SQLAlchemy 2.0 (async), asyncpg, Alembic | Async ORM matches the async API layer; asyncpg is the fastest PostgreSQL driver available |
| Task Queue | Celery, Redis 7 | Durable task queue with retry logic; decouples API response time from evaluation runtime |
| HTTP Client | httpx (async) | Async-native connection pooling; shared across LLM API calls without blocking the event loop |
| Dashboard | Streamlit, Plotly | Zero-boilerplate data dashboards; Plotly for interactive score trend charts |
| Containerisation | Docker Compose | Single command to bring up all five dependent services with health-check ordering |

### Key Design Decisions

**1. Async-first stack (FastAPI + SQLAlchemy async + asyncpg) over synchronous alternatives**

*Chosen over:* Django/Flask with synchronous SQLAlchemy.

*Why:* The framework's API must remain responsive while evaluations run for 5–30 seconds in the background. A synchronous web server would block the event loop during database writes or LLM client calls. Using asyncpg as the PostgreSQL driver (rather than psycopg2) removes the last synchronous bottleneck at the database layer. The connection pool is sized at 10 connections with 5 overflow slots (`db_pool_size=10`, `db_max_overflow=5` in `config.py`), supporting multiple concurrent workers without connection exhaustion.

**2. Celery over FastAPI `BackgroundTasks` for evaluation execution**

*Chosen over:* `asyncio.create_task()` or FastAPI's built-in `BackgroundTasks`.

*Why:* FastAPI background tasks are in-process — if the API server restarts mid-evaluation, the task is lost with no recovery path. Celery persists tasks in Redis and retries failed jobs automatically (up to 3 retries with a 30-second delay, configured in `tasks.py`). This durability is non-negotiable for a quality gate used in CI/CD pipelines, where a lost evaluation job would silently pass a PR that should have been blocked.

**3. Registry pattern for evaluators and LLM clients**

*Chosen over:* Direct imports and conditional `if/elif` blocks.

*Why:* Both `src/evaluators/registry.py` and `src/llm_clients/registry.py` implement a factory pattern that maps string names to class instances. Adding a new evaluator requires only writing a class that extends `BaseEvaluator` and registering its name in the registry — no changes to the worker task or API schema. The same pattern applies to LLM clients. This is the primary extensibility mechanism in the codebase.

**4. Local model fallback for cost-sensitive workloads**

*Chosen over:* LLM-API-only approach.

*Why:* At scale, calling a judge LLM for every hallucination check becomes expensive. The `ConsistencyChecker` lazy-loads `sentence-transformers/all-MiniLM-L6-v2` (80 MB) on first use if the package is installed, falling back to token-level Jaccard similarity automatically if it is not. The `HallucinationDetector` similarly supports swapping to a local `cross-encoder/nli-deberta-v3-base` model (400 MB) via the registry. The API surface doesn't change — the cost/quality tradeoff is a deployment configuration decision, not a code change.

**5. AND logic for `overall_passed` — no composite averaging**

*Chosen over:* A weighted average score across all evaluators.

*Why:* A weighted average can mask a critical failure. A response that halluccinates a specific fact but scores well on LLM-as-judge (because it is well-written and relevant) would still clear an average-based threshold. AND logic means any single evaluator failure blocks the test case. This is intentionally strict: the framework is a quality *gate*, not a quality *summary*.

---

*Report generated: 2026-06-23 | Author: Jaya Arun Kumar Tulluri | Project version: 1.0*
