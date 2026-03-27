"""
Checker for Unit 2.1 — Context Preservation Challenge

Validates the student's ContextPreservationChallenge implementation without
calling the Anthropic API. Tests fact extraction, system prompt construction,
and preservation verification logic.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    ContextPreservationChallenge,
    CONVERSATION_1, CONVERSATION_2, CONVERSATION_3,
    ALL_CONVERSATIONS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create a ContextPreservationChallenge instance (no API calls)."""
    return ContextPreservationChallenge()


# ---------------------------------------------------------------------------
# Mock API responses — summaries containing all critical details
# ---------------------------------------------------------------------------

MOCK_SUMMARY_1 = (
    "Resolution Summary for customer CUST-88210:\n"
    "Order ORD-2024-55123, total charged $2,847.93 on November 3rd.\n"
    "Damaged item: UltraWide-34X (serial MON-2024-7712), price $649.99.\n"
    "Other items: laptop $1,899.99, cable $297.95.\n"
    "Payment: Amex ending in 3847. Customer tier: Platinum."
)

MOCK_SUMMARY_2 = (
    "Invoice dispute summary:\n"
    "Invoice INV-2024-90012 for $15,750.00 dated December 1, 2024.\n"
    "45 hours billed at $350/hour. Contract CTR-2024-4401 caps at 30 hours.\n"
    "Overage: 15 hours = $5,250 to be credited to ACC-77201.\n"
    "AP contact: Maria Rodriguez, ext 4412."
)

MOCK_SUMMARY_3 = (
    "Incident summary for TKT-2024-11234:\n"
    "Three servers down in rack R-14, Bay 3: SRV-A01, SRV-A02, SRV-A03.\n"
    "IPs: 10.0.14.101, 10.0.14.102, 10.0.14.103.\n"
    "Outage started 03:42 UTC on December 5. SLA deadline: 07:42 UTC.\n"
    "Root cause: PowerMax-3000 PDU failure (PDU-2024-8891).\n"
    "Impact: 340 users on VLAN 14.\n"
    "Spare in warehouse W-2, shelf S-14. ETA: 90 minutes."
)


# ---------------------------------------------------------------------------
# Test 1: Fact Extraction
# ---------------------------------------------------------------------------

class TestFactExtraction:
    """Student's extract_case_facts must return structured facts."""

    def test_returns_dict(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        assert isinstance(facts, dict), "extract_case_facts must return a dict"

    def test_preserves_order_number(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        facts_str = json.dumps(facts)
        assert "ORD-2024-55123" in facts_str, (
            "Extracted facts must contain the order number"
        )

    def test_preserves_amounts(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        facts_str = json.dumps(facts)
        assert "2,847.93" in facts_str or "2847.93" in facts_str, (
            "Extracted facts must contain the total amount"
        )

    def test_preserves_customer_id(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        facts_str = json.dumps(facts)
        assert "CUST-88210" in facts_str, (
            "Extracted facts must contain the customer ID"
        )

    def test_conversation_2_preserves_contract(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_2)
        facts_str = json.dumps(facts)
        assert "CTR-2024-4401" in facts_str, (
            "Extracted facts must contain the contract reference"
        )

    def test_conversation_3_preserves_servers(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_3)
        facts_str = json.dumps(facts)
        assert "SRV-A01" in facts_str, (
            "Extracted facts must contain server identifiers"
        )


# ---------------------------------------------------------------------------
# Test 2: System Prompt Construction
# ---------------------------------------------------------------------------

class TestSystemPrompt:
    """Student's build_system_prompt must produce a well-structured prompt."""

    def test_returns_string(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        prompt = challenge.build_system_prompt(facts)
        assert isinstance(prompt, str), "build_system_prompt must return a string"

    def test_contains_facts(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        prompt = challenge.build_system_prompt(facts)
        assert "ORD-2024-55123" in prompt, (
            "System prompt must contain the case facts"
        )

    def test_has_exact_value_instruction(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        prompt = challenge.build_system_prompt(facts).lower()
        has_exact_instruction = any(
            kw in prompt for kw in ["exact", "precise", "specific", "do not paraphrase",
                                     "don't paraphrase", "verbatim", "as-is"]
        )
        assert has_exact_instruction, (
            "System prompt must instruct the model to use exact values"
        )

    def test_has_facts_delimiter(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        prompt = challenge.build_system_prompt(facts)
        has_delimiter = any(
            kw in prompt for kw in ["===", "---", "CASE FACTS", "FACTS", "```"]
        )
        assert has_delimiter, (
            "System prompt must have a clearly delimited facts block"
        )

    def test_not_vague(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        prompt = challenge.build_system_prompt(facts).lower()
        vague_phrases = [
            "try to remember",
            "do your best to recall",
            "approximately",
        ]
        for phrase in vague_phrases:
            assert phrase not in prompt, (
                f"System prompt should NOT contain vague instruction: '{phrase}'"
            )


# ---------------------------------------------------------------------------
# Test 3: Preservation Verification
# ---------------------------------------------------------------------------

class TestVerification:
    """Student's verify_preservation must correctly check details."""

    def test_returns_dict_with_required_keys(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        result = challenge.verify_preservation(MOCK_SUMMARY_1, facts)
        assert "total" in result, "Result must have 'total' key"
        assert "found" in result, "Result must have 'found' key"
        assert "missing" in result, "Result must have 'missing' key"
        assert "preservation_rate" in result, "Result must have 'preservation_rate' key"

    def test_finds_present_details(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        result = challenge.verify_preservation(MOCK_SUMMARY_1, facts)
        assert result["found"] > 0, (
            "Should find at least some details in the mock summary"
        )

    def test_detects_missing_details(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        # Summary missing key details
        partial_summary = "A refund was discussed for the customer's order."
        result = challenge.verify_preservation(partial_summary, facts)
        assert result["found"] < result["total"], (
            "Should detect that details are missing from a vague summary"
        )
        assert len(result["missing"]) > 0, (
            "Missing list should contain details not found in summary"
        )

    def test_preservation_rate_calculated(self, challenge):
        facts = challenge.extract_case_facts(CONVERSATION_1)
        result = challenge.verify_preservation(MOCK_SUMMARY_1, facts)
        expected_rate = result["found"] / result["total"] if result["total"] > 0 else 0
        assert abs(result["preservation_rate"] - expected_rate) < 0.01, (
            "preservation_rate must equal found/total"
        )


# ---------------------------------------------------------------------------
# Test 4: End-to-End (uses mocked API)
# ---------------------------------------------------------------------------

class TestEndToEnd:
    """End-to-end test using mocked Claude responses."""

    def _mock_call(self, challenge, mock_summary):
        """Helper: mock the API and run the pipeline."""
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=mock_summary)]

        with patch.object(challenge.client.messages, "create", return_value=mock_msg):
            return challenge.run_preservation_test(
                CONVERSATION_1, "billing_dispute"
            )

    def test_full_pipeline_returns_results(self, challenge):
        result = self._mock_call(challenge, MOCK_SUMMARY_1)
        assert "total" in result
        assert "found" in result
        assert "preservation_rate" in result

    def test_good_summary_has_high_preservation(self, challenge):
        result = self._mock_call(challenge, MOCK_SUMMARY_1)
        assert result["preservation_rate"] >= 0.70, (
            f"Mock summary with all details should have high preservation rate, "
            f"got {result['preservation_rate']:.0%}"
        )

    def test_bad_summary_has_low_preservation(self, challenge):
        result = self._mock_call(challenge, "A refund was processed for the customer.")
        assert result["preservation_rate"] < 0.50, (
            "Vague summary should have low preservation rate"
        )
