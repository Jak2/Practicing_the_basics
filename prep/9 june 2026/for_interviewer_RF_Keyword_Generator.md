# Robot Framework Keyword Generator
## Streamlit · FastAPI · Claude Haiku · Robot Framework Parser · Python

---

## Elevator Pitch (30 seconds)

> "I built an AI-powered internal tool where 5G test engineers type a test description in plain English and get a ready-to-use Robot Framework keyword file in under 2 seconds. It uses Claude Haiku for entity extraction — understanding natural language like 'mobile identity' when a regex only knows 'IMSI' — then fills deterministic procedure templates, and validates output through the Robot Framework parser itself before returning it. It went from zero to 50+ weekly generations purely through word of mouth, and freed senior engineers from repetitive keyword writing."

---

## The Problem

5G test automation uses Robot Framework — a keyword-driven testing framework. Creating `.robot` keyword files requires knowing Nokia-specific library names, correct RF syntax, 5G procedure structures, and endpoint URLs. A junior tester creating a "UE Registration" test case from scratch might spend an hour on boilerplate. Senior engineers were constantly interrupted to help with repetitive keyword creation for standard 5G procedures.

---

## Architecture — 4 Pipeline Stages

```
Tester types: "Register mobile identity 123456789012345 on AMF, verify success"
   ↓
Streamlit UI → HTTP POST to FastAPI /generate
   ↓
Stage 1: Procedure Detection
  - Dropdown selection trusted first
  - Fallback: keyword scan of description text
  - PROCEDURE_KEYWORDS dict: {"UE Registration": ["register", "attach", "connect"], ...}
   ↓
Stage 2: Entity Extraction (LLM path)
  - Claude Haiku: "Extract JSON with these fields: {imsi, cell_id, expected_result, ...}"
  - temperature=0 (deterministic JSON extraction)
  - max_tokens=300 (small, cheap, fast)
  - Fallback: regex extraction on JSONDecodeError
  - Fallback defaults: imsi="UNKNOWN_IMSI", expected_result="SUCCESS"
   ↓
Stage 3: Template Fill (deterministic)
  - Pre-built .robot template per procedure type
  - params dict slots directly into template.format(**params)
  - {{variable}} in templates = escaped braces (RF uses ${variable}, Python .format() needs {{ }})
   ↓
Stage 4: RF Parser Validation (quality gate)
  - robot.api.get_model(tmp_path) — same parser RF uses at runtime
  - Raises on any syntax error → 500 with specific error message
  - Tester never receives a broken .robot file
   ↓
GenerateResponse: robot_content, params_extracted, procedure_detected
```

---

## What the Output Looks Like

Input: `"Register UE with IMSI 123456789012345 on AMF and verify authentication succeeds"`

Output:
```robot
*** Settings ***
Library    5GCoreLibrary
Library    AMFLibrary

*** Test Cases ***
Register UE 123456789012345
    [Documentation]    Register UE 123456789012345 — expected: SUCCESS
    ${ue_context}=    Register UE On AMF    imsi=123456789012345
    Verify Registration Result    ${ue_context}    expected=SUCCESS

*** Keywords ***
Register UE On AMF
    [Arguments]    ${imsi}
    ${resp}=    POST To AMF
    ...    endpoint=/namf-comm/v1/ue-contexts
    ...    imsi=${imsi}
    RETURN    ${resp}

Verify Registration Result
    [Arguments]    ${context}    ${expected}
    Should Not Be None    ${context}
    Should Be Equal    ${context.status}    ${expected}
```

---

## The Key Design Decisions

### 1. Streamlit + FastAPI split (not one or the other)

**Why not just Streamlit alone?** Streamlit can call Python functions directly. But:
- **Testability:** FastAPI endpoints are testable with `pytest + httpx` without browser automation. Testing Streamlit logic requires UI automation.
- **Reusability:** The `/generate` endpoint can be called from a CI pipeline, a VS Code plugin, or a CLI tool — not just the Streamlit UI.
- **Separation of concerns:** UI redesign doesn't touch the generation engine and vice versa.
- **Deployability:** FastAPI runs behind nginx as a proper ASGI service; Streamlit runs separately.

**Why not React frontend?** For an internal tool used by 20 testers, a full React frontend is overkill. Streamlit gives a working UI in 20 lines. Functional over beautiful for internal tooling.

### 2. LLM for extraction only — templates for structure (the hybrid pattern)

**Why not let the LLM generate the entire Robot Framework keyword?**

*Reliability:* LLMs generating RF syntax from scratch produce subtle errors — wrong indentation, missing `***` section markers, `$variable` instead of `${variable}`. Template generation is syntactically correct by construction, then validated by the RF parser.

*Cost and latency:* At 50+ generations per week, full LLM generation adds API cost and 2-8 second latency. Template filling is instant and zero-cost.

*The right split:* LLM handles what's variable and unpredictable (natural language entity extraction). Templates handle what's fixed and structured (RF keyword syntax). This is the production AI pattern — deterministic for structure, LLM for understanding.

### 3. Claude Haiku specifically (not Sonnet or GPT-4)

Entity extraction is a narrow, well-defined task: find specific values in a sentence and return JSON. It doesn't require reasoning or creativity. Haiku handles this reliably at 3-5× lower cost and ~500ms latency vs Sonnet's 2-4 seconds.

*Model selection is a design decision, not a default.* Using the cheapest model that reliably handles the task is not cutting corners — it's correct engineering.

### 4. Regex fallback — 100% uptime guarantee

If Claude returns malformed JSON, `json.loads()` raises `JSONDecodeError`, and the code falls back to the regex extractor automatically. The tester sees no error. The LLM path is an enhancement, not a dependency.

```python
try:
    params = json.loads(raw)
except json.JSONDecodeError:
    params = extract_params_regex(description)  # never crashes
```

### 5. RF parser as the quality gate

Robot Framework's own parser (`robot.api.get_model()`) validates the generated file. Common failure modes it catches that visual inspection misses:
- `${variable` without closing `}` — valid Python string, invalid RF variable
- Missing `...` continuation marker for multi-line keyword calls
- Wrong indentation (RF is indentation-sensitive)
- `Return` instead of `RETURN` (case-sensitive in RF 5+)

The engineer never receives a broken file.

### 6. The `{{` / `}}` escaping pitfall

Robot Framework uses `${variable}` syntax. Python's `.format()` treats single `{` as a placeholder. Templates must use `{{` and `}}` for literal curly braces. Forgetting this produces malformed `.robot` output. This is a real bug that catches people — documenting it signals you've actually written and debugged this code.

---

## Why It Spread Organically

Zero friction. The Streamlit UI required no installation, no training, no documentation. Open URL, type description, click button, get file. One senior tester used it during a sprint, mentioned it in standup, and within two weeks most of the team was using it for any repetitive procedure. Adoption tracked via FastAPI request logs.

The 60% usage on UE Registration specifically informed which templates to prioritise improving next.

---

## Results

- **50+** weekly generations (tracked via FastAPI request logs)
- Keyword creation reduced from hours to minutes
- Senior engineers freed for complex multi-vendor interoperability scenarios
- Zero formal announcement — pure organic word-of-mouth adoption

---

## Anticipated Interview Questions

**Q: Walk me through how this works.**
> A tester types a test description, selects a procedure type, clicks Generate. FastAPI runs four stages: procedure detection via keyword matching, entity extraction using Claude Haiku (which handles any natural language phrasing for 5G parameters), template filling where extracted parameters slot into pre-built Robot Framework keyword templates, and Robot Framework parser validation to guarantee syntactic correctness. Output is a valid .robot file ready to use directly. Whole pipeline under 2 seconds.

**Q: Why didn't you just use GitHub Copilot?**
> Two reasons. Domain specificity — Copilot generates generic code, not Nokia-specific 5G keyword libraries like `5GCoreLibrary` or `AMFLibrary`. Our internal libraries have custom keyword names no public tool knows. The templates encode our team's specific naming conventions and endpoint patterns. Second, workflow — Copilot works in an IDE. Our testers wanted a browser-based tool with a procedure dropdown that produced ready-to-use files without any coding knowledge.

**Q: Why templates instead of full LLM generation?**
> Reliability and cost. An LLM generating RF syntax from scratch produces subtle errors — wrong indentation, missing section markers, incorrect variable syntax. Template generation is syntactically correct by construction, then validated by the RF parser. And at 50+ weekly generations, full LLM generation adds cost and 2-8 second latency. Template filling is instant. The LLM only touches entity extraction — a small, cheap, focused call.

**Q: What happens when the LLM returns bad JSON?**
> The regex fallback kicks in automatically. `extract_params_with_llm` wraps the JSON parse in a try/except. On JSONDecodeError it falls back to the regex extractor, which handles common structured inputs. The tester sees no error — they get a result regardless. This is why the tool could claim 100% uptime: the LLM path is an enhancement, not a dependency.

**Q: How would you scale this to 500 daily users?**
> Three changes. First, async FastAPI — change to `async def` and await the Anthropic client call. Second, Redis cache on the (description, procedure) pair — same description from 20 testers hits LLM once, serves from cache 19 times. Third, at very high volume, RF parser validation could move to a worker pool to avoid blocking the main thread. Template rendering is already sub-millisecond and needs no changes.

**Q: How did you know it was working? What metrics did you have?**
> FastAPI request logs. Every call to `/generate` was logged with timestamp, procedure type, and response status. I aggregated these to get weekly generation counts. It also showed procedure type distribution — UE Registration was ~60% of all generations, which told me which templates to prioritise for improvement and which extraction patterns to harden.
