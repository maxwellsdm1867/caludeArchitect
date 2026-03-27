"""
CHALLENGE: Build a Proper Agentic Loop

Task Statement 1.1 — Implement a stop_reason-driven agentic loop that
handles tool calls correctly and avoids anti-patterns.

Complete the three methods in AgenticLoopChallenge:
  1. run_agent(user_message, tools)  — the main agentic loop
  2. process_tool_calls(response)    — extract and execute tool calls
  3. should_continue(response)       — determine if loop should continue

The checker validates your loop handles multi-step tasks, single-step tasks,
and no-tool tasks correctly — all without making real API calls.
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# Tool definitions used by the challenge
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate a mathematical expression.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "store_value",
        "description": "Store a named value.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "number"}
            },
            "required": ["name", "value"]
        }
    }
]

STORED_VALUES = {}


def execute_tool(name, tool_input):
    """Execute a tool and return the result string."""
    if name == "calculator":
        try:
            result = eval(tool_input["expression"], {"__builtins__": {}}, {})
            return json.dumps({"result": result})
        except Exception as e:
            return json.dumps({"error": str(e)})
    elif name == "store_value":
        STORED_VALUES[tool_input["name"]] = tool_input["value"]
        return json.dumps({"stored": tool_input["name"], "value": tool_input["value"]})
    return json.dumps({"error": f"Unknown tool: {name}"})


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class AgenticLoopChallenge:
    """
    Build a proper stop_reason-driven agentic loop.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def should_continue(self, response) -> bool:
        """
        Determine if the agentic loop should continue based on the response.

        The loop should continue ONLY when the model wants to use tools.
        It should stop when the model signals completion.

        Args:
            response: The API response object with a stop_reason attribute.

        Returns:
            True if the loop should continue (model wants tools),
            False if the loop should stop (model is done).
        """
        # TODO: Implement using stop_reason.
        # DO NOT parse text content for termination signals.
        # DO NOT use iteration counts as the primary mechanism.
        raise NotImplementedError("Complete should_continue()")

    def process_tool_calls(self, response) -> list:
        """
        Extract tool calls from the response, execute them, and return
        tool_result blocks for the next API call.

        Must handle responses that contain BOTH text and tool_use blocks.
        Must preserve the full assistant response (text + tool_use) in history.

        Args:
            response: The API response object.

        Returns:
            A list of tool_result dicts, each with:
            - "type": "tool_result"
            - "tool_use_id": the tool call's ID
            - "content": the tool execution result (string)
        """
        # TODO: Extract tool_use blocks, execute each, return results.
        # Hint: response.content is a list of blocks (text and/or tool_use).
        # Hint: Use execute_tool(name, input) for each tool_use block.
        raise NotImplementedError("Complete process_tool_calls()")

    def run_agent(self, user_message, tools=None, safety_cap=25):
        """
        Run the agentic loop.

        Requirements:
        - Use while True (not for i in range)
        - Primary termination: stop_reason via should_continue()
        - Safety cap as a SAFETY NET only (not primary mechanism)
        - Append full assistant response to messages (both text + tool blocks)
        - Append tool results as user messages

        Args:
            user_message: The user's input message.
            tools: List of tool definitions (defaults to TOOLS).
            safety_cap: Maximum iterations as safety net.

        Returns:
            dict with:
            - "final_text": The model's final text response
            - "iterations": Number of loop iterations
            - "tool_calls": List of tool names called
            - "terminated_by": "stop_reason" or "safety_cap"
        """
        if tools is None:
            tools = TOOLS

        # TODO: Implement the agentic loop.
        # Pattern:
        #   messages = [{"role": "user", "content": user_message}]
        #   while True:
        #       response = self.client.messages.create(...)
        #       if not self.should_continue(response): break
        #       tool_results = self.process_tool_calls(response)
        #       messages.append({"role": "assistant", "content": response.content})
        #       messages.append({"role": "user", "content": tool_results})
        raise NotImplementedError("Complete run_agent()")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Agentic Loop Challenge")
    print("======================")
    print("Goal: Build a stop_reason-driven loop that handles multi-step tasks\n")

    challenge = AgenticLoopChallenge()

    # Test 1: Multi-step calculation
    print("Test 1: Multi-step calculation")
    result = challenge.run_agent(
        "Calculate 15 * 8, then add 25% tax, then store the result as 'total'."
    )
    print(f"  Iterations: {result['iterations']}")
    print(f"  Tool calls: {result['tool_calls']}")
    print(f"  Terminated by: {result['terminated_by']}")
    print(f"  Final text: {result['final_text'][:100]}")

    # Test 2: No tools needed
    print("\nTest 2: No tools needed")
    result = challenge.run_agent(
        "What is the capital of France? Do not use any tools."
    )
    print(f"  Iterations: {result['iterations']}")
    print(f"  Terminated by: {result['terminated_by']}")
