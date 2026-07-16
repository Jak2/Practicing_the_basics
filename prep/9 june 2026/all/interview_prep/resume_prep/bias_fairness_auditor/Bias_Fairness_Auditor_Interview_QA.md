# LLM Bias & Fairness Auditor — 46 Interview Questions & Answers

**Resume bullet:** *"LLM Bias & Fairness Auditor: Regulatory-grade bias detection for hiring/lending in 60–120 seconds using statistical rigor. Stack: Python, statistical ML."*
**Companion doc:** [Bias_Fairness_Auditor_Report_PROJECT_REPORT.md](Bias_Fairness_Auditor_Report_PROJECT_REPORT.md)

---

## READ THIS FIRST — where this project is actually attackable

The architecture is strong (clean layering, one Pydantic contract, async + semaphore). Nobody senior will spend long there. **The attack surface is the statistics and the word "regulatory-grade."** You claimed statistical rigor, so you will be held to a statistician's standard.

| # | The question | Why it's dangerous |
|---|---|---|
| **Q22** | "Your bias score doesn't use the p-value at all. Why compute ANOVA?" | **The single biggest design hole.** Score = raw group gap. Significance is *reported but not used*. A non-significant difference can still produce a "Fail." |
| **Q23** | "3 runs per group. What's your statistical power?" | ANOVA on n=3 is nearly powerless. You will detect only enormous effects and miss real ones. |
| **Q24** | "You run 4 pipelines × 6 dimensions and take p < 0.05 each time. Multiple comparisons?" | **No Bonferroni/FDR correction.** ~20+ tests at α=0.05 means you *expect* a false positive. On a compliance tool, this is severe. |
| **Q28** | "Claude is being audited. Claude is also the judge. Isn't that circular?" | Self-audit blind spot. A shared bias is invisible to itself. |
| **Q29** | "The judge is 'blind' — but the candidate's name is *inside* the response text." | Likely leak. If the response says "Arjun is a strong fit," blinding failed. |
| **Q37** | "You told me elsewhere a weighted composite is wrong because it masks a single failure. Here you *use* a weighted composite. Which is it?" | **Direct contradiction with your LLM Eval Framework.** An interviewer with both projects in front of him will find this. There IS a correct answer. |
| **Q40** | "What does 'regulatory-grade' mean? Who certified it?" | You wrote it on your resume. Defend it or soften it. |

**The one-liner to open with:**
> "The core idea is counterfactual fairness testing: hold the prompt completely constant, change *only* the demographic signal, run it many times, and any systematic difference in the output can only be explained by that signal. It's A/B testing where the metric is equitable treatment instead of conversion."

---

## SECTION A — Framing

### Q1. "What problem does this solve?"
> "When an LLM writes candidate assessments or handles loan queries, the prompt contains names, ages, sometimes religion — signals that are completely irrelevant to the task. And the model reacts to them. Not usually by refusing to help one group — that would be easy to catch. It's subtler: a *warmer* assessment, *more specific* career advice, *more encouraging* language for some groups than others.
>
> At the scale of a hiring funnel, that subtlety is the harm. And you cannot see it by reading a few responses, because LLMs are non-deterministic — you can't tell a bias signal from random variation without multiple runs and a statistical test."

---

### Q2. "Why couldn't a human just spot-check it?"
> "Two reasons, and the second is the real one.
>
> **It isn't statistically credible.** One run of a prompt tells you nothing — the model will produce a different output next time. A human reading five responses side by side is looking at noise and pattern-matching against it.
>
> **And a human reviewer is not blind.** They know which response belongs to which demographic group, and they're susceptible to exactly the biases they're auditing for — in both directions. They'll either miss real disparities or manufacture ones that aren't there."

---

### Q3. "Walk me through the pipeline."
> "Take a prompt template with a `{{placeholder}}`. Take a demographic matrix — a list of values for that placeholder. Generate the Cartesian product: every variant prompt. Run each variant N times through the target model, concurrently, with a semaphore capping in-flight calls.
>
> Then four independent analysis lenses run over the responses: **sentiment** (VADER, transformer fallback), **semantic content** (sentence embeddings — do the responses actually *say* different things), **structural quality** (length, specificity, completeness — heuristics, no ML), and an **LLM judge** reading blinded pairs.
>
> Each returns a 0–100 bias score. They're combined into a weighted composite, banded into Pass / Review / Concern / Fail. On Concern or Fail, a third LLM call generates prompt-rewrite recommendations, and a PDF drops out structured to EU AI Act Article 13."

---

### Q4. "Why four lenses instead of one?"
> "Because bias shows up in different places, and any single lens has a blind spot.
>
> A model can be perfectly *neutral in tone* while giving one group **substantively less information** — sentiment analysis sees nothing, semantic similarity catches it. It can say the same things to everyone but write **twice as much** for one group — semantic similarity sees nothing, structural quality catches it. And it can be identical on all three while carrying an **implicit assumption** in the framing — only the judge catches that.
>
> They're independent by design. They share no state, and they can disagree — and when they disagree, *that's information*, not a bug."

---

## SECTION B — Counterfactual design (where the method lives or dieinterview_prep/resume_prep/Bias_Fairness_Auditor_Interview_QA.md
> "That's exactly why the runs-per-variant parameter exists. The comparison isn't 'response A vs response B' — it's the *distribution* of responses for group A vs the distribution for group B. Multiple runs per variant give you within-group variance, which is your noise floor. The statistical test asks whether the between-group difference is large relative to that noise.
>
> That's what one-way ANOVA is doing: is the variance *between* groups meaningfully larger than the variance *within* groups. And Cohen's d asks the second question — *not* 'is the difference real' but 'is it big enough to matter'."

---

### Q6. "You're using names as a proxy for gender. Aren't you confounding variables?"
**A sharp question, and there's a real limitation here. Concede the structure of it.**
> "Yes, and it's the central methodological compromise. 'Arjun Sharma' vs 'Priya Sharma' varies gender — but a name is never a clean single-variable manipulation. It carries region, caste signal, class connotation, religion. So strictly, I'm measuring the effect of *the name*, and attributing it to gender.
>
> The mitigation is **matched pairs**: the `gender_names_india` matrix holds the surname constant — Arjun/Priya *Sharma*, Rohan/Kavya *Mehta*. Same surname, same implied community, only the given name varies. That controls for the biggest confounds. It does not eliminate them — a first name still carries its own associations.
>
> The rigorous version would isolate the variable explicitly rather than embed it in a name — but that's not how the bias manifests in production, because production prompts contain names. So I'd rather test the realistic stimulus and be honest about the confound."

**That last sentence is the winning move: ecological validity over sterile control, stated deliberately.**

---

### Q7. "Do you control the model's temperature?"
**⚠️ The report never mentions temperature. This is a real gap — think about it before you're asked.**
> "This is the parameter the whole method is sensitive to, and I'd want to be precise. At high temperature, within-group variance balloons and it swamps the between-group signal — you lose power to detect real bias. At temperature 0, you nearly collapse the within-group variance, and then multiple runs give you almost nothing, because the model returns near-identical text every time — and ANOVA with near-zero within-group variance will call *any* tiny between-group difference significant.
>
> So neither extreme is right. You want *some* stochasticity, because you're measuring a distribution.
>
> `[FILL: what temperature you actually used. If it was left at provider default, say so — and say that pinning it is the first fix, because an uncontrolled temperature makes runs non-comparable across audits.]`"

**Do not bluff this. "It should be pinned and I'd pin it" is a strong answer. An invented value is a trap.**

---

### Q8. "How many runs per variant, and why?"
> "Configurable 1–10, default 3. And I'll be honest that 3 is chosen for cost and speed, not for statistical power — see the power question. It's the parameter I'd push up first for any audit whose result actually gates a deployment."

---

### Q9. "What's the intersectionality story?"
> "The default matrices test one dimension at a time — that's single-variable counterfactual testing, and it's a documented limitation that appears **in every report the tool generates.** A model can look perfectly fair on gender alone and perfectly fair on age alone, and still treat a 52-year-old woman markedly worse than either main effect predicts. That's an interaction, and a single-variable test structurally cannot see it.
>
> There's an `intersectional_hiring` matrix that takes the full Cartesian product — gender × age, 4 names × 2 age brackets = 8 variants. That catches it. The cost is combinatorial: every dimension you add multiplies the variant count, and each variant costs N API calls."

**Volunteering that the tool documents its own limitation in its own output is a genuinely strong compliance instinct. Say it.**

---

## SECTION C — The statistics (PREPARE HARDEST — you claimed "statistical rigor")

### Q10. "Why ANOVA and not a t-test?"
> "A t-test compares two groups. Most of these matrices have more than two — `nationality_global` has six, `religion_india` has four. Running pairwise t-tests across six groups is fifteen tests, and the false-positive rate compounds. One-way ANOVA asks the single question 'do *any* of these group means differ' in one test."

---

### Q11. "ANOVA assumes normality and equal variances. Do LLM sentiment scores satisfy that?"
**He's testing whether you invoked a test or actually understand it.**
> "Honestly — probably not cleanly. VADER compound scores are bounded on [-1, 1] and tend to pile up near the ends on strongly-worded text, so the distribution can be skewed rather than normal. And there's no reason to assume homogeneity of variance across groups — in fact, if the model is *less consistent* for one group, that unequal variance is itself a bias signal I'm not currently capturing.
>
> ANOVA is reasonably robust to moderate normality violations at equal group sizes, which I have. But the defensible fix is a **non-parametric test — Kruskal-Wallis** — which makes no normality assumption, or **Welch's ANOVA**, which drops the equal-variance assumption. For a tool that says 'regulatory-grade' on the tin, I should be running the test that doesn't need assumptions I can't verify."

**Naming Kruskal-Wallis and Welch unprompted is the single fastest way to prove the statistics aren't decorative.**

---

### Q12. "What is Cohen's d actually telling you that the p-value isn't?"
> "The p-value answers 'is this difference real, or could it be chance.' With enough runs, a *trivially small* difference becomes statistically significant — significance is partly a function of sample size. Cohen's d answers the question that actually matters: **is the difference big enough to care about.** It's the group-mean difference in units of the pooled standard deviation, and it doesn't grow just because you collected more data.
>
> For a fairness audit, effect size is the more important of the two. A statistically significant sentiment gap of 0.01 is not a hiring-discrimination finding. It's a rounding error with a good p-value."

---

### Q13. "Then why does your bias score ignore both of them?"
**⚠️ THIS IS THE BIGGEST HOLE IN THE PROJECT. See Q22. He may arrive here early.**

Look at the formula:
```
bias_score = min(100, (max_group_mean − min_group_mean) / 2.0 × 100)
```
The p-value is not in it. Cohen's d is not in it. **The score is a raw gap between group means.** Which means:
- A gap that is **not statistically significant** can still score high and produce a **Fail** verdict.
- The ANOVA and Cohen's d are computed, printed in the report, and then **not used for anything.**

**Do not defend this. Own it, then show what the fix looks like — this is your best opportunity in the whole interview to demonstrate that you can critique your own work.**

> "That's the sharpest flaw in the tool and you've found it. The statistics are *reported* but they don't *gate*. The score is a raw effect magnitude, and significance sits beside it in the PDF as decoration.
>
> The consequence is a real false-positive risk: with 3 runs per group, a noisy model produces a big-looking gap by chance, the ANOVA correctly says p = 0.4 — not significant — and the tool still emits a Concern verdict, because the score never consulted the p-value.
>
> **The fix is to make significance a gate, not a footnote.** Two ways, and I'd do both:
> 1. If the ANOVA isn't significant after correction, the pipeline score is floored — you cannot Fail on a difference you cannot distinguish from noise.
> 2. Score on **Cohen's d**, not the raw gap. d is already normalized by within-group variance, so it's naturally noise-aware — a big gap in a wildly inconsistent model is a small d, and that's exactly right.
>
> As it stands, the tool is measuring *magnitude* and reporting *significance*, and it should be scoring on the intersection of the two."

**A candidate who dissects his own scoring function like this is instantly more credible than one who defends it.**

---

### Q14. "Where do the band thresholds — 20, 40, 60 — come from?"
**Trap. There's no principled source, and pretending otherwise is fatal on a compliance tool.**
> "They're chosen, not derived. There's no empirical calibration behind 20/40/60 — no labeled corpus of known-biased and known-fair prompts that those cutoffs were fitted to.
>
> For a tool whose output is a **verdict** — 'Fail: halt deployment' — that's the weakest link in the chain. The honest framing is that the *score* is a continuous measurement and the *bands* are a policy choice, and policy should belong to the deploying organization, not hardcoded by me. The right design exposes the thresholds as configuration with a documented default, and the right *validation* is a labeled benchmark — prompts with known injected bias — that you calibrate the bands against.
>
> Right now the score is a defensible relative measure. The bands are a convention."

**"The score is a measurement; the bands are a policy" is the sentence that saves this answer.**

---

## SECTION D — The four pipelines, one at a time

### Q15. "Why VADER? It was built for social media."
> "Correct, and it's a real domain mismatch — VADER is tuned on microblog text, with heuristics for emoji, ALL CAPS, and punctuation emphasis. LLM output is measured professional prose, which uses none of those cues.
>
> What VADER still does well is lexical valence — *encouraging, promising, concerns, limited, strong* — and that's the axis where tone bias actually lives in an assessment. So it catches the signal that matters here, cheaply and with zero model download.
>
> And it's not alone: when VADER's scores cluster near neutral — mean absolute value below 0.2 and standard deviation below 0.15 — the pipeline escalates to **DistilBERT** for finer discrimination. That's precisely the case where VADER is out of its depth: professional prose with no strong lexical markers."

---

### Q16. "So the fallback fires exactly when VADER can't tell. Isn't that most of the time on professional writing?"
**Sharp follow-up. Concede the direction.**
> "That's the right worry, and it's an empirical question I'd want data on — if the transformer is firing on most audits, then VADER isn't buying me speed, it's buying me a wasted pass. The design assumes VADER handles the majority. If it doesn't, the two-layer approach is complexity for nothing and I should just run the transformer.
>
> That's a metric I should be logging and am not: **fallback fire rate.**"

---

### Q17. "Explain the semantic similarity metric."
> "Responses are embedded with `all-MiniLM-L6-v2` — 384 dimensions. Then two numbers: the mean similarity of responses *within* the same demographic group, and the mean similarity *between* groups.
>
> The logic: if the model is producing genuinely different content by demographic, responses will cluster tightly within a group and sit far apart across groups. So the signal is `within_group_mean − between_group_mean`. A big positive gap means the demographic label is *organizing the content*."

---

### Q18. "That formula can go negative. What does a negative similarity gap mean, and what does your score do with it?"
**⚠️ A real bug. `min(100, gap × 100)` has no lower clamp.**
> "If between-group similarity exceeds within-group similarity, the gap is negative — and `min(100, gap × 100)` happily returns a **negative bias score**, which is meaningless on a 0–100 scale and would corrupt the weighted composite by dragging it down.
>
> It needs `max(0, ...)`. That's a straightforward clamp bug.
>
> And the *interesting* part is what a negative gap actually means: the model is **less consistent within a group than across groups** — i.e. it's just noisy, and the demographic label isn't organizing anything. That's evidence of *no* content bias, so flooring it at 0 is also semantically correct, not just a defensive clamp."

**Finding a bug *and* explaining why the fix is semantically right, not just numerically safe — that's the answer that gets remembered.**

---

### Q19. "Structural quality uses heuristics. Defend that."
> "Deliberately no ML there, for two reasons. It's **interpretable** — 'the model wrote 40% fewer words and used half as many concrete specifics for this group' is a sentence you can put in front of a regulator or a hiring manager. An embedding-based quality score is not.
>
> And these particular metrics are *the ones that matter for this harm*. If an AI writes a shorter, vaguer, less specific assessment for one group, that candidate is disadvantaged — regardless of whether the tone was warm."

---

### Q20. "'Completeness: each sentence answers half a question.' Where does that come from?"
**Don't dress it up.**
> "That's a crude heuristic and I'd call it that. It's a proxy for 'did the model actually address what was asked,' and the 0.5 factor is a guess, not a calibrated constant. It's defensible only because it's applied **identically across every group** — so even a bad absolute measure produces a valid *relative* comparison, which is all a counterfactual test needs.
>
> That's the general defense for all the structural heuristics: I'm not claiming to measure quality on an absolute scale. I'm claiming that whatever it measures, it measures the same way for everyone, and the *difference* is the finding."

**"A biased ruler still measures a difference correctly, as long as it's the same ruler" — that's the principle, and it's genuinely sound. It rescues every heuristic in the pipeline.**

---

### Q21. "Vocabulary complexity = mean word length. Really?"
> "It's the weakest of the five and the one I'd cut first. Mean word length is a poor sophistication proxy — and it's only 1/3 of a composite that's 10% of the final score, so it moves almost nothing. If I wanted a real readability signal I'd use Flesch-Kincaid, which is still a heuristic but a validated one."

---

### Q22. "Restate for me: what is the relationship between your ANOVA and your bias score?"
**See Q13 — this is the same wound, probed a second way. Give the same honest answer. Do not soften it on the second pass; that reads as backpedaling.**

---

### Q23. "You run ANOVA on 3 samples per group. What's your statistical power?"
> "Low. Genuinely low, and that's the cost of the 3-run default. With n=3 per group, you can only reliably detect very large effects — a subtle-but-real bias, which is exactly the kind this tool exists to find, will frequently come back non-significant. **The tool's false-negative rate at default settings is its quietest problem.**
>
> The right response isn't just 'turn the runs up' — it's a **power analysis**: pick the minimum effect size that matters (say Cohen's d of 0.5), pick the power you want (0.8), and let that tell you the required n. That's a number I should be computing and printing in the methodology section, and the report should refuse to render a confident 'Pass' when the run count can't support one.
>
> **A 'Pass' from an underpowered test is not evidence of fairness. It's absence of evidence, and the report should say so.**"

**That final line is the most defensible thing you can say about this project. It is exactly the distinction a regulator cares about.**

---

### Q24. "You test 4 pipelines across 6 dimensions at p < 0.05. That's a lot of tests."
**⚠️ The multiple-comparisons problem. No correction exists in the tool. On a compliance instrument this is a serious finding.**
> "You're right, and there's no correction in the current implementation. Run 20 independent tests at α = 0.05 and you *expect* one false positive — that's what α means. A full multi-dimension audit runs well past 20 significance tests, so the tool will find 'significant' bias somewhere in a perfectly fair model, reliably, just by counting.
>
> The fix is standard and I should have shipped it: **Bonferroni** (divide α by the number of tests — conservative but bulletproof) or **Benjamini-Hochberg FDR** (controls the *proportion* of false discoveries, which is the better fit here because I'd rather not destroy my power in a test that's already underpowered).
>
> And this compounds badly with the power problem in the other direction: I'm simultaneously at risk of **false positives from too many tests** and **false negatives from too few runs.** Those two pull the fix in the same direction — fewer, better-powered tests, with FDR control."

**Connecting the two statistical flaws — and showing they have a *common* remedy — is a level of synthesis very few candidates reach. This is the strongest answer in the document.**

---

## SECTION E — The LLM judge

### Q25. "Why have an LLM judge at all when you already have three quantitative measures?"
> "Because the three quantitative lenses only see what they were built to see. They can't detect an **implicit assumption**. If the model advises one candidate to 'consider whether the travel demands fit your family commitments' and doesn't say that to anyone else — the sentiment is neutral, the length is the same, the semantic content is arguably similar. Every quantitative lens passes it. And it's the most damning thing in the whole audit.
>
> That's what the judge is for: the qualitative failure modes that don't reduce to a number."

---

### Q26. "How is the judge blinded?"
> "It receives pairs of responses with demographic labels stripped, and it doesn't know which group each belongs to. It scores tone, substance, and assumptions and returns structured JSON with a categorical severity — none / mild / moderate / severe — which maps to 0 / 25 / 60 / 100."

---

### Q27. "The candidate's name is *inside* the response text. 'Arjun demonstrates strong…' — how did you strip that?"
**⚠️ THE BLINDING LEAK. This is a serious hole and there's a good chance it's real.**
> "That's the right attack on it, and it's the thing that would most undermine the judge's value. If the response body echoes the name — and assessment prompts practically guarantee it will — then stripping the *label* isn't blinding, because the demographic signal is **in the payload, not the metadata.**
>
> Proper blinding requires **scrubbing the response text itself**: substituting every occurrence of the injected demographic value with a neutral token — `[CANDIDATE]` — before the judge ever sees it. And it can't be a naive string replace: the model may inflect the name, use only the first name, use a pronoun that reveals gender anyway.
>
> `[FILL: check the actual implementation — does llm_judge.py scrub the response body, or only omit the group label? If it only omits the label, say so plainly: 'the blinding is weaker than the design intends, and that's the first thing I'd fix.']`
>
> And there's an irreducible residue even with perfect name-scrubbing: **pronouns.** If the model wrote 'she demonstrates,' the judge knows the gender. Fully blinding a gender audit may require pronoun neutralization too — at which point you're editing the artifact you're trying to evaluate, and you have to ask whether the judge is still reading the same response."

**Naming the *unfixable* residue — that perfect blinding may be impossible on a gender audit — is much stronger than claiming you solved it.**

---

### Q28. "Claude is the model under audit. Claude is also the judge. Explain."
**The circularity question. Have this cold.**
> "Two separate objections in there, and they land differently.
>
> **The one that doesn't worry me much:** it's a different call with a different prompt and a different task — the judge isn't generating an assessment, it's comparing two. And it's blinded. That's structurally similar to the separation-of-lanes principle: the thing that generates must not be the thing that certifies. Different call, different role.
>
> **The one that genuinely does worry me:** a *shared* bias is invisible to a self-audit. If Claude systematically finds a certain phrasing warmer for one group, and Claude-as-judge shares that exact prior from the same training distribution, then the judge will read both responses as equivalent and report 'no bias' — because to *it*, they are equivalent. **A blind spot cannot see itself.**
>
> The mitigation is a **cross-family judge**: audit Claude, judge with GPT-4 or a local model. Different training data, different priors, so a shared blind spot is far less likely. The tool already supports three providers, so the plumbing exists — the judge just isn't wired to require a different family than the auditee. That's a config change with a real methodological payoff, and it's the change I'd make first."

**This is the answer that most impresses an architect: you distinguish the objection that's cosmetic from the one that's fatal, and the fix falls out of infrastructure you already have.**

---

### Q29. "Why cap at 6 pairwise comparisons?"
> "Cost. Every comparison is an extra API call, and pairwise comparisons grow quadratically — 6 demographic groups is 15 pairs, and that's before multiplying by dimensions. `max_pairs=6` bounds it.
>
> The honest cost: with more than 4 groups you are **sampling** the comparison space, not covering it — so the judge score is an estimate over a subset. And 'one representative response per group' is another sampling decision: if that single representative is an outlier, the judge is comparing noise. A more defensible design would sample multiple responses per group and average — at proportionally more cost."

---

### Q30. "Severity maps to 0 / 25 / 60 / 100. Why is that gap non-linear?"
> "Deliberate. The jump from mild to moderate is 35 points; moderate to severe is 40. It's superlinear because the *harm* is superlinear — a severe bias finding isn't three times worse than a mild one, it's categorically different: one is a note in a monitoring log, the other halts a deployment.
>
> That said — like the band thresholds, those numbers are chosen, not calibrated. Same honest caveat."

---

## SECTION F — Architecture (he'll move faster here — it's solid)

### Q31. "Why one Pydantic model as the universal contract?"
> "`BiasReport` is consumed by the CLI, the REST API, the Streamlit dashboard, and the PDF generator — with **zero translation between them.** Four output surfaces, one shape.
>
> The payoff is that adding a field propagates everywhere automatically, and a type mismatch is caught at **validation time**, not silently at runtime in the PDF generator three layers away from the bug. The alternative — each output layer reshaping the data — is where drift lives: the dashboard shows one number, the PDF shows another, and nobody knows which is right. On a compliance tool, that's not a cosmetic problem."

---

### Q32. "Explain the async + semaphore design."
> "A 100-variant × 5-run audit is **500 API calls.** Sequentially, at ~2 seconds each, that's over 15 minutes and the tool is unusable. So all calls are dispatched concurrently with `asyncio.gather`.
>
> But naive `gather` on 500 calls fires 500 simultaneously and you're instantly rate-limited — or worse, partially rate-limited, so *some* variants fail and your demographic groups end up with unequal sample sizes, which quietly corrupts the statistics.
>
> So an `asyncio.Semaphore` caps in-flight calls at `max_concurrent_calls`, default 10. Full concurrency up to a bound the provider tolerates."

**That middle paragraph — rate limiting doesn't just slow you down, it *biases your sample* — is the insight. Most candidates only say "avoid 429s."**

---

### Q33. "What happens if 3 of the 500 calls fail?"
**⚠️ The report doesn't say. Think about it.**
> "This matters more here than in a typical pipeline, because **unequal group sizes damage the statistics** — ANOVA is most robust to its assumption violations when groups are balanced, and a group that silently lost 2 of its 5 runs is now both underpowered and unbalanced.
>
> So the correct behavior is: retry with backoff, and if a variant still can't complete, either **drop the whole group** or **fail the audit loudly** — never quietly proceed with a lopsided sample and print a confident verdict. `[FILL: what the code actually does. If it just proceeds, that's an honest gap and the right answer is 'the audit should refuse to score on an incomplete matrix.']`"

---

### Q34. "Why support three providers?"
> "Two reasons, and the second one only became obvious later. The plain one: users audit the model they deploy, and that isn't always Claude. Ollama support also means an organization can audit **locally, with no data leaving the building** — which matters when the prompts contain real candidate data.
>
> And the one I'd emphasize now: multi-provider is what makes a **cross-family judge** possible (see Q28). Audit Claude, judge with GPT. The infrastructure for the strongest methodological fix in this project is already there."

---

### Q35. "Why fpdf2 over WeasyPrint or ReportLab?"
> "fpdf2 is pure Python — no `libcairo`, no `libpango`, no OS-level binaries. So the Docker image needs nothing beyond the Python runtime, which keeps the image small and the build reproducible.
>
> The trade-off is real and I'd name it: **limited Unicode outside Latin-1.** Which is a genuinely awkward constraint for a tool whose entire purpose is testing names across cultures — a name with a character outside Latin-1 will not render. There's a `_safe()` encoder that downgrades em-dashes, smart quotes and bullets to ASCII, but that's a workaround, not a solution.
>
> If the matrices needed to cover, say, Chinese or Arabic names in the *report body*, fpdf2 would be the wrong call and I'd take the heavier dependency."

**Choosing a library and then naming the exact scenario where your own choice breaks — architects love this.**

---

## SECTION G — The hard cross-cutting questions

### Q36. "Weights: 35 / 30 / 10 / 10. Where did those come from, and why don't they sum to 100?"
**Two questions in one, and the second is a detail-check.**
> "They sum to 85. There's a fifth reserved weight — `length`, at 15% — defined in config but **not folded into the composite** in the current implementation; length variation is tracked separately as an alert threshold. So the four active weights are renormalized over their own sum.
>
> That's a config-versus-code mismatch and it's exactly the kind of thing that rots: a weight that exists in configuration and does nothing is a trap for the next person who edits it, who will reasonably assume changing it does something. It should either be wired in or deleted.
>
> As for *why* 35/30/10/10 — semantic content is weighted highest because **substantively different information is the most consequential harm**: it's the difference between telling one candidate about a growth path and not telling another. Tone matters but is more cosmetic. Structural and judge are lower because they're noisier — heuristics and a probabilistic judge respectively.
>
> But like the bands, these are **reasoned, not calibrated.** I can defend the ordering. I can't defend 35 versus 33."

**"I can defend the ordering, I can't defend 35 versus 33" is precisely the right level of confidence. Claiming more would be a lie he can catch.**

---

### Q37. "In your LLM Eval Framework you argued a weighted composite is wrong — that a response 95% faithful with one hallucinated claim should still *fail*, so you used AND logic. Here you use a weighted average. Why the contradiction?"
**⚠️ THE CROSS-PROJECT TRAP. An interviewer holding both of your projects will find this. There is a correct answer and it makes you look excellent.**

> "It's not a contradiction — the two systems are measuring fundamentally different *kinds* of things, and the aggregation has to follow the measurement.
>
> **Hallucination is a defect. Bias is a gradient.**
>
> A hallucinated claim is a discrete, binary event — the claim is either supported by the source or it isn't. One of them is a *defect*, and a defect doesn't get averaged away by the parts of the output that were fine. That's why the eval framework uses AND logic: it's a **quality gate**, and gates are conjunctive. You don't let a fatal flaw through because everything around it was good.
>
> Bias isn't like that. There is no binary 'this response is biased' event — there's a *degree* of disparity across four different measurement axes, each of which is a continuous magnitude with its own noise. AND logic would be actively wrong here: it would mean any single lens crossing a threshold fails the entire audit, and with four noisy pipelines and no multiple-comparison correction, **you'd fail every model you ever tested.**
>
> So: **conjunctive logic for defects, weighted aggregation for magnitudes.** The eval framework gates. The auditor measures. Different jobs, different math.
>
> Where I'd concede a point: the *verdict band* on the auditor is doing gate-like work — 'Fail: halt deployment' is a binary consequence downstream of a continuous score. So there's an argument for a hybrid: composite score for the magnitude, plus an *override* rule where a single **severe** judge finding fails the audit outright regardless of the average — because 'severe' is the one signal in this system that behaves like a defect rather than a gradient."

**That final concession is what turns a good answer into the best answer in the interview. You defended the distinction, then found the one place where his objection is actually right, and designed for it in real time.**

---

### Q38. "Suppose the audit says Pass. Is the model fair?"
**A philosophical trap with a precise answer. Do not say yes.**
> "No — and the report should never let anyone read it that way.
>
> A Pass means: *on the dimensions I tested, with the prompts I tested, at the statistical power I had, I did not detect a disparity.* That is a much weaker claim, and the gap between the two is where the liability lives.
>
> Everything a Pass **doesn't** cover: dimensions not in the matrix. Intersections not tested. Prompts other than the one audited — bias is prompt-specific, and a model fair on one template can be badly unfair on another. And, most importantly, **effects too small for 3 runs to detect** — see the power question.
>
> **Absence of detected bias is not evidence of fairness.** If the tool's output ever gets read as a certificate, the tool has done harm. Which is why the limitations section is generated into every report, not left as an optional appendix."

---

### Q39. "Who owns the decision when the tool says Fail?"
> "Not the tool. It's advisory — it produces evidence, statistics, and documentation. A human decides. The remediation output is *prompt-rewrite suggestions*, not an automatic prompt change; nothing is auto-applied.
>
> That's deliberate and it's the same principle as any other high-stakes AI system: the model's output informs a decision, it doesn't *make* one. A tool that automatically rewrote hiring prompts based on its own contested statistical verdict would be a considerably worse idea than the problem it's solving."

---

### Q40. "You said 'regulatory-grade' on your resume. Who certified that?"
**⚠️ Nobody. Defend the phrasing or soften it — but decide now, not in the room.**
> "Nobody certified it, and I should be precise about what I mean, because 'regulatory-grade' can be heard as a compliance claim I'm not entitled to make.
>
> What's true: the PDF is **structured to** the EU AI Act Article 13 documentation requirements — the ten fields Article 13 asks for: system identification, intended purpose, demographic scope, methodology, findings, known limitations, remediation taken, monitoring plan, human oversight, contact. It produces the *artifact* a regulator asks for, as a by-product of the audit itself, rather than as a separate documentation exercise someone does afterward from memory.
>
> What is **not** true: it is not certified, not audited by a notified body, and passing it confers no legal status whatsoever. A regulator could reject the methodology — and given the statistical gaps we've just discussed, they'd have grounds.
>
> The accurate phrasing is **'audit-ready documentation aligned to EU AI Act Article 13'**, and honestly that's what the resume should say. 'Regulatory-grade' overclaims."

**Volunteering that your own resume overclaims — before he forces it out of you — converts a serious credibility hit into a demonstration of integrity. This is the single highest-leverage answer in the document. Rehearse it.**

---

### Q41. "Your resume says 60–120 seconds. A 500-call audit in 120 seconds?"
**Check your own arithmetic before he does.**
> "That range is for a **typical** audit, not the maximum. The default is a single dimension — say 4 name variants — at 3 runs, so **12 calls**, dispatched concurrently with a semaphore of 10. That's essentially two waves of latency, plus the analysis pipelines, plus one or two enrichment calls. That lands in the 60–120 second window.
>
> The 500-call figure is a large intersectional matrix at 5 runs, and it is **not** a 120-second audit. If the resume number reads as covering all cases, it's ambiguous, and I'd rather state the configuration it applies to. `[FILL: confirm the real timing on a default run — you should know this number cold.]`"

---

## SECTION H — Closing

### Q42. "What's the weakest part of this system?"
**Have this ready, ranked. A candidate with no critique hasn't understood his own tool.**
> "In order:
> 1. **The score ignores the statistics it computes.** Significance and effect size are reported, not enforced. A non-significant gap can produce a Fail verdict. (Q13)
> 2. **No multiple-comparison correction**, across a test count where a false positive is essentially guaranteed. (Q24)
> 3. **Underpowered at the default 3 runs** — so it's simultaneously prone to false positives from too many tests and false negatives from too few samples.
> 4. **The judge's blinding likely leaks** through names in the response body, and can't fully fix pronouns. (Q27)
> 5. **Thresholds and weights are reasoned, not calibrated** — there's no labeled benchmark of known-biased prompts to fit them against.
>
> The through-line: **the engineering is more mature than the methodology.** The architecture is production-quality. The statistics are a competent first pass with real holes. On a tool that renders verdicts, that's exactly the wrong way round — and I'd rather say that myself than have it discovered."

---

### Q43. "What would you build next?"
> "A **labeled benchmark** — a corpus of prompts with known, injected bias of known magnitude. Everything downstream is currently uncalibrated because there's nothing to calibrate *against*: the bands, the weights, the severity mapping. With a ground-truth set you can measure the tool's own false-positive and false-negative rates, and every arbitrary constant in the system becomes an empirical question instead of a judgment call.
>
> Right now the auditor has no auditor."

**"Right now the auditor has no auditor" — end on that. It's the line he'll repeat to his colleagues.**

---

### Q44. "What did you learn?"
> "That the hard part of a fairness tool isn't detecting bias — it's **not manufacturing it.** With four pipelines, six dimensions, and no correction for multiplicity, I can find a significant disparity in a perfectly fair model just by running enough tests. A tool that cries bias is worse than no tool, because it burns the credibility that a real finding needs.
>
> Which flips the design goal. The instinct is to make the detector as sensitive as possible. The correct goal is to make it as **trustworthy** as possible — and those pull in opposite directions."

---

### Q45. "Why does this project exist? Nobody asked you to build it."
> "The EU AI Act classifies hiring and lending AI as high-risk, and requires documented bias testing before deployment and an explanation to regulators on request. So there's a compliance obligation with a real deadline attached.
>
> And there was no open-source tool that did all three things at once: automated multi-run counterfactual testing, statistical significance testing, and the regulatory paperwork. You could find pieces. You couldn't find one run that produces the evidence, the statistics, and the document a regulator asks for.
>
> The insight is that **the documentation should be a by-product of the audit, not a separate exercise.** The moment compliance paperwork is written by hand *after* the testing, it drifts from what was actually measured — and the version that reaches the regulator is a description of what someone remembers doing."

---

### Q46. "If you had to defend this in front of an actual regulator, what happens?"
**The final boss. Answer it with the honesty you'd need in that room.**
> "I'd defend the **method** and I'd disclose the **limits**, and I would not let anyone in that room believe a Pass is a clean bill of health.
>
> What holds up: counterfactual testing is the right methodology, it's the standard approach in the fairness literature, and holding the prompt constant while varying only the demographic signal is a genuinely sound causal design. Multiple runs with a statistical test is the right way to separate signal from noise. Independent measurement lenses with a blinded judge is a defensible architecture. And every report already carries its own limitations section.
>
> What I'd have to concede: the significance testing doesn't gate the score, there's no multiple-comparison correction, the default run count is underpowered, and the thresholds are conventions rather than calibrated constants. All four are fixable, none of them are fixed.
>
> So the honest position is: **this is a well-built instrument with a methodology that isn't finished.** It produces real evidence and real documentation. It should not be the last word on whether a model is fair — and any organization treating it as one has misread what it's telling them."

---

## Cheat card — say these exactly

| Trigger | Line |
|---|---|
| Opening | "A/B testing where the metric is equitable treatment instead of conversion." |
| Why multi-run | "One run tells you nothing. LLMs are non-deterministic — you're comparing distributions, not responses." |
| Effect size | "The p-value says the difference is real. Cohen's d says it's big enough to care about. For fairness, the second one matters more." |
| **The scoring flaw (own it)** | **"The statistics are reported, but they don't gate. The score should be Cohen's d, not a raw gap."** |
| Power | **"A Pass from an underpowered test isn't evidence of fairness. It's absence of evidence."** |
| Multiple comparisons | "Twenty tests at α = 0.05 means I *expect* a false positive. A tool that cries bias is worse than no tool." |
| Heuristics defense | "A biased ruler still measures a difference correctly — as long as it's the same ruler for everyone." |
| Self-audit | "A blind spot can't see itself. Audit Claude, judge with GPT — the multi-provider plumbing is already there." |
| Eval-framework contradiction | **"Conjunctive logic for defects. Weighted aggregation for magnitudes. Hallucination is a defect; bias is a gradient."** |
| The Pass verdict | "Absence of detected bias is not evidence of fairness." |
| "Regulatory-grade" | "Audit-ready documentation aligned to Article 13. Not certified. 'Regulatory-grade' overclaims — that's on my resume and I'd change it." |
| Closing | **"Right now, the auditor has no auditor."** |

---

## Prep priority

**Tier 1 — the statistics. You wrote "statistical rigor" on your resume; you will be held to it.**
1. **Q13 / Q22 — the score ignores the p-value.** The biggest hole. Own it, then fix it out loud (score on Cohen's d; gate on significance).
2. **Q24 — no multiple-comparison correction.** Name Bonferroni and Benjamini-Hochberg. Connect it to the power problem — same remedy.
3. **Q23 — underpowered at n=3.** "A Pass from an underpowered test is absence of evidence."

**Tier 2 — the credibility questions.**
4. **Q40 — "regulatory-grade."** Volunteer that your own resume overclaims. Highest-leverage answer in the doc.
5. **Q37 — the cross-project contradiction with your LLM Eval Framework.** He may well have both. "Defects gate; magnitudes average."
6. **Q28 / Q27 — Claude judging Claude, and the blinding leak.**

**Tier 3 — raise before he finds them.**
7. **Q18** — the negative-similarity-gap clamp bug.
8. **Q14 / Q36** — thresholds and weights are reasoned, not calibrated.
9. **Q38** — a Pass is not a fairness certificate.

## The `[FILL]` list — do not walk in blank

- **Q7** — what temperature did you actually use? If it was the provider default, say so and say you'd pin it.
- **Q27** — does `llm_judge.py` scrub names from the **response body**, or only omit the group label? Check the code. This determines whether your blinding is real.
- **Q33** — what does the executor do when some of the 500 calls fail? Does the audit proceed on an unbalanced sample?
- **Q41** — the real wall-clock time of a default audit. Know this cold; it's on your resume.
- **Q40** — decide before the interview whether "regulatory-grade" stays on the resume. My recommendation: change it to "audit-ready documentation aligned to EU AI Act Article 13." It's stronger *because* it's precise.
