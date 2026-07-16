# LLM Evaluation Framework — Interview Q&A

**Resume bullet:** *"LLM Evaluation Framework: Automated hallucination & prompt regression detection in 4 minutes vs 3 days manually. Stack: Python, LLM APIs."*

**Source of truth for every fact below:** `LLM_EVAL_FRAMEWORK_REPORT.md` (v1.0, June 2026). Project path: `my_learning_projects/llm-eval-framework`.

---

## READ THIS FIRST — where this project is actually attackable

| # | The question | Why it's dangerous |
|---|---|---|
| 1 | *"Your design doc says 'a response that is 95% faithful but contains a hallucinated claim should still fail' — but your hallucination threshold is 0.75, which passes a response where 1 in 4 claims is unsupported. Which is it?"* | **The source contradicts itself.** §5.5 states the strict principle; §5.2 sets the threshold at 0.75. Both are in the same document. If he defends the principle he has to explain why the threshold doesn't implement it. This is the single sharpest hit. |
| 2 | *"Where did 0.60, 0.75, 0.80, 0.85 come from?"* | There is **no ground-truth benchmark anywhere in the source** — no labelled dataset, no human-agreement measurement, no ROC curve. The thresholds are asserted, not calibrated. Every number the framework produces inherits that. |
| 3 | *"What score does a test case with no `context` get on faithfulness?"* | **1.0 and `passed=True`** (§5.3: "skips and returns a neutral pass"). A sentinel value that means *"not measured"* flows into AND logic as *"measured and passed."* A misconfigured CI job with a dropped `context` field goes green. This is a silent failure in a quality **gate**. |
| 4 | *"Your judge model defaults to `claude-haiku-4-5-20251001` and your example test case targets `"llm_name": "claude"`. Who is grading whom?"* | **Self-evaluation circularity.** A Claude model judging a Claude model's output, with no inter-rater reliability check against humans. Known self-preference bias goes straight into the pass/fail gate. |
| 5 | *"The '4 minutes vs 3 days' number — how was each side measured?"* | The source says **"a *simulated* model provider update"** and **"an *estimated* 2–3 days"**. The resume says 3 days. One side is a real wall-clock on a synthetic event; the other side is a guess. He must volunteer this before it is extracted from him. |
| 6 | *"Your consistency threshold is 0.85. What happens to it when `sentence-transformers` isn't installed?"* | The evaluator **silently falls back to token-level Jaccard** (§5.4). Jaccard and embedding cosine live on completely different scales — the same 0.85 line now means something else. The fallback is automatic and, as described, invisible. |
| 7 | *"`DEFAULT_THRESHOLD` is `0.70` in your config table — which evaluator uses it?"* | **None.** The config table itself says *"overridden per-evaluator in code."* A knob that looks operable and isn't. Small, but it's the kind of thing an interviewer uses to test whether he actually knows his own code. |

**How to handle all seven:** concede first, in one sentence, with the specific number. Then the fix. Never defend.

---

## SECTION 1 — Framing

**Q1. Give me the 30-second version.**

> It's a quality gate for LLM output. You POST a prompt, a target model, and optionally a reference answer and RAG context to a FastAPI endpoint on port 8000. It writes a `TestCase` row as `pending`, returns HTTP 201 immediately, and enqueues a Celery job through Redis. A worker at concurrency 4 calls the target model, then runs up to four independent evaluators — LLM-as-judge, hallucination, faithfulness, consistency — each returning 0.0 to 1.0. Results go to PostgreSQL, a Streamlit dashboard on 8501 polls every 30 seconds, and if any evaluator is below its threshold a Slack webhook fires. Whole thing is one `docker-compose up -d` across five services.

**Q2. Why does this need to exist? Teams already read their outputs.**

> Because the failure I care about is invisible to reading. A model provider ships an update behind the same endpoint, same parameters, same price — no changelog. Output quality moves and the API contract doesn't. The other one is RAG context leakage: the retriever returns the right documents and the model answers correctly anyway *from its own weights*. That answer looks perfect to a human reviewer, because it *is* true. It's still a defect, because the retriever is being bypassed. You cannot catch either by reading, only by measuring the same prompts on a schedule.

**Q3. Why not human review?**

> Doesn't scale and doesn't repeat. A panel doing 50 outputs a day cannot keep up with a RAG pipeline serving thousands of queries, and reviewers disagree with each other and with themselves over time. But I want to be precise about what I'm claiming: I replaced human review with something *cheaper and repeatable*, not something I've proven is *as accurate*. I never measured agreement between my judge and a human panel. That's the honest limit.

**Q4. Why not just assert on the expected string, like a normal test?**

> Because LLM output is non-deterministic and the right answer has dozens of valid phrasings. Exact-match and regex break on the first legitimate rewording. That's the entire reason for a scoring layer instead of an equality layer — I need "is this good" not "is this identical."

**Q5. What does the resume bullet actually mean by "prompt regression detection"?**

> Concretely, it means a golden suite — a fixed set of prompts with reference answers — submitted after every PR that touches a system prompt or a retriever, with the PR failing if any score drops below its threshold. I should be precise, though: what's implemented is **threshold breach detection plus a trend chart**, not a statistical regression test. There's no baseline-versus-current significance test in the codebase. The dashboard shows the trend; a human sees the drop; the alert fires on the absolute threshold. Calling that "regression detection" is a slight stretch and I'd rather say it plainly than have you find it.

---

## SECTION 2 — The four evaluators

### 2A. LLM-as-Judge

**Q6. Walk me through the judge.**

> `src/evaluators/llm_judge.py`. A system prompt tells a judge model — default `claude-haiku-4-5-20251001` — to score the response on five dimensions: accuracy, relevance, completeness, clarity, safety. Each 1 to 5. It returns strict JSON, including an `overall` field and a `recommendation` of `PASS`, `REVIEW`, or `FAIL`. I normalise with `(overall − 1.0) / 4.0`, so 1 maps to 0.0 and 5 maps to 1.0. Threshold is 0.60, which is a raw mean of 3.4 out of 5. If `overall` is missing I compute the arithmetic mean of the five dimensions first.

**Q7. `(overall − 1.0) / 4.0`. What does that return if the judge hands you a 0? Or a 6?**

> −0.25 and 1.25. There's no clamp in the formula as I documented it, and the input to that formula is a *free-form JSON field emitted by a language model* — the one thing in the whole system I cannot constrain. Nothing stops a judge from returning `"overall": 0` on a response it hates. So my score column can hold values outside its own declared 0.0–1.0 range, which quietly corrupts every mean and every chart downstream. The fix is two lines: validate the raw score is in `[1, 5]` and reject the judge response as a parse failure if it isn't, then `max(0.0, min(1.0, x))` on the normalised value as a belt-and-braces clamp. I'd take the parse-failure path over the clamp as primary, because a clamp hides a malformed judge and a rejection surfaces it.

**Q8. Your judge emits a `recommendation` field: PASS / REVIEW / FAIL. What consumes it?**

> Nothing that gates. Pass/fail is decided purely by the numeric score against 0.60. So `recommendation` is stored metadata, not control flow. That's actually defensible — I don't want a categorical label from a stochastic model steering a gate — but I should have either used it as a cross-check (flag disagreement between `recommendation=FAIL` and `score >= 0.60` as a case for human review) or dropped the field. Right now it's decoration, and decoration in a rubric encourages the judge to spend attention on it.

**Q9. Five dimensions collapse into one `overall`. Doesn't a 5-for-clarity mask a 1-for-accuracy?**

> Yes, and this is the composite problem reappearing *inside* the judge. If `overall` is the mean of the five, a beautifully-written wrong answer scores accuracy 1, relevance 5, completeness 4, clarity 5, safety 5 — mean 4.0, normalised 0.75, well over the 0.60 threshold. It passes. The mitigation that exists is structural, not internal: the hallucination detector runs separately and catches the factual failure. But *within* the judge, averaging accuracy with clarity is exactly the mistake I refuse to make at the top level. The fix is a floor rule — any dimension scoring 1 or 2 fails the judge regardless of the mean — and safety should be a hard veto, not one-fifth of an average.

**Q10. Why 0.60?**

> I picked it. It maps to a clean raw mean of 3.4 out of 5, which felt like "clearly above mediocre." That's the whole derivation, and it's not good enough — see the calibration question below.

### 2B. Hallucination Detector

**Q11. How does hallucination detection work?**

> `src/evaluators/hallucination.py`. The judge decomposes the response into individual factual claims and labels each against the reference: `SUPPORTED`, `UNSUPPORTED`, or `CONTRADICTED`. Then `hallucination_rate = (UNSUPPORTED + CONTRADICTED) / total_claims`, and `score = 1.0 − hallucination_rate`. Threshold 0.75.

**Q12. Why is UNSUPPORTED counted as a hallucination? It might be true.**

> It might be — and that's the whole point, it's the most important idea in the project. `UNSUPPORTED` explicitly means "cannot be inferred from the reference; may or may not be true." I count it as a defect anyway, because in a RAG system a true-but-unsupported claim means the model answered *from its parametric memory instead of the retrieved context*. It got lucky. Next week, on a query where its memory is stale or wrong, the same behaviour produces a confident lie with no retrieval to blame. So a true statement can absolutely be a hallucination in this framework — I'm measuring *provenance*, not truth.

**Q13. Your denominator, `total_claims`, is produced by a language model. What if it produces zero claims?**

> Then it's a divide-by-zero, and the source doesn't document a guard. `[FILL: confirm whether the code guards total_claims == 0 — check src/evaluators/hallucination.py]`. On a response like "I don't know" or an empty completion, zero extracted claims is a completely realistic input. The correct behaviour is not to return 1.0 — that's the sentinel bug again — it's to return `skipped=True` with an explicit "no claims extracted" reason and route it to human review.

**Q14. Harder version of the same: the denominator is non-deterministic. The judge decides how to chunk.**

> Right, and this is the deepest weakness in the metric. "Paris is the capital of France and has 2 million people" can be decomposed as one claim or two. If the judge splits it into two and one is unsupported, the rate is 0.50. If it merges them, the rate is 1.0 or 0.0. The score moves on a chunking decision the judge makes freshly on every call, with no stability guarantee. I have no measurement of decomposition variance — I never ran the same response through claim extraction N times and looked at the spread. That's the experiment I'd run first if I picked this back up, and it's the number I'd want before I trusted any hallucination score to a decimal place.

**Q15. The local mode — the cross-encoder.**

> For high-volume workloads where per-check API cost matters, the registry in `src/evaluators/registry.py` can swap the judge LLM for a local `cross-encoder/nli-deberta-v3-base` NLI model — 400 MB, needs `transformers` and `torch`. The `BaseEvaluator` interface doesn't change; only the backend does. That's the payoff of the registry pattern: cost-versus-quality becomes a deployment config, not a code change.

**Q16. Does the 0.75 threshold still mean the same thing under the cross-encoder?**

> No, and I don't have evidence that it does. A DeBERTa NLI entailment classifier and a Claude claim-labeller will not agree on the same set of claims, and they certainly won't produce the same score distribution. I kept one threshold across two very different scorers. The correct move is a per-backend threshold, calibrated separately on the same labelled set — which brings us back to the fact that I don't have that labelled set.

### 2C. Faithfulness Scorer

**Q17. How is faithfulness different from hallucination? They sound like the same check.**

> Different reference and different question. Hallucination checks the response against a `reference_answer` **or** a `context`, and asks "is this claim supported anywhere I gave you." Faithfulness — `src/evaluators/faithfulness.py` — requires a `context` specifically, and asks "did the answer stay *inside* the retrieved documents." Score is `SUPPORTED statements / total statements`. Threshold 0.80. Crucially, faithfulness 1.0 does **not** mean the answer is correct — it means the model only used what the retriever gave it. The context itself may be garbage.

**Q18. Then what is it actually for?**

> Two-axis RAG diagnosis, and it's the best thing in the project. Run faithfulness and hallucination together on a golden set and the combination localises the bug: **high faithfulness + high hallucination rate → the retrieved documents are wrong**, go fix the corpus. **Low faithfulness → the model is bypassing the retriever entirely** and generating from parametric memory, go fix the prompt or the model. Neither number alone tells you which team owns the bug. Together they do.

**Q19. What's the score when no `context` is supplied?**

> `score=1.0`, `skipped=True`, and it counts as a pass. And that is the bug I most want to fix in this codebase. `skipped=True` means *"I did not measure this."* AND logic then reads the 1.0 and concludes *"this passed."* Those are not the same statement. A CI job that drops the `context` field — a typo in a workflow YAML, a schema change upstream — gets a green faithfulness score forever and nobody notices, because the gate has no way to distinguish "clean" from "unmeasured." In a *quality gate*, unmeasured must never read as passed. The fix is a third state: `overall_passed` becomes `True` only if every requested evaluator actually **ran** and passed, and any `skipped=True` on an evaluator the caller explicitly requested is a hard error on the test case — you asked for faithfulness and didn't give me context, that's your bug, and I'm going to tell you loudly rather than hand you a 1.0.

**Q20. Why 0.80 for faithfulness but 0.75 for hallucination?**

> The intent was that faithfulness should be stricter, because in a RAG pipeline drifting outside the context is the whole failure mode I'm hunting. But I have to be straight with you: the 5-point gap between them is not derived from anything. It's a feeling. Two adjacent, uncalibrated numbers with a plausible story attached is exactly what calibration is supposed to replace.

### 2D. Consistency Checker

**Q21. How does the consistency checker work?**

> `src/evaluators/consistency.py`. It re-runs the same prompt `N−1` more times concurrently — default `N=5` from `CONSISTENCY_RUNS` — at `temperature=0.7` to deliberately surface sampling variance. Then mean pairwise cosine similarity across all `N(N−1)/2` pairs, so 10 pairs at N=5. Score is that mean. Threshold 0.85: at or above is `STABLE`, below is `INCONSISTENT`. Standard deviation across pairs is stored in metadata.

**Q22. Why do I care? A single judge run said the prompt was good.**

> Because a prompt can score well *once* and be unreliable *in production*. If five calls produce answers where three mention a critical caveat and two omit it, the mean judge score can still look fine, but 40% of your users get an incomplete answer. Single-sample evaluation systematically misses variance. That's the class of failure this catches and nothing else in the framework does.

**Q23. My example test case sent `"temperature": 0.0`. Your consistency checker runs at 0.7. You're testing a model I'm not shipping.**

> Correct, and it's a real design tension I'd defend but not pretend away. The argument for hard-coding 0.7 is that it's a *stress test* — it deliberately amplifies latent instability so you find prompts that are fragile before sampling settings change under you. The argument against is exactly yours: if I ship at 0.0, a 0.7 instability score is measuring a system that doesn't exist, and it can fail a prompt that is perfectly stable in production. The right answer is that it should be configurable per test case, defaulting to the test case's own temperature, with the 0.7 stress run available as an explicit opt-in mode. Two different questions — "is my prompt fragile" and "is my deployed config stable" — currently share one code path.

**Q24. You compute standard deviation across the 10 pairs and call it diagnostic. Those 10 pairs come from 5 samples. Defend that statistically.**

> I can't fully. The pairs are not independent observations — every response appears in 4 of the 10 pairs, so one weird outlier response contaminates 4 pairs at once and the pairwise standard deviation understates the true uncertainty. It's a *correlated* statistic being read as if it were an i.i.d. one. It's fine as a rough signal — high pairwise spread does mean something is unstable — but it is not a confidence interval and I shouldn't present it as one. If I wanted an honest uncertainty estimate I'd bootstrap over the 5 responses, not over the 10 pairs. And 5 samples is a small n for any variance claim regardless.

**Q25. The similarity fallback. Walk me through it and then tell me what's wrong with it.**

> Priority order: if `sentence-transformers` is installed, semantic cosine similarity with `all-MiniLM-L6-v2`, 80 MB, lazy-loaded on first use so it isn't imported at startup. If the package isn't there, automatic fallback to token-level Jaccard similarity, zero extra dependencies. What's wrong with it is the threshold. Jaccard on raw token overlap and cosine in a MiniLM embedding space are not on the same scale — two paraphrases that mean identical things score near 1.0 in embedding space and can score well under 0.5 on token overlap. The same 0.85 line is applied to both. So a deploy that simply doesn't have `sentence-transformers` installed will start failing consistency checks on stable prompts, and — this is the part I dislike most — the fallback is *automatic and silent*, so the on-call engineer sees a wall of red with no signal that the metric definition changed underneath them. The fix is that the scoring backend must be recorded in `eval_scores` metadata, the threshold must be per-backend, and the dashboard should refuse to plot a trend line that changed backends mid-series.

---

## SECTION 3 — Architecture and design decisions

**Q26. Why Celery instead of FastAPI `BackgroundTasks`?**

> Durability. `BackgroundTasks` and `asyncio.create_task()` are in-process — if the API server restarts mid-evaluation, the task vanishes with no recovery path. For a CI/CD quality gate that is unacceptable in a specific way: a lost evaluation job means a PR that should have been *blocked* silently *passes*. The failure mode of the queue is the failure mode of the gate. Celery persists tasks in Redis and retries up to 3 times with a 30-second delay, configured in `src/workers/tasks.py`.

**Q27. Your retry is 3 attempts. The task calls a stochastic LLM. Is that retry safe?**

> Not entirely, and this is a nice catch. A retry re-calls the target model, and unless temperature is 0 that's a *different response*, so attempt 3 is evaluating a different artefact than attempt 1. It's not idempotent. In practice it's tolerable — I want *some* valid response scored, not that exact one — but it means "the same test case ran twice" can legitimately give two different verdicts, and for a gate that's uncomfortable. The clean version is to make the retry boundary correct: retry the *evaluator* calls against a persisted response, and treat a failed *target-model* call as a distinct, separately-retried stage. Right now one retry policy wraps two stages with different idempotency properties.

**Q28. Why the registry pattern instead of `if/elif`?**

> `src/evaluators/registry.py` and `src/llm_clients/registry.py` map string names to instantiated objects. Adding an evaluator means writing a class extending `BaseEvaluator` and registering the name — zero changes to the worker task or the API schema. It's the primary extensibility mechanism, and it's what makes the local-model swap a config decision instead of a code change.

**Q29. That's the standard justification. What did it actually buy you here, specifically?**

> Two concrete things, not hypothetical ones. First, the hallucination detector can be swapped to a local cross-encoder with no interface change. Second, `evaluators` arrives as a *list of strings from an API payload* — `["llm_judge", "hallucination"]` — so it has to be resolved from a string at runtime by design; an `if/elif` chain would just be a worse registry. It earned its place because the dispatch is genuinely dynamic. If it weren't, I'd agree it was a pattern for the sake of a pattern.

**Q30. Why does `eval_scores` live in a JSON column instead of proper tables?**

> Because the evaluator set is the thing most likely to change and I didn't want a schema migration to be the tax on adding one. `eval_scores` is a nested dict keyed by evaluator name, holding `score`, `passed`, `explanation` and raw metadata for each. A new evaluator's results land in the existing column. The cost I'm accepting is real: no referential integrity on evaluator names, no column-level constraints on score ranges — which, as you noticed with `(overall−1)/4`, is exactly where an out-of-range value slipped through — and analytical queries over history require JSON path expressions rather than plain SQL. For a project whose evaluator set was still moving, I'd make the same call. For a mature one I'd promote scores to a proper `eval_scores` table with a `CHECK (score BETWEEN 0 AND 1)` constraint, which would have caught the clamp bug at the database layer.

**Q31. Why async everywhere?**

> The API has to stay responsive while evaluations run for 5–30 seconds. FastAPI plus SQLAlchemy 2.0 async plus asyncpg means no synchronous blocking anywhere in the request path — asyncpg specifically removes the last blocking layer that psycopg2 would have left at the database. Pool is 10 connections with 5 overflow (`db_pool_size=10`, `db_max_overflow=5` in `src/config.py`).

**Q32. Worker concurrency is 4. Consistency at N=5 fires 4 extra LLM calls per test case. Do the numbers work?**

> That's a genuine throughput trap. A single test case with all four evaluators is: 1 target-model call, plus 4 more for consistency, plus a judge call for each of llm_judge / hallucination / faithfulness. Evaluators run *sequentially* in the worker (§4, step 3), so per-test-case latency is the sum, not the max. With 4 workers, a golden suite of any size is bounded by LLM API latency and rate limits, not by my code. `[FILL: the actual observed wall-clock for a full golden-suite run, if you measured one]`. The obvious fix is that the four evaluators are declared *fully independent* — none feeds another — so there is nothing stopping me running them concurrently with `asyncio.gather`. Sequential execution there is pure leftover, and it's the cheapest speedup available in the codebase.

**Q33. Threshold config. `DEFAULT_THRESHOLD` is `0.70`. Which evaluator uses it?**

> None of them. Every evaluator hard-codes its own — 0.60, 0.75, 0.80, 0.85 — and my own config table admits it: "overridden per-evaluator in code." So it's a knob on the dashboard that isn't connected to anything. Worse than useless, because an operator who sets it will believe they changed the gate. Either it becomes the real fallback for evaluators that don't specify one, or it comes out of `.env.example` entirely. Given the four thresholds should be individually tunable anyway, the right shape is `LLM_JUDGE_THRESHOLD`, `HALLUCINATION_THRESHOLD`, and so on, with `DEFAULT_THRESHOLD` deleted.

**Q34. Alerting. Slack fires whenever `overall_passed=False`. What happens on a bad deploy?**

> A flood. There's no deduplication, no rate limit, and no grouping in what I built — every failing test case is its own webhook post. Push a broken system prompt, run a 200-case golden suite, and you've hit Slack 200 times with the same root cause. That's how alerting gets muted, and a muted alert channel is worse than no alert channel because it looks like coverage. The fix is to alert on the *run*, not the *case*: aggregate one message per golden-suite run, with a count and the top failing evaluators, and only page when the failure *rate* crosses a threshold rather than when any single case does.

**Q35. Security. Talk me through the auth model.**

> A single shared secret in the `X-API-Key` header on all endpoints, from `API_KEY` in config. The default in the config table is `dev-secret-key`, which is exactly the kind of default that ends up in production. It's a shared secret with no per-caller identity, no rotation, and no scoping — a CI runner and a curious engineer with a browser have identical rights. That's acceptable for an internal tool behind a network boundary and nowhere near acceptable if it's exposed. Also worth saying: this service holds `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`, so anyone who can POST to it can spend my money — the endpoint is a billing surface, not just a data surface, and that raises the bar on auth well above where I set it.

**Q36. What happens if the target LLM call itself fails or times out?**

> `[FILL: what src/workers/tasks.py does on target-LLM failure — does the TestCase status go to 'failed', and does that surface as an alert or just sit?]` What I can tell you is the shape of the risk: if a target-model failure results in *no* `EvalResult` row rather than a *failed* one, then a CI job polling `GET /api/results` sees nothing — and "no result" must not be allowed to read as "no failure." It's the same class of bug as the skipped-evaluator neutral pass: absence of a measurement must never be silently equivalent to a good measurement.

---

## SECTION 4 — The hard cross-cutting questions

**Q37. THE BIG ONE. Your design doc says "a response that is 95% faithful but contains a hallucinated claim should still fail." Your hallucination threshold is 0.75 — four out of five claims supported scores 0.80 and passes. Your stated principle and your implementation disagree. Which is it?**

> You've found the real contradiction in the document and I'm not going to talk my way around it. §5.5 states the strict principle. §5.2 sets the threshold at 0.75, which explicitly allows "at most 25% of claims non-supported." Those cannot both be true. What §5.5 is actually arguing is the *composition* rule — that I don't average *across* evaluators, so a great judge score can't rescue a bad hallucination score. That argument stands. What it is *not* entitled to claim is that a single hallucinated claim fails the gate, because within the hallucination evaluator itself I *am* averaging — a rate is an average. I smuggled a composite back in one level down and then wrote a principle that denies it.
>
> The defensible position, if I'm honest about which one I'd actually ship: **`CONTRADICTED` and `UNSUPPORTED` are not the same defect and must not share a denominator.** A `CONTRADICTED` claim directly conflicts with the source — that is a *lie*, and one of them should fail the gate outright, count of one, no rate, no threshold. An `UNSUPPORTED` claim is a groundedness *smell* — a rate over those, with a tunable threshold, is completely reasonable. So: hard veto on any contradiction, rate-based threshold on unsupported. That splits the metric along the axis that actually matters, and it makes §5.5's principle *true* instead of aspirational. The current formula, `(UNSUPPORTED + CONTRADICTED) / total`, adds a lie to a gap and divides — and that addition is the actual bug.

**Q38. CROSS-PROJECT. In this framework you use strict AND logic and refuse to compose a weighted score. But in your Bias & Fairness Auditor you *do* use a weighted composite. Which is it? Pick one and defend it.**

> Both, and the choice isn't stylistic — it follows from what's being measured. **Hallucination is a defect. Bias is a gradient.**
>
> A hallucination is discrete and binary at the claim level: the claim is supported by the source or it isn't. There's no meaningful "40% supported" for a single claim. Defects don't average — you don't ship a car with working brakes and a broken airbag on the grounds that it scored 80%. So the composition rule for defects is **conjunctive**: any one failure fails the whole thing.
>
> Bias is not like that. It's a continuous degree of disparity, measured across several noisy demographic axes, where the underlying quantity genuinely *is* a magnitude — a 3% selection-rate gap and a 30% gap differ in degree, not in kind. Aggregating magnitudes with weights is the correct operation on that data, and refusing to aggregate would just mean pretending a 3% gap and a 30% gap are the same event.
>
> The rule I'd state as a principle: **a gate is conjunctive; a measurement is not.** The eval framework is a gate — it blocks a deploy, so it must be conservative, and AND logic is the conservative composition. The bias auditor is a measurement — it produces a magnitude a human reasons about, so it should preserve gradient. Where I got it *wrong* is the boundary between them: as I said in the previous question, my hallucination evaluator internally averages over claims, which means I applied gradient logic *inside* something I declared a gate. The contradiction you should hold me to isn't between the two projects — it's inside this one.

**Q39. Calibration. Where did 0.60, 0.75, 0.80, 0.85 come from?**

> I chose them. Nothing in this project calibrated them. There is no labelled dataset, no human-agreement study, no precision/recall curve, no ROC. I picked numbers with plausible stories — 0.60 is a clean raw 3.4/5, 0.75 means "at most a quarter unsupported," 0.80 is "faithfulness should be stricter than hallucination," 0.85 is "consistency should be strictest." Every one of those stories is post-hoc.
>
> That matters more than it sounds, because the thresholds *are* the product. A quality gate is a threshold with a scorer attached; if the thresholds are arbitrary, the gate's precision and recall are unknown, and an unknown-precision gate in CI either blocks good PRs or waves bad ones through and I can't tell you which.
>
> The fix is a real benchmark and it is not exotic. Take 200 to 300 prompt/response pairs from the target domain, have humans label each as ship / don't-ship — and, for hallucination specifically, label at the claim level. Then run every evaluator across the set, plot precision and recall against threshold, and *pick the threshold from the curve* based on which error you'd rather make. For a CI gate on customer-facing output I'd bias hard toward recall — I'd rather block a good PR than ship a hallucination — and I'd choose the operating point that says so explicitly. Until that exists, the honest description of my thresholds is "reasonable defaults," not "calibrated."

**Q40. Self-evaluation circularity. Your judge is `claude-haiku-4-5-20251001`. Your example targets `"llm_name": "claude"`. A Claude is grading a Claude.**

> Yes, and it's the structural weakness I'd fix first if this went anywhere near a real deploy. Three separate problems stacked on top of each other:
>
> First, **self-preference bias** — a model family scores output that resembles its own generation distribution more generously. My gate would be systematically softer on Claude than on GPT-4o, which quietly poisons the "Model Provider Canary" and "Cost and Model Selection Benchmarking" use cases in §6 — the two use cases whose entire purpose is comparing models fairly. That's not a cosmetic flaw; it means one of my advertised use cases produces a *biased comparison by construction*.
>
> Second, **correlated blind spots** — if the judge and the target share training data and failure modes, the confabulation the target makes is exactly the one the judge finds plausible. The errors aren't independent, so my detector's misses are correlated with the generator's mistakes, which is the worst possible correlation to have.
>
> Third, **provider drift hits both sides** — the framework's headline job is catching a silent model update. But `JUDGE_PROVIDER` and `JUDGE_MODEL` point at the same provider. If Anthropic ships an update, my *measuring instrument* moves at the same moment my *measured system* does, and the drift can cancel out in the score. My ruler is made of the same rubber as the thing I'm measuring.
>
> The mitigations, in order of cost. Cheapest: **pin the judge model to an explicit dated version** — which `claude-haiku-4-5-20251001` already does, that part I got right — and treat any judge-model change as a re-baselining event, not a config tweak. Next: **cross-provider judging** — the registry already supports `JUDGE_PROVIDER=openai`, so grading Claude output with a GPT judge is a one-line env change; the infrastructure is there and I simply didn't default to it. Best: **pin a golden set with known-good and known-bad responses and run it through the judge on every deploy** — if the judge's scores on frozen inputs move, the *judge* drifted, not the model. That's calibrating the instrument, and it's the piece that would make the whole thing trustworthy.

**Q41. The headline number. "4 minutes vs 3 days." Sell it to me and then tell me what's wrong with it.**

> The claim is: a model provider update caused a 14-point faithfulness drop in a RAG pipeline, and the framework detected and flagged it in under 4 minutes, against an estimated 2–3 days for manual review.
>
> Now the caveats, all of which I'd rather say than have you find. The provider update was **simulated** — the source says so plainly. So the 4 minutes is a real wall-clock, but on a synthetic event I constructed, not on a surprise from a real vendor. The "2–3 days" is an **estimate**, not a measurement — I never ran a human panel against the same regression and timed them. And the resume compresses "2–3 days" to "3 days," which takes the generous end of my own guess. So the defensible version of the sentence is: *"on a simulated provider regression, the pipeline surfaced a 14-point faithfulness drop end-to-end in under 4 minutes; the manual-review baseline is an estimate, not a measurement."*
>
> What the number *does* prove is real and worth defending: it's an end-to-end latency measurement of the whole path — submit, queue, worker, four evaluators, database write, Slack — under 4 minutes. That's the pipeline working. It just isn't a controlled comparison against humans, and I won't dress it up as one.

**Q42. So what does the 14-point drop actually tell you?**

> That faithfulness moved by 0.14 on the golden set. `[FILL: the before and after faithfulness scores, and how many test cases were in the golden set]`. The reason I care about the *direction* of that specific metric is the diagnostic I described earlier: a *faithfulness* drop with hallucination roughly flat means the model started reaching outside the retrieved context — it's ignoring the retriever more than it used to. That's a much more precise finding than "quality went down," and it points at a specific owner. That precision is the actual product; the 4 minutes is just the delivery time.

**Q43. Is a 14-point drop on your golden set even statistically significant?**

> I can't tell you, because I never established a variance baseline. Here's the problem in full. The framework runs the target model at a caller-specified temperature, the *judge* is itself stochastic, and claim decomposition is non-deterministic — three independent sources of noise stacked on one score. Without knowing the run-to-run standard deviation of faithfulness on an *unchanged* model, I cannot say whether 0.14 is a regression or a bad Tuesday. I never ran the golden suite five times against a fixed model to establish that floor, and that is a genuine gap, not a nitpick.
>
> It's also completely fixable and it's the first thing I'd build: run the golden suite N times against a pinned model, compute the per-evaluator standard deviation, and *that* becomes the noise floor. Then the alert condition stops being "score dropped below 0.80" and becomes "score dropped by more than 2 sigma from the rolling baseline" — which is what "regression detection" should have meant all along, and is the honest version of my resume bullet. Right now I have absolute thresholds and a trend line, and I'm calling it regression detection. A control chart is what it needs to be.

**Q44. Your framework's whole premise is that LLM output can't be trusted without checking. Every one of your evaluators is an LLM. Doesn't the argument eat itself?**

> It's the sharpest version of the question and it doesn't quite eat itself, for one specific reason: **verification is a strictly easier task than generation.** Asking a model "does this specific sentence follow from this specific paragraph" is a narrow, local, closed-book judgement with the evidence sitting right there in the prompt. Asking it to *produce* a correct answer is open-ended and unconstrained. My evaluators only ever ask the easy question, and I decompose deliberately so each judgement is as small as possible — one claim, one reference, three labels.
>
> But that only *reduces* the problem, it doesn't dissolve it, and I'd be bluffing if I said otherwise. The judge is still stochastic, still uncalibrated against humans, and still — in the default config — from the same family as the thing it's judging. What actually rescues the architecture is that I'm not asking it to be *right*, I'm asking it to be *consistent enough to detect change*. A biased ruler that's biased the same way every time still measures a delta correctly. That's why the *pinned* judge model matters so much, and why my failure to freeze a golden calibration set for the judge is the thing that undermines this defence. Fix that and the argument closes. Leave it and you're right to press.

**Q45. What would you throw away and rebuild?**

> The pass/fail composition layer, and I'd rebuild it in this order. One: split `CONTRADICTED` from `UNSUPPORTED` — a contradiction is a hard veto, unsupported is a rate. Two: make `skipped` a first-class state so "not measured" can never read as "passed." Three: replace the absolute thresholds with a 2-sigma control chart against a measured noise floor. Four: clamp and validate every score at the boundary, ideally with a database `CHECK` constraint so it's structurally impossible to store an out-of-range value. Everything else — the async stack, Celery, the registry, the JSON column — I'd keep as-is. The infrastructure is sound. It's the *semantics of the verdict* that need the work, and that's where I'd spend the next month.

**Q46. What's the thing you're proudest of that isn't the headline number?**

> The two-axis RAG diagnostic. Faithfulness and hallucination look redundant and aren't, and running them together turns "the RAG pipeline is bad" into "the retriever is fine and the corpus is wrong" or "the corpus is fine and the model is ignoring the retriever." That's the difference between an alert and an *assignment* — one wakes someone up, the other tells them what to fix. Almost no eval tooling separates those axes, and it comes directly from being strict about the fact that faithfulness is *not* accuracy.

---

## SECTION 5 — Closing

**Q47. What would you do differently if you started over tomorrow?**

> Build the labelled benchmark *first*, before any evaluator. 200–300 human-labelled pairs. Everything downstream — every threshold, the judge choice, the claim-decomposition strategy, the local-model swap — is a decision I made blind and would have made with evidence. I built the instrument before I built the ruler to check the instrument, and the whole project's credibility hangs on that missing 200 rows.

**Q48. Where would this break first at 100x scale?**

> Not in my code — in LLM API rate limits and cost. A full-evaluator test case is 8 or 9 model calls (1 target + 4 consistency re-runs + judge calls for llm_judge, hallucination, faithfulness), and the four evaluators run *sequentially* in the worker despite being fully independent. First move is `asyncio.gather` across the evaluators, which is nearly free. Second is the local-model path that already exists — the cross-encoder for hallucination, MiniLM for consistency — which trades API cost for a 400 MB and an 80 MB model in the worker image. Third is that consistency is by far the most expensive evaluator per unit of signal, at 4 extra generations, so it should be sampled — run it on 10% of cases, not all of them.

---

## Cheat card — trigger → the exact line to say

| If they say… | Say exactly this |
|---|---|
| "Isn't AND logic too strict?" | "A gate is conjunctive; a measurement is not. This is a gate." |
| "But your bias project averages." | "Hallucination is a defect, bias is a gradient. Defects don't average." |
| "Where did the thresholds come from?" | "I chose them. There's no labelled benchmark. That's the biggest gap in the project and 300 labelled pairs fixes it." |
| "Isn't an unsupported claim maybe just true?" | "It might be true and still be a hallucination — in RAG, unsupported means the retriever got bypassed." |
| "Claude judging Claude?" | "Self-preference bias, correlated blind spots, and my ruler drifts with the thing I'm measuring. `JUDGE_PROVIDER=openai` is a one-line fix and I should have defaulted to it." |
| "4 minutes vs 3 days?" | "The 4 minutes is real end-to-end wall-clock on a *simulated* regression. The 3 days is an *estimate*, not a measurement. I'd rather say that than have you find it." |
| "What if there's no context?" | "Faithfulness returns 1.0 and `skipped=True` — and AND logic reads that as a pass. Unmeasured must never read as passed. That's the bug I'd fix first." |
| "Your normalisation can go negative." | "`(overall−1)/4` with a judge-supplied `overall` of 0 gives −0.25. No clamp. Should be a parse rejection, not a clamp — a clamp hides a malformed judge." |
| "`DEFAULT_THRESHOLD`?" | "Dead config. Nothing reads it. Should be four per-evaluator thresholds instead." |
| "Is your framework's premise self-defeating?" | "Verification is strictly easier than generation. But that only reduces the problem — it doesn't dissolve it." |
| Stuck / don't know | "I don't know — I never measured that. Here's how I'd measure it: …" |

---

## Prep priority

**Tier 1 — must be automatic, no thinking (rehearse out loud):**
- Q37 (threshold contradicts the stated principle — CONTRADICTED vs UNSUPPORTED split)
- Q38 (defect vs gradient — the cross-project answer)
- Q39 (thresholds are uncalibrated; the 300-pair benchmark fix)
- Q19 (skipped=True → 1.0 → silent pass)
- Q40 (self-evaluation circularity; cross-provider judging)
- Q41 (the 4-minutes-vs-3-days honesty pass)

**Tier 2 — know cold, can think for two seconds:**
- Q7 (unclamped normalisation), Q12 (true-but-unsupported), Q17/Q18 (the two-axis RAG diagnostic), Q25 (Jaccard fallback silently changes the threshold's meaning), Q43 (no variance baseline → control chart), Q44 (verification is easier than generation)

**Tier 3 — have the facts ready, don't rehearse:**
- Q26 (Celery durability), Q28/Q29 (registry), Q30 (JSON column), Q31 (async), Q34 (alert flood), Q35 (auth), Q48 (scaling)

---

## [FILL] list

Everything below is something the source report does **not** contain. Do not improvise these in the room — either fill them in from the actual codebase or say "I don't know, I never measured that."

1. `[FILL: does src/evaluators/hallucination.py guard against total_claims == 0?]` — Q13
2. `[FILL: the actual observed wall-clock for a full golden-suite run, if one was ever measured]` — Q32
3. `[FILL: what src/workers/tasks.py does when the target-LLM call fails — does TestCase status go to 'failed', and does that surface as an alert?]` — Q36
4. `[FILL: the before and after faithfulness scores in the 14-point drop, and the golden-set size]` — Q42
5. `[FILL: confirm whether the report's "simulated model provider update" was something you actually ran, or a designed scenario]` — needed to keep Q41 truthful
