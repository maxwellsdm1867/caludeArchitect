"""
Checker for Unit 4.1 — Tool Description Challenge

Validates the student's ToolDescriptionChallenge implementation without
calling the Anthropic API. Tests description construction, evaluation logic,
and fix suggestions. The selection test uses mock API responses.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    ToolDescriptionChallenge,
    SCENARIO_1_TOOLS_SKELETON,
    SCENARIO_1_QUERIES,
    SCENARIO_2_TOOLS_SKELETON,
    SCENARIO_2_QUERIES,
    ALL_SCENARIOS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create a ToolDescriptionChallenge instance (no API calls)."""
    return ToolDescriptionChallenge()


# ---------------------------------------------------------------------------
# Test 1: Tool Definition Construction
# ---------------------------------------------------------------------------

class TestToolConstruction:
    """Student's build_tools must produce well-structured tool definitions."""

    def test_returns_list(self, challenge):
        tools = challenge.build_tools(SCENARIO_1_TOOLS_SKELETON)
        assert isinstance(tools, list), "build_tools must return a list"

    def test_correct_count_scenario1(self, challenge):
        tools = challenge.build_tools(SCENARIO_1_TOOLS_SKELETON)
        assert len(tools) == len(SCENARIO_1_TOOLS_SKELETON), (
            f"Expected {len(SCENARIO_1_TOOLS_SKELETON)} tools, got {len(tools)}"
        )

    def test_correct_count_scenario2(self, challenge):
        tools = challenge.build_tools(SCENARIO_2_TOOLS_SKELETON)
        assert len(tools) == len(SCENARIO_2_TOOLS_SKELETON), (
            f"Expected {len(SCENARIO_2_TOOLS_SKELETON)} tools, got {len(tools)}"
        )

    def test_tools_have_required_fields(self, challenge):
        tools = challenge.build_tools(SCENARIO_1_TOOLS_SKELETON)
        for tool in tools:
            assert "name" in tool, f"Tool missing 'name': {tool}"
            assert "description" in tool, f"Tool missing 'description': {tool}"
            assert "input_schema" in tool, f"Tool missing 'input_schema': {tool}"
            assert isinstance(tool["name"], str), "name must be a string"
            assert isinstance(tool["description"], str), "description must be a string"
            assert isinstance(tool["input_schema"], dict), "input_schema must be a dict"

    def test_tool_names_match_skeletons(self, challenge):
        tools = challenge.build_tools(SCENARIO_1_TOOLS_SKELETON)
        tool_names = {t["name"] for t in tools}
        expected_names = {s["name"] for s in SCENARIO_1_TOOLS_SKELETON}
        assert tool_names == expected_names, (
            f"Tool names {tool_names} don't match expected {expected_names}"
        )

    def test_descriptions_have_positive_triggers(self, challenge):
        tools = challenge.build_tools(SCENARIO_1_TOOLS_SKELETON)
        for tool in tools:
            desc = tool["description"].lower()
            has_trigger = any(
                kw in desc for kw in [
                    "use when", "use for", "use this", "use to",
                    "call when", "call this",
                ]
            )
            assert has_trigger, (
                f"Tool '{tool['name']}' description lacks positive triggers "
                f"(e.g., 'Use when...')"
            )

    def test_descriptions_have_negative_boundaries(self, challenge):
        tools = challenge.build_tools(SCENARIO_1_TOOLS_SKELETON)
        for tool in tools:
            desc = tool["description"].lower()
            has_boundary = any(
                kw in desc for kw in [
                    "do not use", "don't use", "do not call",
                    "not for", "don't call",
                ]
            )
            assert has_boundary, (
                f"Tool '{tool['name']}' description lacks negative boundaries "
                f"(e.g., 'Do NOT use for...')"
            )

    def test_descriptions_not_minimal(self, challenge):
        tools = challenge.build_tools(SCENARIO_1_TOOLS_SKELETON)
        for tool in tools:
            assert len(tool["description"]) >= 50, (
                f"Tool '{tool['name']}' description too short "
                f"({len(tool['description'])} chars). Needs triggers and boundaries."
            )

    def test_input_schema_is_valid(self, challenge):
        tools = challenge.build_tools(SCENARIO_1_TOOLS_SKELETON)
        for tool in tools:
            schema = tool["input_schema"]
            assert "type" in schema, f"input_schema missing 'type' for {tool['name']}"
            assert schema["type"] == "object", (
                f"input_schema type must be 'object' for {tool['name']}"
            )
            assert "properties" in schema, (
                f"input_schema missing 'properties' for {tool['name']}"
            )


# ---------------------------------------------------------------------------
# Test 2: Evaluation Logic
# ---------------------------------------------------------------------------

class TestEvaluation:
    """Student's evaluate_selection must correctly identify correct/wrong selections."""

    def test_correct_selection(self, challenge):
        result = challenge.evaluate_selection("search_docs", "search_docs")
        assert isinstance(result, dict), "evaluate_selection must return a dict"
        assert result["correct"] is True, "Same tool should be correct"
        assert result["selected"] == "search_docs"
        assert result["expected"] == "search_docs"

    def test_wrong_selection(self, challenge):
        result = challenge.evaluate_selection("search_web", "search_docs")
        assert result["correct"] is False, "Different tools should be incorrect"
        assert result["selected"] == "search_web"
        assert result["expected"] == "search_docs"

    def test_result_has_required_keys(self, challenge):
        result = challenge.evaluate_selection("search_docs", "search_docs")
        assert "correct" in result, "Result missing 'correct' key"
        assert "selected" in result, "Result missing 'selected' key"
        assert "expected" in result, "Result missing 'expected' key"


# ---------------------------------------------------------------------------
# Test 3: Fix Suggestions
# ---------------------------------------------------------------------------

class TestFixSuggestions:
    """Student's suggest_fix must produce actionable improvement suggestions."""

    def test_returns_string(self, challenge):
        fix = challenge.suggest_fix(
            "Find our remote work policy",
            "search_web",
            "search_docs"
        )
        assert isinstance(fix, str), "suggest_fix must return a string"

    def test_mentions_wrong_tool(self, challenge):
        fix = challenge.suggest_fix(
            "Find our remote work policy",
            "search_web",
            "search_docs"
        )
        assert "search_web" in fix.lower(), (
            "Fix suggestion should mention the incorrectly selected tool"
        )

    def test_mentions_correct_tool(self, challenge):
        fix = challenge.suggest_fix(
            "Find our remote work policy",
            "search_web",
            "search_docs"
        )
        assert "search_docs" in fix.lower(), (
            "Fix suggestion should mention the correct tool as alternative"
        )

    def test_suggests_boundary(self, challenge):
        fix = challenge.suggest_fix(
            "Find our remote work policy",
            "search_web",
            "search_docs"
        ).lower()
        has_boundary_language = any(
            kw in fix for kw in [
                "do not", "don't", "boundary", "not use",
                "instead", "redirect", "point to",
            ]
        )
        assert has_boundary_language, (
            "Fix should suggest adding a negative boundary to the description"
        )


# ---------------------------------------------------------------------------
# Test 4: End-to-End with Mock API
# ---------------------------------------------------------------------------

class TestEndToEnd:
    """End-to-end test using mocked Claude responses."""

    def _mock_tool_call(self, challenge, tool_name):
        """Helper: mock the API to return a specific tool selection."""
        mock_block = MagicMock()
        mock_block.type = "tool_use"
        mock_block.name = tool_name

        mock_msg = MagicMock()
        mock_msg.content = [mock_block]

        with patch.object(
            challenge.client.messages, "create", return_value=mock_msg
        ):
            tools = challenge.build_tools(SCENARIO_1_TOOLS_SKELETON)
            return challenge.run_selection(tools, "test query")

    def test_run_selection_returns_tool_name(self, challenge):
        result = self._mock_tool_call(challenge, "search_docs")
        assert result == "search_docs", (
            f"run_selection should return tool name, got {result}"
        )

    def test_full_pipeline_correct(self, challenge):
        """Simulate a correct selection and verify the pipeline."""
        selected = self._mock_tool_call(challenge, "search_docs")
        evaluation = challenge.evaluate_selection(selected, "search_docs")
        assert evaluation["correct"] is True

    def test_full_pipeline_wrong(self, challenge):
        """Simulate a wrong selection and verify the fix suggestion."""
        selected = self._mock_tool_call(challenge, "search_web")
        evaluation = challenge.evaluate_selection(selected, "search_docs")
        assert evaluation["correct"] is False

        fix = challenge.suggest_fix(
            "Find our remote work policy",
            selected,
            "search_docs"
        )
        assert isinstance(fix, str) and len(fix) > 10, (
            "Fix suggestion should be a meaningful string"
        )
