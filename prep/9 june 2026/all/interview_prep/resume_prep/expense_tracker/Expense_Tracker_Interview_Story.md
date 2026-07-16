# Financial Statement Parser — The 3-Minute Story

**Use when:** "Tell me about a project you're proud of." / "Walk me through something you built."
**Runtime:** ~3 minutes at a natural pace. Do not rush the villain.

> **Before you tell this story, read the top of `Expense_Tracker_Interview_QA.md`.** Your resume bullet says "no data leaves your device" and "Python." Neither is true of this project. This story is built to be told by someone who *knows* that and states the boundary precisely — which is what makes it land. Told by someone still claiming "100% private," the same story is a trap: you'd be inviting an interviewer to check a claim you can't defend.

---

## 1. Setup — the world before

> Everybody with a bank account has done this.
>
> You open a PDF of your statement. You put a spreadsheet next to it. And you start typing. Date, description, amount. Date, description, amount. A typical statement is thirty to a hundred rows.
>
> A freelancer doing three months before a tax filing does it for an afternoon. An accountant doing twenty client statements a week does it every week. And somewhere around row forty you transpose two digits, and you don't find out until the totals don't reconcile.
>
> It's the most mechanical work imaginable, and skilled people are still doing it by hand in 2026.

---

## 2. The real problem — the stakes

> Now, tools exist. Docparser, Tabula, the paid parsing services. They work.
>
> And every single one of them asks you for the same thing first: **upload your bank statement.**
>
> Sit with what's actually in that document. Not "financial data" — the specifics. Your salary, to the rupee. Your rent. Your landlord's name. What you spent at a pharmacy last March. Your account number. Your balance on every single day of the month. If I wanted to reconstruct your entire life — where you live, what you earn, what you're worried about, who you pay — I would not ask for your diary. I'd ask for your bank statement.
>
> And to save an afternoon of typing, we hand it over. To a company we've never heard of, whose privacy policy we didn't read.
>
> That's the actual problem. It was never the typing.

---

## 3. The obvious build — and why it's a trap

> The obvious version of this is a weekend.
>
> Stand up a server. User uploads the PDF. Server runs OCR, or better — skip OCR entirely, hand the raw file to a multimodal model, Gemini reads the page directly. It's *one API call*. No canvas rendering, no OCR engine, no character limits, no text extraction at all. It's less code and it's more accurate, because a vision model reads a table layout better than OCR-then-text ever will.
>
> The naive build isn't just easier. It's genuinely *better* on almost every axis.
>
> It also requires me to build the exact thing I'm angry about. It requires the user to upload their bank statement.
>
> And then I'd write "we don't store your files" on the landing page. And I'd mean it.

---

## 4. The villain, named

> **And that's the villain: "we don't store it" is a promise. It is not an architecture.**
>
> A promise has four ways to fail, and none of them require anybody to be a bad person.
>
> It can be **broken** — someone leaves a debug log on. It can be **breached** — the bucket was public for six hours and nobody noticed. It can be **subpoenaed** — the company's intentions become irrelevant. And it can be **acquired** — the founders who meant it sincerely in year one sell in year three, and the new owner writes a new privacy policy, and your statements are already in the bucket.
>
> Every one of those failures ends with your financial life somewhere you didn't put it. And the honest thing to notice is: **you can't audit any of it.** You cannot tell, from the outside, whether a server that promises not to keep your data is keeping your data. You are trusting a sentence.
>
> That's the villain. Not a company. Not a breach. **The convenience that quietly demands your entire financial life as its price — and then hands you a sentence as a receipt.**
>
> The only privacy guarantee worth anything is the one where the data *physically cannot leave*. Where there's no promise to break, because there's no server to break it.

---

## 5. The hero — the architecture that makes the promise unnecessary

> So I built it with no backend. At all.
>
> The file goes into the browser and stops there. If it's a PDF, pdf.js renders each page to a canvas — in the tab. Then Tesseract.js reads the text off it — Tesseract, the real OCR engine, compiled to WebAssembly, running as a binary inside the browser at near-native speed. Also in the tab. The document never crosses the network.
>
> Then — and I want to be exact here, because this is where most people would overclaim — **only the extracted text** goes to Gemini, which turns it into structured transactions with a category and a fixed-or-variable label. Not the file. The text.
>
> And it goes on **the user's own API key**, straight from their browser to Google. Because there's no server of mine in the middle. There's no database. There's no account. There's no telemetry — and not because I promise there isn't. **Because there is nothing to send it to.**
>
> That's the whole point. I'm not asking anyone to trust me. I built a thing where I *have no capability to betray*. You can verify it in thirty seconds — open the network tab, process a statement, count the requests. One POST to Google. That's it.
>
> I moved the trust boundary as far as I could without losing the product. And I know exactly where I left it.

---

## 6. The dip

> And then I gave it a real statement. A long one.
>
> The transactions came back. The table rendered. The dashboard lit up — total expenses, net cash flow, daily burn rate, a nice bar chart of where the money went.
>
> And there were fewer transactions than the statement had.
>
> Not an error. Not a crash. Not a red banner. A **beautiful, confident, complete-looking report that was quietly missing rows.**
>
> Two things were causing it, and they were the same thing wearing different clothes.
>
> The first: to stay inside the model's token budget, I cap the OCR text at eight thousand characters. Anything past that just... doesn't get sent. Those transactions were never in the request.
>
> The second was worse, because it was something I'd built **on purpose**. Gemini has an output limit too, and on a big statement it hits it and stops mid-array. So I'd written a three-method salvage: strip the code fences, find the outer braces, and if it's still broken, walk back to the last complete transaction object, close the JSON by hand, and carry on. I was proud of it. I'd written the principle down: *partial results are more useful than a failure.*
>
> And it is. In a note-taking app. In a summarizer.
>
> In a tool that tells you what you spent this month, **a partial result the user believes is complete is worse than a failure.** Because a failure sends them to go check. And a slightly-too-small number sends them to bed.
>
> I had spent all this effort making sure nobody could *steal* the user's financial data. And I'd built a tool that would quietly *lie* to them about it.

---

## 7. The turn — the realization

> The fix for the cap is engineering. Chunk the text, call the model per chunk, merge the arrays. It's an afternoon.
>
> The realization was different, and it came from staring at the schema I'd already written.
>
> Every bank statement has a **running balance** column. Previous balance, minus the debit, plus the credit, equals the current balance. Every row. It's not decoration — **it's a checksum. The document validates itself.** Banks have been shipping a built-in integrity check on every statement for a century and I'd been looking straight at it.
>
> And I was already extracting it. It was sitting right there in my data contract, in the table, in the Excel export — and **not one line of code was reading it.**
>
> One loop over that column and every silent failure I had becomes loud. A dropped row breaks the chain. A misread digit breaks the chain. A swapped debit and credit column breaks the chain. The thing I'd been trying to detect had been handed to me by the domain, for free, and I'd walked past it because I was busy being clever about JSON.
>
> That's the moment the project actually taught me something. Not "add a validation layer." **Look at what the data already knows about itself.**

---

## 8. The landing

> Where it ended up: a bank statement — a PDF or a phone photo of a paper one — becomes a categorized, editable table and a five-sheet Excel workbook, or a CSV, or a formatted PDF report with the charts embedded. Fourteen categories, fixed versus variable, burn rate, cash flow. No account. No subscription. No server. It deploys as a folder of static files and costs nothing to run, forever, because there's nothing running.
>
> And two things I'd say honestly rather than let someone find them.
>
> The extracted text does reach Google. I've stopped the *document* from leaving — the account number, the letterhead, the page itself. I haven't stopped the *text*, and I won't stand here and claim I have.
>
> And the balance-column checksum isn't built yet. It's the first thing I'm building.
>
> But the principle I'd take from this and carry into anything else I build — it's the one that answers the villain. **A promise is not a guarantee. If your architecture requires the user to trust you, you haven't solved their problem — you've just asked them to hope.** The good version isn't the one where I'm trustworthy. It's the one where I *can't* be untrustworthy.
>
> And the second half, which the statement taught me: **in a financial tool, the failure that hurts you isn't the one that throws an error. It's the one that hands you a plausible number.**

---

## Why this works on this audience

| The move | What the interviewer actually reads from it |
|---|---|
| Opening with the *contents* of a bank statement, not "financial data" | You reason about users, not about features. Specificity is the tell. |
| Naming the multimodal call as **easier, shorter, and more accurate** — and refusing it | You made a costly trade on principle and you can articulate the cost. Anyone can refuse a bad option. |
| "A promise is not an architecture" | This is a *senior* distinction. Junior engineers implement policies; senior engineers design away the need for them. |
| Volunteering that the text still reaches Google | Kills the interview's sharpest attack before it's asked, and buys credibility for everything else you said. |
| The dip being **your own design decision**, not a library's bug | Self-critical about a thing you were *proud of*. This is the hardest and most convincing form of honesty. |
| "Partial beats failure is right for notes and wrong for money" | Context-dependent engineering judgement. Reciting a principle is cheap; knowing where it *stops* is not. |
| The balance-column turn | A realization, not heroics. And it's genuinely a good insight — domain knowledge beating cleverness. |
| Admitting it isn't built yet | Nothing in this story is inflated, so nothing in it is checkable-and-false. |

---

## Delivery notes

| Beat | Pace | Do this |
|---|---|---|
| §1 Setup | Brisk | Don't linger. This is throat-clearing that earns the next beat. |
| §2 Stakes | **Slow down** | "Your salary, to the rupee. Your rent. Your landlord's name." Land each one. This is where they lean in. |
| §3 The trap | Conversational | Genuinely sell the naive build as *good*. If they don't believe it was tempting, the refusal is worthless. |
| §4 **THE VILLAIN** | **Slowest point** | Beat of silence before "we don't store it is a promise, not an architecture." Then the four failures, one at a time. |
| §5 The hero | Build energy | "Because there is nothing to send it to." Stop there. Let it sit. |
| §5 The concession | Level, unhurried | "Only the extracted text." Say it like a spec, not an apology. It's precision, not confession. |
| §6 THE DIP | Drop the energy | "And there were fewer transactions than the statement had." Then silence. This is the pivot of the whole story. |
| §7 The turn | Quiet, then dawning | "It's a checksum. The document validates itself." This is the smartest sentence you will say. Don't rush it. |
| §8 The landing | Firm, unhurried | Last two lines are memorized. Say them clean and stop talking. |

**If they interrupt during the villain, let them.** An interviewer who interrupts to argue about privacy architecture is an interviewer who is now *in* the conversation. Answer, then say "— and that's exactly why I couldn't build it the easy way," and continue.

**If you only have 90 seconds:** §2 (stakes) → §4 (villain) → §5 first and last paragraphs → §6 dip → §7 turn → last line of §8. Drop §1 and §3.

---

## Lines to memorize

1. *"If I wanted to reconstruct your entire life, I wouldn't ask for your diary. I'd ask for your bank statement."*
2. *"'We don't store it' is a promise. It is not an architecture."*
3. *"Broken, breached, subpoenaed, or acquired."*
4. *"No telemetry — not because I promise there isn't. Because there is nothing to send it to."*
5. *"I built a thing where I have no capability to betray."*
6. *"A partial result the user believes is complete is worse than a failure. A failure sends them to go check."*
7. *"It's a checksum. The document validates itself."*
8. *"If your architecture requires the user to trust you, you haven't solved their problem — you've just asked them to hope."*
9. *"In a financial tool, the failure that hurts you isn't the one that throws an error. It's the one that hands you a plausible number."*

---

## [FILL] list

| # | Where | What you must supply — and why it matters |
|---|---|---|
| 1 | **§6, the whole dip** | **[FILL: confirm this actually happened to you.]** The source documents the 8,000-char cap and the truncation salvage as *design facts*. It does **not** say you discovered them by feeding in a long statement and finding rows missing. If you never had that moment, **do not narrate it as a moment.** Rewrite §6 in the honest form: *"Neither of these has bitten a user, because I built for one- and two-page statements. But I can read my own architecture, and I know exactly what a fifty-page statement does: it silently under-reports."* That version is nearly as strong and it is unfalsifiable, because it's true. |
| 2 | §7, the balance realization | **[FILL: confirm you actually had this insight.]** The source confirms `balance` is extracted and that `analytics.js` never reads it — the *gap* is real and verifiable. Whether you *noticed* it as a checksum is yours to confirm. If it's a realization you're having now, reframe: *"Reviewing this before today, the thing that jumped out at me was..."* — still honest, still lands. |
| 3 | §8 | The stakes example uses ₹ (the source's sample data is `debit: 2499.00`, currency unstated). Match the currency to your audience. |
| 4 | §8 | **[FILL: one real number.]** The story has zero metrics, which is *safe* but leaves it a little abstract. One measured figure — "a one-page statement takes N seconds on my laptop" or "I've run it on M statements from K banks" — makes the landing concrete. Get this from the Tier-2 prep in the Q&A file. |
| 5 | Everywhere | **Do not say "100% private," "no data leaves your device," or "Python"** while telling this story. All three are contradicted by the source, and the story's whole power comes from being the person who states the boundary precisely. |
