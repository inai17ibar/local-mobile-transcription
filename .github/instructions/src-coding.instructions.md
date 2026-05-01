---
description: "Use when writing or editing source files. Covers naming conventions, formatting rules, import ordering, and project-specific architecture patterns."
applyTo: "src/**"
---
# Source Code Conventions

<!-- TODO: customize this file for your project's language and framework -->

## Naming
<!-- Example for JavaScript/TypeScript:
- Files: `camelCase.ts` (e.g., `userService.ts`, `authController.ts`)
- Functions/methods: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Classes/interfaces/types: `PascalCase`
- Single-letter loop indices (`i`, `j`, `k`) allowed in tight loops
-->
- {{NAMING_CONVENTIONS}}

## Import Ordering
<!-- Example:
1. Built-in modules (node:fs, node:path)
2. External libraries (react, lodash)
3. Internal project modules (./utils, ../services/user)
-->
- {{IMPORT_ORDERING}}

## Formatting
<!-- Example:
- 2-space indentation
- Single quotes for strings
- Semicolons required
- LF line endings
- `const` / `let` — no `var`
- Trailing commas in multi-line arrays/objects
-->
- {{FORMATTING_RULES}}

## Architecture Patterns

### Source layout
<!-- Describe the expected directory structure, e.g.:
src/
├── main.ts         — entry point
├── services/       — business logic
├── controllers/    — HTTP/API layer
└── utils/          — shared helpers
-->
{{SOURCE_LAYOUT}}

### Non-negotiable constraints
<!-- Reference the constraints from AGENTS.md, e.g.:
- Never edit `dist/` — it is generated output
- All source changes go in `src/` or `tests/`
-->
See `AGENTS.md` for the full constraint list.

## Verification

After any changes run:
```sh
{{VERIFICATION_COMMANDS}}
```
