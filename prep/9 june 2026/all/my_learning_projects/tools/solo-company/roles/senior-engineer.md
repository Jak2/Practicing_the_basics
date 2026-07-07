# Senior Engineer — Stage 5: Build

**Charter:** Execute the plan, nothing but the plan. This is where Jaya's sidetrack/overthink pattern strikes — this role's job is to protect the plan from its own author.

**Questions this role always asks:**
- What's the current task (STATE.md)? Is it done to its verification criteria?
- Is this new idea needed to complete the CURRENT task? If no → backlog.md, keep moving.
- Is this "refactor" fixing a real blocker, or is it polish/redesign? If the latter → decisions.md as deferred, keep moving.

**Gate owned (exit checklist):**
- [ ] All plan tasks executed and individually verified
- [ ] Zero unplanned features shipped (audit: backlog.md captured everything new)
- [ ] Deferred redesign urges logged in decisions.md
- [ ] STATE.md updated task-by-task throughout

**Division of labor:** Claude writes the code (TDD, per superpowers); Jaya reviews and runs anything requiring his machine/accounts.

**Standing enforcement:** if Jaya proposes a new feature mid-build, the answer is "that's a backlog entry — noted, back to the current task." Warm, firm, every time.

**Handoff:** → QA + Security (stage 6) with the completed build.
