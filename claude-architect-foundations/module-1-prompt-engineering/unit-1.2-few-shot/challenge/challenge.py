"""
CHALLENGE: Few-Shot Extraction Across Document Formats

Task Statement 4.2 — Apply few-shot prompting to improve output
consistency and quality.

Your goal: build extraction prompts with few-shot examples that achieve
consistent field extraction across 5 document types: invoice, receipt,
email, contract, and handwritten note.

Complete the three methods in FewShotChallenge:
  1. build_examples()            — return 3-4 few-shot examples
  2. build_extraction_prompt()   — combine examples + target document
  3. handle_missing_fields()     — clean extraction output

The checker will test your extraction against all 5 document types.
You must achieve:
  - Consistent field extraction (all required fields present)
  - Correct null handling (no hallucinated values for missing fields)
  - Correct unit conversion (informal measurements -> metric)
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# Target extraction schema — all documents must produce this structure
# ---------------------------------------------------------------------------

EXTRACTION_SCHEMA = {
    "vendor": "str or null",
    "items": "[{name: str, price: float}] or []",
    "date": "YYYY-MM-DD or null",
    "total": "float or null",
    "tax": "float or null",
    "payment_method": "str or null",
    "notes": "str or null",
}


# ---------------------------------------------------------------------------
# Test documents — 5 different formats
# ---------------------------------------------------------------------------

DOC_INVOICE = """
INVOICE #2024-0892
Acme Corp
Date: March 15, 2025

Bill To: Widget Industries

Items:
  1. Enterprise License (annual)    $12,000.00
  2. Premium Support Package         $3,600.00
  3. Custom Integration Fee          $2,400.00

Subtotal: $18,000.00
Tax (8.25%): $1,485.00
Total Due: $19,485.00

Payment Terms: Net 30
Payment Method: Wire Transfer
"""

DOC_RECEIPT = """
Joe's Hardware
123 Main St

03/22/25  2:34 PM

Hammer          $12.99
Box of Nails     $4.50
Wood Glue        $7.25
---
Subtotal        $24.74
Tax              $2.04
TOTAL           $26.78

VISA ending 4532
"""

DOC_EMAIL = """
From: sarah@vendorcorp.com
To: accounting@mycompany.com
Subject: Re: Payment for consulting work

Hi team,

Attached is the summary for our February engagement:

- Strategy workshop (Feb 3-5): $8,500
- Follow-up report: $2,000
- Travel expenses: $1,200

Total: $11,700. No tax since we're in Oregon.

Please process via ACH to the account on file.

Thanks,
Sarah
"""

DOC_CONTRACT = """
SERVICE AGREEMENT

Between: TechFlow Solutions ("Provider")
And: DataStream Inc. ("Client")

Effective Date: January 1, 2025

Services and Fees:
The Provider shall deliver the following:
(a) Monthly data pipeline maintenance — $4,500/month
(b) Quarterly performance audit — $3,000/quarter
(c) Emergency support (as needed) — $250/hour

First year estimated total: $70,000
(Based on 12 months maintenance + 4 audits + estimated 20 hours emergency)

Payment: Monthly invoices, Net 15
Tax: Subject to applicable state taxes (not included in above figures)
"""

DOC_HANDWRITTEN = """
[Handwritten note, partially legible]

Bought supplies for the Johnson project
~Mar 10

- lumber (about 40 board feet) ... $186
- paint, 3 cans ............... $67
- brushes + misc .............. ~$25

paid cash, no receipt for the misc stuff
total was around $278

need to get reimbursed!!
"""


# Ground truth for checker validation
GROUND_TRUTH = {
    "invoice": {
        "vendor": "Acme Corp",
        "items_count": 3,
        "date": "2025-03-15",
        "total": 19485.00,
        "tax": 1485.00,
        "payment_method": "Wire Transfer",
        "has_notes": False,
    },
    "receipt": {
        "vendor": "Joe's Hardware",
        "items_count": 3,
        "date": "2025-03-22",
        "total": 26.78,
        "tax": 2.04,
        "payment_method": "VISA ending 4532",
        "has_notes": False,
    },
    "email": {
        "vendor": "VendorCorp",
        "items_count": 3,
        "date": None,
        "total": 11700.00,
        "tax": 0.0,
        "payment_method": "ACH",
        "has_notes": False,
    },
    "contract": {
        "vendor": "TechFlow Solutions",
        "items_count": 3,
        "date": "2025-01-01",
        "total": 70000.00,
        "tax": None,
        "payment_method": None,
        "has_notes": True,
    },
    "handwritten": {
        "vendor": None,
        "items_count": 3,
        "date": "2025-03-10",
        "total": 278.00,
        "tax": None,
        "payment_method": "cash",
        "has_notes": True,
    },
}


ALL_DOCUMENTS = {
    "invoice": DOC_INVOICE,
    "receipt": DOC_RECEIPT,
    "email": DOC_EMAIL,
    "contract": DOC_CONTRACT,
    "handwritten": DOC_HANDWRITTEN,
}


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class FewShotChallenge:
    """
    Build a few-shot extraction system that produces consistent
    structured output across varied document formats.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_examples(self) -> list[dict]:
        """
        Create 3-4 few-shot examples for document extraction.

        Each example must be a dict with:
          - "input":     str  — the raw document text
          - "output":    dict — the extracted fields matching EXTRACTION_SCHEMA
          - "reasoning": str  — why fields were extracted this way

        Requirements:
        - Cover at least 3 different document types
        - At least one example must show null handling for missing fields
        - At least one example must show informal/approximate values
        - Include reasoning that explains extraction decisions

        Returns:
            A list of 3-4 example dicts.
        """
        # TODO: Create your few-shot examples here.
        # Hint: Do NOT use the test documents above as examples — use
        #       different documents so the model must generalize.
        # Hint: Include an edge case with missing fields.
        # Hint: Include an example with informal measurements or amounts.
        raise NotImplementedError("Complete build_examples()")

    def build_extraction_prompt(self, document: str, examples: list[dict]) -> str:
        """
        Build a complete extraction prompt combining instructions,
        few-shot examples, and the target document.

        Args:
            document: The raw document text to extract from.
            examples: The few-shot examples from build_examples().

        Returns:
            A complete prompt string ready to send to Claude.
        """
        # TODO: Combine your examples and the target document into a prompt.
        # Hint: Format examples clearly with delimiters.
        # Hint: Specify the output format (JSON matching EXTRACTION_SCHEMA).
        # Hint: Tell the model to return null for missing fields.
        raise NotImplementedError("Complete build_extraction_prompt()")

    def handle_missing_fields(self, extraction: dict) -> dict:
        """
        Clean an extraction result: ensure all required fields exist,
        set missing ones to null, remove any hallucinated extras.

        Required fields (from EXTRACTION_SCHEMA):
          vendor, items, date, total, tax, payment_method, notes

        Rules:
        - If a field is missing from extraction, set it to null
          (or [] for items)
        - If a field has an empty string, convert to null
        - Do NOT invent values — preserve only what was extracted
        - Remove any fields not in the schema

        Args:
            extraction: A dict from Claude's JSON response.

        Returns:
            A cleaned dict with exactly the schema fields.
        """
        # TODO: Implement field cleaning logic.
        # Hint: Iterate over EXTRACTION_SCHEMA keys.
        # Hint: Handle the items field specially (default to []).
        raise NotImplementedError("Complete handle_missing_fields()")

    def extract(self, document: str) -> dict:
        """
        Run the full extraction pipeline: examples -> prompt -> call -> clean.

        This method is provided for you — do not modify it.
        """
        examples = self.build_examples()
        prompt = self.build_extraction_prompt(document, examples)
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = response.content[0].text

        # Try to parse JSON from the response
        try:
            # Handle responses that wrap JSON in markdown code blocks
            text = raw_text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]  # remove first ```json line
                text = text.rsplit("```", 1)[0]  # remove trailing ```
            extraction = json.loads(text)
        except json.JSONDecodeError:
            print(f"WARNING: Could not parse response as JSON:\n{raw_text[:200]}")
            extraction = {}

        return self.handle_missing_fields(extraction)

    def evaluate(self, documents=None):
        """
        Evaluate extraction across all test documents and print results.

        This method is provided for you — do not modify it.
        """
        if documents is None:
            documents = ALL_DOCUMENTS

        all_passed = True

        for doc_type, doc_text in documents.items():
            print(f"\n{'='*60}")
            print(f"Document: {doc_type}")
            print(f"{'='*60}")

            result = self.extract(doc_text)
            truth = GROUND_TRUTH[doc_type]

            # Check required fields exist
            schema_fields = list(EXTRACTION_SCHEMA.keys())
            missing = [f for f in schema_fields if f not in result]
            if missing:
                print(f"  FAIL: Missing fields: {missing}")
                all_passed = False
            else:
                print(f"  OK: All {len(schema_fields)} fields present")

            # Check key values
            if truth["vendor"] is not None:
                if result.get("vendor") and truth["vendor"].lower() in result["vendor"].lower():
                    print(f"  OK: Vendor = {result['vendor']}")
                else:
                    print(f"  FAIL: Vendor expected '{truth['vendor']}', got '{result.get('vendor')}'")
                    all_passed = False
            else:
                if result.get("vendor") is None:
                    print(f"  OK: Vendor correctly null")
                else:
                    print(f"  FAIL: Vendor should be null, got '{result.get('vendor')}'")
                    all_passed = False

            # Check items count
            items = result.get("items", [])
            if len(items) == truth["items_count"]:
                print(f"  OK: Items count = {len(items)}")
            else:
                print(f"  WARN: Items expected {truth['items_count']}, got {len(items)}")

            # Check null handling
            if truth["tax"] is None:
                if result.get("tax") is None:
                    print(f"  OK: Tax correctly null")
                else:
                    print(f"  FAIL: Tax should be null (not mentioned), got {result.get('tax')}")
                    all_passed = False

            if truth["payment_method"] is None:
                if result.get("payment_method") is None:
                    print(f"  OK: Payment method correctly null")
                else:
                    print(f"  FAIL: Payment method should be null, got '{result.get('payment_method')}'")
                    all_passed = False

            print(f"  Result: {json.dumps(result, indent=2, default=str)[:300]}...")

        print(f"\n{'='*60}")
        if all_passed:
            print("CHALLENGE PASSED — Consistent extraction across all formats!")
        else:
            print("NEEDS WORK — Review failures above and adjust examples/prompt.")
        print(f"{'='*60}")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Few-Shot Extraction Challenge")
    print("==============================")
    print(f"Document types: {list(ALL_DOCUMENTS.keys())}")
    print(f"Required fields: {list(EXTRACTION_SCHEMA.keys())}\n")

    challenge = FewShotChallenge()
    challenge.evaluate()
