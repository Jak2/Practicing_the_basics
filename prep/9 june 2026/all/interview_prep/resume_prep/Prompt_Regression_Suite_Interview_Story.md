# Prompt Regression Suite — The 3-Minute Spoken Story

**Use when:** "Tell me about a project you're proud of." / "Walk me through something you built."
**Target:** ~3 minutes. ~420 words of spoken text. Do not rush the villain.

---

## THE STORY

**[1 — Setup: the world before]**

Every team shipping an LLM feature ends up in the same place. Prompts live in the repo like code — but they're tested like folklore. Someone edits a system prompt, runs it once by hand, reads the output, says "yeah, that looks better," and merges it. Unit tests pass, because unit tests check logic and types. Nothing in that pipeline checks *meaning.*

**[2 — The real problem: stakes, not speed]**

And the failures that come out of that gap are not loud. They're quiet, and they're expensive.

Three shapes, over and over. A developer refactors a verbose prompt to be cleaner. It *is* cleaner. And the model starts giving shorter, less detailed answers — and nobody notices for two weeks, and then only through user complaints, not monitoring. That's the **silent shortening.** A financial-analyst prompt gains one new instruction, and the model, now busy attending to that instruction, quietly stops citing its sources — so unverified financial assertions start reaching customers. That's the **citation drop.** And the third one is the one that keeps you up: the provider silently updates the base model underneath you. Tone shifts. Output length drifts. Your JSON keys come back in a different order. **No code changed.** The failure arrived through the API.

**[3 — The obvious build, and why it's a trap]**

So the obvious move is: write tests. Golden outputs. Snapshot the response, assert the next one matches.

That's a trap, and you find out in about ten minutes. Because at temperature 0.7, the same input *legitimately* produces different output every single run. Your snapshot test fails on the second run and it's not a regression — it's Tuesday. So you loosen it. And you keep loosening it. And you loosen it until it passes everything, including the bugs.

**[4 — THE VILLAIN, NAMED]**

That's when I actually named the thing I was fighting, and it wasn't a bug. It was this:

**The thing I have to regression-test has no stable oracle.**

Think about what that means. Regression testing has *one* load-bearing assumption — that "correct" holds still. That yesterday's answer is a fact you can measure today against. Take that away and the whole discipline evaporates. And what's underneath it is the failure an architect actually fears: **the prompt change that is an improvement in nine cases out of ten and a silent catastrophe in the tenth.** It doesn't break. It gets *less reliable on average.* You cannot unit-test that, because the same input is *supposed* to give you a different answer every time — so the tenth case doesn't look like a failure. It looks like variance. And variance is something every engineer on the team has already been trained to ignore.

**[5 — The hero]**

The insight was to stop looking for the oracle.

I don't assert on the output. I assert on a **distribution, relative to its own past.** Run each test case three times, average the scores, and compare the mean against a *stored baseline* for that specific prompt. Regression fires only when the mean drops more than the delta threshold — five points — below that baseline. Absolute quality is irrelevant. A prompt that always scores 0.78 doesn't flag at 0.76. It flags at 0.73.

The oracle isn't a correct answer. The oracle is **yesterday's version of this same prompt.**

And to score it at all, three tiers, cheapest first: twelve free deterministic rules, then a local semantic-similarity model — 80 megabytes, runs in five milliseconds, costs nothing — and only if both of those pass do I spend money on an LLM judge. Fail one free check and the paid call never happens.

**[6 — THE DIP]**

And then I looked at my own two constants.

The threshold that says "this test is too noisy to trust" — standard deviation above **0.05**.
The threshold that says "this is a real regression" — a drop of **0.05**.

**The same number.** My noise floor and my signal were exactly the same size.

Which means the thing I built the entire system to detect is, by my own definition, indistinguishable from the thing I built the entire system to ignore. Every clean layer, every typed contract, every governance rule — all of it stacked on top of two numbers I had picked *by feel*, that happened to collide, and I hadn't noticed.

**[7 — The turn: a realization, not heroics]**

I didn't fix it with cleverness. I sat with it and realised what it was actually telling me.

It wasn't a bug. It was a **category error.** I had been treating my thresholds as *architecture* — things you reason about, defend, design well. They're not. They're **measurements.** And you cannot reason your way to a measurement. Nothing in a well-structured six-layer system tells you what a five-point drop *means* on a real prompt, because that's an empirical fact about the world, and I had never gone out and gotten it.

The honest fix isn't a smaller number. It's that the regression threshold has to be *derived from each test's own observed noise* — a multiple of its actual std_dev, not a global constant — and that requires a labelled corpus: real prompt diffs, each marked regression-or-not by a human. I don't have one. That is, still, the true limit of the system, and I'd rather say that out loud than dress it up.

**[8 — The landing]**

What shipped is a merge gate. Touch a prompt file, and the reverse index finds exactly the affected tests — three prompt files out of eighty runs about twelve tests, not eighty. Scores post to the PR with the delta and the judge's verdict; drop below baseline and the merge is blocked. Baselines auto-advance on merge to main so improvements are recognised, never on PRs so regressions can't be erased, and a forced reset throws a `ValueError` if you don't type a reason — which is stored, forever, with your commit SHA.

And every Monday at 09:00 the full suite runs against the live model, on main, with nothing changed — because model drift never, ever arrives in a pull request.

The principle I took out of it: **when you can't test the thing, test its distance from itself.** And then — measure the distance you called too far. Don't pick it.

---

## Why this works on this audience

- **It opens on a failure mode, not a feature.** Senior engineers pattern-match on "have I been burned by this?" — silent shortening and citation drop land in the first fifteen seconds.
- **The villain is a real epistemology problem, not a hard bug.** "The thing I must regression-test has no stable oracle" is a sentence an architect *feels*. It reframes you from "person who wrote a script" to "person who found the load-bearing assumption and noticed it was missing."
- **The obvious build is explicitly named and killed.** Interviewers are already thinking "why not golden outputs?" — you kill it before they ask, which buys you their attention for the rest.
- **The dip is self-inflicted and specific.** 0.05 == 0.05 is falsifiable, checkable, and slightly embarrassing. Candidates who volunteer a specific self-criticism read as *senior*; candidates whose struggle was "it was tricky to debug" read as junior.
- **The turn is a realisation, not a rescue.** "Thresholds are measurements, not architecture" is a transferable idea. They will remember that sentence longer than they remember the project.
- **It ends conceding an open gap.** You do not claim you solved calibration. That restraint is the strongest credibility signal in the whole three minutes — and it pre-empts the interviewer's best attack by making it your own closing line.

---

## Delivery notes

| Beat | Time | How to say it |
|---|---|---|
| Setup | ~20s | Conversational, slightly wry. "Tested like folklore" — let it land, small pause. |
| The three failures | ~30s | Speed up. Rhythm of three. Hit **"No code changed"** hard, then stop. |
| The trap | ~20s | Faster still. "It's not a regression — it's Tuesday" is the laugh line. Don't oversell it. |
| **The villain** | ~30s | **Slow all the way down.** Say the sentence — *"the thing I have to regression-test has no stable oracle"* — then **silence for two full beats.** This is the moment the story is for. |
| The hero | ~30s | Calm, mechanical, confident. You're just explaining now. Numbers land better said flat. |
| **The dip** | ~25s | Drop your volume. Say the two 0.05s as if you're still slightly annoyed at yourself. Pause after **"The same number."** |
| The turn | ~25s | Quiet, reflective. Do **not** perform triumph — there isn't any. The realisation *is* the payoff. |
| The landing | ~30s | Pick the pace back up. Concrete, brisk. Land the final principle and **stop talking.** |

**If they interrupt during the villain — let them.** That interruption means it worked. Answer, then say "so that's exactly the problem I had to solve" and pick up at the hero.

**If you have 90 seconds, not 3 minutes:** setup → villain → hero → the 0.05 collision → the merge gate. Cut the three failure modes to one (silent shortening) and cut the Monday run.

---

## Lines to memorize

1. *"Prompts live in the repo like code, but they're tested like folklore."*
2. *"Your snapshot test fails on the second run and it's not a regression — it's Tuesday."*
3. **"The thing I have to regression-test has no stable oracle."** ← the whole story in one line
4. *"It's an improvement in nine cases out of ten and a silent catastrophe in the tenth. It doesn't break — it gets less reliable on average."*
5. *"The oracle isn't a correct answer. The oracle is yesterday's version of this same prompt."*
6. *"My noise floor and my signal were exactly the same size."*
7. *"Thresholds aren't architecture. They're measurements. You can't reason your way to a measurement."*
8. *"Model drift never arrives in a pull request."*
9. *"When you can't test the thing, test its distance from itself."*

---

## [FILL] list

| # | What to supply / verify |
|---|---|
| 1 | **[FILL: confirm the 0.05-vs-0.05 collision was something you actually noticed *during the build*, or whether you're recognising it now.]** The source states both defaults (`std_dev > 0.05` flags flaky; `delta_threshold = 0.05` triggers regression) but **never says you noticed the collision.** Both framings are fine and both are honest — but pick one and say it consistently. If you're seeing it now, say *"looking back at it, the thing that bothers me most is…"* rather than narrating it as a struggle you lived through. **Never claim a war story that didn't happen.** |
| 2 | **[FILL: was this used by a real team, or is it a portfolio system?]** The story never claims users — deliberately. Keep it that way unless you can name one. |
| 3 | **[FILL: do NOT introduce a "4 minutes vs 3 days" style speed claim.]** The source contains no manual-review-time comparison anywhere. Its only timing facts are: 6–8× concurrency speedup on a 10-test suite, ~5ms per semantic pair, ~0.5s model first load, weekly Monday 09:00 UTC run. If you want a time-saving line, you must source it yourself. |
| 4 | **[FILL: the "cuts API costs 50%" resume claim is deliberately absent from this story.]** That is intentional — the source calls it *estimated*, never derived. If asked, go to the Q&A file §5. Do **not** volunteer the number in the story. |
| 5 | The "three prompt files out of eighty runs about twelve tests" figure is from the source (§6.4) — it is an illustrative example in the report, not a measured production stat. Phrase it as *"a PR touching three of eighty prompt files runs about twelve tests"* — a property of the design, which is true — never as *"in production we saw…"*. |
