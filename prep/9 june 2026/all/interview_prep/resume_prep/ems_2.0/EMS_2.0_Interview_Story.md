# EMS 2.0 — The 3-Minute Spoken Story

Every fact below is traceable to `EMS_2.0_PROJECT_REPORT.md`. Anything the report doesn't support is marked `[FILL]`. **Do not smooth over a [FILL] with a plausible-sounding number — that is the one thing that can lose you the room.**

---

## THE STORY

### 1. Setup — the world before

> Every employee management system I'd used worked the same way. To add one person, you fill in twenty-plus fields by hand. And to find someone, you have to already know the filter — you can't just ask "who's our most experienced Python developer?" You have to know it's a dropdown, and know which dropdown.
>
> So the resume — a document that already contains every one of those fields — gets read by a human, who retypes it into boxes. The information is already structured. We just don't have anything that can read it.

### 2. The real problem — the stakes, not the speed

> The obvious framing is "it's slow." That's the boring version, and I don't think it's the real one.
>
> Here's the real one. **When a task is tedious, humans do it badly.** Twenty-plus fields, by hand, from a PDF, forty times in a day — you skip the optional ones. You truncate the skills list at the ones you recognize. You don't type in the fourth job. And nobody ever knows, because a half-filled record looks exactly like a full one.
>
> So the cost isn't minutes. The cost is that the candidate who *did* have the skill you're now searching for is in your database with that skill missing. He applied. He's in there. He's unfindable.

### 3. The obvious build — and why it's a trap

> The obvious build is: bolt an LLM onto the form. Parse the PDF, prefill the boxes, done. Ship it in a weekend.
>
> The trap is what that architecture assumes. It assumes the model is *right*. You've moved the typing from a human to a model, and you've kept every one of the human's failure modes while removing the only thing that made them survivable — which is that a human who isn't sure *hesitates*. A model never hesitates. It fills the field. It fills it with total confidence, at temperature zero, in about two seconds.
>
> I found out how confident it is: **roughly ten to twenty percent of the raw JSON coming back from the model didn't even parse.** That's the failures I could *see*. It's the ones underneath that number that I started worrying about.

### 4. The villain

> And that's the thing I ended up building the whole system against. Not a crash. Not a bug.
>
> **The villain is the qualified candidate who silently disappears.**
>
> Think about what that failure actually looks like from inside the system. There's no exception. No stack trace. No alert. Nothing turns red. My pipeline runs, reports `"status": "done"`, and returns a clean two-hundred. It thinks it succeeded — and by its own logic, it *did*. A person applied for a job, hit a threshold in a scoring function, and evaporated. They just never get a callback, and nobody — not them, not me, not the hiring manager — ever finds out.
>
> A crash is a gift. A crash is loud, it has a stack trace, and someone fixes it by Friday. A silent rejection is the one that scares me, because **the system reports success.**

### 5. The hero — the design insight

> So the insight the whole architecture turns on is this: **you cannot make the model reliable. You can only make it unable to fail quietly.**
>
> That's why there are seven validation layers before anything touches the database, and why the load-bearing one isn't clever — it's Pydantic. A hard schema gate. The model can hallucinate whatever it likes; it does not get to write to my employee table unless the shape is right. And when the extracted name is missing, we don't shrug and insert a nameless employee — we retry, because a nameless employee record is worthless.
>
> The same principle shows up in identity. If you ask about "John" and there are two Johns, the system **stops and asks you for the employee ID.** It refuses to guess. That's the rule the whole thing is built on: *where the system is unsure, it asks — it doesn't decide.*

### 6. The dip

> And then the validator itself turned out to be the villain.
>
> Before any resume reaches the model, it gets scored out of a hundred — section headers, professional keywords, contact info, dates. Below forty, it's rejected. That guard saves real money: a local model on my hardware is five to thirty seconds an inference, and I don't want to spend that on a random PDF.
>
> Twenty-five of those hundred points are contact information — an email pattern and a phone pattern. And I'd written those two regexes with `^...$` anchors on them.
>
> Anchors match the *whole string*. An email address inside a resume is never the whole string. **So the contact block never matched. Not once. On any real resume.** I was silently deleting twenty-five points from every genuine candidate who walked through the door, and quietly shoving them toward my own rejection threshold.
>
> And it threw no error. Ever. It scored them, and it dropped them, and it said `done`.

### 7. The turn — the realization

> The fix took one line — drop the anchors, use `re.search` instead of `re.match`. That's not the point.
>
> The point is *how I found it*, which is that **I got lucky.** Nothing told me. There was no alert, no failing test, no angry user — because the users who would have been angry were the resumes that never made it into the system to complain.
>
> And that reframed the entire project for me. I'd spent all this effort building guards against the model hallucinating — and the thing that was actually dropping qualified people was a regex *I* wrote, in a layer I trusted so much I never looked at it. **My defenses were pointed at the model. The failure came from me.**
>
> Which means the real gap wasn't a missing guard. It was that I had **seven layers of validation and zero measurements**. I'd hardened the system against every failure I could imagine, and I was completely blind to the ones I couldn't. That's exactly backwards, and it's the thing I'd change first if I started over: an evaluation harness before a feature. Because right now, if I tweak the extraction prompt, I genuinely cannot tell you whether I made the system better or worse.

### 8. The landing

> What shipped: a chat interface where the forms are gone. Drop in a PDF or a photo of a resume, and a local model — `qwen2.5:7b-instruct`, running on Ollama, on my own machine — pulls out twenty-plus structured fields. And it stays on my machine: **no resume text ever leaves the box.** No third-party API, no vendor holding a stranger's career history. That was deliberate.
>
> After that, everything is plain English. "Show me who knows Python." "Update John's email." Semantic search over the resumes, so "experienced DevOps engineer" finds the right people even when nobody wrote that phrase.
>
> [FILL: your headline number — the "15 minutes to 30 seconds" from your resume bullet. The project report does not contain either figure. Before you say it out loud, know exactly which part you measured and which part you estimated, and be ready to say which is which the instant you're asked. What the report *does* let you claim, hard: after moving off a 14B model that didn't fit in 6GB of VRAM, you went from 30-plus second CPU-bound responses to 2-5 seconds on GPU.]
>
> And the principle I took out of it — the one I'd bring to your team:
>
> **The most dangerous failure in an AI system is the one that doesn't raise an exception. So the first thing I want to know about any model I ship is not how often it's right. It's what it looks like when it's wrong and doesn't say so.**

---

## Why this works on this audience

| Move | Why it lands with an engineer / hiring manager |
|---|---|
| Reframing "slow" as "tedium produces silently incomplete records" | Anyone who has run a hiring pipeline has *felt* this. You're describing their problem better than they would. |
| Naming the trap in the obvious build | Proves you can see two moves ahead. Most candidates describe what they built; almost none describe the version they *rejected*. |
| The villain is invisible failure, not a bug | This is the thing that keeps architects awake. A bug is a ticket. An undetectable wrong answer is a liability, and in a hiring context it's a legal one. |
| The dip is a regex — not a heroic distributed-systems saga | Small, concrete, humiliating, and *true*. Grandiose war stories read as invented. `^...$` reads as lived. |
| The turn is "I got lucky," not "I heroically debugged it" | The single highest-status move available. Only senior engineers admit that detection was the gap, not skill. |
| "Seven layers of validation and zero measurements" | It's self-critical, it's structural, and it's the exact instinct a team wants in someone shipping LLM features. |
| Privacy stated as an architecture choice, not a policy claim | "The model runs locally, no data leaves the machine" is a *verifiable* claim. It's the strongest privacy sentence you can say and it's fully backed by the source. |
| The closing principle calls straight back to the villain | The story closes its own loop, which is what makes it *repeatable* by the interviewer to their team. |

---

## Delivery notes

| Beat | Time | Pace / tone | Do NOT |
|---|---|---|---|
| Setup | ~20s | Even, slightly wry. This is the setup, not the show. | Don't rush it — the "information is already structured" line needs to land. |
| Real problem | ~25s | Slow down. **"He applied. He's in there. He's unfindable."** — three short sentences, hard stops between them. | Don't say "it was slow." Ever. |
| The trap | ~20s | Pick up pace. Slight edge. | Don't strawman it — the obvious build is genuinely reasonable, which is *why* it's a trap. |
| **THE VILLAIN** | ~30s | **Slowest beat in the story.** Drop your volume, don't raise it. Full stop after *"the system reports success."* Let it sit for two seconds. | Don't gesture. Don't smile. Don't rush into the next beat to fill the silence. |
| The hero | ~25s | Recover energy. Crisp, confident, technical. | Don't oversell the seven layers — you're about to admit one of them was broken. |
| **THE DIP** | ~30s | Fast, embarrassed, concrete. Lean in. **"Not once. On any real resume."** | Don't soften it. Don't add "but of course I caught it quickly." |
| The turn | ~25s | Quiet. Reflective. This is the beat where they decide you're senior. | Don't turn "I got lucky" into a humblebrag. Say it flat and move on. |
| The landing | ~25s | Warm, then hard stop on the principle. | Don't trail off. The last sentence is the last sentence. Stop talking. |

**Total: ~3:00.** If you're running long, cut the second half of the Setup — never the villain, never the dip.

**The two silences that do the work:** after *"the system reports success"* and after *"Not once. On any real resume."* Both are counted, not accidental. Two full seconds. Resist filling them.

---

## Lines to memorize (word-for-word)

1. **"When a task is tedious, humans do it badly."**
2. **"He applied. He's in there. He's unfindable."**
3. **"A model never hesitates. It fills the field."**
4. **"The villain is the qualified candidate who silently disappears."**
5. **"A crash is a gift. A silent rejection is the one that scares me — because the system reports success."**
6. **"You cannot make the model reliable. You can only make it unable to fail quietly."**
7. **"Where the system is unsure, it asks. It doesn't decide."**
8. **"So the contact block never matched. Not once. On any real resume."**
9. **"My defenses were pointed at the model. The failure came from me."**
10. **"Seven layers of validation and zero measurements."**
11. **"The most dangerous failure in an AI system is the one that doesn't raise an exception."**

---

## [FILL] list

| # | Beat | What you must supply |
|---|---|---|
| 1 | **Landing** | **Your headline metric.** The "15 minutes to 30 seconds" on your resume appears **nowhere** in the project report. Decide before you walk in: what was measured, on what hardware, against what baseline. If it's an estimate, *say* it's an estimate — an interviewer will forgive an honest estimate and will never forgive a number you can't source. **Fallback that is 100% defensible: "14B model didn't fit in 6GB of VRAM, fell back to CPU, 30+ second responses. Switched to a quantized 7B, hit ~100% GPU utilization, 2-5 second responses."** |
| 2 | **Dip** | The report confirms BUG-002 (the `^...$` anchor bug) as a real bug you fixed. It does **not** say a specific candidate was actually dropped because of it. Keep the story as written — *"I was shoving them toward my rejection threshold"* — which is true and provable. **Do not upgrade it to "a real candidate got rejected and we found out later"** unless [FILL: confirm that actually happened to you]. |
| 3 | **Setup / Problem** | The "forty times a day", "half-filled record" framing is a *reasonable inference* from the report's "20+ fields manually" — but it's your framing, not a documented incident. Deliver it as reasoning about the problem, not as a war story. If asked *"did you see that happen?"*, the answer is **"that's my read of why the manual path is dangerous, not something I measured."** |

---

## If they interrupt the story (they will)

| They cut in with | Pivot line |
|---|---|
| "Did you use a cloud LLM?" | **"No — Ollama, locally. `qwen2.5:7b-instruct`. No resume text ever leaves the machine. That was the point."** → back to the story. |
| "Did you check it for bias?" | **Stop the story. Take the question.** "No — and that's the sharpest thing you could ask me about this system." → full answer in the Q&A doc, §6. Do not try to get back to the story until that's fully answered. |
| "How accurate is it?" | **"10-20% of raw model JSON failed to parse — that I measured. Field-level accuracy I never measured, because I never built the eval. Which is exactly where this story is going."** → resume at the turn. |
| "Is it in production?" | **"No — it's a learning project, and I'd argue it shouldn't be in production: no auth, no fairness evaluation. I can tell you exactly what I'd need to fix first."** |
