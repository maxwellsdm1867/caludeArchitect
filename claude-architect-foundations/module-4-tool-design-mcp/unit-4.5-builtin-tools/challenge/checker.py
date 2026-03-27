"""
Checker for Unit 4.5 — Built-in Tool Selection Challenge

Validates tool selection, explanations, and usage suggestions
without calling the Anthropic API.
"""

import pytest

from challenge import (
    BuiltinToolChallenge,
    TASKS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create a BuiltinToolChallenge instance."""
    return BuiltinToolChallenge()


# ---------------------------------------------------------------------------
# Test 1: Tool Selection Accuracy
# ---------------------------------------------------------------------------

class TestToolSelection:
    """Student's select_tool must return the correct tool for each task."""

    def test_returns_valid_tool(self, challenge):
        valid_tools = {"Grep", "Glob", "Read", "Edit", "Write", "Bash"}
        for t in TASKS:
            selected = challenge.select_tool(t["task"])
            assert selected in valid_tools, (
                f"select_tool returned '{selected}' for task '{t['task'][:40]}...' "
                f"-- must be one of {valid_tools}"
            )

    def test_glob_tasks(self, challenge):
        glob_tasks = [t for t in TASKS if t["correct_tool"] == "Glob"]
        for t in glob_tasks:
            selected = challenge.select_tool(t["task"])
            assert selected == "Glob", (
                f"Task '{t['task'][:50]}...' should use Glob (path search), "
                f"got {selected}"
            )

    def test_grep_tasks(self, challenge):
        grep_tasks = [t for t in TASKS if t["correct_tool"] == "Grep"]
        for t in grep_tasks:
            selected = challenge.select_tool(t["task"])
            assert selected == "Grep", (
                f"Task '{t['task'][:50]}...' should use Grep (content search), "
                f"got {selected}"
            )

    def test_read_tasks(self, challenge):
        read_tasks = [t for t in TASKS if t["correct_tool"] == "Read"]
        for t in read_tasks:
            selected = challenge.select_tool(t["task"])
            assert selected == "Read", (
                f"Task '{t['task'][:50]}...' should use Read, got {selected}"
            )

    def test_edit_tasks(self, challenge):
        edit_tasks = [t for t in TASKS if t["correct_tool"] == "Edit"]
        for t in edit_tasks:
            selected = challenge.select_tool(t["task"])
            assert selected == "Edit", (
                f"Task '{t['task'][:50]}...' should use Edit, got {selected}"
            )

    def test_write_tasks(self, challenge):
        write_tasks = [t for t in TASKS if t["correct_tool"] == "Write"]
        for t in write_tasks:
            selected = challenge.select_tool(t["task"])
            assert selected == "Write", (
                f"Task '{t['task'][:50]}...' should use Write, got {selected}"
            )

    def test_bash_tasks(self, challenge):
        bash_tasks = [t for t in TASKS if t["correct_tool"] == "Bash"]
        for t in bash_tasks:
            selected = challenge.select_tool(t["task"])
            assert selected == "Bash", (
                f"Task '{t['task'][:50]}...' should use Bash, got {selected}"
            )

    def test_perfect_accuracy(self, challenge):
        correct = 0
        for t in TASKS:
            if challenge.select_tool(t["task"]) == t["correct_tool"]:
                correct += 1
        assert correct == len(TASKS), (
            f"Must achieve 100% accuracy. Got {correct}/{len(TASKS)}."
        )


# ---------------------------------------------------------------------------
# Test 2: Explanations
# ---------------------------------------------------------------------------

class TestExplanations:
    """Student's explain_selection must return meaningful explanations."""

    def test_returns_string(self, challenge):
        explanation = challenge.explain_selection(
            "Find all Python files", "Glob"
        )
        assert isinstance(explanation, str), "explain_selection must return a string"

    def test_explanation_not_empty(self, challenge):
        for t in TASKS[:5]:
            explanation = challenge.explain_selection(
                t["task"], t["correct_tool"]
            )
            assert len(explanation) > 10, (
                f"Explanation too short for task: {t['task'][:40]}..."
            )

    def test_grep_explanation_mentions_content(self, challenge):
        explanation = challenge.explain_selection(
            "Find where UserService is defined", "Grep"
        ).lower()
        has_content_reference = any(
            kw in explanation for kw in ["content", "text", "inside", "within"]
        )
        assert has_content_reference, (
            "Grep explanation should mention searching file content"
        )

    def test_glob_explanation_mentions_paths(self, challenge):
        explanation = challenge.explain_selection(
            "Find all TypeScript files", "Glob"
        ).lower()
        has_path_reference = any(
            kw in explanation for kw in ["path", "name", "pattern", "file"]
        )
        assert has_path_reference, (
            "Glob explanation should mention file paths or names"
        )


# ---------------------------------------------------------------------------
# Test 3: Usage Suggestions
# ---------------------------------------------------------------------------

class TestUsageSuggestions:
    """Student's suggest_usage must return concrete examples."""

    def test_returns_string(self, challenge):
        usage = challenge.suggest_usage("Find all .py files", "Glob")
        assert isinstance(usage, str), "suggest_usage must return a string"

    def test_usage_not_empty(self, challenge):
        for t in TASKS[:5]:
            usage = challenge.suggest_usage(t["task"], t["correct_tool"])
            assert len(usage) > 5, (
                f"Usage too short for task: {t['task'][:40]}..."
            )

    def test_glob_usage_has_pattern(self, challenge):
        usage = challenge.suggest_usage(
            "Find all TypeScript files in src/", "Glob"
        )
        assert "**" in usage or "*" in usage or "pattern" in usage.lower(), (
            "Glob usage should include a glob pattern"
        )

    def test_grep_usage_has_pattern(self, challenge):
        usage = challenge.suggest_usage(
            "Find all TODO comments", "Grep"
        )
        assert "TODO" in usage or "pattern" in usage.lower(), (
            "Grep usage should reference the search pattern"
        )
