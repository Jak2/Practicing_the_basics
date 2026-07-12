# LLM Evaluation Framework — The 3-Minute Spoken Story

> Every fact below traces to `LLM_EVAL_FRAMEWORK_REPORT.md`. Anything the report doesn't say is marked `[FILL]`. **Do not improvise over a [FILL] in the room.**

---

## THE STORY

### 1. Setup — the world before

*(slow, conversational)*

Here's a thing that's true of basically every team shipping an LLM feature right now, and almost nobody has a plan for it.

You write a prompt. You test it. It's good — call it 92% accurate. You ship it. Three weeks later it's at 61%, and *nothing on your side changed*. The provider pushed a model update. Same endpoint. Same parameters. Same price. No changelog. The API contract didn't move. The output quality did.

And you don't find out from your monitoring, because your monitoring watches latency and error rates, and the model is returning 200 OK, on time, every time. You find out from a support ticket. Days later.

### 2. The real problem — the stakes

So the honest framing isn't "quality dropped." It's that **the system lies to you and looks healthy while it does it.** Every dashboard is green. Every SLA is met. And a customer is being confidently told something wrong.

The two ways teams handle this today both fail. Human review panels — a panel doing 50 outputs a day cannot keep pace with a RAG pipeline serving thousands of queries, and reviewers disagree with each other and with themselves over time. Or automated string matching — which breaks on the first sentence where the correct answer is phrased a different but equally valid way. LLM output isn't deterministic. Exact match was never going to work.

So teams do the third thing, which is nothing. And discovery happens through the support queue.

### 3. The obvious build — and why it's a trap

The obvious answer, and the one I started with, is: **use a strong model as a judge.** Give it a rubric — accuracy, relevance, completeness, clarity, safety — score each one from 1 to 5, return strict JSON, normalise to a 0-to-1 score, set a threshold, ship it.

And I'll tell you honestly: that demos *beautifully*. You feed it a garbage response and it says 1.2 out of 5, "the answer is factually incorrect and does not address the question." Perfect. You feed it a great response and it says 4.8. It looks like you've solved the problem.

Then I fed it the response that actually scares me.

A *beautifully written* answer. Fluent. Confident. Well-structured, on topic, complete, perfectly safe. It scores accuracy 1 — but relevance 5, completeness 4, clarity 5, safety 5. Mean of 4.0. Normalised, that's **0.75**. My threshold was **0.60**.

It sailed straight through the gate. The rubric averaged a lie into a pass.

### 4. The villain, named

*(slow down here — this is the centre of the story)*

And that's the villain, and it isn't a bug. It's a *category*.

**The villain is the response that is fluent, confident, well-written — and quietly ungrounded.**

It's the worst adversary an eval system can face, because *every surface signal is positive*. It's well-formed, it's on-topic, it's safe. Every proxy you're tempted to measure says "good." It fails on exactly one axis, and it's the only axis that's expensive to check.

And then it gets worse, and this is the part that reorganised how I think about the whole problem.

**A true statement can still be a hallucination.**

Say that out loud and it sounds wrong. Here's why it isn't. In a RAG pipeline, you retrieve documents and you ask the model to answer *from those documents*. Suppose the model answers from its own training data instead — never even looks at what you retrieved — and it happens to be *right*, because its memory of the fact is correct.

Every truth-based check passes. A human reviewer nods. The answer is *true*.

But that response is a **defect**, because the retriever was bypassed. The model got lucky. And next week, on a query where its parametric memory is stale or wrong — a price that changed, a policy that got updated, a document you added *specifically so it would stop being wrong* — the exact same behaviour produces a confident lie, and there's no retrieval to blame, because retrieval was never in the loop.

The bug was there the whole time. Truth was hiding it.

So the villain, properly stated: **"is this true?" is the wrong question. The question is "is this grounded?"** And you cannot get from one to the other by being a better judge. You have to change what you measure.

### 5. The hero — the design insight

So I stopped building one smart evaluator and built **four independent ones**, and I made a rule: **none of them feeds another, and I never average across them.**

The one that carries the villain is **faithfulness**. It doesn't ask "is this true." It asks: **did every statement in this answer come from the retrieved context?** Score is supported statements over total statements. Threshold 0.80. A faithfulness score of 1.0 explicitly does *not* mean the answer is correct — it means the model *only used what I gave it*.

And the moment I separated groundedness from truth, I got something I genuinely didn't expect: **a two-axis diagnostic that names the guilty party.**

Run faithfulness *and* hallucination together, and the combination localises the bug:

- **High faithfulness, high hallucination rate** → the model stayed inside the documents and is still wrong. **The documents are wrong.** Go fix the corpus.
- **Low faithfulness** → the model is bypassing the retriever and generating from memory. **The retrieval isn't reaching the model.** Go fix the prompt.

That's the difference between an alert and an *assignment*. One wakes somebody up. The other tells them what to fix.

And the composition rule follows from the same idea. `overall_passed` is **AND logic** — every selected evaluator must pass its own threshold. No weighted composite, no averaging. Because a beautiful hallucination is exactly what a weighted average *rescues*. This is a quality **gate**, not a quality **summary**. A gate is conjunctive.

### 6. The dip

`[FILL: confirm this actually happened to you — the report describes the neutral-pass behaviour as a design, and does not narrate discovering it as a bug. If you didn't live this, tell it as "the flaw I found reviewing my own pass logic," NOT as an incident.]`

I had it running. Four evaluators, thresholds, Slack alerts, dashboard. And I was looking at a run where a test case came back green — `overall_passed = True` — with **faithfulness scoring a perfect 1.0.**

A *perfect* one point zero. On a RAG test.

And that number is too good. Real RAG answers don't land on 1.000. So I went and looked at the record, and the metadata said `skipped = True`.

The test case had no `context` field. And I had written the evaluator to do the polite thing: no context, nothing to measure, **return a neutral pass — score 1.0, skipped true.**

And AND logic dutifully read that 1.0 and concluded: *passed.*

Sit with that for a second. I had built a gate whose entire purpose was catching ungrounded output — and the way to get past it was **to send it nothing to ground against.** The one input that makes the check impossible was the input that guaranteed a green light. A CI workflow with a typo in a YAML field. A schema change upstream that quietly drops a key. Faithfulness reads 1.0 forever, and the dashboard is *green*, and nobody knows.

I'd rebuilt the exact thing I set out to destroy. A number that looks healthy and means nothing.

### 7. The turn

And the fix wasn't clever. It was a realisation, and it was almost embarrassing in how small it was.

**`skipped` and `passed` are not the same state. "I did not measure this" is not "this is clean."**

I had collapsed three states into two. Passed, failed — and *unmeasured*, which I'd quietly filed under passed because 1.0 was the convenient default.

And it's the *same* mistake as the villain, one level down. The confident answer that isn't grounded, and the confident score that isn't measured — both are **fluent output with nothing behind it.** I'd caught it in the model and then reproduced it in my own code.

So: unmeasured becomes its own state. If you *request* faithfulness and don't supply context, that's not a pass and it's not a skip — it's a **hard error on the test case**. You asked me to check something and then made it impossible to check. I'm going to tell you loudly, not hand you a 1.0.

**In a quality gate, absence of a measurement can never be allowed to look like a good measurement.** That's the whole lesson, and it now applies everywhere in the system: a missing context, a failed model call, zero extracted claims — none of them get to be silent, and none of them get to be green.

### 8. The landing

What it became: four evaluators, FastAPI on 8000, Celery workers pulling off Redis, PostgreSQL, a Streamlit dashboard, Slack alerts — one `docker-compose up`.

And the headline: a simulated model-provider update caused a **14-point faithfulness drop** in a RAG pipeline, and the framework caught it and fired an alert in **under 4 minutes.** The manual-review baseline is 2 to 3 days — and I want to be precise, because it matters: **the 4 minutes is a real end-to-end wall-clock. The 2-to-3 days is an estimate, not a measurement, and the regression was one I simulated.** I'd rather tell you that than have you find it.

But the number I actually care about isn't the 4 minutes. It's *which* number moved. **Faithfulness** dropped — not accuracy. Which means the new model started reaching outside the retrieved context. It didn't get dumber. It got **less obedient to the retriever.** That's a completely different bug, with a completely different owner, and no single quality score in the world could have told me that.

Which is the principle I took out of the whole thing, and it's the villain, inverted:

**A confident answer and a correct one are not the same object — and neither is a green score and a measured one. The job of an eval system isn't to ask whether the output is good. It's to make sure that every way of *looking* good has been ruled out.**

---

## Why this works on this audience

| Signal it sends | How it lands |
|---|---|
| **You know what an eval actually is.** | Most candidates say "I used LLM-as-a-judge." The truth-vs-groundedness distinction is a *research-level* separation and it's the fastest way to sound like someone who has genuinely operated a RAG system. |
| **You reason about failure modes, not features.** | The story is structured around what *defeats* the system, not what it does. Senior engineers hire for this. |
| **You will not bluff.** | Volunteering that "3 days" is an estimate and the regression was simulated, *before being asked*, buys more credibility than the number itself ever could. Interviewers are looking for the tell. Removing it is the move. |
| **You found your own bug.** | The dip is a bug in *your own reasoning*, not a library's, and the fix is a conceptual correction, not heroics. That's the highest-status kind of engineering story. |
| **Composition logic is a first-class concern to you.** | "A gate is conjunctive; a measurement is not" is a one-line principle that survives being repeated back to a hiring committee. |

---

## Delivery notes

| Beat | Time | Delivery |
|---|---|---|
| 1. Setup | 0:00–0:25 | Conversational. "92% today, 61% next week, nothing on your side changed." Let it land. |
| 2. Stakes | 0:25–0:45 | Harder. "The system lies to you and looks healthy while it does it." |
| 3. The trap | 0:45–1:15 | Concede the naive build sincerely — *"it demos beautifully"*. Then the numbers: **accuracy 1, mean 4.0, normalised 0.75, threshold 0.60.** Deliver those four numbers flatly. Let the arithmetic do the work. |
| 4. **VILLAIN** | 1:15–1:50 | **Slow down.** This is the centre. Pause after *"a true statement can still be a hallucination."* Let them react — they may interrupt. **If they interrupt here, you've won; go with it.** |
| 5. Hero | 1:50–2:20 | Speed up. Confident, clean. The two-axis diagnostic is the payoff — deliver the high/low branches crisply, they're memorable. |
| 6. **DIP** | 2:20–2:45 | **Drop your voice.** Sudden and concrete. *"A perfect 1.0. And that number is too good."* Do not soften it. Own the stupidity of it. |
| 7. Turn | 2:45–3:00 | Quiet. It's a realisation, not a victory. *"skipped and passed are not the same state."* Flat, not triumphant. |
| 8. Landing | 3:00–3:20 | Numbers first, caveat second (unprompted), then the principle. End on the principle and **stop talking.** Do not add anything after it. |

**Total: ~3:20 at a natural spoken pace. Do not rush the villain to save time — cut from the setup instead.**

---

## Lines to memorize

These are the load-bearing sentences. Word for word.

1. *"Same endpoint, same parameters, same price, no changelog. The API contract didn't move. The output quality did."*
2. *"The system lies to you and looks healthy while it does it."*
3. *"Accuracy one. Mean of four. Normalised, 0.75. My threshold was 0.60. It sailed straight through."*
4. **"A true statement can still be a hallucination — because in RAG, ungrounded means the retriever got bypassed. The model got lucky, and next week it won't be."**
5. *"'Is this true' is the wrong question. The question is 'is this grounded.'"*
6. *"High faithfulness and still wrong means the documents are wrong. Low faithfulness means the model is ignoring the retriever. That's not an alert, that's an assignment."*
7. *"A gate is conjunctive, not an average. A beautiful hallucination is exactly what an average rescues."*
8. **"I'd built a gate for catching ungrounded output, and the way past it was to send it nothing to ground against."**
9. **"`skipped` and `passed` are not the same state. 'I did not measure this' is not 'this is clean.'"**
10. *"The 4 minutes is a real wall-clock. The 3 days is an estimate. The regression was simulated. I'd rather tell you that than have you find it."*
11. *"It didn't get dumber. It got less obedient to the retriever."*

---

## [FILL] list

The report does **not** contain these. Fill them from the codebase or leave them out of the spoken version entirely.

1. **`[FILL: confirm the DIP actually happened to you.]`** — The report presents the `skipped=True → score 1.0` neutral pass as an intentional *design*, in §5.2 and §5.3. It never says you discovered it as a bug in a live run. **If you did not actually catch this in a run, you must reframe beat 6** as: *"Reviewing my own pass logic, I realised…"* — same insight, same power, zero fabrication. **Do not tell it as an incident if it wasn't one.** This is the single highest-risk line in the story.
2. `[FILL: the before/after faithfulness scores in the 14-point drop, and how many cases were in the golden set]` — you can deliver beat 8 without these, but if asked, do not guess.
3. `[FILL: whether the "simulated model provider update" was a scenario you actually executed end-to-end, or a designed/illustrative one]` — this changes whether you can say "I ran it" in beat 8. The report says "simulated," which is honest either way; do not upgrade it to "a real provider update."
4. `[FILL: whether the specific well-written-but-inaccurate response in beat 3 is a real example you tested, or an illustration of the averaging flaw]` — the arithmetic (1/5/4/5/5 → mean 4.0 → 0.75 vs threshold 0.60) is sound and traceable to the report's own rubric and formula. But if you never fed that exact case through, say *"the failure mode the rubric allows is…"* rather than *"then I fed it…"*.
