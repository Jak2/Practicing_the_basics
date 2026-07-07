# Instructions — How to Build the Giant Interview Study Notes

This file is the spec to follow when generating the single master study-notes document from job descriptions + resume_prep. It merges: (1) my original request verbatim, (2) the "Choice B" optimized prompt, (3) gaps found during review that must be added on top of Choice B.

---

## 1. Original request (verbatim)

read all files in interview_prep/job_description folder except files in {interview_prep/job_description/Ibridge/study_guide-Ibridge_python_backend_developer, interview_prep/job_description/right_job.in/masterclass} and read my resume, project explanations and my notes etc that i prepared at interview_prep/resume_prep.
understand every skills expected, responsibility and write a notes on how it can be handled.

there will be points/concepts in the job descriptions that match the technology or points in the resume — keep them in one section and keep the non matched points in a separate section.

merge all the points from the job descriptions and prepare one giant single study notes. the notes should answer every concept, point, intent, every explanation etc from the job description — include if i missed anything. the giant file should not have duplicates. for the points or concepts in the job description consider as many questions needed/present to answer completely so that the points/concepts in job description are thoroughly explained without leaving any gaps. always crosscheck.

as per the content in resume_prep folder, ignore interview_prep/resume_prep/to_explain_interviewer folder and merge all the files from the resume_prep folder — do not merge the resume itself in resume_prep folder — and in a separate section give individual project explanation content focused for the ears of the interviewer. the explanation should be like a discussion rather than a question-to-answer, for all projects mentioned in resume.

Notes should read as if written by a human, in active voice.

---

## 2. Choice B (optimized prompt, verbatim)

**Objective:** Generate a single, comprehensive master study guide by analyzing job descriptions, resume, project documentation, and prep notes. Written in professional, human-like voice, active voice, direct language.

**Source scope**

- Job descriptions: all files in `interview_prep/job_description`, EXCLUDING `interview_prep/job_description/Ibridge/study_guide-Ibridge_python_backend_developer` and `interview_prep/job_description/right_job.in/masterclass`.
- Candidate profile: all files in `interview_prep/resume_prep`, EXCLUDING `interview_prep/resume_prep/to_explain_interviewer` and excluding the primary resume file from being merged verbatim into the notes.

**Execution requirements**

- Analyze every skill, responsibility, technical requirement across the JDs.
- Consolidate into one document, no duplicate concepts.
- Address every concept/point/intent in the JDs with comprehensive explanations, no gaps. Cross-check output against source files.
- Active voice throughout, natural expert-peer tone.

**Document structure**

- **Section 1 — Matched Skills and Technologies:** JD concepts that align with resume_prep skills/experience. Give actionable, real-world explanations of how to handle these responsibilities.
- **Section 2 — Gap Analysis / Non-Matched Concepts:** JD requirements/tools not in candidate profile. Deep-dive explanations, using as many breakdown questions as needed to fully cover the topic and close the gap.
- **Section 3 — Project Explanations for the Interviewer:** Merge project docs from resume_prep. Narrative, discussion-style breakdowns (not Q&A) covering architecture, execution, engineering decisions, for every project mentioned in the resume.

---

## 3. Gaps found in Choice B — must apply on top of it

These were identified reviewing Choice B against the original request and against a second opinion (ChatGPT). Keep the good parts, drop the bloat. Final rules to follow:

1. **Resume must be read, just never copied verbatim.**
   Choice B lists "the resume file" as an *exclusion*, same bucket as `to_explain_interviewer`. That's wrong — those two are different:
   - `to_explain_interviewer` → skip reading entirely.
   - resume → READ FULLY. Needed to (a) determine matched vs non-matched skills, (b) know every project to cover in Section 3.
   Only rule: never paste/merge resume text verbatim into the notes.

2. **resume_prep content is source material, not just a matching filter.**
   Pull the actual substance of the user's own resume_prep notes/explanations into Section 1/2 answers — don't just use resume_prep to decide "does this match," then write generic answers from scratch.

3. **Question-driven exhaustive coverage applies to BOTH sections, not just gaps.**
   Original says "as many questions as needed" for every JD concept. Choice B only attached this to Section 2. Apply it to Section 1 too — matched skills still need thorough explanation, not just a light "here's how to handle it."

4. **Semantic deduplication, not just literal-string dedup.**
   Merge concepts that are the same idea under different wording — e.g. "Redis" / "caching layer" / "distributed cache" / "performance optimization via cache" → ONE chapter (Caching), not four. Detect synonyms/variants before writing, not after.

5. **Merge-priority rule when resume tech ≠ JD tech.**
   E.g. resume says FastAPI, JD says Django. Don't create two isolated silos. Explain both, map the resume skill to the JD skill, cover the delta (what's different, what transfers directly, what needs fresh study).

6. **Depth scales with emphasis, not fixed length.**
   A skill repeated across many JDs / central to the role → deep coverage. A skill mentioned once, peripherally → concise coverage. No fixed "N paragraphs per topic" — depth follows how much the JDs actually emphasize it.

7. **Cross-reference instead of repeating.**
   If a topic (e.g. RBAC) is relevant under Security, Backend, and Microservices, explain it once in full, then reference it briefly elsewhere ("see Caching / RBAC section") instead of re-explaining it each time.

8. **Full-depth completeness checklist (why it exists, tradeoffs, production considerations, security, performance, testing, monitoring, common mistakes, when NOT to use it, real-world example) applies mainly to Section 2 (gap / unknown-to-user concepts).**
   For Section 1 (matched / already-known-to-user concepts), stay tighter: user's own experience + how to explain/handle it in an interview — don't pad with generic textbook material on things the user already knows from hands-on work.
   *(Explicitly rejected: applying this exhaustive checklist uniformly to every single concept regardless of match status — that produces generic bloat, not personalized notes.)*
   *(Explicitly rejected: multi-persona roleplay framing ("act as Staff Engineer + Hiring Manager + Coach + Writer + Architect simultaneously") — prompt theater, no material effect once the actual content rules above are followed.)*

---

## 4. Final execution checklist (what to actually do)

- [ ] Read all files in `interview_prep/job_description`, except the two excluded paths.
- [ ] Read resume fully (for matching + project list) — do not copy its text into the notes.
- [ ] Read all other files in `interview_prep/resume_prep`, except `to_explain_interviewer`.
- [ ] Extract every skill/responsibility/concept from all JDs; semantically dedupe (rule 4) before organizing into topics.
- [ ] For each topic, decide match status against resume_prep content — including delta-mapping for adjacent/different tech (rule 5).
- [ ] Write Section 1 (Matched): personalized, tied to user's actual experience/notes, question-driven, depth per rule 6, cross-referenced per rule 7.
- [ ] Write Section 2 (Non-matched / Gaps): full-depth completeness checklist per topic (rule 8), question-driven, depth per rule 6, cross-referenced per rule 7.
- [ ] Write Section 3 (Project Explanations for Interviewer): discussion-style narrative (not Q&A) for every project mentioned in resume, using resume_prep project docs as source.
- [ ] Final pass: crosscheck whole doc against all source files — confirm no JD concept was dropped, no duplicate chapters remain, active voice throughout, reads as human-written.
