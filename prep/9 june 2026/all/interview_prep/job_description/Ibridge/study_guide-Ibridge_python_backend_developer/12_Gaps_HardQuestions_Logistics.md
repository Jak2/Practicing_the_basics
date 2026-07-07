# 12 — Coding Round, Hard Questions & Contract Logistics

Closes three gaps the rest of the guide didn't cover: (A) a live Python coding round, (B) the uncomfortable personal questions, (C) contract/IBridge-vendor logistics. Nothing here contradicts files 00–11; it extends them.

---

## PART A — Live Coding / Practical Round Prep

You may get one of: a LeetCode easy/medium, a practical "write this function/endpoint" task, or a debugging task. You're a strong engineer — this is about not being rusty. **2 hours total is enough.**

### A1. Talk-while-you-code protocol (more important than the answer)
1. **Restate the problem** + ask clarifying Qs (input size? edge cases? empty/null? duplicates?).
2. **State approach + complexity** before coding ("brute force is O(n²); I'll use a hash map for O(n)").
3. **Code incrementally**, narrate as you go.
4. **Test out loud** with a small example + an edge case.
5. **State time/space complexity** at the end.
> Interviewers score *how you think*, not just a passing solution. Silence kills; narration saves.

### A2. Patterns that cover ~80% of practical questions
- **Hash map / set** for lookups, dedupe, counting (`collections.Counter`, `defaultdict`).
- **Two pointers / sliding window** for arrays/strings.
- **Sorting + scan**.
- **Dict grouping** ("group anagrams", "group by key").
- **String parsing** (split, regex, count words/chars).
- **Recursion / simple tree or dict traversal**.
Don't over-prep graphs/DP for a backend contract role — practical > algorithmic here.

### A3. Warm-up problems (do these Sunday AM, write from scratch)
1. Reverse words in a string / check palindrome.
2. Count word frequency in text → return top N (`Counter.most_common`).
3. Find duplicates / first non-repeating char.
4. Two-sum (hash map).
5. Merge two sorted lists; flatten a nested list.
6. Group a list of dicts by a key.
7. FizzBuzz (yes, still asked — don't fumble it).
8. Parse a log line / CSV row into a dict.

### A4. Practical backend-flavored tasks (more likely than pure DSA)
- **"Write a FastAPI endpoint that…"** → recall file 01: Pydantic model, path/query/body, `Depends`, status code, error handling. Practice writing one endpoint from memory.
- **"Write a function to call an API and retry on failure"** → `httpx` + try/except + backoff loop.
- **"Deduplicate/aggregate this list of records"** → dict/Counter.
- **"Given this SQL schema, write a query for X"** → file 04.
- **"Find the bug in this code"** → look for mutable default args, off-by-one, blocking I/O in async, missing await, SQL injection.

### A5. Python snippets to have at fingertips
```python
from collections import Counter, defaultdict
Counter(words).most_common(3)            # top-N frequency
d = defaultdict(list); d[k].append(v)    # grouping
sorted(items, key=lambda x: x["age"])    # sort by key
{x for x in seq}                          # dedupe
[x for x in seq if cond]                  # filter
# retry with backoff
for attempt in range(3):
    try: return call()
    except TransientError:
        time.sleep(2 ** attempt)
```

---

## PART B — The Hard Personal Questions (rehearse these word-roughly)

These WILL come if the interviewer reads your resume carefully. Answer calm, brief, forward-looking. **Never sound defensive or badmouth anyone.**

### B1. "You've been at Brane only ~2 months — why leave already?"
Your strongest framing (pick the one that's TRUE for you):
- *Contract/role nature:* "That engagement was scoped/short-term, and it's wrapping up — which is why I'm available immediately. It gave me focused, intense exposure to a production AI-agent runtime, but I'm looking for a role centered on backend API and platform engineering, which is exactly this one."
- Keep it 2 sentences. Pivot to enthusiasm for *this* role. Do not over-explain.

### B2. "Your roles have been fairly short — are you a flight risk?"
> "A few were contract or transition-driven — for example my Nokia work continued seamlessly into Infinite with zero disruption to the client. My longest was nearly 3 years at Nokia, where I went from delivery to architecting NFTRACE and mentoring engineers to senior readiness. I'm looking for exactly that kind of depth again — somewhere I can own a backend platform over time."
- Anchor on the **2y10m Nokia tenure** as proof you stay and grow when the work is right.

### B3. "JD wants 6–8 years; you have ~5. Why are you a fit?"
> "I'm at 5+ years, but the responsibilities have been senior — architecting distributed systems, owning schema design end-to-end, mentoring three engineers to senior level, and authoring team-wide code-review standards that the whole team adopted. I'd ask you to weigh the depth and ownership, not just the year count."

**Specific evidence to draw from (have these ready as follow-up details):**
- **Architecture ownership:** NFTRACE — I didn't just contribute to it, I designed the session isolation model (Redis keying strategy), the decoupled scenario/validator architecture, and the lifecycle API. The 50% pipeline validation improvement came from those architectural choices.
- **Mentoring to senior level:** At Nokia, I mentored three engineers from mid-level to senior readiness — not just code review, but helping them own problem framing and design tradeoffs. That's the work that doesn't show up in commit history.
- **Team-wide process:** Authored the code-review checklist used across the team — covering async safety, SQL injection surface, Pydantic validation completeness, and error propagation. That was adopted as a standard, not just a personal habit.
- **Production incident response:** Owned the on-call response for NFTRACE pipeline failures — that meant diagnosing under pressure, communicating status, and doing post-mortems. That's not junior work.

> "As an immediate joiner I close the gap on day one — there's no ramp-up cost."
- Confident, not apologetic. Lead with **impact and ownership**, never "I know I'm short but…".

### B4. "Why contract instead of permanent?" / "Are you ok with a contract role?"
> "Yes — I'm comfortable with contract engagements; several of my roles have been. I value the focused scope and the chance to deliver impact quickly, and I'm an immediate joiner, so I can ramp fast."

### B5. "Why are you applying for a backend role when you're branded AI Engineer?"
(Already in file 08 §2 — same reframe: backend is the core, AI sits on top and is a tool you use.)

### B6. "What's your current/last CTC and expectation?"
- See Part C. Don't anchor low; give a researched range; let them move first if you can.

### B7. "Any gaps in employment?" / dates
- Your timeline is continuous (Mar 2021 → now). If asked about the Nokia→Infinite overlap: "That was a contractor transition — same 5G project (UDM/AUSF LOT3), continued under Infinite with zero handover disruption." Clean, honest.

### B8. General rule for all hard questions
Acknowledge briefly → give the honest, positive frame → **pivot to why you want THIS role** → stop talking. Don't fill silence with over-justification.

---

## PART C — Contract / IBridge-Vendor Logistics

This is a **contract role, payroll via IBridge Tech soft** for an end client. The flow differs from a permanent hire.

### C1. Likely process
- IBridge (vendor) may do a **screening call first** (availability, rate, basic fit) before the client technical round.
- Then **client technical interview(s)** — the Monday one.
- Possible **background/reference verification** and document checks (contract roles verify heavily).
- Confirm: how many rounds, who you meet, video vs in-person, duration of contract, extension/conversion possibility.

### C2. Rate / compensation
- Contract pay is usually a **monthly or per-day/hourly rate**, often higher gross than equivalent permanent salary (no benefits).
- **Know your number before the call.** Decide: minimum acceptable, target, and a range to state.
- Tactics: let them name a budget first if possible ("What's the budget range for this role?"). If pushed, give a **range** with your target near the bottom-third, and tie it to your experience/immediate availability.
- Ask: rate basis (monthly/daily), payment cycle, contract length, renewal terms, who handles taxes/PF (vendor payroll).

### C3. Logistics to confirm / have ready
- **Notice period:** you're an **immediate joiner** — say it early and often; it's a real edge for contract hiring.
- **UK shift:** JD requires flexibility — confirm clearly you're fine with it.
- **Location:** Hyderabad — confirm on-site / hybrid / remote expectation.
- **Documents:** updated resume, ID, prior experience letters/payslips if asked (contract verification).
- **References:** line up 1–2 people who'll vouch (a manager/peer from Nokia is ideal — longest tenure).

### C4. Questions to ask the vendor/client (logistics)
1. "What's the contract duration and is there scope for extension or conversion to permanent?"
2. "What does the interview process look like end-to-end after Monday?"
3. "Is this on-site in Hyderabad, hybrid, or remote? And the exact shift hours?"
4. "What's the rate range budgeted for this role?" (ask the vendor, not the client)

---

## PART D — Final completeness checklist (tick before Monday)
- [ ] Can give 2-min intro + the AI→backend reframe smoothly (file 08, CHEATSHEET).
- [ ] 3 flagship project index cards written + rehearsed out loud (file 11 Part D).
- [ ] Can defend every major tech choice with the 4-beat pattern (file 11).
- [ ] Wrote 15 SQL queries from scratch (file 04 / 09).
- [ ] Did 8 warm-up coding problems + wrote one FastAPI endpoint from memory (Part A).
- [ ] Rehearsed the hard questions: 2-month Brane, short tenures, 5-vs-8 yrs, why contract (Part B).
- [ ] Know my rate number + range (Part C).
- [ ] 5 questions ready to ask them (Master Plan §6 + Part C4).
- [ ] Snowflake basics — can answer "what is it / why different" (file 05).
- [ ] Logistics confirmed: format, rounds, shift, location, documents, references.
- [ ] Printed CHEATSHEET.md for morning-of glance.
- [ ] Reviewed DANGER ZONE questions in file 11 — have honest answers, not bluffs.
- [ ] Slept well Sunday. Calm > crammed.

---

## PART E — The Knowledge Gap Recovery Protocol

**This is the most important section for your specific situation.** You've built real things but may not remember every detail. Gaps are not disqualifying — how you handle them is.

The principle: **a skilled interviewer would rather see you navigate uncertainty honestly than watch you bluff and get caught.** Bluffs collapse under follow-up questions. Honest pivots demonstrate meta-awareness, which is a senior trait.

### E1. Scripted phrases for the three common gap situations

**When you genuinely don't know a concept:**
> "I haven't used X directly, but the principle is similar to [related thing I know well], so I'd approach it by [your reasoning]. I'd want to read the docs before committing to specifics, but that's my instinct on the design."

Example: "I haven't used Celery directly, but the principle is similar to how I've used background worker queues — task serialization, broker as the shared queue, worker pool consuming from it. I'd verify the API specifics, but the mental model maps."

**When you don't remember the exact implementation:**
> "I'd need to look up the exact API / the specific code to give you the precise details, but the design reasoning was [explain the why], and the trade-off we were navigating was [explain the constraint]. The specific implementation I can pull up — the reasoning behind it I can give you right now."

This works because it separates *engineering judgment* (which you have) from *implementation recall* (which fades). Interviewers care more about the former.

**When an interviewer notices you used X on your resume but your answer is thin:**
> "That was [early in the project / a library we integrated / a decision inherited from the team setup] — what I can speak to confidently is [the design decisions I personally owned and can defend in detail]."

Do not apologize for this. Own your scope. "I can go deep on the schema design and the API layer — those were mine. The infrastructure provisioning was shared with the team and I'd be less precise there."

### E2. The redirect move

When you don't know something, redirect to adjacent territory you DO know — and name the redirect explicitly:

> "I can't speak precisely to X, but it connects to [Y], which I know well — want me to walk through that?"

This is not dodging. It is demonstrating that you know what you know and what you don't, which is a senior skill.

### E3. The "I'd look it up" answer is valid

For specific syntax, API parameters, library versions: "I'd look that up rather than guess — I'd rather give you the right answer than a confident wrong one" is completely acceptable for implementation minutiae. It is NOT acceptable for design reasoning, architecture decisions, or system behavior. Know which category the question falls in.

### E4. What never to do
- **Never invent a specific detail** (key schema, column name, error message format) and state it with false confidence. One follow-up question collapses it and damages credibility for the rest of the interview.
- **Never apologize repeatedly** for not knowing. Say it once, pivot, move on.
- **Never pretend to be thinking** when you're actually stalling. It reads poorly. Silence + "let me think through this" is better than visible flailing.

---

## PART F — Interview Recovery Moves

Things go wrong. Here is exactly what to do.

### F1. You gave a wrong technical answer and the interviewer corrected you

**What happens:** You say something technically incorrect. The interviewer says "actually, that's not quite right" or explains the correct behavior.

**The wrong response:** Getting defensive, doubling down, or visibly flustered.

**The right response — exact script:**
> "You're right — I had that backwards / I was conflating it with [X]. That makes more sense because [restate their correction in your own words to show you absorbed it]. Good catch."

Then move on. Do not dwell on it, do not apologize three times, do not let it derail your composure. One acknowledgment, restate to confirm understanding, continue.

**Why this works:** Accepting a correction gracefully and demonstrating you actually absorbed it is a positive signal. Interviewers are partly watching how you respond to being wrong — it predicts how you'll behave in code review and on-call.

### F2. You started answering and realized mid-sentence you're going the wrong direction

**What happens:** You begin an answer, get two sentences in, and realize you're addressing the wrong thing, or your reasoning is collapsing.

**The wrong response:** Trailing off, mumbling to a stop, or forcing a bad answer to completion.

**The right response — exact script:**
> "Actually — let me back up. I started going down [X] but I think the better answer starts with [Y]. Let me restart."

This is not a failure. This is exactly what you do in a code review or design discussion when you catch your own error. It demonstrates intellectual honesty and self-correction in real time. Interviewers respect it.

### F3. You drew a blank on something you should know

**What happens:** The interviewer asks about something core — a Python built-in, a SQL clause, a concept from your resume — and your mind goes completely empty.

**The wrong response:** Silence for 10+ seconds, visible panic, or making something up.

**The right response — two options:**

Option A (if you need a moment):
> "Give me a second — I want to think through this properly rather than rush an answer."
Then use the silence. 5-10 seconds of deliberate silence looks like thoughtfulness, not blankness. Take it.

Option B (if it's genuinely not coming):
> "I'm blanking on the exact [term / syntax / detail] right now — I know the concept but I'd be inventing the specifics. Can I describe the behavior and you tell me if I'm thinking of the right thing?"

Then describe what you think you know about it. Often the description will unlock the term. And if it doesn't, you've demonstrated you understand the concept even if you lost the label — which is more important.

**The composure rule:** The interviewer is not as surprised by a blank as you feel. What they're watching is whether you spiral or recover. A smooth recovery from a blank is often more impressive than a candidate who never stumbles at all — it shows real-world engineering behavior.

---

## GAP FILL: "Why IBridge / Why This Role?" (must prep — asked in every interview)

**Why this matters:** Every interview ends with "why us?" A blank or generic answer after a strong technical round leaves a poor final impression.

### The answer frame

Three components: (1) what draws you to the *type of work*, (2) what draws you to *this specific role*, (3) what you're looking for next.

**Spoken answer (adapt in your own words):**
> "A few things, honestly. First, I've been building backend Python services and AI integrations for a few years now, and the IBridge role is exactly the intersection — production FastAPI, SQL, and intelligent systems working together, not one or the other. That's the kind of stack I've been deep in and want to go deeper.
>
> Second, the scale of the problem is interesting to me — ad creative generation at production volume means real system design challenges around async processing, caching, and reliability. Those are the kinds of engineering problems I find genuinely engaging, not just 'another CRUD API.'
>
> Third, the immediate-join timing works out well — I'm available now, which means I can ramp quickly without a notice period disruption, and I want to be in something meaningful right away rather than sitting idle."

**If they press on "why IBridge the company specifically":**
> "Honestly, I care more about the engineering culture and the kind of problems I'll be solving day-to-day than the brand name at this stage of my career. What I'm looking for is a team where backend quality is taken seriously — code review, migration discipline, production observability — and based on how this role is described, that seems to be the environment here."

### What NOT to say
- "It's a great opportunity" (generic — tells them nothing)
- "I need a job" (true but never say it)
- "The salary is good" (never lead with money)
- Anything that implies desperation or that you're only applying because you're available

---

## GAP FILL: Salary / Rate Conversation (contract role)

**Why this matters:** IBridge is a contract role. They WILL ask your expected rate or salary. No prep for this = fumbling a simple logistical question.

### What to expect

As a contractor, you'll likely be asked:
- "What is your expected CTC / salary?"
- "What is your expected day rate / monthly rate?"
- "What are you currently earning?"

### Your approach

**Step 1: Know your number before the interview.** Research the market for Senior Python/FastAPI contractors in Hyderabad (₹15L–₹25L CTC range for contract senior roles is typical; adjust based on your research and current earnings).

**Step 2: Anchor high, not exact:**
> "Based on my experience level and the responsibilities — senior backend ownership, FastAPI production systems, SQL architecture — I'm looking at [X]. I'm open to discussing based on the full engagement structure — duration, renewal terms, and so on."

**Step 3: Don't reveal your current salary if you can avoid it:**
> "I'd rather focus on what the role is worth in the market and what fits your budget — I'm happy to discuss from there."

**Step 4: If pressed for a number and you're not sure:**
> "I've been looking at ranges in the ₹[X–Y] per month bracket for contract senior backend work. Is that in the range you have budgeted for this position?"

Turning it into a question stops the negotiation from being one-sided.

### The UK shift question (if not yet raised)

The JD says "flexible to UK shift." If this hasn't come up, raise it yourself — it signals you've read the JD and removes a concern:
> "I saw the JD mentions flexibility with UK shift hours — yes, I'm comfortable with that. Happy to align to whatever working window works for the team."

---
