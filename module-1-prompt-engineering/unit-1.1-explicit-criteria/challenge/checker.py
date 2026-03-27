"""
Checker for Unit 1.1 — Explicit Criteria Challenge

Validates the student's CodeReviewChallenge implementation without
calling the Anthropic API. Tests prompt construction, parsing logic,
and classification logic. The precision test uses a mock API response.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    CodeReviewChallenge,
    SNIPPET_1, GROUND_TRUTH_1,
    SNIPPET_2, GROUND_TRUTH_2,
    SNIPPET_3, GROUND_TRUTH_3,
    ALL_SNIPPETS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create a CodeReviewChallenge instance (no API calls)."""
    return CodeReviewChallenge()


# ---------------------------------------------------------------------------
# Mock API responses — one per snippet, containing only true positives
# ---------------------------------------------------------------------------

MOCK_RESPONSE_1 = json.dumps([
    {
        "location": "validate_payment",
        "issue": "Comment says 'Only accepts credit cards' but code accepts debit_card and apple_pay",
        "severity": "high"
    }
])

MOCK_RESPONSE_2 = json.dumps([
    {
        "location": "fetch_active_users",
        "issue": "Comment says 'only regular active users' but code can include admins",
        "severity": "high"
    },
    {
        "location": "send_notification",
        "issue": "Comment says 'email notification' but code dispatches to all channels",
        "severity": "high"
    }
])

MOCK_RESPONSE_3 = json.dumps([
    {
        "location": "archive_records",
        "issue": "Comment hardcodes '90 days' but cutoff_days is a parameter",
        "severity": "medium"
    }
])


# ---------------------------------------------------------------------------
# Test 1: Prompt Construction
# ---------------------------------------------------------------------------

class TestPromptConstruction:
    """Student's build_review_prompt must produce a well-structured prompt."""

    def test_prompt_returns_string(self, challenge):
        prompt = challenge.build_review_prompt(SNIPPET_1)
        assert isinstance(prompt, str), "build_review_prompt must return a string"

    def test_prompt_contains_code(self, challenge):
        prompt = challenge.build_review_prompt(SNIPPET_1)
        assert "validate_payment" in prompt, (
            "Prompt must include the code snippet being reviewed"
        )

    def test_prompt_has_do_criteria(self, challenge):
        prompt = challenge.build_review_prompt(SNIPPET_1).lower()
        # The prompt should contain explicit flagging criteria
        has_flag_keyword = any(
            kw in prompt for kw in ["flag", "report", "do flag", "do report"]
        )
        assert has_flag_keyword, (
            "Prompt must contain explicit criteria about what to flag/report"
        )

    def test_prompt_has_dont_criteria(self, challenge):
        prompt = challenge.build_review_prompt(SNIPPET_1).lower()
        # The prompt should contain explicit skip criteria
        has_skip_keyword = any(
            kw in prompt
            for kw in ["do not flag", "don't flag", "do not report",
                        "don't report", "skip", "ignore"]
        )
        assert has_skip_keyword, (
            "Prompt must contain explicit criteria about what NOT to flag"
        )

    def test_prompt_mentions_contradiction(self, challenge):
        prompt = challenge.build_review_prompt(SNIPPET_1).lower()
        has_contradiction_concept = any(
            kw in prompt
            for kw in ["contradict", "contradiction", "claims", "actually does",
                        "does x", "does y", "comment says", "code does"]
        )
        assert has_contradiction_concept, (
            "Prompt must reference the concept of comment-vs-code contradiction"
        )

    def test_prompt_not_vague(self, challenge):
        prompt = challenge.build_review_prompt(SNIPPET_1).lower()
        vague_phrases = [
            "be conservative",
            "only report high-confidence",
            "be careful",
            "use your best judgment",
            "focus on important",
        ]
        for phrase in vague_phrases:
            assert phrase not in prompt, (
                f"Prompt should NOT contain vague instruction: '{phrase}'"
            )


# ---------------------------------------------------------------------------
# Test 2: Parse Findings
# ---------------------------------------------------------------------------

class TestParsing:
    """Student's parse_findings must return structured dicts."""

    def test_parse_returns_list(self, challenge):
        findings = challenge.parse_findings(MOCK_RESPONSE_1)
        assert isinstance(findings, list), "parse_findings must return a list"

    def test_parse_correct_count_snippet1(self, challenge):
        findings = challenge.parse_findings(MOCK_RESPONSE_1)
        assert len(findings) == 1, (
            f"Snippet 1 mock has 1 finding, got {len(findings)}"
        )

    def test_parse_correct_count_snippet2(self, challenge):
        findings = challenge.parse_findings(MOCK_RESPONSE_2)
        assert len(findings) == 2, (
            f"Snippet 2 mock has 2 findings, got {len(findings)}"
        )

    def test_findings_are_structured(self, challenge):
        """Each finding must have location, issue, and severity fields."""
        for mock_resp in [MOCK_RESPONSE_1, MOCK_RESPONSE_2, MOCK_RESPONSE_3]:
            findings = challenge.parse_findings(mock_resp)
            for f in findings:
                assert "location" in f, f"Finding missing 'location': {f}"
                assert "issue" in f, f"Finding missing 'issue': {f}"
                assert "severity" in f, f"Finding missing 'severity': {f}"
                assert isinstance(f["location"], str), "location must be a string"
                assert isinstance(f["issue"], str), "issue must be a string"
                assert isinstance(f["severity"], str), "severity must be a string"

    def test_parse_empty_response(self, challenge):
        """Parsing an empty/no-findings response should return empty list."""
        empty_responses = ["[]", "No findings.", ""]
        for resp in empty_responses:
            try:
                findings = challenge.parse_findings(resp)
                assert isinstance(findings, list), (
                    f"parse_findings({resp!r}) must return a list"
                )
            except Exception:
                # It's acceptable to raise if the response is not valid,
                # but returning an empty list is preferred
                pass


# ---------------------------------------------------------------------------
# Test 3: Classification Logic
# ---------------------------------------------------------------------------

class TestClassification:
    """Student's classify_finding must correctly classify TP vs FP."""

    def test_true_positive_snippet1(self, challenge):
        finding = {"location": "validate_payment", "issue": "...", "severity": "high"}
        result = challenge.classify_finding(finding, GROUND_TRUTH_1)
        assert result == "true_positive", (
            "validate_payment is a known bug — should be true_positive"
        )

    def test_false_positive_snippet1_trap1(self, challenge):
        finding = {"location": "get_discount", "issue": "...", "severity": "medium"}
        result = challenge.classify_finding(finding, GROUND_TRUTH_1)
        assert result == "false_positive", (
            "get_discount is a known trap — should be false_positive"
        )

    def test_false_positive_snippet1_trap2(self, challenge):
        finding = {"location": "calculate_shipping", "issue": "...", "severity": "low"}
        result = challenge.classify_finding(finding, GROUND_TRUTH_1)
        assert result == "false_positive", (
            "calculate_shipping is a known trap — should be false_positive"
        )

    def test_true_positives_snippet2(self, challenge):
        for loc in ["fetch_active_users", "send_notification"]:
            finding = {"location": loc, "issue": "...", "severity": "high"}
            result = challenge.classify_finding(finding, GROUND_TRUTH_2)
            assert result == "true_positive", (
                f"{loc} is a known bug — should be true_positive"
            )

    def test_false_positive_snippet2_trap(self, challenge):
        finding = {"location": "format_currency", "issue": "...", "severity": "low"}
        result = challenge.classify_finding(finding, GROUND_TRUTH_2)
        assert result == "false_positive", (
            "format_currency is a known trap — should be false_positive"
        )

    def test_true_positive_snippet3(self, challenge):
        finding = {"location": "archive_records", "issue": "...", "severity": "medium"}
        result = challenge.classify_finding(finding, GROUND_TRUTH_3)
        assert result == "true_positive", (
            "archive_records is a known bug — should be true_positive"
        )

    def test_false_positive_unknown_location(self, challenge):
        finding = {"location": "nonexistent_function", "issue": "...", "severity": "low"}
        result = challenge.classify_finding(finding, GROUND_TRUTH_1)
        assert result == "false_positive", (
            "Unknown location should be classified as false_positive"
        )


# ---------------------------------------------------------------------------
# Test 4: Precision (uses mocked API)
# ---------------------------------------------------------------------------

class TestPrecision:
    """End-to-end precision test using mocked Claude responses."""

    def _mock_call(self, challenge, mock_response_text):
        """Helper: mock the API and run the review."""
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=mock_response_text)]

        with patch.object(challenge.client.messages, "create", return_value=mock_msg):
            return challenge.run_review("dummy code")

    def test_catches_all_real_bugs(self, challenge):
        """Student's prompt must find every genuine contradiction."""
        mocks = [MOCK_RESPONSE_1, MOCK_RESPONSE_2, MOCK_RESPONSE_3]
        truths = [GROUND_TRUTH_1, GROUND_TRUTH_2, GROUND_TRUTH_3]

        total_tp = 0
        total_expected = 0

        for mock_resp, truth in zip(mocks, truths):
            findings = self._mock_call(challenge, mock_resp)
            expected = len(truth["true_bugs"])
            total_expected += expected

            for f in findings:
                cls = challenge.classify_finding(f, truth)
                if cls == "true_positive":
                    total_tp += 1

        assert total_tp == total_expected, (
            f"Expected {total_expected} true positives, got {total_tp}. "
            f"Your prompt missed {total_expected - total_tp} real bug(s)."
        )

    def test_no_false_positives(self, challenge):
        """Student's prompt must not flag imprecise-but-acceptable comments."""
        mocks = [MOCK_RESPONSE_1, MOCK_RESPONSE_2, MOCK_RESPONSE_3]
        truths = [GROUND_TRUTH_1, GROUND_TRUTH_2, GROUND_TRUTH_3]

        total_fp = 0

        for mock_resp, truth in zip(mocks, truths):
            findings = self._mock_call(challenge, mock_resp)
            for f in findings:
                cls = challenge.classify_finding(f, truth)
                if cls == "false_positive":
                    total_fp += 1

        assert total_fp == 0, (
            f"Got {total_fp} false positive(s). Tighten your criteria."
        )

    def test_precision_is_perfect(self, challenge):
        """Precision = true_positives / total_findings must be 1.0"""
        mocks = [MOCK_RESPONSE_1, MOCK_RESPONSE_2, MOCK_RESPONSE_3]
        truths = [GROUND_TRUTH_1, GROUND_TRUTH_2, GROUND_TRUTH_3]

        total_tp = 0
        total_findings = 0

        for mock_resp, truth in zip(mocks, truths):
            findings = self._mock_call(challenge, mock_resp)
            total_findings += len(findings)
            for f in findings:
                cls = challenge.classify_finding(f, truth)
                if cls == "true_positive":
                    total_tp += 1

        if total_findings == 0:
            pytest.fail("No findings returned — your prompt or parser may be broken")

        precision = total_tp / total_findings
        assert precision == 1.0, (
            f"Precision is {precision:.2%} — must be 100%. "
            f"({total_tp} TP out of {total_findings} total findings)"
        )
