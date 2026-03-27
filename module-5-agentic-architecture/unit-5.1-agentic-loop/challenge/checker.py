"""
Checker for Unit 5.1 — Agentic Loop Challenge

Validates the student's AgenticLoopChallenge implementation without
calling the Anthropic API. Tests loop control, tool processing, and
termination logic using mock API responses.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import AgenticLoopChallenge, TOOLS, execute_tool, STORED_VALUES


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create an AgenticLoopChallenge instance (no API calls)."""
    return AgenticLoopChallenge()


# ---------------------------------------------------------------------------
# Mock response builders
# ---------------------------------------------------------------------------

def make_tool_use_response(tool_name, tool_input, tool_id="tool_001", text=None):
    """Build a mock response with stop_reason='tool_use'."""
    response = MagicMock()
    response.stop_reason = "tool_use"
    blocks = []
    if text:
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = text
        blocks.append(text_block)
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = tool_name
    tool_block.input = tool_input
    tool_block.id = tool_id
    blocks.append(tool_block)
    response.content = blocks
    return response


def make_end_turn_response(text="Done."):
    """Build a mock response with stop_reason='end_turn'."""
    response = MagicMock()
    response.stop_reason = "end_turn"
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = text
    response.content = [text_block]
    return response


# ---------------------------------------------------------------------------
# Test 1: should_continue logic
# ---------------------------------------------------------------------------

class TestShouldContinue:
    """Student's should_continue must use stop_reason correctly."""

    def test_continues_on_tool_use(self, challenge):
        response = make_tool_use_response("calculator", {"expression": "1+1"})
        assert challenge.should_continue(response) is True, (
            "should_continue must return True when stop_reason is 'tool_use'"
        )

    def test_stops_on_end_turn(self, challenge):
        response = make_end_turn_response("All done!")
        assert challenge.should_continue(response) is False, (
            "should_continue must return False when stop_reason is 'end_turn'"
        )

    def test_stops_on_max_tokens(self, challenge):
        response = MagicMock()
        response.stop_reason = "max_tokens"
        assert challenge.should_continue(response) is False, (
            "should_continue should return False on 'max_tokens' (not tool_use)"
        )


# ---------------------------------------------------------------------------
# Test 2: process_tool_calls
# ---------------------------------------------------------------------------

class TestProcessToolCalls:
    """Student's process_tool_calls must extract and execute tools."""

    def test_returns_list(self, challenge):
        response = make_tool_use_response("calculator", {"expression": "2+3"})
        results = challenge.process_tool_calls(response)
        assert isinstance(results, list), "process_tool_calls must return a list"

    def test_correct_tool_result_structure(self, challenge):
        response = make_tool_use_response(
            "calculator", {"expression": "2+3"}, tool_id="test_id_1"
        )
        results = challenge.process_tool_calls(response)
        assert len(results) == 1, f"Expected 1 tool result, got {len(results)}"
        result = results[0]
        assert result["type"] == "tool_result", "Each result must have type 'tool_result'"
        assert result["tool_use_id"] == "test_id_1", "tool_use_id must match"
        assert "content" in result, "Each result must have 'content'"

    def test_executes_calculator(self, challenge):
        response = make_tool_use_response(
            "calculator", {"expression": "10 * 5"}, tool_id="calc_1"
        )
        results = challenge.process_tool_calls(response)
        content = json.loads(results[0]["content"])
        assert content["result"] == 50, (
            f"Calculator should return 50, got {content}"
        )

    def test_handles_mixed_content(self, challenge):
        """Response with both text and tool_use should process the tool."""
        response = make_tool_use_response(
            "calculator", {"expression": "3+4"}, tool_id="mixed_1",
            text="Let me calculate that."
        )
        results = challenge.process_tool_calls(response)
        assert len(results) == 1, (
            "Should process tool_use even when text is present"
        )

    def test_no_tool_calls_returns_empty(self, challenge):
        response = make_end_turn_response("No tools needed.")
        results = challenge.process_tool_calls(response)
        assert results == [], (
            "process_tool_calls should return empty list when no tool_use blocks"
        )


# ---------------------------------------------------------------------------
# Test 3: run_agent (mocked API)
# ---------------------------------------------------------------------------

class TestRunAgent:
    """Student's run_agent must implement a proper agentic loop."""

    def test_single_iteration_no_tools(self, challenge):
        """Task with no tool use should complete in 1 iteration."""
        with patch.object(challenge.client.messages, "create") as mock_create:
            mock_create.return_value = make_end_turn_response("Paris is the capital.")
            result = challenge.run_agent("What is the capital of France?")

        assert result["iterations"] == 1, (
            f"No-tool task should take 1 iteration, got {result['iterations']}"
        )
        assert result["terminated_by"] == "stop_reason", (
            "Should terminate by stop_reason, not safety_cap"
        )
        assert "Paris" in result["final_text"], (
            "Final text should contain the answer"
        )
        assert result["tool_calls"] == [], (
            "No tool calls should be recorded"
        )

    def test_multi_step_tool_use(self, challenge):
        """Multi-step task should loop until end_turn."""
        responses = [
            make_tool_use_response("calculator", {"expression": "15 * 8"}, "t1"),
            make_tool_use_response("store_value", {"name": "total", "value": 120}, "t2"),
            make_end_turn_response("The total is 120."),
        ]

        with patch.object(challenge.client.messages, "create") as mock_create:
            mock_create.side_effect = responses
            result = challenge.run_agent("Calculate 15 * 8 and store it.")

        assert result["iterations"] == 3, (
            f"Expected 3 iterations (2 tool + 1 end), got {result['iterations']}"
        )
        assert result["terminated_by"] == "stop_reason"
        assert "calculator" in result["tool_calls"]
        assert "store_value" in result["tool_calls"]

    def test_safety_cap_triggers(self, challenge):
        """Safety cap should stop infinite loops."""
        infinite_response = make_tool_use_response(
            "calculator", {"expression": "1+1"}, "inf_1"
        )

        with patch.object(challenge.client.messages, "create") as mock_create:
            mock_create.return_value = infinite_response
            result = challenge.run_agent("Loop forever", safety_cap=3)

        assert result["iterations"] <= 3, (
            f"Safety cap of 3 should limit iterations, got {result['iterations']}"
        )
        assert result["terminated_by"] == "safety_cap", (
            "Should report termination by safety_cap"
        )

    def test_returns_required_fields(self, challenge):
        """Result must contain all required fields."""
        with patch.object(challenge.client.messages, "create") as mock_create:
            mock_create.return_value = make_end_turn_response("Done.")
            result = challenge.run_agent("Test")

        required = ["final_text", "iterations", "tool_calls", "terminated_by"]
        for field in required:
            assert field in result, f"Result must contain '{field}'"

    def test_uses_while_not_for(self, challenge):
        """Loop should be while-based, not for-range based."""
        import inspect
        source = inspect.getsource(challenge.run_agent)
        assert "while" in source, (
            "run_agent should use a while loop, not a for loop"
        )
