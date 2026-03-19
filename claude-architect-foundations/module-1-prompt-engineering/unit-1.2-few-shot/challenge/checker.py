"""
Checker for Unit 1.2 — Few-Shot Extraction Challenge

Validates the student's FewShotChallenge implementation without calling
the Anthropic API. Tests example construction, prompt building, and
missing-field handling. The extraction test uses mock API responses.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    FewShotChallenge,
    EXTRACTION_SCHEMA,
    ALL_DOCUMENTS,
    GROUND_TRUTH,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create a FewShotChallenge instance (no API calls)."""
    return FewShotChallenge()


# ---------------------------------------------------------------------------
# Mock API responses — one per document type
# ---------------------------------------------------------------------------

MOCK_INVOICE_RESPONSE = json.dumps({
    "vendor": "Acme Corp",
    "items": [
        {"name": "Enterprise License (annual)", "price": 12000.00},
        {"name": "Premium Support Package", "price": 3600.00},
        {"name": "Custom Integration Fee", "price": 2400.00}
    ],
    "date": "2025-03-15",
    "total": 19485.00,
    "tax": 1485.00,
    "payment_method": "Wire Transfer",
    "notes": None
})

MOCK_RECEIPT_RESPONSE = json.dumps({
    "vendor": "Joe's Hardware",
    "items": [
        {"name": "Hammer", "price": 12.99},
        {"name": "Box of Nails", "price": 4.50},
        {"name": "Wood Glue", "price": 7.25}
    ],
    "date": "2025-03-22",
    "total": 26.78,
    "tax": 2.04,
    "payment_method": "VISA ending 4532",
    "notes": None
})

MOCK_EMAIL_RESPONSE = json.dumps({
    "vendor": "VendorCorp",
    "items": [
        {"name": "Strategy workshop (Feb 3-5)", "price": 8500.00},
        {"name": "Follow-up report", "price": 2000.00},
        {"name": "Travel expenses", "price": 1200.00}
    ],
    "date": None,
    "total": 11700.00,
    "tax": 0.0,
    "payment_method": "ACH",
    "notes": None
})

MOCK_CONTRACT_RESPONSE = json.dumps({
    "vendor": "TechFlow Solutions",
    "items": [
        {"name": "Monthly data pipeline maintenance", "price": 4500.00},
        {"name": "Quarterly performance audit", "price": 3000.00},
        {"name": "Emergency support (as needed)", "price": 250.00}
    ],
    "date": "2025-01-01",
    "total": 70000.00,
    "tax": None,
    "payment_method": None,
    "notes": "Prices are per-period. Emergency support is hourly. Tax not included."
})

MOCK_HANDWRITTEN_RESPONSE = json.dumps({
    "vendor": None,
    "items": [
        {"name": "lumber (about 40 board feet)", "price": 186.00},
        {"name": "paint, 3 cans", "price": 67.00},
        {"name": "brushes + misc", "price": 25.00}
    ],
    "date": "2025-03-10",
    "total": 278.00,
    "tax": None,
    "payment_method": "cash",
    "notes": "Need reimbursement. No receipt for misc items."
})

MOCK_RESPONSES = {
    "invoice": MOCK_INVOICE_RESPONSE,
    "receipt": MOCK_RECEIPT_RESPONSE,
    "email": MOCK_EMAIL_RESPONSE,
    "contract": MOCK_CONTRACT_RESPONSE,
    "handwritten": MOCK_HANDWRITTEN_RESPONSE,
}


# ---------------------------------------------------------------------------
# Test 1: Example Construction
# ---------------------------------------------------------------------------

class TestExampleConstruction:
    """Student's build_examples must return well-structured examples."""

    def test_returns_list(self, challenge):
        examples = challenge.build_examples()
        assert isinstance(examples, list), "build_examples must return a list"

    def test_correct_count(self, challenge):
        examples = challenge.build_examples()
        assert 3 <= len(examples) <= 4, (
            f"Expected 3-4 examples, got {len(examples)}"
        )

    def test_example_structure(self, challenge):
        examples = challenge.build_examples()
        for i, ex in enumerate(examples):
            assert "input" in ex, f"Example {i} missing 'input'"
            assert "output" in ex, f"Example {i} missing 'output'"
            assert "reasoning" in ex, f"Example {i} missing 'reasoning'"
            assert isinstance(ex["input"], str), f"Example {i} input must be str"
            assert isinstance(ex["output"], dict), f"Example {i} output must be dict"
            assert isinstance(ex["reasoning"], str), f"Example {i} reasoning must be str"

    def test_examples_have_reasoning(self, challenge):
        """Each example's reasoning must be meaningful (>20 chars)."""
        examples = challenge.build_examples()
        for i, ex in enumerate(examples):
            assert len(ex["reasoning"]) > 20, (
                f"Example {i} reasoning is too short — must explain extraction decisions"
            )

    def test_at_least_one_null_example(self, challenge):
        """At least one example must demonstrate null field handling."""
        examples = challenge.build_examples()
        has_null = False
        for ex in examples:
            output = ex["output"]
            for key, val in output.items():
                if val is None:
                    has_null = True
                    break
            if has_null:
                break
        assert has_null, (
            "At least one example must include a null field to demonstrate "
            "correct handling of missing data"
        )

    def test_examples_cover_multiple_formats(self, challenge):
        """Examples should not all look the same — check for variety."""
        examples = challenge.build_examples()
        inputs = [ex["input"] for ex in examples]
        # Simple heuristic: at least 2 examples should differ in length by >50%
        lengths = sorted(len(inp) for inp in inputs)
        if len(lengths) >= 2:
            ratio = lengths[-1] / max(lengths[0], 1)
            assert ratio > 1.3, (
                "Examples all seem similar in length — include varied document types"
            )


# ---------------------------------------------------------------------------
# Test 2: Prompt Construction
# ---------------------------------------------------------------------------

class TestPromptConstruction:
    """Student's build_extraction_prompt must produce a well-formed prompt."""

    def test_returns_string(self, challenge):
        examples = challenge.build_examples()
        prompt = challenge.build_extraction_prompt("Test document", examples)
        assert isinstance(prompt, str), "build_extraction_prompt must return a string"

    def test_prompt_contains_document(self, challenge):
        examples = challenge.build_examples()
        prompt = challenge.build_extraction_prompt("UNIQUE_DOC_MARKER_XYZ", examples)
        assert "UNIQUE_DOC_MARKER_XYZ" in prompt, (
            "Prompt must include the target document text"
        )

    def test_prompt_contains_examples(self, challenge):
        examples = challenge.build_examples()
        prompt = challenge.build_extraction_prompt("Some document", examples)
        # Check that example content appears in the prompt
        for ex in examples:
            # At least part of the example input should be in the prompt
            assert ex["input"][:30] in prompt or ex["reasoning"][:30] in prompt, (
                "Prompt must include the few-shot examples"
            )

    def test_prompt_mentions_json(self, challenge):
        examples = challenge.build_examples()
        prompt = challenge.build_extraction_prompt("Test doc", examples).lower()
        assert "json" in prompt, (
            "Prompt should request JSON output for structured extraction"
        )

    def test_prompt_mentions_null(self, challenge):
        examples = challenge.build_examples()
        prompt = challenge.build_extraction_prompt("Test doc", examples).lower()
        assert "null" in prompt or "none" in prompt, (
            "Prompt should mention null/None handling for missing fields"
        )

    def test_prompt_specifies_schema_fields(self, challenge):
        examples = challenge.build_examples()
        prompt = challenge.build_extraction_prompt("Test doc", examples).lower()
        required_fields = ["vendor", "items", "date", "total", "tax", "payment_method"]
        found = sum(1 for f in required_fields if f in prompt)
        assert found >= 4, (
            f"Prompt should specify most schema fields. Found {found}/6: "
            f"{[f for f in required_fields if f in prompt]}"
        )


# ---------------------------------------------------------------------------
# Test 3: Missing Field Handling
# ---------------------------------------------------------------------------

class TestMissingFieldHandling:
    """Student's handle_missing_fields must clean extraction output."""

    def test_adds_missing_fields(self, challenge):
        """Missing fields should default to null (or [] for items)."""
        result = challenge.handle_missing_fields({"vendor": "Test"})
        for field in EXTRACTION_SCHEMA:
            assert field in result, f"Missing field '{field}' not added"

    def test_items_defaults_to_empty_list(self, challenge):
        result = challenge.handle_missing_fields({})
        assert result.get("items") == [] or result.get("items") is None, (
            "Items should default to [] when missing"
        )

    def test_empty_string_becomes_null(self, challenge):
        result = challenge.handle_missing_fields({
            "vendor": "",
            "items": [],
            "date": "",
            "total": None,
            "tax": "",
            "payment_method": "",
            "notes": ""
        })
        assert result["vendor"] is None, "Empty string vendor should become null"
        assert result["date"] is None, "Empty string date should become null"
        assert result["tax"] is None, "Empty string tax should become null"

    def test_preserves_valid_values(self, challenge):
        result = challenge.handle_missing_fields({
            "vendor": "Test Corp",
            "items": [{"name": "Widget", "price": 9.99}],
            "date": "2025-01-15",
            "total": 9.99,
            "tax": 0.82,
            "payment_method": "cash",
            "notes": "Test note"
        })
        assert result["vendor"] == "Test Corp"
        assert result["total"] == 9.99
        assert result["payment_method"] == "cash"

    def test_removes_extra_fields(self, challenge):
        result = challenge.handle_missing_fields({
            "vendor": "Test",
            "items": [],
            "date": None,
            "total": 10.0,
            "tax": None,
            "payment_method": None,
            "notes": None,
            "extra_field_1": "should be removed",
            "hallucinated_data": 42
        })
        assert "extra_field_1" not in result, "Extra fields should be removed"
        assert "hallucinated_data" not in result, "Hallucinated fields should be removed"

    def test_returns_exactly_schema_keys(self, challenge):
        result = challenge.handle_missing_fields({"vendor": "X"})
        assert set(result.keys()) == set(EXTRACTION_SCHEMA.keys()), (
            f"Result should have exactly the schema keys. "
            f"Got: {set(result.keys())}, expected: {set(EXTRACTION_SCHEMA.keys())}"
        )


# ---------------------------------------------------------------------------
# Test 4: End-to-End Extraction (mocked API)
# ---------------------------------------------------------------------------

class TestExtraction:
    """End-to-end extraction test using mocked Claude responses."""

    def _mock_extract(self, challenge, doc_type):
        """Run extraction with mocked API."""
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=MOCK_RESPONSES[doc_type])]

        with patch.object(
            challenge.client.messages, "create", return_value=mock_msg
        ):
            return challenge.extract(ALL_DOCUMENTS[doc_type])

    def test_invoice_extraction(self, challenge):
        result = self._mock_extract(challenge, "invoice")
        assert result.get("vendor") is not None, "Invoice vendor should not be null"
        assert len(result.get("items", [])) == 3, "Invoice should have 3 items"
        assert result.get("total") == 19485.00, "Invoice total mismatch"

    def test_receipt_extraction(self, challenge):
        result = self._mock_extract(challenge, "receipt")
        assert result.get("vendor") is not None, "Receipt vendor should not be null"
        assert result.get("tax") is not None, "Receipt tax should not be null"

    def test_handwritten_null_handling(self, challenge):
        result = self._mock_extract(challenge, "handwritten")
        assert result.get("vendor") is None, (
            "Handwritten note has no vendor — should be null, not hallucinated"
        )
        assert result.get("tax") is None, (
            "Handwritten note has no tax — should be null"
        )

    def test_contract_null_handling(self, challenge):
        result = self._mock_extract(challenge, "contract")
        assert result.get("payment_method") is None, (
            "Contract has no specific payment method — should be null"
        )
        assert result.get("tax") is None, (
            "Contract says tax 'not included' — should be null, not 0"
        )

    def test_all_documents_have_all_fields(self, challenge):
        """Every extraction must produce exactly the schema fields."""
        schema_keys = set(EXTRACTION_SCHEMA.keys())
        for doc_type in ALL_DOCUMENTS:
            result = self._mock_extract(challenge, doc_type)
            assert set(result.keys()) == schema_keys, (
                f"{doc_type}: Expected fields {schema_keys}, got {set(result.keys())}"
            )

    def test_no_extra_fields(self, challenge):
        """No document should produce fields outside the schema."""
        schema_keys = set(EXTRACTION_SCHEMA.keys())
        for doc_type in ALL_DOCUMENTS:
            result = self._mock_extract(challenge, doc_type)
            extra = set(result.keys()) - schema_keys
            assert not extra, (
                f"{doc_type}: Extra fields found: {extra}"
            )
