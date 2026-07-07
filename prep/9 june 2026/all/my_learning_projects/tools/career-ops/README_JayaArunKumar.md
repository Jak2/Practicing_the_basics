# Career-Ops Setup — Jaya Arun Kumar Tulluri

Personal setup log for using career-ops as an AI job search pipeline.

---

## What Was Done

### 1. Resume Extracted → `cv.md`

Source PDF: `interview_prep/resume_prep/Jaya_Arun_Kumar_Resume_Ai_Engineer_Python_Developer.pdf`
(located at `/media/asterisk/windows_drive/project/learn/interview_prep/resume_prep/`)

Extracted and converted to `cv.md` in the career-ops root. This is the **canonical CV** the system reads for every evaluation, PDF generation, and cover letter.

### 2. PDF Extraction Tool → `my_learning_projects/tools/made_by_claude/pdf_to_md.py`

A reusable Python script to convert any PDF to Markdown using `pymupdf`.

```bash
# Install dependency once
pip install pymupdf

# Usage
python my_learning_projects/tools/made_by_claude/pdf_to_md.py <input.pdf> [output.md]
```

Claude Code auto-discovers this tool via the workspace-root `CLAUDE.md` at `/media/asterisk/windows_drive/project/learn/CLAUDE.md` — no need to mention it in future sessions.

### 3. Profile Created → `config/profile.yml`

Filled with Jaya's actual data:

| Field | Value |
|-------|-------|
| Name | Jaya Arun Kumar Tulluri |
| Email | jayaarunkumartulluri2@gmail.com |
| Phone | +91 80086 23789 |
| Location | Hyderabad, India |
| Timezone | IST (UTC+5:30) |
| Target roles | AI Engineer, Python Developer, LLM Engineer, Agentic AI Engineer |
| Availability | Immediate joiner |
| Comp target | ₹18L–30L per annum (India); $40–60K (international remote) |
| Comp minimum | ₹15L per annum |

**Still needs updating:**
- `portfolio_url` — add when available
- `github` — add GitHub profile URL
- `linkedin` — verify exact LinkedIn slug

### 4. Portal Scanner Configured → `portals.yml`

Configured based on Jaya's answers:

**Location strategy:** Remote globally + on-site/hybrid in Hyderabad only.

**Role title filters:** AI Engineer, LLM Engineer, Agentic AI, Python Developer, Backend Engineer, ML Engineer. Excludes Junior, Intern, Java, PHP, .NET, Blockchain etc.

**Tracked companies (28):**

| Category | Companies |
|----------|-----------|
| Global AI labs | Anthropic, OpenAI, Cohere, LangChain, Pinecone, Hugging Face, Mistral, Perplexity, Arize AI, W&B, Langfuse |
| Agentic / Automation | n8n, Zapier, Lindy |
| Dev Tools / AI Infra | Supabase, Vercel, Hightouch, Glean |
| Indian Fintech | Razorpay, PhonePe, Groww, Zerodha |
| Indian E-commerce | Flipkart, Swiggy, Zomato, Zepto, Blinkit |
| Indian SaaS / AI | Freshworks, Browserstack, Chargebee, Hasura, Sarvam AI, Krutrim |
| Global MNCs India | Microsoft, Google, Amazon, IBM, Accenture |

**Job board feeds enabled:** Remotive, We Work Remotely, Working Nomads, Himalayas, Jobicy.

### 5. Archetype Profile Created → `modes/_profile.md`

Copied from `modes/_profile.template.md` and customized with Jaya's strategy:

**Archetypes defined:**

| Archetype | Key proof point |
|-----------|----------------|
| Agentic AI / LLM Engineer | 5G remediation pipeline — LangChain + Vector DB + Redis |
| Python Backend / Automation Engineer | NFTRACE — FastAPI + Redis + Celery + SQLite |
| MLOps / LLMOps Engineer | LLM Evaluation Framework — 4 min vs 3 days |
| AI Solutions / Integration Engineer | NFTRACE telecom integration across Nokia CI/CD |

**Core narrative framing:** "AI engineer with systems depth" — not just LangChain usage but the infrastructure around it (Redis caching, gRPC gateways, Celery queues, K8s ops).

**Location scoring:**
- Remote (global): 5.0
- Hybrid Hyderabad: 4.5
- On-site Hyderabad: 3.5
- Hybrid other Indian cities: 2.5
- On-site outside India: 1.0

---

## Files Created / Modified

| File | Status | Purpose |
|------|--------|---------|
| `cv.md` | ✅ Created | Canonical resume — read by every evaluation |
| `config/profile.yml` | ✅ Created | Personal data, comp targets, location |
| `portals.yml` | ✅ Created | Scanner config — companies + job boards |
| `modes/_profile.md` | ✅ Created | Archetype strategy, framing, negotiation scripts |
| `my_learning_projects/tools/made_by_claude/pdf_to_md.py` | ✅ Created | PDF → Markdown tool |
| `/media/asterisk/windows_drive/project/learn/CLAUDE.md` | ✅ Created | Workspace root — Claude auto-discovers tools |

---

## Steps to Get Career-Ops Running

### Step 1 — Install dependencies

```bash
cd my_learning_projects/tools/career-ops
npm install
npx playwright install chromium   # required for PDF generation and portal scanning
```

### Step 2 — Verify setup

```bash
node doctor.mjs --json
```

Expected output: `{"onboardingNeeded": false, "missing": [], "warnings": []}` — all four required files (`cv.md`, `config/profile.yml`, `portals.yml`, `modes/_profile.md`) must be present. All four are now in place.

If anything shows in `missing`, see the **Files Created** table above for what to check.

### Step 3 — Check for system updates

```bash
node update-system.mjs check
```

If an update is available it will tell you. Your personal data files (`cv.md`, `config/profile.yml`, `portals.yml`, `modes/_profile.md`, `data/`, `reports/`) are **never touched** by updates.

### Step 4 — Create the applications tracker (if missing)

```bash
node doctor.mjs --json   # will flag if data/applications.md is missing
```

If missing, career-ops creates it automatically on first use. It looks like:

```markdown
# Applications Tracker

| # | Date | Company | Role | Score | Status | PDF | Report | Notes |
|---|------|---------|------|-------|--------|-----|--------|-------|
```

### Step 5 — Open Claude Code in the career-ops directory

```bash
claude
```

On first launch career-ops runs a silent update check and doctor check. If everything is green, you're ready.

### Step 6 — Start using it

**Evaluate a job (main flow):**
Paste any job URL or the full JD text directly in the chat → career-ops auto-detects it and runs the full pipeline:
1. Classifies the archetype (Agentic AI / Python Backend / MLOps / Solutions Engineer)
2. Scores the role A–F across 10 dimensions against your `cv.md`
3. Generates an ATS-optimized PDF CV tailored to that JD
4. Adds an entry to `data/applications.md`
5. Saves a report to `reports/`

**Available slash commands:**

| Command | What it does |
|---------|-------------|
| `/career-ops` | Show all available commands |
| `/career-ops {paste a JD or URL}` | Full auto-pipeline |
| `/career-ops scan` | Scan all 28 tracked companies + 5 job board feeds |
| `/career-ops pdf` | Generate ATS-optimized CV PDF for a role |
| `/career-ops cover` | Generate a cover letter |
| `/career-ops tracker` | View application pipeline status |
| `/career-ops pipeline` | Process pending URLs from `data/pipeline.md` |
| `/career-ops batch` | Evaluate multiple offers in parallel |
| `/career-ops deep` | Deep research on a company |
| `/career-ops interview-prep` | Generate interview prep guide for a role |
| `/career-ops patterns` | Analyse rejection patterns across applications |

### Step 7 — Set up recurring scans (optional)

Inside Claude Code, ask:
> "Scan for new offers every 3 days"

Career-ops will configure a recurring `/career-ops scan` using the `/schedule` or `/loop` skill if available, or give you a cron command to run manually.

### Pipeline integrity — run these periodically

```bash
node merge-tracker.mjs        # merge batch tracker additions into applications.md
node verify-pipeline.mjs      # health check — flags broken links, missing fields
node normalize-statuses.mjs   # fix non-canonical status values
node dedup-tracker.mjs        # remove duplicate entries
```

### Canonical application statuses

Use exactly one of these in `data/applications.md` — no bold, no dates, no extra text:

`Evaluated` · `Applied` · `Responded` · `Interview` · `Offer` · `Rejected` · `Discarded` · `SKIP`

---

## Smoke Test

Run this anytime you update the system, change config files, or want to verify everything is working.

### Quick smoke test (recommended — skips dashboard build)

```bash
cd my_learning_projects/tools/career-ops
node test-all.mjs --quick
```

### Full smoke test (includes dashboard binary build — slower)

```bash
cd my_learning_projects/tools/career-ops
node test-all.mjs
```

### What to expect

| Result | Meaning |
|--------|---------|
| `850 passed, 0 failed` | All good — system is healthy |
| warnings (yellow 🟡) | Non-blocking — expected local gaps like missing optional files |
| any `❌ failed` | Something is broken — check the output above the summary line |

**Last run result:** 850 passed, 0 failed, 15 warnings ✅

### Individual test files (run specific areas)

```bash
node test-salary-filter.mjs       # test salary filter logic
node test-trust-validator.mjs     # test job trust scoring
node tracker-columns-tests.mjs    # test tracker column format
node updater-migration-tests.mjs  # test system updater
```

### Doctor check (setup health, not code health)

```bash
node doctor.mjs --json
```

Expected: `{"onboardingNeeded": false, "missing": [], "warnings": []}`
This checks that your personal files (`cv.md`, `config/profile.yml`, `portals.yml`, `modes/_profile.md`) are all present — different from the smoke test which checks the system code itself.

---

## Setup Q&A — Answers I Gave During Configuration

**Where are you open to working?**
Remote anywhere + on-site/hybrid in Hyderabad only.

**Which types of roles should the scanner look for?**
AI / LLM / Agentic Engineer and Python / Backend Developer.

**Which company types are you most interested in?**
AI-native startups / labs, Indian product companies, Global MNCs with India offices, Remote-first global companies.

**Do you have a minimum salary expectation?**
₹15L+ per annum.

**For Indian product companies, which ones specifically?**
All categories — Fintech (Razorpay, Zerodha, PhonePe, Groww), E-commerce / Quick commerce (Flipkart, Swiggy, Zomato, Zepto, Blinkit), SaaS / B2B (Freshworks, Zoho, Chargebee, Browserstack).

**Should the scanner include global job board feeds?**
Yes — include Remotive, We Work Remotely, Working Nomads, Himalayas, Jobicy.

---

## Use Cases

> **Before any of these:** open a terminal, `cd` into `my_learning_projects/tools/career-ops`, then run `claude`. The `/career-ops` slash commands only appear when Claude is launched from inside this folder.

---

### 1. Evaluate a single job offer

You found a job posting. Paste the URL or the full JD text directly in the chat — no slash command needed.

```
https://jobs.ashbyhq.com/langchain/ai-engineer
```
or just paste the JD text. Career-ops will:
- Classify the archetype (Agentic AI / Python Backend / MLOps / Solutions Engineer)
- Score it A–F across 10 dimensions against your `cv.md`
- Flag gaps and strengths
- Generate a tailored ATS-optimised PDF CV
- Add a row to `data/applications.md`
- Save a full report to `reports/`

**When to use:** Every time you find a role worth considering.

---

### 2. Scan all tracked companies for new roles

```
/career-ops scan
```

Hits all 28 tracked companies (Anthropic, Razorpay, Sarvam AI, LangChain etc.) + 5 job board feeds (Remotive, Himalayas, We Work Remotely etc.) and finds roles matching your title filter. Zero tokens for ATS API checks — only uses AI when needed.

Results land in `data/pipeline.md` as a list of URLs ready for evaluation.

**When to use:** Run every few days to stay on top of new postings. Ask Claude to set up a recurring scan: *"scan for new offers every 3 days"*.

---

### 3. Process a batch of pending job URLs

You've collected several URLs in `data/pipeline.md` from scanning or manually saving roles.

```
/career-ops pipeline
```

Processes each URL one by one — evaluates, generates PDF if score ≥ 3.5, and adds to tracker. You review before applying to anything.

**When to use:** After a scan, or when you've been saving URLs to evaluate later.

---

### 4. Generate a tailored CV PDF for a specific role

```
/career-ops pdf
```

Takes your `cv.md` + the job description and produces an ATS-optimised PDF with keywords injected from the JD. Uses the Space Grotesk + DM Sans template in `templates/cv-template.html`. PDF lands in `output/`.

**When to use:** When you've decided to apply to a role and need a customised CV PDF.

---

### 5. Generate a cover letter

```
/career-ops cover
```

Or with a specific role slug:
```
/career-ops cover langchain-ai-engineer
```

Research-backed cover letter with keyword mirroring from the JD. Goes through a 4-angle interactive prompt (why this company / problems you'd solve / your approach / tone) before generating. You approve the draft before it's finalised.

**When to use:** Roles where a cover letter is required or would make a difference.

---

### 6. View your application pipeline status

```
/career-ops tracker
```

Summary of everything in `data/applications.md` — how many evaluated, applied, in interview, offers, rejected. Grouped by status with scores.

**When to use:** Weekly review of where you stand across all applications.

---

### 7. Deep research a company before applying or interviewing

```
/career-ops deep
```

Then paste the company name or URL. Career-ops researches: business model, funding, team size, tech stack, recent news, culture signals, and red flags. Helps you write a better cover letter and prepare better questions.

**When to use:** Before applying to any role scoring 4.0+, and definitely before any interview.

---

### 8. Generate interview prep for a specific company

```
/career-ops interview-prep
```

Given the company + role, generates:
- Likely interview questions (technical + behavioural)
- STAR stories mapped from your `cv.md` to their likely questions
- Company-specific talking points
- Questions to ask them

Saved to `interview-prep/{company}-{role}.md`.

**When to use:** As soon as you get an interview scheduled.

---

### 9. Compare two or more offers

```
/career-ops ofertas
```

Then paste 2–3 JDs or slugs. Side-by-side comparison across comp, role fit, growth, culture signals, and risk factors.

**When to use:** When you have multiple offers or are deciding which roles to prioritise applying to.

---

### 10. Evaluate a course or certification

```
/career-ops training
```

Paste the course name/URL. Career-ops scores it against your North Star roles — whether it fills a real gap in your profile or is just noise.

**When to use:** Before spending money or time on any certification or course.

---

### 11. Evaluate a portfolio project idea

```
/career-ops project
```

Describe the project you're thinking of building. Career-ops evaluates whether it would meaningfully strengthen your profile for your target roles or not.

**When to use:** When deciding what to build next to improve your candidacy.

---

### 12. Analyse rejection patterns

```
/career-ops patterns
```

Reads across all your `reports/` and `data/applications.md` to find patterns — which archetypes you're losing, which gaps come up repeatedly, which companies ghost vs respond.

**When to use:** After 10+ evaluations or applications, or if you feel like something isn't working.

---

### 13. Generate a LinkedIn outreach message

```
/career-ops contacto
```

Paste the person's name, role, and company. Generates a personalised, non-generic connection request or cold outreach message grounded in your background.

**When to use:** When reaching out to hiring managers or engineers at target companies before or after applying.

---

### 14. Batch evaluate multiple offers in parallel (advanced)

```
/career-ops batch
```

Or run headless workers directly:
```bash
claude -p "Evaluate this JD with career-ops auto-pipeline: https://company.com/jobs/123"
```

Runs multiple evaluations in parallel using sub-agents. Much faster than one by one when you have 5–10 URLs to process.

**When to use:** After a large scan surfaces many new roles and you want to clear them fast.

---

### How to launch correctly (critical)

```bash
# Always do this first — skills only load from inside the project folder
cd /media/asterisk/windows_drive/project/learn/my_learning_projects/tools/career-ops
claude
```

Type `/` to confirm `career-ops` appears in the slash command list before starting.

---

## Q&A — How to Use Career-Ops to Apply for Jobs

### Q: How do I use career-ops to apply for jobs?

End-to-end flow to apply for jobs with career-ops:

**1. Get a job in the pipeline**
- Paste a JD or job URL directly → runs full auto-pipeline (evaluate + report + PDF + tracker) automatically
- Or add URLs to `data/pipeline.md` and run `/career-ops pipeline` to process a batch

**2. Evaluation happens first (always)**
- Scores the role A-F against your CV/profile. Anything below 4.0/5 gets flagged, with a recommendation against applying.
- Produces a numbered report in `reports/` with a Legitimacy tier (checks the posting is real/live before you invest time).

**3. If it scores well, generate materials**
- `/career-ops pdf` — ATS-optimized CV tailored to that JD
- `/career-ops cover` — cover letter
- `/career-ops latex` — Overleaf-ready CV if you want to hand-tweak

**4. Fill the application**
- `/career-ops apply` — live assistant that reads the actual application form and drafts answers using only your `cv.md` / `article-digest.md` / profile (no fabrication). It **stops before hitting Submit** — you review and send it yourself, always.

**5. Track and follow up**
- Every evaluation auto-updates `data/applications.md` (tracker)
- `/career-ops tracker` — see status overview
- `/career-ops followup` — flags overdue applications, drafts follow-up messages
- `/career-ops patterns` — after enough rejections, analyzes what's not working

**Other useful modes:** `contacto` (LinkedIn outreach to find a warm contact), `deep` (company research before applying/interviewing), `interview-prep` (once you land an interview), `scan` (auto-discover new postings from tracked companies).

### Q: How can I automate this like a pipeline execution without user interaction?

Most of the pipeline can be automated, but one step is hard-blocked by design: **no application is ever submitted without the user reviewing it first.** This is a non-negotiable rule baked into the project config, not something that can be routed around.

**Fully automatable (no interaction needed):**
- **Scanning** — `scan` mode hits ATS APIs (Greenhouse/Ashby/Lever) directly, zero LLM cost, dedupes against `data/scan-history.tsv`. Can run unattended.
- **Evaluation pipeline** — feeding scanned/pipeline URLs through `auto-pipeline` (score + report + PDF + tracker update) runs headless, no prompts.
- **Batch mode** — `batch` spawns parallel headless workers (`claude -p "..."` or equivalent) to evaluate a queue of JDs at once, then `node merge-tracker.mjs` consolidates results.
- **Tracker maintenance** — `merge-tracker.mjs`, `normalize-statuses.mjs`, `dedup-tracker.mjs`, `verify-pipeline.mjs` are all deterministic scripts, no LLM/user needed.
- **Follow-up cadence** — `followup-cadence.mjs` computes what's overdue and can draft messages (drafting only, not sending).

**Scheduling it:** use the `/loop` or `/schedule` skill to run something like `scan` → `pipeline` on a recurring interval (e.g. every 3 days) so new postings flow in and get scored automatically while unattended.

**What stops for manual review every time, by design:**
- `apply` mode fills the form and drafts answers, but halts before Submit/Send.
- Anything scoring below 4.0/5 gets flagged, not auto-discarded silently — it still shows up in the tracker.
- No mass-blast application submission — that's explicitly against how this system is meant to be used (quality over volume).

So the realistic "hands-off pipeline" is: **scheduled scan → auto-evaluate → auto-generate CV/report/tracker entry**, with a manual pass at the end to pick which ones to actually apply to and hit submit.

---

## Key Metrics to Lead With (from cv.md)

- **70% auto-resolution** of 5G signaling errors (LangChain + Redis remediation pipeline)
- **55% MTTR reduction** (mean time to repair)
- **50% faster** pipeline validation (NFTRACE across Nokia CI/CD)
- **50+ weekly** Robot Framework keyword generations
- **25% improvement** in code quality scores (Python review checklists)
- **80% manual labor reduction** (network device config backup automation)

---

## Scheduled Agent — Autonomous Job Search Pipeline

`auto-scan-and-batch.sh` is a bash script that chains the full pipeline into a single command you can run manually or via cron. It was built as both a practical job search tool and a portfolio piece demonstrating agentic AI pipeline architecture.

### What it does (in order)

1. **Scan** — `claude -p "/career-ops scan"` → hits all 28 tracked companies + 5 job boards, dedupes against `data/scan-history.tsv`, writes new URLs to `data/pipeline.md`
2. **Extract new URLs** — reads `data/pipeline.md` and writes only new (unseen) entries to `batch/batch-input.tsv` with auto-incrementing IDs
3. **Batch evaluate** — `bash batch/batch-runner.sh` → spawns parallel headless Claude workers, one per URL, each producing a scored report + PDF + tracker entry
4. **Consolidate** — runs `node merge-tracker.mjs` (merges TSV additions into `data/applications.md`) then `node verify-pipeline.mjs` (integrity check)
5. **Log** — everything goes to `batch/logs/auto-run-YYYY-MM-DD-HH-MM.log`

### Run manually

```bash
cd my_learning_projects/tools/career-ops
./auto-scan-and-batch.sh
```

Flags:

| Flag | What it does |
|------|-------------|
| `--dry-run` | Scan only — no evaluation, no tracker writes |
| `--parallel N` | Number of parallel batch workers (default: 3) |
| `--min-score N` | Skip PDF generation for scores below N (default: 3.5) |
| `--retry-failed` | Re-run evaluations that failed in a previous run |
| `--resume-paused` | Resume a run that was interrupted mid-batch |

### Set up cron for recurring runs

Open crontab:
```bash
crontab -e
```

Add one of these lines — pick a cadence that fits your search intensity:

```cron
# Every 3 days at 8am (recommended for active search)
0 8 */3 * * cd /media/asterisk/windows_drive/project/learn/my_learning_projects/tools/career-ops && ./auto-scan-and-batch.sh >> batch/logs/cron.log 2>&1

# Every day at 9am (aggressive mode)
0 9 * * * cd /media/asterisk/windows_drive/project/learn/my_learning_projects/tools/career-ops && ./auto-scan-and-batch.sh >> batch/logs/cron.log 2>&1

# Weekdays only at 8am
0 8 * * 1-5 cd /media/asterisk/windows_drive/project/learn/my_learning_projects/tools/career-ops && ./auto-scan-and-batch.sh >> batch/logs/cron.log 2>&1
```

Save and exit. Verify cron picked it up:
```bash
crontab -l
```

### What you get after each run

- `data/pipeline.md` — updated with new URLs found this run
- `reports/` — one scored report per new role (format: `###-company-YYYY-MM-DD.md`)
- `output/` — ATS-optimised PDFs for roles scoring ≥ 3.5
- `data/applications.md` — tracker updated with all new evaluations
- `batch/logs/auto-run-*.log` — full run log for debugging

Then open Claude inside the project and run `/career-ops tracker` to review what came in. Pick the best-scored roles and proceed to `/career-ops apply`.

### Why this is a portfolio piece

This script is a working example of an **agentic AI pipeline** — the class of systems that most AI Engineer roles in 2025–2026 are asking candidates to have built:

- **Multi-step orchestration** with state handoff between steps (scan → extract → evaluate → consolidate)
- **Headless sub-agent spawning** (`claude -p` workers, one per job URL, in parallel)
- **ATS API integration** (Greenhouse/Ashby/Lever — zero-token direct API calls before involving LLMs)
- **Idempotent deduplication** (scan-history.tsv + merge logic means reruns don't create duplicate tracker entries)
- **Structured output pipeline** (TSV → merge-tracker.mjs → markdown table — typed handoff between agent and deterministic scripts)
- **Observability** (per-run logs, integrity checker after every run)

Frame it in applications: *"Built an autonomous AI pipeline that evaluates 28 companies + 5 job boards on a cron schedule, spawns parallel Claude sub-agents per offer, and consolidates scored reports into a structured tracker — demonstrating end-to-end agentic orchestration with structured I/O handoff."*

### Serving the immediate joiner situation

As an immediate joiner, speed of application matters. This pipeline means:
- New roles at Anthropic, Sarvam AI, Razorpay, etc. get evaluated within hours of being posted — no manual daily scanning
- Only roles scoring ≥ 3.5 surface for your attention, so you spend zero time on poor fits
- When you sit down to apply, the CV PDF and full evaluation report are already waiting
