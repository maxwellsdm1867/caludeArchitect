"""
CHALLENGE: Build Agent SDK Hooks

Task Statement 1.5 — Implement PostToolUse hooks for data normalization
and PreToolCall hooks for access control.

Complete the three methods in HooksChallenge:
  1. post_tool_use_hook(tool_name, result)      — normalize tool output
  2. pre_tool_call_hook(tool_name, input, role)  — access control
  3. apply_hooks(tool_name, input, role)         — full hook pipeline

The checker tests normalization consistency and access control correctness.
No API calls needed.
"""

import json
import re
from datetime import datetime


# ---------------------------------------------------------------------------
# Test data with inconsistent formats
# ---------------------------------------------------------------------------

RAW_CUSTOMER = {
    "name": "Alice Johnson",
    "signup_date": "January 15, 2023",
    "last_purchase": "03/22/2024",
    "renewal_date": "2024-12-01",
    "balance": "$1,234.56",
    "last_order_total": "89.99",
    "pending_refund": "$25.00"
}

RAW_ORDERS = [
    {"order_id": "ORD-100", "date": "Mar 22, 2024", "total": "$89.99"},
    {"order_id": "ORD-101", "date": "12/01/2024", "total": "24.99"},
    {"order_id": "ORD-102", "date": "November 15, 2024", "total": "$149.99"}
]

# Role permissions
ROLE_PERMISSIONS = {
    "support": ["get_customer", "get_orders", "process_refund"],
    "analytics": ["get_orders"],
    "admin": ["get_customer", "get_orders", "process_refund", "delete_customer"],
}


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class HooksChallenge:
    """
    Build hooks for data normalization and access control.
    """

    def post_tool_use_hook(self, tool_name: str, raw_result: str) -> str:
        """
        PostToolUse hook: normalize dates and monetary values in tool output.

        Normalization rules:
        - All dates -> ISO 8601 (YYYY-MM-DD)
        - All monetary values -> plain decimal with 2 places (no $, no commas)

        Date fields: any key containing "date", "purchase", "renewal", "created"
        Money fields: any key containing "balance", "total", "refund", "amount", "cost", "price"

        Must handle both dict and list inputs (parse JSON, normalize, re-serialize).

        Args:
            tool_name: The tool that produced this output.
            raw_result: JSON string of the tool's raw output.

        Returns:
            JSON string with all dates and monetary values normalized.
        """
        # TODO: Parse the JSON, normalize date and money fields, re-serialize.
        # Handle nested dicts and lists.
        # Date formats to handle: "January 15, 2023", "Mar 22, 2024",
        #   "03/22/2024", "12/01/2024", "November 15, 2024", "2024-12-01"
        # Money: strip $, strip commas, format to 2 decimal places.
        raise NotImplementedError("Complete post_tool_use_hook()")

    def pre_tool_call_hook(self, tool_name: str, tool_input: dict, user_role: str) -> dict:
        """
        PreToolCall hook: check if the user's role allows this tool call.

        Use ROLE_PERMISSIONS to determine access.
        Unknown roles are blocked from all tools.

        Args:
            tool_name: The tool being called.
            tool_input: The tool's input parameters (not used for access control).
            user_role: The user's role string.

        Returns:
            {"allowed": True} if permitted.
            {"allowed": False, "error": "..."} if blocked.
        """
        # TODO: Check ROLE_PERMISSIONS for the user_role.
        # If role not in ROLE_PERMISSIONS -> blocked.
        # If tool not in role's allowed list -> blocked.
        raise NotImplementedError("Complete pre_tool_call_hook()")

    def apply_hooks(self, tool_name: str, tool_input: dict, user_role: str, raw_result: str) -> dict:
        """
        Apply the full hook pipeline: PreToolCall check, then PostToolUse normalization.

        Steps:
        1. Run pre_tool_call_hook — if blocked, return {"blocked": True, "error": "..."}
        2. If allowed, run post_tool_use_hook on the raw_result
        3. Return {"blocked": False, "normalized_result": "..."}

        Args:
            tool_name: The tool name.
            tool_input: The tool's input.
            user_role: The user's role.
            raw_result: The raw tool output (JSON string).

        Returns:
            dict with "blocked" bool and either "error" or "normalized_result".
        """
        # TODO: Implement the full pipeline.
        raise NotImplementedError("Complete apply_hooks()")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Agent SDK Hooks Challenge")
    print("========================\n")

    challenge = HooksChallenge()

    # Test normalization
    raw = json.dumps(RAW_CUSTOMER)
    normalized = challenge.post_tool_use_hook("get_customer", raw)
    print(f"Before: {raw[:80]}...")
    print(f"After:  {normalized[:80]}...")

    # Test access control
    for role in ["support", "analytics", "admin", "unknown"]:
        result = challenge.pre_tool_call_hook("get_customer", {}, role)
        print(f"  {role} -> get_customer: {result}")
