#!/usr/bin/env python3
"""
Claude Architect Foundations — CLI Navigator

Usage:
  python run.py                                       Show status dashboard in terminal
  python run.py module-1                              Show Module 1 progress
  python run.py module-1 unit-1.1                     Show Unit 1.1 status
  python run.py open module-1 unit-1.1 card            Open concept card in browser
  python run.py open module-1 unit-1.1 lab             Open lab notebook
  python run.py open module-1 unit-1.1 drill           Run quiz (drill) in terminal
  python run.py check module-1 unit-1.1               Run the challenge checker
  python run.py quiz module-1 unit-1.1                Run quiz in terminal
  python run.py dashboard                             Open dashboard.html in browser
  python run.py cheatsheet module-1                   Open module cheat sheet in browser
"""

import argparse
import json
import os
import re
import subprocess
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

# ── ANSI color helpers ──────────────────────────────────────────────────────

SUPPORTS_COLOR = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _ansi(code: str, text: str) -> str:
    if not SUPPORTS_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(t: str) -> str:
    return _ansi("1", t)


def dim(t: str) -> str:
    return _ansi("2", t)


def green(t: str) -> str:
    return _ansi("32", t)


def red(t: str) -> str:
    return _ansi("31", t)


def amber(t: str) -> str:
    return _ansi("33", t)


def cyan(t: str) -> str:
    return _ansi("36", t)


def magenta(t: str) -> str:
    return _ansi("35", t)


# ── Paths ───────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent
PROGRESS_FILE = ROOT / "progress.json"

MODULE_DIRS = {
    "module-1": "module-1-prompt-engineering",
    "module-2": "module-2-context-reliability",
    "module-3": "module-3-claude-code-config",
    "module-4": "module-4-tool-design-mcp",
    "module-5": "module-5-agentic-architecture",
}

UNIT_DIRS = {
    "unit-1.1": "unit-1.1-explicit-criteria",
    "unit-1.2": "unit-1.2-few-shot",
    "unit-1.3": "unit-1.3-structured-output",
    "unit-1.4": "unit-1.4-validation-retry",
    "unit-1.5": "unit-1.5-batch-processing",
    "unit-1.6": "unit-1.6-multi-pass-review",
    "unit-2.1": "unit-2.1-context-preservation",
    "unit-2.2": "unit-2.2-escalation-patterns",
    "unit-2.3": "unit-2.3-error-propagation",
    "unit-2.4": "unit-2.4-codebase-context",
    "unit-2.5": "unit-2.5-human-review-workflows",
    "unit-2.6": "unit-2.6-provenance",
    "unit-3.1": "unit-3.1-claude-md-hierarchy",
    "unit-3.2": "unit-3.2-commands-skills",
    "unit-3.3": "unit-3.3-path-specific-rules",
    "unit-3.4": "unit-3.4-plan-vs-direct",
    "unit-3.5": "unit-3.5-iterative-refinement",
    "unit-3.6": "unit-3.6-ci-cd-integration",
    "unit-4.1": "unit-4.1-tool-descriptions",
    "unit-4.2": "unit-4.2-structured-errors",
    "unit-4.3": "unit-4.3-tool-distribution",
    "unit-4.4": "unit-4.4-mcp-integration",
    "unit-4.5": "unit-4.5-built-in-tools",
    "unit-5.1": "unit-5.1-agentic-loop",
    "unit-5.2": "unit-5.2-coordinator-subagent",
    "unit-5.3": "unit-5.3-subagent-context",
    "unit-5.4": "unit-5.4-enforcement-handoff",
    "unit-5.5": "unit-5.5-agent-sdk-hooks",
    "unit-5.6": "unit-5.6-task-decomposition",
    "unit-5.7": "unit-5.7-session-management",
}


# ── Progress I/O ────────────────────────────────────────────────────────────


def load_progress() -> dict:
    """Load progress.json, returning the parsed dict."""
    if not PROGRESS_FILE.exists():
        print(red("Error: progress.json not found at " + str(PROGRESS_FILE)))
        sys.exit(1)
    with open(PROGRESS_FILE, "r") as f:
        return json.load(f)


def save_progress(data: dict) -> None:
    """Write progress.json back to disk."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def touch_activity(data: dict) -> None:
    """Update last_activity and ensure started is set."""
    now = datetime.now(timezone.utc).isoformat()
    data["student"]["last_activity"] = now
    if data["student"]["started"] is None:
        data["student"]["started"] = now


# ── Path resolvers ──────────────────────────────────────────────────────────


def module_dir(module_id: str) -> Path:
    dirname = MODULE_DIRS.get(module_id)
    if not dirname:
        print(red(f"Unknown module: {module_id}"))
        print(dim(f"Valid modules: {', '.join(sorted(MODULE_DIRS.keys()))}"))
        sys.exit(1)
    return ROOT / dirname


def unit_dir(module_id: str, unit_id: str) -> Path:
    dirname = UNIT_DIRS.get(unit_id)
    if not dirname:
        print(red(f"Unknown unit: {unit_id}"))
        # Show valid units for the module
        prefix = module_id.split("-")[1] + "."
        valid = [k for k in UNIT_DIRS if k.startswith("unit-" + prefix)]
        print(dim(f"Valid units for {module_id}: {', '.join(sorted(valid))}"))
        sys.exit(1)
    return module_dir(module_id) / dirname


def validate_module(data: dict, module_id: str) -> dict:
    """Validate module_id exists in progress data and return its dict."""
    if module_id not in data["modules"]:
        print(red(f"Module '{module_id}' not found in progress.json"))
        sys.exit(1)
    return data["modules"][module_id]


def validate_unit(data: dict, module_id: str, unit_id: str) -> tuple:
    """Validate both module and unit, return (module_dict, unit_dict)."""
    mod = validate_module(data, module_id)
    if unit_id not in mod["units"]:
        print(red(f"Unit '{unit_id}' not found in module '{module_id}'"))
        valid = list(mod["units"].keys())
        print(dim(f"Valid units: {', '.join(valid)}"))
        sys.exit(1)
    return mod, mod["units"][unit_id]


# ── Stage icon helper ───────────────────────────────────────────────────────


def stage_icon(done: bool, attempted: bool = False, score=None) -> str:
    """Return a colored symbol for a stage's completion state."""
    if done:
        if score is not None and score < 70:
            return amber("~")
        return green("*")
    if attempted:
        return red("x")
    return dim(".")


def unit_status_line(unit_id: str, unit: dict) -> str:
    """Format a single unit's status as a compact line."""
    c = stage_icon(unit.get("card_read", unit.get("overview_read", False)))
    l = stage_icon(unit.get("lab_completed", unit.get("challenge_passed", False)), unit.get("lab_attempts", unit.get("challenge_attempts", 0)) > 0)
    d = stage_icon(
        unit.get("drill_score", unit.get("quiz_score")) is not None,
        unit.get("drill_attempts", unit.get("quiz_attempts", 0)) > 0,
        unit.get("drill_score", unit.get("quiz_score")),
    )
    stages = f"[{c}{l}{d}]"

    name = unit["name"]

    # Extra info
    extras = []
    if unit.get("lab_attempts", unit.get("challenge_attempts", 0)) > 0:
        passed = unit.get("lab_completed", unit.get("challenge_passed", False))
        status = green("passed") if passed else red("failed")
        extras.append(f"lab: {status}")
    qs = unit.get("drill_score", unit.get("quiz_score"))
    if qs is not None:
        color = green if qs >= 80 else amber if qs >= 60 else red
        extras.append(f"drill: {color(str(qs) + '%')}")
    extra_str = f"  ({', '.join(extras)})" if extras else ""

    return f"  {dim(unit_id):>18s}  {stages}  {name}{extra_str}"


# ── Commands ────────────────────────────────────────────────────────────────


def cmd_dashboard_terminal(data: dict) -> None:
    """Show compact progress overview in the terminal."""
    print()
    print(bold("  Claude Architect Foundations"))
    print(dim("  ─" * 30))
    print()

    # Overall stats
    total_stages = 0
    done_stages = 0
    total_units = 0
    done_units = 0

    def _unit_done(u):
        """Count completed stages for a unit (backward compatible)."""
        done = 0
        if u.get("card_read", u.get("overview_read", False)):
            done += 1
        if u.get("lab_completed", u.get("challenge_passed", False)):
            done += 1
        if u.get("drill_score", u.get("quiz_score")) is not None:
            done += 1
        return done

    stages_per_unit = 3

    for mod in data["modules"].values():
        for unit in mod["units"].values():
            total_units += 1
            d = _unit_done(unit)
            total_stages += stages_per_unit
            done_stages += d
            if d == stages_per_unit:
                done_units += 1

    pct = (done_stages / total_stages * 100) if total_stages > 0 else 0

    # Compute exam readiness
    readiness = 0.0
    total_weight = 0
    for mod in data["modules"].values():
        unit_list = list(mod["units"].values())
        mod_total = len(unit_list) * stages_per_unit
        mod_done = sum(_unit_done(u) for u in unit_list)
        mod_pct = mod_done / mod_total if mod_total > 0 else 0
        readiness += mod_pct * mod["weight"]
        total_weight += mod["weight"]
    readiness = readiness / total_weight * 100 if total_weight > 0 else 0

    print(f"  Overall:  {bold(f'{pct:.0f}%')}  ({done_stages}/{total_stages} stages, {done_units}/{total_units} units complete)")
    readiness_color = green if readiness >= 80 else amber if readiness >= 50 else red if readiness > 0 else dim
    print(f"  Exam Readiness: {readiness_color(f'{readiness:.0f}%')}  (weighted by domain %)")
    if data["student"]["last_activity"]:
        print(f"  Last activity:  {dim(data['student']['last_activity'][:19])}")
    print()

    # Legend
    print(dim("  Legend: [CLD]  C=Card  L=Lab  D=Drill"))
    print(dim("          " + green("*") + "=done  " + amber("~") + "=partial  " + red("x") + "=failed  " + dim(".") + "=not started"))
    print()

    # Per-module tables
    for mod_id, mod in data["modules"].items():
        unit_count = len(mod["units"])
        mod_stages = unit_count * stages_per_unit
        mod_done = sum(_unit_done(u) for u in mod["units"].values())
        mod_pct = (mod_done / mod_stages * 100) if mod_stages > 0 else 0

        domain = mod["domain"]
        weight = mod["weight"]
        header = f"  {bold(mod_id.upper())}  {mod['name']}  {dim(f'({domain}, {weight}%)')}"
        bar_width = 20
        filled = int(mod_pct / 100 * bar_width)
        bar_color = green if mod_pct >= 80 else amber if mod_pct >= 40 else red if mod_pct > 0 else dim
        bar = bar_color("=" * filled) + dim("-" * (bar_width - filled))
        print(f"{header}")
        print(f"  [{bar}] {mod_pct:.0f}%")

        for unit_id, unit in mod["units"].items():
            print(unit_status_line(unit_id, unit))

        print()

    # Capstone
    cap = data.get("capstone", {})
    scenarios = cap.get("scenarios_completed", [])
    mocks = cap.get("mock_exam_scores", [])
    if scenarios or mocks:
        print(bold("  CAPSTONE"))
        if scenarios:
            print(f"  Scenarios completed: {len(scenarios)}")
        if mocks:
            print(f"  Mock exam scores: {', '.join(str(s) for s in mocks)}")
        print()


def cmd_module(data: dict, module_id: str) -> None:
    """Show progress for a single module."""
    mod = validate_module(data, module_id)
    print()
    print(bold(f"  {module_id.upper()}: {mod['name']}"))
    print(dim(f"  {mod['domain']}  |  Exam weight: {mod['weight']}%"))
    print()

    print(dim("  Legend: [OWCQ]  " + green("*") + "=done  " + amber("~") + "=partial  " + red("x") + "=failed  " + dim(".") + "=not started"))
    print()

    for uid, unit in mod["units"].items():
        print(unit_status_line(uid, unit))
    print()

    cs = "Yes" if mod.get("cheatsheet_reviewed") else "No"
    print(dim(f"  Cheatsheet reviewed: {cs}"))
    print()


def cmd_unit(data: dict, module_id: str, unit_id: str) -> None:
    """Show detailed status for a single unit."""
    mod, unit = validate_unit(data, module_id, unit_id)
    print()
    print(bold(f"  {unit_id}: {unit['name']}"))
    print(dim(f"  Module: {mod['name']}  |  Task Statement: {unit['task_statement']}"))
    print()

    def status(done, label_done="Done", label_not="Not done"):
        return green(label_done) if done else dim(label_not)

    print(f"  Card:   {status(unit.get('card_read', unit.get('overview_read', False)), 'Read', 'Not read')}")
    print(f"  Lab:    {status(unit.get('lab_completed', unit.get('challenge_passed', False)), 'Completed', 'Not completed')}")

    lab_attempts = unit.get("lab_attempts", unit.get("challenge_attempts", 0))
    if lab_attempts > 0:
        lab_passed = unit.get("lab_completed", unit.get("challenge_passed", False))
        cs = green("Passed") if lab_passed else red("Not passed")
        print(f"            {cs}  ({lab_attempts} attempts)")
    else:
        print(f"            {dim('Not attempted')}")

    drill_score = unit.get("drill_score", unit.get("quiz_score"))
    drill_attempts = unit.get("drill_attempts", unit.get("quiz_attempts", 0))
    if drill_score is not None:
        qc = green if drill_score >= 80 else amber if drill_score >= 60 else red
        print(f"  Drill:  {qc(str(drill_score) + '%')}  ({drill_attempts} attempts)")
    elif drill_attempts > 0:
        print(f"  Drill:  {red('Not passed')}  ({drill_attempts} attempts)")
    else:
        print(f"  Drill:  {dim('Not taken')}")

    if unit["confidence"] is not None:
        print(f"  Confidence:   {unit['confidence']}/5")

    if unit["notes"]:
        print(f"  Notes:        {unit['notes']}")
    print()


def cmd_open(data: dict, module_id: str, unit_id: str, stage: str) -> None:
    """Open a stage file in the browser or appropriate application."""
    validate_unit(data, module_id, unit_id)
    ud = unit_dir(module_id, unit_id)

    if stage in ("overview", "card"):
        target = ud / "overview.html"
        if not target.exists():
            # Fall back to the markdown file in the module directory
            md_dir = module_dir(module_id)
            candidates = list(md_dir.glob(f"{unit_id}*.md"))
            if candidates:
                target = candidates[0]
            else:
                print(amber(f"Warning: overview.html not found at {target}"))
                return
    elif stage in ("walkthrough", "lab"):
        # Prefer lab.ipynb, fall back to any notebook
        target = ud / "lab.ipynb"
        if not target.exists():
            notebooks = list(ud.glob("*.ipynb"))
            if not notebooks:
                nb_dir = module_dir(module_id) / "notebooks"
                if nb_dir.exists():
                    notebooks = list(nb_dir.glob("*.ipynb"))
            if not notebooks:
                print(amber(f"No lab notebook found for {unit_id}"))
                return
            target = notebooks[0]
    elif stage == "challenge":
        target = ud / "challenge"
        if target.is_dir():
            # Look for the main challenge file
            py_files = list(target.glob("*.py"))
            if py_files:
                target = py_files[0]
            else:
                print(amber(f"No challenge Python file found in {target}"))
                return
        else:
            print(amber(f"Challenge directory not found at {target}"))
            return
    elif stage in ("quiz", "drill"):
        # Drill is the quiz stage — run interactively in terminal
        cmd_quiz(data, module_id, unit_id)
        return
    else:
        print(red(f"Unknown stage: {stage}"))
        print(dim("Valid stages: overview, walkthrough, challenge, quiz"))
        return

    url = target.as_uri() if hasattr(target, "as_uri") else "file://" + str(target)
    print(f"Opening {cyan(str(target.relative_to(ROOT)))}...")
    webbrowser.open(url)

    # Mark overview as read when opened
    if stage == "overview":
        mod_data = data["modules"][module_id]
        if "card_read" in mod_data["units"][unit_id]:
            mod_data["units"][unit_id]["card_read"] = True
        else:
            mod_data["units"][unit_id]["overview_read"] = True
        touch_activity(data)
        save_progress(data)
        print(green("Marked overview as read."))


def cmd_check(data: dict, module_id: str, unit_id: str) -> None:
    """Run pytest on the challenge checker and update progress."""
    mod, unit = validate_unit(data, module_id, unit_id)
    challenge_dir = unit_dir(module_id, unit_id) / "challenge"

    if not challenge_dir.exists():
        print(red(f"Challenge directory not found: {challenge_dir}"))
        return

    # Find checker file
    checker_files = list(challenge_dir.glob("checker*.py")) + list(
        challenge_dir.glob("test_*.py")
    )
    if not checker_files:
        print(red(f"No checker file found in {challenge_dir}"))
        print(dim("Expected: checker.py or test_*.py"))
        return

    checker = checker_files[0]
    print(bold(f"  Running challenge checker for {unit_id}: {unit['name']}"))
    print(dim(f"  File: {checker.relative_to(ROOT)}"))
    print()

    # Run pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(checker), "-v", "--tb=short"],
        cwd=str(challenge_dir),
        capture_output=True,
        text=True,
    )

    # Print output
    print(result.stdout)
    if result.stderr:
        print(dim(result.stderr))

    # Parse results
    passed = result.returncode == 0

    # Try to extract pass/total from pytest output
    score = 100 if passed else 0
    for line in result.stdout.splitlines():
        # Match lines like "2 passed, 1 failed" or "5 passed"
        if "passed" in line:
            import re

            m = re.search(r"(\d+) passed", line)
            f = re.search(r"(\d+) failed", line)
            if m:
                p = int(m.group(1))
                fa = int(f.group(1)) if f else 0
                total = p + fa
                score = int(p / total * 100) if total > 0 else 0

    # Update progress (backward compatible)
    attempts_key = "lab_attempts" if "lab_attempts" in unit else "challenge_attempts"
    unit[attempts_key] = unit.get(attempts_key, 0) + 1
    if passed:
        if "lab_completed" in unit:
            unit["lab_completed"] = True
        else:
            unit["challenge_passed"] = True
    touch_activity(data)
    save_progress(data)

    print()
    if passed:
        print(green(f"  PASSED  ({score}%)"))
    else:
        print(red(f"  FAILED  ({score}%)"))
        print(dim(f"  Attempts so far: {unit.get(attempts_key, 0)}"))
    print()


def cmd_quiz(data: dict, module_id: str, unit_id: str) -> None:
    """Run an interactive quiz in the terminal."""
    mod, unit = validate_unit(data, module_id, unit_id)
    quiz_file = unit_dir(module_id, unit_id) / "quiz.json"

    if not quiz_file.exists():
        print(red(f"Quiz file not found: {quiz_file}"))
        return

    with open(quiz_file, "r") as f:
        quiz_data = json.load(f)

    questions = quiz_data if isinstance(quiz_data, list) else quiz_data.get("questions", [])

    if not questions:
        print(red("No questions found in quiz file."))
        return

    print()
    print(bold(f"  Quiz: {unit_id} — {unit['name']}"))
    print(dim(f"  {len(questions)} questions"))
    print(dim("  ─" * 25))
    print()

    correct = 0
    total = len(questions)

    for i, q in enumerate(questions, 1):
        question_text = q.get("question", q.get("text", ""))
        raw_options = q.get("options", q.get("choices", []))
        answer_key = q.get("answer", q.get("correct", ""))

        # Normalize options: dict {"A": "...", "B": "..."} → list of strings
        if isinstance(raw_options, dict):
            options = list(raw_options.values())
        else:
            options = raw_options

        # Handle answer as index or letter
        if isinstance(answer_key, int):
            correct_idx = answer_key
        elif isinstance(answer_key, str) and len(answer_key) == 1 and answer_key.upper() in "ABCDEFGH":
            correct_idx = ord(answer_key.upper()) - ord("A")
        else:
            # Try to match answer text
            correct_idx = -1
            for j, opt in enumerate(options):
                opt_text = opt if isinstance(opt, str) else opt.get("text", "")
                if opt_text == answer_key or str(j) == str(answer_key):
                    correct_idx = j
                    break

        print(f"  {bold(f'Q{i}.')} {question_text}")
        for j, opt in enumerate(options):
            opt_text = opt if isinstance(opt, str) else opt.get("text", "")
            # Strip leading letter prefix to avoid doubling (e.g., "A) ..." → "...")
            opt_text = re.sub(r'^[A-Za-z][.)]\s*', '', opt_text)
            letter = chr(ord("A") + j)
            print(f"    {letter}) {opt_text}")

        # Get answer
        while True:
            try:
                raw = input(f"\n  Your answer (A-{chr(ord('A') + len(options) - 1)}): ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                print("\n")
                print(amber("  Quiz cancelled."))
                return

            if len(raw) == 1 and "A" <= raw <= chr(ord("A") + len(options) - 1):
                chosen = ord(raw) - ord("A")
                break
            print(red(f"  Please enter a letter A-{chr(ord('A') + len(options) - 1)}"))

        if chosen == correct_idx:
            print(green("  Correct!"))
            correct += 1
        else:
            correct_letter = chr(ord("A") + correct_idx) if 0 <= correct_idx < len(options) else "?"
            print(red(f"  Wrong. Answer: {correct_letter}"))

            # Show explanation if available
            explanation = q.get("explanation", q.get("rationale", ""))
            if explanation:
                print(dim(f"  {explanation}"))

        print()

    # Score
    score = int(correct / total * 100) if total > 0 else 0
    print(dim("  ─" * 25))
    score_color = green if score >= 80 else amber if score >= 60 else red
    print(f"  Result: {score_color(f'{correct}/{total} ({score}%)')}")
    print()

    # Update progress (backward compatible)
    attempts_key = "drill_attempts" if "drill_attempts" in unit else "quiz_attempts"
    score_key = "drill_score" if "drill_score" in unit else "quiz_score"
    unit[attempts_key] = unit.get(attempts_key, 0) + 1
    # Keep the best score
    if unit.get(score_key) is None or score > unit.get(score_key, 0):
        unit[score_key] = score
    touch_activity(data)
    save_progress(data)

    if score >= 80:
        print(green("  Great job! Moving on."))
    elif score >= 60:
        print(amber("  Decent, but review the material and try again."))
    else:
        print(red("  Review the unit content before retrying."))
    print()


def cmd_open_dashboard() -> None:
    """Open dashboard.html via a local HTTP server (needed for fetch to work)."""
    import http.server
    import threading

    dashboard = ROOT / "dashboard.html"
    if not dashboard.exists():
        print(red(f"dashboard.html not found at {dashboard}"))
        return

    port = 8847
    handler = http.server.SimpleHTTPRequestHandler

    # Suppress request logs
    class QuietHandler(handler):
        def log_message(self, format, *args):
            pass

    try:
        httpd = http.server.HTTPServer(("127.0.0.1", port), QuietHandler)
    except OSError:
        port = 8848
        httpd = http.server.HTTPServer(("127.0.0.1", port), QuietHandler)

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    url = f"http://127.0.0.1:{port}/dashboard.html"
    print(f"  Serving at {cyan(url)}")
    print(dim("  (Press Ctrl+C to stop)"))
    webbrowser.open(url)

    try:
        thread.join()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        httpd.shutdown()


def cmd_cheatsheet(data: dict, module_id: str) -> None:
    """Open a module's cheat sheet in the browser."""
    validate_module(data, module_id)
    md = module_dir(module_id)

    # Try various cheatsheet file patterns
    candidates = (
        list(md.glob("cheatsheet.*"))
        + list(md.glob("cheat-sheet.*"))
        + list(md.glob("*cheatsheet*"))
    )

    if not candidates:
        print(amber(f"No cheatsheet found in {md}"))
        print(dim("Expected: cheatsheet.html or cheatsheet.md"))
        return

    target = candidates[0]
    url = target.as_uri() if hasattr(target, "as_uri") else "file://" + str(target)
    print(f"Opening {cyan(str(target.relative_to(ROOT)))}...")
    webbrowser.open(url)

    # Mark cheatsheet as reviewed
    data["modules"][module_id]["cheatsheet_reviewed"] = True
    touch_activity(data)
    save_progress(data)
    print(green("Marked cheatsheet as reviewed."))


# ── CLI argument parsing ────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="Claude Architect Foundations — CLI Navigator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python run.py                                  Show status dashboard
  python run.py module-1                         Module 1 progress
  python run.py module-1 unit-1.1                Unit 1.1 details
  python run.py open module-1 unit-1.1 overview  Open overview in browser
  python run.py check module-1 unit-1.1          Run challenge checker
  python run.py quiz module-1 unit-1.1           Take quiz in terminal
  python run.py dashboard                        Open HTML dashboard
  python run.py cheatsheet module-1              Open module cheat sheet
""",
    )

    subparsers = parser.add_subparsers(dest="command")

    # open
    p_open = subparsers.add_parser("open", help="Open a stage in the browser")
    p_open.add_argument("module", help="Module ID (e.g. module-1)")
    p_open.add_argument("unit", help="Unit ID (e.g. unit-1.1)")
    p_open.add_argument(
        "stage",
        choices=["overview", "walkthrough", "challenge", "quiz"],
        help="Stage to open",
    )

    # check
    p_check = subparsers.add_parser("check", help="Run challenge checker (pytest)")
    p_check.add_argument("module", help="Module ID")
    p_check.add_argument("unit", help="Unit ID")

    # quiz
    p_quiz = subparsers.add_parser("quiz", help="Take quiz in terminal")
    p_quiz.add_argument("module", help="Module ID")
    p_quiz.add_argument("unit", help="Unit ID")

    # dashboard
    subparsers.add_parser("dashboard", help="Open HTML dashboard in browser")

    # cheatsheet
    p_cs = subparsers.add_parser("cheatsheet", help="Open module cheat sheet")
    p_cs.add_argument("module", help="Module ID")

    # Positional: module and optionally unit (when no subcommand)
    parser.add_argument(
        "args",
        nargs="*",
        default=[],
        help=argparse.SUPPRESS,
    )

    return parser


def main() -> None:
    # We need custom parsing because argparse subcommands and positional
    # args for the default (no-command) case don't mix cleanly.

    args = sys.argv[1:]

    # No arguments: show terminal dashboard
    if not args:
        data = load_progress()
        cmd_dashboard_terminal(data)
        return

    # Route subcommands
    first = args[0]

    if first == "dashboard":
        cmd_open_dashboard()
        return

    if first == "open":
        if len(args) < 4:
            print(red("Usage: python run.py open <module> <unit> <stage>"))
            sys.exit(1)
        data = load_progress()
        cmd_open(data, args[1], args[2], args[3])
        return

    if first == "check":
        if len(args) < 3:
            print(red("Usage: python run.py check <module> <unit>"))
            sys.exit(1)
        data = load_progress()
        cmd_check(data, args[1], args[2])
        return

    if first == "quiz":
        if len(args) < 3:
            print(red("Usage: python run.py quiz <module> <unit>"))
            sys.exit(1)
        data = load_progress()
        cmd_quiz(data, args[1], args[2])
        return

    if first == "cheatsheet":
        if len(args) < 2:
            print(red("Usage: python run.py cheatsheet <module>"))
            sys.exit(1)
        data = load_progress()
        cmd_cheatsheet(data, args[1])
        return

    # Check if it looks like a module ID
    if first.startswith("module-"):
        data = load_progress()
        if len(args) >= 2 and args[1].startswith("unit-"):
            cmd_unit(data, args[0], args[1])
        else:
            cmd_module(data, args[0])
        return

    # Unknown command
    print(red(f"Unknown command: {first}"))
    print()
    print("Usage:")
    print("  python run.py                                  Show status dashboard")
    print("  python run.py module-1                         Module 1 progress")
    print("  python run.py module-1 unit-1.1                Unit 1.1 details")
    print("  python run.py open module-1 unit-1.1 overview  Open overview in browser")
    print("  python run.py check module-1 unit-1.1          Run challenge checker")
    print("  python run.py quiz module-1 unit-1.1           Take quiz in terminal")
    print("  python run.py dashboard                        Open HTML dashboard")
    print("  python run.py cheatsheet module-1              Open module cheat sheet")
    sys.exit(1)


if __name__ == "__main__":
    main()
