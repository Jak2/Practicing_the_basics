**Correctness signals that don't equal quality:**
- Runs and passes the one example you tried, but no test coverage for edge cases (empty input, null, boundary values)
- Works for the happy path but silently mishandles errors (broad `except:` blocks, swallowed exceptions)
- No input validation on external data (API responses, user input, file content)

**Structural smells:**
- `Duplicated logic instead of a shared function` — AI tools often regenerate similar blocks rather than reuse
- `Inconsistent patterns within the same file` (different error-handling styles, naming conventions across functions)
- `Functions doing more than one job` — making the "what does this do" answer take more than one sentence

**Dependency/API risk:**
- `Calls to library methods or endpoints you can't personally confirm` exist in the current version — AI tools confidently invent plausible-looking method names. You have to check the docs, not trust that it compiles-in-your-head.
- `using unrelated library` that are not related to project structure
- Hardcoded values (API versions, model names, config) that should be parameterized

**Security/safety:**
- `Secrets or credentials inlined` instead of pulled from env vars
- `SQL/queries built via string concatenation instead of parameterization`
- `No rate-limiting or timeout on external calls` that could hang or get abused

**Maintainability:**
- No comments explaining *why* a non-obvious choice was made (AI code tends to comment *what*, which the code already shows)
- Magic numbers with no named constant
- Would a teammate understand this in 6 months without you explaining it live?

**The actual test, from your own field notes:** can you explain every line yourself, in your own words, without re-reading the AI's explanation? If you hit a line you can't explain, that's the line to stop and actually read — regardless of whether it currently "works."