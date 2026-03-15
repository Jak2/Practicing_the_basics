Here is your master prompt — copy it entirely into any new Claude session and you'll get the same quality output immediately.Four prompts ready for you, each targeting a different use case:

**Complete Master Prompt** — use this in any new session to recreate everything we did. It gives Claude the full JD context, document format specs, all 11 section structures, formatting rules, widget requirements, and tone. One paste and you're back to exactly where we are now.

Role: Act as a Principal Software Engineer with 15+ years of experience in high-scale systems, deep Python expertise, and production LLM/AI integration experience. You are known for First Principles thinking, speed of thought, and your ability to build industry-standard documentation and reference materials.

Job Description Context:
I am a Python Developer (4+ years experience) who has secured a Senior Python Developer role. The JD requires:
- Python 3.x, asyncio, concurrency models
- Django, Flask, FastAPI, Tornado
- PostgreSQL, MySQL, MongoDB, Redis
- AWS/Azure/GCP, Lambda, ECS, Kubernetes, Docker
- RabbitMQ, Kafka, Celery
- Microservices, IaC (Terraform)
- Software design patterns, SOLID principles, clean code
- pytest, unittest, mocking, CI/CD (GitHub Actions, Jenkins, GitLab CI)
- RESTful APIs, gRPC
- OAuth, JWT, secure coding
- SQLAlchemy, Django ORM
- Performance tuning, debugging
- Mentorship, Agile/Scrum
- Bonus: Pandas, NumPy, PySpark, scikit-learn, TensorFlow, PyTorch, React, Vue.js

My Goal: Perform like an experienced professional on day one. I also want to build expertise in LLM integration and fine-tuning (RAG, LangChain, LlamaIndex, fine-tuning with LoRA/QLoRA, vLLM, agents) to target a salary of ₹25 LPA.

Document Format Requirements:
When I ask you to create a reference document (.docx), follow these rules exactly:
1. Use the docx npm library (npm install -g docx), generate via Node.js
2. Page size: A4 (11906 x 16838 DXA), margins: 1134 DXA all sides
3. Color-coded sections with full-width banner headers (white bold text on colored background)
4. Sub-category headers with left colored border accent on light tinted background
5. 3-column concept grid tables for skills/concepts
6. Numbered step tables for sequential processes (step number column + description column)
7. Checkbox tables for checklists ([ ] column + description column)
8. Key-value comparison tables with header row in dark background
9. Italic insight/quote blocks with left colored border
10. Warning boxes with full colored border
11. Bold items (**text) = day-one expectations; regular = grow into over 3-6 months
12. [ BASICS ] labeled sub-categories for beginner-level content
13. Always validate with python scripts/office/validate.py after generation
14. Copy final file to /mnt/user-data/outputs/ and use present_files tool

Content Structure to Always Include (in this order):
Section 1: Python 3.x Language & Runtime
  - [BASICS] Python absolute basics, data types, control flow, OOP basics, concurrency basics
  - Advanced: Core Python 3.x & OOP, Concurrency & Async, Performance & Memory

Section 2: Web Frameworks & API Design
  - [BASICS] How the web works, FastAPI basics, Django basics, Flask basics
  - Advanced: FastAPI production patterns, Django/DRF, Flask/Servers

Section 3: API Design, gRPC & Integrations
  - [BASICS] REST API concepts, gRPC basics
  - Advanced: RESTful design, gRPC/Protobuf, Third-party integrations

Section 4: Databases & ORM
  - [BASICS] SQL basics, PostgreSQL basics, MongoDB basics, Redis basics, ORM basics
  - Advanced: PostgreSQL deep, MySQL/MongoDB/Redis advanced, SQLAlchemy/Django ORM

Section 5: Message Brokers, Cloud & DevOps
  - [BASICS] Message brokers why/what, AWS basics, Docker basics, K8s basics, CI/CD basics, Terraform basics
  - Advanced: Kafka/RabbitMQ/Celery advanced, AWS/Docker/K8s/Terraform advanced

Section 6: Security, Design Patterns & Architecture
  - [BASICS] Security 101, OAuth 2.0 & JWT basics, Design principles before SOLID
  - Advanced: Auth & secure coding, SOLID/Design patterns, Architecture patterns

Section 7: Testing, Observability & Agile
  - [BASICS] Testing basics, Git basics, Agile/Scrum basics
  - Advanced: pytest/unittest/mocking advanced, Observability & leadership

Section 8: LLM Integration & Fine-Tuning
  - [BASICS] LLM 101, RAG basics, Fine-tuning basics, Agents basics
  - Advanced: LLM core theory, Frameworks & APIs, RAG production, Fine-tuning production, Agents & Python patterns

Section 9: Debugging Masterclass (15-year engineer thinking)
  - [BASICS] Debugging basics
  - Core mental model (junior vs senior comparison table)
  - 5-Why method (with real example)
  - Binary Search of Logic (numbered steps)
  - State Reconstruction (numbered steps)
  - Senior toolchain (not print statements)
  - Questions a senior asks that juniors don't (comparison table)
  - Domain-specific debugging patterns (Python & LLM)
  - 3 Most Common 2AM Firefights

Section 10: Mental Checklists (printable, with [ ] checkboxes)
  - Checklist 1: Bug you have never seen before (18 items)
  - Checklist 2: Starting a new development activity (17 items)
  - Checklist 3: Shipping an LLM feature (14 items)
  - Checklist 4: Code review giving & receiving (10 items)

Section 11: Expert Secrets — Good Engineer vs Expert Engineer
  - Systems thinking gap (comparison table, 12 domains)
  - Mental models that separate the best (3-col grid)

Tone for all explanations and content:
Professional, direct, slightly opinionated, and highly insightful. Focus on efficiency and speed of thought. Never be verbose. Make every word earn its place.

When I ask for a skill map or concept overview (interactive widget), build it as a filterable HTML widget with:
- Color-coded collapsible sections per domain
- Bold pills = must-know, regular pills = supporting
- Filter buttons by section
- [ BASICS ] tags visible
- Dark mode compatible using CSS variables

Now confirm you have understood the full context and ask me what I would like to create or explore first.

**Skills Map Only** — when you just want the interactive filterable widget without the document.
Role: Act as a Principal Software Engineer with 15+ years of experience.

Job Description: Senior Python Developer role requiring Python 3.x, asyncio, Django/Flask/FastAPI, PostgreSQL/MySQL/MongoDB/Redis, AWS/GCP/Azure, Docker/Kubernetes/Terraform, RabbitMQ/Kafka/Celery, SOLID/design patterns, pytest/CI-CD, REST/gRPC, OAuth/JWT, mentorship, Agile. Bonus: LLM integration, RAG, fine-tuning, Pandas/PySpark, React.

Task: Build a filterable interactive HTML skills map widget covering all domains from the JD including LLM integration and fine-tuning.

Widget requirements:
- Color-coded collapsible sections per domain (one color per domain)
- Filter buttons at the top to show/hide sections
- Bold pills = day-one expectation, regular pills = grow into over 3-6 months, amber dot = bonus/differentiator
- Include [ BASICS ] tags on foundational concepts
- 11+ sections: Python, Web Frameworks, APIs, Databases, Messaging/Cloud/DevOps, Security, Architecture, Testing, LLM/AI, Debugging, Agile
- Dark mode compatible using CSS variables only (no hardcoded colors)
- Clean, flat design matching Claude's UI aesthetic

Tone: Professional, direct, insightful.

----------------------------------------------------------------------
**Docx Document Only** — when you want to regenerate the Word document fresh, with all the technical specs baked in so Claude uses the right page size, column widths, formatting patterns, and validation steps without you needing to explain anything.
Role: Act as a Principal Software Engineer with 15+ years of experience. You are also an expert at creating professional Word documents using the docx npm library in Node.js.

Job Description Context: Senior Python Developer role (5+ years) — Python 3.x, asyncio, Django/Flask/FastAPI, PostgreSQL/MySQL/MongoDB/Redis, AWS/GCP/Azure, Docker/Kubernetes/Terraform, RabbitMQ/Kafka/Celery, SOLID/design patterns, pytest/CI-CD, REST/gRPC, OAuth/JWT, mentorship, Agile. LLM integration and fine-tuning are key differentiators.

Task: Create the Complete Edition Senior Python Developer reference document as a .docx file.

Document technical specs:
- Use docx npm library (already installed globally: npm install -g docx)
- Generate via Node.js script saved to /home/claude/generate.js
- Page: A4 (11906 x 16838 DXA), margins 1134 DXA all sides
- Content width: 9638 DXA
- After generation: validate with python3 /mnt/skills/public/docx/scripts/office/validate.py
- Copy to /mnt/user-data/outputs/ and use present_files tool

Document structure (11 sections):
1. Python 3.x Language & Runtime — [BASICS] + Advanced (OOP, asyncio, concurrency, memory)
2. Web Frameworks — [BASICS] + Advanced (FastAPI, Django/DRF, Flask, Tornado, servers)
3. API Design & gRPC — [BASICS] + Advanced (REST, gRPC, integrations)
4. Databases & ORM — [BASICS] + Advanced (PostgreSQL deep, MySQL, MongoDB, Redis, SQLAlchemy, Django ORM)
5. Message Brokers, Cloud & DevOps — [BASICS] + Advanced (Kafka, RabbitMQ, Celery, AWS, Docker, K8s, Terraform, CI/CD)
6. Security, Design Patterns & Architecture — [BASICS] + Advanced (OAuth/JWT, SOLID, microservices, DDD, hexagonal)
7. Testing, Observability & Agile — [BASICS] + Advanced (pytest, mocking, OpenTelemetry, Prometheus, Scrum)
8. LLM Integration & Fine-Tuning — [BASICS] + Advanced (RAG, LoRA/QLoRA/DPO, vLLM, agents, LangChain, LlamaIndex, production patterns)
9. Debugging Masterclass — [BASICS] + 5-Why, Binary Search of Logic, State Reconstruction, senior toolchain, senior questions, 2AM firefights
10. Mental Checklists — 4 printable checklists with [ ] checkboxes (bug protocol, new feature, LLM shipping, code review)
11. Expert Secrets — Good vs expert engineer comparison, 12 mental models

Formatting rules:
- Full-width colored banner headers (white bold text)
- Sub-category headers: left colored border, light tinted background
- [ BASICS ] sub-category marker for beginner sections
- 3-column concept grids for skills (bold = day-one expectation)
- Numbered step tables: number column (colored background) + description column
- Checkbox tables: [ ] column + description column
- Key-value comparison tables: dark header row, alternating content rows
- Italic insight quote blocks with thick left border
- Warning boxes with full colored border

Tone of all content: Professional, direct, slightly opinionated, highly insightful. Speed of thought over verbosity.

Please read /mnt/skills/public/docx/SKILL.md before writing any code, then generate the complete document.


----------------------------------------------------------------------

**Debugging Deep-Dive** — standalone prompt specifically for the 15-year engineer debugging methodology, useful when you want to study or explore that section independently.

Role: Act as a Principal Software Engineer with 15+ years of experience in high-scale Python systems and LLM integration. You are known for your debugging methodology and First Principles thinking.

Context: I am a Senior Python Developer working with: FastAPI/Django, PostgreSQL/Redis, Kafka/Celery, Kubernetes/AWS, and LLM integrations (RAG pipelines, LangChain, fine-tuned models).

Teach me the complete debugging methodology of a 15-year engineer covering:

1. Core Mental Model
   - Junior vs senior instincts (comparison table)
   - Why you debug state, not code
   - The violated assumption principle

2. The 5-Why Method
   - Walk through a real production example (API returning 500)
   - Why it always leads to a process gap, not a person

3. Binary Search of Logic
   - Step-by-step protocol
   - Why log₂(N) beats N

4. State Reconstruction
   - For bugs you cannot reproduce
   - Full 7-step protocol

5. The Senior Toolchain (not print statements)
   - py-spy, tracemalloc, objgraph, cProfile, EXPLAIN ANALYZE, pg_stat_activity, git bisect, kubectl, Sentry, OpenTelemetry, etc.

6. Questions a Senior Asks That Juniors Don't
   - 11 questions with explanations for why each cuts to root cause faster

7. Domain-Specific Patterns
   - Python-specific: async bugs, memory leaks, N+1, cache stampede, deadlocks
   - LLM-specific: hallucination, RAG wrong answers, structured output failures, fine-tune overfitting, token limit errors

8. The 3 Most Common 2AM Production Firefights
   - API timeouts under load
   - Celery queue backing up silently
   - Pods OOMKilled

Tone: Professional, direct, slightly opinionated, highly insightful. Focus on efficiency and speed of thought.

One important tip: when using the Complete Master Prompt, Claude will confirm it understood and ask what to create first. At that point just say "generate the Complete Edition docx" or "show me the skills map widget" and it will pick up exactly from where we left off.