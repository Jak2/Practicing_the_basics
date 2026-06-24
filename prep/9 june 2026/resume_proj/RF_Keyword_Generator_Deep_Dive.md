# Robot Framework Keyword Generator — Complete Deep Dive
## Architecture · Interview Prep · Resume Bullet · LLM Upgrade

---

# PART 1: HOW IT ACTUALLY WORKS — END TO END

## The user journey

A tester opens the Streamlit UI and types:
> "Register a UE with IMSI 123456789012345 on AMF and verify authentication succeeds"

They select "UE Registration" from the procedure dropdown and click Generate.

Within 1-2 seconds they get back:

```robot
*** Settings ***
Library    5GCoreLibrary
Library    AMFLibrary

*** Test Cases ***
Register UE 123456789012345
    [Documentation]    Register UE with IMSI 123456789012345 on AMF
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

They copy this directly into their test suite. Zero manual keyword writing.

---

## The full pipeline

```
Tester types description
        ↓
Streamlit UI (frontend)
        ↓  HTTP POST
FastAPI backend receives request
        ↓
Stage 1: Procedure detection (keyword matching)
        ↓
Stage 2: Entity extraction (regex OR LLM)
        ↓
Stage 3: Template fill (deterministic)
        ↓
Stage 4: RF parser validation (syntax check)
        ↓
.robot file returned to Streamlit
        ↓
Tester downloads and uses it
```

---

## Why Streamlit + FastAPI instead of one framework

This is the first question interviewers ask. The split is intentional:

**Streamlit** is a Python library that turns Python scripts into web UIs with minimal code. A text input, a dropdown, a button — 10 lines of Python. No HTML, no CSS, no JavaScript. Perfect for internal tools where you want a working UI in an hour.

**FastAPI** is the backend API. It handles the actual logic — parsing, template filling, validation.

**Why not just Streamlit alone?**
Streamlit can call Python functions directly without a separate backend. But separating into Streamlit + FastAPI gives you:

- **Testability** — you can test the FastAPI endpoints with pytest and httpx without touching the UI. Testing pure Streamlit logic is much harder.
- **Reusability** — the FastAPI backend can be called by other tools, not just the Streamlit UI. Someone could build a CLI tool or a VS Code extension that hits the same `/generate` endpoint.
- **Separation of concerns** — UI logic and generation logic are independent. You can redesign the UI without touching the generation engine and vice versa.
- **Deployability** — FastAPI runs as a proper WSGI (Web Server Gateway Interface) service. Streamlit runs as a separate process. You can scale the backend independently if the tool gets heavy usage.

**Why not just FastAPI with a proper React frontend?**
For an internal tool used by 10-20 testers, building a full React frontend is overkill. Streamlit gives you a working UI in 20 lines. The tradeoff is customisability — Streamlit UIs are functional, not beautiful. For internal tooling, functional is enough.

---

## Stage 1: Procedure detection — keyword matching

The procedure type dropdown does most of the work. But the parser also scans the description text as a fallback and confidence check.

```python
PROCEDURE_KEYWORDS = {
    "UE Registration":  ["register", "attach", "connect", "onboard"],
    "Authentication":   ["authenticate", "auth", "5G-AKA", "verify identity"],
    "Handover":         ["handover", "handoff", "mobility", "move to"],
    "PDU Session":      ["session", "data connection", "bearer", "PDU"],
    "Deregistration":   ["deregister", "detach", "disconnect", "remove"],
}

def detect_procedure(description: str, selected: str) -> str:
    # Trust the dropdown first
    if selected in PROCEDURE_KEYWORDS:
        return selected

    # Fallback: scan description
    desc_lower = description.lower()
    for procedure, keywords in PROCEDURE_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return procedure

    return "Unknown"
```

No LLM needed here. The vocabulary of 5G procedures is small and well-defined.

---

## Stage 2: Entity extraction — the core parsing challenge

This is where the tool either works or breaks.

**Without LLM (original — regex):**

```python
import re

def extract_params_regex(description: str) -> dict:
    params = {}

    # IMSI — always exactly 15 digits
    imsi = re.search(r'\b(\d{15})\b', description)
    if imsi:
        params["imsi"] = imsi.group(1)

    # Cell/gNB identifier
    cell = re.search(r'(?:cell|gNB)[- ](\w+)', description, re.IGNORECASE)
    if cell:
        params["cell_id"] = cell.group(1)

    # 5G interfaces
    interface = re.search(r'\b(N[1-9]|S1-U|X2|Xn)\b', description)
    if interface:
        params["interface"] = interface.group(1)

    # Expected result
    if any(word in description.lower() for word in ["fail", "reject", "deny"]):
        params["expected_result"] = "FAILURE"
    else:
        params["expected_result"] = "SUCCESS"

    return params
```

Works for: "Register UE with IMSI 123456789012345 on gNB-007"
Breaks for: "Test that mobile identity 123456789012345 can join the network"
("mobile identity" not in regex, "join" not mapped)

**With LLM (upgraded — Claude Haiku):**

```python
import anthropic
import json

client = anthropic.Anthropic()

EXTRACTION_SCHEMA = {
    "UE Registration": {
        "imsi":            "15-digit IMSI number if present, else null",
        "cell_id":         "cell or gNB identifier if present, else null",
        "amf_id":          "AMF identifier if present, else null",
        "expected_result": "expected outcome if stated, else SUCCESS"
    },
    "Authentication": {
        "imsi":            "15-digit IMSI number if present, else null",
        "auth_method":     "auth method e.g. 5G-AKA, EAP-AKA if present, else null",
        "expected_result": "expected outcome if stated, else SUCCESS"
    },
    "Handover": {
        "imsi":            "15-digit IMSI if present, else null",
        "source_cell":     "source cell or gNB if present, else null",
        "target_cell":     "target cell or gNB if present, else null",
        "expected_result": "expected outcome if stated, else SUCCESS"
    },
    "PDU Session": {
        "imsi":            "15-digit IMSI if present, else null",
        "dnn":             "Data Network Name or APN if present, else internet",
        "session_type":    "IPv4/IPv6/IPv4v6 if present, else IPv4",
        "expected_result": "expected outcome if stated, else ESTABLISHED"
    },
    "Deregistration": {
        "imsi":            "15-digit IMSI if present, else null",
        "reason":          "deregistration reason if stated, else null",
        "expected_result": "expected outcome if stated, else DEREGISTERED"
    }
}

def extract_params_with_llm(description: str, procedure: str) -> dict:
    schema = EXTRACTION_SCHEMA.get(procedure, {})

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",   # cheap + fast — perfect for extraction
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""Extract test parameters from this 5G test description.

Procedure type: {procedure}
Description: "{description}"

Return ONLY valid JSON with these fields:
{json.dumps(schema, indent=2)}

Rules:
- Return null for any field not mentioned
- Do not invent values not in the description
- Return ONLY the JSON object, no explanation, no markdown"""
        }]
    )

    raw = response.content[0].text.strip()

    try:
        params = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback to regex if LLM returns bad JSON
        params = extract_params_regex(description)

    return apply_defaults(params, procedure)


def apply_defaults(params: dict, procedure: str) -> dict:
    defaults = {
        "UE Registration":  {"imsi": "UNKNOWN_IMSI", "expected_result": "SUCCESS"},
        "Authentication":   {"imsi": "UNKNOWN_IMSI", "expected_result": "SUCCESS"},
        "Handover":         {"source_cell": "SOURCE", "target_cell": "TARGET"},
        "PDU Session":      {"dnn": "internet", "session_type": "IPv4"},
        "Deregistration":   {"imsi": "UNKNOWN_IMSI", "expected_result": "DEREGISTERED"}
    }
    for key, default_val in defaults.get(procedure, {}).items():
        if not params.get(key):
            params[key] = default_val
    return params
```

Now "mobile identity 123456789012345 can join" → correctly extracts imsi=123456789012345.
"subscriber wants to authenticate using EAP-AKA" → extracts auth_method=EAP-AKA.

The LLM handles any phrasing. The regex fallback handles LLM failures.

---

## Stage 3: Template fill — fully deterministic

Pre-built templates for every common 5G procedure. Parameters from Stage 2 slot directly in.

```python
TEMPLATES = {
    "UE Registration": """\
*** Settings ***
Library    5GCoreLibrary
Library    AMFLibrary

*** Test Cases ***
Register UE {imsi}
    [Documentation]    Register UE {imsi} — expected: {expected_result}
    ${{ue_context}}=    Register UE On AMF    imsi={imsi}
    Verify Registration Result    ${{ue_context}}    expected={expected_result}

*** Keywords ***
Register UE On AMF
    [Arguments]    ${{imsi}}
    ${{resp}}=    POST To AMF
    ...    endpoint=/namf-comm/v1/ue-contexts
    ...    imsi=${{imsi}}
    RETURN    ${{resp}}

Verify Registration Result
    [Arguments]    ${{context}}    ${{expected}}
    Should Not Be None    ${{context}}
    Should Be Equal    ${{context.status}}    ${{expected}}
""",

    "Authentication": """\
*** Settings ***
Library    5GCoreLibrary
Library    AUSFLibrary

*** Test Cases ***
Authenticate UE {imsi}
    [Documentation]    Authenticate {imsi} using {auth_method}
    ${{auth_result}}=    Initiate Authentication
    ...    imsi={imsi}    method={auth_method}
    Verify Auth Result    ${{auth_result}}    expected={expected_result}

*** Keywords ***
Initiate Authentication
    [Arguments]    ${{imsi}}    ${{method}}
    ${{resp}}=    POST To AUSF
    ...    endpoint=/nausf-auth/v1/ue-authentications
    ...    imsi=${{imsi}}    method=${{method}}
    RETURN    ${{resp}}

Verify Auth Result
    [Arguments]    ${{result}}    ${{expected}}
    Should Be Equal    ${{result.status}}    ${{expected}}
""",

    "Handover": """\
*** Settings ***
Library    5GCoreLibrary
Library    AMFLibrary

*** Test Cases ***
Handover UE From {source_cell} To {target_cell}
    [Documentation]    UE handover from {source_cell} to {target_cell}
    ${{ho_result}}=    Execute Handover
    ...    source={source_cell}    target={target_cell}
    Verify Handover Result    ${{ho_result}}    expected={expected_result}

*** Keywords ***
Execute Handover
    [Arguments]    ${{source}}    ${{target}}
    ${{resp}}=    POST To AMF
    ...    endpoint=/namf-comm/v1/ue-contexts/handover
    ...    source=${{source}}    target=${{target}}
    RETURN    ${{resp}}

Verify Handover Result
    [Arguments]    ${{result}}    ${{expected}}
    Should Be Equal    ${{result.status}}    ${{expected}}
""",
}

def fill_template(procedure: str, params: dict) -> str:
    template = TEMPLATES.get(procedure)
    if not template:
        raise ValueError(f"No template for procedure: {procedure}")
    return template.format(**params)
```

Critical note on `{{` and `}}` in the template strings: Robot Framework uses `${variable}` syntax. In Python f-strings or `.format()`, curly braces must be escaped as `{{` and `}}` to be treated as literal text. This is a common bug — forgetting this produces malformed `.robot` output.

---

## Stage 4: RF parser validation — the quality gate

You import Robot Framework not to run tests but to validate generated syntax.

```python
from robot.api import get_model
import tempfile
import os

def validate_robot_syntax(robot_content: str) -> str:
    # Write to temp file — RF parser needs a file path
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.robot',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(robot_content)
        tmp_path = f.name

    try:
        get_model(tmp_path)    # raises if syntax is invalid
        return robot_content   # valid — return unchanged
    except Exception as e:
        raise ValueError(f"Generated RF syntax is invalid: {e}")
    finally:
        os.unlink(tmp_path)    # always clean up temp file
```

This is the safety net. If the template fill produces malformed output (e.g., a missing `${}`, an unclosed keyword block), the RF parser catches it before it reaches the tester. The tester never receives a broken `.robot` file.

---

## Complete FastAPI backend

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="RF Keyword Generator", version="1.0.0")

class GenerateRequest(BaseModel):
    description: str
    procedure: str

class GenerateResponse(BaseModel):
    robot_content: str
    params_extracted: dict
    procedure_detected: str

@app.post("/generate", response_model=GenerateResponse)
def generate_keyword(req: GenerateRequest):
    # Stage 1: Detect procedure
    procedure = detect_procedure(req.description, req.procedure)
    if procedure == "Unknown":
        raise HTTPException(
            status_code=400,
            detail="Could not detect 5G procedure type from description"
        )

    # Stage 2: Extract params (LLM or regex)
    try:
        params = extract_params_with_llm(req.description, procedure)
    except Exception:
        params = extract_params_regex(req.description)
        params = apply_defaults(params, procedure)

    # Stage 3: Fill template
    try:
        robot_content = fill_template(procedure, params)
    except KeyError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required parameter: {e}"
        )

    # Stage 4: Validate RF syntax
    try:
        validated = validate_robot_syntax(robot_content)
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generated invalid Robot Framework syntax: {e}"
        )

    return GenerateResponse(
        robot_content=validated,
        params_extracted=params,
        procedure_detected=procedure
    )

@app.get("/procedures")
def list_procedures():
    return {"procedures": list(TEMPLATES.keys())}

@app.get("/health")
def health():
    return {"status": "ok"}
```

---

## Complete Streamlit frontend

```python
import streamlit as st
import requests

st.set_page_config(
    page_title="RF Keyword Generator",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 5G Robot Framework Keyword Generator")
st.caption("Input a test description → get ready-to-use .robot keywords")

col1, col2 = st.columns([1, 1])

with col1:
    procedure = st.selectbox(
        "Procedure type",
        ["UE Registration", "Authentication", "Handover",
         "PDU Session", "Deregistration"]
    )

    description = st.text_area(
        "Describe what you want to test",
        height=120,
        placeholder="e.g. Register UE with IMSI 123456789012345 on AMF and verify success"
    )

    generate = st.button("Generate Keywords", type="primary")

with col2:
    if generate and description:
        with st.spinner("Generating..."):
            try:
                response = requests.post(
                    "http://localhost:8000/generate",
                    json={
                        "description": description,
                        "procedure": procedure
                    },
                    timeout=15
                )

                if response.status_code == 200:
                    data = response.json()

                    st.success(f"Generated for: {data['procedure_detected']}")

                    with st.expander("Parameters extracted", expanded=False):
                        st.json(data["params_extracted"])

                    st.code(data["robot_content"], language="robot")

                    st.download_button(
                        label="⬇️ Download .robot file",
                        data=data["robot_content"],
                        file_name=f"{procedure.lower().replace(' ', '_')}_test.robot",
                        mime="text/plain"
                    )
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

            except requests.exceptions.Timeout:
                st.error("Request timed out. Is the backend running?")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Run: uvicorn main:app --reload")
    elif generate and not description:
        st.warning("Please enter a test description first.")
```

---

# PART 2: ARCHITECTURE DECISIONS — INTERVIEW DEEP DIVE

---

**Q1. Why Streamlit + FastAPI instead of just Streamlit?**

Streamlit can call Python functions directly — you don't need a separate backend. But separating into Streamlit + FastAPI gives:

Testability: FastAPI endpoints are testable with pytest + httpx without touching the UI. Testing Streamlit logic requires browser automation.

Reusability: The `/generate` endpoint can be called from a CLI tool, a VS Code extension, a CI/CD (Continuous Integration/Continuous Deployment) pipeline — not just the Streamlit UI. With pure Streamlit, the logic is locked inside the UI.

Separation of concerns: The UI team and the generation logic can be developed independently. Redesigning the UI doesn't touch the generation engine.

Deployability: FastAPI runs as a proper ASGI (Asynchronous Server Gateway Interface) service behind nginx. Streamlit runs as a separate process. You can scale the backend independently.

For an internal tool used by 20 testers, this architecture is slightly over-engineered — but it's the correct pattern for anything that might grow.

---

**Q2. Why templates instead of just asking an LLM to generate the whole keyword?**

Two reasons: reliability and cost.

Reliability: An LLM generating Robot Framework keywords from scratch can produce syntactically invalid output — missing `***` section markers, incorrect indentation, wrong variable syntax (`$variable` instead of `${variable}`). Template generation is 100% syntactically correct by construction, validated by the RF parser.

Cost and latency: Generating a full keyword with an LLM requires a large prompt and a large response. Template filling is zero-cost and sub-millisecond. With 50+ generations per week, LLM-based generation would add API cost and 2-8 second latency per generation. Template filling is instant.

The right split: LLM handles what's variable and unpredictable (entity extraction from natural language). Templates handle what's fixed and structured (RF keyword syntax). This is the hybrid pattern — deterministic for structure, LLM for understanding.

---

**Q3. Why use the Robot Framework parser for validation instead of just visual inspection?**

Because RF syntax errors are subtle. Common failure modes:

- `${variable` without closing `}` — valid Python string, invalid RF variable
- Missing `...` continuation marker for multi-line keyword calls
- Wrong indentation — RF is indentation-sensitive
- Using `Return` instead of `RETURN` (case-sensitive in RF 5+)

Visual inspection misses these. The RF parser catches all of them in under 10ms. The engineer never receives a broken file.

---

**Q4. Why Claude Haiku for entity extraction instead of a larger model?**

Entity extraction is a structured, well-defined task: find specific values in a sentence and return JSON. It does not require reasoning, creativity, or domain knowledge beyond recognising that "mobile identity" and "IMSI" mean the same thing.

Haiku handles this reliably at 3-5x lower cost and ~500ms latency vs Sonnet's 2-4 seconds. For a tool used 50+ times per week by testers who want immediate results, latency matters.

If extraction quality degrades (e.g., a tester uses highly unusual phrasing), the regex fallback ensures the tool still returns something useful rather than failing entirely.

---

**Q5. What happens when a tester describes a procedure you don't have a template for?**

The `/procedures` endpoint lists available procedures. If the detected procedure has no template, the API returns a 400 with a clear message: "No template found for procedure X. Available procedures: [list]."

The longer-term fix is adding templates. Each new template takes about 30 minutes — define the keyword structure for the procedure, add the extraction schema, add the template string. The architecture makes this easy: templates are data, not code.

---

**Q6. How would you scale this if 500 testers used it daily?**

Current architecture: single FastAPI process, synchronous LLM calls, no caching.

At 500 uses/day (~20/hour peak), bottlenecks appear at:

The LLM extraction call (500ms-1s per request). Fix: async FastAPI with `async def` endpoints and `await` on the Anthropic client call. FastAPI handles many concurrent requests efficiently with async.

Repeated identical descriptions. Fix: Redis cache on (description, procedure) → params. Same description from 20 testers hits LLM once, serves from cache 19 times.

Template rendering: already sub-millisecond, no scaling needed.

RF parser validation: already fast, but runs in-process. At very high volume, move to a worker pool.

---

**Q7. How did you test this tool?**

Three levels:

Unit tests: for each stage independently — procedure detection with known inputs, regex extraction with boundary cases (IMSI at start/end of string, no IMSI), template fill with all parameter combinations, RF validation with deliberately broken templates to confirm it catches errors.

Integration tests: full pipeline tests with httpx hitting the FastAPI endpoints. Input: description string. Assert: response contains valid RF syntax, detected procedure matches expected, extracted params are correct.

User testing: informal — gave 5 testers a list of 20 descriptions and asked them to generate keywords. Tracked which descriptions failed (procedure not detected, params missing). Used failures to extend the keyword list and add regex patterns.

---

**Q8. The usage "exploded organically to 50+ weekly generations" — how did that happen without any promotion?**

Word of mouth within the team. One senior tester used it for repetitive registration test cases during a sprint. They mentioned it in standup. Three more testers tried it. Within two weeks it was used by most of the team for any repetitive procedure.

The key was zero friction: Streamlit UI needed no installation, no training, no documentation. Open URL, type description, click button, get file. The adoption metric (50+ weekly generations) was tracked from FastAPI's request logs.

---

# PART 3: THE LLM UPGRADE — WHAT CHANGES ON THE RESUME

## Before (original — regex only)

> "Built internal self-service Robot Framework keyword generator (Streamlit + FastAPI) — testers input high-level descriptions and get ready-to-use 5G keywords instantly → 50+ weekly generations, freed seniors for complex multi-vendor interoperability scenarios."

**Problem with this bullet:** Sounds like a simple CRUD tool. No technical depth visible. Any developer could claim this.

---

## After (with LLM entity extraction)

> "Built an AI-powered 5G Robot Framework keyword generator (Streamlit + FastAPI + Claude Haiku) — natural language test descriptions are parsed by an LLM entity extractor, mapped to deterministic procedure templates, and validated by the RF parser before output; regex fallback ensures 100% uptime even on LLM failure → 50+ weekly generations, reduced keyword creation from hours to minutes, freed seniors for complex multi-vendor interoperability scenarios."

**What this bullet now shows:**
- LLM integration with a specific model (Claude Haiku)
- Hybrid architecture thinking (LLM for understanding, deterministic for structure)
- Production reliability awareness (fallback mechanism)
- Output validation (RF parser)
- Concrete metric (50+ weekly generations)

---

## What to add to skills section

Add to AI & LLM row: `Claude Haiku (entity extraction)`
This is small but signals you understand model selection — using the right model for the task rather than always reaching for the most powerful one.

---

# PART 4: INTERVIEW Q&A — ALL QUESTIONS AN INTERVIEWER CAN ASK

---

**Q: Walk me through how the keyword generator works.**

A tester opens a Streamlit UI, types a test description in plain English, selects the procedure type from a dropdown, and clicks Generate. The request goes to a FastAPI backend which runs four stages: procedure detection via keyword matching, entity extraction (originally regex, upgraded to Claude Haiku for natural language robustness), template filling where extracted parameters slot into pre-built Robot Framework keyword templates, and finally Robot Framework parser validation to guarantee syntactic correctness. The tester gets back a valid .robot file they can use directly. The whole pipeline runs in under 2 seconds.

---

**Q: Why did you split Streamlit and FastAPI instead of using just one?**

Testability, reusability, and separation of concerns. With a separate FastAPI backend I can write pytest tests against the generation logic without touching the UI. The `/generate` endpoint can be called from a CI pipeline or a VS Code plugin, not just the Streamlit UI. And redesigning the UI doesn't touch the generation engine. For an internal tool it's slightly over-engineered, but it's the correct pattern if the tool grows.

---

**Q: Why templates instead of asking an LLM to generate the entire keyword?**

Two reasons. Reliability — an LLM generating Robot Framework syntax from scratch can produce subtle errors: wrong indentation, missing `***` section markers, incorrect variable syntax. Template generation is syntactically correct by construction. Cost and latency — 50+ generations per week adds up if every generation makes a full LLM call. Template filling is instant and zero-cost. The LLM only touches the entity extraction step, which is a small, cheap call. The right split: LLM for understanding natural language, templates for structured output.

---

**Q: What does the RF parser actually do in your pipeline?**

It validates syntax. I import Robot Framework's own parser — `get_model()` from `robot.api` — and run it on the generated file. This is the same parser Robot Framework uses when it actually executes tests, so if it passes validation it will run correctly. It catches subtle errors that would be invisible to the human eye: unclosed variable braces, wrong continuation markers, case-sensitive keyword issues. The tester never receives a broken file.

---

**Q: Why Claude Haiku specifically for entity extraction?**

Entity extraction is a structured, well-defined task — find specific values in a sentence and return JSON. It doesn't need deep reasoning or creativity. Haiku handles this reliably at 3-5x lower cost than Sonnet and around 500ms latency. For a tool used by testers who want immediate results, that latency matters. If I needed to synthesise across multiple retrieved patterns or explain a failure chain, I'd use Sonnet. For simple extraction, Haiku is the right tool.

---

**Q: What happens when the LLM returns malformed JSON?**

The regex fallback kicks in automatically. The `extract_params_with_llm` function wraps the JSON parse in a try/except. On JSONDecodeError, it falls back to the regex extractor, which handles the common structured inputs. The tester sees no error — they get a result regardless. This is why the tool can claim 100% uptime: the LLM path is an enhancement, not a dependency.

---

**Q: How do you handle a procedure type you don't have a template for?**

The API returns a clear 400 error: "No template found for procedure X. Available procedures: [list]." I also expose a `/procedures` endpoint that lists all supported procedures. Adding a new template takes about 30 minutes — define the keyword structure, add the extraction schema, add the template string. The architecture separates templates as data from generation logic as code, making extension easy.

---

**Q: How did you test this?**

Three levels. Unit tests for each stage: procedure detection with known inputs, regex extraction boundary cases (IMSI at start/end/middle of string, no IMSI present), template fill with all parameter combinations, RF validation with deliberately broken templates to confirm it catches errors. Integration tests hitting the FastAPI endpoints via httpx: input description, assert response contains valid RF syntax and correct detected procedure. User testing: gave 5 testers 20 descriptions, tracked which failed, used failures to extend keyword lists and add extraction patterns.

---

**Q: 50+ weekly generations — how do you know that number?**

FastAPI request logs. Every call to `/generate` is logged with timestamp, procedure type, and response status. I aggregated these logs to get the weekly generation count. It also showed which procedures were generated most frequently (UE Registration dominated at ~60%) which informed which templates to prioritise for improvement.

---

**Q: How would you scale this to 500 daily users?**

Three changes. First, async FastAPI — change `def generate_keyword` to `async def` and await the Anthropic client call. FastAPI handles many concurrent requests efficiently with async. Second, Redis cache on the (description, procedure) pair — same description from 20 testers hits the LLM once, serves from cache 19 times. Third, at very high volume the RF parser validation could move to a worker pool to avoid blocking the main thread. Template rendering is already sub-millisecond and needs no changes.

---

**Q: Why not just use GitHub Copilot or another existing tool for this?**

Two reasons. First, domain specificity — Copilot generates generic code, not Nokia-specific 5G keyword libraries like `5GCoreLibrary` or `AMFLibrary`. Our internal libraries have custom keyword names that no public tool knows. The templates encode our team's specific naming conventions and endpoint patterns. Second, workflow integration — Copilot works in an IDE. Our testers wanted a browser-based tool with a dropdown that understood 5G procedure types and produced ready-to-use files without any coding knowledge. Different users, different interface.

---

**Q: What would you improve with more time?**

Three things. First, expand template coverage — we had templates for 5 procedure types. There are easily 15-20 common 5G test procedures. Each template takes 30 minutes to add. Second, parameter suggestions — if the tester doesn't provide an IMSI, instead of defaulting to UNKNOWN_IMSI, the tool could query an internal test subscriber database and suggest available IMSIs. Third, version control integration — automatically create a Git commit with the generated file in the appropriate test suite directory, rather than making the tester download and place it manually.

---

# PART 5: THE RESUME BULLET — FINAL VERSION

## Current bullet in resume

> "Built internal self-service Robot Framework keyword generator (Streamlit + FastAPI) — testers input high-level descriptions and get ready-to-use 5G keywords instantly → 50+ weekly generations, freed seniors for complex multi-vendor interoperability scenarios."

## Upgraded bullet (after adding LLM entity extraction)

> "Built an AI-powered 5G Robot Framework keyword generator (Streamlit + FastAPI + Claude Haiku) — natural language descriptions parsed by LLM entity extractor, mapped to deterministic 5G procedure templates, validated by RF parser before output; regex fallback ensures reliability even on LLM failure → 50+ weekly generations, reduced keyword creation from hours to minutes, freed seniors for complex multi-vendor interoperability work."

## What to update in skills

AI & LLM row — add: `Claude Haiku · Hybrid LLM-Deterministic Pipelines`

This signals something more valuable than just "used an LLM" — it signals you understand when to use LLM and when to use deterministic logic. That's what separates engineers who build toy AI apps from engineers who build production AI systems.
