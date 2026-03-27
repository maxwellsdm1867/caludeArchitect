"""
Checker for Unit 5.3 — Subagent Context Passing Challenge

Validates that context is properly scoped: includes needed data,
excludes irrelevant data. No API calls.
"""

import json
import pytest

from challenge import ContextPassingChallenge, DOCUMENT


@pytest.fixture
def challenge():
    return ContextPassingChallenge()


# ---------------------------------------------------------------------------
# Test 1: Context Extraction
# ---------------------------------------------------------------------------

class TestContextExtraction:
    """build_analysis_context must return properly scoped data."""

    def test_market_data_contains_spending(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "market_data")
        assert isinstance(ctx, dict), "Must return a dict"
        ctx_str = json.dumps(ctx)
        assert "12.8" in ctx_str or "7.6" in ctx_str, (
            "Market context must contain spending data"
        )

    def test_market_data_excludes_competitors(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "market_data")
        ctx_str = json.dumps(ctx)
        assert "CloudCo" not in ctx_str, (
            "Market context must NOT contain competitor names"
        )

    def test_market_data_excludes_risks(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "market_data")
        ctx_str = json.dumps(ctx)
        assert "GPU" not in ctx_str and "EU AI Act" not in ctx_str, (
            "Market context must NOT contain risk descriptions"
        )

    def test_competitors_contains_names(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "competitors")
        ctx_str = json.dumps(ctx)
        assert "CloudCo" in ctx_str or "DataScale" in ctx_str, (
            "Competitor context must contain company names"
        )

    def test_competitors_excludes_risks(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "competitors")
        ctx_str = json.dumps(ctx)
        assert "GPU" not in ctx_str and "supply_chain" not in ctx_str, (
            "Competitor context must NOT contain risk data"
        )

    def test_risks_contains_risk_data(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "risks")
        ctx_str = json.dumps(ctx)
        assert "GPU" in ctx_str or "supply" in ctx_str.lower() or "regulatory" in ctx_str.lower(), (
            "Risk context must contain risk descriptions"
        )

    def test_risks_excludes_competitors(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "risks")
        ctx_str = json.dumps(ctx)
        assert "CloudCo" not in ctx_str and "DataScale" not in ctx_str, (
            "Risk context must NOT contain competitor names"
        )


# ---------------------------------------------------------------------------
# Test 2: Prompt Construction
# ---------------------------------------------------------------------------

class TestPromptConstruction:
    """build_subagent_prompt must produce focused prompts."""

    def test_prompt_returns_string(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "market_data")
        prompt = challenge.build_subagent_prompt("Analyze market data", ctx)
        assert isinstance(prompt, str), "Must return a string"

    def test_prompt_contains_task(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "market_data")
        prompt = challenge.build_subagent_prompt("Analyze market growth rates", ctx)
        assert "market" in prompt.lower() or "growth" in prompt.lower(), (
            "Prompt must reference the task"
        )

    def test_prompt_contains_data(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "market_data")
        prompt = challenge.build_subagent_prompt("Analyze", ctx)
        assert "12.8" in prompt or "7.6" in prompt, (
            "Prompt must include the context data"
        )

    def test_prompt_length_reasonable(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "market_data")
        prompt = challenge.build_subagent_prompt("Analyze market data", ctx)
        assert len(prompt) > 50, "Prompt too short -- needs task + data + format"
        assert len(prompt) < 5000, "Prompt too long -- may contain too much context"


# ---------------------------------------------------------------------------
# Test 3: Context Scoping Validation
# ---------------------------------------------------------------------------

class TestContextValidation:
    """validate_context_scoping must correctly detect scope violations."""

    def test_valid_market_prompt(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "market_data")
        prompt = challenge.build_subagent_prompt("Analyze market data", ctx)
        result = challenge.validate_context_scoping(prompt, "market_data")
        assert result["is_valid"] is True, (
            "Properly scoped market prompt should be valid"
        )
        assert result["contains_own_data"] is True
        assert result["leaks_other_data"] is False

    def test_valid_competitor_prompt(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "competitors")
        prompt = challenge.build_subagent_prompt("Analyze competitors", ctx)
        result = challenge.validate_context_scoping(prompt, "competitors")
        assert result["is_valid"] is True

    def test_valid_risk_prompt(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "risks")
        prompt = challenge.build_subagent_prompt("Analyze risks", ctx)
        result = challenge.validate_context_scoping(prompt, "risks")
        assert result["is_valid"] is True

    def test_detects_leaked_competitors_in_market(self, challenge):
        """If competitor data leaks into a market prompt, validation should catch it."""
        leaky_prompt = "Analyze market data. Total spending: $12.8B. CloudCo has 34% market share."
        result = challenge.validate_context_scoping(leaky_prompt, "market_data")
        assert result["leaks_other_data"] is True, (
            "Should detect competitor data in market prompt"
        )

    def test_detects_leaked_risks_in_competitor(self, challenge):
        leaky_prompt = "Analyze competitors: CloudCo, DataScale. GPU supply chain is a risk."
        result = challenge.validate_context_scoping(leaky_prompt, "competitors")
        assert result["leaks_other_data"] is True, (
            "Should detect risk data in competitor prompt"
        )

    def test_returns_required_fields(self, challenge):
        ctx = challenge.build_analysis_context(DOCUMENT, "market_data")
        prompt = challenge.build_subagent_prompt("Test", ctx)
        result = challenge.validate_context_scoping(prompt, "market_data")
        for field in ["is_valid", "contains_own_data", "leaks_other_data", "leaked_sections"]:
            assert field in result, f"Result must contain '{field}'"
