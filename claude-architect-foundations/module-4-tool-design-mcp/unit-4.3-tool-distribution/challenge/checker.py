"""
Checker for Unit 4.3 — Tool Distribution Challenge

Validates tool distribution, router design, and pipeline configuration
without calling the Anthropic API.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    ToolDistributionChallenge,
    ALL_TOOLS,
    CROSS_ROLE_TOOL,
    PIPELINE_STEPS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create a ToolDistributionChallenge instance (no API calls)."""
    return ToolDistributionChallenge()


# ---------------------------------------------------------------------------
# Test 1: Tool Distribution
# ---------------------------------------------------------------------------

class TestDistribution:
    """Student's distribute_tools must respect the 4-5 tool limit."""

    def test_returns_dict(self, challenge):
        dist = challenge.distribute_tools(ALL_TOOLS)
        assert isinstance(dist, dict), "distribute_tools must return a dict"

    def test_all_tools_assigned(self, challenge):
        dist = challenge.distribute_tools(ALL_TOOLS)
        assigned = set()
        for tools in dist.values():
            assigned.update(tools)
        expected = {t["name"] for t in ALL_TOOLS}
        missing = expected - assigned
        assert not missing, f"Tools not assigned to any agent: {missing}"

    def test_no_tool_assigned_twice(self, challenge):
        dist = challenge.distribute_tools(ALL_TOOLS)
        all_tools = []
        for tools in dist.values():
            # Exclude the cross-role tool from duplication check
            all_tools.extend(t for t in tools if t != CROSS_ROLE_TOOL["name"])
        assert len(all_tools) == len(set(all_tools)), (
            "Some tools are assigned to multiple agents (excluding cross-role tools)"
        )

    def test_max_five_domain_tools_per_agent(self, challenge):
        dist = challenge.distribute_tools(ALL_TOOLS)
        for agent, tools in dist.items():
            domain_tools = [t for t in tools if t != CROSS_ROLE_TOOL["name"]]
            assert len(domain_tools) <= 5, (
                f"Agent '{agent}' has {len(domain_tools)} domain tools (max 5)"
            )

    def test_max_six_total_tools_per_agent(self, challenge):
        dist = challenge.distribute_tools(ALL_TOOLS)
        for agent, tools in dist.items():
            assert len(tools) <= 6, (
                f"Agent '{agent}' has {len(tools)} total tools (max 6 with cross-role)"
            )

    def test_at_least_three_agents(self, challenge):
        dist = challenge.distribute_tools(ALL_TOOLS)
        assert len(dist) >= 3, (
            f"Need at least 3 agents, got {len(dist)}"
        )

    def test_no_empty_agents(self, challenge):
        dist = challenge.distribute_tools(ALL_TOOLS)
        for agent, tools in dist.items():
            assert len(tools) > 0, f"Agent '{agent}' has no tools"


# ---------------------------------------------------------------------------
# Test 2: Router Design
# ---------------------------------------------------------------------------

class TestRouter:
    """Student's design_router must create routing tools for each agent."""

    def test_returns_list(self, challenge):
        dist = challenge.distribute_tools(ALL_TOOLS)
        router = challenge.design_router(dist)
        assert isinstance(router, list), "design_router must return a list"

    def test_one_route_per_agent(self, challenge):
        dist = challenge.distribute_tools(ALL_TOOLS)
        router = challenge.design_router(dist)
        assert len(router) == len(dist), (
            f"Expected {len(dist)} routing tools, got {len(router)}"
        )

    def test_routing_tools_have_required_fields(self, challenge):
        dist = challenge.distribute_tools(ALL_TOOLS)
        router = challenge.design_router(dist)
        for tool in router:
            assert "name" in tool, f"Routing tool missing 'name': {tool}"
            assert "description" in tool, f"Routing tool missing 'description': {tool}"
            assert "input_schema" in tool, f"Routing tool missing 'input_schema': {tool}"

    def test_routing_descriptions_not_empty(self, challenge):
        dist = challenge.distribute_tools(ALL_TOOLS)
        router = challenge.design_router(dist)
        for tool in router:
            assert len(tool["description"]) > 20, (
                f"Routing tool '{tool['name']}' description too short"
            )


# ---------------------------------------------------------------------------
# Test 3: Pipeline Configuration
# ---------------------------------------------------------------------------

class TestPipeline:
    """Student's configure_pipeline must set correct tool_choice modes."""

    def test_returns_list(self, challenge):
        config = challenge.configure_pipeline(PIPELINE_STEPS)
        assert isinstance(config, list), "configure_pipeline must return a list"

    def test_correct_count(self, challenge):
        config = challenge.configure_pipeline(PIPELINE_STEPS)
        assert len(config) == len(PIPELINE_STEPS), (
            f"Expected {len(PIPELINE_STEPS)} configs, got {len(config)}"
        )

    def test_step1_forced_tool(self, challenge):
        config = challenge.configure_pipeline(PIPELINE_STEPS)
        step1 = next(c for c in config if c["step"] == 1)
        tc = step1["tool_choice"]
        assert tc.get("type") == "tool", (
            f"Step 1 should force a specific tool, got type={tc.get('type')}"
        )
        assert tc.get("name") == "query_database", (
            f"Step 1 should force 'query_database', got name={tc.get('name')}"
        )

    def test_step2_any(self, challenge):
        config = challenge.configure_pipeline(PIPELINE_STEPS)
        step2 = next(c for c in config if c["step"] == 2)
        tc = step2["tool_choice"]
        assert tc.get("type") == "any", (
            f"Step 2 should use 'any', got type={tc.get('type')}"
        )

    def test_step3_auto(self, challenge):
        config = challenge.configure_pipeline(PIPELINE_STEPS)
        step3 = next(c for c in config if c["step"] == 3)
        tc = step3["tool_choice"]
        assert tc.get("type") == "auto", (
            f"Step 3 should use 'auto', got type={tc.get('type')}"
        )

    def test_each_config_has_step_and_tool_choice(self, challenge):
        config = challenge.configure_pipeline(PIPELINE_STEPS)
        for c in config:
            assert "step" in c, f"Config missing 'step': {c}"
            assert "tool_choice" in c, f"Config missing 'tool_choice': {c}"
            assert isinstance(c["tool_choice"], dict), (
                f"tool_choice must be a dict, got {type(c['tool_choice'])}"
            )
