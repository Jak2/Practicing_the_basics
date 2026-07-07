# LLM Evaluation Framework
## FastAPI · Celery · Redis · PostgreSQL · Streamlit · Plotly · Docker Compose

---

## Elevator Pitch (30 seconds)

> "I built a production-grade automated quality gate for LLM-powered applications. It runs four independent evaluators — an LLM-as-judge, a hallucination detector, a RAG faithfulness scorer, and a consistency checker — against any prompt/response pair submitted via API. Results land in PostgreSQL, trigger Slack alerts on failure, and appear on a live Streamlit dashboard. A simulated model provider update that caused a 14-point faithfulness drop was detected and flagged in under 4 minutes — compared to an estimated 2-3 days via manual human review."

---

## The Problem

Every company shipping LLMs in production is flying blind. A prompt scoring 92% accuracy today can silently degrade to 61% next week after a model provider pushes an update with no public changelog — the API contract doesn't change, but the output quality does.

Two failure modes are especially hard to catch manually:

**Model provider drift:** Anthropic or OpenAI releases a new model version. The behavioural changes are subtle — slightly shorter answers, different edge-case handling, shifted safety filters. None of this shows up unless you're running systematic quality checks.

**RAG context leakage:** A RAG pipeline retrieves the right documents but the model blends in knowledge from its internal training data that the retriever never returned. The answer looks factually correct (the model's parametric knowledge happens to agree) but it isn't grounded in the retrieved context. This is invisible to any check that only asks "is this true?" rather than "did the model stay within the retrieved context?"

---

## Architecture — Full Data Flow

```
Client (curl / CI pipeline / browser)
   │ POST /api/test-cases  (X-API-Key header)
   ▼
FastAPI :8000
  - Pydantic validates payload
  - Writes TestCase (status=pending) → PostgreSQL
  - Enqueues run_evaluation(test_case_id) → Redis
  → HTTP 201 returned immediately (caller does NOT wait)
   ↓
Redis Broker :6379
   ↓
Celery Worker (concurrency=4)
  1. Fetch TestCase from PostgreSQL
  2. Call target LLM (Anthropic / OpenAI) → record response, latency_ms, tokens
  3. Run each evaluator sequentially:
     ├── LLM Judge        (threshold 0.60)
     ├── Hallucination    (threshold 0.75)
     ├── Faithfulness     (threshold 0.80)
     └── Consistency      (threshold 0.85)
  4. Write EvalResult → PostgreSQL
  5. overall_passed=False → Slack webhook alert
   ↓
Streamlit :8501 — polls every 30s — 4 tabs — Plotly score charts
```

---

## The Four Evaluators

### 1. LLM-as-Judge (threshold: 0.60)

A judge LLM (Claude Haiku) scores the response on 5 dimensions: accuracy, relevance, completeness, clarity, safety — rated 1-5 each. Normalisation: `(overall_1_to_5 − 1.0) / 4.0`.

*Why LLM judge over heuristics?* Hand-crafted heuristics break for novel prompts. LLM outputs aren't deterministic — the "right" answer can be phrased in dozens of equivalent ways. An LLM judge handles natural variation; regex doesn't.

### 2. Hallucination Detector (threshold: 0.75)

The judge LLM decomposes the response into individual factual claims and classifies each as `SUPPORTED`, `UNSUPPORTED`, or `CONTRADICTED` against a reference document.

```
score = 1.0 − (UNSUPPORTED + CONTRADICTED claims) / total claims
```

*Local model option:* `cross-encoder/nli-deberta-v3-base` (400MB) can replace the LLM judge for high-volume/cost-sensitive workloads — same interface, different backend.

### 3. Faithfulness Scorer (threshold: 0.80)

**Key distinction:** Faithfulness ≠ accuracy. Faithfulness = did the model stay within the retrieved context?

```
score = SUPPORTED statements / total statements
```

This enables precise RAG diagnostics:
- High faithfulness + wrong answer → retrieved documents are the problem
- Low faithfulness → model is ignoring the retriever (context leakage)

### 4. Consistency Checker (threshold: 0.85)

Re-runs the same prompt N−1 times at `temperature=0.7` to surface natural output variance. Computes mean pairwise cosine similarity across all N responses.

**Similarity strategy (priority order):**
1. `sentence-transformers/all-MiniLM-L6-v2` (80MB) — lazy-loaded on first use
2. Token-level Jaccard similarity (zero dependencies) — automatic fallback

*Why this matters:* A prompt that scores well on a single LLM-as-judge run can still be unreliable in production — some runs mention a key fact, others omit it.

### Pass Logic — AND, not average

`overall_passed = True` only when **every** selected evaluator independently passes its threshold. A response that is 95% faithful but contains a hallucinated claim still fails. A weighted average would mask critical failures.

---

## The Key Design Decisions

### 1. Celery over FastAPI BackgroundTasks

FastAPI background tasks are in-process — if the API server restarts mid-evaluation, the task is lost with no recovery. Celery persists tasks in Redis and retries automatically (3 retries, 30s delay). This is non-negotiable for a quality gate used in CI/CD pipelines — a lost evaluation job would silently pass a PR that should have been blocked.

### 2. Async-first stack: FastAPI + SQLAlchemy async + asyncpg

The API must remain responsive while evaluations run for 5-30 seconds in the background. A synchronous web server would block during database writes or LLM calls. asyncpg is the fastest PostgreSQL driver available — it removes the last synchronous bottleneck at the database layer.

### 3. Registry pattern for evaluators and LLM clients

Both `evaluators/registry.py` and `llm_clients/registry.py` implement a factory pattern mapping string names to class instances. Adding a new evaluator means: write a class extending `BaseEvaluator`, register its name. No changes to the worker task or API schema. This is the primary extensibility mechanism.

### 4. `eval_scores` as a JSON column

No schema migration needed to add a new evaluator — its results land in the existing `eval_scores` JSON column on the `EvalResult` table, keyed by evaluator name. New evaluators are just new keys in the JSON.

### 5. Local model fallbacks for cost-sensitive workloads

The consistency checker lazy-loads `all-MiniLM-L6-v2` (80MB) on first use if installed, falls back to Jaccard automatically. The hallucination detector similarly supports swapping to a local NLI model. The API surface doesn't change — it's a deployment configuration decision.

---

## Real-World Use Cases

- **CI/CD gating:** Submit a golden test suite after each PR that modifies a system prompt. Fail the PR if any score drops below threshold. Prompt quality becomes a measurable, blocking gate.
- **RAG diagnostics:** Run golden questions with faithfulness + hallucination evaluators to precisely locate whether retrieved documents or the model itself is the problem.
- **Model provider canary testing:** Run the full golden suite against a new model version before switching production traffic.
- **A/B prompt comparison:** Submit two prompt variants as separate test cases. The one with higher judge scores and lower consistency variance is objectively better.

---

## Anticipated Interview Questions

**Q: Why AND logic instead of a weighted average?**
> A weighted average can mask a critical failure. A response that halluccinates a specific fact but is well-written and relevant would still clear an average-based threshold. AND logic means any single evaluator failure blocks the test case. This is intentionally strict — the framework is a quality gate, not a quality summary.

**Q: What's the difference between hallucination detection and faithfulness scoring?**
> Hallucination detection asks: "does the response contain claims that aren't verifiable against the reference?" It's about factual grounding. Faithfulness asks: "did the model stay within the retrieved context?" A faithfulness score of 1.0 doesn't mean the answer is correct — it means the model only used content from the retriever. If faithfulness is high but the answer is wrong, the retriever surfaced bad documents. If faithfulness is low, the model ignored the retriever entirely. These are completely different failure modes requiring different fixes.

**Q: Why not just use human reviewers?**
> Human reviewers don't scale — a panel reviewing 50 outputs per day can't keep pace with a RAG pipeline processing thousands of queries. They're also inconsistent across reviewers and over time. The framework provides a shared, auditable, numeric definition of "good enough to ship" that product and engineering can agree on.

**Q: How do you handle the cost of running LLM-based evaluators at scale?**
> Two mechanisms. First, the local model fallbacks — the consistency checker uses a 80MB sentence-transformer model instead of an API call when installed; the hallucination detector supports swapping to a local NLI model. Second, the evaluators are selectable per test case — you don't have to run all four on every submission. A routine unit test might only run LLM-as-judge; a RAG regression test runs faithfulness + hallucination.

**Q: Celery + Redis vs a simpler approach like FastAPI BackgroundTasks?**
> FastAPI background tasks live in-process. If the API server restarts while an evaluation is running — during a deploy, for example — the task disappears with no recovery. Celery tasks are persisted in Redis and retried automatically on failure. For a quality gate wired into CI/CD, silent task loss would cause a PR to pass a check that never actually ran. That's worse than the complexity of adding Celery.
