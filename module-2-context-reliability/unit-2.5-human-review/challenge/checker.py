"""
Checker for Unit 2.5 — Human Review Challenge

Validates the student's HumanReviewChallenge implementation without
calling the Anthropic API. Tests routing prompt construction, decision
parsing, and accuracy evaluation logic.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    HumanReviewChallenge,
    EXTRACTION_1, EXTRACTION_2, EXTRACTION_3, EXTRACTION_4, EXTRACTION_5,
    ALL_EXTRACTIONS,
    ACCURACY_DATA,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create a HumanReviewChallenge instance (no API calls)."""
    return HumanReviewChallenge()


# ---------------------------------------------------------------------------
# Mock API responses — correct routing decisions
# ---------------------------------------------------------------------------

MOCK_AUTO_APPROVE = json.dumps({
    "routing": "auto_approve",
    "review_fields": [],
    "reasoning": "All fields have confidence above 70% threshold"
})

MOCK_REVIEW_RECEIPT = json.dumps({
    "routing": "human_review",
    "review_fields": ["receipt_date", "line_items", "total_amount", "tax_amount"],
    "reasoning": "Multiple fields below 70% confidence threshold"
})

MOCK_REVIEW_SINGLE = json.dumps({
    "routing": "human_review",
    "review_fields": ["total_amount"],
    "reasoning": "total_amount at 33% confidence is below threshold"
})

MOCK_REVIEW_HANDWRITTEN = json.dumps({
    "routing": "human_review",
    "review_fields": ["author_name", "date", "amounts", "description", "reference_number"],
    "reasoning": "All fields below 70% confidence for handwritten note"
})


# ---------------------------------------------------------------------------
# Test 1: Routing Prompt Construction
# ---------------------------------------------------------------------------

class TestPromptConstruction:
    """Student's build_routing_prompt must use field-level confidence."""

    def test_prompt_returns_string(self, challenge):
        prompt = challenge.build_routing_prompt(EXTRACTION_1)
        assert isinstance(prompt, str), "build_routing_prompt must return a string"

    def test_prompt_contains_fields(self, challenge):
        prompt = challenge.build_routing_prompt(EXTRACTION_1)
        assert "vendor_name" in prompt or "0.97" in prompt, (
            "Prompt must include field names or confidence values"
        )

    def test_prompt_mentions_confidence_threshold(self, challenge):
        prompt = challenge.build_routing_prompt(EXTRACTION_1).lower()
        has_threshold = any(
            kw in prompt for kw in ["threshold", "70%", "0.7", "0.70",
                                     "below", "above", "confidence"]
        )
        assert has_threshold, (
            "Prompt must reference a confidence threshold for routing"
        )

    def test_prompt_routes_by_field(self, challenge):
        prompt = challenge.build_routing_prompt(EXTRACTION_2).lower()
        has_field_routing = any(
            kw in prompt for kw in ["which field", "review_fields", "specific field",
                                     "per field", "each field", "field-level"]
        )
        assert has_field_routing, (
            "Prompt must route based on per-field confidence, not whole document"
        )

    def test_prompt_not_aggregate_based(self, challenge):
        prompt = challenge.build_routing_prompt(EXTRACTION_2).lower()
        aggregate_phrases = [
            "average confidence",
            "overall confidence",
            "aggregate score",
        ]
        for phrase in aggregate_phrases:
            assert phrase not in prompt, (
                f"Prompt should NOT route based on aggregate confidence: '{phrase}'"
            )


# ---------------------------------------------------------------------------
# Test 2: Decision Parsing
# ---------------------------------------------------------------------------

class TestParsing:
    """Student's parse_routing_decision must return structured dicts."""

    def test_parse_returns_dict(self, challenge):
        result = challenge.parse_routing_decision(MOCK_AUTO_APPROVE)
        assert isinstance(result, dict), "parse_routing_decision must return a dict"

    def test_parse_has_routing(self, challenge):
        result = challenge.parse_routing_decision(MOCK_AUTO_APPROVE)
        assert "routing" in result, "Decision must have 'routing' key"
        assert result["routing"] in ("auto_approve", "human_review"), (
            "routing must be 'auto_approve' or 'human_review'"
        )

    def test_parse_has_review_fields(self, challenge):
        result = challenge.parse_routing_decision(MOCK_REVIEW_RECEIPT)
        assert "review_fields" in result, "Decision must have 'review_fields' key"
        assert isinstance(result["review_fields"], list), "review_fields must be a list"

    def test_parse_auto_approve(self, challenge):
        result = challenge.parse_routing_decision(MOCK_AUTO_APPROVE)
        assert result["routing"] == "auto_approve"
        assert result["review_fields"] == []

    def test_parse_human_review(self, challenge):
        result = challenge.parse_routing_decision(MOCK_REVIEW_RECEIPT)
        assert result["routing"] == "human_review"
        assert len(result["review_fields"]) > 0


# ---------------------------------------------------------------------------
# Test 3: Accuracy Evaluation
# ---------------------------------------------------------------------------

class TestAccuracyEvaluation:
    """Student's evaluate_accuracy must compute per-field breakdown."""

    def test_returns_dict(self, challenge):
        result = challenge.evaluate_accuracy(ACCURACY_DATA)
        assert isinstance(result, dict), "evaluate_accuracy must return a dict"

    def test_has_aggregate(self, challenge):
        result = challenge.evaluate_accuracy(ACCURACY_DATA)
        assert "aggregate_accuracy" in result, "Must have aggregate_accuracy"
        assert 0 <= result["aggregate_accuracy"] <= 1, "Accuracy must be 0-1"

    def test_has_per_doc_type(self, challenge):
        result = challenge.evaluate_accuracy(ACCURACY_DATA)
        assert "per_doc_type" in result, "Must have per_doc_type breakdown"
        assert "typed_invoices" in result["per_doc_type"]
        assert "scanned_receipts" in result["per_doc_type"]
        assert "handwritten_notes" in result["per_doc_type"]

    def test_has_failing_fields(self, challenge):
        result = challenge.evaluate_accuracy(ACCURACY_DATA)
        assert "failing_fields" in result, "Must have failing_fields list"
        assert isinstance(result["failing_fields"], list)

    def test_identifies_handwritten_failures(self, challenge):
        result = challenge.evaluate_accuracy(ACCURACY_DATA)
        failing_keys = [(f["doc_type"], f["field"]) for f in result["failing_fields"]]
        # Handwritten notes amounts (38%) should be failing
        assert any(
            dt == "handwritten_notes" and "amount" in field
            for dt, field in failing_keys
        ), "Should identify handwritten_notes amounts as failing"

    def test_typed_invoices_not_failing(self, challenge):
        result = challenge.evaluate_accuracy(ACCURACY_DATA)
        failing_types = [f["doc_type"] for f in result["failing_fields"]]
        typed_failures = [t for t in failing_types if t == "typed_invoices"]
        assert len(typed_failures) == 0, (
            "Typed invoices should have no failing fields (all above 80%)"
        )


# ---------------------------------------------------------------------------
# Test 4: End-to-End (uses mocked API)
# ---------------------------------------------------------------------------

class TestEndToEnd:
    """End-to-end test using mocked Claude responses."""

    def _mock_call(self, challenge, extraction, mock_response):
        """Helper: mock the API and run routing."""
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=mock_response)]

        with patch.object(challenge.client.messages, "create", return_value=mock_msg):
            return challenge.run_routing(extraction)

    def test_auto_approve_high_confidence(self, challenge):
        result = self._mock_call(challenge, EXTRACTION_1, MOCK_AUTO_APPROVE)
        assert result["routing"] == "auto_approve"

    def test_human_review_low_confidence(self, challenge):
        result = self._mock_call(challenge, EXTRACTION_2, MOCK_REVIEW_RECEIPT)
        assert result["routing"] == "human_review"
        assert len(result["review_fields"]) > 0

    def test_single_field_review(self, challenge):
        result = self._mock_call(challenge, EXTRACTION_3, MOCK_REVIEW_SINGLE)
        assert result["routing"] == "human_review"
        assert "total_amount" in result["review_fields"]
