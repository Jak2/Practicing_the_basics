# Prompt Regression Suite — Interview Preparation Guide

> **How to present this project in an interview — what to say, how deep to go, and how to demonstrate engineering maturity**

---

## How to Open (The 60-Second Pitch)

When an interviewer says *"Tell me about a project you've built,"* lead with the problem and the impact — not the technology. Tech is the *how*. The problem is the *why*, and that's what lands.

**Say this:**

> "I built a prompt regression testing framework — think pytest for prompts. The problem it solves is one every team shipping AI features eventually hits: a developer cleans up a prompt, the unit tests are green, CI passes — and then a week later something quietly breaks in production. The model starts giving shorter answers, stops citing sources, or an AI provider silently updates their base model and behavior shifts. None of that shows up in traditional tests. It shows up in user complaints three weeks later.
>
> My solution treats prompts as first-class software artifacts. Each prompt file gets a behavioral test suite defined in a version-controlled YAML file. Every PR that modifies a prompt triggers those tests in GitHub Actions. If quality drops below a stored baseline, the merge is blocked — before the regression reaches users.
>
> The system uses a tiered evaluation pipeline: cheap deterministic rule checks run first, local semantic similarity second, and an AI judge only as a last resort — which cuts evaluation API costs by roughly half. It supports Anthropic, OpenAI, and local Ollama models, with a Streamlit dashboard for tracking quality trends over time."

**Why this works:**
- Opens with a concrete, recognizable problem that any engineer who's worked on AI features will immediately relate to
- "pytest for prompts" is a single phrase that frames the entire concept
- Mentions three distinct capabilities before naming a single technology
- "blocks the merge before it reaches users" signals deployment gate thinking, not just test runner thinking

---

## The Architecture Question

**Interviewer:** *"Walk me through the architecture."*

**Answer:**

> "The system is organized into six bounded layers. The entry point is a Registry — it glob-walks a directory for `.prompt-test.yaml` files, parses each through Pydantic v2 validation at load time, and builds two indexes: a forward map from test case ID to the test case, and a reverse index from prompt file path to test case IDs.
>
> The reverse index is the key to efficient CI. When GitHub Actions triggers on a PR, `detect_affected.py` runs first — it gets the changed file list from `git diff`, queries the reverse index, and returns only the test cases that reference those modified prompt files. A PR touching 3 of 80 prompts runs roughly 12 tests, not 80.
>
> The Runner orchestrates execution asynchronously using `asyncio`. It uses `asyncio.Semaphore` to cap concurrent LLM calls, respecting rate limits without serializing everything. Each test case runs three times and scores are averaged — because a single LLM response at temperature 0.7 is an unreliable signal.
>
> The AssertionEngine evaluates each response through three tiers: rule-based checks first (free and deterministic), semantic similarity second (local model, no API cost), and an LLM judge last (paid, only if the first two pass). Fail-fast: if a rule check fails, the judge never fires.
>
> Results are compared against stored baselines. Regression fires when the mean score drops more than 0.05 below the stored baseline. Everything persists to SQLite or PostgreSQL — same ORM models for both, one environment variable to swap."

**If they push deeper on the CI integration:**

> "There are two GitHub Actions workflows. The PR workflow triggers on changes to `prompts/**` or `tests/**/*.yaml`. It runs detect → suite → post PR comment → exit non-zero if regressions. The PR comment names each regressed test, its current score, its baseline, the delta, and the judge's one-line verdict. The second workflow runs every Monday at 09:00 UTC on the main branch — full suite, no selective filtering. This is the drift monitor: it catches silent base model updates from AI providers that would never trigger a PR run because no code changed."

---

## The Technical Depth Question

**Interviewer:** *"What's the most technically interesting part of this project?"*

Lead with whichever you feel most confident explaining in depth.

### Option A: The LLM-as-Judge Design

> "The judge is the most carefully engineered component. Three non-obvious design decisions.
>
> First: the system prompt literally ends with 'Begin your response with the opening brace {'. That's not cosmetic — free-text preamble before JSON is a common silent failure mode at scale. A model often responds 'Sure, here's my evaluation:' followed by the JSON. That breaks every parser that assumes the response starts with `{`. Ending the prompt with that constraint forces the model to open with the brace.
>
> Second: I throw away the judge's reported overall score and recompute it client-side. The judge provides four dimension scores — instruction following, factual accuracy, format compliance, tone — with fixed weights. But LLM arithmetic is unreliable. The judge might score instruction_following at 0.9, factual_accuracy at 0.2, but report an overall of 0.82 that doesn't match the weighted formula. Recomputing client-side means regression decisions are never based on the judge's math.
>
> Third: anti-self-bias routing. A model evaluating its own outputs introduces systematic bias toward responses in its own style. The factory enforces that Claude-tested prompts are judged by OpenAI and vice versa — structurally, in the constructor, not as a comment in the README."

### Option B: The Three-Rule Baseline Policy

> "The baseline management policy is what makes the system trustworthy over time rather than just accurate at a point in time.
>
> Rule 1: baselines update automatically on every merge to main. When a prompt improves and the PR passes, the new higher score becomes the next baseline — automatically.
>
> Rule 2: PR runs never update baselines. If they did, a single PR run would immediately overwrite the stored score, and the regression would be forgotten before the PR closed.
>
> Rule 3: forced resets require a documented reason. `force_reset()` raises a ValueError if the reason string is empty or whitespace. The reason is stored in the database alongside the score, commit SHA, and timestamp. 'We intentionally shortened responses for mobile' is a valid reason. An empty string raises an exception at every interface layer — CLI, API endpoint, and dashboard form all call the same method.
>
> Without Rule 1, every quality improvement is flagged as a false positive forever. Without Rule 2, regressions are forgotten the moment they're measured. Without Rule 3, teams silently paper over regressions by resetting baselines. The three rules together are the minimum viable governance that makes the system both sensitive and trustworthy."

### Option C: The Tiered Assertion Engine

> "The assertion engine is an example of cost-aware system design applied to AI evaluation. I order assertions by cost: deterministic rule checks run first at zero cost, local semantic similarity runs second at 5 milliseconds with no API call, and the LLM judge runs last as a paid API call.
>
> The fail-fast logic is the key design decision: if any rule check fails, the engine stops immediately. No semantic check runs. No judge fires. A test case that fails a keyword check costs exactly zero API budget.
>
> Across a mixed-assertion test suite, this cuts evaluation costs by roughly half — because most regressions are detectable without needing an AI model to evaluate them. The citation drop failure mode, for example, is detectable with a single `not_contains` assertion for 'I cannot' and a `contains_keyword` assertion for 'billion' — free, instant, deterministic.
>
> Each assertion carries a configurable weight. The financial analyst test assigns the LLM judge weight 2.0 — double keyword checks — because judge quality is the most important signal for factual verification. The final score is a proper weighted mean, not a simple average. This means test designers can express which assertions matter most for their specific use case."

---

## The Decision Question

**Interviewer:** *"Why Python? Why asyncio? Why SQLite as default?"*

> "Python was the only real choice because the AI/ML ecosystem is Python-native. `sentence-transformers` for local semantic similarity, the official Anthropic and OpenAI SDKs, the data tooling — none of these have equivalent alternatives in JavaScript or Go. Using another language would mean wrapping or reimplementing libraries that simply don't exist there.
>
> asyncio was the right concurrency model because the workload is I/O-bound — the bottleneck is waiting for LLM API responses, not computation. `asyncio.Semaphore` lets me run multiple test cases concurrently while respecting rate limits, without the overhead of thread pools or multiprocessing. A 10-test suite that takes 90 seconds serially finishes in around 15 seconds at the default concurrency cap of 10.
>
> SQLite as default was a developer experience decision. The goal was: clone the repo, install requirements, run `prs run`. No Docker Compose prerequisite, no PostgreSQL setup, no separate process running in the background. SQLite is built into Python and stores the entire database in one file. The PostgreSQL upgrade path is a single environment variable — `DATABASE_URL=postgresql+asyncpg://...` — because the same SQLAlchemy 2.0 async ORM models work with both backends without any code changes."

---

## The Trade-Offs Question

**Interviewer:** *"What are the trade-offs in your architecture? What would you change at scale?"*

> "The biggest trade-off is the 3× API cost from multi-run averaging. Running each test case three times reduces stochastic noise significantly, but it triples the API budget. At small scale that's fine. At a team with 500 test cases, running three times each is a real cost line.
>
> My planned mitigation is adaptive run counts: start with 1 run, escalate to 3 only if the score falls within the delta threshold margin. Most test cases pass or fail decisively — they don't need averaging. Only borderline scores where the difference between pass and regression is within 0.05 actually benefit from multi-run averaging. This could reduce the averaging overhead by 60–70% at scale.
>
> The second trade-off is SQLite for local dev. It's excellent for zero-friction setup but doesn't handle concurrent write operations safely. The moment you run two `prs run` processes simultaneously — common in a team environment where multiple engineers are running local tests — you hit write contention. The production path, PostgreSQL via one env var, solves this. But the setup docs need to be very clear that SQLite is development-only.
>
> Third: the 30% threshold for triggering a full suite run is somewhat arbitrary. A team that reorganizes their prompt directory in a single PR would correctly trigger the full suite. But a team that simply adds 30% new prompts in one PR also triggers it, which might be unexpected. I'd make this threshold configurable and document it prominently."

---

## The Challenges Question

**Interviewer:** *"What was the hardest part to build?"*

> "Getting the LLM judge prompt engineering right took several iterations. My first version produced scores but the reported overall was inconsistent with the dimension scores — the model was computing the weighted average incorrectly, or not at all. I'd get instruction_following=0.9, factual_accuracy=0.2, and an overall of 0.82 that matched neither a simple average nor the weighted formula I specified.
>
> The fix had two parts: first, be very explicit in the prompt about the exact weights and formula — don't assume the model will infer it. Second, recompute the overall client-side and throw away the model's reported value entirely. The lesson is: never trust LLM arithmetic for critical evaluation logic when you can compute it yourself.
>
> The second hard part was JSON output reliability. Early versions would produce preamble text before the JSON — something like 'Sure, here's my evaluation:' followed by the JSON object. That silently breaks every downstream parser. The parser gets a string that starts with 'S', not '{', and fails. The fix was ending the system prompt with 'Begin your response with the opening brace {' — a concrete, unambiguous constraint rather than 'return only JSON', which the model sometimes interpreted loosely."

---

## The Business Thinking Question

**Interviewer:** *"This seems like a developer tool. What makes it valuable to a business?"*

> "It's valuable to a business precisely because the failures it catches are invisible to businesses until they've already caused damage. When a prompt change silently degrades response quality, the signal doesn't appear in unit test results or error logs — it appears in customer support tickets three weeks later, or in a churn increase, or in an NPS drop. By that point, the change that caused it has been buried under five more releases.
>
> The tool converts a class of invisible risk into a visible, automatable gate. The specific value proposition: a developer who makes a prompt change knows within minutes whether it degraded quality for any existing test case, before the change reaches users. That's the same value proposition as unit tests for logic — the reason the industry adopted them wasn't philosophical, it was that catching bugs before deployment is dramatically cheaper than catching them after.
>
> The weekly drift monitor adds another business dimension: catching provider changes. When OpenAI or Anthropic updates a base model, companies currently find out through user behavior, not through their own monitoring. A scheduled regression run means you find out on Monday morning, not through customer complaints on Friday afternoon."

---

## Common Follow-Up Questions

**"How does the change detection work exactly?"**
> "`ci/detect_affected.py` calls `git diff --name-only` against the PR base branch to get the list of changed files. It then queries the Registry's reverse index — a dictionary from prompt file path to a list of test case IDs — and returns only the test cases referencing those files. Path normalization (forward vs. backslash) handles cross-platform CI agents. If more than 30% of tracked prompt files changed, it sets `should_run_full_suite: true` instead of returning a partial list."

**"What happens if the judge returns malformed JSON?"**
> "`_parse_judge_response` wraps the `json.loads()` call in a try/except. If it fails, it returns a failed `AssertionResult` with score 0.0 and the exception message as the explanation. There's also a strip that handles accidental markdown fencing — models sometimes wrap JSON in ` ```json ``` ` despite the system prompt. On any parse failure, the suite run continues — one judge failure doesn't crash everything."

**"How do you prevent regressions from silently becoming the new baseline?"**
> "Rule 2 of the baseline policy: PR runs never update baselines. Only runs triggered on the main branch — after the PR has passed and merged — call `update_baselines_from_run()`. A PR that causes regressions is blocked from merging by the exit code 1 in the CI step, so it can't reach main and can't advance the baseline. The only way a regression score becomes a new baseline is if the developer intentionally merges a degraded PR and then also intentionally calls `force_reset()` with a documented reason."

**"Could you use this framework for non-prompt evaluation?"**
> "The core mechanism — YAML-defined test cases, tiered assertions, baseline comparison, CI integration — is general enough that you could apply it to any non-deterministic system output. LLM prompts are the obvious use case, but the same pattern applies to: RAG retrieval quality, function-calling response validation, chatbot conversation flow testing, or any output where 'correct' is a spectrum rather than a binary. You'd replace the prompt template + variables system with whatever your system takes as input."

**"How would you add a new assertion type?"**
> "Add the type string to `RULE_BASED_TYPES` in `rule_based.py` and implement a handler function with the signature `(response: str, config: AssertionConfig, context: dict) → AssertionResult`. Register it in the dispatch table in `engine._evaluate_one()`. The YAML schema is open — `AssertionConfig` uses Pydantic's model with optional extras, so new assertion-type-specific fields are additive and don't break existing test files."

---

## Key Numbers & Facts to Have Ready

| What | Detail |
|---|---|
| Language | Python 3.11 |
| Async model | `asyncio` + `asyncio.Semaphore` |
| Assertion tiers | 3: rule-based (12 types) → semantic similarity → LLM judge |
| Semantic model | `all-MiniLM-L6-v2` (80MB disk, ~22MB RAM, 384-dim, ~5ms per pair) |
| Default run count | 3 runs per test case, scores averaged |
| Flakiness threshold | std_dev > 0.05 across run iterations |
| Default delta threshold | 0.05 (5-point drop triggers regression) |
| Judge scoring dimensions | IF=0.40, FA=0.30, FC=0.20, TA=0.10 |
| Critical failure | Any single dimension < 0.40 fires regardless of overall |
| Judge temperature | 0.0 — deterministic scoring |
| Anti-bias routing | `claude-*` → OpenAI judge; `gpt-*/o1/o3/o4` → Anthropic judge |
| Storage ORM tables | 4: test_cases, test_runs, test_results, baselines |
| Database | SQLite (default, zero setup) → PostgreSQL (one env var) |
| CI workflows | 2: PR gate (selective), weekly drift monitor (full suite, Monday 09:00 UTC) |
| Full-suite trigger | >30% of tracked prompt files changed in one PR |
| PR artifact retention | 30 days |
| Weekly artifact retention | 90 days |
| Supported providers | Anthropic (Claude), OpenAI (GPT series), Ollama (local) |
| Dashboard | Streamlit, 5 views, direct DB reads (no API dependency) |
| API | FastAPI, auto-generated Swagger at /docs |

---

## The One-Sentence Closer

If the interviewer asks you to summarize in one sentence:

> "This project demonstrates that I can identify invisible failure modes in production AI systems, design cost-aware evaluation infrastructure, and build governance mechanisms that make that infrastructure trustworthy over time — not just correct on day one."

---

*Rehearse answers out loud. The goal is not to memorize scripts but to internalize the reasoning so you can answer any follow-up confidently from first principles.*
