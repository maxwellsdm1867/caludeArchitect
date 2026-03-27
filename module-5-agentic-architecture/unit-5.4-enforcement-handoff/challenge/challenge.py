"""
CHALLENGE: Build Programmatic Enforcement Gates

Task Statement 1.4 — Implement prerequisite gates that enforce business
rules in code, not in prompts. Design structured handoff summaries.

Complete the three methods in EnforcementChallenge:
  1. enforce_gates(tool_name, tool_input, state) — prerequisite gate checks
  2. build_handoff(state)                        — structured handoff summary
  3. classify_rule(rule)                         — decide enforcement method

The checker tests that gates block unauthorized actions, handoffs are
structured, and rules are correctly classified.
"""

import json


# ---------------------------------------------------------------------------
# Business rules and state
# ---------------------------------------------------------------------------

BUSINESS_RULES = [
    {"id": "R1", "rule": "Identity must be verified before any refund", "consequence": "financial"},
    {"id": "R2", "rule": "Refund amount must not exceed $100 without supervisor", "consequence": "financial"},
    {"id": "R3", "rule": "Agent should use a friendly tone", "consequence": "style"},
    {"id": "R4", "rule": "Suggest related products after resolving issue", "consequence": "best_practice"},
    {"id": "R5", "rule": "All PII must be redacted from logs", "consequence": "compliance"},
    {"id": "R6", "rule": "Prefer shorter responses when possible", "consequence": "style"},
    {"id": "R7", "rule": "Escalate if customer mentions legal action", "consequence": "compliance"},
    {"id": "R8", "rule": "Transactions over $10K require compliance review", "consequence": "financial"},
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class EnforcementChallenge:
    """
    Build programmatic enforcement gates for critical business rules.
    """

    def enforce_gates(self, tool_name: str, tool_input: dict, state: dict) -> dict:
        """
        Check prerequisite gates before allowing a tool to execute.

        Gates for process_refund:
        1. state["identity_verified"] must be True
        2. tool_input["amount"] must be <= 100
        3. tool_input["reason"] must be non-empty (at least 3 chars)

        If all gates pass, return: {"allowed": True}
        If any gate fails, return: {"allowed": False, "error": "...", "required_action": "..."}

        Gates only apply to "process_refund" tool. Other tools pass through.

        Args:
            tool_name: Name of the tool being called.
            tool_input: The tool's input parameters.
            state: Current session state dict.

        Returns:
            dict with "allowed" bool and optional error/required_action.
        """
        # TODO: Implement prerequisite gates for process_refund.
        # Other tools should always be allowed.
        raise NotImplementedError("Complete enforce_gates()")

    def build_handoff(self, state: dict) -> dict:
        """
        Build a structured handoff summary for supervisor escalation.

        The handoff must include:
        - customer: id, name, identity_verified status
        - request: type, order_id, amount, reason
        - actions_taken: list of what the agent already did
        - escalation_reason: why this is being escalated
        - recommended_action: what the supervisor should do next

        Args:
            state: Current session state with customer and request info.

        Returns:
            A structured dict with the five fields above.
        """
        # TODO: Build a structured handoff from the state.
        # Include: customer info, request details, actions, reason, recommendation.
        # Exclude: full conversation history, raw API responses, internal reasoning.
        raise NotImplementedError("Complete build_handoff()")

    def classify_rule(self, rule: dict) -> str:
        """
        Classify a business rule as needing programmatic or prompt-based enforcement.

        Rules with financial, compliance, or safety consequences -> "programmatic"
        Rules about style, best practices, or suggestions -> "prompt"

        Args:
            rule: Dict with "id", "rule" text, and "consequence" type.

        Returns:
            "programmatic" or "prompt"
        """
        # TODO: Classify based on the consequence field.
        # "financial" or "compliance" -> "programmatic"
        # "style" or "best_practice" -> "prompt"
        raise NotImplementedError("Complete classify_rule()")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Enforcement & Handoff Challenge")
    print("================================")

    challenge = EnforcementChallenge()

    # Test gates
    state = {"identity_verified": False}
    result = challenge.enforce_gates("process_refund", {"amount": 50, "reason": "test"}, state)
    print(f"Gate (no identity): {result}")

    state = {"identity_verified": True}
    result = challenge.enforce_gates("process_refund", {"amount": 250, "reason": "test"}, state)
    print(f"Gate (over limit): {result}")

    # Test classification
    for rule in BUSINESS_RULES:
        cls = challenge.classify_rule(rule)
        print(f"  {rule['id']}: {cls} ({rule['consequence']})")
