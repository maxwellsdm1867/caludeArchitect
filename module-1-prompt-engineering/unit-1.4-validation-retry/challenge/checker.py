"""
Unit 1.4 Checker — Validation, Retry, and Feedback Loops

Run with:  pytest checker.py -v
"""

import json

import pytest

from challenge import (
    DOCUMENT_MISSING_WARRANTY,
    DOCUMENT_WITH_FORMAT_ERRORS,
    DOCUMENT_WITH_MATH_ERROR,
    EXTRACTION_MISSING_WARRANTY,
    EXTRACTION_SCHEMA,
    EXTRACTION_WITH_FORMAT_ERRORS,
    EXTRACTION_WITH_MATH_ERROR,
    ValidationRetryChallenge,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def challenge():
    return ValidationRetryChallenge()


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------


class TestValidation:
    """Test that validate_extraction catches the right errors."""

    def test_catches_date_format_errors(self, challenge):
        """Format errors: non-ISO dates should be flagged."""
        errors = challenge.validate_extraction(
            EXTRACTION_WITH_FORMAT_ERRORS, EXTRACTION_SCHEMA
        )
        assert len(errors) > 0, "Should detect date format errors"
        date_errors = [e for e in errors if "date" in e.lower() or "format" in e.lower()]
        assert len(date_errors) > 0, (
            f"Should flag date format issues. Got errors: {errors}"
        )

    def test_catches_math_errors(self, challenge):
        """Numeric consistency: total should match sum of components."""
        errors = challenge.validate_extraction(
            EXTRACTION_WITH_MATH_ERROR, EXTRACTION_SCHEMA
        )
        assert len(errors) > 0, "Should detect numeric consistency errors"
        math_errors = [
            e for e in errors
            if "total" in e.lower() or "sum" in e.lower() or "math" in e.lower()
                or "consistency" in e.lower() or "mismatch" in e.lower()
                or "match" in e.lower()
        ]
        assert len(math_errors) > 0, (
            f"Should flag total mismatch. Got errors: {errors}"
        )

    def test_valid_extraction_passes(self, challenge):
        """A correctly extracted document should produce no errors."""
        errors = challenge.validate_extraction(
            EXTRACTION_MISSING_WARRANTY, EXTRACTION_SCHEMA
        )
        assert errors == [], (
            f"Valid extraction should have no errors. Got: {errors}"
        )

    def test_returns_list_of_strings(self, challenge):
        """validate_extraction must return a list of strings."""
        errors = challenge.validate_extraction(
            EXTRACTION_WITH_FORMAT_ERRORS, EXTRACTION_SCHEMA
        )
        assert isinstance(errors, list), "Must return a list"
        for e in errors:
            assert isinstance(e, str), f"Each error must be a string. Got: {type(e)}"

    def test_null_nullable_fields_are_valid(self, challenge):
        """Nullable fields with null values should not generate errors."""
        extraction = {
            "invoice_number": "TEST-001",
            "vendor_name": "Test Vendor",
            "purchase_date": "2024-01-15",
            "line_items": [
                {
                    "description": "Item",
                    "quantity": 1,
                    "unit_price": 100.00,
                    "line_total": 100.00,
                }
            ],
            "subtotal": 100.00,
            "tax": None,
            "shipping": None,
            "total": 100.00,
            "payment_status": "paid",
            "warranty_expiry": None,
        }
        errors = challenge.validate_extraction(extraction, EXTRACTION_SCHEMA)
        warranty_errors = [e for e in errors if "warranty" in e.lower()]
        tax_errors = [e for e in errors if "tax" in e.lower() and "required" in e.lower()]
        assert warranty_errors == [], (
            f"Null warranty_expiry should be valid (field is nullable). Got: {warranty_errors}"
        )
        assert tax_errors == [], (
            f"Null tax should be valid (field is nullable). Got: {tax_errors}"
        )


# ---------------------------------------------------------------------------
# Retry decision tests
# ---------------------------------------------------------------------------


class TestShouldRetry:
    """Test that should_retry makes the right call for each error type."""

    def test_retry_on_format_errors(self, challenge):
        """Format errors should trigger a retry."""
        errors = challenge.validate_extraction(
            EXTRACTION_WITH_FORMAT_ERRORS, EXTRACTION_SCHEMA
        )
        result = challenge.should_retry(errors, DOCUMENT_WITH_FORMAT_ERRORS)
        assert result is True, (
            "Format errors (wrong date format) should trigger retry"
        )

    def test_retry_on_math_errors(self, challenge):
        """Numeric consistency errors should trigger a retry."""
        errors = challenge.validate_extraction(
            EXTRACTION_WITH_MATH_ERROR, EXTRACTION_SCHEMA
        )
        result = challenge.should_retry(errors, DOCUMENT_WITH_MATH_ERROR)
        assert result is True, (
            "Math/numeric errors should trigger retry"
        )

    def test_no_retry_when_no_errors(self, challenge):
        """Empty error list means no retry needed."""
        result = challenge.should_retry([], DOCUMENT_WITH_FORMAT_ERRORS)
        assert result is False, (
            "No errors means no retry needed"
        )

    def test_no_retry_for_absent_information(self, challenge):
        """Should not retry when information is absent from the source."""
        # Simulate an error for a field that doesn't exist in the document
        errors = ["warranty_expiry is required but not present"]
        result = challenge.should_retry(errors, DOCUMENT_MISSING_WARRANTY)
        assert result is False, (
            "Should not retry when warranty info is absent from source document. "
            "The data doesn't exist — retrying won't help."
        )


# ---------------------------------------------------------------------------
# Retry prompt tests
# ---------------------------------------------------------------------------


class TestBuildRetryPrompt:
    """Test that retry prompts include all necessary components."""

    def test_includes_original_document(self, challenge):
        """Retry prompt must include the original document text."""
        prompt = challenge.build_retry_prompt(
            DOCUMENT_WITH_FORMAT_ERRORS,
            EXTRACTION_WITH_FORMAT_ERRORS,
            ["purchase_date '03/15/2024' is not ISO 8601 format"],
        )
        assert "Precision Parts Ltd" in prompt, (
            "Retry prompt must include the original document"
        )

    def test_includes_failed_extraction(self, challenge):
        """Retry prompt must include the failed extraction result."""
        prompt = challenge.build_retry_prompt(
            DOCUMENT_WITH_FORMAT_ERRORS,
            EXTRACTION_WITH_FORMAT_ERRORS,
            ["purchase_date '03/15/2024' is not ISO 8601 format"],
        )
        assert "03/15/2024" in prompt, (
            "Retry prompt must include the failed extraction"
        )

    def test_includes_specific_errors(self, challenge):
        """Retry prompt must include each specific validation error."""
        errors = [
            "purchase_date '03/15/2024' is not ISO 8601 format",
            "payment_date '03/20/2024' is not ISO 8601 format",
        ]
        prompt = challenge.build_retry_prompt(
            DOCUMENT_WITH_FORMAT_ERRORS,
            EXTRACTION_WITH_FORMAT_ERRORS,
            errors,
        )
        for error in errors:
            assert error in prompt, (
                f"Retry prompt must include error: {error!r}"
            )

    def test_includes_correction_instruction(self, challenge):
        """Retry prompt must instruct the model to correct errors."""
        prompt = challenge.build_retry_prompt(
            DOCUMENT_WITH_FORMAT_ERRORS,
            EXTRACTION_WITH_FORMAT_ERRORS,
            ["purchase_date format error"],
        )
        prompt_lower = prompt.lower()
        correction_keywords = ["correct", "fix", "re-extract", "retry", "again"]
        has_correction = any(kw in prompt_lower for kw in correction_keywords)
        assert has_correction, (
            "Retry prompt must include a correction/re-extraction instruction"
        )

    def test_returns_string(self, challenge):
        """build_retry_prompt must return a string."""
        prompt = challenge.build_retry_prompt(
            DOCUMENT_WITH_FORMAT_ERRORS,
            EXTRACTION_WITH_FORMAT_ERRORS,
            ["test error"],
        )
        assert isinstance(prompt, str), (
            f"Must return a string. Got: {type(prompt)}"
        )


# ---------------------------------------------------------------------------
# Extraction loop integration tests (requires API key)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not __import__("os").environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping API tests",
)
class TestExtractionLoop:
    """Test the full extract -> validate -> retry loop."""

    @pytest.fixture(scope="class")
    def tool_definition(self):
        """A tool definition for the extraction loop test."""
        return {
            "name": "extract_invoice",
            "description": "Extract structured data from an invoice document.",
            "input_schema": {
                "type": "object",
                "required": [
                    "invoice_number", "vendor_name", "purchase_date",
                    "line_items", "total", "payment_status",
                ],
                "properties": {
                    "invoice_number": {"type": "string"},
                    "vendor_name": {"type": "string"},
                    "purchase_date": {
                        "type": "string",
                        "description": "Date in ISO 8601 format: YYYY-MM-DD",
                    },
                    "line_items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "quantity": {"type": "number"},
                                "unit_price": {"type": "number"},
                                "line_total": {"type": "number"},
                            },
                        },
                    },
                    "subtotal": {"type": ["number", "null"]},
                    "tax": {"type": ["number", "null"]},
                    "shipping": {"type": ["number", "null"]},
                    "total": {"type": "number"},
                    "payment_status": {
                        "type": "string",
                        "enum": ["paid", "unpaid", "partial", "unclear"],
                    },
                    "warranty_expiry": {"type": ["string", "null"]},
                },
            },
        }

    def test_loop_returns_dict(self, challenge, tool_definition):
        """Extraction loop must return a dict."""
        result = challenge.run_extraction_loop(
            DOCUMENT_WITH_FORMAT_ERRORS, tool_definition, max_retries=1
        )
        assert isinstance(result, dict), (
            f"run_extraction_loop must return a dict. Got: {type(result)}"
        )

    def test_loop_extracts_basic_fields(self, challenge, tool_definition):
        """Extraction loop should populate core fields."""
        result = challenge.run_extraction_loop(
            DOCUMENT_WITH_FORMAT_ERRORS, tool_definition, max_retries=2
        )
        assert "invoice_number" in result, "Result must include invoice_number"
        assert "vendor_name" in result, "Result must include vendor_name"
        assert "total" in result, "Result must include total"
