"""
CHALLENGE: Build Tool Descriptions That Achieve Reliable Selection

Task Statement 2.1 — Design tool descriptions that serve as the primary
selection mechanism for Claude.

Your goal: write tool descriptions so that, when given to Claude with a user
query, the correct tool is selected every time.

Complete the three methods in ToolDescriptionChallenge:
  1. build_tools()           — return a list of tool definitions with descriptions
  2. evaluate_selection()    — check if the selected tool matches expected
  3. suggest_fix()           — given a misselection, suggest a description improvement

The checker will test your descriptions against queries with known correct
tools. You must achieve 100% selection accuracy.
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# Test scenarios: tools + queries with expected correct selections
# ---------------------------------------------------------------------------

SCENARIO_1_TOOLS_SKELETON = [
    {"name": "search_docs", "params": ["query", "filters"]},
    {"name": "search_web", "params": ["query"]},
    {"name": "query_database", "params": ["sql", "database"]},
]

SCENARIO_1_QUERIES = [
    {
        "query": "Find our internal policy on remote work",
        "expected_tool": "search_docs",
    },
    {
        "query": "What is the latest news about Python 3.13?",
        "expected_tool": "search_web",
    },
    {
        "query": "How many active users signed up last month?",
        "expected_tool": "query_database",
    },
    {
        "query": "What does our employee handbook say about PTO?",
        "expected_tool": "search_docs",
    },
    {
        "query": "Look up the current stock price of ANTHROPIC competitors",
        "expected_tool": "search_web",
    },
    {
        "query": "Get the total revenue for Q3 from the sales table",
        "expected_tool": "query_database",
    },
]

SCENARIO_2_TOOLS_SKELETON = [
    {"name": "get_file_content", "params": ["file_path"]},
    {"name": "search_codebase", "params": ["pattern", "file_type"]},
    {"name": "list_directory", "params": ["path"]},
    {"name": "get_file_metadata", "params": ["file_path"]},
]

SCENARIO_2_QUERIES = [
    {
        "query": "Show me the contents of src/main.py",
        "expected_tool": "get_file_content",
    },
    {
        "query": "Find all files that import the requests library",
        "expected_tool": "search_codebase",
    },
    {
        "query": "What files are in the tests/ directory?",
        "expected_tool": "list_directory",
    },
    {
        "query": "When was config.yaml last modified?",
        "expected_tool": "get_file_metadata",
    },
    {
        "query": "Where is the database connection string defined in the code?",
        "expected_tool": "search_codebase",
    },
    {
        "query": "What's the file size of the production database dump?",
        "expected_tool": "get_file_metadata",
    },
]

ALL_SCENARIOS = [
    (SCENARIO_1_TOOLS_SKELETON, SCENARIO_1_QUERIES),
    (SCENARIO_2_TOOLS_SKELETON, SCENARIO_2_QUERIES),
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class ToolDescriptionChallenge:
    """
    Build tool definitions with descriptions that achieve
    100% selection accuracy.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_tools(self, tool_skeletons: list[dict]) -> list[dict]:
        """
        Given a list of tool skeletons (name + param names), return
        full tool definitions with production-grade descriptions.

        Each tool definition must have:
        - "name": str (from skeleton)
        - "description": str (YOUR production-grade description)
        - "input_schema": dict (JSON Schema for parameters)

        Requirements for descriptions:
        - What the tool does (specific capability)
        - When to use it (positive triggers)
        - When NOT to use it (negative boundaries with alternatives)

        Args:
            tool_skeletons: List of {"name": str, "params": list[str]}

        Returns:
            List of complete tool definitions ready for the API.
        """
        # TODO: Build full tool definitions with production-grade descriptions.
        # Hint: For each skeleton, write a description that includes:
        #   1. What it does
        #   2. When to use it (positive triggers)
        #   3. When NOT to use it (negative boundaries)
        # Hint: Build input_schema from the params list.
        raise NotImplementedError("Complete build_tools()")

    def evaluate_selection(
        self, selected_tool: str, expected_tool: str
    ) -> dict:
        """
        Evaluate whether a tool selection was correct.

        Args:
            selected_tool: The tool name Claude selected.
            expected_tool: The tool name that should have been selected.

        Returns:
            A dict with:
            - "correct": bool
            - "selected": str
            - "expected": str
        """
        # TODO: Implement evaluation logic.
        raise NotImplementedError("Complete evaluate_selection()")

    def suggest_fix(
        self, query: str, selected_tool: str, expected_tool: str
    ) -> str:
        """
        Given a misselection, suggest how to fix the tool description.

        Args:
            query: The user query that caused misselection.
            selected_tool: The tool that was incorrectly selected.
            expected_tool: The tool that should have been selected.

        Returns:
            A string suggestion for improving the description of the
            incorrectly selected tool.
        """
        # TODO: Generate a suggestion for fixing the description.
        # Hint: The fix is always a negative boundary:
        #   "Add to {selected_tool}: Do NOT use for ... -- use {expected_tool}"
        raise NotImplementedError("Complete suggest_fix()")

    def run_selection(self, tools: list[dict], query: str) -> str:
        """
        Send a query to Claude with tools and return the selected tool name.

        This method is provided for you — do not modify it.
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            tools=tools,
            tool_choice={"type": "any"},
            messages=[{"role": "user", "content": query}],
        )
        for block in response.content:
            if block.type == "tool_use":
                return block.name
        return "none"

    def evaluate_scenario(
        self, tool_skeletons: list[dict], queries: list[dict]
    ):
        """
        Evaluate your descriptions against a full scenario.

        This method is provided for you — do not modify it.
        """
        tools = self.build_tools(tool_skeletons)
        results = []

        for q in queries:
            selected = self.run_selection(tools, q["query"])
            evaluation = self.evaluate_selection(selected, q["expected_tool"])
            results.append({**evaluation, "query": q["query"]})

        correct = sum(1 for r in results if r["correct"])
        total = len(results)

        print(f"\nAccuracy: {correct}/{total} ({correct/total:.0%})")
        for r in results:
            tag = "CORRECT" if r["correct"] else "WRONG"
            print(f"  [{tag}] \"{r['query'][:50]}\"")
            if not r["correct"]:
                fix = self.suggest_fix(r["query"], r["selected"], r["expected"])
                print(f"         {fix}")

        return results


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Tool Description Challenge")
    print("==========================")
    print("Goal: 100% tool selection accuracy\n")

    challenge = ToolDescriptionChallenge()
    for i, (skeletons, queries) in enumerate(ALL_SCENARIOS, 1):
        print(f"\n{'='*60}")
        print(f"Scenario {i}")
        print(f"{'='*60}")
        challenge.evaluate_scenario(skeletons, queries)
