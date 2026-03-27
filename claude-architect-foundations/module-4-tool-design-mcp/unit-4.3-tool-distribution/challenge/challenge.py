"""
CHALLENGE: Design Tool Distribution for a Multi-Agent System

Task Statement 2.3 — Design tool distributions across agents and
configure tool_choice for reliable selection.

Your goal: distribute 16 tools across 4 agents (max 5 per agent),
design a router, and configure tool_choice for a 3-step pipeline.

Complete the three methods in ToolDistributionChallenge:
  1. distribute_tools(tools)        — assign tools to agents
  2. design_router(agent_configs)   — create router tool definitions
  3. configure_pipeline(steps)      — set tool_choice for each step

The checker will verify your distribution respects the 4-5 tool limit,
covers all tools, and uses correct tool_choice modes.
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# System tools to distribute
# ---------------------------------------------------------------------------

ALL_TOOLS = [
    # Data team (should get 4-5)
    {"name": "query_database", "domain": "data"},
    {"name": "run_report", "domain": "data"},
    {"name": "export_csv", "domain": "data"},
    {"name": "validate_data", "domain": "data"},
    # Analysis team (should get 4-5)
    {"name": "compute_metrics", "domain": "analysis"},
    {"name": "detect_anomalies", "domain": "analysis"},
    {"name": "forecast_trend", "domain": "analysis"},
    {"name": "compare_periods", "domain": "analysis"},
    # Visualization team (should get 4-5)
    {"name": "create_chart", "domain": "visualization"},
    {"name": "create_dashboard", "domain": "visualization"},
    {"name": "format_table", "domain": "visualization"},
    {"name": "export_pdf", "domain": "visualization"},
    # Communication team (should get 4-5)
    {"name": "draft_summary", "domain": "communication"},
    {"name": "send_email", "domain": "communication"},
    {"name": "create_presentation", "domain": "communication"},
    {"name": "schedule_meeting", "domain": "communication"},
]

# Cross-role tool that multiple agents may need
CROSS_ROLE_TOOL = {"name": "verify_fact", "domain": "shared"}

# Pipeline steps with required tool_choice
PIPELINE_STEPS = [
    {
        "step": 1,
        "name": "extract_data",
        "description": "Must always run query_database first",
        "required_tool": "query_database",
        "expected_tool_choice": {"type": "tool", "name": "query_database"},
    },
    {
        "step": 2,
        "name": "analyze",
        "description": "Must call an analysis tool, but any one is valid",
        "required_tool": None,
        "expected_tool_choice": {"type": "any"},
    },
    {
        "step": 3,
        "name": "present",
        "description": "May respond with text or call a visualization tool",
        "required_tool": None,
        "expected_tool_choice": {"type": "auto"},
    },
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class ToolDistributionChallenge:
    """
    Design tool distributions for a multi-agent analytics system.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def distribute_tools(self, tools: list[dict]) -> dict[str, list[str]]:
        """
        Distribute tools across agents. Each agent gets 4-5 tools max.

        Args:
            tools: List of {"name": str, "domain": str} tool definitions.

        Returns:
            Dict mapping agent name to list of tool names.
            Example: {"data_agent": ["query_database", "run_report", ...], ...}

        Rules:
        - Each agent gets at most 5 tools
        - Every tool must be assigned to exactly one agent
        - You may add the CROSS_ROLE_TOOL to agents that need it
          (it does NOT count against the 5-tool limit from ALL_TOOLS,
           but an agent should not exceed 6 total tools)
        """
        # TODO: Assign tools to agents based on domain.
        # Hint: Group by domain, then check counts.
        # Hint: Consider which agents benefit from verify_fact.
        raise NotImplementedError("Complete distribute_tools()")

    def design_router(self, agent_configs: dict[str, list[str]]) -> list[dict]:
        """
        Design router tools that direct queries to the right agent.

        Args:
            agent_configs: Output from distribute_tools().

        Returns:
            List of tool definitions for the router agent.
            Each tool should have: name, description, input_schema.
            The description should explain when to route to that agent.
        """
        # TODO: Create one routing tool per agent.
        # Hint: Each routing tool's description should list the
        #       types of queries that belong to that agent.
        raise NotImplementedError("Complete design_router()")

    def configure_pipeline(self, steps: list[dict]) -> list[dict]:
        """
        Configure tool_choice for each pipeline step.

        Args:
            steps: List of pipeline step definitions.

        Returns:
            List of {"step": int, "tool_choice": dict} configurations.

        Rules:
        - Step must always call a specific tool -> forced tool_choice
        - Step must call some tool but any is OK -> "any"
        - Step may respond with text or call a tool -> "auto"
        """
        # TODO: Map each step to the correct tool_choice mode.
        # Hint: Look at required_tool and description for each step.
        raise NotImplementedError("Complete configure_pipeline()")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Tool Distribution Challenge")
    print("============================")
    print(f"Tools to distribute: {len(ALL_TOOLS)}\n")

    challenge = ToolDistributionChallenge()

    # Test distribution
    print("1. Tool Distribution:")
    try:
        dist = challenge.distribute_tools(ALL_TOOLS)
        for agent, tools in dist.items():
            print(f"   {agent}: {len(tools)} tools -- {tools}")
    except NotImplementedError as e:
        print(f"   Not implemented: {e}")

    # Test router
    print("\n2. Router Design:")
    try:
        dist = challenge.distribute_tools(ALL_TOOLS)
        router = challenge.design_router(dist)
        for tool in router:
            print(f"   {tool['name']}: {tool['description'][:60]}...")
    except NotImplementedError as e:
        print(f"   Not implemented: {e}")

    # Test pipeline
    print("\n3. Pipeline Config:")
    try:
        config = challenge.configure_pipeline(PIPELINE_STEPS)
        for step in config:
            print(f"   Step {step['step']}: tool_choice = {step['tool_choice']}")
    except NotImplementedError as e:
        print(f"   Not implemented: {e}")
