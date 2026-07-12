# RF Keyword Generator — The 3-Minute Story
### Spoken. Not read. Nokia Networks · 5G RF Keyword Generator

> **Use when they say:** "Tell me about a project you're proud of." / "Walk me through something you built with an LLM." / "Tell me about a hard technical decision."

---

## THE STORY

*(Target: ~3 minutes spoken. Beats are marked. Slashes are breath marks, not punctuation.)*

---

### 1 · SETUP — the world before

> At Nokia I was on 5G test automation. Everything we tested ran through Robot Framework — every UE registration, every authentication, every handover, written as `.robot` keywords by hand.
>
> And the thing about Robot Framework is that it's *fussy*. It's indentation-sensitive. `RETURN` is case-sensitive. A variable is `${imsi}` and if you forget the closing brace it's not a variable any more, it's a string. Multi-line calls need a `...` continuation marker. None of that is hard. All of it is tedious. And most of the keywords we wrote were the same five shapes over and over — register a UE, authenticate it, hand it over, open a session, tear it down.

---

### 2 · THE REAL PROBLEM — stakes, not speed

> Now, "it was slow" is the boring version of this problem, and it's not the one that mattered.
>
> Here's the one that mattered. **The scarce resource on that team was senior engineer time.** The seniors were the only people who could design multi-vendor interoperability scenarios — Nokia gear talking to somebody else's gear, which is where the genuinely hard 5G bugs live and where the ugly surprises come from. That's the work only they could do.
>
> And they were spending their hours writing `Register UE On AMF` for the four hundredth time. / We weren't losing minutes. We were spending our most expensive people on the cheapest work we had.

---

### 3 · THE OBVIOUS BUILD — and why it's a trap

> So the obvious build is right there, and I want to be honest that I could see it: **put a text box in front of an LLM and ask it to write the Robot Framework keyword.** Tester types "register a UE with IMSI one-two-three... and verify auth succeeds," model writes the `.robot` file. Done in an afternoon.
>
> And it *demos beautifully.* That's the trap. It works in the demo. It works in the second demo. It works most of the time in production.
>
> **Most of the time.**
>
> And I sat with that phrase, and I started asking a different question. Not "will it work?" — it will. The question is: **when it doesn't work, what does that look like?**

---

### 4 · THE VILLAIN, NAMED

> And this is the thing I got stuck on, and it's what the whole project turned into.
>
> If an LLM writes bad Robot Framework, one of two things happens.
>
> The first: it writes broken syntax. Missing `***` section header. `$variable` instead of `${variable}`. Wrong indentation. **And that's fine.** That's a *gift*. It explodes immediately, someone sees a red parse error, and they fix it in thirty seconds.
>
> The second is the villain. The model writes Robot Framework that is **syntactically perfect and semantically wrong.** It parses. It runs. It passes code review, because it *looks* exactly like every other keyword in the suite. And it quietly asserts the wrong thing — or, worse, it drops the verification step entirely and just asserts that nothing crashed.
>
> **That test goes green.** / Forever.
>
> And now you have something worse than no test. You have a test everybody *trusts* — sitting in a 5G regression suite, reporting pass, covering nothing. In test automation that's not a bug. **That's a lie with a build badge on it.**
>
> So that was the villain. Not "the LLM makes mistakes." **The LLM makes mistakes that look like success.**

---

### 5 · THE HERO — the constrained-generation insight

> Which led me to the one decision this whole project rests on:
>
> **The LLM never writes the code.**
>
> Not "the LLM writes the code and I check it." Not "the LLM writes the code and I prompt it very carefully." **It is structurally prevented from ever emitting a single character of Robot Framework.**
>
> Here's what it does instead. The tester types free English. The LLM — Claude Haiku, deliberately the small one — gets exactly one job: **read that sentence and give me back JSON.** IMSI. Source cell. Target cell. Auth method. Expected result. That's it. That is the entire surface area of the model in my system.
>
> Then **deterministic templates** — hand-written, reviewed once, correct by construction — take those values and produce the `.robot` file. And then the last stage: I import **Robot Framework's own parser** — `get_model()` from `robot.api`, the same parser RF uses to run real tests — and I run it on the output before anyone sees it. If it doesn't parse, it never leaves the building.
>
> And underneath all of it, the regex extractor I'd built *first* is still sitting there as a fallback — so if the LLM returns garbage JSON, or the API's down, the tool doesn't fail, it degrades.
>
> **The shape of it:** the LLM does the one thing it's genuinely great at — understanding that "mobile identity" and "IMSI" mean the same thing, that "subscriber wants to authenticate with EAP-AKA" means `auth_method: EAP-AKA`. And it is *structurally forbidden* from the thing it's bad at — producing exactly-correct syntax, deterministically, every single time.
>
> **Fuzzy in. Exact out. And a machine standing at the door between them.**

---

### 6 · THE DIP

> And then the deterministic half of my beautiful deterministic system started producing broken files.
>
> Robot Framework wants `${ue_context}`. Python's `.format()` wants `{imsi}`. **Same brace. Two different languages, in one string.** So inside a template, the slots I'm filling are single-braced — `{imsi}` — and the literal RF variables I'm *emitting* have to be doubled — `${{ue_context}}` — so `.format()` collapses them back down to one.
>
> Miss one. Just one. And you get malformed `.robot` output, or a `KeyError` on a variable name you never intended to substitute in the first place.
>
> [FILL: confirm this actually happened to you, and how you found it — a test failing, a tester reporting a broken file, or you catching it yourself. The source flags the `{{`/`}}` escaping as "a common bug — forgetting this produces malformed .robot output" in the design write-up, but does not confirm it bit you personally. **If it did not, cut this beat and use the [ALTERNATIVE DIP] below instead — do not fabricate an incident.**]
>
> And the part that actually stung: **I'd spent the whole design being suspicious of the LLM.** I'd built a cage around the model. And the thing shipping broken files was *me*. My hand-written, deterministic, correct-by-construction templates.

---

### 7 · THE TURN — a realization, not heroics

> And that's when it landed properly.
>
> I'd built the parser gate thinking of it as *the LLM's chaperone.* Something to catch the model.
>
> But the model can't produce syntax at all. **It was never the thing that could break the syntax.** The only thing in that entire pipeline that could emit malformed Robot Framework was the deterministic layer — the human-written templates. Me.
>
> So the gate wasn't there to police the LLM. **The gate was there to police whoever writes the next template** — which is me, at 6pm, on template number six, when the LLM has nothing to do with it.
>
> That reframed the whole thing. *Determinism is not the same as correctness.* Deterministic just means it's wrong the same way every time. So the parser stopped being a fallback and became the **hard gate the entire pipeline exits through**, no exceptions, LLM path or regex path or template path — everything walks past `get_model()` on its way out the door.

---

### 8 · THE LANDING

> Where it ended up: a tester types a sentence, and in **one to two seconds** they get a valid `.robot` file they paste straight into their suite.
>
> It went to **50+ generations a week** — and I know that number because it's the one thing I actually instrumented; every `/generate` call is logged, and I aggregated it. It got there with **zero promotion.** I never announced it. [FILL: confirm — the source says one senior tester picked it up for repetitive registration cases during a sprint, mentioned it in standup, three more tried it, and within two weeks most of the team was on it. Confirm that's true to your memory before you say it.]
>
> Keyword creation went from **hours to minutes.** [FILL: know the provenance of "hours" — there is **no measurement of the manual baseline anywhere in the project.** The 50+ is instrumented; this is directional. If pressed, say so — do not invent a stopwatch study.]
>
> And the seniors got their afternoons back for the multi-vendor interop work that was the actual job.
>
> **But the line I'd leave you with is the one about the villain.**
>
> When you put a language model in front of engineers who are going to *trust its output*, the question is never "can it do this." It usually can. The question is **"what does it look like when it's wrong."**
>
> A syntax error is a gift. It screams.
>
> The thing I built the entire architecture to prevent — is the test that runs green while testing nothing.

*(Stop. Do not add a summary sentence. That's the ending.)*

---

### [ALTERNATIVE DIP] — use this if the brace bug did not actually happen to you

> Use this only if beat 6 isn't true. It is fully source-supported.

> I put it in front of five testers and gave them twenty descriptions each to run through it. And I sat there and watched descriptions fail.
>
> Not fail *loudly* — fail as in: the procedure didn't get detected, or the params came back empty. Someone typed *"test that mobile identity one-two-three... can join the network"* — and my regex extractor, which was looking for the literal word IMSI, just shrugged. The IMSI was **right there in the sentence.** It was fifteen digits, it was unambiguous, and my parser couldn't see it because the tester didn't use the vocabulary I'd guessed they'd use.
>
> And my first instinct was: fine, add "mobile identity" to the pattern list. Add "join" to the keyword list.
>
> **[TURN]** And I got maybe three patterns into that before I realised what I was doing. Every tester phrases things differently. Every new phrasing is a new regex. **I had signed myself up for a treadmill with no end** — a lexicon I would be maintaining forever, always one phrasing behind whoever typed next.
>
> That's when the split became obvious to me, and it's the thing I'd actually defend: *understanding English is not a job you can finish.* But *emitting correct Robot Framework* is a job you can finish once, in a template, and never do again. So give the unfinishable job to the model. Keep the finishable one.

---

## WHY THIS WORKS ON THIS AUDIENCE

| They are hiring for… | The story proves it because… |
|---|---|
| An engineer who can use an LLM in production, not a demo | You articulate the *failure shape* of an LLM, not its capabilities. Anyone can say "I used Claude." Almost nobody says "I designed around what it looks like when it's wrong." |
| Judgment, not tool-collecting | You explicitly describe the naive build, admit it demos better than what you shipped, and explain why you didn't ship it. That's the single strongest signal in the whole story. |
| Someone who won't create silent risk | The villain *is* silent risk. You named it before they had to. |
| Someone who tells the truth about their own work | The dip is you being the one who broke it — not the LLM, not a vendor, not a teammate. Interviewers notice who the villain in your dip is. If it's never you, they discount everything. |
| Model selection, not model worship | Haiku, deliberately, for a bounded task — and you can defend the tradeoff *and* concede you never measured the accuracy delta. |

---

## DELIVERY NOTES

| Beat | Time | Tone | Watch for |
|---|---|---|---|
| 1 · Setup | ~20s | Flat, factual | Don't linger. This is scenery. |
| 2 · Real problem | ~20s | **Slow down.** Land "senior engineer time" | The line is *"we were spending our most expensive people on the cheapest work."* Say it, then pause. |
| 3 · Obvious build | ~20s | Conversational, a little rueful | You must genuinely concede it demos beautifully. If you sneer at it, you lose the setup. |
| 4 · **Villain** | ~35s | **Slowest beat. Drop your voice.** | "That test goes green. / Forever." — take a full beat on that. This is the moment the interviewer leans in. Do not rush past it. |
| 5 · Hero | ~40s | Pick the pace back up. Confident. | Say **"The LLM never writes the code"** as a flat, complete sentence. Don't hedge it, don't qualify it, don't smile. |
| 6 · Dip | ~25s | Deflate. Genuinely. | The self-deprecation must be real: *"the thing shipping broken files was me."* |
| 7 · Turn | ~25s | Quiet realisation, not triumph | It's a *thought*, not a fix. "Determinism is not the same as correctness." |
| 8 · Landing | ~25s | Warm, then hard-stop | Say the last line and **stop talking.** The silence is the point. Do not add "so, yeah." |

**Total: ~3:10.** Cut beat 1 to two sentences if you're over.

**If they interrupt:** good. That means it's working. Answer the question, then say *"— and that's actually where the whole thing turned"* and rejoin at the beat you were on.

---

## LINES TO MEMORIZE — word for word

1. *"We weren't losing minutes. We were spending our most expensive people on the cheapest work we had."*
2. *"The question is never 'will it work.' It's: when it doesn't work, what does that look like?"*
3. *"A syntax error is a gift. It explodes immediately."*
4. *"The villain isn't that the LLM makes mistakes. It's that the LLM makes mistakes that look like success."*
5. *"That test goes green. Forever."*
6. *"The LLM never writes the code."*
7. *"Fuzzy in, exact out, and a machine standing at the door between them."*
8. *"Determinism is not the same as correctness. Deterministic just means it's wrong the same way every time."*
9. *"The gate wasn't there to police the LLM. It was there to police whoever writes the next template — which is me."*
10. *"The thing I built the entire architecture to prevent is the test that runs green while testing nothing."*

---

## [FILL] LIST — before you tell this story

| # | Beat | What you must supply |
|---|---|---|
| 1 | 6 · Dip | **Confirm the `{{`/`}}` escaping bug actually bit you**, and how you found it. The source describes it as "a common bug" in a design write-up — it does **not** confirm it happened to you. If it didn't, **cut beat 6 and use the [ALTERNATIVE DIP]**, which is fully source-supported (5 testers × 20 descriptions, tracked failures, regex breaking on "mobile identity … join"). |
| 2 | 8 · Landing | Confirm the adoption origin story: one senior tester → repetitive registration cases during a sprint → mentioned in standup → three more → most of the team in two weeks. Source states it; confirm it's true to your memory before you say it as fact. |
| 3 | 8 · Landing | The provenance of **"hours to minutes."** The manual baseline is **not measured anywhere in the source.** Know what you'll say when they ask. |
| 4 | 2 · Real problem | Your actual team size / number of seniors, if you want to make it concrete. Source only says "10-20 testers." |

---

## THE ONE FOLLOW-UP THAT IS COMING

They will ask: **"But if the LLM extracts the *wrong entity*, don't you get the exact villain you just described? Valid syntax, wrong test, green?"**

**Yes. Concede it immediately and completely.** Do not defend.

> "Yes. That's the residual risk and my architecture shapes it rather than eliminating it. What I bought is that the model can only be wrong *inside a slot* — it can never invent a keyword, never call the wrong library, never silently delete an assertion. That's a much smaller wrong. But it is still a silent wrong, and nothing in my pipeline catches it. The fixes are cheap and I know exactly what they are: an IMSI is fifteen digits — check it. `expected_result` is a closed enum — check it. And run the regex extractor *alongside* the LLM and flag disagreement to the user, which costs nothing because the regex is already there. I didn't build those. That's the honest answer."

**That answer is why they hire you.** The story earns the question. The concession wins it.
