# Prompt Regression Suite — Interview Q&A

**Resume bullet under test:**
> "Prompt Regression Suite: CI/CD test suite for LLM prompts — catches breaking changes before production, cuts API costs 50%. Stack: Python, pytest."

Everything below is traceable to `Prompt_Regression_Suite_Report_FULL_PROJECT_REPORT.md` (v1.0, June 2026). Anything the report does not substantiate is marked `[FILL: ...]`. **Do not improvise over a [FILL] in the room. Say "I'd have to check my notes" — that is survivable. A fabricated number is not.**

---

## READ THIS FIRST — where this project is actually attackable

| # | The question that hurts | Why it hurts | Your one-line posture |
|---|---|---|---|
| 1 | "You wrote *cuts API costs 50%*. Fifty percent versus what baseline, measured how?" | The report says **"Estimated cost reduction from fail-fast: ~50%"** and **"~50% across a mixed-assertion test suite"**. The word is *estimated*. There is **no measurement methodology anywhere in the source.** This is the single most dangerous line on the resume. | "It's a modelled estimate from the fail-fast tier ordering, not a metered A/B. Let me show you the model — and let me be precise that the resume word should be 'estimated'." |
| 2 | "What is your test oracle? The system is non-deterministic — exact match is impossible. So what are you actually asserting against?" | This is the intellectual core of the whole project. If he fumbles it, nothing else matters. | "There is no stable oracle, so I stopped chasing one. I assert on a **distribution relative to its own past**: mean of 3 runs vs. the stored baseline, regression only if it drops more than `delta_threshold` (0.05)." |
| 3 | "std_dev > 0.05 = flaky. delta_threshold = 0.05. judge weight 2.0. Where did those numbers come from?" | The source states them as **defaults** and never shows a calibration study. The report itself concedes the 30% full-suite threshold is *"somewhat arbitrary."* | "They're engineering defaults, not calibrated constants. I have no labelled ground-truth set of known-good/known-bad prompt changes to fit them against. That's the honest gap." |
| 4 | "A flaky test is worse than no test. What happens when std_dev is 0.06 — does the build fail?" | The source says flakiness is only **flagged in the results table**. It does *not* say a flaky test is quarantined or excluded from the merge gate. So a noisy test can still block a PR. | "Today flakiness is a *label*, not a gate. That's a real design hole — the fix is to make high-variance tests advisory-only until they stabilise." |
| 5 | "Your judge is an LLM. Who regression-tests the judge? When OpenAI ships a new GPT, your oracle moves." | The whole premise of the project is model drift — and the judge itself runs on a drifting model. The source never pins the judge model version or baselines the judge. | "That's the recursion at the heart of it. `temperature=0.0` and client-side score recomputation reduce the variance, but they don't pin the judge model. The judge is an unversioned dependency and I'd fix that with a golden-set canary." |
| 6 | "Nothing stops a developer from tuning the prompt until the test passes. Isn't this just overfitting to your test set?" | The source has **no held-out set, no test/eval split, no hidden cases.** The reference answers and keywords are in the same repo as the prompt. | "Correct. There is no holdout. The suite prevents *unintentional* regression; it does not prevent *deliberate* overfitting. Rule 3 audit trails are governance, not a defence against that." |
| 7 | "Your resume says pytest. Your architecture says Typer, FastAPI, SQLAlchemy, Streamlit. Which is it?" | The 400+ line report **never mentions pytest once.** The resume line names it as the stack. That's a credibility crack in the first ten seconds. | "The resume line is compressing 'pytest-*style*' — the framing is 'pytest for prompts'. The runner is my own async Typer CLI, not pytest. I should reword the bullet." |

---

## 1. Framing

**Q: Give me the thirty-second version.**

> It's pytest for prompts. Traditional tests verify logic and types; this verifies *meaning* — whether a prompt still behaves the way the team specified. Three pieces: a tiered assertion engine that escalates from free deterministic rules, to a local semantic-similarity check, to a paid LLM-as-judge; a GitHub Actions gate that blocks a PR merge when a prompt's score drops below its stored baseline; and a Streamlit + Plotly dashboard for quality trends over time. Python 3.11, an API key, and nothing else — no Docker, no cloud DB.

**Q: What problem does it actually solve? Give me the failure it prevents.**

> Three concrete failure modes, and they're all invisible to normal CI. **Silent shortening** — someone refactors a verbose system prompt to be cleaner, unit tests pass, and the model quietly starts giving shorter, less detailed answers; nobody notices for two weeks and then only through user complaints. **Citation drop** — a financial-analyst prompt gains a new instruction, the model now attends to it and stops citing sources it used to cite, and unverified assertions reach customers. **Model drift** — the provider silently updates the base model between API versions; tone shifts, output length drifts, JSON key order changes. No code changed at all. The failure arrived *through the API*.

**Q: Why isn't this solved by existing tools?**

> Manual spot-checking doesn't scale past a handful of prompts. Ad-hoc eval scripts aren't version-controlled, aren't in CI, and aren't comparable across releases. And paid evaluation platforms require sensitive data to leave the org — which for a lot of teams is a hard no. The gap I filled: prompts as first-class software artifacts. Each prompt file gets a behavioural test suite in a version-controlled `.prompt-test.yaml`, and every PR touching that prompt runs it.

**Q: Who was this for? Did anyone use it?**

> [FILL: was this a personal/portfolio project, or was it deployed on a real team? The source report describes it as a system built to solve a real engineering pattern but never names a user, team, or deployment. Be honest — "built as a portfolio system modelled on failure patterns I've seen" is a perfectly strong answer and far safer than implying users you don't have.]

---

## 2. The Assertion Engine — the three tiers

**Q: Walk me through the three tiers.**

> `src/assertions/engine.py` sorts every assertion in a test case by cost tier before executing. **Tier 0** is 12 rule-based types — zero cost, deterministic: `contains_keyword`, `not_contains`, `max_words`, `min_words`, `valid_json`, `json_contains_key`, `starts_with`, `not_starts_with`, `language_is`, `regex_match`, `response_time_under`, and `reading_level` (Flesch–Kincaid inside a `[min, max]` band). **Tier 1** is local semantic similarity — `all-MiniLM-L6-v2` cosine similarity against a reference answer, roughly 5ms, zero API cost. **Tier 2** is the LLM judge — a paid API call, and it only fires when tiers 0 and 1 have already passed.

**Q: What is fail-fast buying you, mechanically?**

> If any Tier 0 assertion fails, the engine stops immediately — no semantic check, no judge call. A test that fails a keyword check costs exactly zero API budget for that run. That's the entire cost story: the expensive check is *conditional on the cheap checks passing*.

**Q: The obvious criticism of fail-fast — you're throwing away information.**

> Yes, and the report names it in the trade-offs table: *"expensive checks aren't evaluated in isolation."* If Tier 0 fails I never learn what the judge would have said. So when a test regresses, I know it broke a rule but I don't get the judge's diagnosis of *why*. In a debugging pass that's exactly the information you want. If I were extending it I'd add a `--no-fail-fast` diagnostic mode that runs all tiers regardless, for the human who's actually investigating — and keep fail-fast on for CI where the budget matters.

**Q: How do you get one number out of a mixed bag of assertions?**

> Weighted mean: `sum(score × weight) / sum(weight)`. Every assertion carries a configurable `weight`, default 1.0. The financial-analyst test gives the LLM judge `weight: 2.0` — double a keyword check — because for factual verification the judge is the signal that matters most. Weights are YAML-configurable, not hardcoded.

**Q: `weight: 2.0` — why 2.0 and not 1.5 or 3.0?**

> Honestly: judgement, not calibration. I picked 2.0 because I wanted the judge to dominate the two keyword checks in that test, and 2.0 was the round number that did that. I have no ground-truth dataset of "prompt changes a human called a regression" to fit the weight against. That's the real answer, and it's the same answer for `delta_threshold`, for `std_dev > 0.05`, and — the report says this out loud — for the 30% full-suite threshold, which it calls *"somewhat arbitrary."* If I had a labelled set of, say, 100 prompt diffs each marked regression/not-regression by a human, I'd fit these to maximise F1 instead of guessing. I don't. That's the honest limit of the system.

**Q: Doesn't a weighted mean let a catastrophic failure hide behind good scores?**

> It does, and that's exactly why the judge has a separate `critical_failure` flag. If **any single dimension scores below 0.40**, `critical_failure: true` fires *regardless* of the overall weighted score. A response can score 0.75 overall while fundamentally failing on factual accuracy — the mean would swallow that, so the flag surfaces it to the dashboard and the PR comment independently of the score.

**Q: Then what does `critical_failure` actually *do*?**

> In the source it *surfaces* — it goes to the dashboard and the PR comment. [FILL: confirm whether `critical_failure: true` also fails the CI exit gate. The source's exit gate reads `ci_results.json` and exits 1 only on `has_regressions: true`. If critical_failure doesn't feed that flag, then a critically-failing response whose weighted mean stayed within delta of baseline can still merge — say so plainly; it's a sharp catch and owning it beats being caught by it.]

---

## 3. The LLM-as-Judge

**Q: You're using an LLM to grade an LLM. Convince me that isn't circular.**

> It's circular unless you break the symmetry, so I broke it in four places. **One — different provider.** `src/llm/factory.py` routes by model-name prefix: anything `claude-*` is judged by OpenAI; anything `gpt-*`, `o1`, `o3`, `o4` is judged by Anthropic. A model evaluating its own output is systematically biased toward text that matches its own generation patterns. And this is enforced *structurally* — `Runner.__init__` constructs `_test_client` and `_judge_client` separately, so it's a construction-time property, not a line in a README. **Two — `temperature=0.0`** on the judge, so the scoring itself is as deterministic as the API allows. **Three — I throw away the judge's arithmetic**, which I'll come back to. **Four — a fixed rubric**, not an open-ended "rate this out of 10."

**Q: The rubric.**

> Four dimensions with fixed weights: `instruction_following` at 0.40, `factual_accuracy` at 0.30, `format_compliance` at 0.20, `tone_appropriateness` at 0.10.

**Q: Those four weights — same question as before. Calibrated?**

> Same honest answer: chosen, not calibrated. The ordering encodes a belief — that following instructions matters more than tone — and I'd defend the *ordering* anywhere. The exact 0.40/0.30/0.20/0.10 split is a reasonable prior, not a fitted result. [FILL: if you did sanity-check these against any set of examples, say so specifically; if not, do not imply you did.]

**Q: "I throw away the judge's arithmetic." Explain.**

> The judge returns a 4-dimension JSON score *and* an `overall`. I discard the `overall` entirely and recompute client-side: `sum(dim_score × dim_weight for dim, dim_weight in DIMENSION_WEIGHTS.items())`. LLM arithmetic is unreliable — a model will happily score `instruction_following` 0.9 and `factual_accuracy` 0.2 and then report an `overall` of 0.82 that doesn't correspond to any weighting. If that number feeds a merge gate, you have a gate that lies. So the judge's job is narrowed to what LLMs are actually good at — *judging* — and the arithmetic goes to Python, which is good at arithmetic.

**Q: How do you stop the judge from wrapping its JSON in prose?**

> The system prompt ends with the literal instruction: *"Begin your response with the opening brace {"*. That's not cosmetic. Free-text preamble before JSON — "Sure, here's my evaluation: {" — is a classic silent failure at scale. Constraining the first character to `{` means any malformed response is *immediately* detectable rather than half-parsed. And `_parse_judge_response` in `src/assertions/judge.py` handles both `json.JSONDecodeError` and accidental markdown fencing — ```` ```json ... ``` ````. On any parse failure it returns a *failed* `AssertionResult` with the error text as the explanation, and the suite continues. One judge failure doesn't take down the run.

**Q: A parse failure returns a FAILED assertion result. Isn't that a silent false positive? The prompt might be fine — your parser broke.**

> That's a genuinely sharp catch and yes, it's a real flaw. A judge that returns malformed JSON scores as a *failure of the prompt under test*, which is wrong — it's a failure of the judge, and those are different events. In a mixed-assertion suite that could pull the weighted mean below baseline and block a PR for an infrastructure hiccup. The right model is three-valued: pass / fail / **errored-and-therefore-unscored**, with errored assertions excluded from the weighted mean and surfaced separately. The `TestResult` model already has an `error` field and `SuiteRun` already counts `errored` separately at suite level — so the concept exists; it just isn't threaded down to the individual assertion. That's the fix, and it's small.

**Q: Who tests the judge?**

> Nobody, today. That's the recursion in this project and I'll name it before you do: my oracle is itself a drifting LLM behind a vendor API. If OpenAI ships a new GPT, my judge's scoring distribution can shift, every baseline in the database becomes subtly stale, and I'd see a suite-wide score movement that looks like prompt regression but is actually judge drift. Mitigations I have: `temperature=0.0` and client-side recomputation, which cut variance but do not pin the model. Mitigation I *don't* have and would build first: a **golden set** — a handful of frozen response/score pairs that a human has scored, run through the judge on every suite execution. If the judge's scores on the frozen set move, the alert is "your oracle moved," not "your prompts broke." Without that, a judge-drift event and a real regression are indistinguishable in my dashboard.

**Q: Is the judge model version pinned?**

> [FILL: the source never names a specific judge model or version — it only gives routing by prefix (`claude-*` → OpenAI, `gpt-*`/`o1`/`o3`/`o4` → Anthropic). State plainly whether you pinned a dated snapshot like a `-2024-xx-xx` model string or used a floating alias. If it floats, that is a real bug on a *drift-detection* tool and you should say so.]

---

## 4. Non-determinism, flakiness, and the oracle

**Q: The central question. The system under test is non-deterministic. Exact match is impossible. So what *is* your test oracle?**

> There isn't one, and accepting that was the design. Any prompt test that asserts "output equals X" is dead on arrival, because at `temperature=0.7` the same input legitimately produces different output every run. So I stopped asserting on *the output* and started asserting on *a distribution, relative to its own past*. Concretely: run the test case `run_count` times — default 3 — average the scores, and compare the **mean against the stored baseline**. Regression fires when `mean_score < baseline_score − delta_threshold`, default delta 0.05. **Absolute score levels don't matter at all.** A test case that consistently scores 0.78 does not flag when it scores 0.76. It flags when it drops to 0.73 or below. The oracle isn't a correct answer; the oracle is *yesterday's behaviour of this same prompt*.

**Q: Why not just set an absolute quality threshold — "must score above 0.8"?**

> Because fixed thresholds break as prompts improve. A prompt that legitimately improves from 0.82 to 0.91 has to be able to *keep* that. With a fixed bar you either set it low enough to be meaningless or you're constantly hand-editing it. Delta comparison lets the baseline ratchet upward when you merge to main, while still catching drops from wherever the prompt currently sits. That's the whole reason the three-rule baseline policy exists.

**Q: 3 runs. Standard deviation over three samples is a terrible variance estimate.**

> Statistically, yes — three samples gives you a very noisy std_dev, and I'm not going to pretend otherwise. Three is a *cost* compromise: multi-run averaging already costs 3× the API budget of a single run per test case, and that's in the trade-offs table. What it buys is not statistical rigour, it's a crude noise floor — enough to stop a single unlucky sample from blocking a merge. If I wanted defensible variance I'd need something like 10+ runs per case, and the API bill for that on a full suite is the reason I didn't. The `run_count` is per-test-case configurable in the YAML, so a genuinely borderline high-stakes test *can* be given more runs — that's the escape hatch.

**Q: You said 3 runs is a cost compromise. So you're 3×-ing cost while the resume claims a 50% cost cut. Reconcile those.**

> They're independent axes and I should be careful not to blur them. Multi-run averaging *multiplies* the cost per test case by `run_count`. Fail-fast tier ordering *divides* it, by skipping the paid judge whenever a free check has already failed. The ~50% figure in my report is attributed specifically to fail-fast, against a hypothetical suite where every assertion including the judge always runs. It is not a claim that my suite costs half of what my suite used to cost. That distinction matters and the resume line doesn't make it.

**Q: std_dev > 0.05 flags a test as flaky. Then what happens?**

> It gets flagged in the results table. And that's the honest end of the sentence — flakiness is a **label, not a gate.** A test that scores 0.95, 0.60, 0.88 across three runs is not a reliable regression signal, it's noise, and the report says as much: it needs tighter prompting or more runs. But nothing in the pipeline *stops that test from blocking a merge.* Its mean could land below `baseline − 0.05` purely by chance and the exit gate exits 1.

**Q: So a flaky test can block a merge. That's the classic "a flaky test is worse than no test" failure. What's the fix?**

> Conceding it fully: yes, that's a real hole, and it's the one that would bite a real team first — because the failure mode of a flaky merge gate isn't a bad merge, it's that engineers learn to ignore the gate. Three fixes in order of how cheap they are. **One: quarantine.** If `std_dev > 0.05`, the test's verdict becomes advisory — it posts to the PR comment but does not feed `has_regressions`, so it can't exit 1. **Two: escalate instead of fail.** A test whose mean lands within the noise band shouldn't be a verdict at all; it should be a trigger to re-run at higher `run_count` and *then* decide. The report already sketches that under scalability as *"adaptive run counts"* — start at 1 run, escalate to 3 only for borderline cases — and the same machinery runs backwards for the flaky case. **Three: widen `delta_threshold` per test as a function of its own observed std_dev**, so a naturally noisy test needs a bigger drop to trigger. None of these are built. Number one is an afternoon's work and I'd do it before anything else on the list.

**Q: `delta_threshold = 0.05`. Where does 0.05 come from?**

> It's a default I chose, not a number I derived. Same category as `std_dev > 0.05` and the 30% full-suite rule the report itself calls arbitrary. What I'd say for it: it's per-test-case overridable in the YAML, so it's a *default* rather than a constant, and a high-stakes test can tighten it. What I won't claim: that 0.05 is the value that maximises true positives against false positives on any dataset, because I never had that dataset.

**Q: Notice that your flakiness threshold and your regression threshold are the same number — 0.05. That means your noise band and your signal band are identical.**

> That's a genuinely uncomfortable observation and it's correct. If the natural run-to-run std_dev of a test is right at 0.05, and a regression trigger is a 0.05 drop in the mean, then the signal I'm trying to detect is the same magnitude as the noise I've declared tolerable. Statistically those numbers should not be equal — the regression threshold ought to be some multiple of the observed noise, per test case, not a shared global constant that happens to be the same value. That's the single sharpest technical criticism of the system and I don't have a defence beyond "they were both reasonable-looking defaults, and I never noticed they collided." The fix is the per-test adaptive delta I mentioned: `delta_threshold = k × observed_std_dev`, floor 0.05.

---

## 5. The 50% cost claim — the resume's weakest point

**Q: "Cuts API costs 50%." How did you measure that?**

> I need to be precise and slightly uncomfortable here, because the resume line is stronger than my evidence. My own report says, verbatim, *"Estimated cost reduction from fail-fast: ~50%"* and *"~50% across a mixed-assertion test suite."* The operative word is **estimated**. It is a *modelled* figure derived from the tier architecture, not a metered before/after A/B on a real workload with real invoices. The resume compresses "estimated ~50%" into "cuts 50%", and that compression is doing work I can't back up. If you want the honest version of that bullet, it's: *"tiered fail-fast assertion ordering, modelled to roughly halve judge-call volume on a mixed-assertion suite."*

**Q: Then walk me through the model. Where does 50% come from?**

> [FILL — CRITICAL. The source report states the ~50% figure three times (§3, §13, §17) and **never once shows the derivation**. There is no measured baseline, no cost-per-run figure, no judge-call count, no invoice comparison, no assumed Tier-0 failure rate. You must reconstruct the arithmetic yourself before the interview and be able to say it out loud. The structure of the argument is: *the judge is the only paid call; the judge fires only when tiers 0+1 pass; therefore judge-call volume is reduced by exactly the fraction of runs that fail a cheap check first; if roughly half of the runs in a mixed suite fail a Tier-0 rule, judge volume halves and, since the judge is the dominant cost, so does spend.* **That chain contains one number you must own: the assumed Tier-0 failure rate.** If you never measured it, the honest sentence is "~50% assumes roughly half of runs trip a cheap check first — that was my working assumption from the example suites, not a measured rate."]

**Q: A regression suite mostly *passes*. If your suite is green, every test passes Tier 0, so the judge fires every time and you save nothing.

> That's the sharpest possible attack on the number and it's basically right. Fail-fast only saves money **when tests fail.** On a healthy suite on a quiet day, every test sails through tiers 0 and 1 and pays for the judge — the saving is zero. The ~50% figure implicitly assumes a *mixed* suite with a meaningful failure rate, and my report does say "across a mixed-assertion test suite" — but it doesn't say what mix. So the truthful framing is: **fail-fast is a cost *ceiling* mechanism, not a steady-state discount.** It bounds your spend on a bad day; it doesn't halve your bill on a good one.

**Q: So is the 50% number wrong?**

> It's unverified, which for an engineering claim is functionally the same as wrong until measured — and I'd rather say that to you than have you find it. What I'd actually do to earn the number: `TestResult` already carries `token_count` and `latency_ms` per run, and `test_results` persists them. So the instrumentation to *measure* this already exists in the schema — I'd sum tokens across a suite run with fail-fast on, sum them again with fail-fast forced off, and divide. That's a one-flag experiment I never ran, and I should have, because the data model was already sitting there waiting for it.

**Q: What are the *other* cost mechanisms — is any of the saving from caching or model routing?**

> No, and I want to be exact because those are the two things an interviewer expects to hear. There is **no response caching** in this system — no cache layer, no memoised LLM calls. And the model routing that exists (`src/llm/factory.py`) routes *by prefix to a different provider for the judge* — that's for **anti-self-bias**, not for cost. There is no "route the easy case to a cheap model" logic. The only cost mechanisms in the system are: **(a)** fail-fast tier ordering, **(b)** doing semantic similarity locally with `all-MiniLM-L6-v2` instead of paying for an embeddings API — 80MB on disk, ~22MB RAM, ~5ms a pair, zero API cost, no network call — and **(c)** selective CI execution via the reverse index, which reduces how many test cases run at all. That third one is arguably the biggest real-money lever and it's not what the 50% number refers to.

**Q: Selective execution — quantify it.**

> A PR touching 3 of 80 prompt files runs about 12 tests, not 80. That's from the reverse index: `prompt_template_path → [test_case_ids]`. Every test you don't run is 100% of its cost saved, not 50%. Arithmetically that dwarfs the fail-fast saving on a typical PR — and it's the mechanism I'd put on the resume if I were rewriting the bullet.

---

## 6. Registry & selective execution

**Q: How does the registry know what to run?**

> `Registry` (`src/registry.py`) does a single directory walk at load time and builds two indexes. **Forward:** `test_case_id → TestCase`. **Reverse:** `prompt_template_path → [test_case_ids]`. The reverse index is the whole trick. CI calls `Registry.affected_by(changed_files)` with the output of `git diff --name-only` against the PR base branch, and gets back only the test cases that reference a modified prompt file.

**Q: What if I rename a YAML file? Do my baselines orphan?**

> No — `TestCase.id` is `file_path.stem + "::" + name`. So it's stable across YAML renames **as long as the `name` field is unchanged**. Reorganise the directory structure and the stored baseline scores follow.

**Q: You just said the ID contains `file_path.stem`. If I move `qa_citation.prompt-test.yaml` to a new directory the stem is unchanged — fine. But if I *rename the file itself*, the stem changes and the ID changes. So it's not actually stable across renames.**

> You're right and I overstated it. `file_path.stem` is the filename without extension — so moving the file between directories preserves the ID, but renaming the file does not. What's actually stable is *relocation*, not *renaming*. If someone renames `qa_citation.prompt-test.yaml` to `citation_qa.prompt-test.yaml`, the ID changes, the baseline lookup misses, and that test case silently starts with **no baseline.** Which raises the follow-up you're about to ask.

**Q: What happens when a test case has no baseline?**

> [FILL — this is a real gap in the source and a likely interview landmine. The report never states the no-baseline behaviour. There are only three possibilities and you must know which one you built: **(1)** it skips the regression check and passes — meaning a renamed file silently loses its gate, which is a genuine silent-failure hole; **(2)** it treats the baseline as 0.0 — meaning nothing ever regresses; or **(3)** it errors. Check `baseline_manager.py` and `runner.py` and answer with the truth. If it's (1) or (2), that's a **sentinel-value silent failure** and conceding it well is worth more than any feature you could describe.]

**Q: Selective execution means a change can slip through. How do you cover that?**

> Two ways. First, `Registry.should_run_full_suite()` — if more than **30% of all tracked prompt files** changed in one PR, selective execution is abandoned and the complete suite runs. That's aimed at systemic refactors: reorganising the prompts directory, renaming shared components. Second, the weekly full-suite run on Monday. But I'll pre-empt you: the report itself lists *"systemic changes may not trigger selective runs"* as an unresolved trade-off, and calls the 30% number "somewhat arbitrary." A PR that changes one *shared* prompt fragment that 40 other prompts include would, under selective execution, only run the tests that name that fragment as their `prompt_template` — [FILL: confirm whether the reverse index handles prompt *includes*/composition at all, or only direct `prompt_template` references. If it only tracks direct references, then shared-fragment changes are a real blind spot and you should say so.]

**Q: One malformed YAML — does the whole suite die?**

> No. Pydantic `ValidationError` is caught **per file** during `Registry.load()`. The invalid file is logged with its full error and skipped; the rest of the suite runs. One bad test file doesn't block CI.

**Q: Skipped and logged. So if I break a test file, its gate silently disappears and my PR merges green.**

> Yes. That's the flip side and I'd rather name it than defend it: "skip the broken file" and "silently disable a safety check" are the same action described two ways. The right behaviour is that a YAML that *fails to parse* should be a hard CI failure — `prs validate` is a zero-cost parse-only command that exists precisely for this and could run as a pre-commit hook or as a blocking first CI step — whereas a *runtime* error on one test case should degrade gracefully. Right now I apply the graceful path to both. The distinction is: never fail-soft on something a developer can fix for free in five seconds.

---

## 7. Baselines and governance

**Q: The three-rule baseline policy.**

> **Rule 1 — baselines update automatically on merge to `main`.** `update_baselines_from_run()` is only called on main-branch runs. Improvements get recognised: a prompt that reliably scores 0.91 instead of 0.82 advances its baseline. **Rule 2 — PR runs never update baselines.** They're comparison-only. **Rule 3 — forced resets require a documented reason.** `force_reset()` raises `ValueError` if `reason` is empty or whitespace, and the reason is stored in the `baselines` table alongside score, commit SHA, and timestamp.

**Q: Why does each rule have to exist? Argue the negative.**

> Without Rule 1, every genuine quality improvement flags as a false positive and the team learns to ignore the tool. Without Rule 2, a single PR run would immediately overwrite the stored score — the regression would be *forgotten before the PR even closed*, which is the most darkly funny failure mode available: a regression detector that erases the evidence as it measures it. Without Rule 3, teams paper over regressions by resetting the baseline, and the tool becomes theatre. Those three are the minimum viable governance that makes it both sensitive *and* trustworthy over time.

**Q: Rule 3 requires a non-empty string. I can type "x".**

> Correct, and I'll go further: `force_reset()` validates *presence*, not *quality*. It's an audit trail, not an authorisation gate — the value is that someone's name, commit SHA, timestamp, and stated reason are permanently attached to the moment quality was allowed to drop, and that's socially expensive to abuse in code review even though it's technically trivial to bypass. What it *doesn't* do is require a second person's approval. If I wanted a real gate rather than a real record, the reset would need to be a PR against a checked-in baselines file, so it goes through code review like anything else. That's a genuinely better design and I'd take it.

**Q: What stops a developer from just tuning the prompt until the test goes green?**

> Nothing. There is no held-out set. The reference answers, the keywords, the thresholds, and the prompt all live in the same repo, and a developer can iterate the prompt against the test until it passes — which is textbook overfitting to the eval set. The suite catches **unintentional** regression, which is what it was built for; it does not defend against **deliberate** gaming, and I shouldn't claim it does. The mitigation in a real team would be to hold back a set of test cases that the prompt author doesn't see — the same discipline as a hidden test set in ML — and run those only on `main`. The architecture supports it trivially: it's a `tag`, and the CLI already filters by tag with `prs run --tag`. I just never split the set.

**Q: If baselines auto-update on every merge to main, can quality drift downward one merge at a time?**

> Yes — and this is the slow-boil version of the attack. Each merge can drop the score by up to `delta_threshold − ε`, roughly 0.049, without ever firing a regression, and then Rule 1 *promotes that lower score to the new baseline.* Repeat twenty times and you've walked a prompt from 0.90 to 0.05 with a green board the entire way. Every individual step was legitimate; the sequence is a catastrophe. **The delta gate is per-merge and memoryless — there is nothing in the system watching the trend.** [FILL: confirm no absolute floor / cumulative-drift check exists — the source describes none. If none exists, the fix is straightforward: an absolute floor per test case below which no baseline may be auto-promoted, plus a cumulative-drift alarm comparing today's baseline to the 30-day-old one. The dashboard already renders a 7-day rolling average and a baseline reference line in the Score Trends view — the *data* to catch this is on screen; nothing acts on it.]

---

## 8. Model drift — the premise of the whole project

**Q: The provider swaps the model under you. That's your headline use case. What actually catches it?**

> `weekly-drift.yml` — every Monday at 09:00 UTC, on `main`, running the **full suite**, not the selective subset. That's the point: model drift doesn't appear in a PR, because no code changed. It arrives through the API. Without a scheduled run against the live model, a silent behavioural shift accumulates undetected for weeks. Results go to a Slack webhook with an emoji-coded summary — 🟢 for zero regressions, 🟡 for 1–3, 🔴 for more than 3 — naming the worst-regressing test case. Artifacts retained 90 days, versus 30 for PR runs.

**Q: Monday 09:00 weekly. A provider ships a bad model Monday at 10:00 — you find out in seven days.**

> Correct, and the mean time to detection is worse than that: it's up to a week, averaging three and a half days. That's a *deliberate* cost trade — a full suite run costs real API money, and daily would be 7× the bill for a class of event that historically happens rarely. But I'd defend the *tier* of the choice rather than the specific cadence: for a team where the LLM feature is core revenue, weekly is indefensible and I'd move to daily on a reduced canary subset — tag a dozen high-signal test cases, run *those* every morning, keep the full suite weekly. The `--tag` filter already exists for exactly that shape of run. It's configuration, not engineering.

**Q: How would you even *tell* provider drift apart from your own prompt regression?**

> By the shape of the signal, and only circumstantially. A prompt regression is *localised* — it hits the test cases whose prompt file changed, and it correlates with a commit. Provider drift is *broad and commit-less* — the weekly run finds multiple unrelated test cases sagging together, on `main`, with no code change in between. That's why the Slack summary counts regressions and buckets them 🟢/🟡/🔴: 🔴 on a weekly run with a quiet week of commits is the drift signature. But I'll be honest that this is *inference from a pattern*, not a discriminator the system computes. And the confound I mentioned earlier makes it worse — if the *judge's* provider drifts, I get the exact same broad, commit-less, multi-test sag, and I'd be looking for a bad model under test when actually my ruler shrank. A frozen golden-set canary for the judge is what disambiguates those two, and I don't have it.

**Q: When the model genuinely changes and every baseline is now stale — what's the operational move?**

> `force_reset()` with a documented reason, per test case, and the reason string is exactly what it's for: *"Provider updated gpt-4o base model on <date>; re-baselining against new model behaviour."* That entry lives in the `baselines` table forever with a commit SHA and a timestamp. Six months later, when someone asks why quality on this prompt looks different before and after March, the answer is in the audit trail and not in someone's memory. That is the entire payoff of Rule 3, and it's the case it was designed for.

---

## 9. Architecture, concurrency, storage

**Q: Six layers. Why?**

> Discovery (`src/registry.py`), Orchestration (`src/runner.py`), Assertion (`src/assertions/`), LLM Communication (`src/llm/`), Storage (`src/storage/`), Interfaces (`cli.py`, `src/api/`, `dashboard/`). The thing I'd actually defend is not the count — it's that **every cross-layer boundary is typed.** No layer receives raw strings or unvalidated dicts. `TestCase`, `AssertionConfig`, `AssertionResult`, `TestResult`, `SuiteRun`. The `Runner` and the `AssertionEngine` never reference a provider-specific API — they only consume the standardised `LLMResponse` contract with `content`, `ok`, `error`, `latency_ms`, `token_count`. Adding a provider is: implement `LLMClient`, add one routing rule to the factory.

**Q: Concurrency model.**

> `asyncio.Semaphore(max_concurrent_workers)`, default 10, tunable through `PRS_CONCURRENCY_LIMIT`. It's I/O-bound work — waiting on HTTP — so the GIL is irrelevant and asyncio is the right tool. Measured speedup is **6–8× versus serial on a 10-test suite**. The Semaphore is there specifically so it isn't "fire everything at once" into a rate limit.

**Q: What happens on a 429?**

> [FILL: the source describes the Semaphore as the concurrency throttle but never describes retry, backoff, or rate-limit handling. If there's no retry-with-backoff, say so — an unretried 429 becomes an `LLMResponse` with `ok=False` and an `error`, which surfaces as an errored test rather than a crash, but it also means transient rate-limiting shows up as noise in your regression signal. Check `src/llm/*_client.py`.]

**Q: SQLite. Really?**

> SQLite by default, and I'll own the reason: zero friction. Clone, install, run — no Docker Compose, no separate process. The report is blunt about the cost: *concurrent write contention; not suitable for multi-process production.* PostgreSQL is one `DATABASE_URL` env var away and needs **zero ORM model changes** because it's SQLAlchemy 2.0 async with identical models for both backends. So the trade is: optimise for the developer's first five minutes, and make the production path a config change rather than a rewrite.

**Q: Your CI runs concurrently and writes to SQLite. Isn't that exactly the contention case you just described?**

> [FILL: confirm what the CI writes to and where. The GitHub Actions job writes `ci_results.json` and posts a PR comment; the source does not say whether the CI run also persists to the database, or whether the DB file survives between runs at all. If CI is stateless and only `main` runs persist, say that — it's a clean answer. If CI writes to a SQLite file in the runner, that file dies with the runner and your PR-run history is being thrown away, which you should know before someone asks.]

**Q: Pydantic v2 — why does that matter?**

> Roughly 10× faster validation than v1, but the reason I care is `model_validator` for cross-field invariants **at parse time, not run time.** An `AssertionConfig` of type `contains_keyword` with no `keywords` list is caught by `prs validate` at zero API cost, in milliseconds, before a single token is spent — not discovered forty seconds into a paid suite run.

---

## 10. Hard cross-cutting questions

**Q: Your resume says the stack is "Python, pytest." I've read your report. It never mentions pytest.**

> You're right, and that's a fair hit. The report's framing is "pytest **for** prompts" — the analogy, not the dependency. The actual runner is my own async orchestrator driven by a Typer CLI; the interfaces are FastAPI and Streamlit; storage is SQLAlchemy 2.0. Saying "pytest" on the resume implies I built this *on* pytest, which I didn't, and the honest bullet says "Python, asyncio, Pydantic, SQLAlchemy, GitHub Actions." [FILL: if you *do* have pytest unit tests covering PRS's own code — the rule handlers, the weighted-mean maths, the baseline policy — say so, because "I unit-tested my test framework" is a genuinely good answer to a question about rigour. If you don't, the honest answer is that the framework itself is untested, which is an uncomfortable thing to admit about a testing tool and better admitted than discovered.]

**Q: You built a testing tool. Is *it* tested?**

> [FILL: see above. This is the question that follows the pytest one and you cannot dodge it twice. If there are no tests on PRS's own logic — the weighted mean, the fail-fast ordering, the three baseline rules — say it, and say what you'd test first: the baseline policy, because it's the only component where a bug silently *destroys stored data* rather than just producing a wrong number.]

**Q: This is a lot of surface area for one engineer. FastAPI, Streamlit, Typer, an ORM, a CI integration. Did you need all of it?**

> Probably not, and that's a fair criticism of scope rather than of engineering. The load-bearing parts are the registry, the runner, the assertion engine, the baseline manager, and the two workflows — that's the product. The FastAPI layer in particular is arguably speculative: the CLI and the dashboard both work without it, and the **dashboard deliberately reads the database directly via SQLAlchemy rather than going through the API**, precisely so the analytics tool works whether or not the API process is running. Which means I built a REST API that my only two clients bypass. I'd defend it as "the integration point for a team that wants to trigger runs from somewhere other than GitHub Actions" — but if you told me it was YAGNI, I wouldn't fight hard.

**Q: What's the single biggest weakness in this system?**

> That my thresholds are chosen rather than calibrated, and that the noise threshold and the signal threshold are the same number — 0.05 for flaky, 0.05 for regression. Everything else here is engineering I'd stand behind. That one is a *statistics* problem sitting at the exact centre of the product, and no amount of clean architecture around it fixes it. What it needs is a labelled corpus: a hundred real prompt diffs, each marked by a human as regression or not, and then fit the thresholds against it. Until that exists, every number in this system is a defensible guess, and I'd rather call it a guess in front of you than call it a metric.

**Q: If you had two weeks, what do you build?**

> In order. **One:** the judge golden-set canary — frozen human-scored responses run through the judge every execution, so I can tell "my oracle drifted" from "my prompts broke." Without that, the system's headline feature is confounded. **Two:** flaky-test quarantine — `std_dev > 0.05` makes a test advisory, so it can't block a merge on noise, because a merge gate that fires randomly gets ignored and then the whole thing is decoration. **Three:** actually *measure* the cost claim — sum `token_count` across a suite with fail-fast on versus forced off. The field is already in the schema and persisted in `test_results`; it's a flag and a division, and I should be embarrassed I put an unmeasured number on a resume when the measurement was a day's work.

---

## Closing

**Q: What did you learn?**

> That the hard part of testing an LLM isn't running it — it's deciding what "correct" even means when the same input legitimately produces different output every time. Every instinct I had from normal software testing was wrong. There's no golden output, so I had to replace *equality against a truth* with *distance from a distribution's own past*. And once you accept that, the second lesson lands immediately: **you don't get to skip the statistics.** I built a lot of good architecture around a threshold I picked by feel, and the architecture is not what makes the system trustworthy or not. The threshold is.

**Q: Would you build it again?**

> The registry, the tiered engine, and the three-rule baseline policy, yes, unchanged — those are the parts I'd port to any eval system I ever build. I'd cut the FastAPI layer. And I'd start with the calibration set, not end with it, because every number in the system is downstream of it and I built the whole thing before admitting I didn't have one.

---

## Cheat card — trigger → exact line to say

| When they say... | You say... |
|---|---|
| "50% cost cut — measured how?" | "It's an *estimated* figure from the tier architecture, not a metered A/B. My report says 'estimated ~50%' and the resume dropped that word. The mechanism is fail-fast: the judge is the only paid call, and it only fires if the free checks pass." |
| "So it saves nothing on a green suite." | "Correct. Fail-fast is a cost *ceiling*, not a steady-state discount. It bounds your bad day; it doesn't halve your good one." |
| "What's your oracle?" | "There isn't one, and that's the design. I don't assert on the output — I assert on a distribution relative to its own past. Mean of 3 runs versus stored baseline, regression at a 0.05 drop." |
| "Why 0.05?" | "I chose it, I didn't calibrate it. No labelled ground-truth set to fit against. That's the honest limit of the system." |
| "Flaky tests?" | "std_dev over 0.05 flags them — but flagging is a *label, not a gate*. A flaky test can still block a merge. That's a real hole. Fix is quarantine: advisory-only until it stabilises." |
| "Your flaky and regression thresholds are both 0.05." | "Yes. My noise band and signal band are identical, which is statistically indefensible. Delta should be a multiple of each test's own observed std_dev, not a shared constant." |
| "Who judges the judge?" | "Nobody, today. temperature=0.0 and client-side score recomputation cut variance but don't pin the model. What I need is a frozen golden set — if the judge's scores on it move, the alert is 'your ruler shrank,' not 'your prompts broke.'" |
| "Isn't this circular — LLM grading LLM?" | "Broken structurally: `factory.py` routes `claude-*` to an OpenAI judge and `gpt-*`/`o1`/`o3`/`o4` to an Anthropic judge. Enforced in `Runner.__init__`, not in a README." |
| "Judge reports an overall score." | "I throw it away. LLM arithmetic is unreliable. I recompute client-side from the four dimensions — 0.40/0.30/0.20/0.10. The judge judges; Python does the maths." |
| "Overfitting to your test set?" | "Yes. No holdout. It catches *unintentional* regression, not *deliberate* gaming. The fix is a hidden tag-filtered set run only on main — the CLI already supports `--tag`, I just never split it." |
| "Model provider swaps the model." | "`weekly-drift.yml`, Monday 09:00 UTC, full suite on main, Slack 🟢/🟡/🔴. Drift arrives through the API, not through a PR — so nothing PR-triggered can ever catch it." |
| "Up to a week to detect drift." | "Yes, avg 3.5 days. Deliberate cost trade. For a revenue-critical feature I'd run a daily tagged canary and keep the full suite weekly — that's config, not engineering." |
| "pytest?" | "The framing is 'pytest *for* prompts', the analogy — not the dependency. The runner is my own async Typer CLI. The resume bullet is imprecise and I'd reword it." |
| "Biggest weakness?" | "Chosen thresholds, not calibrated ones — and the noise threshold equals the signal threshold. That's a statistics problem at the centre of the product and clean architecture doesn't fix it." |

---

## Prep priority

**Tier 1 — you cannot walk in without these. Rehearse out loud.**
1. The oracle answer (§4, Q1) — *the* question. Must be fluent, ~40 seconds, no hesitation.
2. The 50% derivation (§5) — **reconstruct the arithmetic before the interview.** The source does not contain it. Know your assumed Tier-0 failure rate, or say plainly that you assumed it.
3. Thresholds chosen not calibrated (§4) — concede fast, then show you know what calibration would look like (labelled corpus, fit for F1).
4. The 0.05 == 0.05 collision — if you spot it before they do, you win the exchange. Volunteer it.
5. The pytest discrepancy — have a one-liner ready; it's the first thing a careful reader notices.

**Tier 2 — likely, and each has a strong honest answer.**
6. Flaky-test quarantine gap (§4)
7. Who judges the judge / golden set (§3)
8. Overfitting, no holdout (§7)
9. Baseline downward drift via repeated sub-threshold merges (§7)
10. Fail-fast throws away diagnostic information (§2)
11. Judge parse-failure scores as a prompt failure (§3)

**Tier 3 — know them, don't lead with them.**
12. Six-layer architecture, typed contracts, `LLMResponse`
13. SQLite → PostgreSQL portability, one env var
14. Semaphore(10), 6–8× speedup, `all-MiniLM-L6-v2` at 80MB / 22MB RAM / 5ms / 384-dim
15. Registry stable IDs and the 30% full-suite rule
16. Scope critique: the unused FastAPI layer

---

## [FILL] list — resolve every one of these before the interview

| # | What you must supply | Why it matters |
|---|---|---|
| 1 | **The derivation of ~50%.** The source states it 3× (§3, §13, §17) and never derives it. What Tier-0 failure rate did you assume? Was it measured or assumed? | The resume's headline number. Highest-risk item in this document. |
| 2 | Was this deployed / used by anyone, or is it a portfolio system? | Determines whether you can say "in production" at all. Never imply users you don't have. |
| 3 | Does `critical_failure: true` fail the CI exit gate, or only surface to the dashboard/PR comment? | If not, a critically-failing response can merge. Real hole. |
| 4 | Is the judge model version **pinned** to a dated snapshot, or a floating alias? | A floating judge on a *drift-detection* tool is a live bug. |
| 5 | What happens when a test case has **no baseline** (first run, or after a file rename changes the stable ID)? Skip / 0.0 / error? | Sentinel-value silent-failure class. |
| 6 | Does the reverse index track prompt **includes/composition**, or only direct `prompt_template` references? | If only direct, shared-fragment changes are a selective-execution blind spot. |
| 7 | Is there any **absolute floor** or cumulative-drift check preventing baselines walking downward 0.049 at a time? | Source describes none. Slow-boil quality collapse with a green board. |
| 8 | Rate-limit / 429 handling in `src/llm/*_client.py` — retry with backoff, or straight to `ok=False`? | Transient 429s polluting the regression signal. |
| 9 | Does the CI run persist to the database, and does that DB survive the runner? | If not, PR-run history is discarded. |
| 10 | **Does PRS have its own unit tests (pytest)?** If yes — what do they cover? If no — say so. | You built a testing tool. "Is it tested?" is inevitable. |
| 11 | Did you sanity-check the judge's 0.40/0.30/0.20/0.10 dimension weights against any examples? | Only claim it if true. |
| 12 | The "4 minutes vs 3 days"-style speed claim, if you intend to use one anywhere. | **The source contains no such comparison.** The only timing numbers in it are: 6–8× concurrency speedup on a 10-test suite, ~5ms per semantic pair, ~0.5s semantic model first load. **Do not state a manual-review-time comparison unless you can source it.** |
