"""
Checker for Unit 2.4 — Codebase Context Challenge

Validates the student's CodebaseContextChallenge implementation without
calling the Anthropic API. Tests scratchpad generation, resume prompt
construction, and recall verification logic.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    CodebaseContextChallenge,
    SESSION_1, SESSION_2, SESSION_3,
    ALL_SESSIONS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create a CodebaseContextChallenge instance (no API calls)."""
    return CodebaseContextChallenge()


# ---------------------------------------------------------------------------
# Mock API responses — recall text containing all required details
# ---------------------------------------------------------------------------

MOCK_RECALL_1 = (
    "Session decisions:\n"
    "1. Renamed PaymentGatewayService to PaymentProcessor in src/payments/gateway.py\n"
    "2. Extracted PaymentValidator into src/payments/validator.py\n"
    "3. Added event-driven pattern: PaymentProcessor emits PaymentCompleted event\n"
    "4. Deprecated endpoint: POST /api/v1/process-payment\n"
    "5. Created migration script: scripts/migrate_payment_configs.py\n"
    "6. New endpoint: POST /api/v2/payments (event-driven)"
)

MOCK_RECALL_2 = (
    "Auth migration decisions:\n"
    "1. Renamed JWTAuthenticator to TokenAuthService in src/auth/jwt_handler.py\n"
    "2. Switched signing algorithm from HS256 to RS256\n"
    "3. Added refresh token rotation with 7-day expiry\n"
    "4. Deprecated GET /auth/legacy/token endpoint\n"
    "5. Created src/auth/key_manager.py for RSA key management\n"
    "6. New endpoint: POST /auth/v2/token with RS256"
)


# ---------------------------------------------------------------------------
# Test 1: Scratchpad Generation
# ---------------------------------------------------------------------------

class TestScratchpadGeneration:
    """Student's build_scratchpad must produce structured content."""

    def test_returns_string(self, challenge):
        scratchpad = challenge.build_scratchpad(SESSION_1["decisions"])
        assert isinstance(scratchpad, str), "build_scratchpad must return a string"

    def test_contains_class_names(self, challenge):
        scratchpad = challenge.build_scratchpad(SESSION_1["decisions"])
        assert "PaymentProcessor" in scratchpad, (
            "Scratchpad must contain the new class name"
        )
        assert "PaymentValidator" in scratchpad, (
            "Scratchpad must contain the extracted class name"
        )

    def test_contains_file_paths(self, challenge):
        scratchpad = challenge.build_scratchpad(SESSION_1["decisions"])
        assert "src/payments/validator.py" in scratchpad, (
            "Scratchpad must contain new file paths"
        )

    def test_contains_endpoints(self, challenge):
        scratchpad = challenge.build_scratchpad(SESSION_1["decisions"])
        assert "/api/v1/process-payment" in scratchpad, (
            "Scratchpad must contain deprecated endpoints"
        )
        assert "/api/v2/payments" in scratchpad, (
            "Scratchpad must contain new endpoints"
        )

    def test_contains_event_name(self, challenge):
        scratchpad = challenge.build_scratchpad(SESSION_1["decisions"])
        assert "PaymentCompleted" in scratchpad, (
            "Scratchpad must contain event names"
        )

    def test_session_2_contains_algorithm(self, challenge):
        scratchpad = challenge.build_scratchpad(SESSION_2["decisions"])
        assert "RS256" in scratchpad, "Scratchpad must contain algorithm changes"
        assert "HS256" in scratchpad, "Scratchpad must contain old algorithm"

    def test_session_3_contains_table(self, challenge):
        scratchpad = challenge.build_scratchpad(SESSION_3["decisions"])
        assert "event_log" in scratchpad, "Scratchpad must contain table names"

    def test_is_structured_not_narrative(self, challenge):
        scratchpad = challenge.build_scratchpad(SESSION_1["decisions"])
        # Structured content has multiple short lines, not long paragraphs
        lines = scratchpad.strip().split("\n")
        assert len(lines) >= 5, (
            "Scratchpad should be structured with multiple lines, not a paragraph"
        )


# ---------------------------------------------------------------------------
# Test 2: Resume Prompt Construction
# ---------------------------------------------------------------------------

class TestResumePrompt:
    """Student's build_resume_prompt must produce a well-structured system prompt."""

    def test_returns_string(self, challenge):
        scratchpad = challenge.build_scratchpad(SESSION_1["decisions"])
        prompt = challenge.build_resume_prompt(scratchpad)
        assert isinstance(prompt, str), "build_resume_prompt must return a string"

    def test_contains_scratchpad(self, challenge):
        scratchpad = challenge.build_scratchpad(SESSION_1["decisions"])
        prompt = challenge.build_resume_prompt(scratchpad)
        assert "PaymentProcessor" in prompt, (
            "Resume prompt must contain the scratchpad content"
        )

    def test_has_source_of_truth_instruction(self, challenge):
        scratchpad = challenge.build_scratchpad(SESSION_1["decisions"])
        prompt = challenge.build_resume_prompt(scratchpad).lower()
        has_instruction = any(
            kw in prompt for kw in ["source of truth", "exact", "reference",
                                     "use these", "do not paraphrase", "scratchpad"]
        )
        assert has_instruction, (
            "Resume prompt must instruct the model to use scratchpad as source of truth"
        )


# ---------------------------------------------------------------------------
# Test 3: Recall Verification
# ---------------------------------------------------------------------------

class TestRecallVerification:
    """Student's verify_recall must correctly check details."""

    def test_returns_dict(self, challenge):
        result = challenge.verify_recall(MOCK_RECALL_1, SESSION_1["required_details"])
        assert isinstance(result, dict), "verify_recall must return a dict"

    def test_has_required_keys(self, challenge):
        result = challenge.verify_recall(MOCK_RECALL_1, SESSION_1["required_details"])
        assert "total" in result
        assert "found" in result
        assert "missing" in result
        assert "recall_rate" in result

    def test_finds_present_details(self, challenge):
        result = challenge.verify_recall(MOCK_RECALL_1, SESSION_1["required_details"])
        assert result["found"] > 0, "Should find details in the mock recall"

    def test_perfect_recall_rate(self, challenge):
        result = challenge.verify_recall(MOCK_RECALL_1, SESSION_1["required_details"])
        assert result["recall_rate"] >= 0.80, (
            f"Mock recall with all details should have high recall rate, "
            f"got {result['recall_rate']:.0%}"
        )

    def test_poor_recall_detected(self, challenge):
        result = challenge.verify_recall(
            "We made some changes to the codebase.",
            SESSION_1["required_details"]
        )
        assert result["found"] < result["total"], (
            "Vague text should have low recall"
        )
        assert len(result["missing"]) > 0


# ---------------------------------------------------------------------------
# Test 4: End-to-End (uses mocked API)
# ---------------------------------------------------------------------------

class TestEndToEnd:
    """End-to-end test using mocked Claude responses."""

    def _mock_call(self, challenge, session, mock_recall):
        """Helper: mock the API and run the session test."""
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=mock_recall)]

        with patch.object(challenge.client.messages, "create", return_value=mock_msg):
            return challenge.run_session_test(session)

    def test_full_pipeline_session_1(self, challenge):
        result = self._mock_call(challenge, SESSION_1, MOCK_RECALL_1)
        assert result["recall_rate"] >= 0.80

    def test_full_pipeline_session_2(self, challenge):
        result = self._mock_call(challenge, SESSION_2, MOCK_RECALL_2)
        assert result["recall_rate"] >= 0.80
