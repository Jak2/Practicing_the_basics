# Financial Statement Parser — Interview Q&A

**Project:** Financial Statement Parser (v1.3.1, June 2026) — React + Vite browser app. Bank statement image/PDF → in-browser OCR → Google Gemini for parsing/categorisation → editable table → CSV / Excel / PDF export.

**Resume bullet under test:**
> "Financial Statement Parser: 100% private, browser-based AI that transforms messy bank statement PDFs into categorized Excel reports in 10 seconds. No servers, no data leaves your device. Stack: Python, AI, browser."

---

## ⚠️ STOP — FIX THE RESUME BULLET BEFORE YOU INTERVIEW

Three statements in that bullet are **contradicted by your own project report**. If an interviewer reads the bullet and then reads your architecture, you lose the room — not because the project is bad (it isn't), but because you overclaimed.

| Bullet claim | What the source actually says | Verdict |
|---|---|---|
| **"No data leaves your device"** | §3 Step 3, §4 Client-Side Boundary, §6: *"Only the OCR-extracted text leaves the browser — plain text capped at 8,000 characters — sent to Google's Gemini API over HTTPS."* The endpoint is `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`. | **FALSE.** The *file* doesn't leave. The *contents* do — every date, merchant, debit, credit and balance the OCR could read. That is the financially sensitive part. |
| **"100% private"** | Private *relative to the app*: there is no app-controlled backend, no DB, no telemetry. But your transaction text is in Google's hands, under Google's terms, on the user's own API key. | **OVERCLAIMED.** True statement: *"no app-controlled server; your document never leaves the browser; only extracted text goes to the AI, under your own API key."* |
| **"Stack: Python"** | Source lists React 18.2, Vite 5.0.10, Tailwind 3.4, Tesseract.js 5.0.4, pdfjs-dist 4.0.379, Gemini 2.5 Flash, Recharts, SheetJS, jsPDF, html2canvas, file-saver, Lucide. Node 18+. | **FALSE. There is zero Python in this project.** Anyone who asks one Python question here will discover it. |
| **"in 10 seconds"** | The source never benchmarks anything. No timing, no hardware, no page count. | **UNSUPPORTED.** See Q-T1. |
| **"categorized Excel reports"** | True. 5-sheet .xlsx via SheetJS: Summary, Categories, Transactions, Fixed Costs, Variable Costs. 14 categories + fixed/variable. | **TRUE.** |

**Rewrite it to something you can defend, e.g.:**
> *Financial Statement Parser — browser-only React app that turns bank statement PDFs/scans into categorized Excel/CSV/PDF reports. OCR runs client-side in WASM (Tesseract.js) so the document itself never leaves the device; only extracted text is sent to Gemini, on the user's own API key. No backend, no database, no telemetry. Stack: React, Vite, Tesseract.js (WASM), pdf.js, Gemini 2.5 Flash, SheetJS.*

If the bullet is already out on live applications: **do not defend it, concede it in the first breath.** The script is in Q-P1. A candidate who says "that bullet is sloppy, here's the precise claim" reads as rigorous. A candidate who defends it reads as someone who doesn't know what their own architecture does.

---

## READ THIS FIRST — where this project is actually attackable

| # | The question that hurts | Why it hurts | Your one-line answer |
|---|---|---|---|
| 1 | **"You say no data leaves the device. But you POST to `generativelanguage.googleapis.com`. What's in that POST?"** | It's your headline claim vs. your own §4. | "Extracted text — the transactions themselves. The file stays local; the text doesn't. The resume bullet is imprecise and I'd fix it." |
| 2 | **"Your resume says Python. Where's the Python?"** | There is none. | "That's a mistake on the bullet. It's a React/Vite front-end with WASM OCR — no Python anywhere." |
| 3 | **"You cap OCR text at 8,000 characters. What happens to transaction 61 on a long statement?"** | §5.1 states the cap. Source never says the user is warned. **Silent truncation in a financial tool = silently wrong totals.** | "It's dropped, and today the user isn't told. That's the bug I'd fix first — it corrupts every downstream number." |
| 4 | **"Your JSON 'truncation repair' closes a half-finished response and shows the user the result. How do they know it's partial?"** | §5.3 method 3 + §8 decision 3: *"Partial results are more useful than a failure."* In a money tool, a partial result the user believes is complete is worse than a failure. | "Same root problem as the 8k cap — I chose recoverable over correct, and I didn't surface the recovery to the user." |
| 5 | **"Every bank formats statements differently. How does this generalize, and what does it do on a layout it's never seen?"** | Source has **no** evaluation, no test set, no accuracy number, no bank list. | "It generalizes because there's no per-bank parser — it's raw OCR text into an LLM. The honest gap is I have no measured accuracy, so I can't tell you where it degrades." |
| 6 | **"How do you know the categorization is right?"** | No ground truth, no eval, no accuracy metric anywhere in the source. The editable table is the *only* correctness mechanism. | "I don't measure it. The design bet is human-in-the-loop: every cell is editable before export. That's a mitigation, not a validation." |
| 7 | **"Money in floating point?"** | The data contract shows `"debit": 2499.00` — JSON numbers, JS `number`, IEEE-754 float64. `analytics.js` sums them. Classic. | "Yes — floats. Sums of thousands of two-decimal values will drift in the last cents. Should be integer minor units." |

If you can only prep three: **#1, #2, #3.**

---

## 1. Framing

### Q-F1. "Give me the ninety-second version."
> It's a browser-only tool that turns a bank statement — a PDF or a phone photo of a paper statement — into a categorized spreadsheet.
>
> You drop the file in. If it's a PDF, pdf.js renders each page to a canvas *in the browser*. Tesseract.js — the Tesseract OCR engine compiled to WebAssembly — reads text off those canvases, also in the browser. Then only that extracted text, capped at 8,000 characters, goes to Google's Gemini 2.5 Flash, which returns JSON: one object per transaction with date, description, debit, credit, balance, one of fourteen categories, and a fixed-or-variable label. That lands in an editable table with an analytics dashboard, and you export to CSV, a five-sheet Excel workbook, or a formatted PDF report.
>
> There is no backend. No database. No account. No telemetry. The user brings their own free Gemini API key, which lives in their `localStorage` and goes straight to Google. That's the whole system: React, Vite, Tailwind, and a pile of client-side libraries.

### Q-F2. "Why did you build it?"
> The manual path is: open the PDF, read a row, type the date, type the description, type the amount, repeat thirty to a hundred times. A freelancer doing three months before tax filing, or an accountant doing twenty client statements a week, burns real hours on it and transposes digits doing it.
>
> The tools that fix it all have the same price: upload your statement to somebody's server. Docparser, Tabula, the paid parsers — the document goes to them. And a bank statement is not a neutral document. It's your salary, your rent, your medical payments, your account number, your balance. I didn't want to build the thing that asks for that.

### Q-F3. "Who's it for?"
> Small business owners reconciling monthly expenses, freelancers preparing tax records, accountants processing client statements — and anyone who's spent an afternoon retyping a scanned PDF.

### Q-F4. "What did you actually build versus glue together?"
> Honestly: the heavy machinery is off-the-shelf. Tesseract does the OCR, pdf.js does the rendering, Gemini does the parsing, SheetJS does the Excel, jsPDF does the report. I want to be straight about that.
>
> What's mine is the architecture and the plumbing: the decision to OCR locally and send only text, the BYOK model that removes the backend entirely, the prompt that pins Gemini to a fixed fourteen-category schema, the three-method JSON salvage that recovers truncated model output, the analytics engine, the state machine, and the export paths that all consume one shared transaction shape. It's an integration project. The interesting parts are the boundaries, not the algorithms.

---

## 2. Privacy — the headline claim (attack surface #1)

### Q-P1. "Your resume says 'no data leaves your device.' Walk me through every outbound network call."
> Let me correct the bullet first, because it's imprecise and I'd rather say so than get caught on it.
>
> The **file** never leaves the device. That's true and it's the thing the architecture actually guarantees. But **data** does leave: the OCR-extracted text goes over HTTPS to `generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`. That text *is* the transactions — dates, merchants, amounts, balances. So the accurate claim is "your document never leaves your browser, and the only thing that does is extracted text, sent under your own API key, to no server I control." "No data leaves your device" is a stronger claim than my architecture supports, and I should not have written it that way.
>
> The complete outbound list from the source:
> 1. The Gemini POST — OCR text, capped at 8,000 chars.
> 2. The pdf.js **worker script fetched from the jsDelivr CDN** — code coming in, not data going out, but it is a third-party host on the critical path.
> 3. That's it. No app-controlled server exists. No analytics, no crash reporting, no telemetry — there's nothing to receive them.
>
> `localStorage` holds the API key under `gemini_api_key`. It goes browser → Google, never through me.

### Q-P2. "So what exactly is private about it?"
> Two things, precisely:
>
> **The document.** The image or PDF — with the account number, the letterhead, the balance summary, whatever else is on the page that OCR doesn't pick up or that I don't send — never goes anywhere. It's rendered and OCR'd inside the tab.
>
> **My liability surface.** There is no server, no database, no logs, no key store. Not "I promise not to look at your statements" — there is no mechanism by which I *could*. That's the part I'd defend hardest, because it's structural, not a policy.
>
> What is **not** private: your transaction text is processed by Google, under Google's API terms, on your key. I'd be lying if I said otherwise.

### Q-P3. "Then why is that better than a SaaS parser that also says it doesn't store your data?"
> Because "we don't store it" is a **promise**, and a promise has four failure modes: it can be broken, breached, subpoenaed, or acquired. The company that meant it in year one gets bought in year three, and the new owner writes a new privacy policy.
>
> An architecture with no server has none of those failure modes for the document. There's no bucket to breach. Nothing to subpoena. Nothing that changes hands in an acquisition.
>
> I'll concede immediately that the *text* path still rests on Google's terms — I've reduced the trust surface, not eliminated it. But I've eliminated *me* from it entirely, and I've kept the raw document out of it. That's a real reduction, and I'd rather state it exactly than oversell it.

### Q-P4. "Why not just send the PDF straight to Gemini? It's multimodal. You'd delete the whole OCR stage."
> That was the biggest fork in the project, and I chose the harder path on purpose. A multimodal call is one function; it deletes Tesseract, deletes pdf.js, deletes the canvas pipeline, deletes 8,000-character caps and truncation salvage. It's strictly less code and probably more accurate — a vision model reads table layout better than OCR-then-text ever will.
>
> And it uploads the user's bank statement to Google. That's the one thing I built this to not do. Privacy over simplicity — that's design decision #1 in my own report, and I stand on it.
>
> If I'm being fully honest with you: the *gap* between the two is smaller than I'd like, because the text I do send contains the transactions anyway. The document itself — the account number, the letterhead — is what I'm actually keeping back. That's meaningful. It's not everything.

### Q-P5. "The pdf.js worker loads from jsDelivr. Isn't that a supply-chain hole in a privacy tool?"
> Yes, and it's a fair hit. I load it from the CDN rather than bundling it — the report says it keeps the production build lean and avoids WebAssembly loader conflicts, and both are true. But it means a third-party host serves executable code into a tab that is about to handle a bank statement. A compromised or swapped script there could read the canvas or the OCR text before I ever get it.
>
> The mitigations I did *not* implement and should: bundle the worker locally, or at minimum pin it with Subresource Integrity, plus a Content-Security-Policy that permits `connect-src` only to `generativelanguage.googleapis.com`. For a tool whose entire pitch is privacy, "we fetch code from a CDN at runtime" is the loose thread, and I'd close it before I'd add another feature.

### Q-P6. "You store the API key base64-encoded and reversed. Is that security?"
> No, and I don't claim it is — the README literally says "This prevents casual inspection but is NOT secure encryption." Reversing a string and base64ing it is obfuscation. Anyone with devtools reverses it in ten seconds.
>
> The reasoning: the threat model is a shoulder-surfer or someone glancing at devtools, not an attacker with the device. And there's no good answer available — the browser has no secret store, and any key I encrypt has to be decryptable by client code, so the decryption key ships alongside it. The real mitigations are (a) it's a free-tier key the user can revoke in one click at AI Studio, and (b) the settings modal lets them delete it. What I'd tell a user: this key is disposable, treat it that way.

### Q-P7. "XSS on your page and the key's gone. And the transaction data. Response?"
> Correct, and that's the honest ceiling on a BYOK browser app. Any script executing in my origin reads `localStorage`, un-obfuscates the key trivially, and reads the transaction array out of React state. The obfuscation buys nothing against that.
>
> What limits the blast radius: the app is a static build with no user-generated content, no injection surface I'm aware of, and the key is free-tier and revocable. What I'd add: a strict CSP, which would also kill the jsDelivr concern — one control, two holes closed.

### Q-P8. "You said no telemetry. Prove it."
> The strongest proof is structural: **there's no server to send it to.** I never built a backend, so there's no endpoint that could receive an event. The report is explicit — "No app-controlled server exists. No analytics or telemetry calls are made."
>
> The verifiable proof is one step: open devtools, network tab, process a statement, and count the outbound requests. You should see the jsDelivr worker fetch and one POST to `generativelanguage.googleapis.com`. Nothing else. That's a check any user can run in thirty seconds, and I'd rather hand people that than a privacy policy.

---

## 3. The OCR pipeline

### Q-O1. "Walk me through the OCR stage."
> Two paths, one output.
>
> **Images (PNG, JPG, WEBP):** the file goes straight into `Tesseract.recognize(file, 'eng', { logger })`.
>
> **PDFs:** `src/utils/pdf.js` wraps pdf.js. Each page is rendered to an HTML canvas at the page's native dimensions, then exported as a PNG data URL via `canvas.toDataURL('image/png')`. That data URL goes into Tesseract. Pages are OCR'd in sequence and the text is concatenated.
>
> Both paths land in `src/utils/ocr.js`, which normalises progress so the bar means the same thing either way: PDF page conversion is 0–30%, OCR across all pages is 30–100%.
>
> The floor: if fewer than 50 characters come back, I error out with "Could not extract text. Please use a clearer image or PDF." Better to refuse than to send four characters of noise to an LLM and let it invent transactions.

### Q-O2. "Tesseract.js — is that actually running locally or is it calling out?"
> Actually local. Tesseract.js is the Tesseract OCR engine compiled to **WebAssembly**, so the binary runs inside the browser tab at near-native speed, in a Web Worker so it doesn't lock the UI thread. No server-side OCR process, no OCR API. That's the load-bearing piece of the whole privacy story — it's what lets the document stay on the device. If OCR were an API call, the architecture would collapse into "upload your statement," which is the thing I was avoiding.

### Q-O3. "Tesseract on a phone photo of a crumpled statement. Realistically?"
> Realistically, degraded, and I'll be honest that I don't have a number for how degraded. Tesseract is genuinely good on clean digital-native PDFs — the text is crisp because the page came from a renderer, not a camera. It gets worse with skew, shadow, low contrast, and column bleed, which is exactly what a phone photo has.
>
> What I did *not* build and should have: any preprocessing. No deskew, no binarisation, no contrast normalisation, no per-page confidence threshold. Tesseract exposes confidence scores and I don't use them. The 50-character floor is my only quality gate, and it catches "OCR found nothing," not "OCR found garbage." A page that OCRs to plausible-looking nonsense sails straight through to Gemini.
>
> [FILL: have you actually run this on a phone photo? If yes, what happened — say it concretely. If you've only tested digital PDFs, say *that* — "I've only validated it on digital-native PDFs" is a much stronger answer than a hedge.]

### Q-O4. "8,000 characters. Why, and what breaks?"
> The why is boring: it's a token-budget guard on the Gemini call.
>
> The break is not boring, and it's the thing I'd fix first. A statement whose OCR text exceeds 8,000 characters gets **truncated**, and the transactions past the cut simply never reach the model. They don't appear in the table. They don't appear in the totals. They don't appear in the Excel. And the source doesn't show me warning the user.
>
> That's the worst failure mode a financial tool can have: not "it broke," but "it silently gave you a smaller number than the truth and looked confident doing it." A user reconciling against their real balance would find it. A user trusting the burn-rate card would not.
>
> The fix isn't hard — chunk the OCR text, call Gemini per chunk, merge the transaction arrays, and dedupe. The reason it isn't done is that I built for the common case, a one-to-two-page statement, and never came back. That's a defensible starting point and an indefensible ending point.

### Q-O5. "What does 8,000 characters buy you in transactions? Is a typical statement even at risk?"
> [FILL: measure this. Take a real statement, OCR it, print `text.length` and count the transactions. Then you can say "a 40-row statement OCRs to roughly N characters, so the cap bites at around M rows." Without that number this question has no floor and you'll be guessing in the room — which is the one thing you cannot afford on the cap question, because it's already the sharpest attack on the project.]

---

## 4. The Gemini integration

### Q-G1. "Why an LLM at all? A regex-and-heuristics parser is deterministic, free, and never hallucinates."
> Because of the thing that makes this problem actually hard: **every bank's statement layout is different.** Different column orders, different date formats, different debit/credit conventions — some banks use two columns, some use one signed column, some put the balance first. A deterministic parser means one template per bank, and then you own a template library forever, and it breaks the day a bank redesigns its PDF, and it can't touch a scanned paper statement at all.
>
> The LLM is what lets me have zero bank-specific code. Raw OCR text goes in, structured transactions come out, and an unseen bank is just another Tuesday. That's the whole reason it generalizes.
>
> The price is real and I'll name it: non-determinism, an accuracy I can't state, hallucination risk, and dependence on an external API. I pushed back on the first with `temperature: 0.1` and on the last with BYOK. The accuracy one I have no answer for — see the eval question.

### Q-G2. "Walk me through the actual API call."
> Direct HTTPS POST to `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`, from `src/utils/gemini.js`. No SDK, no backend proxy — the browser talks to Google.
>
> Generation config:
> - `temperature: 0.1` — near-deterministic. Financial extraction has one right answer; I don't want creativity, I want the same output twice.
> - `maxOutputTokens: 16384`
> - `responseMimeType: 'application/json'` — Gemini's JSON mode, so I get valid JSON rather than prose I have to fish JSON out of.
>
> The prompt embeds all fourteen category names and the fixed-versus-variable rules, and pins the exact output schema. Errors are mapped to human language: HTTP 400 → "Invalid API key. Please check your Gemini API key."; HTTP 429 → "Rate limit exceeded. Please try again in a moment."

### Q-G3. "Why 2.5 Flash and not Pro?"
> Free tier, fast, and it supports structured JSON output mode — which is the feature I actually need. The task is extraction and classification from clean-ish text, not reasoning, so Flash-class is the right tier; Pro would cost more for capability the task doesn't use. And because it's BYOK, the model choice directly determines whether the tool is free for the user. Flash on the free tier means it is.
>
> [FILL: did you A/B Flash against Pro on a real statement? If yes, what changed. If no, say "I chose on cost and JSON-mode support and never benchmarked Pro against it" — that's an honest answer and it's fine.]

### Q-G4. "You set responseMimeType to JSON. So why do you need a three-method JSON salvage?"
> Because JSON mode guarantees *well-formed* JSON, not *complete* JSON. If the model hits the 16,384-token output ceiling mid-array, the stream just stops. What arrives is a valid prefix of a JSON document, which is not a JSON document. `JSON.parse` throws, and I've lost every transaction the model already correctly extracted.
>
> So `gemini.js` tries three recoveries in order:
> 1. **Code-block extraction** — strip markdown ```` ```json ```` fences if the model wrapped the output.
> 2. **Index-based boundary** — take everything from the first `{` to the last `}` by character index.
> 3. **Truncation repair** — find the last complete `},` in the transactions array, cut there, close the JSON structure by hand, and set `bankName` and `period` to `null` since those fields never arrived.
>
> The principle I wrote down was "partial results are more useful than a failure." I now think that principle is only half-right, and the missing half is the next question.

### Q-G5. "Method three hands the user a partial extraction. How do they know some of their transactions are missing?"
> They don't, and that's the flaw. Method three is silent salvage. The user gets a table, a dashboard, an Excel file, a burn-rate number — and no indication that the model got cut off and I stitched the response back together.
>
> In a note-taking app, "partial results beat failure" is correct. In a **financial** tool, a partial result the user believes is complete is *worse* than a failure, because a failure sends them to check and a wrong total does not. Silent under-reporting of expenses is the single most damaging thing this app can do, and I built two separate paths to it — this one and the 8,000-character cap.
>
> What it should do: still salvage, still show the rows — but flag it. A banner saying "the AI response was truncated; N transactions recovered, some may be missing," and mark the exports too. Keep the recovery, kill the silence. That's a small change and it's top of my list.

### Q-G6. "Does Gemini hallucinate transactions? How would you know?"
> It can. `temperature: 0.1` reduces it — that's explicitly why it's there — and a near-deterministic model given clean text mostly transcribes rather than invents. But "mostly" is doing a lot of work in that sentence and I have no measurement behind it.
>
> The structural defences: the model only ever sees OCR text from the actual document, so it has no external material to invent from; JSON mode plus a pinned schema constrains the shape; and every row is editable in the table before export, so a human is in the loop by construction.
>
> The gap I won't paper over: I have **no automated check** that the extracted rows correspond to real lines in the OCR text. A cheap one exists and I should build it — fuzzy-match each returned `description` back against the OCR string and flag any row that doesn't appear in the source. That would catch pure fabrication with about twenty lines of code and no extra API call.

### Q-G7. "The fourteen categories are hard-coded in the prompt. Why not let the model choose freely?"
> Because free-form categories make the analytics meaningless. If the model returns "Groceries" on one statement and "Food" on the next and "Supermarket" on a third, then `categoryTotals` in `analytics.js` — which groups by the `category` string — produces three buckets for one concept, the bar chart is noise, and the "top spending category" summary line is wrong. A fixed vocabulary is what makes cross-statement aggregation possible at all, and the Add More flow depends on it.
>
> The cost is a real ceiling: fourteen categories can't express everything, so genuinely ambiguous spend lands in "Other," and there's no way for a user to add a category. That's a fair trade for v1 and an obvious v2 feature.

### Q-G8. "Fixed versus variable — who decides, and is it even a property of the transaction?"
> The model decides, from rules embedded in the prompt: fixed means recurring or essential — rent, insurance, subscriptions; variable means discretionary — groceries, entertainment, shopping. It feeds the pie chart and the Fixed Costs metric card.
>
> And you're right that it's shaky, so let me not defend it too hard: fixed-versus-variable is a property of your *life*, not of the transaction. The same ₹5,000 to the same merchant is fixed for one person and discretionary for another. The model is inferring it from the merchant name and a rule of thumb. It's a useful default that will be wrong for individual rows — which is exactly why the category is editable in the table and the analytics recompute from the edited values.

---

## 5. Accuracy, evaluation, and generalization

### Q-A1. "What's the extraction accuracy?"
> I don't have a number. There is no test set, no labelled ground truth, and no evaluation harness in this project. I'm not going to invent a figure for you.
>
> What I have instead is a design that assumes it's imperfect: every cell in the results table is editable, rows can be deleted, and the analytics and all three exports recompute from whatever the user has corrected. Human-in-the-loop by construction.
>
> But I want to be clear-eyed — that's a **mitigation, not a validation**. It means errors are *correctable*; it doesn't mean I know how often they happen, and it quietly assumes the user will proofread, which for a fifty-row statement they mostly won't.
>
> [FILL: how many real statements have you personally run through this, and from how many different banks? Even "eleven statements from four banks, and I eyeballed the output against the PDF each time" is a real answer. Have it ready — "I don't have a number" is honest but it's much better with a floor under it.]

### Q-A2. "How would you build the eval if I gave you a week?"
> I'd keep it small and boring and I'd build it in this order:
>
> **The set.** Twenty to thirty statements — real ones plus synthetic — spanning as many banks and layouts as I can find, plus deliberate hard cases: a scanned paper statement, a multi-page statement long enough to blow the 8,000-character cap, a statement with a signed single-amount column instead of debit/credit pairs. Hand-label the transactions once. That labelling is the expensive part and there's no way around it.
>
> **The metrics**, in priority order:
> 1. **Transaction count recall** — did we get every row? This is the one that matters most, because a missing row silently reduces the total, and my two known failure paths both cause exactly that.
> 2. **Field exact-match** on date, debit, credit, balance. Amounts are pass/fail; there's no partial credit on money.
> 3. **Category accuracy** — a plain confusion matrix over the fourteen. I'd expect this to be the *weakest* number and I'd care about it *least*, because it's the one the user can trivially fix in the table and it doesn't corrupt the totals.
> 4. **Hallucination rate** — rows returned that don't fuzzy-match anything in the OCR text.
>
> **The split I'd insist on:** report OCR accuracy and LLM accuracy separately. Right now if a transaction is wrong I genuinely cannot tell you whether Tesseract misread the page or Gemini misparsed the text, and until I can, I don't know which half to fix. Feed clean ground-truth text straight to Gemini to isolate the model, and diff OCR output against known page text to isolate the OCR.

### Q-A3. "An unseen bank layout. Does it fail loudly or silently?"
> Both, depending on where it breaks, and the silent half is the problem.
>
> **Loud:** OCR recovers under 50 characters → hard error, "Could not extract text." HTTP 400 or 429 from Gemini → mapped error message. Those are fine.
>
> **Silent — and this is the honest answer to your question:** if OCR reads the page but garbles a column, or if Gemini misreads an unusual layout — say it maps a credit column to debit because the bank puts them in an order it hasn't seen — nothing in my pipeline notices. I have no validation layer. No balance-continuity check, no debit/credit sanity check, no confidence threshold. The wrong numbers flow straight into the analytics and out to Excel, formatted beautifully.
>
> The cheapest fix is one I keep coming back to: bank statements have a running balance, and a running balance is a **built-in checksum**. If `balance[n-1] - debit[n] + credit[n] != balance[n]`, something is wrong on row n — a misread digit, a swapped column, a missing row. I already extract the balance field. I do nothing with it. That's a self-validating property of the data sitting right there in my schema, and using it would turn most of the silent failures into loud ones. It's the single highest-value thing missing from this project.

### Q-A4. "Non-English statements? Non-Latin scripts?"
> Not supported. Tesseract is initialised with `'eng'` — English only, hard-coded. A statement in another script would OCR to garbage or to nothing, and if it produced under 50 characters it would at least error out cleanly rather than hallucinating.
>
> Tesseract.js supports other language packs, so it's a one-parameter change plus a language selector plus a bigger WASM download. Not hard, just not done.

---

## 6. Money handling (attack surface — the floats)

### Q-M1. "Show me how you represent an amount."
> The shared data contract is:
> ```json
> { "id": "txn_1719100000000_0", "date": "2024-01-15", "description": "AMAZON PAY",
>   "debit": 2499.00, "credit": null, "balance": 45000.00, "reference": null,
>   "category": "Shopping", "costType": "variable" }
> ```
> So amounts are JSON numbers, which in JavaScript are IEEE-754 doubles. Floats.

### Q-M2. "Floats. For money. Talk me through why that's a problem here specifically."
> Because binary floating point can't represent most two-decimal values exactly — the classic demo is `0.1 + 0.2 === 0.30000000000000004` — and `analytics.js` does exactly the operation that accumulates that error: `totalDebit` and `totalCredit` are simple sum reductions over the whole transaction array, and `netFlow` and `dailyBurnRate` are derived from those sums. Sum a hundred rows and the error compounds into the last cents.
>
> Concretely: the totals row in the Excel export can disagree with a hand-add of the column by a fraction of a currency unit, and the net cash flow figure can be off by cents. For an accountant reconciling against a bank balance, a total that's off by anything is a total that's wrong. It won't be off by rupees — but "small enough that nobody notices" is not a property you want in a financial tool. It's a property that *hides* the bug.
>
> The right representation is integer minor units — store paise or cents as integers, do all arithmetic in integers, and format to decimal only at the display and export boundary. JS integers are exact well past any plausible statement total. It's a contained change: the parse boundary in `gemini.js`, the arithmetic in `analytics.js`, and formatting in the three export paths.
>
> Why it isn't done: I didn't think about it, and rounding to two decimals at display time hides it well enough that it never announced itself. That's not a defence, it's just the truth.

### Q-M3. "Is it actually causing a visible bug today?"
> [FILL: check this. Load a real statement, and compare `totalDebit` against a hand-add of the debit column to full precision — log the raw float, not the rounded display value. If you find a real discrepancy, that is a *fantastic* answer: "yes, and here's the exact statement where the total came out 0.0000000004 off." If you don't, say "I haven't observed it in practice, but the representation makes it possible and I wouldn't ship a money tool on floats." Do NOT claim you hit this bug if you didn't.]

### Q-M4. "You have a `balance` field. What do you do with it?"
> Nothing. It's extracted, it's in the schema, it's in the exports, and no code reads it.
>
> Which — as I said on the layout question — is the biggest miss in the project. That field is a free checksum. Every bank statement's running balance encodes the arithmetic of every row: previous balance, minus debit, plus credit, equals current balance. A single validation loop over that would catch misread digits, swapped debit/credit columns, and rows dropped by the 8,000-character cap. It's the one place where this domain hands you ground truth for free, and I left it on the table.

---

## 7. The "10 seconds" claim

### Q-T1. "Ten seconds. On what?"
> I have to walk that back. The report contains no benchmark — no timing, no hardware, no page count. That number should not be on my resume as stated.
>
> And it's a number that *can't* be stated as a constant, because the dominant cost is Tesseract WASM running on the user's CPU. Nothing about that is fixed. It scales with page count — pages are OCR'd **in sequence**, so a five-page statement is roughly five times the OCR of a one-pager — and it scales with the user's machine. A desktop and a mid-range phone are not in the same order of magnitude. On top of that sits the Gemini round-trip, which depends on network and on Google's latency, and which is *bounded* by the 8,000-character cap: the model call doesn't grow with statement size past that point, only the OCR does.
>
> The right way to state it is a range with the variables named, not a point estimate.
>
> [FILL: actually measure it. You need: (a) pages, (b) resulting OCR character count, (c) OCR wall time, (d) Gemini round-trip time, (e) the machine — CPU and browser. Do it on a laptop and on a phone. Then say "a one-page digital PDF is about X seconds on an M1 MacBook — roughly Y in OCR and Z in the API call — and about N seconds on a mid-range Android." That answer wins the room. The current one loses it.]

### Q-T2. "Where's the actual bottleneck, and how would you speed it up?"
> Tesseract, almost certainly — it's the only CPU-bound stage and it's the only one that scales with document size. The Gemini call is capped at 8,000 characters of input, so it's roughly constant regardless of statement length. But I want to flag that this is **reasoning, not measurement** — I haven't profiled it.
>
> If it profiles as I expect, the fixes in order of effort:
> 1. **Parallelise OCR across pages.** Today `ocr.js` processes pages sequentially. Tesseract.js supports a worker pool — a four-page statement on a four-core machine could be close to the cost of one page.
> 2. **Downscale the canvas.** pdf.js renders each page at native dimensions, which for a 300-DPI scan is far more pixels than Tesseract needs. There's a resolution knee below which accuracy doesn't degrade and speed improves a lot; I've never looked for it.
> 3. **Overlap the stages.** OCR page 1, start the Gemini call, OCR page 2 — the network wait is dead time today.
>
> None of these are done, and I'd want the profile before I picked one.

---

## 8. Design decisions

### Q-D1. "Why no backend at all? A thin proxy would let you hold the API key and drop the setup friction."
> A proxy solves a real problem — first-run friction, where a user has to go get a Gemini key before they can do anything. That friction is genuinely the worst part of the product.
>
> And it costs me everything the project is for. A proxy means the OCR text now flows through *my* server. Which means I have logs, or I have to prove I don't. It means I'm holding a key that bills me, so now I need rate limiting, abuse prevention, and probably auth — and auth means accounts, and accounts mean a user database. One server turns a static file into a company. And the whole pitch — "I have no mechanism to receive your data" — becomes "trust my server," which is exactly the promise I said was worthless.
>
> BYOK means the deploy is a static `dist/` folder, hosting cost is zero, data liability is zero, and there's no rate limit for me to manage because the user's quota is the user's problem. I took setup friction over all of that, and I'd take it again. What I did to soften it: a direct link to Google AI Studio, and live key validation on entry so you find out immediately if the key is bad.

### Q-D2. "All state in App.jsx, useState. No Redux, no Zustand, no reducer. Justify."
> Because the state is small and the shape is simple: a status string, a transactions array, an API key, and a couple of booleans. Analytics aren't state — they're derived by pure functions in `analytics.js` from the transactions array, recomputed on change. There's no server cache to sync, no optimistic updates, no cross-tab coordination. Reaching for Redux here would be adding a state library to manage six variables.
>
> The honest caveat: it did bite me. The Add More bug in v1.3.0 was a state-machine collision, and a formal reducer with explicit transitions might have made it structurally impossible. So I'll say this — `useState` was right for the app I first built, and it started creaking the moment I added a second concurrent flow. If a third flow arrives, I'd move to `useReducer` before I'd move to a library.

### Q-D3. "Six status strings in a `useState` string. Why not a real state machine?"
> The states are `idle → reading → ocr → extracting → complete`, plus an `error` branch that can fire from anywhere. Sections render conditionally on that string.
>
> For a linear pipeline that's fine, and a string is the laziest thing that works. But the Add More bug is precisely a state-machine bug: a background process reached in and reset the global status, the results section unmounted because it only renders on `status === 'complete'`, and the user's transactions vanished from the DOM. A real state chart with declared transitions — or even just a discriminated union — would have made "you cannot go from `complete` to `ocr`" a type error instead of a Tuesday afternoon.
>
> My fix worked, but I'll admit what it is: a `updateStatus` boolean that lets one path opt out of the state machine. That's not a state machine, that's a state machine with a hole cut in it for the one case that didn't fit.

### Q-D4. "One shared transaction shape across the table, the analytics, and three export paths. Sell me on that."
> It's the thing I'd defend hardest in the whole codebase. There is exactly one transaction object shape, and the table, the analytics engine, the CSV writer, the SheetJS workbook, and the jsPDF report all consume it directly. No adapters, no per-export mapping layer.
>
> The payoff is concrete: adding a field propagates to every consumer for free, edits made in the table are automatically in all three exports because they're the same objects, and there's no class of bug where CSV and Excel disagree because two mappers drifted. When I added the Add More merge, appending to one array was the entire feature — every consumer just re-derived.
>
> The cost, honestly, is coupling: every consumer is welded to that shape, so a breaking change to it touches everything. At this size that's a trade I'll take all day.

### Q-D5. "html2canvas to get charts into the PDF. That feels like a hack."
> It is a hack, and it's the right one. jsPDF can't render SVG or React components, and Recharts produces SVG in the DOM. So the choice was: reimplement the charts a second time in jsPDF's primitive drawing API — two chart implementations to keep in sync forever — or screenshot the ones that already exist.
>
> html2canvas captures the live Recharts DOM nodes at 2× pixel density and hands back PNG data URLs to embed. The charts are guaranteed to be mounted at export time, because export is only reachable from the results screen where they're already rendered.
>
> The cost I accept: they're raster, so they don't scale in the PDF, and I get 2× density to make that acceptable at print size. Fine for a report someone reads or files. If it needed vector charts I'd have picked a different chart library — but I'd rather have one chart implementation and a raster export than two implementations and a divergence bug.

### Q-D6. "Five-sheet Excel. Why not one sheet with a filter?"
> Because the audience is an accountant or a small business owner, and they don't want a data dump, they want a document. Summary, Categories, Transactions, Fixed Costs, Variable Costs — that maps to how someone actually reviews spend: glance at the summary, look at where it went, then drill into the rows. Fixed and variable are split into their own sheets because that's the cut people act on — fixed costs are the ones you renegotiate.
>
> One sheet with a filter is what an engineer wants. Five sheets is what the user wants. SheetJS makes multi-sheet basically free, so there was no reason to make them do the work.

---

## 9. Hard cross-cutting questions

### Q-H1. "This is React, Tesseract.js, pdf.js, Gemini, SheetJS, jsPDF. What's *yours*?"
> Fair, and I'd rather answer it straight than pad. None of the heavy algorithms are mine.
>
> What's mine is every decision at a boundary, and in an integration project that's where the whole design lives:
> - The choice to OCR locally and send only text, which is the entire privacy architecture, and which I chose over the *easier* multimodal call.
> - BYOK, which deletes the backend and with it the hosting cost, the data liability, and the rate-limit problem.
> - The prompt that pins Gemini to a fixed fourteen-category schema so cross-statement aggregation is even possible.
> - The three-method JSON salvage — that's real engineering against a real failure mode: a model that stops mid-array and gives you a valid prefix of an invalid document.
> - The single shared data contract that makes five consumers work off one shape.
> - The analytics engine as pure functions, so everything recomputes from edited data for free.
>
> And I'd say the diagnosis in the Add More bug is mine too — tracing "my transactions disappear" back through a status reset to a conditional unmount to a stale closure is the actual work. The libraries did none of that.

### Q-H2. "Take away the LLM. Build the same product. What do you do?"
> I'd lose the thing that makes it work, so let me say what I'd lose first: zero bank-specific code. The LLM is what lets an unseen layout just work.
>
> Without it, the honest design is layout-aware parsing rather than text parsing. pdf.js gives you text items **with coordinates** — I'm currently throwing that away by rasterising to canvas and OCR'ing, which for a digital-native PDF is genuinely lossy: I'm converting structured text into pixels and then guessing the text back out. With coordinates you can cluster items into columns, detect the header row, classify columns by content (a column of parseable dates is the date column, a column of currency-shaped strings on the right is an amount column), and read rows off geometry. That works well and deterministically for digital PDFs, and it dies completely on a scanned image, where you'd fall back to OCR plus a per-bank template.
>
> Categorisation without an LLM is a merchant-name lookup table plus fuzzy matching — which is what most budgeting apps actually do, and it's fine for the top few hundred merchants and useless in the tail.
>
> The interesting bit: for digital-native PDFs, that coordinate approach might genuinely be *better* than what I built — more accurate, instant, free, and it needs no network call at all, which would make the privacy claim absolutely airtight. The strongest version of this product is probably a hybrid: coordinates when the PDF has a text layer, OCR-plus-LLM only when it doesn't. I'd build that next.

### Q-H3. "Ship this to a hundred thousand accountants. What breaks?"
> Nothing on my side, which is the point — it's a static bundle, it scales like any static file, and every user brings their own API quota, so there's no shared rate limit and no cost curve on me.
>
> What breaks is the *product*:
> 1. **Multi-page statements hit the 8,000-character cap and silently under-report.** An accountant with real statements finds this within a week and loses trust permanently. This is the one that actually kills it.
> 2. **The BYOK setup wall.** Ask a hundred thousand accountants to go get a Google API key and most of them close the tab. This is the conversion killer, and I don't have a good answer that doesn't reintroduce a backend.
> 3. **Google's free-tier rate limits** under real usage, which surface as my "Rate limit exceeded" message with no queue or retry behind it.
> 4. **Accuracy variance across banks that I cannot quantify**, because I never built the eval.
> 5. **Twenty client statements a week** means Add More, batch export, and probably persistence across sessions — none of which exist.
>
> If I had one week: chunk the OCR text to kill the cap, and add balance-continuity validation so errors become loud. Correctness before features.

### Q-H4. "Fifty-page statement. What actually happens?"
> Reasoning it through, since I haven't run it: pdf.js renders fifty canvases, Tesseract OCRs fifty pages **in sequence** — so the OCR is fifty times a single page and the tab is busy for a long time, though the Web Worker keeps the UI from freezing. Then the concatenated text — which will be far over the limit — gets **truncated at 8,000 characters**, so Gemini sees roughly the first page or two, and the user gets a table with a fraction of their transactions, no warning, and an analytics dashboard confidently reporting the burn rate of a partial statement.
>
> So: slow, then silently wrong. The slowness is annoying. The silence is the bug.
>
> [FILL: run it. Even a ten-page statement gives you a real number and a real screenshot, and turns this from reasoning into evidence. This is the highest-value hour of testing available to you.]

### Q-H5. "Two users, two files. Any cross-contamination?"
> No, and structurally there can't be. There is no shared state anywhere — no server, no database, no session store. Each user is a browser tab holding its own React state and its own `localStorage`. Two users are two isolated processes on two machines that never meet. That's a property I get for free from having no backend, and it's one of the underrated wins of the architecture.
>
> Within one tab, Add More deliberately *does* merge files — that's the feature — and results accumulate into the shared transactions array. There's no per-file provenance on a transaction, so once merged you can't tell which statement a row came from. That's a real limitation for the accountant use case, where you'd want to keep clients separate, and it's a `sourceFile` field away from being fixed.

### Q-H6. "Tests?"
> The report doesn't describe a test suite, and I'm not going to claim one exists.
>
> [FILL: state the truth. If there are no tests, say so and go straight to what you'd test first — that turns the answer around.]
>
> What I'd test first, in order, and why that order:
> 1. **`analytics.js`.** It's already pure functions over the transaction array — sums, groupings, date derivation — so it's free to test and it's where a silent numeric bug does the most damage. Including the float behaviour on money.
> 2. **The three-method JSON salvage in `gemini.js`.** It's the most intricate logic in the project and it exists specifically to handle malformed input, which is exactly what unit tests are good at. I'd feed it: clean JSON, fenced JSON, JSON with prose around it, JSON truncated mid-object, and JSON truncated mid-array — the last one being the case it was actually written for.
> 3. **The `updateStatus` / Add More flow**, because it's shipped a data-loss bug once already and a regression there loses the user's work.
>
> Notice what those three have in common: they're the places where a failure is *silent*. Rendering bugs announce themselves; a wrong total does not.

---

## 10. The bug you shipped and fixed (tell this one — it's your best story)

### Q-B1. "Tell me about a bug you shipped."
> v1.3.0 added multiple-file support — Add More, to combine several statements into one report. It shipped with a bug that was almost the worst kind: uploading a second file **replaced the first file's results entirely.** The user's already-extracted transactions just vanished from the screen.
>
> Data-loss-shaped, from the user's point of view. And it made the flagship feature of that release actively destructive.

### Q-B2. "Root cause. Precisely."
> A state-machine collision in `App.jsx`.
>
> The inner function `processFileInternal(file, updateStatus)` **always** set the global `status` state — that was correct and unremarkable for the first-file path. But Add More calls the same function while results are already on screen. So processing file two reset `status` from `'complete'` back to `'ocr'`. And the results section is conditionally rendered on `status === 'complete'` — so the moment status changed, React unmounted the entire results view. Every existing transaction disappeared from the DOM.
>
> The subtlety worth naming: the transactions were still *in state* at that moment. Nothing had been deleted. The data-loss *looked* like a data-loss but was actually a rendering consequence of a status transition — which is exactly why it took a minute to find. I went looking for where I was clearing the array, and I wasn't. The array was fine. The view was gone.

### Q-B3. "The fix."
> Two parts, and the second one is the one I'd want you to notice.
>
> **Part one:** a boolean parameter, `processFileInternal(file, updateStatus = true)`. The Add More path calls it with `false`, so the function runs its whole pipeline without ever touching the global status. `status` stays `'complete'`, the results view never unmounts. A separate `isAddingMore` boolean drives a non-destructive overlay banner, so the user still gets progress feedback — the feedback just doesn't destroy their screen to deliver it.
>
> **Part two, and this is the one that actually mattered:** snapshotting the existing transactions into a local variable at the top of the function.
> ```javascript
> const currentTransactions = [...transactions]
> ```
> Because `processFileInternal` is async and closes over `transactions`, the value it captured was from the render where it was created. Across the await boundaries of a multi-page OCR run, that closure goes stale — and merging new results against a stale array is a *second*, subtler way to lose the existing data. Part one fixed the symptom I could see. Part two fixed the bug I hadn't hit yet.
>
> The generalisable lesson: **a sub-process running inside an active state machine must not be allowed to drive that state machine.** The `updateStatus` flag is how I let one caller opt out. It works, and I'd still call it a patch — the structural fix is a state chart where "you cannot go from `complete` to `ocr`" is illegal by construction rather than by convention.

### Q-B4. "How did you find the stale closure? Did it actually bite you?"
> [FILL — this one matters. Did you hit the stale-closure bug in practice, or did you spot it while fixing the status bug and pre-empt it? BOTH are good answers and they're different stories: "I hit it, here's what I saw" is a debugging story; "I spotted it while fixing the first bug because I'd been burned by React closures before" is a judgement story. Tell the true one. Do not tell the debugging story if you didn't debug it.]

---

## 11. Closing

### Q-C1. "What would you do differently?"
> Three things, in order.
>
> **One: chunk the OCR text instead of truncating it at 8,000 characters.** That single line silently drops transactions from long statements, and every downstream number — the totals, the burn rate, the Excel — is wrong as a result, with no warning. It's the difference between a tool that fails and a tool that lies.
>
> **Two: use the balance column as a checksum.** I already extract it and I do nothing with it. Bank statements carry their own validation — previous balance minus debit plus credit equals current balance — and checking it would turn most of my silent failures loud. It's the highest-value missing feature and it's a loop.
>
> **Three: integers for money, not floats.** Minor units, formatted at the boundary. Correct by construction instead of correct-looking after rounding.
>
> All three are the same lesson, which is the one I'd want to take from this project: **in a financial tool, the dangerous failure isn't the one that errors — it's the one that returns a plausible number.**

### Q-C2. "What are you proudest of?"
> That the privacy property is **structural rather than promised.** I don't ask anyone to trust me, because I built a thing that gives me no capability to betray. There's no server, so there's no log; no database, so there's nothing to breach; no telemetry, so there's nothing to leak. It's not a policy that a future owner could rewrite — it's an architecture.
>
> And the part I actually had to choose: the multimodal call was *right there*. One API call, delete the whole OCR pipeline, better accuracy, less code. I didn't take it, because taking it meant uploading the user's bank statement. That was the fork where the project either meant something or didn't.
>
> I'll hold the line on how far that goes, though — the extracted text still goes to Google, and I've said so. What I'd claim is that I moved the trust boundary as far as I could without giving up the product, and I know exactly where I left it.

### Q-C3. "What's next?"
> Correctness first, and I'd resist every feature until it's done: chunk the OCR text, validate against the balance column, move money to integers, and surface truncation to the user instead of silently repairing it.
>
> Then the eval — twenty to thirty labelled statements across banks, with OCR accuracy and LLM accuracy measured *separately*, because right now I can't tell you which half is at fault when a row is wrong.
>
> Then the hybrid parser: use pdf.js's text layer with coordinates when the PDF has one, and fall back to OCR-plus-LLM only for scans. For digital-native PDFs that's faster, more accurate, free, and needs **no network call at all** — which would let me finally make the strong version of the privacy claim, honestly, for the majority of files.

---

## Cheat card — trigger → exact line to say

| They say | You say |
|---|---|
| "No data leaves the device?" | "The *file* doesn't. The extracted *text* does — to Gemini, under the user's own key. My resume bullet is imprecise and I'd fix the wording." |
| "Where's the Python?" | "There isn't any. That's an error on the bullet — it's React, Vite, and WASM Tesseract, no Python anywhere." |
| "100% private?" | "Structurally private from *me* — no server, no DB, no telemetry. Not private from Google, and I won't claim it is." |
| "Why not just send the PDF to Gemini?" | "One call, less code, probably more accurate — and it uploads your bank statement. Privacy over simplicity. That was the fork." |
| "10 seconds?" | "That number isn't benchmarked and shouldn't be stated flat — it's dominated by Tesseract on the user's CPU and scales with page count. [FILL: real range]" |
| "What's the accuracy?" | "I don't have a number, and I won't invent one. Every cell is editable — that's a mitigation, not a validation." |
| "8,000-character cap?" | "Transactions past the cap are silently dropped. That's the worst failure a money tool can have and it's the first thing I'd fix — chunk and merge." |
| "Truncated JSON salvage?" | "Three methods; the third stitches a cut-off response. 'Partial beats failure' is right for notes and wrong for money — it needs to warn the user." |
| "Floats for money?" | "Yes, and it's wrong. Sums drift in the cents. Should be integer minor units, formatted at the boundary." |
| "Unseen bank layout?" | "Zero bank-specific code, so it generalizes — but it can fail *silently*. The balance column is a free checksum and I don't use it. Biggest miss." |
| "What's actually yours?" | "The boundaries: OCR-local-send-text-only, BYOK, the pinned category schema, the JSON salvage, one shared data contract." |
| "Tell me about a bug." | "Add More wiped the first file's results. A background process reset the global status; the results view unmounted on the status change. Plus a stale closure underneath it." |
| "Tests?" | "[FILL: truth]. First three I'd write: analytics.js, the JSON salvage, the Add More flow — because those are the three that fail *silently*." |
| Anything you don't know | "I don't have that number. Here's how I'd get it." — never bluff a metric. |

---

## Prep priority

**Tier 1 — do not walk in without these (2 hours)**
1. **Fix the resume bullet.** Remove "Python." Remove "no data leaves your device." Remove or qualify "10 seconds." This is the single highest-value hour.
2. Rehearse Q-P1 (the outbound-call walk) until the concession is smooth and unhesitating. You must be the one who names it.
3. Own the 8,000-character cap (Q-O4) and the silent-truncation family (Q-G5, Q-A3). You get enormous credit for volunteering these; you get destroyed if the interviewer finds them.
4. Q-M2 — floats for money. Know why it's wrong and know the fix.

**Tier 2 — get these measured (one evening of actual work)**
5. **Benchmark the 10 seconds** (Q-T1). One page, five pages, laptop, phone. Real numbers.
6. **Run a long statement** (Q-H4) and watch the cap bite. Screenshot it.
7. **Count statements and banks tested** (Q-A1). Any floor beats "I don't know."
8. **Check the float drift** (Q-M3). If it's real, it's your best finding.
9. State the truth about tests (Q-H6).

**Tier 3 — polish**
10. The Add More bug story (Q-B1–B4) — this is your strongest engineering narrative. Confirm whether the stale closure actually bit you.
11. The no-LLM design (Q-H2) — the pdf.js coordinate approach shows real depth.
12. Q-C1/C2 — the "silent failure" principle. It's the line that lands.

---

## [FILL] list — everything the source could not tell me

| # | Where | What you must supply |
|---|---|---|
| 1 | Q-O3 | Have you actually run this on a phone photo / scanned paper statement? What happened? If you've only tested digital PDFs, say exactly that. |
| 2 | Q-O5 | How many characters does a real statement's OCR text come to, and how many transactions? This gives you the row count at which the 8,000-char cap bites. |
| 3 | Q-G3 | Did you compare Gemini Flash against Pro? If not, say you chose on cost + JSON mode and never benchmarked. |
| 4 | Q-A1 | How many real statements, from how many banks, have you run through it? |
| 5 | Q-M3 | Does the float drift show up in practice? Log the raw unrounded `totalDebit` against a hand-add. Do not claim you hit this bug if you didn't. |
| 6 | Q-T1 | **The benchmark.** Pages, OCR char count, OCR wall time, Gemini round-trip, machine (CPU + browser). Laptop and phone. This is the most important missing number. |
| 7 | Q-H4 | Run a long (10+ page) statement end to end. What actually happened? |
| 8 | Q-H6 | Are there any tests? State the truth. |
| 9 | Q-B4 | Did the stale-closure bug actually bite you, or did you pre-empt it while fixing the status bug? Both are good — tell the true one. |
| 10 | Resume | Is the "Python / no data leaves / 10 seconds" bullet already out on live applications? If so, prepare to concede it in the first breath. |
