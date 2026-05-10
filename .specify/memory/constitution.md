<!--
Sync Impact Report
==================
Version change: [TEMPLATE] → 1.0.0
Added sections:
  - I. Code Quality (new)
  - II. Testing Standards (new)
  - III. User Experience Consistency (new)
  - IV. Performance Requirements (new)
  - Development Standards (new)
  - Quality Gates (new)
  - Governance (populated from template)
Modified principles: N/A — initial authoring from template
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ aligned (Constitution Check gate section present)
  - .specify/templates/spec-template.md ✅ aligned (Success Criteria + Measurable Outcomes present)
  - .specify/templates/tasks-template.md ✅ aligned (test tasks, performance, polish phases present)
Follow-up TODOs: None — all placeholders resolved
-->

# Resume Builder Constitution

## Core Principles

### I. Code Quality

All code MUST be clean, readable, and maintainable from the moment it is written.

- Naming MUST be descriptive and unambiguous; abbreviations are forbidden except for
  universally recognized acronyms (e.g., `id`, `url`, `api`).
- Functions and methods MUST do one thing; any function exceeding 40 lines MUST be split.
- Dead code, commented-out blocks, and unused imports MUST NOT be committed.
- All public APIs MUST be typed (TypeScript types, Python type hints, or equivalent for
  the project's language stack).
- Complexity beyond current feature requirements MUST be explicitly justified with a
  rationale comment; premature abstractions are a violation.

**Rationale**: Every developer touching this codebase MUST be able to understand any file
within five minutes of reading it. Unreadable code is a compounding liability.

### II. Testing Standards

Automated testing is NON-NEGOTIABLE. No feature is complete without passing tests.

- Tests MUST be written before implementation (TDD). Red → Green → Refactor cycle is
  strictly enforced.
- Unit test coverage MUST be ≥80% for all business logic modules.
- Integration tests MUST cover every user-facing workflow defined in the feature spec.
- Tests MUST be independent: no test may depend on the execution order or state of
  another test.
- Flaky tests MUST be fixed or removed immediately — they MUST NOT be merged.
- Test files MUST mirror the source tree (e.g., `src/foo.ts` → `tests/foo.test.ts`).
- Contract tests MUST be written for any API boundary or shared schema change.

**Rationale**: Tests are the only reliable indicator of correct behavior. Skipping tests
to move faster consistently produces slower delivery over the lifetime of the project.

### III. User Experience Consistency

The UI and all user-facing outputs MUST be consistent and accessible across every feature.

- All interactive components MUST follow the established design system (spacing,
  typography, color tokens). Ad-hoc or one-off styles are forbidden.
- Every user-facing action MUST provide feedback within 100ms of user input (loading
  states, success messages, or error messages — never silent).
- The application MUST meet WCAG 2.1 Level AA accessibility standards at all times.
- Navigation patterns and terminology MUST be consistent: the same concept MUST always
  use the same label and icon throughout the application.
- Resume output (PDF/HTML/print) MUST be visually consistent across all export targets
  and formats.

**Rationale**: Users trust software that behaves predictably. Inconsistency erodes
confidence and multiplies the support burden.

### IV. Performance Requirements

Performance targets are hard constraints enforced at merge time, not aspirational goals.

- Largest Contentful Paint (LCP) MUST be ≤2.5 seconds on a simulated 4G connection.
- Time to Interactive (TTI) MUST be ≤4 seconds on a simulated 4G connection.
- Resume PDF generation MUST complete in ≤3 seconds for documents up to 5 pages.
- Initial JavaScript bundle (main entry) MUST NOT exceed 250 KB gzipped.
- Any feature introducing a regression beyond these thresholds MUST NOT be merged until
  the regression is resolved and verified.

**Rationale**: A slow resume builder frustrates users at the moment they need confidence
most. Performance is a user-facing feature, not an internal concern.

## Development Standards

Guidelines that apply to all development activity on this project:

- All features MUST be developed on a dedicated feature branch. Direct commits to `main`
  are forbidden.
- Code review is mandatory for every merge request; at least one approval is required
  before merge.
- Linting and type-checking MUST pass before any PR can be merged (enforced in CI).
- Dependencies MUST be pinned to exact versions in lock files; manifest version ranges
  are permitted for minor/patch only.
- Secrets and credentials MUST NEVER be committed; use environment variables with a
  committed `.env.example` listing all required keys without values.

## Quality Gates

Every PR MUST satisfy all of the following gates before merge:

| Gate | Threshold | Enforced By |
|------|-----------|-------------|
| Unit test coverage | ≥80% business logic | CI |
| Type errors | 0 | CI |
| Lint errors | 0 | CI |
| LCP | ≤2.5s (4G) | Lighthouse CI or manual |
| Bundle size (gzip) | ≤250 KB | CI bundle analyzer |
| Accessibility (Lighthouse) | ≥90 | CI or manual |

Failures block merge. Waivers require a documented rationale in the PR description and
MUST be approved by a reviewer. Repeated waivers on the same gate trigger a constitution
amendment review.

## Governance

This constitution supersedes all other project practices and informal conventions.
Compliance is verified at every code review and at the Constitution Check gate in every
implementation plan.

**Amendment procedure**:

1. Author opens a PR modifying `.specify/memory/constitution.md`.
2. Amendment is reviewed and approved by at least one other contributor.
3. `CONSTITUTION_VERSION` is bumped per the versioning policy below.
4. All dependent templates are updated in the same PR.

**Versioning policy**:

- MAJOR: Removal or incompatible redefinition of a principle.
- MINOR: New principle or section added; material expansion of existing guidance.
- PATCH: Wording clarification, typo fix, or non-semantic refinement.

**Compliance review**: Constitution alignment MUST be verified at the start of every
implementation plan (see the Constitution Check section in `plan-template.md`).

**Version**: 1.0.0 | **Ratified**: 2026-05-10 | **Last Amended**: 2026-05-10
