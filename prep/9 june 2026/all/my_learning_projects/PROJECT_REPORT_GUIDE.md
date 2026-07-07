# Project Report Writing Guide

> A reusable playbook for producing mixed-audience project reports — derived from the Bias & Fairness Auditor report (June 2026).

**Author:** Jaya Arun Kumar Tulluri
**Purpose:** Use this guide when creating a comprehensive project report for any new project.

---

## 1. Core Decision: The Layered Briefing Format

**Decision:** Use a single document structured as a "layered briefing" — plain English at the top, progressively technical further down.

**Why:** A single document serves all audiences (executives, compliance, engineers, recruiters) without maintaining two separate files. Each reader stops when the detail level exceeds their interest. A table of contents lets them jump directly to what they need.

**The alternative rejected:** Splitting into a non-technical brief + a technical reference. Rejected because it creates maintenance overhead and redundant context.

---

## 2. Standard 8-Section Structure

Use this section order for any software project report. Scale each section's length to the project's complexity.

| # | Section | Primary Audience | Target Word Count |
|---|---------|-----------------|-------------------|
| 1 | Executive Summary | Non-technical (executives, recruiters, compliance) | 150–200 words |
| 2 | Problem & Motivation | All | 300–400 words |
| 3 | How It Works — Plain English | Non-technical / general | 350–450 words |
| 4 | System Architecture | Engineers | 400–500 words |
| 5 | Core Technical Component(s) | Engineers | 500–700 words |
| 6 | Compliance / Standards Design (if applicable) | Compliance, legal | 250–300 words |
| 7 | Usage Guide | Engineers, practitioners | 300–400 words |
| 8 | Tech Stack & Key Design Decisions | Portfolio, recruiters, engineers | 300–400 words |

**Total target:** 2,500–3,500 words.

### What Each Section Must Cover

**Section 1 — Executive Summary**
- One paragraph: what the tool does, what problem it solves
- Key capabilities in plain English (no acronyms without expansion)
- Who uses it and in what context
- How it can be accessed (web UI, CLI, API, Docker)

**Section 2 — Problem & Motivation**
- The problem the project solves (with concrete real-world examples)
- Why existing approaches fall short
- Any regulatory, legal, or organisational pressure driving the need
- The specific gap this project fills

**Section 3 — How It Works (Plain English)**
- The core concept explained with an analogy a non-engineer would understand
- The main workflow steps in plain prose (no code)
- What the outputs mean (scores, verdicts, reports)
- What happens after the tool runs (next steps, artefacts produced)

**Section 4 — System Architecture**
- A module map table: `module path | one-line responsibility`
- An ASCII data flow diagram showing how data moves through the system
- The key data contract / central model that holds everything together
- Brief note on how the architecture enables extensibility

**Section 5 — Core Technical Components**
- One subsection per major analytical or processing component
- For each: what it measures/does, the algorithm or approach, the formula or metric, why this approach over alternatives
- A composite/aggregation section if components are combined into a final score

**Section 6 — Compliance / Standards Design**
- Which regulation or standard is targeted and why
- What the tool generates to satisfy it
- What the output artefact contains (enumerate the sections/fields)
- Known limitations explicitly documented

**Section 7 — Usage Guide**
- Prerequisites (install, configuration)
- Each usage mode with runnable example commands
- A table of built-in data, configs, or presets with descriptions
- What output artefacts are produced per mode

**Section 8 — Tech Stack & Key Design Decisions**
- Tech stack table: `Layer | Technology | Reason chosen`
- 4–6 non-obvious design decisions — decisions where the "why" is not obvious from the code
- For each decision: what was chosen, what was rejected, and why

---

## 3. Abbreviation Discipline

**Rule:** Every abbreviation is expanded on its **first use only**, in the form `Full Term (ABBR)`. After that, use the abbreviation alone. Never re-expand it later in the document.

**How to apply:**
- Decide in which section each abbreviation first appears.
- Write it expanded there. Use the short form everywhere else.
- In the final review pass, do a sweep to catch re-expansions and incorrect formats.

**Common abbreviations for technical project reports:**

| Abbreviation | Full form | Typically first used |
|---|---|---|
| LLM | Large Language Model | Section 1 |
| API | Application Programming Interface | Section 1 |
| CLI | Command-Line Interface | Section 1 |
| PDF | Portable Document Format | Section 1 |
| UI | User Interface | Section 3 or 4 |
| JSON | JavaScript Object Notation | Section 4 |
| ORM | Object-Relational Mapper | Section 4 |
| NLP | Natural Language Processing | Section 5 or 8 |
| ML | Machine Learning | Section 5 |
| CI/CD | Continuous Integration / Continuous Deployment | Section 8 |

Always expand domain-specific abbreviations (ANOVA, VADER, TF-IDF, etc.) on first use regardless of how well-known they are.

---

## 4. Tone Rules

- **Section 1–3:** Plain English. No jargon left unexplained. Write as if the reader has no technical background.
- **Section 4–5:** Technical. Use precise terminology. Engineers are the audience — don't over-explain basics, but do explain non-obvious design choices.
- **Section 6:** Plain-technical hybrid. Compliance audience understands their regulatory domain but not necessarily the engineering. Be precise about what the tool produces, avoid algorithmic detail.
- **Section 7:** Instructional. Commands must be copy-pasteable. Show real examples, not placeholders.
- **Section 8:** Portfolio-ready. "Why we chose X over Y" is more valuable than "we used X." Quantify where possible (e.g., "caps concurrent calls at 10").

---

## 5. Technical Accuracy Requirements

Every factual claim in the report must be verified against the actual source code. Before finalising, run these spot-checks:

- **Configuration values** (timeouts, thresholds, defaults) — check `config.py` or equivalent
- **Score formulas** — check the scorer/calculator module directly
- **File paths and module names** — verify they match the actual directory tree
- **CLI flags** — verify against the argument parser, not memory
- **Port numbers** — verify against docker-compose or server config
- **Database schema fields** — verify against the ORM model definitions
- **Output artefact structure** — verify against the generator/builder code

---

## 6. Final Review Checklist

Run this checklist before considering the document complete:

### Abbreviation Sweep
- [ ] Every abbreviation appears expanded on its first use in `Full Term (ABBR)` format
- [ ] No abbreviation is re-expanded in a later section
- [ ] No abbreviation appears for the first time in unexpanded form

### Technical Accuracy
- [ ] All configuration values (thresholds, defaults, limits) verified against source
- [ ] All score formulas verified against the scoring module
- [ ] All module paths match the actual filesystem
- [ ] All CLI commands are copy-pasteable and tested
- [ ] All port numbers match the deployment config
- [ ] Output artefact sections/fields enumerated match the generator code

### Structure
- [ ] Table of contents links work
- [ ] Each section has a clear heading at the right markdown level
- [ ] Each section ends with `---` (except the final footer)
- [ ] Footer present: `*Report generated: YYYY-MM-DD | Author: Name | Project version: X.Y*`

### Quality
- [ ] Total word count between 2,500 and 3,500
- [ ] No placeholder text (TBD, TODO, fill in later)
- [ ] No jargon in Sections 1–3 left unexplained
- [ ] Code examples in Section 7 are runnable as written
- [ ] Design decisions in Section 8 each explain "why X over Y"

---

## 7. Document Metadata Block

Every report opens with this block immediately after the title:

```markdown
# [Project Name] — Project Report

> [One-sentence description of what the project does]

**Author:** [Full name]
**Version:** [X.Y — Month YYYY]
**Project:** [Link or identifier]

---
```

And closes with this footer after the final section:

```markdown
*Report generated: YYYY-MM-DD | Author: [Full name] | Project version: X.Y*
```

---

## 8. Lessons from the Bias Auditor Report

These are non-obvious issues that came up during production of the first report using this format — worth knowing before you start the next one.

**1. The plan may contain inaccuracies about the code.**
The implementation plan is written before deep code reading. During writing, subagents should verify all numeric values and formulas directly against source files, and correct the plan's claims if they don't match the actual code. Accuracy to the code trumps accuracy to the plan.

*Example:* The plan listed a `length` weight of 15% as part of the composite scoring formula. The actual `bias_scorer.py` only uses four weights and the `length` key, while defined in `config.py`, is never referenced in the scoring calculation. The report correctly described the code's actual behaviour.

**2. Structural quality composites may not use all measured metrics.**
If a pipeline measures five metrics but only three feed into the final score, the report must say so explicitly. Listing all five metrics under "how the score is calculated" would be misleading.

**3. Re-expansion is the most common abbreviation error.**
The most frequent mistake is expanding an abbreviation again in a later section (e.g., spelling out VADER in Section 5 when it was already expanded in Section 3). Always do a document-wide sweep at the end.

**4. "Mode N — Full Term" headings re-expand abbreviations.**
Heading text like "Mode 2 — Command-Line Interface" re-expands CLI after it was expanded in Section 1. Use the short form in headings: "Mode 2 — CLI".

**5. Tech stack NLP entry format.**
The tech stack table entry for NLP should follow the same `Full Term (ABBR)` convention as the rest of the document: `Natural Language Processing (NLP)` not `NLP / Natural Language Processing`.

---

## 9. Process That Produced This Guide

This guide was derived from the following workflow, executed in Claude Code:

1. **Brainstorming** (`superpowers:brainstorming`) — explored the project, clarified audience (mixed), chose the Layered Briefing approach over a two-document split or README expansion.
2. **Spec writing** (`superpowers:brainstorming` continues) — produced `docs/superpowers/specs/YYYY-MM-DD-project-report-design.md` with per-section content blueprints.
3. **Plan writing** (`superpowers:writing-plans`) — produced `docs/superpowers/plans/YYYY-MM-DD-project-report.md` with one task per section, exact content, and verification checklists.
4. **Execution** (`superpowers:subagent-driven-development`) — dispatched one subagent per section; each wrote, verified, and committed. A reviewer subagent reviewed each diff before proceeding.
5. **Final pass** (Task 9) — abbreviation sweep, technical accuracy spot-checks, word count, fixes committed.

To reuse this process for a new project: run brainstorming with this guide as context, adapt the 8-section structure to the new project's domain, write a new spec with project-specific content per section, then execute via writing-plans + subagent-driven-development.
