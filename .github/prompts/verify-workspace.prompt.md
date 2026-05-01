---
description: "Run focused verification and report failures clearly"
name: "Verify Workspace"
argument-hint: "Changed files, subsystem, or full workspace"
agent: "Verification"
---
Run the narrowest useful verification based on the requested scope.

Requirements:
- Start with the smallest relevant validation command before escalating to full-workspace checks
- Report the exact commands you ran
- Include failing test names, file paths, and raw error output when something breaks
- Call out any validation that could not be run and why
