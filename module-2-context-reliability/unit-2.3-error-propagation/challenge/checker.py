"""
Checker for Unit 2.3 — Error Propagation Challenge

Validates the student's ErrorPropagationChallenge implementation without
calling the Anthropic API. Tests coordinator prompt construction, response
parsing, and error classification logic.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    ErrorPropagationChallenge,
    PIPELINE_1, PIPELINE_2, PIPELINE_3,
    ALL_PIPELINES,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create an ErrorPropagationChallenge instance (no API calls)."""
    return ErrorPropagationChallenge()


# ---------------------------------------------------------------------------
# Mock API responses — correct coordinator decisions
# ---------------------------------------------------------------------------

MOCK_RESPONSE_1 = json.dumps({
    "can_proceed": True,
    "failed_agents": ["database_agent", "file_reader_agent"],
    "successful_agents": ["web_search_agent"],
    "recovery_actions": ["retry database with backoff", "request file access"],
    "data_completeness": "partial"
})

MOCK_RESPONSE_2 = json.dumps({
    "can_proceed": False,
    "failed_agents": ["payment_agent"],
    "successful_agents": ["inventory_agent"],
    "recovery_actions": ["retry payment gateway after 30s", "try backup gateway"],
    "data_completeness": "incomplete"
})

MOCK_RESPONSE_3 = json.dumps({
    "can_proceed": True,
    "failed_agents": ["social_agent"],
    "successful_agents": ["crm_agent", "analytics_agent"],
    "recovery_actions": ["search social by name instead of email"],
    "data_completeness": "partial"
})


# ---------------------------------------------------------------------------
# Test 1: Coordinator Prompt Construction
# ---------------------------------------------------------------------------

class TestPromptConstruction:
    """Student's build_coordinator_prompt must produce a well-structured prompt."""

    def test_prompt_returns_string(self, challenge):
        prompt = challenge.build_coordinator_prompt(PIPELINE_1["results"])
        assert isinstance(prompt, str), "build_coordinator_prompt must return a string"

    def test_prompt_contains_results(self, challenge):
        prompt = challenge.build_coordinator_prompt(PIPELINE_1["results"])
        assert "database_agent" in prompt or "connection_timeout" in prompt, (
            "Prompt must include the pipeline results"
        )

    def test_prompt_distinguishes_error_types(self, challenge):
        prompt = challenge.build_coordinator_prompt(PIPELINE_1["results"]).lower()
        has_distinction = any(
            kw in prompt for kw in ["access failure", "empty result",
                                     "couldn't look", "looked and found nothing",
                                     "error_type", "status"]
        )
        assert has_distinction, (
            "Prompt must instruct coordinator to distinguish access failures from empty results"
        )

    def test_prompt_requires_failure_reporting(self, challenge):
        prompt = challenge.build_coordinator_prompt(PIPELINE_1["results"]).lower()
        has_reporting = any(
            kw in prompt for kw in ["failed", "error", "report", "which agent",
                                     "successful", "failed_agents"]
        )
        assert has_reporting, (
            "Prompt must require reporting which agents failed and succeeded"
        )

    def test_prompt_not_silent_suppression(self, challenge):
        prompt = challenge.build_coordinator_prompt(PIPELINE_1["results"]).lower()
        suppression_phrases = [
            "ignore errors",
            "proceed regardless",
            "skip failed",
            "treat empty as success",
        ]
        for phrase in suppression_phrases:
            assert phrase not in prompt, (
                f"Prompt should NOT contain silent suppression: '{phrase}'"
            )


# ---------------------------------------------------------------------------
# Test 2: Response Parsing
# ---------------------------------------------------------------------------

class TestParsing:
    """Student's parse_coordinator_response must return structured decisions."""

    def test_parse_returns_dict(self, challenge):
        result = challenge.parse_coordinator_response(MOCK_RESPONSE_1)
        assert isinstance(result, dict), "parse_coordinator_response must return a dict"

    def test_parse_has_can_proceed(self, challenge):
        result = challenge.parse_coordinator_response(MOCK_RESPONSE_1)
        assert "can_proceed" in result, "Decision must have 'can_proceed' key"
        assert isinstance(result["can_proceed"], bool), "can_proceed must be a bool"

    def test_parse_has_failed_agents(self, challenge):
        result = challenge.parse_coordinator_response(MOCK_RESPONSE_1)
        assert "failed_agents" in result, "Decision must have 'failed_agents' key"
        assert isinstance(result["failed_agents"], list), "failed_agents must be a list"

    def test_parse_has_successful_agents(self, challenge):
        result = challenge.parse_coordinator_response(MOCK_RESPONSE_1)
        assert "successful_agents" in result, "Decision must have 'successful_agents' key"

    def test_parse_pipeline_1(self, challenge):
        result = challenge.parse_coordinator_response(MOCK_RESPONSE_1)
        assert result["can_proceed"] == True
        assert "database_agent" in result["failed_agents"]
        assert "web_search_agent" in result["successful_agents"]

    def test_parse_pipeline_2_cannot_proceed(self, challenge):
        result = challenge.parse_coordinator_response(MOCK_RESPONSE_2)
        assert result["can_proceed"] == False


# ---------------------------------------------------------------------------
# Test 3: Error Classification
# ---------------------------------------------------------------------------

class TestErrorClassification:
    """Student's classify_error must distinguish access failures from empty results."""

    def test_timeout_is_access_failure(self, challenge):
        error = {"error_type": "connection_timeout", "attempted_query": "..."}
        result = challenge.classify_error(error)
        assert result == "access_failure", (
            "connection_timeout should be classified as access_failure"
        )

    def test_permission_denied_is_access_failure(self, challenge):
        error = {"error_type": "permission_denied", "attempted_query": "..."}
        result = challenge.classify_error(error)
        assert result == "access_failure", (
            "permission_denied should be classified as access_failure"
        )

    def test_service_unavailable_is_access_failure(self, challenge):
        error = {"error_type": "service_unavailable", "attempted_query": "..."}
        result = challenge.classify_error(error)
        assert result == "access_failure", (
            "service_unavailable should be classified as access_failure"
        )

    def test_empty_result_is_empty_result(self, challenge):
        error = {"error_type": "empty_result", "attempted_query": "..."}
        result = challenge.classify_error(error)
        assert result == "empty_result", (
            "empty_result should be classified as empty_result"
        )

    def test_not_found_is_empty_result(self, challenge):
        error = {"error_type": "not_found", "attempted_query": "..."}
        result = challenge.classify_error(error)
        assert result == "empty_result", (
            "not_found should be classified as empty_result"
        )


# ---------------------------------------------------------------------------
# Test 4: End-to-End (uses mocked API)
# ---------------------------------------------------------------------------

class TestEndToEnd:
    """End-to-end test using mocked Claude responses."""

    def _mock_call(self, challenge, pipeline, mock_response):
        """Helper: mock the API and run the pipeline test."""
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=mock_response)]

        with patch.object(challenge.client.messages, "create", return_value=mock_msg):
            return challenge.run_pipeline_test(pipeline)

    def test_pipeline_1_partial_proceed(self, challenge):
        result = self._mock_call(challenge, PIPELINE_1, MOCK_RESPONSE_1)
        assert result["can_proceed"] == True
        assert "database_agent" in result["failed_agents"]

    def test_pipeline_2_cannot_proceed(self, challenge):
        result = self._mock_call(challenge, PIPELINE_2, MOCK_RESPONSE_2)
        assert result["can_proceed"] == False

    def test_pipeline_3_partial_proceed(self, challenge):
        result = self._mock_call(challenge, PIPELINE_3, MOCK_RESPONSE_3)
        assert result["can_proceed"] == True
        assert "social_agent" in result["failed_agents"]
