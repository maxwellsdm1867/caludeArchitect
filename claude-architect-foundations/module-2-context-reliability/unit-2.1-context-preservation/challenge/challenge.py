"""
CHALLENGE: Build a Context Preservation System

Task Statement 5.1 — Manage context windows to preserve critical information
across extended conversations.

Your goal: build a system that extracts structured case facts from a conversation
and injects them into a system prompt to prevent context degradation.

Complete the three methods in ContextPreservationChallenge:
  1. extract_case_facts(conversation) — extract structured facts from raw conversation
  2. build_system_prompt(case_facts) — build a system prompt with structured facts block
  3. verify_preservation(summary, case_facts) — check if summary contains all critical details

The checker will test your system against conversations with specific numbers,
dates, and identifiers that must be preserved exactly.
"""

import json
import anthropic

# ---------------------------------------------------------------------------
# Test conversations with known critical details
# ---------------------------------------------------------------------------

CONVERSATION_1 = {
    "turns": [
        "Hi, I'm calling about order ORD-2024-55123. I was charged $2,847.93 on November 3rd.",
        "The order had three items: a laptop for $1,899.99, a monitor for $649.99, and a cable for $297.95.",
        "The monitor arrived with a cracked screen. I need a replacement or refund.",
        "I paid with my Amex ending in 3847. My customer ID is CUST-88210.",
        "I've been a Platinum member since 2019. Can you expedite this?",
        "The damaged monitor model is UltraWide-34X, serial number MON-2024-7712."
    ],
    "critical_facts": {
        "order_number": "ORD-2024-55123",
        "total_charged": "$2,847.93",
        "order_date": "November 3rd",
        "items": [
            {"name": "laptop", "price": "$1,899.99"},
            {"name": "monitor", "price": "$649.99"},
            {"name": "cable", "price": "$297.95"}
        ],
        "damaged_item": "UltraWide-34X",
        "serial_number": "MON-2024-7712",
        "payment_method": "Amex ending in 3847",
        "customer_id": "CUST-88210",
        "loyalty_tier": "Platinum"
    }
}

CONVERSATION_2 = {
    "turns": [
        "I need help with invoice INV-2024-90012 for $15,750.00 dated December 1, 2024.",
        "We're disputing the consulting fees line item: 45 hours at $350/hour = $15,750.",
        "Our contract ref is CTR-2024-4401 which specifies a cap of 30 hours per month.",
        "The overage is 15 hours x $350 = $5,250 that should not have been billed.",
        "Please credit account ACC-77201 for the $5,250 overage.",
        "Our accounts payable contact is Maria Rodriguez, ext 4412."
    ],
    "critical_facts": {
        "invoice_number": "INV-2024-90012",
        "invoice_total": "$15,750.00",
        "invoice_date": "December 1, 2024",
        "hours_billed": 45,
        "hourly_rate": "$350",
        "contract_ref": "CTR-2024-4401",
        "hour_cap": 30,
        "overage_hours": 15,
        "overage_amount": "$5,250",
        "account_number": "ACC-77201",
        "ap_contact": "Maria Rodriguez",
        "ap_extension": "4412"
    }
}

CONVERSATION_3 = {
    "turns": [
        "Ticket TKT-2024-11234 — three servers down in rack R-14, Bay 3.",
        "Affected servers: SRV-A01 (10.0.14.101), SRV-A02 (10.0.14.102), SRV-A03 (10.0.14.103).",
        "The outage started at 03:42 UTC on December 5. SLA deadline is 4 hours: 07:42 UTC.",
        "Root cause appears to be a failed PDU, model PowerMax-3000, serial PDU-2024-8891.",
        "Impact: 340 users on VLAN 14 lost access to the CRM application.",
        "Spare PDU is in warehouse W-2, shelf S-14. ETA for replacement: 90 minutes."
    ],
    "critical_facts": {
        "ticket_id": "TKT-2024-11234",
        "location": "rack R-14, Bay 3",
        "servers": ["SRV-A01", "SRV-A02", "SRV-A03"],
        "ip_addresses": ["10.0.14.101", "10.0.14.102", "10.0.14.103"],
        "outage_start": "03:42 UTC",
        "outage_date": "December 5",
        "sla_deadline": "07:42 UTC",
        "root_cause_device": "PowerMax-3000",
        "pdu_serial": "PDU-2024-8891",
        "affected_users": 340,
        "vlan": "VLAN 14",
        "spare_location": "warehouse W-2, shelf S-14",
        "repair_eta": "90 minutes"
    }
}

ALL_CONVERSATIONS = [
    (CONVERSATION_1, "billing_dispute"),
    (CONVERSATION_2, "invoice_dispute"),
    (CONVERSATION_3, "infrastructure_outage"),
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class ContextPreservationChallenge:
    """
    Build a context preservation system that extracts structured facts
    from conversations and injects them into system prompts.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def extract_case_facts(self, conversation: dict) -> dict:
        """
        Extract structured case facts from a conversation.

        Given a conversation dict with "turns" (list of strings) and
        "critical_facts" (dict of expected facts), return a structured
        dict containing the critical information.

        For the challenge, you can use the critical_facts directly —
        in production, you would use Claude to extract these from the raw turns.

        Args:
            conversation: dict with "turns" and "critical_facts" keys.

        Returns:
            A dict of structured facts suitable for injection into a system prompt.
        """
        # TODO: Extract structured facts from the conversation.
        # Hint: For this challenge, the critical_facts are provided.
        # In production, you'd use Claude to extract them from turns.
        # Return a clean dict that can be JSON-serialized into a system prompt.
        raise NotImplementedError("Complete extract_case_facts()")

    def build_system_prompt(self, case_facts: dict, case_type: str = "general") -> str:
        """
        Build a system prompt with a structured case facts block.

        The system prompt must:
        - Include the case facts as a clearly delimited JSON block
        - Instruct the model to reference exact values from the facts block
        - Tell the model NOT to paraphrase numbers, dates, or identifiers

        Args:
            case_facts: dict of structured facts (output of extract_case_facts).
            case_type: string describing the type of case.

        Returns:
            A complete system prompt string with embedded case facts.
        """
        # TODO: Build a system prompt with structured case facts.
        # Hint: Use a delimited block (=== CASE FACTS === ... === END ===)
        # Hint: Include explicit instructions about using exact values.
        # Hint: Place the facts block near the top of the system prompt.
        raise NotImplementedError("Complete build_system_prompt()")

    def verify_preservation(self, summary: str, case_facts: dict) -> dict:
        """
        Verify that a summary contains all critical details from case facts.

        Check each critical fact against the summary text. Return a dict
        with the verification results.

        Args:
            summary: The text to verify (e.g., a resolution email).
            case_facts: The original case facts dict.

        Returns:
            A dict with:
              - "total": int (number of facts checked)
              - "found": int (number of facts found in summary)
              - "missing": list of str (fact keys not found)
              - "preservation_rate": float (found / total)
        """
        # TODO: Check each critical fact against the summary.
        # Hint: Flatten nested facts (lists, dicts) into checkable strings.
        # Hint: For numeric values, check the string representation.
        # Hint: Some facts may need flexible matching (e.g., "Amex" vs "American Express").
        raise NotImplementedError("Complete verify_preservation()")

    def run_preservation_test(self, conversation: dict, case_type: str) -> dict:
        """
        Run the full preservation pipeline and return verification results.

        This method is provided — do not modify it.
        """
        facts = self.extract_case_facts(conversation)
        system_prompt = self.build_system_prompt(facts, case_type)

        # Simulate a long conversation ending with a summary request
        messages = []
        for turn in conversation["turns"]:
            messages.append({"role": "user", "content": turn})
            messages.append({"role": "assistant", "content": "Noted, I have that information."})

        messages.append({"role": "user", "content":
            "Please write a detailed resolution summary with ALL specific details: "
            "all numbers, dates, IDs, amounts, and names. Be precise — use exact values."})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system_prompt,
            messages=messages,
        )

        summary = response.content[0].text
        verification = self.verify_preservation(summary, facts)
        verification["summary"] = summary
        return verification

    def evaluate(self, conversations=None):
        """
        Evaluate preservation across all test conversations.

        This method is provided — do not modify it.
        """
        if conversations is None:
            conversations = ALL_CONVERSATIONS

        total_facts = 0
        total_found = 0

        for i, (conv, case_type) in enumerate(conversations, 1):
            print(f"\n{'='*60}")
            print(f"Conversation {i}: {case_type}")
            print(f"{'='*60}")

            result = self.run_preservation_test(conv, case_type)
            total_facts += result["total"]
            total_found += result["found"]

            print(f"  Facts checked: {result['total']}")
            print(f"  Facts found:   {result['found']}")
            print(f"  Preservation:  {result['preservation_rate']:.0%}")
            if result["missing"]:
                print(f"  Missing: {result['missing']}")

        print(f"\n{'='*60}")
        print("OVERALL RESULTS")
        print(f"{'='*60}")
        overall_rate = total_found / total_facts if total_facts > 0 else 0
        print(f"  Total facts: {total_facts}")
        print(f"  Found: {total_found}")
        print(f"  Preservation rate: {overall_rate:.0%}")

        if overall_rate >= 0.90:
            print("\n  CHALLENGE PASSED — 90%+ preservation rate!")
        else:
            print(f"\n  NEEDS WORK — preservation rate below 90%.")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Context Preservation Challenge")
    print("================================")
    print("Goal: 90%+ critical detail preservation rate\n")

    challenge = ContextPreservationChallenge()
    challenge.evaluate()
