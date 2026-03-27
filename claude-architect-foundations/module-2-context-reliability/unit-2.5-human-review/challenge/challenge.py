"""
CHALLENGE: Build a Field-Level Review Routing System

Task Statement 5.5 — Design human review workflows with calibrated confidence signals.

Your goal: build a system that analyzes per-field confidence scores and routes
documents to human review or auto-approval based on field-level thresholds.

Complete the three methods in HumanReviewChallenge:
  1. build_routing_prompt(extraction) — prompt that routes based on field confidence
  2. parse_routing_decision(response_text) — parse the routing decision
  3. evaluate_accuracy(results, ground_truth) — compute per-field accuracy breakdown

The checker will test your routing against extractions with varying confidence
patterns to verify field-level (not aggregate) routing.
"""

import json
import anthropic

# ---------------------------------------------------------------------------
# Test extractions with per-field confidence
# ---------------------------------------------------------------------------

EXTRACTION_1 = {
    "doc_id": "DOC-001",
    "doc_type": "typed_invoice",
    "fields": {
        "vendor_name": {"value": "Acme Corp", "confidence": 0.97},
        "invoice_date": {"value": "2024-11-15", "confidence": 0.94},
        "line_items": {"value": "3 items totaling $1,234.56", "confidence": 0.91},
        "total_amount": {"value": "$1,234.56", "confidence": 0.93},
        "tax_amount": {"value": "$98.76", "confidence": 0.89}
    },
    "expected_routing": "auto_approve",
    "expected_review_fields": []
}

EXTRACTION_2 = {
    "doc_id": "DOC-002",
    "doc_type": "scanned_receipt",
    "fields": {
        "vendor_name": {"value": "Quick Mart", "confidence": 0.80},
        "receipt_date": {"value": "2024-11-10", "confidence": 0.52},
        "line_items": {"value": "misc items", "confidence": 0.38},
        "total_amount": {"value": "$45.80", "confidence": 0.41},
        "tax_amount": {"value": "$3.66", "confidence": 0.29}
    },
    "expected_routing": "human_review",
    "expected_review_fields": ["receipt_date", "line_items", "total_amount", "tax_amount"]
}

EXTRACTION_3 = {
    "doc_id": "DOC-003",
    "doc_type": "typed_invoice",
    "fields": {
        "vendor_name": {"value": "TechSupplies Inc", "confidence": 0.96},
        "invoice_date": {"value": "2024-10-28", "confidence": 0.92},
        "line_items": {"value": "Enterprise License x1", "confidence": 0.88},
        "total_amount": {"value": "$8,750.00", "confidence": 0.33},
        "tax_amount": {"value": "$700.00", "confidence": 0.90}
    },
    "expected_routing": "human_review",
    "expected_review_fields": ["total_amount"]
}

EXTRACTION_4 = {
    "doc_id": "DOC-004",
    "doc_type": "handwritten_note",
    "fields": {
        "author_name": {"value": "J. Smith", "confidence": 0.42},
        "date": {"value": "Nov 2024", "confidence": 0.28},
        "amounts": {"value": "$500", "confidence": 0.22},
        "description": {"value": "Office supplies", "confidence": 0.55},
        "reference_number": {"value": "REF-2024-123", "confidence": 0.18}
    },
    "expected_routing": "human_review",
    "expected_review_fields": ["author_name", "date", "amounts", "description", "reference_number"]
}

EXTRACTION_5 = {
    "doc_id": "DOC-005",
    "doc_type": "typed_invoice",
    "fields": {
        "vendor_name": {"value": "CloudServices LLC", "confidence": 0.99},
        "invoice_date": {"value": "2024-12-01", "confidence": 0.98},
        "line_items": {"value": "Monthly subscription", "confidence": 0.97},
        "total_amount": {"value": "$299.99", "confidence": 0.96},
        "tax_amount": {"value": "$24.00", "confidence": 0.95}
    },
    "expected_routing": "auto_approve",
    "expected_review_fields": []
}

ALL_EXTRACTIONS = [
    EXTRACTION_1, EXTRACTION_2, EXTRACTION_3, EXTRACTION_4, EXTRACTION_5
]

# Per-field accuracy data for evaluate_accuracy
ACCURACY_DATA = {
    "typed_invoices": {
        "vendor_name": {"correct": 990, "total": 1000},
        "invoice_date": {"correct": 970, "total": 1000},
        "line_items": {"correct": 940, "total": 1000},
        "total_amount": {"correct": 950, "total": 1000},
        "tax_amount": {"correct": 930, "total": 1000}
    },
    "scanned_receipts": {
        "vendor_name": {"correct": 176, "total": 200},
        "receipt_date": {"correct": 144, "total": 200},
        "line_items": {"correct": 110, "total": 200},
        "total_amount": {"correct": 142, "total": 200},
        "tax_amount": {"correct": 104, "total": 200}
    },
    "handwritten_notes": {
        "author_name": {"correct": 32, "total": 50},
        "date": {"correct": 22, "total": 50},
        "amounts": {"correct": 19, "total": 50},
        "description": {"correct": 35, "total": 50},
        "reference_number": {"correct": 16, "total": 50}
    }
}


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class HumanReviewChallenge:
    """
    Build a field-level review routing system that uses per-field confidence
    to make routing decisions.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_routing_prompt(self, extraction: dict) -> str:
        """
        Build a prompt that routes extractions based on field-level confidence.

        The prompt must:
        - Check each field's confidence score against a threshold (70%)
        - If ANY field is below threshold, route to human review
        - Specify WHICH fields need review (not the entire document)
        - If all fields are above threshold, auto-approve

        Args:
            extraction: Dict with doc_id, doc_type, and fields with confidence.

        Returns:
            A complete prompt string ready to send to Claude.
        """
        # TODO: Write a routing prompt that uses field-level confidence.
        # Hint: Define a clear threshold (70%) for field-level confidence.
        # Hint: Route to human_review if ANY field is below threshold.
        # Hint: List the specific fields that need review.
        raise NotImplementedError("Complete build_routing_prompt()")

    def parse_routing_decision(self, response_text: str) -> dict:
        """
        Parse the routing decision from Claude's response.

        Each decision must be a dict with:
          - "routing": str ("auto_approve" or "human_review")
          - "review_fields": list of str (field names needing review)
          - "reasoning": str (brief explanation)

        Args:
            response_text: The raw text response from Claude.

        Returns:
            A dict with routing decision.
        """
        # TODO: Parse the response into a structured routing decision.
        # Hint: Use json.loads() if you requested JSON output.
        # Hint: Handle edge cases gracefully.
        raise NotImplementedError("Complete parse_routing_decision()")

    def evaluate_accuracy(self, accuracy_data: dict) -> dict:
        """
        Compute per-field accuracy breakdown from raw counts.

        Return both aggregate and per-field accuracy, plus identify
        failing fields (below 80% accuracy).

        Args:
            accuracy_data: Nested dict of {doc_type: {field: {correct, total}}}.

        Returns:
            A dict with:
              - "aggregate_accuracy": float
              - "per_doc_type": {doc_type: {field: accuracy_float}}
              - "failing_fields": [{doc_type, field, accuracy}]
        """
        # TODO: Compute per-field accuracy and identify failing fields.
        # Hint: A "failing" field has accuracy below 0.80.
        # Hint: Aggregate accuracy is total_correct / total_across_all.
        raise NotImplementedError("Complete evaluate_accuracy()")

    def run_routing(self, extraction: dict) -> dict:
        """
        Run the routing pipeline for a single extraction.

        This method is provided — do not modify it.
        """
        prompt = self.build_routing_prompt(extraction)
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return self.parse_routing_decision(response.content[0].text)

    def evaluate(self, extractions=None):
        """
        Evaluate routing decisions across all test extractions.

        This method is provided — do not modify it.
        """
        if extractions is None:
            extractions = ALL_EXTRACTIONS

        correct_routes = 0
        total = len(extractions)

        for ext in extractions:
            print(f"\n{'='*60}")
            print(f"Document: {ext['doc_id']} ({ext['doc_type']})")
            print(f"{'='*60}")

            decision = self.run_routing(ext)
            route_match = decision.get("routing") == ext["expected_routing"]

            print(f"  Routing: {decision.get('routing', '?')} (expected {ext['expected_routing']}) — {'OK' if route_match else 'WRONG'}")
            if decision.get("review_fields"):
                print(f"  Review fields: {decision['review_fields']}")

            if route_match:
                correct_routes += 1

        # Also show accuracy breakdown
        print(f"\n{'='*60}")
        print("ACCURACY BREAKDOWN")
        print(f"{'='*60}")
        breakdown = self.evaluate_accuracy(ACCURACY_DATA)
        print(f"  Aggregate: {breakdown['aggregate_accuracy']:.1%}")
        print(f"  Failing fields ({len(breakdown['failing_fields'])}):")
        for f in breakdown["failing_fields"]:
            print(f"    {f['doc_type']}/{f['field']}: {f['accuracy']:.0%}")

        print(f"\n{'='*60}")
        print("ROUTING RESULTS")
        print(f"{'='*60}")
        accuracy = correct_routes / total
        print(f"  Routing accuracy: {accuracy:.0%} ({correct_routes}/{total})")

        if accuracy == 1.0:
            print("\n  CHALLENGE PASSED — all documents correctly routed!")
        else:
            print(f"\n  NEEDS WORK — {total - correct_routes} incorrect routing(s).")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Human Review Routing Challenge")
    print("================================")
    print("Goal: 100% correct routing decisions\n")

    challenge = HumanReviewChallenge()
    challenge.evaluate()
