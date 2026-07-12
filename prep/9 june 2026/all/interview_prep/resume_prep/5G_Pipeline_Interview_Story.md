# 5G Failure Pipeline — The Story (tell out loud, ~3 minutes)

**Use when:** "Tell me about a project you're proud of." / "Walk me through the 5G work." / any open-ended invitation.

**Companion docs:** [5G_Pipeline_Interview_QA.md](5G_Pipeline_Interview_QA.md) (47 Q&A) · [5G_Failure_Detection_Pipeline_Deep_Dive.md](5G_Failure_Detection_Pipeline_Deep_Dive.md) (architecture + code)

---

## The honesty rule

Every beat below is real — it's in your code and your design decisions. **Two slots need your actual memory**, marked `[FILL]`. Do not invent them. A story with one fabricated detail is worse than no story, because the follow-up question finds it.

**The structural trick:** the villain is not the model being wrong. **The villain is the answer that is completely right — about the wrong network.** That terrifies architects, because it's the failure that passes every check you thought to write.

---

## THE STORY

### 1. Setup — the world before

> "In 5G operations, when something breaks, the evidence is in a pcap — a packet capture. Every message the network exchanged, in binary.
>
> The process was: an engineer opens it in Wireshark. Scrolls through thousands of packets. Finds the error. Then matches it, *from memory*, against every failure pattern he's seen in his career. Then decides on a fix.
>
> That's hours per incident. But the hours weren't the real problem."

*Beat: pause here. You're about to reframe the problem, and the pause makes them lean in.*

---

### 2. The real problem — not what they expect

> "The real problem was **who was on shift.**
>
> A senior engineer looks at a NAS cause code 24 and instantly knows: authentication timeout, T3560, the UE didn't respond in time, and here's the three things to check. A junior engineer sees a hex value in a packet.
>
> Same failure. Same pcap. Two completely different outcomes, depending entirely on who happened to be on call at 3 AM.
>
> And that knowledge — ten years of pattern-matching — lived in about four people's heads. It went home with them at night. It went on holiday with them. **Eventually it was going to leave the company with them.**"

*Beat: a manager just heard "key-person risk." That's his problem, not yours, and you named it. He is now fully engaged.*

---

### 3. The obvious build — and why it's a trap

> "So: extract the errors from the pcap automatically, and match them against a knowledge base of known failures. Standard RAG. Embed the error, vector search, feed the matches to an LLM, get a fix.
>
> And it works. It demos beautifully. You upload a pcap and out comes a confident, well-written, step-by-step remediation.
>
> **And it will get someone fired.**"

*Beat: stop. Let that sit. This is your hook.*

---

### 4. The villain, named

> "Here's what a pure semantic search does. An engineer uploads a **Nokia** authentication timeout. The vector search finds the closest match in the knowledge base — and the closest match, semantically, is an **Ericsson** authentication timeout. Because they *are* nearly identical. Same protocol, same failure, same words. The embedding is doing its job perfectly.
>
> So the system returns an Ericsson fix. And an Ericsson fix means Ericsson OSS CLI, Ericsson parameter names, Ericsson restart procedures. On a Nokia node, that fix is either unrunnable — or worse, it *runs*, and it runs the wrong command against a live core network.
>
> **That's the villain.** Not a model that hallucinates. Not a model that's confused. A model that is *completely, verifiably, semantically correct* — and catastrophically wrong for the network you're standing in front of.
>
> A wrong answer, you can catch. **An answer that's right about the error and wrong about the world — that one gets executed.**"

*Beat: this is the single strongest paragraph you have. Deliver it slowly. Architects have been burned by exactly this class of bug and they will never forget that you named it.*

---

### 5. The hero — the insight

> "So the design principle became: **semantic similarity is not enough, and it never was.**
>
> The fix is that vendor and protocol layer aren't things you *rank* by. They're things you **filter** by — hard, exact, before ranking ever happens.
>
> And that's actually the reason the whole system runs on Qdrant instead of FAISS. FAISS is a similarity index — it has no metadata filtering, so you'd search the whole corpus and filter to Nokia in Python *afterward*. Which means the Ericsson patterns were still in the ranking. You just hid them at the end.
>
> Qdrant filters **at the database level, before the similarity computation runs.** Only Nokia NAS vectors are ever *considered*. It's not that the system is careful not to return a cross-vendor fix — it's that the system is **structurally incapable** of returning one.
>
> That's the difference between a guardrail and a design. A guardrail is something you can forget to add. A design is something you can't get wrong."

*Beat: "structurally incapable" and "the difference between a guardrail and a design" — those are the two phrases an architect will repeat back to his colleagues.*

---

### 6. THE DIP — and it's beautiful, because the bug hides as its own opposite

> "So we build it. It runs. And then the operations team starts telling me the knowledge base has gaps.
>
> Errors are coming back flagged **'no known pattern — manual review required.'** Not a few. Enough to notice. And the system is behaving *exactly as designed* — I built it to refuse to answer when it doesn't have a confident match, because a confident wrong fix on a live core is worse than no fix. So it refuses, it flags, it escalates to a human. Working as intended.
>
> So I do the obvious thing. I start **writing more patterns.** More error types, more coverage, filling what looks like a hole in the knowledge base.
>
> `[FILL: how long you spent doing this — a few days? a week? Name it. The wasted effort is what makes the reveal land.]`
>
> And it doesn't help."

*Beat: this is where you have them. Everyone in the room has done this — fixed the wrong thing, confidently, for days.*

---

### 7. The reveal

> "The knowledge base was fine.
>
> The vendor detector was failing. And when it fails, it returns the string `unknown`. And that string goes straight into the Qdrant query as a hard filter: `vendor = unknown`.
>
> **There is no pattern in the knowledge base with vendor `unknown`.** So the filter matches zero rows. Zero results come back. And the pipeline says — completely honestly, by its own logic — *'I have no known pattern for this error.'*
>
> But that's not what happened. What happened is: **I couldn't identify the vendor, so I searched an empty subspace.**
>
> Those are two completely different problems. One means *write more patterns*. The other means *fix the detector*. And my system reported them **identically.**"

*Beat: land on that last sentence. Then stop talking for a second.*

---

### 8. The lesson — this is what they'll remember

> "That's the bug I think about most, and it's not really a 5G bug. It's this:
>
> **An unresolved classification silently became a query constraint.**
>
> The detector didn't crash. It didn't throw. It returned a *plausible-looking string* — `unknown` — and that string was quietly load-bearing. It flowed into a filter and poisoned it. And the failure it produced was *indistinguishable from a legitimate result*.
>
> The scariest bugs aren't the ones that break loudly. They're the ones that **produce a correct-looking answer to a question you didn't realize you'd stopped asking.**"

*Beat: this is the line that gets you the job. It is a genuinely senior observation and it is true.*

---

### 9. The fix — two tiers, and the one you refused

> "Two changes.
>
> **Fail loudly.** If the vendor is unresolved, don't run the query at all. Return a distinct status — `vendor_unresolved` — that is *not* the same as `no_pattern_found`. Never silently search a subspace you already know is empty.
>
> **And fix the root cause:** vendor is a property of the **capture**, not the packet. You know which node you captured from. It should come from the upload metadata, not from string-matching the inside of a packet and hoping.
>
> And there's a third option I deliberately **rejected**. I could have made it degrade gracefully — if the vendor is unknown, just drop the vendor filter and search on layer alone. Return *something*.
>
> That is the worst possible fix. **Silently widening a safety filter is exactly how a Nokia engineer ends up holding an Ericsson fix** — which is the precise failure the entire system exists to prevent. It would have taken the villain from the beginning of this story and let him in through the back door, in the name of being helpful."

*Beat: rejecting a tempting fix on principle is the most senior thing in the story. Do not rush it.*

---

### 10. The landing

> "What shipped: an engineer uploads a pcap, and in seconds gets a diagnosis, a step-by-step fix specific to their vendor and their layer, a confidence level, **and the matched patterns with their similarity scores** — so he can see *why* the system said what it said. It's advisory. A human still executes. There is no path from model output to a live command.
>
> 70% auto-resolution of routine errors. 55% MTTR reduction. Hours to seconds.
>
> But the number I'd actually defend is a different one: **the system's most important capability is refusing to answer.** Below a similarity threshold, it produces nothing and says 'manual review.' That refusal is not a limitation I apologize for — it's the feature that makes the other 70% trustworthy.
>
> Because the thing I took away from this project is that in operations, the dangerous output was never the obviously-wrong one. **It was the one that was right about the error and wrong about the world.**"

*Beat: closing on the villain, transformed into a principle. This is the callback that makes the story feel authored rather than recounted.*

---

## Why this works on this specific audience

**A manager hears, in order:** key-person risk (four people's heads, walking out of the door) → a change that could get an engineer fired → a week of effort spent fixing the wrong thing, admitted freely → a hard number.

**An architect hears:** "structurally incapable, not merely careful" → a bug caused by a plausible-looking sentinel value poisoning a downstream constraint → and a tempting fix **rejected on principle** because it would silently widen a safety boundary. That last one is the rarest thing a candidate demonstrates.

**The dip is doing real work.** Most candidates' struggle-beat is "it was hard and I worked late." Yours is *"I confidently fixed the wrong thing for a week, because the bug was disguised as its own opposite."* Every senior engineer in that room has lived that, and none of them expected you to admit it.

---

## Delivery notes

| Beat | Note |
|---|---|
| §2, the real problem | Don't say "it was slow." Say **"it depended on who was on shift."** Reframing hours-of-toil into key-person risk is what promotes this from a tooling story to a business story. |
| §3, "it will get someone fired" | Say it flatly, then stop. The silence does the work. |
| §4, the villain | Slowest delivery in the story. *"Right about the error and wrong about the world."* |
| §5, hero | The two phrases to land: **"structurally incapable"** and **"a guardrail is something you can forget to add; a design is something you can't get wrong."** |
| §6, the dip | Own the wasted week without flinching. Hedging here destroys the payoff. |
| §8, the lesson | **"An unresolved classification silently became a query constraint."** If they remember one sentence from your entire interview, make it this one. |
| §9, the rejected fix | The senior beat. Don't rush past it to get to the results. |
| Scope honesty | If the vendor bug story isn't literally yours, **don't tell it as yours.** Tell it as "the failure mode the design has to defend against" — it's still a strong answer and it's true. |

## The bait you're setting

You end on *"refusing to answer is the feature."* Every architect in the room now wants to ask **"so how do you know when it's wrong? how did you evaluate fix quality?"**

And the honest answer is: **you didn't** — there was no automated fix-quality evaluation in this project (Q37).

That's not a weakness. That's your bridge:
> "That's the gap in this project, and it bothered me enough that I went and built the tool — an LLM evaluation framework with claim-level hallucination detection, and a prompt regression suite that catches breaking changes in CI before they ship."

**You just walked yourself into your two strongest side projects, and it looks like modesty instead of a pivot.** Set this up on purpose.

---

## The four lines to memorize

1. *"It didn't depend on the pcap. It depended on who was on shift."*
2. *"A wrong answer you can catch. An answer that's right about the error and wrong about the world — that one gets executed."*
3. *"An unresolved classification silently became a query constraint."*
4. *"The system's most important capability is refusing to answer."*

Everything else you can improvise from the deep-dive.
