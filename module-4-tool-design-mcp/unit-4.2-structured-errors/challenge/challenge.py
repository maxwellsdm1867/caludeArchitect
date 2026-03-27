"""
CHALLENGE: Build Structured Error Responses for MCP Tools

Task Statement 2.2 — Design structured error responses that enable
intelligent recovery in agentic workflows.

Your goal: implement an error response builder that returns structured
metadata for every error type, enabling agents to make correct
retry/escalate decisions.

Complete the three methods in ErrorResponseChallenge:
  1. build_error_response(error_type, context)  — return structured error
  2. should_agent_retry(error_response)          — decide retry vs escalate
  3. get_recovery_action(error_response)         — suggest recovery strategy

The checker will test your responses against known error scenarios.
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# Error scenarios with expected behavior
# ---------------------------------------------------------------------------

ERROR_SCENARIOS = [
    {
        "error_type": "not_found",
        "context": {"resource": "user", "id": "usr_12345"},
        "expected_retryable": False,
        "expected_category": "not_found",
    },
    {
        "error_type": "rate_limit",
        "context": {"limit": "100/min", "retry_after_seconds": 30},
        "expected_retryable": True,
        "expected_category": "rate_limit",
    },
    {
        "error_type": "auth_expired",
        "context": {"token_type": "bearer", "expired_at": "2024-01-15T10:00:00Z"},
        "expected_retryable": False,
        "expected_category": "authentication",
    },
    {
        "error_type": "validation",
        "context": {"field": "email", "value": "not-an-email", "rule": "email_format"},
        "expected_retryable": False,
        "expected_category": "validation",
    },
    {
        "error_type": "timeout",
        "context": {"timeout_ms": 30000, "endpoint": "api.example.com"},
        "expected_retryable": True,
        "expected_category": "timeout",
    },
    {
        "error_type": "conflict",
        "context": {"resource": "order", "id": "ord_789", "current_status": "shipped"},
        "expected_retryable": False,
        "expected_category": "conflict",
    },
    {
        "error_type": "service_unavailable",
        "context": {"service": "payment_gateway", "status_code": 503},
        "expected_retryable": True,
        "expected_category": "service_unavailable",
    },
    {
        "error_type": "internal",
        "context": {"trace_id": "abc-123", "component": "database"},
        "expected_retryable": True,
        "expected_category": "internal",
    },
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class ErrorResponseChallenge:
    """
    Build structured MCP error responses that enable intelligent
    agent recovery decisions.
    """

    def build_error_response(self, error_type: str, context: dict) -> dict:
        """
        Build a structured error response for an MCP tool failure.

        The response MUST contain:
        - "errorCategory": str — classifies the failure type
        - "isRetryable": bool — whether the agent should retry
        - "userMessage": str — human-readable message safe for end users

        For retryable errors, also include:
        - "retryAfterMs": int — milliseconds to wait before retry

        Args:
            error_type: The type of error that occurred.
            context: Additional context about the error.

        Returns:
            A structured error response dict.
        """
        # TODO: Build a structured error response based on error_type.
        # Hint: Map each error_type to the correct category and retryable flag.
        # Hint: Use context to build a helpful userMessage.
        # Hint: For retryable errors, include retryAfterMs.
        raise NotImplementedError("Complete build_error_response()")

    def should_agent_retry(self, error_response: dict) -> bool:
        """
        Given a structured error response, determine if the agent should retry.

        Args:
            error_response: A structured error dict from build_error_response().

        Returns:
            True if the agent should retry, False if it should escalate.
        """
        # TODO: Extract the retry decision from the error response.
        # Hint: The isRetryable field is the answer.
        raise NotImplementedError("Complete should_agent_retry()")

    def get_recovery_action(self, error_response: dict) -> str:
        """
        Given a structured error response, suggest a recovery action.

        Recovery actions:
        - "retry"    — for retryable errors (rate_limit, timeout, etc.)
        - "escalate" — for auth errors (user needs to re-authenticate)
        - "correct"  — for validation errors (user needs to fix input)
        - "inform"   — for not_found, conflict (tell user the state)

        Args:
            error_response: A structured error dict.

        Returns:
            One of: "retry", "escalate", "correct", "inform"
        """
        # TODO: Map errorCategory to recovery action.
        # Hint: retryable errors -> "retry"
        # Hint: auth errors -> "escalate"
        # Hint: validation errors -> "correct"
        # Hint: not_found, conflict -> "inform"
        raise NotImplementedError("Complete get_recovery_action()")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Structured Error Response Challenge")
    print("====================================")
    print("Goal: Correct structured responses for all error types\n")

    challenge = ErrorResponseChallenge()

    passed = 0
    total = len(ERROR_SCENARIOS)

    for scenario in ERROR_SCENARIOS:
        try:
            resp = challenge.build_error_response(
                scenario["error_type"], scenario["context"]
            )
            retry = challenge.should_agent_retry(resp)
            action = challenge.get_recovery_action(resp)

            retryable_ok = resp.get("isRetryable") == scenario["expected_retryable"]
            category_ok = resp.get("errorCategory") == scenario["expected_category"]
            has_message = bool(resp.get("userMessage"))
            retry_decision_ok = retry == scenario["expected_retryable"]

            all_ok = retryable_ok and category_ok and has_message and retry_decision_ok
            tag = "PASS" if all_ok else "FAIL"
            if all_ok:
                passed += 1

            print(f"  [{tag}] {scenario['error_type']}")
            if not all_ok:
                if not retryable_ok:
                    print(f"    isRetryable: {resp.get('isRetryable')} (expected {scenario['expected_retryable']})")
                if not category_ok:
                    print(f"    errorCategory: {resp.get('errorCategory')} (expected {scenario['expected_category']})")
                if not has_message:
                    print(f"    Missing userMessage")
                if not retry_decision_ok:
                    print(f"    should_agent_retry returned {retry} (expected {scenario['expected_retryable']})")
        except NotImplementedError as e:
            print(f"  [SKIP] {scenario['error_type']} — {e}")

    print(f"\nScore: {passed}/{total}")
    if passed == total:
        print("CHALLENGE PASSED!")
