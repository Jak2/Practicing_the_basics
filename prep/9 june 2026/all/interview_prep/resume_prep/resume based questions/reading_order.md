# Reading Order — Interview is Monday

### interview_pack/ (study from these — your primary material)

| Order | File | When | Why |
| :--- | :--- | :--- | :--- |
| 1 | `6.EXPERIENCE_PROOF.md` | Thursday | 38 experience Q&As anchored in your real projects. This IS your prep. Most reps here. |
| 2 | `4.SQL_WITH_SOLUTIONS.md` | Friday | Highest risk — likely a live query. Cover, write, check. All 13. |
| 3 | `2.PROJECT_SCRIPTS.md` | Saturday | Your 3 projects, scripted + danger zones. Say each out loud under 90s. |
| 4 | `3.BEHAVIORAL_ANSWERS.md` | Sunday AM | "Tell me about yourself," hard HR questions, recovery scripts. |
| 5 | `7.JD_MASTER_GUIDE.md` | Sunday PM | One pass — read each JD line, cover answer, say it. The integration check. |
| 6 | `5.ONE_PAGE.md` | Monday morning | Glance only. No new learning. Confidence scan. |
| 7 | `1.TECHNICAL_ANSWERS.md` | If you have spare time | Reference only — use to reinforce weak spots from EXPERIENCE_PROOF. |

---

### study_guide/ (reference library — only go here when you need more depth on something)

| File | Go here if... |
| :--- | :--- |
| `01_FastAPI.md` | You're shaky on async/Depends/response_model after EXPERIENCE_PROOF |
| `03_API_Integration_Auth.md` | You want the full JWT/OAuth code + tenacity retry pattern |
| `04_SQL_Databases.md` | You want more SQL patterns beyond the 13 in interview_pack |
| `06_System_Design_Microservices.md` | You want the full ad-API design walkthrough (35-40 min practice) |
| `07_DevOps_CICD_Git.md` | You're weak on CI/CD, Docker, incident response |
| `08_Behavioral_HR.md` | You want more STAR story depth |
| Others | Skip unless you have extra time |

---

**The honest summary:** If you only have time for two files — `6.EXPERIENCE_PROOF.md` + `4.SQL_WITH_SOLUTIONS.md`. Everything else is upside.

---------------------------

# Interview Preparation Strategy

## Honest Answer First
You **DO** know things. You built NFTRACE, the 5G pipeline, Brane's RBAC schema. You ran production systems with real metrics. The problem isn't that you know nothing; it's that you used AI to build and don't remember the internals under pressure.

That's a different problem. And it's fixable in 3 days.

---

## Three-Day Execution Plan

If you have 3 days and feel blank, execute this exact timeline:

### DAY 1: Friday (4 Hours Max)

#### Step 1: FastAPI Experience Review (~30 Min)
* Read `EXPERIENCE_PROOF.md` Section 1 only (FastAPI).
* Close the file. 
* Answer Q1.1 out loud: *"Walk me through the most complex FastAPI service you've built."*
* **Target Answer Structure:** *"At Nokia I built NFTRACE; lifecycle endpoints, Redis session isolation keyed to UUID, SQLite persistence..."*
* Repeat this drill for every question in Section 1: **Read → Close → Verbalize**.

#### Step 2: SQL Execution (90 Min)
* Open `4.SQL_WITH_SOLUTIONS.md`.
* Cover the solution, write the query yourself, and check your work. 
* Complete all 13 queries. 
* **Critical Focus Queries:** #2, #3, #4, #6, #9. This is your highest-risk section due to the likelihood of a live query session.

### DAY 2: Saturday (4 Hours)

#### Step 3: Deep Technical Drills
* Open `EXPERIENCE_PROOF.md` Sections 2-5 (Async, Auth, DB, System Design).
* Use the same method: **Read → Close → Verbalize out loud**.

#### Step 4: Project Story Scripting
* Open `2.PROJECT_SCRIPTS.md`.
* Practice your 3 project stories out loud. 
* Time each story to keep it **under 90 seconds**.
* **Framework:** *What I built → What was hard → What I'd do differently.*

### DAY 3: Sunday (3 Hours)

#### Step 5: Final Content Review
* Review `EXPERIENCE_PROOF.md` Sections 6-10 (Integration, Frontend, CI/CD, Leadership, AI Tools).

#### Step 6: Integration Check
* Read through `7.JD_MASTER_GUIDE.md` in a single pass.
* Read each job description line item and verbalize your corresponding answer out loud to ensure no coverage gaps.

#### Step 7: Behavioral Alignment
* Open `3.BEHAVIORAL_ANSWERS.md`.
* Practice your *"Tell me about yourself"* pitch out loud 3 separate times.

#### Evening Routine
* Review `5.ONE_PAGE.md` only. 
* Rest.

---

## The 5 sentences that carry the whole interview

Memorize these 5 key sentences. They anchor your core technical narrative whenever you experience pressure:

1. **NFTRACE Core Architecture:** *"At Nokia, I built NFTRACE: FastAPI lifecycle endpoints, Redis session isolation, SQLite persistence. That drove a 50% reduction in pipeline validation time."*
2. **Data Pipeline Optimization:** *"The 5G failure pipeline auto-resolved 70% of failure events and cut MTTR (Mean Time To Resolution) by 55%, bringing remediation times down from hours to seconds."*
3. **Database Schema Design:** *"At Brane I designed the PostgreSQL schema, implementing attribute-level RBAC with junction tables for multi-agent execution alongside a stateless horizontal gRPC (Google Remote Procedure Call) model gateway."*
4. **Security Reality:** *"JWT is signed, not encrypted, meaning anyone can decode the payload in the browser. I've caught a team member putting PII in the token."*
5. **Role Alignment:** *"I'm a backend engineer (FastAPI, async, SQL) who integrates AI as a backend service. That matches the explicit requirements of this role."*

---

## When you blank in the room

Do not freeze. Deploy one of these recovery scripts:

* *"Let me think through that out loud..."* (Transition into first-principles reasoning rather than trying to recite documentation).
* *"I haven't used that specific tool directly. However, based on my experience with [related technology], I'd approach it by..."*
* *"Let me make sure I'm matching your intent; are you asking about X or Y?"*

> **Note:** A 3-second silence to gather your thoughts is acceptable. Faking expertise is not.

---

## Core Competency Checklist - What you actually need to survive each section

| Topic | Minimum Technical Baseline to Survive |
| :--- | :--- |
| **FastAPI** | Complete NFTRACE structural narrative + Async vs Sync execution + `Depends` injection patterns. |
| **Async** | 5G pipeline architectural story + Identifying and mitigating the event loop blocking-call trap. |
| **Auth** | JWT design constraints (Signed $\neq$ Encrypted) + BOLA mitigation + Brane RBAC schema layout. |
| **SQL** | Execute the 5 key patterns live while narrating your logical progression out loud. |
| **System Design** | The Ad-API pattern: `202 Accepted` status $\rightarrow$ message queue $\rightarrow$ worker pool $\rightarrow$ cache layering $\rightarrow$ database fallback. |
| **Snowflake** | Understanding OLAP vs OLTP clear distinctions + Honest response: *"Working knowledge, ramps quickly."* |
| **Behavioral** | Confident *"Tell me about yourself"* pitch + 1 structured failure story + Explaining exactly why this role fits. |