"""
CHALLENGE: Build a Coordinator-Subagent System

Task Statement 1.2 — Design a coordinator that dispatches to focused
subagents with scoped tools and isolated context.

Complete the three methods in CoordinatorChallenge:
  1. create_subagent_prompt(task, context_data) — build focused subagent prompts
  2. dispatch_subagent(prompt, tools)            — run a subagent with scoped tools
  3. coordinate(user_request)                    — full coordinator flow

The checker tests context isolation, tool scoping, and proper synthesis.
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# Simulated backend and tools
# ---------------------------------------------------------------------------

CUSTOMERS = {
    "C001": {"name": "Alice Johnson", "tier": "premium", "email": "alice@example.com"},
    "C002": {"name": "Bob Smith", "tier": "basic", "email": "bob@example.com"},
}

ORDERS = {
    "ORD-100": {"customer_id": "C001", "status": "shipped", "total": 89.99, "items": ["Widget Pro"]},
    "ORD-101": {"customer_id": "C001", "status": "delivered", "total": 24.99, "items": ["Cable Set"]},
}

CUSTOMER_TOOLS = [
    {"name": "lookup_customer", "description": "Look up customer by ID",
     "input_schema": {"type": "object", "properties": {"customer_id": {"type": "string"}}, "required": ["customer_id"]}}
]

ORDER_TOOLS = [
    {"name": "get_order", "description": "Get order details by ID",
     "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}},
    {"name": "get_customer_orders", "description": "Get all orders for a customer",
     "input_schema": {"type": "object", "properties": {"customer_id": {"type": "string"}}, "required": ["customer_id"]}}
]

ACTION_TOOLS = [
    {"name": "process_refund", "description": "Process a refund",
     "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}, "reason": {"type": "string"}}, "required": ["order_id", "amount", "reason"]}}
]


def execute_tool(name, tool_input):
    """Execute a service tool."""
    if name == "lookup_customer":
        cust = CUSTOMERS.get(tool_input["customer_id"])
        return json.dumps(cust if cust else {"error": "Not found"})
    elif name == "get_order":
        order = ORDERS.get(tool_input["order_id"])
        return json.dumps(order if order else {"error": "Not found"})
    elif name == "get_customer_orders":
        orders = {k: v for k, v in ORDERS.items() if v["customer_id"] == tool_input["customer_id"]}
        return json.dumps(orders if orders else {"error": "No orders"})
    elif name == "process_refund":
        return json.dumps({"status": "approved", "refund_id": "REF-001", "amount": tool_input["amount"]})
    return json.dumps({"error": f"Unknown tool: {name}"})


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class CoordinatorChallenge:
    """
    Build a coordinator-subagent system with proper context isolation
    and scoped tool access.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def create_subagent_prompt(self, task: str, context_data: dict) -> str:
        """
        Build a focused prompt for a subagent.

        The prompt must:
        - Include a clear task description
        - Include ONLY the specific data the subagent needs (from context_data)
        - Specify expected output format
        - NOT include unrelated context or full conversation history

        Args:
            task: Description of what the subagent should do.
            context_data: Dict of specific data to pass (e.g., {"customer_id": "C001"}).

        Returns:
            A complete prompt string for the subagent.
        """
        # TODO: Build a focused subagent prompt.
        # Include: task description, relevant data from context_data, output format.
        # Exclude: unrelated context, full history.
        raise NotImplementedError("Complete create_subagent_prompt()")

    def dispatch_subagent(self, prompt: str, tools: list) -> str:
        """
        Run a subagent with a fresh context and scoped tools.

        Key: The subagent starts with ONLY the prompt — no inherited context.

        Args:
            prompt: The subagent's task prompt (from create_subagent_prompt).
            tools: The scoped tool list for this subagent.

        Returns:
            The subagent's final text response.
        """
        # TODO: Run a subagent agentic loop with fresh context.
        # Messages should start with just the prompt — no history.
        # Use the provided tools list (scoped, not all tools).
        raise NotImplementedError("Complete dispatch_subagent()")

    def coordinate(self, user_request: str) -> dict:
        """
        Full coordinator flow: decompose request, dispatch subagents, synthesize.

        Steps:
        1. Dispatch customer lookup subagent (CUSTOMER_TOOLS only)
        2. Dispatch order lookup subagent (ORDER_TOOLS only)
        3. If refund needed, dispatch action subagent (ACTION_TOOLS only)
           — pass customer info and order info explicitly
        4. Return synthesized result

        Args:
            user_request: The user's original request.

        Returns:
            dict with:
            - "customer_info": result from customer subagent
            - "order_info": result from order subagent
            - "action_result": result from action subagent (if applicable, else None)
            - "subagents_dispatched": list of subagent labels dispatched
        """
        # TODO: Implement the coordinator flow.
        # Each subagent gets: focused prompt, scoped tools, NO shared context.
        raise NotImplementedError("Complete coordinate()")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Coordinator-Subagent Challenge")
    print("==============================")
    print("Goal: Dispatch focused subagents with isolated context\n")

    challenge = CoordinatorChallenge()
    result = challenge.coordinate(
        "Customer C001 wants a refund for order ORD-101 (Cable Set, $24.99)."
    )
    print(f"Subagents dispatched: {result['subagents_dispatched']}")
    print(f"Customer info: {result['customer_info'][:80]}")
    print(f"Order info: {result['order_info'][:80]}")
    print(f"Action result: {result['action_result']}")
