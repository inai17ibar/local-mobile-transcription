---
description: "Use when writing or editing test files. Covers test pyramid structure, coverage targets, test runner syntax, and anti-patterns."
applyTo: "tests/**"
---
# Testing Conventions

<!-- TODO: customize this file for your project's test framework -->

## Test Pyramid

<!-- Example:
- **Unit** (`tests/unit/`): pure logic tests — no I/O, no network, no database
- **Integration** (`tests/integration/`): service interactions, verified after build
- **E2E** (`tests/e2e/`): full user flows
-->
- {{TEST_PYRAMID}}

## Commands

```sh
{{TEST_COMMANDS}}
```

<!-- Example:
npm test              # All tests
npm run test:unit     # Unit only
npm run lint          # Lint before running tests
npm run build         # Build before integration tests
-->

## Coverage Targets

<!-- Example:
- Core business logic: 90%+ line coverage
- All public functions should have at least one test
-->
- {{COVERAGE_TARGETS}}

## Test Framework

<!-- Example for node:test:
```js
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

describe('module', () => {
  it('does something', () => {
    assert.equal(actual, expected);
  });
});
```
-->

## File / Test Structure

<!-- Example:
- Test files: match source file name + `.test.ts` (e.g., `user.test.ts` for `src/user.ts`)
- `describe` block: module or class name
- `it` block: plain-English description of behavior
-->
- {{TEST_STRUCTURE}}

## Anti-Patterns

- Do not write tests that depend on specific timing values
- Do not assert exact floating-point equality; use epsilon tolerances
- Do not import from build output in tests — import from `src/` directly
- Do not skip flaky tests silently — fix or document them
- Do not test implementation details; test observable behavior
