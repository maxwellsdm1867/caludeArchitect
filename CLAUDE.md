# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a study repository for the **Claude Certified Architect – Foundations** certification exam. It contains a resequenced, bottom-up learning program with markdown units, Jupyter notebooks, and a capstone of 6 scenario-based practice exams. All hands-on work uses the Anthropic Python SDK.

## Repository Structure

```
caludeArchitect/
├── module-1-prompt-engineering/     ← Domain 4 (20%) — 6 units
├── module-2-context-reliability/    ← Domain 5 (15%) — 6 units
├── module-3-claude-code-config/     ← Domain 3 (20%) — 6 units
├── module-4-tool-design-mcp/        ← Domain 2 (18%) — 5 units
├── module-5-agentic-architecture/   ← Domain 1 (27%) — 7 units
├── capstone/                        ← All domains — 6 scenario practice exams
├── assets/                          ← Shared CSS, JS, templates
└── run.py                           ← CLI dashboard
```

Modules are intentionally resequenced from the exam guide order. The exam lists Domain 1 (Agentic Architecture) first by weight, but this repo teaches it last because it integrates all other domains.

Each unit follows 3 stages (Card → Lab → Drill):
- `unit-N.N-*/overview.html` — concept card (2-3 min: decision tree + exam trap)
- `unit-N.N-*/lab.ipynb` — Jupyter lab (failure-first: wrong approach → understand → build right)
- `unit-N.N-*/quiz.json` — drill (5 exam-format MC questions)
- `unit-N.N-*/challenge/` — starter code + pytest checker (embedded in lab)
- `cheatsheet.html` — dense reference sheet per module

## Setup & Running

### 1. Install dependencies
```bash
pip install -r requirements.txt          # anthropic, jupyter, pydantic, python-dotenv
```

### 2. Configure API key
Create a `.env` file in the repo root (already in `.gitignore`):
```bash
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
```
Notebooks load this automatically via `python-dotenv` in their first code cell.

### 3. Start JupyterLab
```bash
./jupyter.sh start                       # starts on port 8888
./jupyter.sh stop                        # stop the server
./jupyter.sh status                      # check if running
```
Or use the `/jupyter` slash command in Claude Code to start and verify.

JupyterLab URL: `http://localhost:8888/?token=claude_architect_token`

### 4. Run notebooks
Open notebooks directly in JupyterLab and run cells with Shift+Enter. Alternatively use the CLI dashboard:
```bash
python run.py                            # terminal dashboard
python run.py open module-1 unit-1.1 card  # concept card in browser
python run.py open module-1 unit-1.1 lab   # lab notebook
python run.py quiz module-1 unit-1.1       # drill in terminal
```

Default model for exercises: `claude-sonnet-4-20250514`

## JupyterLab MCP Integration

When working with Claude Code, use the Jupyter MCP server for notebook operations:
- **`NotebookEdit`** — edit notebook cells (insert, replace, delete) without opening the browser
- **`/jupyter`** — slash command to start JupyterLab and verify the MCP connection

The JupyterLab server runs on `localhost:8888` with token `claude_architect_token`. Claude Code can read, edit, and manage notebook cells through MCP while you run them interactively in the browser.

## Conventions

- Notebooks use `anthropic.Anthropic()` client (reads `ANTHROPIC_API_KEY` from `.env` via `python-dotenv`)
- Each notebook's first code cell loads `.env` — do not remove this cell
- Test files use pytest-style assertions (`assert x == y`), one behavior per test, named `test_<behavior>_<condition>_<expected>`
- Path-specific Claude rules live in `.claude/rules/` with YAML frontmatter `paths:` globs
- Module order is a dependency chain — each module builds on the previous

## Exam Context

- Format: multiple choice, 1 correct + 3 distractors, no guessing penalty
- Passing: 720/1000 scaled score
- 4 of 6 scenarios picked at random; each scenario spans multiple domains
- Questions test which technique to use in a specific production scenario, not general knowledge
