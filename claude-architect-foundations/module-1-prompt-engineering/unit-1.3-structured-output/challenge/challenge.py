"""
Unit 1.3 Challenge: Build a Schema That Prevents Hallucination

You are given invoice documents from different vendors. Some include warranty
info, some don't. Some have shipping details, some don't.

Your task: Design extraction tool schemas that prevent hallucination by using
nullable fields, enum + "other" patterns, and "unclear" escape valves.

Run the checker to validate your solution:
    pytest checker.py -v
"""

import json
from typing import Any

import anthropic

# ---------------------------------------------------------------------------
# Test documents — use these to validate your extraction
# ---------------------------------------------------------------------------

INVOICE_FULL = """
INVOICE #2024-0892
Vendor: TechParts International
Date: 2024-03-15

Bill To: Acme Corp, 123 Main St, Springfield, IL 62701
Ship To: Acme Corp Warehouse, 456 Industrial Pkwy, Springfield, IL 62704

Items:
  1. Widget Pro X200 — Qty: 10 — Unit: $45.00 — Total: $450.00
  2. Connector Kit C-50 — Qty: 5 — Unit: $22.00 — Total: $110.00
  3. Mounting Bracket MB-L — Qty: 20 — Unit: $8.50 — Total: $170.00

Subtotal: $730.00
Tax (8%): $58.40
Shipping: $25.00
Total: $813.40

Payment Status: Paid (Wire transfer, 2024-03-18)
Warranty: All items covered under 2-year manufacturer warranty.
Warranty Expiry: 2026-03-15
"""

INVOICE_NO_WARRANTY = """
INVOICE #2024-1045
Vendor: QuickSupply Co
Date: 2024-06-01

Bill To: Acme Corp, 123 Main St, Springfield, IL 62701

Items:
  1. Paper Ream (A4, 500 sheets) — Qty: 50 — Unit: $4.99 — Total: $249.50
  2. Ink Cartridge BK-200 — Qty: 10 — Unit: $18.00 — Total: $180.00

Subtotal: $429.50
Tax (8%): $34.36
Total: $463.86

Payment Status: Paid (Credit card ending 4521, 2024-06-01)
"""

INVOICE_AMBIGUOUS_PAYMENT = """
MEMO / INVOICE #PRE-2024-003
Vendor: Consolidated Services LLC
Date: 2024-08-22

To: Acme Corp

Service: Annual maintenance contract renewal
Amount: $12,000.00

Note: Invoice pending final approval from procurement. Deposit of $4,000
was received on 2024-08-10. Remaining balance to be settled upon contract
signing. Status under review.
"""


class StructuredOutputChallenge:
    """Implement the three methods below to pass the checker."""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    # ------------------------------------------------------------------
    # 1. Define the extraction tool
    # ------------------------------------------------------------------
    def define_extraction_tool(self) -> dict:
        """
        Return a tool definition dict for the Anthropic messages API.

        Requirements:
          - name: "extract_invoice"
          - input_schema with:
            * invoice_number (string, required)
            * vendor_name (string, required)
            * purchase_date (string, required)
            * document_type (enum with "other" option, required)
            * document_type_detail (string or null, required key)
            * line_items (array of objects, required)
            * subtotal (number or null, required key)
            * tax (number or null, required key)
            * shipping (number or null, required key)
            * total (number, required)
            * payment_status (enum with "unclear" option, required)
            * warranty_info (string or null, required key)
            * warranty_expiry (string or null, required key)
            * billing_address (string or null, required key)
            * shipping_address (string or null, required key)

        Fields that may be absent from a document MUST have nullable types.
        Enums MUST include escape valves ("other" / "unclear").

        Returns:
            dict matching the Anthropic tool definition format:
            {
                "name": "extract_invoice",
                "description": "...",
                "input_schema": { ... }
            }
        """
        # TODO: Build the complete tool definition.
        # Hint: Use "type": ["string", "null"] for nullable fields.
        # Hint: Use "enum" with an "other" or "unclear" value for extensible categories.
        raise NotImplementedError("Implement define_extraction_tool()")

    # ------------------------------------------------------------------
    # 2. Choose the correct tool_choice for a scenario
    # ------------------------------------------------------------------
    def choose_tool_choice(self, scenario: str) -> dict:
        """
        Given a scenario description, return the correct tool_choice setting
        for the Anthropic messages API.

        Scenarios to handle:
          - "single_schema": You have one extraction schema and need it called every time.
          - "multiple_schemas": You have several schemas for different document types;
             the model should pick the right one.
          - "model_decides": The model should decide whether extraction applies at all.

        Returns:
            dict matching the Anthropic tool_choice format, e.g.:
            {"type": "auto"} or {"type": "any"} or {"type": "tool", "name": "..."}
        """
        # TODO: Return the correct tool_choice for each scenario.
        # Hint: "single_schema" → forced tool call with a specific name
        # Hint: "multiple_schemas" → model must call *a* tool, picks which
        # Hint: "model_decides" → model can choose text or tool
        raise NotImplementedError("Implement choose_tool_choice()")

    # ------------------------------------------------------------------
    # 3. Extract structured data using tool_use
    # ------------------------------------------------------------------
    def extract_with_tool(self, document: str, tool_definition: dict) -> dict:
        """
        Use the Anthropic API with tool_use to extract structured data.

        Steps:
          1. Call client.messages.create() with:
             - model: self.model
             - max_tokens: 4096
             - tools: [tool_definition]
             - tool_choice: forced to the tool's name
             - messages: user message containing the document
          2. Find the tool_use content block in the response
          3. Return the input dict from that block

        Args:
            document: The raw text of the invoice/document.
            tool_definition: The tool definition dict (from define_extraction_tool).

        Returns:
            dict of the extracted structured data (the tool's input).
        """
        # TODO: Call the API with tool_use and return the extracted data.
        # Hint: response.content is a list; find the block where block.type == "tool_use"
        # Hint: The extracted data is in block.input
        raise NotImplementedError("Implement extract_with_tool()")


# ---------------------------------------------------------------------------
# Manual testing
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    challenge = StructuredOutputChallenge()

    # Step 1: Define the tool
    tool = challenge.define_extraction_tool()
    print("Tool definition:")
    print(json.dumps(tool, indent=2))
    print()

    # Step 2: Test tool_choice scenarios
    for scenario in ["single_schema", "multiple_schemas", "model_decides"]:
        choice = challenge.choose_tool_choice(scenario)
        print(f"tool_choice for '{scenario}': {choice}")
    print()

    # Step 3: Extract from each test document
    for name, doc in [
        ("Full invoice", INVOICE_FULL),
        ("No warranty", INVOICE_NO_WARRANTY),
        ("Ambiguous payment", INVOICE_AMBIGUOUS_PAYMENT),
    ]:
        print(f"\n--- {name} ---")
        result = challenge.extract_with_tool(doc, tool)
        print(json.dumps(result, indent=2))
