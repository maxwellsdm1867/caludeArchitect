# Module 3: Claude Code Configuration & Workflows

**Exam Domain 3 — 20% of scored content**  
**Phase 2 (Tooling) — Prerequisites: Module 1**

## Why this is Module 3

CLAUDE.md files, commands, skills, and rules are all prompts in disguise. You need prompt engineering skills (Module 1) before configuring Claude Code effectively. This module is also where you learn the tooling you'll use to *run* all the exercises in later modules.

## Units

| Unit | Topic | Key exam concepts |
|------|-------|-------------------|
| [3.1](unit-3.1-claude-md-hierarchy/overview.html) | CLAUDE.md hierarchy & modular organization | User/project/directory levels, @import, .claude/rules/, /memory command |
| [3.2](unit-3.2-commands-skills/overview.html) | Custom slash commands & skills | .claude/commands/ vs ~/.claude/commands/, SKILL.md frontmatter, context: fork |
| [3.3](unit-3.3-path-specific-rules/overview.html) | Path-specific rules with glob patterns | .claude/rules/ YAML frontmatter, paths field, glob patterns vs directory CLAUDE.md |
| [3.4](unit-3.4-plan-vs-direct/overview.html) | Plan mode vs direct execution | Complexity assessment, Explore subagent, combining plan + execute |
| [3.5](unit-3.5-iterative-refinement/overview.html) | Iterative refinement techniques | Input/output examples, test-driven iteration, interview pattern |
| [3.6](unit-3.6-cicd-integration/overview.html) | CI/CD integration | -p flag, --output-format json, --json-schema, session isolation, prior findings |

## Key mental models

### The CLAUDE.md hierarchy

```
~/.claude/CLAUDE.md          ← user-level: personal preferences, NOT shared via git
   ↓ (merged with)
.claude/CLAUDE.md            ← project-level: team standards, shared via git
   or root CLAUDE.md
   ↓ (merged with)
subdirectory/CLAUDE.md       ← directory-level: package-specific rules
```

**Exam trap:** A new team member doesn't get your rules because they're in `~/.claude/CLAUDE.md` (user-level, not version controlled). Move to `.claude/CLAUDE.md` for team-wide rules.

### When to use what

| Need | Mechanism |
|------|-----------|
| Universal team standards | Project-level `.claude/CLAUDE.md` or `.claude/rules/` |
| Rules that apply to specific file types (all test files) | `.claude/rules/` with `paths: ["**/*.test.*"]` |
| Rules that apply to a specific directory | Subdirectory `CLAUDE.md` |
| On-demand task-specific workflow | `.claude/skills/` with SKILL.md |
| Team-shared commands | `.claude/commands/` |
| Personal commands | `~/.claude/commands/` |

### Plan mode decision rule

```
Use plan mode when:
├── Architectural decisions with multiple valid approaches
├── Multi-file changes (restructuring, migration)
├── Unknown codebase that needs exploration first
└── Changes affecting 10+ files

Use direct execution when:
├── Single-file bug fix with clear stack trace
├── Adding a validation check to one function
├── Well-understood change with obvious implementation
└── Following up on a plan that was already approved
```
