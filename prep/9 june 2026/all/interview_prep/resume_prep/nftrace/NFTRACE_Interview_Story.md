# NFTRACE — The 3-Minute Story
### Spoken. Not read. This is the answer to "tell me about a project you're proud of."

---

## THE STORY

**(1) Setup — the world before.**

> Nokia, 5G core test automation. To prove a network function behaves correctly you have to look at the actual packets moving between the nodes — the gNB, the AMF, the UPF, the AUSF. And the way we did that was: a test engineer SSHes to each node, starts a packet capture by hand. Runs the scenario. Goes back and stops each capture by hand. Pulls the trace files off each node, one machine at a time. Runs the dissection scripts locally. And then reads SIP and Diameter signalling with their eyes.
>
> Hours. Per scenario. And it's a human doing the same seven steps every time, which means it's not repeatable, and it means nobody does it unless they already suspect something is wrong.

**(2) The real problem — the stakes.**

> Now here's what that actually costs, and it isn't time.
>
> Because trace validation was expensive and manual, it was **optional**. So the pipeline would run, the tests would go green, and the packets underneath — the thing that says whether the network *actually* behaved — nobody looked at. A test could pass its assertions with a Diameter timing violation sitting right there in the signalling. Registration succeeds, so the assertion says PASS, and the defect ships.
>
> That's the real problem. Not "validation is slow." It's that we had a test suite that was answering a question nobody had asked, and staying quiet about the question that mattered.

**(3) The obvious build — and why it's a trap.**

> The obvious build is a script. Loop over the nodes, start the captures, run the test, stop, pull the files, merge, done. One afternoon.
>
> And it works. Once. It works beautifully for one engineer running one scenario on their own testbed.
>
> The trap is that CI/CD doesn't run one test. It runs twenty, in parallel, on a *shared pool of physical nodes*. And every one of those workers wants to start a capture on the same gNB. Now Worker 2's script starts a capture on a node that Worker 1 is already capturing on. Worker 2 finishes first and stops it. And Worker 1 — still running — is now capturing nothing, and it doesn't know.

**(4) THE VILLAIN.**

> That's the villain, and I want to name it precisely, because it isn't "a race condition."
>
> The villain is **a corruption that is invisible in every single test run, and only exists when two runs overlap.** Worker 1 doesn't crash. It doesn't error. It gets back a trace file — a shorter one, missing the packets that would have failed the rule. It merges cleanly. `mergecap` is perfectly happy. Pyshark parses it. The validation rule runs over the packets that *are* there, finds nothing wrong, and reports **PASS**.
>
> A green check mark on missing data. Not a red failure — a *green* one.
>
> And that is the thing that kills a test suite, because it's self-reinforcing. Traces start disagreeing with reality. Engineers see a failure they can't reproduce, shrug, re-run it, it goes green, they move on. Do that four times and the tool has taught the entire team that its output is noise. And once people are ignoring the failures, the *real* failure gets ignored too — and it gets ignored by exactly the tool you built to catch it.
>
> That's what an architect is actually afraid of in test infrastructure. Not that it breaks. That it lies, and stays plausible.

**(5) The hero — the design insight.**

> So the insight isn't "make it faster." It's: **the session has to be a first-class thing, and it has to be the only handle anyone has on a trace.**
>
> Not "start a capture on gNB-001" — nobody gets to say that. Instead: `POST /sessions/start`, and you get back a UUID. Every operation after that — stop, merge, validate — takes that session ID and nothing else. A worker cannot express "stop the capture on that node," because that sentence no longer exists in the API. It can only say "stop *my session*."
>
> That's what Redis is doing in this system, and it's why people misread the resume bullet. It isn't a cache. Nothing is being cached. It's a live registry of who owns what, keyed by session — with a TTL, so that a worker that crashes doesn't leave its session sitting there forever.
>
> FastAPI on the front — four endpoints, start, stop, merge, validate. Redis holding live session state. SQLite for history. And XML-RPC out the back, because that's the only protocol the network nodes speak — that's a constraint, not a choice, and the design decision was confining it to one class so the test engineer never has to know it exists.

**(6) THE DIP.**

> `[FILL: confirm this actually happened to you — the source documents this as a design weakness, not as an incident. If it did happen, tell it as below. If it did NOT, cut this paragraph and use the alternative dip at the bottom of this file, which is honest and just as strong.]`
>
> And then a session vanished.
>
> A worker called `/sessions/stop` and got back a 404. Session not found. But the session was *right there* — five nodes were still capturing, disks filling up, and the API had no idea they existed. I couldn't stop them, because the only thing that could stop a capture was the session ID, and the session ID was gone.
>
> The Redis key had expired. One hour TTL. The test had simply taken longer than that.

**(7) The turn — the realization.**

> My first instinct was: raise the TTL. Two hours. Four. Obviously wrong — I'd just be moving the cliff.
>
> The real realization was this. I had written the session to SQLite — the durable store — at **merge time**. Because merge is when I finally *had something*: a file, a result, something worth keeping. That felt right.
>
> It was exactly backwards. The moment worth recording wasn't when I had a result. It was the moment I started **five physical machines doing something that somebody has to turn off.** That moment is `start`. From `start` onward there is a real, expensive, leaking resource in the world, and I was holding the only receipt for it in a cache with an expiry date.
>
> My orphan cleanup was deleting the one piece of information required to clean up the actual orphan.

**(8) The landing.**

> So the state layer changed. Durable write at start, not at merge. Redis demoted to what it should always have been — a cache, where a miss is recoverable, not an amnesia event. Session state moved off a single JSON string so two writers can't clobber each other's fields.
>
> What shipped: four REST endpoints, parallel start and stop across all nodes so you don't miss the opening messages, automatic merge, and SIP and Diameter validation — wired into Nokia Continuous Delivery, so any test tagged for tracing captures and validates itself with no human in the loop. The number on my resume is a 50% cut in pipeline validation time.
>
> But the number I actually care about is different. The NCD hook has one line in it that fails a pipeline job when the test **passed** and the trace validation **failed** — when the assertions were green and the signalling underneath was wrong. That case was invisible before. Nobody was looking.
>
> And the principle I took out of it is the one the villain taught me: **in test infrastructure, the failure you have to design against isn't the crash. It's the pass.** A tool that goes down gets fixed by lunchtime. A tool that quietly says everything is fine gets believed — right up until the day it matters.

---

## WHY THIS WORKS ON THIS AUDIENCE

- **It refuses the obvious framing.** They expect "it was slow, I made it fast." They get "it was optional, so it was skipped, so we were flying blind." That's a *stakes* answer, and stakes are what senior people listen for.
- **The villain is a distributed-systems villain.** Concurrent shared-state corruption that's invisible to every single-threaded test — that's the thing a systems interviewer has personally been burned by. You're not describing a bug; you're describing their Tuesday.
- **The dip is a design error, not bad luck.** "The TTL expired" is bad luck. "I wrote durable state at the wrong moment in the lifecycle" is a lesson. Interviewers can't reward bad luck.
- **You concede before they attack.** Every weakness in this system (see the Q&A) is one you've already named. That converts the whole interview from prosecution to conversation.
- **It lands on a principle, not a metric.** "Design against the pass, not the crash" is portable, quotable, and it's the thing they'll repeat in the debrief.

---

## DELIVERY NOTES

| Beat | Time | How to deliver it |
|---|---|---|
| 1. Setup | 0:00–0:25 | Flat, factual, slightly weary. You're describing tedium — let it sound tedious. Count the manual steps on your fingers if you're in person. |
| 2. Stakes | 0:25–0:45 | **Slow down.** This is the pivot. Land hard on "so it was optional." Pause after "the defect ships." |
| 3. Obvious build | 0:45–1:05 | Brisk, generous — genuinely concede the script works. Then: "It works. Once." **Beat.** |
| 4. VILLAIN | 1:05–1:45 | The centrepiece. Slowest delivery in the whole story. Land every word of "a green check mark on missing data." Then a real pause before "not a red failure — a *green* one." Do not rush the trust-erosion chain; it's the argument. |
| 5. Hero | 1:45–2:15 | Energy lifts. Crisp, technical, confident. Fastest section — this is the part you obviously know cold. |
| 6. DIP | 2:15–2:35 | Drop the volume. Present tense. "And then a session vanished." Short sentences. Don't dramatise — the facts are dramatic. |
| 7. Turn | 2:35–2:55 | Quiet and reflective. "It was exactly backwards" is the line. Pause before it. |
| 8. Landing | 2:55–3:20 | Steady, plain, unhurried. Deliver the 50% *without emphasis* — you're deliberately walking past it. Then land the principle and **stop talking.** |

**The single most common failure of this story is not stopping.** Say the last line, close your mouth, and let them ask the next question. The silence is doing work.

**If they interrupt during the villain — let them.** An interruption there means they've recognised the bug from their own life. That's the interview going well. Follow them.

---

## LINES TO MEMORIZE (verbatim — everything else can flex)

1. "Because trace validation was expensive and manual, it was **optional**."
2. "It works. Once."
3. "The villain is a corruption that is invisible in every single test run, and only exists when two runs overlap."
4. "A green check mark on missing data. Not a red failure — a *green* one."
5. "It's not a cache. It's a live registry of who owns what."
6. "The moment worth recording wasn't when I had a result. It was the moment I started five physical machines doing something somebody has to turn off."
7. "My orphan cleanup was deleting the one piece of information required to clean up the actual orphan."
8. "In test infrastructure, the failure you have to design against isn't the crash. It's the pass."

---

## ALTERNATIVE DIP — use this if the TTL incident did NOT actually happen to you

Do not tell a story that isn't true. This version is honest, has no `[FILL]`, and is nearly as strong — it trades "war story" for "I audited my own design and found the hole," which reads as senior in its own right.

> **(6') The dip.**
>
> And then I went looking for the hole, because there's always one.
>
> I found it in my own cleanup logic. Redis keys had a one-hour TTL — that was my orphan collector. Worker crashes, nobody ever calls stop, the key expires, no cleanup job needed. I'd been quite pleased with that.
>
> And then I traced it through properly. When that key expires, what have I actually cleaned up? The *record* of the session. But the capture is still running — on five physical machines, holding files open, filling shared lab disks. And the only thing in the world that can stop it is `proxy.trace.stop(session_id)`. Which needs the session ID. Which I just deleted.
>
> **(7') The turn.** — *(then continue exactly as written above: "My first instinct was raise the TTL…")*

---

## [FILL] LIST

1. **Beat 6, the dip.** `[FILL: confirm the TTL expiry / vanished session actually happened to you.]` The source documents this as a design weakness, **not** as a recorded incident. If it did not happen, use the Alternative Dip above. Do not narrate an incident you did not live — it's the one thing in this story that can't survive a follow-up question.
2. **Beat 8, the 50%.** `[FILL: how was the 50% reduction in pipeline validation time actually measured — baseline, method, sample?]` The source asserts this figure and never substantiates it. If you can't defend the methodology, still say the number (it's on your resume) but be ready with: *"That's a wall-clock comparison of the validation stage, not an instrumented benchmark — what I'll defend precisely is the mechanism."*
3. **Beat 8, the defect that got caught.** `[FILL: one concrete example of a test that passed its assertions while NFTRACE caught broken signalling underneath.]` The source states this class of bug was caught but gives no instance. One real example here is worth more than the entire 50% claim — it is the story's whole thesis, made real.
4. **Beat 4, the villain.** `[FILL: did two parallel workers actually collide on a shared node in production, or is this the failure mode you designed against pre-emptively?]` Both are legitimate and the story works either way — but you must know which one you're claiming, because "did that actually happen?" is the obvious follow-up. If it's the latter, phrase it as: *"That's the failure this design exists to prevent"* rather than *"and that's what happened."*
