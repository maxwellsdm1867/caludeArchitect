"""
CHALLENGE: Build an Explicit Escalation Trigger System

Task Statement 5.2 — Design escalation triggers and ambiguity resolution
strategies for AI agents.

Your goal: build a system that decides whether to escalate a customer interaction
to a human agent based on explicit trigger conditions — NOT sentiment analysis.

Complete the three methods in EscalationChallenge:
  1. build_escalation_prompt(message, context) — return a prompt with explicit triggers
  2. parse_decision(response_text) — parse Claude's escalation decision
  3. classify_decision(decision, expected) — check if the decision matches expected

The checker will test your triggers against scenarios where sentiment and escalation
need are intentionally misaligned.
"""

import json
import anthropic

# ---------------------------------------------------------------------------
# Test scenarios with known correct escalation decisions
# ---------------------------------------------------------------------------

SCENARIO_1 = {
    "id": "S1",
    "message": "THIS IS UNACCEPTABLE!!! I ordered a phone case 2 days ago and it hasn't shipped yet!!! WORST SERVICE EVER!!!",
    "context": {
        "issue_type": "shipping_delay",
        "order_placed_days_ago": 2,
        "expected_ship_days": 3,
        "shipping_status": "processing",
        "can_provide_tracking": True
    },
    "expected_action": "handle",
    "expected_reason": "Extremely angry but order is within expected processing time — agent can explain timeline"
}

SCENARIO_2 = {
    "id": "S2",
    "message": "Hi, I noticed my account was charged $4,200 for something called 'Enterprise Upgrade' but I never authorized this. Could you help me understand what happened?",
    "context": {
        "issue_type": "unauthorized_charge",
        "charge_amount": 4200,
        "agent_refund_limit": 500,
        "charge_in_system": True,
        "authorization_record": None
    },
    "expected_action": "escalate",
    "expected_reason": "Calm and polite but charge exceeds agent refund authority ($4,200 > $500 limit)"
}

SCENARIO_3 = {
    "id": "S3",
    "message": "Can you connect me with a human agent? I prefer to discuss this in person.",
    "context": {
        "issue_type": "general_inquiry",
        "explicit_human_request": True,
        "issue_complexity": "low"
    },
    "expected_action": "escalate",
    "expected_reason": "Explicit request for human — escalate immediately regardless of issue complexity"
}

SCENARIO_4 = {
    "id": "S4",
    "message": "I'm really upset. My subscription renewed and I wanted to cancel it. The charge was $14.99.",
    "context": {
        "issue_type": "subscription_cancellation",
        "charge_amount": 14.99,
        "agent_refund_limit": 500,
        "cancellation_policy": True,
        "can_process_refund": True
    },
    "expected_action": "handle",
    "expected_reason": "Upset but within agent capability — can cancel and refund $14.99 per policy"
}

SCENARIO_5 = {
    "id": "S5",
    "message": "Hello! I love your service. Quick question — can I get a custom enterprise plan for my team of 500 people? We need special compliance features.",
    "context": {
        "issue_type": "enterprise_plan_request",
        "team_size": 500,
        "standard_plans": ["basic", "pro", "business"],
        "custom_plan_policy": False,
        "requires_sales_team": True
    },
    "expected_action": "escalate",
    "expected_reason": "Happy customer but request requires sales team — no policy for custom enterprise plans"
}

SCENARIO_6 = {
    "id": "S6",
    "message": "I'm furious! You charged me twice for the same order! I want my $89.99 back RIGHT NOW!",
    "context": {
        "issue_type": "double_charge",
        "charge_amount": 89.99,
        "agent_refund_limit": 500,
        "duplicate_confirmed": True,
        "refund_policy": True
    },
    "expected_action": "handle",
    "expected_reason": "Very angry but duplicate charge confirmed and within refund authority — agent can resolve"
}

SCENARIO_7 = {
    "id": "S7",
    "message": "I've tried three different things to fix my connection: restarting the router, resetting to factory settings, and replacing the ethernet cable. Nothing works.",
    "context": {
        "issue_type": "technical_support",
        "resolution_attempts": 3,
        "max_attempts_before_escalation": 3,
        "customer_sentiment": "neutral",
        "issue_resolved": False
    },
    "expected_action": "escalate",
    "expected_reason": "Three failed resolution attempts — triggers 'no progress after N attempts' condition"
}

ALL_SCENARIOS = [
    SCENARIO_1, SCENARIO_2, SCENARIO_3, SCENARIO_4,
    SCENARIO_5, SCENARIO_6, SCENARIO_7,
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class EscalationChallenge:
    """
    Build an escalation trigger system that uses explicit conditions
    instead of sentiment analysis.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_escalation_prompt(self, message: str, context: dict) -> str:
        """
        Build a prompt with explicit escalation trigger conditions.

        The prompt must:
        - Define concrete escalation triggers (NOT based on sentiment)
        - Include the customer message and context
        - Handle: explicit human requests, policy gaps, authority limits, failed attempts
        - NOT escalate based on angry tone alone

        Args:
            message: The customer's message text.
            context: Dict with issue_type, policy info, limits, etc.

        Returns:
            A complete prompt string ready to send to Claude.
        """
        # TODO: Write a prompt with explicit escalation triggers.
        # Hint: Define triggers for human requests, policy gaps, authority limits.
        # Hint: Explicitly tell the model NOT to use sentiment as an escalation signal.
        # Hint: Include the context so the model can check against limits.
        raise NotImplementedError("Complete build_escalation_prompt()")

    def parse_decision(self, response_text: str) -> dict:
        """
        Parse Claude's response into an escalation decision.

        Each decision must be a dict with:
          - "action": str ("escalate" or "handle")
          - "trigger": str (which trigger condition matched, or "within_capability")
          - "reasoning": str (brief explanation)

        Args:
            response_text: The raw text response from Claude.

        Returns:
            A dict with action, trigger, and reasoning.
        """
        # TODO: Parse the response into a structured decision.
        # Hint: If your prompt requests JSON output, use json.loads().
        # Hint: Handle edge cases (malformed JSON, unexpected format).
        raise NotImplementedError("Complete parse_decision()")

    def classify_decision(self, decision: dict, scenario: dict) -> str:
        """
        Classify a decision as "correct" or "incorrect".

        Compare the decision's action against the scenario's expected_action.

        Args:
            decision: A dict with at least an "action" key.
            scenario: A dict with an "expected_action" key.

        Returns:
            "correct" or "incorrect"
        """
        # TODO: Compare decision["action"] to scenario["expected_action"].
        raise NotImplementedError("Complete classify_decision()")

    def run_escalation(self, scenario: dict) -> dict:
        """
        Run the escalation pipeline for a single scenario.

        This method is provided — do not modify it.
        """
        prompt = self.build_escalation_prompt(scenario["message"], scenario["context"])
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return self.parse_decision(response.content[0].text)

    def evaluate(self, scenarios=None):
        """
        Evaluate escalation decisions across all scenarios.

        This method is provided — do not modify it.
        """
        if scenarios is None:
            scenarios = ALL_SCENARIOS

        correct = 0
        total = len(scenarios)

        for scenario in scenarios:
            print(f"\n{'='*60}")
            print(f"Scenario {scenario['id']}")
            print(f"{'='*60}")

            decision = self.run_escalation(scenario)
            classification = self.classify_decision(decision, scenario)

            print(f"  Message: {scenario['message'][:60]}...")
            print(f"  Decision: {decision.get('action', '?')}")
            print(f"  Expected: {scenario['expected_action']}")
            print(f"  Result: {classification.upper()}")
            print(f"  Trigger: {decision.get('trigger', 'N/A')}")

            if classification == "correct":
                correct += 1

        print(f"\n{'='*60}")
        print("OVERALL RESULTS")
        print(f"{'='*60}")
        accuracy = correct / total
        print(f"  Accuracy: {accuracy:.0%} ({correct}/{total})")

        if accuracy == 1.0:
            print("\n  CHALLENGE PASSED — 100% escalation accuracy!")
        else:
            print(f"\n  NEEDS WORK — {total - correct} incorrect decision(s).")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Escalation Trigger Challenge")
    print("================================")
    print("Goal: 100% correct escalation decisions\n")

    challenge = EscalationChallenge()
    challenge.evaluate()
