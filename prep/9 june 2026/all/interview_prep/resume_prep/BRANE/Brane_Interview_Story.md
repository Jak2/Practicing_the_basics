
Story below. One honesty rule first: a story an interviewer loves is one he can cross-examine. So the villain, the dip and the fix are all real things from your deep-dive — nothing invented. Three spots need your actual memory dropped in; I've marked them [fill]. Don't ship the story with a fabricated detail in those slots — that's the one thing that turns a great narrative into a disqualifier.

The structural trick: the villain is not a person and not a bug. It's the LLM's confidence. Managers and architects love that story because it's the problem they are afraid of.

The story (told out loud, ~3 minutes)
Setup — the world before.
"Brane runs a no-code platform. Business users drag together workflows out of units called Local Objectives. Every LO was one of two types: a HUMAN does it, or DIGITAL automation does it. And both share one property the entire engine is built on — when the step finishes, you trust the answer. A fetch returns what it returns. A calculation is a calculation. The engine commits it and moves on. Twenty other things downstream depend on that assumption."

The ask — sounds trivial.
"The company wanted a third type: AI_AGENT. An LLM does the work — extract the invoice fields, classify the ticket, summarize the case. On the surface that's a Tuesday. It's an API call. Everyone's first instinct, including some of ours, was: add a node, call the model, write the output."

The villain, named.
"Here's what that misses, and it's the whole project. An LLM is wrong with exactly the same confidence it is right. It hallucinates a vendor name in perfect JSON. It invents a line item that looks flawless. And we were about to feed that into an engine whose single foundational assumption is the output of a step is trustworthy the moment it exists. We weren't adding a feature. We were putting a probabilistic component into a deterministic machine and pointing it at customers' real business records.

The villain isn't the model being wrong. Wrong is fine — wrong is detectable. The villain is wrong and confident, because confident is what slips past you and gets committed."

The false-hero moment — the one every architect grins at.
"The obvious fix is: ask the model to check itself. Add to the prompt, 'produce the output, and tell me if it's correct.' And it works. In a demo it works beautifully. The model produces JSON, and a field that says "confident": true.

Which is worthless. Because a confidently-wrong answer certifies itself. You didn't build a check — you built a rubber stamp and put it on the thing that needed checking. That was the moment the actual principle fell out: the thing that generates must never be the thing that certifies."

The design — hero enters.
"So the architecture became one sentence: probabilistic core, deterministic gate.

The agent generates — that's the probabilistic core, and we let it be probabilistic. But it commits nothing. Instead the output goes to a separate verifier lane: first deterministic business rules — real code, the platform's existing rule engine, cheapest and most certain, and it short-circuits on the first failure. Only if that passes does an AI verifier run — a different model class, a different call. And only then, optionally, a human.

Pass, and the workflow's real primary function fires. Fail, and here's the part I like — the failure report is fed back into the next prompt, and the agent tries again. It sees why it was rejected. That's a correction loop, not a retry loop. Blind retry just re-samples the same failure."

The dip — where the story earns attention.
"And then we ran it, and it fell over. Not on the AI. On the plumbing.

Two things, both mine to fix.

First: it was slow, and for a stupid reason. Attribute-level RBAC — the agent only sees the fields it's been granted, because an invoice extractor must never see a salary field. But the naive check is a database round-trip per attribute, per attempt. And it's a loop. So the same fields get re-checked on every iteration. The permission system that existed to make the agent safe was the thing making it unusable. [fill: what the latency actually looked like — "an attempt was spending more time asking permission than thinking"]

Second, and worse: the loop kept dying on garbage. LLMs return broken JSON a meaningful fraction of the time — wrapped in markdown fences, trailing prose after the closing brace, a missing field. And a parse exception was killing the entire run. Think about how backwards that is: we built an elaborate, careful correction loop whose whole purpose is to survive the model being wrong — and it was crashing on the single most common way the model is wrong. [fill: the specific malformation that bit you — the code-fence one, or the trailing-text one]"

The turn — and this is the line to land.
"The fix for the second one wasn't a better parser. It was a reframe. A malformed response isn't an error. It's a failed attempt.

Once you see it that way, it stops being an exception and becomes a row in the attempt table with a parse_failed report — which means it feeds the correction loop like any other failure. The next prompt tells the model its output was malformed, and it tries again. The bug that was killing runs became just another thing the loop already knew how to handle.

And the RBAC one: a per-run cache, keyed on principal-attribute-permission-tenant. N queries per attempt became roughly one query per distinct field for the whole run. But the design decision inside that fix is the one I'd defend hardest — I scoped the cache to the run, so it's built fresh and dies with the run. A long-lived shared cache would've been faster. It also would've meant a revoked permission could be served stale. A stale permission cache isn't a performance bug, it's a security bug. I took the slower cache."

The landing.
"What shipped was an AI agent runtime where the agent can be wrong — and being wrong is a normal, audited, recoverable event instead of a corrupted business record. Every attempt is a row. Every tool call is grant-checked and audited in and out. Every verdict is stored. And it plugs into the existing engine through a single branch — if the LO's primary agent is AI_AGENT, delegate; otherwise the old code runs completely untouched. All the new state lives in sibling tables. You can switch the whole thing off and the platform behaves exactly like it did before.

The thing I'd take to any system like this: putting an LLM into production isn't a modeling problem. It's a containment problem. The interesting engineering isn't making it right — it's what happens when it's wrong."

Why this works on that specific audience
An architect hears: false-hero rejected on principle, one delegation point, additive/reversible schema, a security-over-speed call made deliberately. A manager hears: risk to customer records identified before shipping, and the phrase "you can switch it off."

The dip is load-bearing. Most candidates narrate a clean arc and it plays as rehearsed. Yours dips into two unglamorous plumbing failures — and the recovery from the second one is a conceptual reframe ("malformed isn't an error, it's a failed attempt"), not a heroic all-nighter. That's the beat that makes senior people lean in, because it's the kind of insight they recognize from their own work.

The strongest single line, and it's true: "We built a correction loop to survive the model being wrong, and it was crashing on the most common way the model is wrong." Deliver that one slowly.

Delivery notes
Do not rush the false-hero beat. The "ask the model to check itself" detour is what makes the verifier lane feel earned rather than obvious. If you skip to the answer, you sound like you read it in a blog post.
Own the scope. Somewhere near the end: "Two months, large existing platform — the schema, the gateway integration, the loop, the prompt assembly and the perf work were my slices." Volunteering the boundary makes everything inside it more credible.
Bait the follow-up. End on "containment, not correctness." Every architect in the room now wants to ask about prompt injection — and you have that answer cold (Q29: RBAC contains it, nothing detects it, and you'll say so).
Want this appended to Brane_Interview_QA.md, or as its own file in the BRANE folder?


---------------------------------------------
# Brane — The Story (tell this out loud, ~3 minutes)

**Use when:** "Tell me about a project you're proud of." / "Walk me through your work at Brane." / any open-ended invitation at the top of an interview.

**Companion docs:** [Brane_Interview_QA.md](Brane_Interview_QA.md) (40 Q&A) · [Brane_AI_Agent_Runtime_Deep_Dive.md](Brane_AI_Agent_Runtime_Deep_Dive.md) (architecture)

---

## Before you use this — the honesty rule

A story an interviewer loves is one he can cross-examine. Every beat below is a real thing from the deep-dive. **Three slots need your actual memory** — marked `[FILL]`. Do not ship a fabricated detail in those slots. A great narrative with one invented fact is worse than no narrative, because the follow-up question finds it.

**The structural trick:** the villain is not a person and not a bug. **The villain is the LLM's confidence.** That works on managers and architects because it is the thing they are personally afraid of.

---

## THE STORY

### 1. Setup — the world before

> "Brane runs a no-code platform. Business users drag together workflows out of units called Local Objectives. Every LO was one of two types: a HUMAN does it, or DIGITAL automation does it.
>
> And both share one property the entire engine is built on — **when the step finishes, you trust the answer.** A fetch returns what it returns. A calculation is a calculation. The engine commits it and moves on. Twenty things downstream depend on that assumption."

*Beat: establish the deterministic world. The audience must feel the foundation before you crack it.*

---

### 2. The ask — sounds trivial

> "The company wanted a third type: **AI_AGENT**. An LLM does the work — extract the invoice fields, classify the ticket, summarize the case.
>
> On the surface that's a Tuesday. It's an API call. Everyone's first instinct — including some of ours — was: add a node, call the model, write the output."

---

### 3. The villain, named

> "Here's what that misses, and it's the whole project.
>
> **An LLM is wrong with exactly the same confidence it is right.** It hallucinates a vendor name in perfect JSON. It invents a line item that looks flawless. And we were about to feed that into an engine whose single foundational assumption is *the output of a step is trustworthy the moment it exists.*
>
> We weren't adding a feature. We were putting a probabilistic component into a deterministic machine and pointing it at customers' real business records.
>
> The villain isn't the model being wrong. Wrong is fine — **wrong is detectable.** The villain is *wrong and confident*, because confident is what slips past you and gets committed."

*Beat: this is the hook. Slow down. Let "wrong with the same confidence it is right" land on its own.*

---

### 4. The false hero — the beat every architect grins at

> "The obvious fix is: ask the model to check itself. Add to the prompt — 'produce the output, and tell me if it's correct.' And it *works*. In a demo it works beautifully. The model produces its JSON, and a field that says `confident: true`.
>
> Which is worthless. Because **a confidently-wrong answer certifies itself.** You didn't build a check. You built a rubber stamp and handed it to the thing that needed checking.
>
> That was the moment the actual principle fell out: **the thing that generates must never be the thing that certifies.**"

*Beat: DO NOT SKIP THIS. The detour is what makes the real design feel earned instead of recited. Skip it and you sound like you read it in a blog post.*

---

### 5. The design — hero enters

> "So the architecture became one sentence: **probabilistic core, deterministic gate.**
>
> The agent generates — that's the probabilistic core, and we *let* it be probabilistic. But it commits nothing. The output goes to a **separate verifier lane**:
>
> First, deterministic business rules — real code, the platform's existing rule engine. Cheapest and most certain, and it short-circuits on the first failure. Only if that passes does an **AI verifier** run — a *different model class*, a separate call. And only then, optionally, a **human**.
>
> Pass, and the workflow's real primary function fires and the LO completes. Fail — and here's the part I like — **the failure report is fed back into the next prompt**, and the agent tries again. It sees *why* it was rejected.
>
> That's a **correction** loop, not a retry loop. Blind retry just re-samples the same failure."

---

### 6. THE DIP — where the story earns its attention

> "And then we ran it, and it fell over. Not on the AI. **On the plumbing.**
>
> Two things, both mine to fix.
>
> **First: it was slow, for a stupid reason.** Attribute-level RBAC — the agent only sees the fields it's been granted, because an invoice extractor must never see a salary field. But the naive check is a database round-trip *per attribute, per attempt*. And it's a loop. So the same fields get re-checked on every single iteration. The permission system that existed to make the agent **safe** was the thing making it **unusable**.
> `[FILL: what the latency actually looked like — e.g. "an attempt was spending more time asking permission than thinking"]`
>
> **Second, and worse: the loop kept dying on garbage.** LLMs return broken JSON a meaningful fraction of the time — wrapped in markdown fences, trailing prose after the closing brace, a missing field. And a parse exception was killing the **entire run**.
>
> Think about how backwards that is. We built an elaborate, careful correction loop whose *entire purpose* is to survive the model being wrong — and it was crashing on the single most common way the model is wrong."
> `[FILL: the specific malformation that actually bit you — code fences? trailing text?]`

*Beat: the italicized line above is the strongest sentence in the story. Deliver it slowly. This is where senior people lean in.*

---

### 7. The turn — reframe, not heroics

> "The fix for the second one wasn't a better parser. It was a **reframe**.
>
> **A malformed response isn't an error. It's a failed attempt.**
>
> Once you see it that way, it stops being an exception and becomes a row in the attempt table with a `parse_failed` report — which means it feeds the correction loop like every other failure. The next prompt tells the model its output was malformed, and it tries again. The bug that was killing runs became just another thing the loop already knew how to handle.
>
> And the RBAC one: a per-run cache, keyed on principal–attribute–permission–tenant. N queries per attempt became roughly one query per distinct field for the whole run.
>
> But the decision *inside* that fix is the one I'd defend hardest. I scoped the cache to the **run** — built fresh, dies with the run. A long-lived shared cache would have been faster. It also would have meant a revoked permission could be served stale. **A stale permission cache isn't a performance bug, it's a security bug.** I took the slower cache."

*Beat: the recovery is conceptual, not an all-nighter. That's deliberate — it reads as insight, not stamina.*

---

### 8. The landing

> "What shipped is an AI agent runtime where **the agent is allowed to be wrong** — and being wrong is a normal, audited, recoverable event instead of a corrupted business record.
>
> Every attempt is a row. Every tool call is grant-checked and audited in and out. Every verdict is stored. And it plugs into the existing engine through a **single branch** — if the LO's primary agent is AI_AGENT, delegate; otherwise the old code runs completely untouched. All new state lives in sibling tables. **You can switch the whole thing off and the platform behaves exactly as it did before.**
>
> And the thing I'd carry into any system like this: putting an LLM in production isn't a modeling problem. It's a **containment** problem. The interesting engineering isn't making it right — it's what happens when it's wrong."

---

## Why this lands on this specific audience

**An architect hears:** a false hero rejected *on principle*; one delegation point; additive, reversible schema; and a security-over-speed call made deliberately and defensibly.

**A manager hears:** risk to customer records caught *before* shipping — and the sentence "you can switch it off."

**The dip is load-bearing.** Most candidates narrate a clean arc and it plays as rehearsed. Yours dips into two unglamorous plumbing failures, and the recovery from the second is a *conceptual reframe*, not heroism. That's the beat senior people recognize from their own work.

---

## Delivery notes

| Beat | Note |
|---|---|
| The villain (§3) | Slow down on *"wrong with exactly the same confidence it is right."* Let it sit. |
| False hero (§4) | Never skip. It's what makes the verifier lane feel earned. |
| The dip (§6) | *"A correction loop… crashing on the most common way the model is wrong."* Deliver slowly. Strongest line you have. |
| Scope honesty | Somewhere near the end: **"Two months, large existing platform — the schema, the gateway integration, the loop, the prompt assembly and the perf work were my slices."** Volunteering the boundary makes everything inside it more credible. |
| The bait | End on **"containment, not correctness."** Every architect in the room now wants to ask about prompt injection — and you have that cold (Q29: RBAC *contains* it, nothing *detects* it, and you say so). |

## The three lines to memorize

1. *"An LLM is wrong with exactly the same confidence it is right."*
2. *"The thing that generates must never be the thing that certifies."*
3. *"A malformed response isn't an error — it's a failed attempt."*

Everything else you can improvise from the deep-dive.
