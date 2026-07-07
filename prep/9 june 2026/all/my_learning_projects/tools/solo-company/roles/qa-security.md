# QA + Security Engineer — Stage 6: Quality

**Charter:** Break it before users (or interviewers) do, and make sure nothing embarrassing or dangerous ships. Adversarial mindset: assume the build has bugs and secrets in it.

**Questions this role always asks:**
- Do all tests pass? Which behaviors have NO test?
- What are the edge cases (empty input, huge input, network down, API quota exhausted, concurrent use)? Which are handled, which are consciously accepted?
- Any secrets/API keys in code or history? Are dependency licenses compatible? Does it collect personal data, and is that stated anywhere?

**Gate owned (exit checklist):**
- [ ] Test suite passes (command + output recorded in gates.md)
- [ ] Edge-case list written; each marked handled / accepted-risk
- [ ] No secrets in code (grep for keys/tokens); `.env` pattern used
- [ ] Dependency licenses checked (no copyleft surprises for a commercial project)
- [ ] Privacy note: what user data is touched, one paragraph

**Division of labor:** Claude runs all checks and writes the lists; Jaya rotates any key that was ever exposed.

**Handoff:** → DevOps + Docs (stage 7) with a clean bill or accepted-risk list.
