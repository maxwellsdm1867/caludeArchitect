"""
Unit 1.4 Challenge: Build a Validation-Retry Loop

Given extraction results that may have errors, implement a complete
validation-retry pipeline that:
  - Validates extraction output against expected formats and consistency rules
  - Decides whether a retry would help (vs. information simply being absent)
  - Builds retry prompts with specific error feedback
  - Orchestrates the full extract -> validate -> retry loop

Run the checker to validate your solution:
    pytest checker.py -v
"""

import json
import re
from datetime import datetime
from typing import Any

import anthropic

# ---------------------------------------------------------------------------
# Test data — extractions with known issues
# ---------------------------------------------------------------------------

DOCUMENT_WITH_FORMAT_ERRORS = """
INVOICE #INV-2024-0331
Vendor: Precision Parts Ltd.
Date: March 15, 2024

Items:
  1. Titanium Rod TR-100 — Qty: 5 — Unit: $120.00 — Total: $600.00
  2. Steel Plate SP-50 — Qty: 10 — Unit: $45.00 — Total: $450.00

Subtotal: $1,050.00
Tax (9%): $94.50
Total: $1,144.50

Payment: Paid via wire transfer on March 20, 2024
"""

EXTRACTION_WITH_FORMAT_ERRORS = {
    "invoice_number": "INV-2024-0331",
    "vendor_name": "Precision Parts Ltd.",
    "purchase_date": "03/15/2024",  # Wrong format — should be 2024-03-15
    "line_items": [
        {
            "description": "Titanium Rod TR-100",
            "quantity": 5,
            "unit_price": 120.00,
            "line_total": 600.00,
        },
        {
            "description": "Steel Plate SP-50",
            "quantity": 10,
            "unit_price": 45.00,
            "line_total": 450.00,
        },
    ],
    "subtotal": 1050.00,
    "tax": 94.50,
    "total": 1144.50,
    "payment_status": "paid",
    "payment_date": "03/20/2024",  # Wrong format — should be 2024-03-20
}

DOCUMENT_WITH_MATH_ERROR = """
INVOICE #INV-2024-0445
Vendor: QuickShip Supplies
Date: 2024-06-01

Items:
  1. Bubble Wrap Roll (Large) — Qty: 20 — Unit: $12.00 — Total: $240.00
  2. Packing Tape 3-inch — Qty: 50 — Unit: $3.50 — Total: $175.00
  3. Shipping Labels (Roll of 500) — Qty: 4 — Unit: $18.00 — Total: $72.00

Subtotal: $487.00
Tax (8%): $38.96
Shipping: $15.00
Total: $540.96

Payment: Unpaid — Due by 2024-07-01
"""

EXTRACTION_WITH_MATH_ERROR = {
    "invoice_number": "INV-2024-0445",
    "vendor_name": "QuickShip Supplies",
    "purchase_date": "2024-06-01",
    "line_items": [
        {
            "description": "Bubble Wrap Roll (Large)",
            "quantity": 20,
            "unit_price": 12.00,
            "line_total": 240.00,
        },
        {
            "description": "Packing Tape 3-inch",
            "quantity": 50,
            "unit_price": 3.50,
            "line_total": 175.00,
        },
        {
            "description": "Shipping Labels (Roll of 500)",
            "quantity": 4,
            "unit_price": 18.00,
            "line_total": 72.00,
        },
    ],
    "subtotal": 487.00,
    "tax": 38.96,
    "shipping": 15.00,
    "total": 580.96,  # Wrong — should be 540.96 (487 + 38.96 + 15 = 540.96)
    "payment_status": "unpaid",
}

DOCUMENT_MISSING_WARRANTY = """
INVOICE #INV-2024-0512
Vendor: Office Basics Inc.
Date: 2024-07-10

Items:
  1. Copy Paper A4 — Qty: 100 — Unit: $5.00 — Total: $500.00

Total: $500.00
Payment: Paid
"""

EXTRACTION_MISSING_WARRANTY = {
    "invoice_number": "INV-2024-0512",
    "vendor_name": "Office Basics Inc.",
    "purchase_date": "2024-07-10",
    "line_items": [
        {
            "description": "Copy Paper A4",
            "quantity": 100,
            "unit_price": 5.00,
            "line_total": 500.00,
        },
    ],
    "subtotal": 500.00,
    "tax": None,
    "shipping": None,
    "total": 500.00,
    "payment_status": "paid",
    "warranty_expiry": None,  # Correctly null — no warranty in document
}

# ---------------------------------------------------------------------------
# The schema for validation reference
# ---------------------------------------------------------------------------

EXTRACTION_SCHEMA = {
    "invoice_number": {"type": "string", "required": True},
    "vendor_name": {"type": "string", "required": True},
    "purchase_date": {"type": "string", "format": "date-iso8601", "required": True},
    "line_items": {"type": "array", "required": True},
    "subtotal": {"type": "number", "nullable": True},
    "tax": {"type": "number", "nullable": True},
    "shipping": {"type": "number", "nullable": True},
    "total": {"type": "number", "required": True},
    "payment_status": {
        "type": "string",
        "enum": ["paid", "unpaid", "partial", "unclear"],
        "required": True,
    },
    "payment_date": {"type": "string", "format": "date-iso8601", "nullable": True},
    "warranty_expiry": {"type": "string", "format": "date-iso8601", "nullable": True},
}


class ValidationRetryChallenge:
    """Implement the four methods below to pass the checker."""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    # ------------------------------------------------------------------
    # 1. Validate extraction output
    # ------------------------------------------------------------------
    def validate_extraction(
        self, extraction: dict, schema: dict
    ) -> list[str]:
        """
        Validate an extraction result against the schema and return errors.

        Checks to implement:
          - Date fields with format "date-iso8601" must match YYYY-MM-DD
          - Required non-nullable fields must be present and non-null
          - Numeric consistency: if line_items, subtotal, tax, shipping, and
            total are all present, verify that
            sum(line_totals) ≈ subtotal (if subtotal is not None)
            and subtotal + tax + shipping ≈ total (within $0.02 tolerance)
          - payment_status must be a valid enum value if enum is defined

        Args:
            extraction: The extraction result dict to validate.
            schema: The EXTRACTION_SCHEMA dict defining field rules.

        Returns:
            List of error strings (empty list if valid).
        """
        # TODO: Implement validation logic.
        # Hint: Use datetime.strptime to check date formats.
        # Hint: Use abs(a - b) < 0.02 for numeric tolerance.
        # Hint: Return a descriptive string for each error found.
        raise NotImplementedError("Implement validate_extraction()")

    # ------------------------------------------------------------------
    # 2. Decide whether to retry
    # ------------------------------------------------------------------
    def should_retry(self, errors: list[str], source_document: str) -> bool:
        """
        Decide whether retrying would help, based on the error types.

        Rules:
          - Format errors (wrong date format, etc.) → retry (True)
          - Numeric/math errors (totals don't add up) → retry (True)
          - Information absent from source document → do NOT retry (False)
          - Empty error list → do NOT retry (False)

        To detect "absent information" errors: check if the error mentions
        a field whose data genuinely doesn't exist in the source_document.
        For example, if the error says "warranty_expiry is required" but
        the source has no warranty info, don't retry.

        Args:
            errors: List of validation error strings.
            source_document: The original document text.

        Returns:
            True if retry would likely help, False otherwise.
        """
        # TODO: Implement retry decision logic.
        # Hint: Parse error strings to determine the error type.
        # Hint: Check if the source document contains relevant keywords
        #       for fields flagged in errors.
        raise NotImplementedError("Implement should_retry()")

    # ------------------------------------------------------------------
    # 3. Build a retry prompt
    # ------------------------------------------------------------------
    def build_retry_prompt(
        self,
        document: str,
        failed_extraction: dict,
        errors: list[str],
    ) -> str:
        """
        Build a retry prompt that includes specific error feedback.

        The prompt MUST include:
          1. The original document
          2. The failed extraction (as formatted JSON)
          3. Each specific validation error
          4. An instruction to re-extract while correcting the errors

        Args:
            document: The original source document text.
            failed_extraction: The extraction dict that failed validation.
            errors: List of validation error strings.

        Returns:
            The complete retry prompt string.
        """
        # TODO: Build the retry prompt.
        # Hint: Use json.dumps(failed_extraction, indent=2) for readability.
        # Hint: Number each error for clarity.
        raise NotImplementedError("Implement build_retry_prompt()")

    # ------------------------------------------------------------------
    # 4. Orchestrate the full extraction loop
    # ------------------------------------------------------------------
    def run_extraction_loop(
        self,
        document: str,
        tool_definition: dict,
        max_retries: int = 2,
    ) -> dict:
        """
        Run the full extract -> validate -> retry loop.

        Steps:
          1. Call the API to extract structured data (using tool_use)
          2. Validate the extraction
          3. If errors and should_retry: build retry prompt, re-extract
          4. Repeat up to max_retries times
          5. Return the final extraction (with a "_validation_errors" key
             if there are still errors after all retries)

        Args:
            document: The source document text.
            tool_definition: The Anthropic tool definition dict.
            max_retries: Maximum number of retry attempts.

        Returns:
            dict with extracted data. Includes "_validation_errors" key
            (list of strings) if validation still fails after retries.
        """
        # TODO: Implement the full extraction loop.
        # Hint: Use extract_with_tool from Unit 1.3 as the extraction step.
        # Hint: Track retry count and break when valid or max_retries hit.
        raise NotImplementedError("Implement run_extraction_loop()")


# ---------------------------------------------------------------------------
# Manual testing
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    challenge = ValidationRetryChallenge()

    print("=== Test 1: Format Errors ===")
    errors = challenge.validate_extraction(
        EXTRACTION_WITH_FORMAT_ERRORS, EXTRACTION_SCHEMA
    )
    print(f"Errors found: {errors}")
    should = challenge.should_retry(errors, DOCUMENT_WITH_FORMAT_ERRORS)
    print(f"Should retry: {should}")
    if errors:
        prompt = challenge.build_retry_prompt(
            DOCUMENT_WITH_FORMAT_ERRORS,
            EXTRACTION_WITH_FORMAT_ERRORS,
            errors,
        )
        print(f"Retry prompt length: {len(prompt)} chars")
    print()

    print("=== Test 2: Math Error ===")
    errors = challenge.validate_extraction(
        EXTRACTION_WITH_MATH_ERROR, EXTRACTION_SCHEMA
    )
    print(f"Errors found: {errors}")
    should = challenge.should_retry(errors, DOCUMENT_WITH_MATH_ERROR)
    print(f"Should retry: {should}")
    print()

    print("=== Test 3: Missing Warranty (no errors expected) ===")
    errors = challenge.validate_extraction(
        EXTRACTION_MISSING_WARRANTY, EXTRACTION_SCHEMA
    )
    print(f"Errors found: {errors}")
    print()
