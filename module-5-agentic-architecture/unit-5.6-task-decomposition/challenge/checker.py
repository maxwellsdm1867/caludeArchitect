"""
Checker for Unit 5.6 — Task Decomposition Challenge

Validates strategy selection, per-file extraction, and cross-file
bug detection. No API calls needed.
"""

import json
import pytest

from challenge import (
    DecompositionChallenge, CODEBASE, KNOWN_BUGS, TASK_DESCRIPTIONS,
)


@pytest.fixture
def challenge():
    return DecompositionChallenge()


# ---------------------------------------------------------------------------
# Test 1: Strategy Selection
# ---------------------------------------------------------------------------

class TestStrategySelection:
    """choose_strategy must select the correct decomposition approach."""

    def test_pipeline_tasks_use_chaining(self, challenge):
        for td in TASK_DESCRIPTIONS:
            if td["expected"] == "prompt_chaining":
                result = challenge.choose_strategy(td["task"])
                assert result == "prompt_chaining", (
                    f"Pipeline task should use prompt_chaining, got {result}: {td['task'][:50]}"
                )

    def test_variable_tasks_use_dynamic(self, challenge):
        for td in TASK_DESCRIPTIONS:
            if td["expected"] == "dynamic":
                result = challenge.choose_strategy(td["task"])
                assert result == "dynamic", (
                    f"Variable task should use dynamic, got {result}: {td['task'][:50]}"
                )

    def test_multifile_tasks_use_per_cross(self, challenge):
        for td in TASK_DESCRIPTIONS:
            if td["expected"] == "per_file_cross_file":
                result = challenge.choose_strategy(td["task"])
                assert result == "per_file_cross_file", (
                    f"Multi-file task should use per_file_cross_file, got {result}: {td['task'][:50]}"
                )

    def test_returns_valid_strategy(self, challenge):
        valid = {"prompt_chaining", "dynamic", "per_file_cross_file"}
        for td in TASK_DESCRIPTIONS:
            result = challenge.choose_strategy(td["task"])
            assert result in valid, (
                f"Strategy must be one of {valid}, got '{result}'"
            )


# ---------------------------------------------------------------------------
# Test 2: Per-File Analysis
# ---------------------------------------------------------------------------

class TestPerFileAnalysis:
    """analyze_per_file must extract structured information from code."""

    def test_returns_dict(self, challenge):
        result = challenge.analyze_per_file("test.py", "def foo(): pass")
        assert isinstance(result, dict)

    def test_has_required_fields(self, challenge):
        result = challenge.analyze_per_file("api/routes.py", CODEBASE["api/routes.py"])
        for field in ["functions", "data_contracts", "local_issues"]:
            assert field in result, f"Per-file summary must contain '{field}'"

    def test_finds_functions_in_routes(self, challenge):
        result = challenge.analyze_per_file("api/routes.py", CODEBASE["api/routes.py"])
        func_names = [f if isinstance(f, str) else f.get("name", "") for f in result["functions"]]
        func_str = " ".join(str(f) for f in func_names).lower()
        assert "create_user" in func_str or "create" in func_str, (
            "Should find create_user function in routes.py"
        )

    def test_finds_data_contracts_in_routes(self, challenge):
        result = challenge.analyze_per_file("api/routes.py", CODEBASE["api/routes.py"])
        contracts_str = json.dumps(result["data_contracts"]).lower()
        assert "user_id" in contracts_str or "userid" in contracts_str, (
            "Should identify user_id/userId as a data contract in routes.py"
        )

    def test_finds_functions_in_service(self, challenge):
        result = challenge.analyze_per_file(
            "services/user_service.py", CODEBASE["services/user_service.py"]
        )
        func_names = " ".join(str(f) for f in result["functions"]).lower()
        assert "get_by_id" in func_names or "get" in func_names, (
            "Should find get_by_id in user_service.py"
        )


# ---------------------------------------------------------------------------
# Test 3: Cross-File Analysis
# ---------------------------------------------------------------------------

class TestCrossFileAnalysis:
    """analyze_cross_file must detect integration bugs across files."""

    def _get_summaries(self, challenge):
        return {
            filename: challenge.analyze_per_file(filename, code)
            for filename, code in CODEBASE.items()
        }

    def test_returns_list(self, challenge):
        summaries = self._get_summaries(challenge)
        result = challenge.analyze_cross_file(summaries)
        assert isinstance(result, list), "analyze_cross_file must return a list"

    def test_finds_at_least_one_bug(self, challenge):
        summaries = self._get_summaries(challenge)
        result = challenge.analyze_cross_file(summaries)
        assert len(result) >= 1, (
            "Should find at least 1 cross-file bug"
        )

    def test_bugs_have_required_fields(self, challenge):
        summaries = self._get_summaries(challenge)
        result = challenge.analyze_cross_file(summaries)
        for bug in result:
            assert "bug_type" in bug, "Each bug must have 'bug_type'"
            assert "files" in bug, "Each bug must have 'files'"
            assert "description" in bug, "Each bug must have 'description'"

    def test_detects_type_mismatch(self, challenge):
        summaries = self._get_summaries(challenge)
        result = challenge.analyze_cross_file(summaries)
        bug_descriptions = " ".join(b.get("description", "") + b.get("bug_type", "") for b in result).lower()
        has_type_bug = "type" in bug_descriptions and ("int" in bug_descriptions or "str" in bug_descriptions or "mismatch" in bug_descriptions)
        assert has_type_bug, (
            "Should detect the int/str type mismatch between routes.py and user_service.py"
        )

    def test_detects_key_inconsistency(self, challenge):
        summaries = self._get_summaries(challenge)
        result = challenge.analyze_cross_file(summaries)
        bug_descriptions = " ".join(b.get("description", "") + b.get("bug_type", "") for b in result).lower()
        has_key_bug = ("user_id" in bug_descriptions and "userid" in bug_descriptions) or "key" in bug_descriptions or "inconsisten" in bug_descriptions
        assert has_key_bug, (
            "Should detect the user_id vs userId key inconsistency in routes.py"
        )
