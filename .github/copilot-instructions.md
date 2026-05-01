---
applyTo: "**"
---
# {{PROJECT_NAME}} — Project Instructions

<!-- TODO: replace {{PROJECT_NAME}} and fill in the project-specific details below -->

{{PROJECT_DESCRIPTION}}

See [`AGENTS.md`](../AGENTS.md) for the full agent index and [`ADR.md`](../ADR.md) for architecture decisions.

## Non-negotiable constraints

<!-- TODO: paste the constraints from AGENTS.md here for quick reference -->
- {{CONSTRAINT_1}}
- {{CONSTRAINT_2}}

## Source layout

<!-- TODO: describe your actual source structure, e.g.:
- `src/` — core source code
- `tests/` — test files
- `dist/` — generated output; never edit directly
-->
{{SOURCE_LAYOUT}}

## Verification commands

```sh
{{VERIFICATION_COMMANDS}}
```

## Autonomous pipeline

All agent work flows through five lanes in order:

```
▶ [LANE:explore]   → ✓ [LANE:explore:complete]
▶ [LANE:plan]      → ✓ [LANE:plan:complete]
▶ [LANE:implement] → ✓ [LANE:implement:complete]
▶ [LANE:verify]    → ✓ [LANE:verify:complete]
▶ [LANE:review]    → ✓ [LANE:review:complete]
```

A `✗ [LANE:{name}:blocked]` event means the lane failed and requires attention before the pipeline can proceed.

## Agents available

| Agent | Purpose | Invoke |
|-------|---------|--------|
| `@Main` | Full autonomous pipeline (explore→plan→implement→verify→review) | High-level tasks |
| `@Plan` | Design a plan, wait for approval, handoff to Implementer | Complex features |
| `@Explore` | Read-only codebase research and Q&A | Questions about code |
| `@Implementer` | Execute an approved plan (handoff only) | Via Plan |
| `@Reviewer` | Security + quality audit | After implementation |
| `@Verification` | Run lint / build / tests | Spot checks |

Prompt shortcuts in `.github/prompts/`:
- **Plan Change** — decompose a feature request into an implementation plan
- **Implement Change** — run the full pipeline for a specific request
- **Verify Workspace** — run narrowest relevant verification
