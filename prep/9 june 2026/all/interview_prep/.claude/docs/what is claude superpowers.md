# Claude Code Superpowers

> Comprehensive notes for turning Claude Code into a Staff/Principal Engineer level development assistant.

---

# Table of Contents

1. What Claude Code Really Is
2. Installation & Setup
3. Project Context
4. CLAUDE.md
5. Custom Commands
6. Git Workflows
7. Architecture Analysis
8. Debugging Workflows
9. Performance Engineering
10. Test Generation
11. Refactoring at Scale
12. Multi-Agent Workflows
13. Development Tooling
14. Thinking Modes
15. Onboarding New Repositories
16. Productivity Workflows
17. Recommended Folder Structure
18. Daily Workflow

---

# What Claude Code Really Is

Most people use Claude Code incorrectly.

They treat it like ChatGPT in a terminal.

Instead think of it as:

```text
ChatGPT:
Answers questions.

Claude Code:
Operates on your codebase.
```

Claude Code can:

* Read entire repositories
* Search thousands of files
* Understand architecture
* Trace workflows
* Modify code
* Generate tests
* Review pull requests
* Analyze performance
* Refactor codebases
* Create migrations
* Debug production issues

---

# Installation & Setup

Install Claude Code:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Verify:

```bash
claude --version
```

Login:

```bash
claude
```

---

# Essential Development Tools

Install:

```bash
sudo apt install \
    git \
    gh \
    ripgrep \
    fd-find \
    bat \
    jq \
    zoxide \
    eza
```

Useful tools:

| Tool    | Purpose          |
| ------- | ---------------- |
| ripgrep | Fast code search |
| fd      | Fast file finder |
| bat     | Better cat       |
| eza     | Better ls        |
| zoxide  | Smart cd         |
| gh      | GitHub CLI       |

---

# Project Context

Always run Claude inside a repository.

Bad:

```bash
claude
```

Good:

```bash
cd my-project
claude
```

Ask:

```text
Explain this codebase.
```

```text
Map all services.
```

```text
Show data flow.
```

```text
Identify architectural patterns.
```

---

# CLAUDE.md

One of the highest ROI features.

Create:

```text
CLAUDE.md
```

Example:

```markdown
# Project Rules

Backend:
- Python 3.13
- FastAPI
- PostgreSQL

Architecture:
- Services contain business logic
- Routers contain API logic
- Repository layer handles database access

Testing:
- pytest
- 80% coverage minimum

Performance:
- Avoid N+1 queries
- Prefer bulk operations

Code Style:
- Use type hints
- Follow SOLID principles
```

Claude automatically reads it.

---

# Custom Commands

Create:

```text
.claude/
└── commands/
```

---

## Review Command

File:

```text
.claude/commands/review.md
```

Contents:

```markdown
Review code for:

- Performance
- Security
- Maintainability
- Test coverage
- Readability
```

Usage:

```text
/review
```

---

## Debug Command

```markdown
Act as a senior software engineer.

Trace:

1. API Layer
2. Service Layer
3. Database Layer

Find root cause.

Provide fixes.
```

Usage:

```text
/debug
```

---

## Performance Command

```markdown
Act as a database performance expert.

Focus on:

- N+1 queries
- Missing indexes
- Duplicate queries
- Bulk operations
- Query optimization
```

Usage:

```text
/perform
```

---

# Git Workflows

Review changes:

```text
Review my changes.
```

Create commit message:

```text
Generate a commit message.
```

Generate PR:

```text
Generate PR description.
```

Analyze diff:

```text
Explain this diff.
```

Before merging:

```text
Review all modified files.
```

---

# Architecture Analysis

Useful prompts:

```text
Explain architecture.
```

```text
Map all service dependencies.
```

```text
Show request lifecycle.
```

```text
Trace API → Service → DB flow.
```

```text
Identify architectural bottlenecks.
```

Claude excels at large-scale understanding.

---

# Debugging Workflows

Example:

```text
Manager assigns task.

Employee dashboard does not show task.

Trace entire workflow.
```

Claude should:

* Find API
* Find service
* Find database writes
* Find event handlers
* Find filters
* Find permissions

---

## Root Cause Analysis Prompt

```text
Perform a root cause analysis.

Generate:
- hypotheses
- evidence
- validation steps
- fix recommendation
```

---

# Performance Engineering

Claude is extremely useful for:

## N+1 Detection

```text
Find N+1 queries.
```

## Redundant Queries

```text
Find duplicate database lookups.
```

## Bulk Insert Opportunities

```text
Find loops that can use bulk operations.
```

## Service Optimization

```text
Identify unnecessary service calls.
```

## Query Optimization

```text
Review ORM usage.
```

---

# Example Performance Prompt

```text
Analyze workflow_instances/service.py

Focus on:

- query count
- redundant lookups
- nested loops
- expensive operations
```

---

# Test Generation

Generate tests:

```text
Generate pytest tests.
```

Coverage analysis:

```text
Find missing test coverage.
```

Edge cases:

```text
Generate edge case tests.
```

Regression tests:

```text
Create regression tests for this bug.
```

---

# Refactoring at Scale

Claude handles large changes well.

Examples:

```text
Convert sync SQLAlchemy to async.
```

```text
Move validation logic into services.
```

```text
Replace repository pattern.
```

```text
Introduce dependency injection.
```

```text
Convert function-based views to class-based views.
```

---

# Multi-Agent Workflows

Most developers stop here.

Power users create specialized agents.

---

## Architect Agent

```markdown
You are a principal software architect.

Focus:
- scalability
- maintainability
- system design
- tradeoffs
```

---

## Performance Agent

```markdown
You are a database performance expert.

Focus:
- indexes
- query optimization
- caching
- bulk operations
```

---

## Security Agent

```markdown
You are an application security expert.

Focus:
- auth
- permissions
- secrets
- injection attacks
```

---

## QA Agent

```markdown
You are a senior QA engineer.

Focus:
- testability
- edge cases
- regression prevention
```

---

# Thinking Modes

For complex tasks:

```text
Think deeply.
```

```text
Think step by step.
```

```text
Generate multiple hypotheses.
```

```text
Perform root cause analysis.
```

```text
Challenge your assumptions.
```

```text
Explore alternative designs.
```

These improve quality dramatically.

---

# Repository Onboarding

When joining a new project:

```text
Create onboarding documentation.
```

```text
Explain architecture.
```

```text
Identify key services.
```

```text
Identify deployment flow.
```

```text
Map database schema.
```

```text
Show critical workflows.
```

---

# Productivity Workflows

## Bug Investigation

```text
Trace this bug.

Show:

- entry point
- services involved
- database operations
- likely root cause
```

---

## Feature Development

```text
Design implementation plan.

Include:

- APIs
- services
- models
- migrations
- tests
```

---

## Code Review

```text
Review as Staff Engineer.

Focus on:

- correctness
- performance
- maintainability
```

---

# Recommended Repository Structure

```text
project/
│
├── CLAUDE.md
│
├── .claude/
│   └── commands/
│       ├── review.md
│       ├── debug.md
│       ├── performance.md
│       ├── architecture.md
│       ├── security.md
│       └── testgen.md
│
├── app/
├── tests/
└── docs/
```

---

# Daily Workflow

Morning:

```text
Explain changes since yesterday.
```

---

Before Coding:

```text
Generate implementation plan.
```

---

While Coding:

```text
Review changes continuously.
```

---

Before Commit:

```text
Review my diff.
```

```text
Generate commit message.
```

---

Before PR:

```text
Generate PR description.
```

```text
Perform final review.
```

---

# Ultimate Goal

The objective is not to use Claude as a chatbot.

The objective is to make Claude behave like:

* Staff Engineer
* Principal Engineer
* Performance Expert
* Architect
* QA Engineer
* Security Engineer

all operating directly on your repository with full context.

When configured properly with:

* CLAUDE.md
* Custom Commands
* Git Integration
* Performance Workflows
* Architecture Workflows

Claude Code becomes a development operating system rather than an AI chat tool.
