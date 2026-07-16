# Forward Deployed AI Engineer (Telesat / Infomatics Corp) — Interview Question Bank

**Role:** Forward Deployed AI Engineer — deploy AI into End-to-End System Test Automation. Remote. Contract via Infomatics, deployed to Telesat (LEO satellite operator, Lightspeed network).
**Rounds:** Screening (TA) → Technical 1 (payroll/Infomatics) → Technical 2 (client/Telesat) → Manager.
**Companion docs:** your project Q&As in [../../resume_prep/](../../resume_prep/) — pull concrete evidence from those.

**What this JD is really testing:** *not* a research ML engineer. Someone who takes flaky AI prototypes and hardens them into tools that test engineers trust and adopt, inside a messy existing framework, working directly with the users. Breadth + production discipline + guardrails > deep model theory.

**Your through-line (repeat it every round):** "For four years I embedded LLMs into 5G test automation at Nokia — tools engineers actually adopted into their Robot Framework workflow — and at Brane I built the guardrails that make AI safe inside a production system. Prototype → trusted production tool in a real engineering environment is the thread through my whole résumé."

---

## ROUND 1 — SCREENING (recruiter, non-technical). Test: fit, years, communication, interest, logistics.

1. Walk me through your background in 2–3 minutes. → *Lead with the through-line, not chronology. Frame yourself as "AI-in-test-automation engineer."*
2. Why are you interested in this Forward Deployed Engineer role? → *Embedded with users, hardening AI, no spec — say you enjoy exactly that.*
3. What do you understand a Forward Deployed Engineer does? → *Deployed next to the user; prototype→production; judged on adoption, not cleverness.*
4. What's your experience with AI / LLMs in a real work setting? → *RF Keyword Generator: adopted, 50+ generations/week. 5G failure pipeline.*
5. Do you have test automation experience? → *Robot Framework at Nokia — your RF generator outputs RF keywords. You're already in their domain.*
6. This is deployed to a client (Telesat) — are you comfortable being embedded with a client team? → *Yes; you did exactly this at Nokia-Ext via Infinite.*
7. Are you comfortable with a fully remote role?
8. What's your current notice period / availability? → *Know this cold.*
9. What are your salary expectations? → *Have a researched range ready.*
10. Why are you leaving / why did you leave your last role? → *Brane was 2 months — have the clean, non-bitter one-liner ready (see BRANE Q&A Q1).*
11. What do you know about Telesat / satellite networks? → *LEO, Lightspeed, fiber-like speed, low latency vs GEO. One informed sentence.*
12. Do you have any questions for us? → *Always yes. Ask about the test-automation stack, team size, what "prototype" exists today.*

---

## ROUND 2 — TECHNICAL 1 (Infomatics/payroll side). Test: can you actually engineer. General AI + Python + your projects.

### Agentic AI (JD calls this out explicitly)
13. What is agentic AI, versus a plain LLM call? → *Loop: model plans, calls tools, observes results, iterates toward a goal — not one-shot. Brane = your proof.*
14. Explain an agent loop you've built. → *Brane AgentLoopController: assemble → invoke → parse → verify → retry-with-feedback.*
15. What is tool-calling / function-calling, and why does it matter? → *Agent acts on the world through a whitelist of defined tools. Brane tool registry, grant-checked.*
16. What is the ReAct pattern? → *Reason + Act interleaved: think, act, observe, repeat.*
17. How do you keep an agentic loop from running forever? → *Hard iteration cap + fallback. Brane: default 5, then transition to fallback.*
18. How would you "tune AI behavior based on real test outcomes and failure analysis"? *(near-verbatim JD line — prep a concrete example)* → *Brane verifier correction loop: failure report fed back into next prompt. 5G: confidence routing tuned from match scores.*
19. When is an agent the wrong tool, and a simple deterministic script the right one? → *Ponytail instinct: don't reach for an agent when a rule works. Shows production judgment.*

### Prompt engineering & AI troubleshooting (JD: "tuning prompts/instructions", "strong troubleshooting of AI behavior")
20. Walk me through how you debug a prompt that's producing wrong output. → *Inspect actual model input (verbose), isolate the failing case, change one thing, re-test. 5G: LangChain hides the prompt — you used verbose mode.*
21. System prompt vs. user prompt vs. few-shot — when each? 
22. How do you handle an LLM returning malformed JSON? → *Brane: malformed = a failed attempt, not a crash — feeds the retry loop. RF gen: deterministic template + parser after the LLM.*
23. How do you stop a model treating injected data as instructions (prompt injection)? → *Delimited data blocks, schema-validated output, tool whitelist. Contain, not just detect (Brane Q29).*
24. What are hallucinations and how do you reduce them in production? → *Grounding (RAG), abstention thresholds, advisory-not-executing. 5G: 0.65 threshold, human executes.*
25. How do you make LLM output *consistent* run to run? → *Low temperature, structured output, pinned model. 5G: temp 0.1.*

### RAG & LLM systems (your 5G pipeline is the anchor)
26. What is RAG and when do you use it over fine-tuning? → *Knowledge changes constantly → re-index vs retrain; provenance; cheaper. 5G pipeline.*
27. Explain semantic search. → *Match by meaning not keywords; embed + cosine similarity. "T3560 timeout" matches "NAS authentication timeout".*
28. Why a vector database over SQL for retrieval? → *Similarity, not exact match. Qdrant + metadata filter.*
29. How do you evaluate LLM output quality systematically? → *Golden set + regression harness. Your LLM Eval Framework + Prompt Regression Suite are literally this.*
30. How do you detect when an LLM has regressed after a prompt or model change? → *Prompt Regression Suite. Bridge to it.*

### Python orchestration (JD: "orchestration, integration, control logic across systems")
31. How do you structure a Python pipeline that integrates multiple systems? → *NFTRACE, 5G pipeline: stage modules, one data contract, decoupled.*
32. Sync vs async in Python — when do you reach for asyncio? → *I/O-bound concurrent LLM/API calls. Bias Auditor: asyncio.gather + semaphore.*
33. How do you cap concurrent API calls to avoid rate limits? → *asyncio.Semaphore. Also: partial rate-limiting biases your sample (Bias Auditor).*
34. How do you handle errors and retries in an integration script? → *Retry with backoff, fail loud on unrecoverable, never proceed silently on partial data (NFTRACE lesson).*
35. Generators, memory management on large data? → *5G: keep_packets=False, streaming iteration, constant memory.*
36. Walk me through calling the Anthropic/OpenAI SDK and handling the response. → *Know the basic message-create shape, streaming, tool use.*

### Deep-dive on YOUR projects (they'll pick one and drill)
37. Explain your 5G failure detection pipeline end to end. → *Full answer bank in [5G_Pipeline_Interview_QA.md](../../resume_prep/5G_Pipeline_Interview_QA.md).*
38. Explain the Brane AI agent runtime and the guardrails. → *[BRANE Q&A + Story](../../resume_prep/BRANE/). "Probabilistic core, deterministic gate."*
39. Explain the RF Keyword Generator — most relevant to THIS role. → *LLM → deterministic RF templates → parser validation → regex fallback for 100% uptime. AI in test automation, adopted.*
40. What was the hardest bug across these, and how did you find it? → *5G vendor black hole, or RF brace-escaping. Symptom→assumption→cause→fix→prevention.*

---

## ROUND 3 — TECHNICAL 2 (Telesat/client). Test: domain fit — test automation, networking, deployment, safety-critical judgment.

### Test automation & prototype→production (the core of the role)
41. What does "system test automation" mean to you? → *Automated end-to-end validation of a system against requirements; frameworks, CI, deterministic checks.*
42. Tell me about a time you took an AI prototype to production. → *RF Keyword Generator: demo → adopted daily by the team. STAR.*
43. A prototype works 70% of the time. Walk me through hardening it to production. → *The unglamorous 30%: error handling, edge cases, fallback, guardrails, monitoring. RF gen regex fallback = exactly this.*
44. How would you integrate an AI tool into an existing test framework you didn't build? → *Learn the workflow first, add at a seam, don't rewrite. Single delegation point (Brane). FDE listening.*
45. How do you get test engineers to actually trust and adopt an AI tool? → *Show its work (provenance/source docs), let it abstain, keep it advisory first. 5G: return_source_documents.*
46. How would you add validation layers / guardrails around an AI tool in a safety-critical config? *(near-verbatim JD)* → *Deterministic gate on probabilistic output. Brane verifier lane. "The thing that generates must not certify."*
47. How do you tune AI behavior based on test failures? → *Feedback loop; failure analysis → prompt/threshold adjustment. Brane correction loop.*
48. How would you evaluate a new AI tool (e.g. Qodo) for use in system test? → *Define success metric, test against real workflows/data, measure adoption + failure modes, feed back to platform team. FDE = platform feedback loop.*
49. What guardrails/documentation would you write so engineers use AI *responsibly*? → *Usage patterns, known failure modes, where NOT to trust it, abstention behavior. JD: "enablement, documentation, guardrails."*

### CI/CD, Linux, Docker, Kubernetes (JD preferred)
50. How do containers help deploy an AI tool? → *Reproducible env, no "works on my machine," Qdrant/FastAPI/Streamlit each containerized (5G).*
51. Difference between a Docker image and a container? A pod and a deployment?
52. How would you fit an AI validation step into a CI/CD pipeline? → *A gate stage; Prompt Regression Suite catches breaking prompt changes before merge.*
53. Common Linux commands you use daily? Log inspection, process/port checks? → *grep/journalctl/ps/ss/tail.*
54. How do you handle secrets (API keys) in a deployed AI service? → *Env/secret store, never in image or repo. You already redact .env.*

### Networking fundamentals (JD preferred: TCP/IP, MPLS, gNMI, YANG) — define, don't overclaim
55. Explain TCP/IP basics. → *You have real depth: 5G signaling, Diameter, NAS/NGAP. Lead with that.*
56. What is MPLS at a high level? → *Label-switched forwarding, faster than per-hop IP lookup. Define + "willing to go deeper."*
57. What are gNMI and YANG? → *YANG = data model for network config; gNMI = gRPC-based protocol to get/set that config on devices. You know gRPC (Brane model gateway) — bridge from there. Don't claim hands-on YANG; say "strong network-protocol background, comfortable picking these up fast."*
58. Your 5G background — how does it transfer to satellite/LEO test automation? → *Signaling, protocol validation, test frameworks all transfer; the medium changes, the discipline doesn't.*

### Scenario / systems-thinking
59. An AI test tool starts giving subtly wrong results in production. How do you debug it? → *Reproduce, isolate, check if it's model drift vs prompt vs data. Systematic debugging.*
60. A test engineer says "the AI tool is wrong" but can't say how. How do you extract the real failure? → *FDE core skill: sit with them, watch the failing case, get the concrete example. Half the job is listening.*
61. How would you monitor an AI tool running in a test pipeline? → *Adoption rate, abstention/no-match rate, latency, cost, failure-by-type. 5G: unknown_errors growth = health signal.*
62. How do you handle non-determinism when the tool is used inside a deterministic test suite? → *Pin temperature, structured output, treat variance explicitly. This is the flakiness problem — Prompt Regression Suite territory.*

---

## ROUND 4 — MANAGER. Test: ownership, ambiguity, collaboration, judgment, staying power.

63. Tell me about a time you worked with no clear spec / high ambiguity. → *Nokia: no requirements — watched engineers waste hours, built the fix. FDE trait.*
64. Tell me about working directly with the end users of something you built. → *RF gen / 5G pipeline adoption; iterated with the ops team.*
65. Describe a cross-team collaboration (test + dev + automation owners). → *Nokia multi-vendor testing; Brane on a large existing platform, owned your slices.*
66. Tell me about a project that failed or a decision you got wrong. → *Have a real one. Growth, not blame.*
67. How do you decide when something is "good enough to ship" vs needs more work? → *Ship the lazy-correct version, iterate with the user; don't gold-plate. FDE pragmatism.*
68. A stakeholder wants AI to do something you think is unsafe/unreliable. How do you handle it? → *Brane: you rejected the self-certifying model on principle. Say no with a reason and an alternative.*
69. How do you keep learning / stay current with fast-moving AI tooling? → *Concrete: you build eval tooling, you try new frameworks (name a couple honestly).*
70. Brane was short (2 months). Talk me through that. → *Clean, non-bitter one-liner. Pivot to the dense real work.*
71. Why this role, why now, and where do you want to grow? → *FDE is the intersection of your AI + test-automation + production-hardening experience.*
72. What questions do you have for me? → *Ask about: the current AI prototypes, the biggest test-automation pain, how success is measured for this FDE in 6 months, team structure.*

---

## Honesty guardrails (all rounds)

- **Don't lean on the unverified resume claims** we flagged (Redis on 5G, "Stack: Python"/pytest on some projects, the 50% figures, "regulatory-grade"). This role is won on the RF Generator + Brane guardrail story — both solid. Keep it truthful; the technical rounds will test whatever you say.
- **gNMI/YANG:** define them, don't claim hands-on. "Strong network-protocol background, comfortable going deeper" is credible from your 5G work. Overclaiming here is easy to catch.
- **Brane = 2 months.** Own the scope: "I own my slices, I understand the whole design."
- **Adoption is your strongest card.** The RF generator was *actually used* — 50+ generations/week. That's the single most on-target proof for an FDE role. Lead with it in every technical round.

## The 6 questions to over-prepare

1. "Tell me about taking an AI prototype to production." → **RF Keyword Generator.** Your killer story for this JD.
2. "What is agentic AI / explain an agent loop you built." → **Brane.**
3. "How do you make engineers trust an AI tool in a safety-critical setting?" → **Guardrails / probabilistic-core-deterministic-gate.**
4. "How do you tune AI from failure analysis?" → **Correction loop + confidence routing.**
5. "Why FDE, and what does the role mean to you?" → **Embedded, adoption-driven, prototype→production.**
6. "Your 5G/telecom background vs satellite — does it transfer?" → **Discipline transfers; medium changes.**
