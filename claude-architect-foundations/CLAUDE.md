# Claude Architect Foundations Study Repo

Study platform for the Claude Certified Architect – Foundations exam.

## Context
- All labs use the Anthropic Python SDK (`claude-sonnet-4-20250514`)
- API key is loaded from `.env` in the repo root via `python-dotenv` (first code cell in each notebook)
- Labs follow failure-first pedagogy: wrong approach → see it fail → build the right way
- JupyterLab runs on `localhost:8888` — start with `./jupyter.sh start` or `/jupyter` in Claude Code

## Per-unit structure (3 stages)
- `overview.html` — concept card (2-3 min read: decision tree + key insight + exam trap)
- `lab.ipynb` — Jupyter lab (failure-first walkthrough + challenge with checker)
- `quiz.json` — exam-format drill (5 MC questions)

## Conventions
- Each module builds on the previous — don't skip ahead
- Cheat sheets are the reference layer (one per module)
- `run.py` is the CLI navigator; `progress.json` tracks completion
- Challenges live in `unit-*/challenge/` with `challenge.py` (starter) and `checker.py` (pytest)
