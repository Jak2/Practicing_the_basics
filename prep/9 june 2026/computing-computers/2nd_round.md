
## Problem Statement

### 1. Overview
The interview is a **1-hour live coding & execution session** conducted over screen-share. The primary focus of the evaluation is the candidate's **problem-solving process, logical reasoning, and hands-on execution**, rather than communication or pure recall.

### 2. Core Requirements
The candidate is required to design, implement, and run a **multi-agent system** consisting of **three small, lightweight agents**:
*   **Agent Interaction**: The three agents must be capable of working independently or communicating with one another (collaborative multi-agent setup) depending on the tasks.
*   **Capabilities**: The agents should gather and process information using Large Language Models (LLMs) and/or API calls.
*   **Data Persistence**: A database should be used to store/persist the outputs and execution logs.
*   **Presentation (Dashboard)**: The final execution output and agent results must be displayed in a dashboard/user interface.

### 3. Rules & Constraints
*   **Use of AI Tools**: The candidate is permitted (and encouraged) to use AI tools (e.g., LLMs, Copilot) to generate code.
*   **No Blind Copy-Pasting**: Blind copying is strictly disallowed. The candidate must walk through their reasoning, explain their choices, and show their step-by-step problem-solving and debugging process.
*   **Live execution**: The entire system must be developed, executed, and demonstrated live within the 1-hour window.
*   **Dynamic Task Assignment**: The specific concepts and tasks for the agents will be revealed on the spot during the interview.


1. §4/§5 Original Shape Architecture
Designed for a structured codebase but introduces more execution components and dependencies.

```graph TD
    Task[Task Input] --> Orch[orchestrator.py]
    Orch --> A1[Agent1: BaseAgent Subclass]
    Orch --> A2[Agent2: BaseAgent Subclass]
    Orch --> A3[Agent3: BaseAgent Subclass]
    
    A1 & A2 & A3 --> DB[(SQLite: blackboard.db)]
    Schema[schema.sql] -.-> DB
    
    DB --> Streamlit[Streamlit / Flask Server]
    Streamlit --> UI[Browser Dashboard: localhost:8501]
```


graph TD
    Task[Task Input] --> Main[main.py]
    Main --> f1[agent_1: Plain Function]
    Main --> f2[agent_2: Plain Function]
    Main --> f3[agent_3: Plain Function]
    
    f1 --> DB[(SQLite: blackboard.db)]
    f2 --> DB
    f3 --> DB
    
    DB --> DashScript[build_dashboard.py]
    DashScript --> HTML[dashboard.html]
    HTML --> FileProto[Browser: file:///...]

original_agent_project/
├── schema.sql           # Database schema definition
├── database.py          # SQLite connection and raw query execution helpers
├── agents.py            # BaseAgent class and Agent1, Agent2, Agent3 subclasses
├── orchestrator.py      # Entry point: runs sequence logic and passes context
├── app.py               # Streamlit application dashboard code
├── requirements.txt     # External dependencies (anthropic, streamlit)
└── blackboard.db        # Generated at runtime (SQLite database)



2. §6 Leaner Cut Architecture
Designed for low latency under a 60-minute clock with zero networking/dependency failure surface.

```graph TD
    Task[Task Input] --> Main[main.py]
    Main --> f1[agent_1: Plain Function]
    Main --> f2[agent_2: Plain Function]
    Main --> f3[agent_3: Plain Function]
    
    f1 & f2 & f3 --> DB[(SQLite: blackboard.db)]
    
    DB --> DashScript[build_dashboard.py]
    DashScript --> HTML[dashboard.html]
    HTML --> FileProto[Browser: file:///...]
```


lean_agent_project/
├── main.py              # Self-contained logic: call_llm, log_run, agents, and execution run
├── dashboard.py         # Script that reads DB, writes static HTML, and triggers browser open
└── blackboard.db        # Generated automatically at runtime (SQLite database)
