"""
Unit 1.3 Checker — Structured Output via tool_use & JSON Schemas

Run with:  pytest checker.py -v
"""

import json

import pytest

from challenge import (
    INVOICE_AMBIGUOUS_PAYMENT,
    INVOICE_FULL,
    INVOICE_NO_WARRANTY,
    StructuredOutputChallenge,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def challenge():
    return StructuredOutputChallenge()


@pytest.fixture(scope="module")
def tool(challenge):
    return challenge.define_extraction_tool()


@pytest.fixture(scope="module")
def schema(tool):
    return tool["input_schema"]


# ---------------------------------------------------------------------------
# Schema structure tests (no API calls)
# ---------------------------------------------------------------------------


class TestSchemaDesign:
    """Validate that the schema follows anti-hallucination principles."""

    def test_tool_has_required_keys(self, tool):
        """Tool definition must have name, description, and input_schema."""
        assert "name" in tool, "Tool definition must have a 'name'"
        assert "description" in tool, "Tool definition must have a 'description'"
        assert "input_schema" in tool, "Tool definition must have an 'input_schema'"
        assert tool["name"] == "extract_invoice"

    def test_nullable_fields_present(self, schema):
        """Fields that may be absent MUST allow null via type: [<type>, 'null']."""
        nullable_fields = [
            "warranty_info",
            "warranty_expiry",
            "shipping_address",
            "shipping",
            "document_type_detail",
            "subtotal",
            "tax",
            "billing_address",
        ]
        props = schema.get("properties", {})
        for field in nullable_fields:
            assert field in props, f"Schema must include '{field}'"
            field_type = props[field].get("type", props[field].get("anyOf"))
            # Accept either ["string", "null"] style or anyOf style
            if isinstance(field_type, list):
                assert "null" in field_type, (
                    f"'{field}' must be nullable (include 'null' in type array). "
                    f"Got: {field_type}"
                )
            elif isinstance(field_type, str) and field_type != "null":
                # Check for anyOf pattern
                any_of = props[field].get("anyOf")
                if any_of:
                    null_types = [t for t in any_of if t.get("type") == "null"]
                    assert null_types, (
                        f"'{field}' must be nullable. Got type: {field_type}"
                    )
                else:
                    pytest.fail(
                        f"'{field}' must be nullable. Got type: {field_type}"
                    )

    def test_enum_has_other_option(self, schema):
        """document_type enum must include 'other' as an escape valve."""
        props = schema.get("properties", {})
        assert "document_type" in props, "Schema must include 'document_type'"
        dt = props["document_type"]
        enum_values = dt.get("enum", [])
        assert "other" in enum_values, (
            f"document_type enum must include 'other'. Got: {enum_values}"
        )

    def test_enum_has_unclear_option(self, schema):
        """payment_status enum must include 'unclear' as an escape valve."""
        props = schema.get("properties", {})
        assert "payment_status" in props, "Schema must include 'payment_status'"
        ps = props["payment_status"]
        enum_values = ps.get("enum", [])
        assert "unclear" in enum_values, (
            f"payment_status enum must include 'unclear'. Got: {enum_values}"
        )

    def test_required_fields_listed(self, schema):
        """All fields should be listed as required (keys always present in output)."""
        required = schema.get("required", [])
        expected_required = [
            "invoice_number",
            "vendor_name",
            "purchase_date",
            "document_type",
            "total",
            "payment_status",
        ]
        for field in expected_required:
            assert field in required, (
                f"'{field}' should be in required list. Required: {required}"
            )

    def test_line_items_is_array(self, schema):
        """line_items must be an array of objects."""
        props = schema.get("properties", {})
        assert "line_items" in props, "Schema must include 'line_items'"
        li = props["line_items"]
        assert li.get("type") == "array", "line_items must be type: array"
        assert "items" in li, "line_items must define 'items' schema"


# ---------------------------------------------------------------------------
# tool_choice scenario tests (no API calls)
# ---------------------------------------------------------------------------


class TestToolChoice:
    """Validate correct tool_choice for different scenarios."""

    def test_single_schema_forces_tool(self, challenge):
        """single_schema must force a specific tool call."""
        choice = challenge.choose_tool_choice("single_schema")
        assert choice.get("type") == "tool", (
            f"single_schema should use type='tool'. Got: {choice}"
        )
        assert "name" in choice, "Forced tool choice must include 'name'"

    def test_multiple_schemas_uses_any(self, challenge):
        """multiple_schemas must use 'any' to let model pick."""
        choice = challenge.choose_tool_choice("multiple_schemas")
        assert choice.get("type") == "any", (
            f"multiple_schemas should use type='any'. Got: {choice}"
        )

    def test_model_decides_uses_auto(self, challenge):
        """model_decides must use 'auto' so model can skip extraction."""
        choice = challenge.choose_tool_choice("model_decides")
        assert choice.get("type") == "auto", (
            f"model_decides should use type='auto'. Got: {choice}"
        )


# ---------------------------------------------------------------------------
# API integration tests (requires ANTHROPIC_API_KEY)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not __import__("os").environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping API tests",
)
class TestExtraction:
    """Test actual extraction with the API (costs a small amount)."""

    @pytest.fixture(scope="class")
    def full_result(self, challenge, tool):
        return challenge.extract_with_tool(INVOICE_FULL, tool)

    @pytest.fixture(scope="class")
    def no_warranty_result(self, challenge, tool):
        return challenge.extract_with_tool(INVOICE_NO_WARRANTY, tool)

    @pytest.fixture(scope="class")
    def ambiguous_result(self, challenge, tool):
        return challenge.extract_with_tool(INVOICE_AMBIGUOUS_PAYMENT, tool)

    def test_full_invoice_extracts_warranty(self, full_result):
        """Full invoice should have warranty data populated."""
        assert full_result.get("warranty_expiry") is not None, (
            "Full invoice has warranty data — warranty_expiry should be non-null"
        )

    def test_no_fabrication_warranty(self, no_warranty_result):
        """Invoice without warranty info must return null, not a fabricated date."""
        warranty = no_warranty_result.get("warranty_expiry")
        assert warranty is None, (
            f"No warranty info in document — warranty_expiry should be null. "
            f"Got: {warranty!r} (likely fabricated)"
        )
        warranty_info = no_warranty_result.get("warranty_info")
        assert warranty_info is None, (
            f"No warranty info in document — warranty_info should be null. "
            f"Got: {warranty_info!r}"
        )

    def test_no_fabrication_shipping(self, no_warranty_result):
        """Invoice without shipping info must return null shipping_address."""
        shipping_addr = no_warranty_result.get("shipping_address")
        assert shipping_addr is None, (
            f"No shipping address in document — shipping_address should be null. "
            f"Got: {shipping_addr!r}"
        )

    def test_ambiguous_payment_uses_unclear(self, ambiguous_result):
        """Ambiguous payment status should be 'unclear' or 'partial'."""
        status = ambiguous_result.get("payment_status")
        assert status in ("unclear", "partial"), (
            f"Ambiguous payment should be 'unclear' or 'partial'. Got: {status!r}"
        )

    def test_extraction_returns_dict(self, full_result):
        """Extraction result must be a dict."""
        assert isinstance(full_result, dict), (
            f"extract_with_tool must return a dict. Got: {type(full_result)}"
        )
