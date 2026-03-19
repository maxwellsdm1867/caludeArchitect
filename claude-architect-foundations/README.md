# Claude Certified Architect — Foundations Study Guide

A hands-on, resequenced learning platform for the [Claude Certified Architect – Foundations](https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request) certification exam. Built to be worked through with **Claude Code**, **Jupyter notebooks**, and **interactive HTML overviews**.

> **Exam Guide**: Download the official exam guide from [Anthropic's certification page](https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request) (not included in this repo).

## Why this repo exists

The official exam guide orders domains by exam weight (agentic architecture at 27% comes first). That's a terrible *learning* sequence — you can't orchestrate agents if you don't yet understand prompts, tools, or context management. This repo resequences everything bottom-up so each module builds on the last.

## Exam overview

| Detail | Value |
|--------|-------|
| Format | Multiple choice (1 correct, 3 distractors) |
| Passing score | 720 / 1,000 |
| Scenarios | 4 of 6 picked at random |
| Penalty for guessing | None |

## Learning sequence

```
Phase 1 — Foundations (weeks 1–3)
  ├── Module 1: Prompt Engineering & Structured Output    (Domain 4 — 20%)
  └── Module 2: Context Management & Reliability          (Domain 5 — 15%)
        ↓ (you now understand how Claude thinks, fails, and recovers)
Phase 2 — Tooling (weeks 3–5)
  ├── Module 3: Claude Code Configuration & Workflows     (Domain 3 — 20%)
  └── Module 4: Tool Design & MCP Integration             (Domain 2 — 18%)
        ↓ (you can now configure Claude Code, design tools, wire up MCP)
Phase 3 — Integration (weeks 5–7)
  └── Module 5: Agentic Architecture & Orchestration      (Domain 1 — 27%)
        ↓ (agents orchestrate everything above: prompts, tools, context, Claude Code)
Phase 4 — Capstone (weeks 7–8)
  └── Scenario-based practice exams (all 6 scenarios)
```

### Why this order, not the exam guide order

| Exam guide order | Problem | Our order |
|---|---|---|
| Domain 1: Agentic Architecture (27%) | Agents USE prompts, tools, context — you need those first | Module 5 (last) |
| Domain 2: Tool Design & MCP (18%) | Tool descriptions ARE prompts — need prompt skills first | Module 4 |
| Domain 3: Claude Code Config (20%) | CLAUDE.md IS a prompt — need prompt skills first | Module 3 |
| Domain 4: Prompt Engineering (20%) | No prerequisites — foundational skill | Module 1 (first) |
| Domain 5: Context Management (15%) | No prerequisites — needed by all other domains | Module 2 (first) |

## How to use this repo

### Prerequisites

- Python 3.10+
- An Anthropic API key
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- JupyterLab

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/claude-architect-foundations.git
cd claude-architect-foundations
pip install -r requirements.txt          # anthropic, jupyter, pydantic, python-dotenv
```

Create a `.env` file in the repo root with your API key (already in `.gitignore`):
```bash
echo 'ANTHROPIC_API_KEY=sk-ant-...' > ../.env
```

### Start JupyterLab

```bash
./jupyter.sh start    # starts JupyterLab on localhost:8888
./jupyter.sh stop     # stop the server
./jupyter.sh status   # check if running
```

Or use the `/jupyter` slash command in Claude Code to start and verify.

Open notebooks at: `http://localhost:8888/?token=claude_architect_token`

Notebooks auto-load the API key from `.env` via `python-dotenv` in their first code cell — no need to export the env var manually.

### Learning Loop (per unit, ~45 min)

Each unit follows 3 stages — fail first, then understand, then prove it:

```
1. CARD  (HTML, 2-3 min)     → Core idea + decision tree + exam trap
2. LAB   (Jupyter, 30 min)   → Wrong approach fails → understand why → build the right way
3. DRILL (quiz, 5 min)       → Exam-format MC — which technique for this scenario?
```

The lab is where learning happens. It starts with the **wrong approach** — you run it, watch it fail, understand why, then build the correct solution. The checker validates your work.

### Quick Start

```bash
# Navigate the platform via CLI
python run.py                              # Terminal dashboard
python run.py open module-1 unit-1.1 card  # Open concept card
python run.py open module-1 unit-1.1 lab   # Open lab notebook
python run.py quiz module-1 unit-1.1       # Take the drill (exam-style quiz)
python run.py dashboard                    # Open progress dashboard
python run.py cheatsheet module-1          # Open module cheat sheet
```

### With Claude Code

This repo is designed to be used alongside Claude Code:

```bash
cd claude-architect-foundations
claude  # start Claude Code in the repo root
```

Claude Code will pick up the `.claude/` config and CLAUDE.md files in this repo as part of the learning exercises (Module 3 specifically teaches you how these work).

#### Jupyter MCP Integration

With JupyterLab running, Claude Code can manage notebooks through MCP tools:

- **`NotebookEdit`** — insert, replace, or delete notebook cells directly from Claude Code
- **`/jupyter`** — slash command to start JupyterLab and verify the MCP connection

Recommended workflow: Claude Code edits notebook cells via MCP, you run them interactively in the browser with Shift+Enter. This keeps the feedback loop tight — Claude handles the code, you see the results live.

## Module index

| Module | Directory | Domain | Weight | Prerequisites |
|--------|-----------|--------|--------|---------------|
| [Module 1: Prompt Engineering & Structured Output](module-1-prompt-engineering/) | `module-1-prompt-engineering/` | Domain 4 | 20% | None |
| [Module 2: Context Management & Reliability](module-2-context-reliability/) | `module-2-context-reliability/` | Domain 5 | 15% | None |
| [Module 3: Claude Code Configuration & Workflows](module-3-claude-code-config/) | `module-3-claude-code-config/` | Domain 3 | 20% | Module 1 |
| [Module 4: Tool Design & MCP Integration](module-4-tool-design-mcp/) | `module-4-tool-design-mcp/` | Domain 2 | 18% | Modules 1, 2 |
| [Module 5: Agentic Architecture & Orchestration](module-5-agentic-architecture/) | `module-5-agentic-architecture/` | Domain 1 | 27% | Modules 1–4 |
| [Capstone: Scenario Practice](capstone/) | `capstone/` | All | 100% | Modules 1–5 |

## Exam scenarios you'll encounter

The exam picks 4 of these 6 at random. Each scenario spans multiple domains — this is why isolated topic knowledge isn't enough.

1. **Customer Support Resolution Agent** — Domains 1, 2, 5
2. **Code Generation with Claude Code** — Domains 3, 5
3. **Multi-Agent Research System** — Domains 1, 2, 5
4. **Developer Productivity with Claude** — Domains 2, 3, 1
5. **Claude Code for Continuous Integration** — Domains 3, 4
6. **Structured Data Extraction** — Domains 4, 5

## Key principles this program teaches

These patterns come up repeatedly across exam questions:

- **Programmatic enforcement > prompt-based guidance** when compliance must be guaranteed
- **Tool descriptions are the #1 lever** for tool selection reliability
- **Few-shot examples beat detailed instructions** for consistency
- **Structured errors with metadata** enable intelligent recovery (not generic "operation failed")
- **Context degrades** — extract facts, trim tool output, use scratchpad files
- **Independent review instances** catch more bugs than self-review
- **Batch API is for latency-tolerant work only** — never blocking workflows
- **Subagents don't inherit context** — pass it explicitly every time
- **4-5 tools per agent max** — more degrades selection reliability

## License

MIT — study, share, contribute.
