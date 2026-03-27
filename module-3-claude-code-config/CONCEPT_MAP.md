# Module 3 Concept Coverage Map
## Domain 3: Claude Code Configuration & Workflows (20% of exam)

This map tracks every testable concept from the exam guide against our learning materials.

### Task Statement 3.1 — CLAUDE.md hierarchy & modular organization
**Covered in: Unit 3.1 + Cheat Sheet Section 1**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Three-level hierarchy: user (~/.claude/), project (.claude/), directory | Knowledge | Unit 3.1 Sec 1 |
| User-level is NOT version-controlled — personal preferences only | Knowledge | Unit 3.1 Sec 1, Exam Trap |
| Project-level is shared via git — team-wide standards | Knowledge | Unit 3.1 Sec 1 |
| Directory-level scopes rules to specific packages/modules | Knowledge | Unit 3.1 Sec 1 |
| All levels merge (supplement, not replace) | Knowledge | Unit 3.1 Sec 1 |
| @import directive for modular CLAUDE.md organization | Knowledge | Unit 3.1 Sec 1 |
| .claude/rules/ for path-specific rules (see also 3.3) | Knowledge | Unit 3.1 Sec 1 |
| /memory command for cross-session persistence | Knowledge | Unit 3.1 Sec 1 |
| Designing a CLAUDE.md hierarchy for a multi-team project | Skill | Unit 3.1 Challenge |
| Classifying rules to the correct hierarchy level | Skill | Unit 3.1 Challenge |
| Detecting hierarchy misconfigurations (team rules in user-level) | Skill | Unit 3.1 Challenge |

### Task Statement 3.2 — Custom slash commands & skills
**Covered in: Unit 3.2 + Cheat Sheet Section 2**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| .claude/commands/ (project) vs ~/.claude/commands/ (user) | Knowledge | Unit 3.2 Sec 1 |
| $ARGUMENTS placeholder for command argument substitution | Knowledge | Unit 3.2 Sec 1 |
| Nested directories create namespaced commands (test/unit.md -> /project:test:unit) | Knowledge | Unit 3.2 Sec 1 |
| SKILL.md with YAML frontmatter (name, description, context) | Knowledge | Unit 3.2 Sec 1 |
| context: fork runs skill in isolated context (no conversation bleed) | Knowledge | Unit 3.2 Sec 1, Key Insight |
| Same-context review is biased; fork provides independent perspective | Knowledge | Unit 3.2 Phase 1 |
| Building commands with $ARGUMENTS for team sharing | Skill | Unit 3.2 Challenge |
| Building skills with context: fork for independent review | Skill | Unit 3.2 Challenge |
| Classifying workflows as command vs skill | Skill | Unit 3.2 Challenge |

### Task Statement 3.3 — Path-specific rules with glob patterns
**Covered in: Unit 3.3 + Cheat Sheet Section 3**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| .claude/rules/ YAML frontmatter with paths: field | Knowledge | Unit 3.3 Sec 1 |
| Glob patterns: * (single level) vs ** (recursive) | Knowledge | Unit 3.3 Sec 1 |
| Rules files vs directory CLAUDE.md: when to use each | Knowledge | Unit 3.3 Sec 1 |
| Rules and directory CLAUDE.md both load and merge when applicable | Knowledge | Unit 3.3 Sec 1 |
| Cross-cutting concerns (all test files) -> rules file, not duplicated CLAUDE.md | Knowledge | Unit 3.3 Exam Trap |
| Writing glob patterns for specific file types | Skill | Unit 3.3 Challenge |
| Matching files against glob patterns | Skill | Unit 3.3 Challenge |
| Validating rule coverage (precision and recall) | Skill | Unit 3.3 Challenge |
| Designing separate rules for similar file types (migrations vs seeds) | Skill | Unit 3.3 Challenge |

### Task Statement 3.4 — Plan mode vs direct execution
**Covered in: Unit 3.4 + Cheat Sheet Section 4**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Complexity signals: scope, clarity, familiarity, risk | Knowledge | Unit 3.4 Sec 1 |
| Plan mode for multi-file, unclear, unknown codebase, high-risk tasks | Knowledge | Unit 3.4 Sec 1 |
| Direct execution for single-file, clear, well-known, low-risk tasks | Knowledge | Unit 3.4 Sec 1 |
| Plan-then-execute is a two-phase workflow | Knowledge | Unit 3.4 Sec 1 |
| Approved plans should be executed directly (no re-planning) | Knowledge | Unit 3.4 Exam Trap |
| Explore subagent: read-only, safe codebase exploration | Knowledge | Unit 3.4 Sec 1 |
| Assessing task complexity along multiple dimensions | Skill | Unit 3.4 Challenge |
| Building a decision tree for mode recommendation | Skill | Unit 3.4 Challenge |
| Classifying diverse tasks as plan or direct | Skill | Unit 3.4 Challenge |

### Task Statement 3.5 — Iterative refinement techniques
**Covered in: Unit 3.5 + Cheat Sheet Section 5**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Input/output examples for format/style issues | Knowledge | Unit 3.5 Sec 1 |
| Test-driven iteration: tests as automated specification | Knowledge | Unit 3.5 Phase 2 |
| Interview pattern: clarifying questions before generating | Knowledge | Unit 3.5 Phase 3 |
| Targeted feedback: specific errors, not vague instructions | Knowledge | Unit 3.5 Phase 1 |
| Test-driven iteration prevents regressions automatically | Knowledge | Unit 3.5 Key Insight |
| Combining interview + TDD for best results | Knowledge | Unit 3.5 Phase 3 |
| Building prompts with test cases as specification | Skill | Unit 3.5 Challenge |
| Generating clarifying interview questions | Skill | Unit 3.5 Challenge |
| Constructing retry prompts with specific error feedback | Skill | Unit 3.5 Challenge |

### Task Statement 3.6 — CI/CD integration
**Covered in: Unit 3.6 + Cheat Sheet Section 6**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| -p flag for headless (non-interactive) mode | Knowledge | Unit 3.6 Sec 1 |
| --output-format json for machine-readable output | Knowledge | Unit 3.6 Sec 1 |
| --json-schema for enforcing output schema | Knowledge | Unit 3.6 Sec 1 |
| Session isolation: -p starts fresh by default | Knowledge | Unit 3.6 Key Insight |
| --continue for multi-step pipelines with session continuity | Knowledge | Unit 3.6 Sec 1 |
| Prior findings feed-forward: capture JSON, inject into next prompt | Knowledge | Unit 3.6 Sec 1 |
| Per-file review to prevent attention dilution | Knowledge | Unit 3.6 Phase 2 |
| Building CI review prompts with explicit criteria and JSON output | Skill | Unit 3.6 Challenge |
| Aggregating per-file findings into a CI report with pass/fail | Skill | Unit 3.6 Challenge |
| Generating fix suggestions for findings | Skill | Unit 3.6 Challenge |

---

## Coverage Verification

- Task Statement 3.1: 11/11 concepts covered
- Task Statement 3.2: 9/9 concepts covered
- Task Statement 3.3: 9/9 concepts covered
- Task Statement 3.4: 9/9 concepts covered
- Task Statement 3.5: 9/9 concepts covered
- Task Statement 3.6: 10/10 concepts covered
- **Total: 57/57 testable concepts from Domain 3**

## Cross-Reference: Exam Scenarios Using Domain 3

| Scenario | How Domain 3 appears |
|----------|---------------------|
| Scenario 1: Multi-Team Dev | CLAUDE.md hierarchy for team rules, .claude/rules/ for cross-cutting standards |
| Scenario 3: Code Review Bot | CI/CD integration (-p flag, JSON output), plan mode for complex reviews |
| Scenario 5: CI/CD Pipeline | -p flag, --output-format json, session isolation, per-file review, multi-step pipelines |
| Scenario 6: Data Extraction | Iterative refinement (TDD for extraction accuracy), commands for reusable workflows |
