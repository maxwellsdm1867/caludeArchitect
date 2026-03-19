# Claude Certified Architect — Foundations Study Guide

> **Status:** In development — Module 1 (Prompt Engineering) complete, Modules 2–5 scaffolded.

A hands-on, resequenced learning platform for the [Claude Certified Architect – Foundations](https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request) certification exam. Built to be worked through with **Claude Code**, **Jupyter notebooks**, and **interactive HTML overviews**.

## Quick start

```bash
git clone https://github.com/maxwellsdm1867/caludeArchitect.git
cd caludeArchitect/claude-architect-foundations
pip install -r requirements.txt
```

Create a `.env` in the repo root with your API key (already gitignored):
```bash
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
```

Start JupyterLab:
```bash
./jupyter.sh start
```
Open notebooks at `http://localhost:8888/?token=claude_architect_token` and run cells with Shift+Enter. Notebooks auto-load the API key from `.env`.

## What's inside

```
claude-architect-foundations/
├── module-1-prompt-engineering/     ← Domain 4 (20%) — COMPLETE
├── module-2-context-reliability/    ← Domain 5 (15%) — scaffolded
├── module-3-claude-code-config/     ← Domain 3 (20%) — scaffolded
├── module-4-tool-design-mcp/        ← Domain 2 (18%) — scaffolded
├── module-5-agentic-architecture/   ← Domain 1 (27%) — scaffolded
└── capstone/                        ← All domains — scaffolded
```

Modules are intentionally resequenced from the exam guide. The exam lists Agentic Architecture first by weight, but this repo teaches it last because it integrates all other domains.

## Learning approach

Each unit follows 3 stages:

| Stage | Format | Time | What happens |
|-------|--------|------|--------------|
| Card | HTML | 2–3 min | Core concept + decision tree + exam trap |
| Lab | Jupyter | 30 min | Wrong approach fails → understand why → build it right |
| Drill | JSON quiz | 5 min | Exam-format MC questions |

## Using with Claude Code

```bash
cd caludeArchitect
claude
```

Claude Code picks up the CLAUDE.md and `.claude/` config automatically. With JupyterLab running, Claude Code can edit notebook cells via MCP (`NotebookEdit`) while you run them interactively in the browser.

Use `/jupyter` in Claude Code to start JupyterLab.

## Exam overview

| Detail | Value |
|--------|-------|
| Format | Multiple choice (1 correct, 3 distractors) |
| Passing score | 720 / 1,000 |
| Scenarios | 4 of 6 picked at random |
| Penalty for guessing | None |

See the full [study guide README](claude-architect-foundations/README.md) for the complete learning sequence, module index, and exam scenarios.

## License

MIT
