"""
Checker for Unit 5.4 — Enforcement & Handoff Challenge

Validates gate logic, handoff structure, and rule classification.
No API calls needed.
"""

import json
import pytest

from challenge import EnforcementChallenge, BUSINESS_RULES


@pytest.fixture
def challenge():
    return EnforcementChallenge()


# ---------------------------------------------------------------------------
# Test 1: Prerequisite Gates
# ---------------------------------------------------------------------------

class TestGates:
    """enforce_gates must block unauthorized refunds and allow valid ones."""

    def test_blocks_without_identity(self, challenge):
        state = {"identity_verified": False}
        result = challenge.enforce_gates(
            "process_refund", {"amount": 50, "reason": "defective"}, state
        )
        assert result["allowed"] is False, (
            "Must block refund when identity is not verified"
        )
        assert "error" in result, "Blocked result must include error message"

    def test_blocks_over_limit(self, challenge):
        state = {"identity_verified": True}
        result = challenge.enforce_gates(
            "process_refund", {"amount": 250, "reason": "defective"}, state
        )
        assert result["allowed"] is False, (
            "Must block refund over $100 limit"
        )

    def test_blocks_empty_reason(self, challenge):
        state = {"identity_verified": True}
        result = challenge.enforce_gates(
            "process_refund", {"amount": 50, "reason": ""}, state
        )
        assert result["allowed"] is False, (
            "Must block refund without a valid reason"
        )

    def test_allows_valid_refund(self, challenge):
        state = {"identity_verified": True}
        result = challenge.enforce_gates(
            "process_refund", {"amount": 50, "reason": "Defective product"}, state
        )
        assert result["allowed"] is True, (
            "Must allow valid refund (identity verified, under limit, has reason)"
        )

    def test_allows_other_tools(self, challenge):
        state = {"identity_verified": False}
        result = challenge.enforce_gates(
            "lookup_customer", {"customer_id": "C001"}, state
        )
        assert result["allowed"] is True, (
            "Non-refund tools should always be allowed"
        )

    def test_boundary_amount_100(self, challenge):
        state = {"identity_verified": True}
        result = challenge.enforce_gates(
            "process_refund", {"amount": 100, "reason": "test reason"}, state
        )
        assert result["allowed"] is True, (
            "Exactly $100 should be allowed (limit is 'over $100')"
        )

    def test_boundary_amount_101(self, challenge):
        state = {"identity_verified": True}
        result = challenge.enforce_gates(
            "process_refund", {"amount": 101, "reason": "test reason"}, state
        )
        assert result["allowed"] is False, (
            "$101 should be blocked (over $100 limit)"
        )


# ---------------------------------------------------------------------------
# Test 2: Handoff Summary
# ---------------------------------------------------------------------------

class TestHandoff:
    """build_handoff must return a properly structured summary."""

    def test_has_required_fields(self, challenge):
        state = {
            "customer_id": "C001",
            "customer_name": "Alice Johnson",
            "identity_verified": True,
            "request_type": "refund",
            "order_id": "ORD-101",
            "amount": 250,
            "reason": "Double charge",
            "actions_taken": ["Verified identity", "Looked up order"],
            "escalation_reason": "Amount exceeds agent limit"
        }
        handoff = challenge.build_handoff(state)

        required = ["customer", "request", "actions_taken", "escalation_reason", "recommended_action"]
        for field in required:
            assert field in handoff, f"Handoff must contain '{field}'"

    def test_customer_has_verification_status(self, challenge):
        state = {
            "customer_id": "C001", "customer_name": "Alice",
            "identity_verified": True, "request_type": "refund",
            "order_id": "ORD-1", "amount": 50, "reason": "test",
            "actions_taken": [], "escalation_reason": "test"
        }
        handoff = challenge.build_handoff(state)
        customer = handoff.get("customer", {})
        assert "identity_verified" in str(customer) or "verified" in str(customer).lower(), (
            "Customer info must include identity verification status"
        )

    def test_no_conversation_history(self, challenge):
        state = {
            "customer_id": "C001", "customer_name": "Alice",
            "identity_verified": True, "request_type": "refund",
            "order_id": "ORD-1", "amount": 50, "reason": "test",
            "actions_taken": ["Verified identity"], "escalation_reason": "test"
        }
        handoff = challenge.build_handoff(state)
        handoff_str = json.dumps(handoff).lower()
        assert "transcript" not in handoff_str, (
            "Handoff should not contain conversation transcripts"
        )
        assert "chain of thought" not in handoff_str, (
            "Handoff should not contain internal reasoning"
        )


# ---------------------------------------------------------------------------
# Test 3: Rule Classification
# ---------------------------------------------------------------------------

class TestRuleClassification:
    """classify_rule must correctly categorize enforcement methods."""

    def test_financial_is_programmatic(self, challenge):
        for rule in BUSINESS_RULES:
            if rule["consequence"] == "financial":
                result = challenge.classify_rule(rule)
                assert result == "programmatic", (
                    f"Financial rule {rule['id']} must be programmatic, got {result}"
                )

    def test_compliance_is_programmatic(self, challenge):
        for rule in BUSINESS_RULES:
            if rule["consequence"] == "compliance":
                result = challenge.classify_rule(rule)
                assert result == "programmatic", (
                    f"Compliance rule {rule['id']} must be programmatic, got {result}"
                )

    def test_style_is_prompt(self, challenge):
        for rule in BUSINESS_RULES:
            if rule["consequence"] == "style":
                result = challenge.classify_rule(rule)
                assert result == "prompt", (
                    f"Style rule {rule['id']} should be prompt-based, got {result}"
                )

    def test_best_practice_is_prompt(self, challenge):
        for rule in BUSINESS_RULES:
            if rule["consequence"] == "best_practice":
                result = challenge.classify_rule(rule)
                assert result == "prompt", (
                    f"Best practice rule {rule['id']} should be prompt-based, got {result}"
                )

    def test_all_rules_classified(self, challenge):
        for rule in BUSINESS_RULES:
            result = challenge.classify_rule(rule)
            assert result in ["programmatic", "prompt"], (
                f"Rule {rule['id']} classified as '{result}' — must be 'programmatic' or 'prompt'"
            )
