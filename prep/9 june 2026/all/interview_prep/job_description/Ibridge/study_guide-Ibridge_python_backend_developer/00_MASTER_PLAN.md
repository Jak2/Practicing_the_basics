# Interview Prep Master Plan — Senior Backend Python Developer (IBridge / Client)

**Interview:** Monday | **Today:** Wednesday 2026-06-18 | **Days available:** Thu, Fri, Sat, Sun (4 days)

---

## 1. The Role in One Sentence
A **strictly backend** Senior Python engineer who builds **scalable FastAPI REST APIs**, integrates them with **frontends (React/Next.js) and third-party services**, knows **SQL well** (PostgreSQL/MySQL/SQL Server), has **basic Snowflake** awareness, follows **Git + Agile + CI/CD** (Continuous Integration/Continuous Deployment), and **leverages AI tools to ship faster**.

## 2. What the Company Actually Wants (reading between the lines)
| JD phrase | What they're really testing |
|---|---|
| "strictly backend-focused" | Don't oversell AI/ML. Prove backend depth. |
| "scalable RESTful APIs using FastAPI" | Can you design clean endpoints, handle load, async? |
| "microservices + asynchronous processing" | Do you understand service boundaries, queues, async I/O? |
| "Authentication (JWT/OAuth)" | Can you explain token flows precisely? |
| "solid fundamentals in SQL" | Live SQL questions are very likely. Joins/aggregations/indexes. |
| "basic understanding of Snowflake" | Just don't be blank — know what it is and why it's different. |
| "collaborate with frontend (React/Next.js)" | API contract design, CORS, pagination, error shapes. |
| "leverage AI tools to improve efficiency" | They WANT you to use Claude/Copilot. Have a story. |
| "Agile, sprint planning, code reviews" | Behavioral: teamwork, reviews, mentoring. |

## 3. Your Positioning Strategy (memorize this)
> "I'm a backend Python engineer with 5+ years building production FastAPI services, async pipelines, and SQL-backed systems. Recently I've specialized in AI-integrated backends — but the core of my work has always been API design, database schema, performance, and reliability. I use AI tools daily to ship faster, which lines up exactly with how this team works."

**Pivot every AI story back to a backend skill:**
- 5G remediation pipeline → *async processing, Redis caching, vector DB integration, third-party data ingestion*
- gRPC (Google Remote Procedure Call) model gateway → *microservices, horizontal stateless scaling, multi-provider routing, service integration*
- NFTRACE → *FastAPI lifecycle endpoints, Redis session isolation, SQLite persistence, REST + RPC design*
- PSQL schema (RBAC — Role-Based Access Control, junction tables) → *relational schema design, data integrity, auth*

## 4. Four-Day Schedule
**THU — Core backend & FastAPI (your strength, lock it in)**
- AM: `01_FastAPI.md`, `02_Python_Backend.md`
- PM: `03_API_Integration_Auth.md` (JWT/OAuth)
- Eve: 20 rapid-fire Qs from `09_Mock_Questions_QA.md`

**FRI — Databases (highest ROI — likely live questions)**
- AM: `04_SQL_Databases.md` — practice writing queries by hand
- PM: `05_Snowflake.md` (just the essentials, 2 hrs max)
- Eve: SQL drills (write 15 queries from scratch)

**SAT — System design, DevOps & project defense**
- AM: `06_System_Design_Microservices.md`
- PM: `07_DevOps_CICD_Git.md`
- Eve: `13_The_Art_of_Explaining_Projects.md` (write the 6-beat Adventure Arc per project) + `10` (STAR) + `11_Project_Deep_Dive_Defense.md` index cards — rehearse out loud, timed under 90s

**SUN — Coding warm-up, revision & mocks**
- AM: `12` Part A coding warm-ups (8 problems + 1 FastAPI endpoint from memory), then full mock from `09_Mock_Questions_QA.md` (out loud, timed)
- PM: `08_Behavioral_HR.md` + `12` Part B hard questions + weak-spot review
- Eve: `12` Part D checklist, confirm logistics, print CHEATSHEET, sleep early

## 5. Interview-Day Logistics
- Confirm format (video/in-person), round structure, who you meet.
- Have ready: 2-min intro, 3 polished project stories, 3 questions to ask them.
- Salary/contract: it's a contract role via IBridge payroll — know your expected rate and notice period (you're an immediate joiner — that's a selling point, lead with it).
- UK shift: confirm you're flexible (JD requires it).

## 6. Questions to Ask Them (shows seniority)
1. "How is the backend split into services today — monolith moving to microservices, or already distributed?"
2. "What does the Snowflake integration look like — is backend reading from it, or feeding it?"
3. "What's the CI/CD and deployment setup — containers, where do APIs run?"
4. "How does the team currently use AI tools in the workflow?"
5. "What does success in the first 90 days look like for this role?"

---
**File index:** 01 FastAPI · 02 Python Backend · 03 Auth/Integration · 04 SQL · 05 Snowflake · 06 System Design · 07 DevOps/Git · 08 Behavioral · 09 Mock Q&A · 10 Resume Talking Points · 11 Project Deep-Dive & Decision Defense · 12 Coding Round/Hard Questions/Logistics · 13 Art of Explaining Projects (storytelling) · CHEATSHEET (print, glance morning-of)
