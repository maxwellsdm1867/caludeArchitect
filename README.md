# Claude Certified Architect — Foundations Study Guide

A hands-on, resequenced learning platform for the [Claude Certified Architect – Foundations](https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request) certification exam. 30 units across 5 modules, 6 capstone scenario exams, 206 mapped exam concepts.

Built to be worked through with **Claude Code**, **Jupyter notebooks**, and **interactive HTML overviews**.

## Quick start

```bash
git clone https://github.com/maxwellsdm1867/caludeArchitect.git
cd caludeArchitect/claude-architect-foundations
pip install -r requirements.txt
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
./jupyter.sh start
```

Open notebooks at `http://localhost:8888/?token=claude_architect_token` and run cells with Shift+Enter.

## What's inside

```
claude-architect-foundations/
├── module-1-prompt-engineering/     ← Domain 4 (20%) — 6 units, 47 concepts
├── module-2-context-reliability/    ← Domain 5 (15%) — 6 units, 48 concepts
├── module-3-claude-code-config/     ← Domain 3 (20%) — 6 units, 57 concepts
├── module-4-tool-design-mcp/        ← Domain 2 (18%) — 5 units, 44 concepts
├── module-5-agentic-architecture/   ← Domain 1 (27%) — 7 units, 57 concepts
└── capstone/                        ← All domains — 6 scenarios, 42 questions
```

Modules are intentionally resequenced from the exam guide. The exam lists Agentic Architecture first by weight, but this repo teaches it last because it integrates all other domains.

## Learning approach

Each of the 30 units follows 3 stages — fail first, then understand, then prove it:

| Stage | Format | Time | What happens |
|-------|--------|------|--------------|
| Card | HTML overview | 2-3 min | Core concept + decision tree + exam trap |
| Lab | Jupyter notebook | 30 min | Wrong approach fails → understand why → build it right |
| Drill | JSON quiz | 5 min | 5 exam-format MC questions per unit |

Plus a challenge with starter code and pytest checker in every unit.

```bash
python run.py                              # Terminal dashboard
python run.py open module-1 unit-1.1 card  # Open concept card
python run.py open module-1 unit-1.1 lab   # Open lab notebook
python run.py quiz module-1 unit-1.1       # Take the drill
```

## Module map

| Module | Domain | Weight | Units | Key topics |
|--------|--------|--------|-------|------------|
| **1. Prompt Engineering** | D4 | 20% | 6 | Explicit criteria, few-shot, tool_use schemas, validation-retry, batch API, multi-pass review |
| **2. Context & Reliability** | D5 | 15% | 6 | Context degradation, escalation triggers, error propagation, scratchpads, human review, provenance |
| **3. Claude Code Config** | D3 | 20% | 6 | CLAUDE.md hierarchy, commands/skills, path rules, plan mode, iterative refinement, CI/CD integration |
| **4. Tool Design & MCP** | D2 | 18% | 5 | Tool descriptions, structured errors, tool distribution, MCP servers, built-in tools |
| **5. Agentic Architecture** | D1 | 27% | 7 | Agentic loop, coordinator-subagent, context passing, enforcement, hooks, decomposition, sessions |
| **Capstone** | All | 100% | 6 | Cross-domain scenario exams (customer support, code gen, research, dev productivity, CI/CD, extraction) |

## Using with Claude Code

```bash
cd caludeArchitect
claude
```

Claude Code picks up the CLAUDE.md and `.claude/` config automatically. With JupyterLab running, Claude Code can edit notebook cells via MCP (`NotebookEdit`) while you run them interactively in the browser. Use `/jupyter` in Claude Code to start JupyterLab.

## Exam overview

| Detail | Value |
|--------|-------|
| Format | Multiple choice (1 correct, 3 distractors) |
| Passing score | 720 / 1,000 |
| Scenarios | 4 of 6 picked at random |
| Penalty for guessing | None |

## Key patterns the exam tests

- **Programmatic enforcement > prompt-based guidance** for compliance-critical rules
- **Tool descriptions are the #1 lever** for selection reliability
- **Few-shot examples beat detailed instructions** for consistency
- **Context degrades** over long sessions — use scratchpads, subagents, `/compact`
- **Subagents don't inherit context** — pass it explicitly every time
- **4-5 tools per agent max** — more degrades selection
- **Independent review instances** catch more than self-review
- **Batch API has no latency SLA** — never use for blocking workflows

See the full [study guide README](claude-architect-foundations/README.md) for setup details, the complete learning sequence, and exam scenario breakdowns.

## License

MIT
