"""
Checker for Unit 5.5 — Agent SDK Hooks Challenge

Validates normalization consistency and access control logic.
No API calls needed.
"""

import json
import re
import pytest

from challenge import (
    HooksChallenge, RAW_CUSTOMER, RAW_ORDERS, ROLE_PERMISSIONS,
)


@pytest.fixture
def challenge():
    return HooksChallenge()


ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PLAIN_MONEY = re.compile(r"^\d+\.\d{2}$")


# ---------------------------------------------------------------------------
# Test 1: PostToolUse — Date Normalization
# ---------------------------------------------------------------------------

class TestDateNormalization:
    """post_tool_use_hook must normalize all dates to ISO 8601."""

    def test_normalizes_long_date(self, challenge):
        raw = json.dumps({"signup_date": "January 15, 2023"})
        result = json.loads(challenge.post_tool_use_hook("get_customer", raw))
        assert ISO_DATE.match(result["signup_date"]), (
            f"'January 15, 2023' should become '2023-01-15', got '{result['signup_date']}'"
        )

    def test_normalizes_us_date(self, challenge):
        raw = json.dumps({"last_purchase": "03/22/2024"})
        result = json.loads(challenge.post_tool_use_hook("get_customer", raw))
        assert ISO_DATE.match(result["last_purchase"]), (
            f"'03/22/2024' should become ISO date, got '{result['last_purchase']}'"
        )

    def test_preserves_iso_date(self, challenge):
        raw = json.dumps({"renewal_date": "2024-12-01"})
        result = json.loads(challenge.post_tool_use_hook("get_customer", raw))
        assert result["renewal_date"] == "2024-12-01", (
            "ISO dates should be preserved as-is"
        )

    def test_normalizes_all_customer_dates(self, challenge):
        raw = json.dumps(RAW_CUSTOMER)
        result = json.loads(challenge.post_tool_use_hook("get_customer", raw))
        date_fields = ["signup_date", "last_purchase", "renewal_date"]
        for field in date_fields:
            assert ISO_DATE.match(result[field]), (
                f"Date field '{field}' not normalized: '{result[field]}'"
            )

    def test_normalizes_dates_in_list(self, challenge):
        raw = json.dumps(RAW_ORDERS)
        result = json.loads(challenge.post_tool_use_hook("get_orders", raw))
        for order in result:
            assert ISO_DATE.match(order["date"]), (
                f"Order date not normalized: '{order['date']}'"
            )


# ---------------------------------------------------------------------------
# Test 2: PostToolUse — Money Normalization
# ---------------------------------------------------------------------------

class TestMoneyNormalization:
    """post_tool_use_hook must normalize monetary values to plain decimals."""

    def test_strips_dollar_and_commas(self, challenge):
        raw = json.dumps({"balance": "$1,234.56"})
        result = json.loads(challenge.post_tool_use_hook("get_customer", raw))
        assert PLAIN_MONEY.match(result["balance"]), (
            f"'$1,234.56' should become '1234.56', got '{result['balance']}'"
        )

    def test_normalizes_plain_number(self, challenge):
        raw = json.dumps({"last_order_total": "89.99"})
        result = json.loads(challenge.post_tool_use_hook("get_customer", raw))
        assert PLAIN_MONEY.match(result["last_order_total"]), (
            f"'89.99' should stay '89.99', got '{result['last_order_total']}'"
        )

    def test_normalizes_money_in_list(self, challenge):
        raw = json.dumps(RAW_ORDERS)
        result = json.loads(challenge.post_tool_use_hook("get_orders", raw))
        for order in result:
            assert PLAIN_MONEY.match(order["total"]), (
                f"Order total not normalized: '{order['total']}'"
            )


# ---------------------------------------------------------------------------
# Test 3: PreToolCall — Access Control
# ---------------------------------------------------------------------------

class TestAccessControl:
    """pre_tool_call_hook must enforce role-based access."""

    def test_support_can_access_customer(self, challenge):
        result = challenge.pre_tool_call_hook("get_customer", {}, "support")
        assert result["allowed"] is True, "Support should access get_customer"

    def test_support_can_access_orders(self, challenge):
        result = challenge.pre_tool_call_hook("get_orders", {}, "support")
        assert result["allowed"] is True

    def test_analytics_can_access_orders(self, challenge):
        result = challenge.pre_tool_call_hook("get_orders", {}, "analytics")
        assert result["allowed"] is True

    def test_analytics_blocked_from_customer(self, challenge):
        result = challenge.pre_tool_call_hook("get_customer", {}, "analytics")
        assert result["allowed"] is False, (
            "Analytics should be blocked from customer PII"
        )

    def test_analytics_blocked_from_refund(self, challenge):
        result = challenge.pre_tool_call_hook("process_refund", {}, "analytics")
        assert result["allowed"] is False

    def test_unknown_role_blocked(self, challenge):
        result = challenge.pre_tool_call_hook("get_orders", {}, "unknown")
        assert result["allowed"] is False, "Unknown roles should be blocked"

    def test_admin_has_full_access(self, challenge):
        for tool in ["get_customer", "get_orders", "process_refund", "delete_customer"]:
            result = challenge.pre_tool_call_hook(tool, {}, "admin")
            assert result["allowed"] is True, (
                f"Admin should access {tool}"
            )


# ---------------------------------------------------------------------------
# Test 4: Full Pipeline
# ---------------------------------------------------------------------------

class TestFullPipeline:
    """apply_hooks must combine pre-check and post-normalization."""

    def test_blocked_call_returns_error(self, challenge):
        result = challenge.apply_hooks(
            "get_customer", {}, "analytics", json.dumps(RAW_CUSTOMER)
        )
        assert result["blocked"] is True, "Blocked call should set blocked=True"
        assert "error" in result

    def test_allowed_call_returns_normalized(self, challenge):
        result = challenge.apply_hooks(
            "get_customer", {}, "support", json.dumps(RAW_CUSTOMER)
        )
        assert result["blocked"] is False, "Allowed call should set blocked=False"
        assert "normalized_result" in result
        normalized = json.loads(result["normalized_result"])
        assert ISO_DATE.match(normalized["signup_date"]), (
            "Allowed calls should have normalized output"
        )
