"""
Checker for Unit 5.2 — Coordinator-Subagent Challenge

Validates context isolation, tool scoping, and coordinator synthesis
without calling the Anthropic API.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    CoordinatorChallenge,
    CUSTOMER_TOOLS, ORDER_TOOLS, ACTION_TOOLS,
    CUSTOMERS, ORDERS, execute_tool,
)


@pytest.fixture
def challenge():
    return CoordinatorChallenge()


# ---------------------------------------------------------------------------
# Test 1: Subagent Prompt Construction
# ---------------------------------------------------------------------------

class TestSubagentPrompt:
    """Subagent prompts must be focused and include only relevant context."""

    def test_prompt_returns_string(self, challenge):
        prompt = challenge.create_subagent_prompt(
            "Look up customer", {"customer_id": "C001"}
        )
        assert isinstance(prompt, str), "create_subagent_prompt must return a string"

    def test_prompt_contains_task(self, challenge):
        prompt = challenge.create_subagent_prompt(
            "Look up customer details", {"customer_id": "C001"}
        )
        assert "customer" in prompt.lower(), (
            "Prompt must mention the task"
        )

    def test_prompt_contains_context_data(self, challenge):
        prompt = challenge.create_subagent_prompt(
            "Look up customer", {"customer_id": "C001"}
        )
        assert "C001" in prompt, (
            "Prompt must include the provided context data"
        )

    def test_prompt_does_not_contain_unrelated_data(self, challenge):
        """Customer prompt should not contain order details."""
        prompt = challenge.create_subagent_prompt(
            "Look up customer", {"customer_id": "C001"}
        )
        assert "ORD-100" not in prompt and "ORD-101" not in prompt, (
            "Customer subagent prompt should not contain order IDs"
        )

    def test_prompt_specifies_output_format(self, challenge):
        prompt = challenge.create_subagent_prompt(
            "Look up customer", {"customer_id": "C001"}
        ).lower()
        has_format = any(
            kw in prompt for kw in ["return", "respond", "output", "format", "summary", "json"]
        )
        assert has_format, (
            "Prompt should specify an expected output format"
        )


# ---------------------------------------------------------------------------
# Test 2: Subagent Dispatch
# ---------------------------------------------------------------------------

class TestSubagentDispatch:
    """dispatch_subagent must use fresh context and scoped tools."""

    def test_dispatch_returns_string(self, challenge):
        mock_response = MagicMock()
        mock_response.stop_reason = "end_turn"
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "Customer Alice Johnson, premium tier."
        mock_response.content = [text_block]

        with patch.object(challenge.client.messages, "create", return_value=mock_response) as mock_create:
            result = challenge.dispatch_subagent("Look up C001", CUSTOMER_TOOLS)

        assert isinstance(result, str), "dispatch_subagent must return a string"

    def test_dispatch_uses_provided_tools(self, challenge):
        mock_response = MagicMock()
        mock_response.stop_reason = "end_turn"
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "Result"
        mock_response.content = [text_block]

        with patch.object(challenge.client.messages, "create", return_value=mock_response) as mock_create:
            challenge.dispatch_subagent("Test", CUSTOMER_TOOLS)

        # Verify the tools passed to the API are the scoped ones
        call_kwargs = mock_create.call_args
        if call_kwargs:
            tools_used = call_kwargs.kwargs.get("tools") or call_kwargs[1].get("tools", [])
            tool_names = [t["name"] for t in tools_used]
            assert "lookup_customer" in tool_names, (
                "dispatch_subagent must pass the provided tools to the API"
            )
            assert "process_refund" not in tool_names, (
                "Customer subagent should NOT have refund tools"
            )

    def test_dispatch_uses_fresh_context(self, challenge):
        """Messages should start with just the prompt, not accumulated history."""
        mock_response = MagicMock()
        mock_response.stop_reason = "end_turn"
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "Result"
        mock_response.content = [text_block]

        with patch.object(challenge.client.messages, "create", return_value=mock_response) as mock_create:
            challenge.dispatch_subagent("Fresh prompt only", ORDER_TOOLS)

        call_kwargs = mock_create.call_args
        if call_kwargs:
            messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages", [])
            assert len(messages) == 1, (
                f"Subagent should start with 1 message (the prompt), got {len(messages)}"
            )
            assert messages[0]["role"] == "user", (
                "First message should be a user message with the prompt"
            )


# ---------------------------------------------------------------------------
# Test 3: Coordinator Flow
# ---------------------------------------------------------------------------

class TestCoordinate:
    """Coordinator must dispatch subagents and synthesize results."""

    def _mock_dispatch(self, challenge):
        """Helper to mock dispatch_subagent for testing coordinate."""
        results = [
            "Customer Alice Johnson, premium tier, active.",
            "Order ORD-101: delivered, $24.99, Cable Set.",
            "Refund REF-001 approved for $24.99.",
        ]
        with patch.object(challenge, "dispatch_subagent", side_effect=results):
            return challenge.coordinate(
                "Customer C001 wants a refund for order ORD-101."
            )

    def test_returns_dict(self, challenge):
        result = self._mock_dispatch(challenge)
        assert isinstance(result, dict), "coordinate must return a dict"

    def test_has_required_fields(self, challenge):
        result = self._mock_dispatch(challenge)
        for field in ["customer_info", "order_info", "subagents_dispatched"]:
            assert field in result, f"Result must contain '{field}'"

    def test_dispatches_multiple_subagents(self, challenge):
        result = self._mock_dispatch(challenge)
        dispatched = result["subagents_dispatched"]
        assert len(dispatched) >= 2, (
            f"Should dispatch at least 2 subagents, dispatched {len(dispatched)}"
        )

    def test_customer_info_populated(self, challenge):
        result = self._mock_dispatch(challenge)
        assert result["customer_info"] and len(result["customer_info"]) > 0, (
            "customer_info should contain data from the customer subagent"
        )

    def test_order_info_populated(self, challenge):
        result = self._mock_dispatch(challenge)
        assert result["order_info"] and len(result["order_info"]) > 0, (
            "order_info should contain data from the order subagent"
        )
