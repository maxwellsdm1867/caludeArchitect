"""
Checker for Unit 4.2 — Structured Error Response Challenge

Validates the student's ErrorResponseChallenge implementation without
calling the Anthropic API. Tests error response construction, retry
decisions, and recovery action mapping.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    ErrorResponseChallenge,
    ERROR_SCENARIOS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create an ErrorResponseChallenge instance (no API calls)."""
    return ErrorResponseChallenge()


# ---------------------------------------------------------------------------
# Test 1: Error Response Construction
# ---------------------------------------------------------------------------

class TestErrorResponseConstruction:
    """Student's build_error_response must return structured error dicts."""

    def test_returns_dict(self, challenge):
        resp = challenge.build_error_response("not_found", {"resource": "user", "id": "123"})
        assert isinstance(resp, dict), "build_error_response must return a dict"

    def test_has_required_fields(self, challenge):
        for scenario in ERROR_SCENARIOS:
            resp = challenge.build_error_response(
                scenario["error_type"], scenario["context"]
            )
            assert "errorCategory" in resp, (
                f"Missing 'errorCategory' for {scenario['error_type']}"
            )
            assert "isRetryable" in resp, (
                f"Missing 'isRetryable' for {scenario['error_type']}"
            )
            assert "userMessage" in resp, (
                f"Missing 'userMessage' for {scenario['error_type']}"
            )

    def test_correct_categories(self, challenge):
        for scenario in ERROR_SCENARIOS:
            resp = challenge.build_error_response(
                scenario["error_type"], scenario["context"]
            )
            assert resp["errorCategory"] == scenario["expected_category"], (
                f"Error type '{scenario['error_type']}': expected category "
                f"'{scenario['expected_category']}', got '{resp['errorCategory']}'"
            )

    def test_correct_retryable_flags(self, challenge):
        for scenario in ERROR_SCENARIOS:
            resp = challenge.build_error_response(
                scenario["error_type"], scenario["context"]
            )
            assert resp["isRetryable"] == scenario["expected_retryable"], (
                f"Error type '{scenario['error_type']}': expected isRetryable="
                f"{scenario['expected_retryable']}, got {resp['isRetryable']}"
            )

    def test_retryable_errors_have_backoff(self, challenge):
        for scenario in ERROR_SCENARIOS:
            if scenario["expected_retryable"]:
                resp = challenge.build_error_response(
                    scenario["error_type"], scenario["context"]
                )
                assert "retryAfterMs" in resp, (
                    f"Retryable error '{scenario['error_type']}' must include retryAfterMs"
                )
                assert isinstance(resp["retryAfterMs"], int), (
                    f"retryAfterMs must be an integer for '{scenario['error_type']}'"
                )
                assert resp["retryAfterMs"] > 0, (
                    f"retryAfterMs must be positive for '{scenario['error_type']}'"
                )

    def test_user_message_is_string(self, challenge):
        for scenario in ERROR_SCENARIOS:
            resp = challenge.build_error_response(
                scenario["error_type"], scenario["context"]
            )
            assert isinstance(resp["userMessage"], str), (
                f"userMessage must be a string for '{scenario['error_type']}'"
            )
            assert len(resp["userMessage"]) > 10, (
                f"userMessage too short for '{scenario['error_type']}'"
            )

    def test_user_message_no_internal_details(self, challenge):
        """userMessage should not contain stack traces or internal paths."""
        for scenario in ERROR_SCENARIOS:
            resp = challenge.build_error_response(
                scenario["error_type"], scenario["context"]
            )
            msg = resp["userMessage"].lower()
            for bad_pattern in ["traceback", "stack trace", "/usr/", "exception at"]:
                assert bad_pattern not in msg, (
                    f"userMessage contains internal details: '{bad_pattern}'"
                )


# ---------------------------------------------------------------------------
# Test 2: Retry Decisions
# ---------------------------------------------------------------------------

class TestRetryDecisions:
    """Student's should_agent_retry must correctly read isRetryable."""

    def test_retry_for_retryable_errors(self, challenge):
        for scenario in ERROR_SCENARIOS:
            if scenario["expected_retryable"]:
                resp = challenge.build_error_response(
                    scenario["error_type"], scenario["context"]
                )
                assert challenge.should_agent_retry(resp) is True, (
                    f"should_agent_retry must return True for '{scenario['error_type']}'"
                )

    def test_no_retry_for_permanent_errors(self, challenge):
        for scenario in ERROR_SCENARIOS:
            if not scenario["expected_retryable"]:
                resp = challenge.build_error_response(
                    scenario["error_type"], scenario["context"]
                )
                assert challenge.should_agent_retry(resp) is False, (
                    f"should_agent_retry must return False for '{scenario['error_type']}'"
                )


# ---------------------------------------------------------------------------
# Test 3: Recovery Actions
# ---------------------------------------------------------------------------

class TestRecoveryActions:
    """Student's get_recovery_action must map categories to actions."""

    def test_retryable_errors_return_retry(self, challenge):
        for error_type in ["rate_limit", "timeout", "service_unavailable", "internal"]:
            scenario = next(s for s in ERROR_SCENARIOS if s["error_type"] == error_type)
            resp = challenge.build_error_response(
                scenario["error_type"], scenario["context"]
            )
            action = challenge.get_recovery_action(resp)
            assert action == "retry", (
                f"Recovery action for '{error_type}' should be 'retry', got '{action}'"
            )

    def test_auth_errors_return_escalate(self, challenge):
        scenario = next(s for s in ERROR_SCENARIOS if s["error_type"] == "auth_expired")
        resp = challenge.build_error_response(
            scenario["error_type"], scenario["context"]
        )
        action = challenge.get_recovery_action(resp)
        assert action == "escalate", (
            f"Recovery action for 'auth_expired' should be 'escalate', got '{action}'"
        )

    def test_validation_errors_return_correct(self, challenge):
        scenario = next(s for s in ERROR_SCENARIOS if s["error_type"] == "validation")
        resp = challenge.build_error_response(
            scenario["error_type"], scenario["context"]
        )
        action = challenge.get_recovery_action(resp)
        assert action == "correct", (
            f"Recovery action for 'validation' should be 'correct', got '{action}'"
        )

    def test_not_found_returns_inform(self, challenge):
        scenario = next(s for s in ERROR_SCENARIOS if s["error_type"] == "not_found")
        resp = challenge.build_error_response(
            scenario["error_type"], scenario["context"]
        )
        action = challenge.get_recovery_action(resp)
        assert action == "inform", (
            f"Recovery action for 'not_found' should be 'inform', got '{action}'"
        )

    def test_conflict_returns_inform(self, challenge):
        scenario = next(s for s in ERROR_SCENARIOS if s["error_type"] == "conflict")
        resp = challenge.build_error_response(
            scenario["error_type"], scenario["context"]
        )
        action = challenge.get_recovery_action(resp)
        assert action == "inform", (
            f"Recovery action for 'conflict' should be 'inform', got '{action}'"
        )

    def test_recovery_action_returns_valid_string(self, challenge):
        valid_actions = {"retry", "escalate", "correct", "inform"}
        for scenario in ERROR_SCENARIOS:
            resp = challenge.build_error_response(
                scenario["error_type"], scenario["context"]
            )
            action = challenge.get_recovery_action(resp)
            assert action in valid_actions, (
                f"Invalid recovery action '{action}' for '{scenario['error_type']}'. "
                f"Must be one of: {valid_actions}"
            )
