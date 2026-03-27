"""
Checker for Unit 3.4 — Plan vs Direct Mode Challenge

Validates the student's ComplexityChallenge implementation without
calling the Anthropic API. Tests complexity assessment, mode
recommendation, and classification accuracy.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    ComplexityChallenge,
    TASKS,
)


@pytest.fixture
def challenge():
    return ComplexityChallenge()


class TestComplexityAssessment:
    """Student's assess_complexity must return valid signals."""

    def test_returns_dict(self, challenge):
        result = challenge.assess_complexity("Fix a typo in README.md")
        assert isinstance(result, dict), "assess_complexity must return a dict"

    def test_has_required_signals(self, challenge):
        result = challenge.assess_complexity("Fix a typo in README.md")
        required = ["scope", "clarity", "familiarity", "risk", "has_approved_plan"]
        for field in required:
            assert field in result, f"Signals missing '{field}'"

    def test_simple_fix_signals(self, challenge):
        result = challenge.assess_complexity(
            "Fix the off-by-one error in pagination.ts line 23"
        )
        assert result["scope"] == "single", "Single-file fix should be scope=single"
        assert result["clarity"] == "high", "Clear bug fix should be clarity=high"

    def test_migration_signals(self, challenge):
        result = challenge.assess_complexity(
            "Migrate from Express.js to Fastify across 45 route handlers"
        )
        assert result["scope"] == "multi", "Migration should be scope=multi"
        assert result["risk"] == "high", "Framework migration should be risk=high"

    def test_approved_plan_signal(self, challenge):
        result = challenge.assess_complexity(
            "Implement the rate limiting approach approved in yesterday's review"
        )
        assert result["has_approved_plan"] is True, (
            "Task referencing approved plan should have has_approved_plan=True"
        )

    def test_investigation_signals(self, challenge):
        result = challenge.assess_complexity(
            "Investigate why the test suite takes 12 minutes"
        )
        assert result["scope"] in ("unknown", "multi"), (
            "Investigation should be scope=unknown or multi"
        )
        assert result["clarity"] == "low", "Investigation should be clarity=low"


class TestModeRecommendation:
    """Student's recommend_mode must follow the decision rules."""

    def test_approved_plan_always_direct(self, challenge):
        signals = {
            "scope": "multi", "clarity": "low", "familiarity": "unknown",
            "risk": "high", "has_approved_plan": True
        }
        result = challenge.recommend_mode(signals)
        assert result == "direct", (
            "Approved plan should always recommend direct, regardless of other signals"
        )

    def test_multi_scope_low_clarity_is_plan(self, challenge):
        signals = {
            "scope": "multi", "clarity": "low", "familiarity": "unknown",
            "risk": "high", "has_approved_plan": False
        }
        result = challenge.recommend_mode(signals)
        assert result == "plan", "Multi-scope + low clarity should be plan"

    def test_single_scope_high_clarity_is_direct(self, challenge):
        signals = {
            "scope": "single", "clarity": "high", "familiarity": "known",
            "risk": "low", "has_approved_plan": False
        }
        result = challenge.recommend_mode(signals)
        assert result == "direct", "Single-scope + high clarity should be direct"

    def test_high_risk_is_plan(self, challenge):
        signals = {
            "scope": "multi", "clarity": "medium", "familiarity": "unknown",
            "risk": "high", "has_approved_plan": False
        }
        result = challenge.recommend_mode(signals)
        assert result == "plan", "High risk should be plan"

    def test_unknown_scope_is_plan(self, challenge):
        signals = {
            "scope": "unknown", "clarity": "low", "familiarity": "unknown",
            "risk": "medium", "has_approved_plan": False
        }
        result = challenge.recommend_mode(signals)
        assert result == "plan", "Unknown scope (investigation) should be plan"


class TestClassifyTask:
    """Student's classify_task must return complete results."""

    def test_returns_correct_structure(self, challenge):
        result = challenge.classify_task("Fix a typo in README.md")
        assert "mode" in result, "Result must have 'mode'"
        assert "signals" in result, "Result must have 'signals'"
        assert result["mode"] in ("plan", "direct"), (
            f"Mode must be 'plan' or 'direct', got '{result['mode']}'"
        )


class TestAccuracy:
    """Classification must be correct across all task scenarios."""

    def test_all_tasks_classified_correctly(self, challenge):
        correct = 0
        misclassified = []
        for task in TASKS:
            result = challenge.classify_task(task["description"])
            if result["mode"] == task["correct_mode"]:
                correct += 1
            else:
                misclassified.append(
                    f"'{task['description'][:50]}...' -> {result['mode']} "
                    f"(expected {task['correct_mode']})"
                )

        accuracy = correct / len(TASKS)
        assert accuracy == 1.0, (
            f"Accuracy: {accuracy:.0%} ({correct}/{len(TASKS)}). "
            f"Misclassified:\n" + "\n".join(misclassified)
        )

    def test_direct_tasks_are_direct(self, challenge):
        direct_tasks = [t for t in TASKS if t["correct_mode"] == "direct"]
        for task in direct_tasks:
            result = challenge.classify_task(task["description"])
            assert result["mode"] == "direct", (
                f"Should be direct: {task['description'][:50]}..."
            )

    def test_plan_tasks_are_plan(self, challenge):
        plan_tasks = [t for t in TASKS if t["correct_mode"] == "plan"]
        for task in plan_tasks:
            result = challenge.classify_task(task["description"])
            assert result["mode"] == "plan", (
                f"Should be plan: {task['description'][:50]}..."
            )
