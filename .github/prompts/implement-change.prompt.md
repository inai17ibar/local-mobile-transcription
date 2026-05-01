---
description: "Implement a scoped change using the full autonomous agent pipeline"
name: "Implement Change"
argument-hint: "Feature, bugfix, or refactor request"
agent: "Main"
---
Implement the requested change.

Requirements:
- Read [AGENTS.md](../../AGENTS.md) and respect all project constraints
- Keep changes tightly scoped to the user request
- Run lint, build, and tests before finishing
- If the task is ambiguous or risky, stop and ask a clarifying question before editing
- Report any verification that could not be run
