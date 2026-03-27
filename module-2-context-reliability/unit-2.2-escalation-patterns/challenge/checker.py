"""
Checker for Unit 2.2 — Escalation Patterns Challenge

Validates the student's EscalationChallenge implementation without
calling the Anthropic API. Tests prompt construction, parsing logic,
and classification logic. The escalation test uses mock API responses.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    EscalationChallenge,
    SCENARIO_1, SCENARIO_2, SCENARIO_3, SCENARIO_4,
    SCENARIO_5, SCENARIO_6, SCENARIO_7,
    ALL_SCENARIOS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create an EscalationChallenge instance (no API calls)."""
    return EscalationChallenge()


# ---------------------------------------------------------------------------
# Mock API responses — correct escalation decisions
# ---------------------------------------------------------------------------

MOCK_HANDLE = json.dumps({
    "action": "handle",
    "trigger": "within_capability",
    "reasoning": "Issue is within agent capability and policy exists"
})

MOCK_ESCALATE_HUMAN_REQUEST = json.dumps({
    "action": "escalate",
    "trigger": "explicit_human_request",
    "reasoning": "Customer explicitly requested a human agent"
})

MOCK_ESCALATE_AUTHORITY = json.dumps({
    "action": "escalate",
    "trigger": "exceeds_authority",
    "reasoning": "Amount exceeds agent refund authority"
})

MOCK_ESCALATE_POLICY_GAP = json.dumps({
    "action": "escalate",
    "trigger": "policy_gap",
    "reasoning": "No policy exists for this request type"
})

MOCK_ESCALATE_ATTEMPTS = json.dumps({
    "action": "escalate",
    "trigger": "max_attempts_exceeded",
    "reasoning": "Three failed resolution attempts"
})


# ---------------------------------------------------------------------------
# Test 1: Prompt Construction
# ---------------------------------------------------------------------------

class TestPromptConstruction:
    """Student's build_escalation_prompt must produce a well-structured prompt."""

    def test_prompt_returns_string(self, challenge):
        prompt = challenge.build_escalation_prompt(SCENARIO_1["message"], SCENARIO_1["context"])
        assert isinstance(prompt, str), "build_escalation_prompt must return a string"

    def test_prompt_contains_message(self, challenge):
        prompt = challenge.build_escalation_prompt(SCENARIO_1["message"], SCENARIO_1["context"])
        assert "UNACCEPTABLE" in prompt or SCENARIO_1["message"][:20] in prompt, (
            "Prompt must include the customer message"
        )

    def test_prompt_contains_context(self, challenge):
        prompt = challenge.build_escalation_prompt(SCENARIO_2["message"], SCENARIO_2["context"])
        assert "4200" in prompt or "4,200" in prompt or "unauthorized" in prompt.lower(), (
            "Prompt must include the context information"
        )

    def test_prompt_has_explicit_triggers(self, challenge):
        prompt = challenge.build_escalation_prompt(SCENARIO_1["message"], SCENARIO_1["context"]).lower()
        has_trigger_language = any(
            kw in prompt for kw in ["trigger", "escalate when", "escalate if",
                                     "condition", "criteria"]
        )
        assert has_trigger_language, (
            "Prompt must define explicit escalation trigger conditions"
        )

    def test_prompt_not_sentiment_based(self, challenge):
        prompt = challenge.build_escalation_prompt(SCENARIO_1["message"], SCENARIO_1["context"]).lower()
        sentiment_phrases = [
            "analyze sentiment",
            "if sentiment is negative",
            "if the customer is angry",
            "based on emotional state",
        ]
        for phrase in sentiment_phrases:
            assert phrase not in prompt, (
                f"Prompt should NOT use sentiment-based escalation: '{phrase}'"
            )

    def test_prompt_handles_human_request_trigger(self, challenge):
        prompt = challenge.build_escalation_prompt(SCENARIO_3["message"], SCENARIO_3["context"]).lower()
        has_human_trigger = any(
            kw in prompt for kw in ["human", "manager", "supervisor", "person",
                                     "explicit request", "transfer"]
        )
        assert has_human_trigger, (
            "Prompt must include a trigger for explicit human requests"
        )


# ---------------------------------------------------------------------------
# Test 2: Parse Decision
# ---------------------------------------------------------------------------

class TestParsing:
    """Student's parse_decision must return structured dicts."""

    def test_parse_returns_dict(self, challenge):
        result = challenge.parse_decision(MOCK_HANDLE)
        assert isinstance(result, dict), "parse_decision must return a dict"

    def test_parse_has_action(self, challenge):
        result = challenge.parse_decision(MOCK_HANDLE)
        assert "action" in result, "Decision must have 'action' key"
        assert result["action"] in ("handle", "escalate"), (
            "Action must be 'handle' or 'escalate'"
        )

    def test_parse_handle(self, challenge):
        result = challenge.parse_decision(MOCK_HANDLE)
        assert result["action"] == "handle"

    def test_parse_escalate(self, challenge):
        result = challenge.parse_decision(MOCK_ESCALATE_HUMAN_REQUEST)
        assert result["action"] == "escalate"

    def test_parse_has_trigger(self, challenge):
        result = challenge.parse_decision(MOCK_ESCALATE_AUTHORITY)
        assert "trigger" in result, "Decision must have 'trigger' key"
        assert isinstance(result["trigger"], str), "trigger must be a string"


# ---------------------------------------------------------------------------
# Test 3: Classification Logic
# ---------------------------------------------------------------------------

class TestClassification:
    """Student's classify_decision must correctly classify decisions."""

    def test_correct_handle(self, challenge):
        decision = {"action": "handle", "trigger": "within_capability"}
        result = challenge.classify_decision(decision, SCENARIO_1)
        assert result == "correct", "Handling S1 (angry but simple) should be correct"

    def test_correct_escalate(self, challenge):
        decision = {"action": "escalate", "trigger": "exceeds_authority"}
        result = challenge.classify_decision(decision, SCENARIO_2)
        assert result == "correct", "Escalating S2 (calm but complex) should be correct"

    def test_incorrect_escalate(self, challenge):
        decision = {"action": "escalate", "trigger": "sentiment_negative"}
        result = challenge.classify_decision(decision, SCENARIO_1)
        assert result == "incorrect", "Escalating S1 based on sentiment should be incorrect"

    def test_incorrect_handle(self, challenge):
        decision = {"action": "handle", "trigger": "within_capability"}
        result = challenge.classify_decision(decision, SCENARIO_3)
        assert result == "incorrect", "Handling S3 (explicit human request) should be incorrect"

    def test_human_request_must_escalate(self, challenge):
        decision = {"action": "escalate", "trigger": "explicit_human_request"}
        result = challenge.classify_decision(decision, SCENARIO_3)
        assert result == "correct"

    def test_policy_gap_must_escalate(self, challenge):
        decision = {"action": "escalate", "trigger": "policy_gap"}
        result = challenge.classify_decision(decision, SCENARIO_5)
        assert result == "correct"

    def test_attempts_exhausted_must_escalate(self, challenge):
        decision = {"action": "escalate", "trigger": "max_attempts"}
        result = challenge.classify_decision(decision, SCENARIO_7)
        assert result == "correct"


# ---------------------------------------------------------------------------
# Test 4: End-to-End (uses mocked API)
# ---------------------------------------------------------------------------

class TestEndToEnd:
    """End-to-end test using mocked Claude responses."""

    def _mock_call(self, challenge, scenario, mock_response):
        """Helper: mock the API and run escalation."""
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=mock_response)]

        with patch.object(challenge.client.messages, "create", return_value=mock_msg):
            return challenge.run_escalation(scenario)

    def test_handle_scenario(self, challenge):
        decision = self._mock_call(challenge, SCENARIO_1, MOCK_HANDLE)
        assert decision["action"] == "handle"

    def test_escalate_human_request(self, challenge):
        decision = self._mock_call(challenge, SCENARIO_3, MOCK_ESCALATE_HUMAN_REQUEST)
        assert decision["action"] == "escalate"

    def test_escalate_authority(self, challenge):
        decision = self._mock_call(challenge, SCENARIO_2, MOCK_ESCALATE_AUTHORITY)
        assert decision["action"] == "escalate"

    def test_all_scenarios_classified(self, challenge):
        """All scenarios must produce valid classifications."""
        mocks = {
            "S1": MOCK_HANDLE,
            "S2": MOCK_ESCALATE_AUTHORITY,
            "S3": MOCK_ESCALATE_HUMAN_REQUEST,
            "S4": MOCK_HANDLE,
            "S5": MOCK_ESCALATE_POLICY_GAP,
            "S6": MOCK_HANDLE,
            "S7": MOCK_ESCALATE_ATTEMPTS,
        }
        for scenario in ALL_SCENARIOS:
            mock_resp = mocks[scenario["id"]]
            decision = self._mock_call(challenge, scenario, mock_resp)
            cls = challenge.classify_decision(decision, scenario)
            assert cls == "correct", (
                f"Scenario {scenario['id']}: expected correct, got {cls}"
            )
