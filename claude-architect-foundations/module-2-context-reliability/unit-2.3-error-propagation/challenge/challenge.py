"""
CHALLENGE: Build Structured Error Propagation for Multi-Agent Systems

Task Statement 5.3 — Design error handling that preserves context and enables
intelligent recovery in multi-agent pipelines.

Your goal: build a coordinator that correctly interprets structured error responses
from subagents and makes appropriate recovery decisions.

Complete the three methods in ErrorPropagationChallenge:
  1. build_coordinator_prompt(pipeline_results) — prompt that handles errors correctly
  2. parse_coordinator_response(response_text) — parse the coordinator's decision
  3. classify_error(error_result) — classify an error as access_failure or empty_result

The checker will test your system against pipelines with different failure modes
to verify you distinguish access failures from empty results.
"""

import json
import anthropic

# ---------------------------------------------------------------------------
# Test pipeline results with different error types
# ---------------------------------------------------------------------------

PIPELINE_1 = {
    "name": "research_pipeline",
    "description": "Multi-source research query about a company",
    "results": [
        {
            "agent": "database_agent",
            "status": "error",
            "error_type": "connection_timeout",
            "attempted_query": "SELECT * FROM companies WHERE name = 'Acme Corp'",
            "partial_results": None,
            "alternatives": ["retry_with_backoff", "use_cached_data"]
        },
        {
            "agent": "web_search_agent",
            "status": "success",
            "data": [
                {"title": "Acme Corp Q4 Earnings", "snippet": "Revenue: $4.2B"}
            ]
        },
        {
            "agent": "file_reader_agent",
            "status": "error",
            "error_type": "permission_denied",
            "attempted_query": "read /data/reports/acme_internal.pdf",
            "partial_results": None,
            "alternatives": ["request_access", "use_public_filing"]
        }
    ],
    "expected_decision": {
        "can_proceed": True,
        "proceed_with_partial": True,
        "failed_agents": ["database_agent", "file_reader_agent"],
        "successful_agents": ["web_search_agent"],
        "should_flag_incomplete": True
    }
}

PIPELINE_2 = {
    "name": "order_pipeline",
    "description": "Order processing: inventory -> payment -> shipping",
    "results": [
        {
            "agent": "inventory_agent",
            "status": "success",
            "data": {"sku": "WIDGET-X", "in_stock": True, "quantity": 42}
        },
        {
            "agent": "payment_agent",
            "status": "error",
            "error_type": "service_unavailable",
            "attempted_query": "charge $149.99 to card ending 4821",
            "partial_results": None,
            "alternatives": ["retry_after_30s", "use_backup_gateway"]
        },
        {
            "agent": "shipping_agent",
            "status": "skipped",
            "reason": "payment_not_completed"
        }
    ],
    "expected_decision": {
        "can_proceed": False,
        "proceed_with_partial": False,
        "failed_agents": ["payment_agent"],
        "successful_agents": ["inventory_agent"],
        "should_flag_incomplete": True
    }
}

PIPELINE_3 = {
    "name": "data_enrichment_pipeline",
    "description": "Customer data enrichment from 3 sources",
    "results": [
        {
            "agent": "crm_agent",
            "status": "success",
            "data": {"name": "John Doe", "email": "john@example.com", "tier": "Gold"}
        },
        {
            "agent": "analytics_agent",
            "status": "success",
            "data": {"ltv": 12500, "churn_risk": "low", "last_purchase": "2024-11-28"}
        },
        {
            "agent": "social_agent",
            "status": "error",
            "error_type": "empty_result",
            "attempted_query": "find social profiles for john@example.com",
            "partial_results": None,
            "alternatives": ["search_by_name", "skip_social_enrichment"]
        }
    ],
    "expected_decision": {
        "can_proceed": True,
        "proceed_with_partial": True,
        "failed_agents": ["social_agent"],
        "successful_agents": ["crm_agent", "analytics_agent"],
        "should_flag_incomplete": True
    }
}

ALL_PIPELINES = [PIPELINE_1, PIPELINE_2, PIPELINE_3]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class ErrorPropagationChallenge:
    """
    Build a coordinator that correctly handles structured error responses
    from subagents in a multi-agent pipeline.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_coordinator_prompt(self, pipeline_results: list) -> str:
        """
        Build a coordinator prompt that handles pipeline errors correctly.

        The prompt must:
        - Instruct the coordinator to check each agent's status
        - Distinguish access failures from empty results
        - Determine if the pipeline can proceed (with partial or not at all)
        - Report which agents failed and what recovery is possible
        - NOT silently ignore errors

        Args:
            pipeline_results: List of dicts with agent results (success or error).

        Returns:
            A complete prompt string ready to send to Claude.
        """
        # TODO: Write a coordinator prompt that handles errors correctly.
        # Hint: Instruct the coordinator to check status fields.
        # Hint: Define what "can_proceed" means for different failure types.
        # Hint: Request structured output with failed/successful agents.
        raise NotImplementedError("Complete build_coordinator_prompt()")

    def parse_coordinator_response(self, response_text: str) -> dict:
        """
        Parse the coordinator's response into a structured decision.

        The decision must have:
          - "can_proceed": bool
          - "failed_agents": list of str
          - "successful_agents": list of str
          - "recovery_actions": list of str

        Args:
            response_text: The raw text response from Claude.

        Returns:
            A dict with the coordinator's decision.
        """
        # TODO: Parse the response into a structured decision.
        # Hint: Use json.loads() if you requested JSON output.
        # Hint: Handle malformed responses gracefully.
        raise NotImplementedError("Complete parse_coordinator_response()")

    def classify_error(self, error_result: dict) -> str:
        """
        Classify an error as "access_failure" or "empty_result".

        Access failures (timeout, permission denied, service unavailable)
        mean "we couldn't look." Empty results mean "we looked and found nothing."

        Args:
            error_result: A dict with error_type and other fields.

        Returns:
            "access_failure" or "empty_result"
        """
        # TODO: Classify the error type.
        # Hint: connection_timeout, permission_denied, service_unavailable = access_failure
        # Hint: empty_result, not_found, no_match = empty_result
        raise NotImplementedError("Complete classify_error()")

    def run_pipeline_test(self, pipeline: dict) -> dict:
        """
        Run the coordinator on a pipeline and return the decision.

        This method is provided — do not modify it.
        """
        prompt = self.build_coordinator_prompt(pipeline["results"])
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return self.parse_coordinator_response(response.content[0].text)

    def evaluate(self, pipelines=None):
        """
        Evaluate coordinator decisions across all test pipelines.

        This method is provided — do not modify it.
        """
        if pipelines is None:
            pipelines = ALL_PIPELINES

        all_correct = True

        for pipeline in pipelines:
            print(f"\n{'='*60}")
            print(f"Pipeline: {pipeline['name']}")
            print(f"{'='*60}")

            decision = self.run_pipeline_test(pipeline)
            expected = pipeline["expected_decision"]

            proceed_match = decision.get("can_proceed") == expected["can_proceed"]
            failed_match = set(decision.get("failed_agents", [])) == set(expected["failed_agents"])
            success_match = set(decision.get("successful_agents", [])) == set(expected["successful_agents"])

            print(f"  can_proceed: {decision.get('can_proceed')} (expected {expected['can_proceed']}) — {'OK' if proceed_match else 'WRONG'}")
            print(f"  failed_agents: {decision.get('failed_agents')} — {'OK' if failed_match else 'WRONG'}")
            print(f"  successful_agents: {decision.get('successful_agents')} — {'OK' if success_match else 'WRONG'}")

            if not (proceed_match and failed_match and success_match):
                all_correct = False

        print(f"\n{'='*60}")
        print("OVERALL RESULTS")
        print(f"{'='*60}")
        if all_correct:
            print("\n  CHALLENGE PASSED — all pipeline decisions correct!")
        else:
            print("\n  NEEDS WORK — some decisions were incorrect.")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Error Propagation Challenge")
    print("================================")
    print("Goal: Correct error handling for all pipelines\n")

    challenge = ErrorPropagationChallenge()
    challenge.evaluate()
