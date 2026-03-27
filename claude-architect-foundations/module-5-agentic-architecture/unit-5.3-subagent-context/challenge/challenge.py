"""
CHALLENGE: Master Subagent Context Passing

Task Statement 1.3 — Pass explicit, scoped context to subagents.
Demonstrate the difference between Task (isolated) and fork_session (shared).

Complete the three methods in ContextPassingChallenge:
  1. build_analysis_context(document, section)  — extract relevant context
  2. build_subagent_prompt(task, context)        — build a focused prompt
  3. validate_context_scoping(prompt, section)   — verify context isolation

The checker tests that context is properly scoped: includes needed data,
excludes irrelevant data.
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# Test document with multiple sections
# ---------------------------------------------------------------------------

DOCUMENT = {
    "title": "Q4 2024 AI Market Report",
    "sections": {
        "market_data": {
            "total_spending": 12.8,
            "unit": "billion_usd",
            "yoy_growth": 0.45,
            "segments": {
                "cloud": {"spending": 7.6, "growth": 0.52},
                "on_premise": {"spending": 3.8, "growth": 0.28},
                "edge": {"spending": 1.4, "growth": 0.61}
            }
        },
        "competitors": [
            {"name": "CloudCo", "market_share": 0.34, "revenue": 4.35},
            {"name": "DataScale", "market_share": 0.22, "revenue": 2.82},
            {"name": "InfraMax", "market_share": 0.18, "revenue": 2.30}
        ],
        "risks": {
            "supply_chain": "GPU allocation constraints may limit Q1 2025 growth",
            "regulatory": "EU AI Act compute requirements could impact cloud segment",
            "market": "Potential bubble if spending growth outpaces adoption"
        },
        "recommendations": [
            "Increase allocation to edge computing (highest growth)",
            "Monitor GPU supply chain weekly",
            "Prepare EU AI Act compliance framework"
        ]
    }
}

# Section-specific tools
MARKET_TOOLS = [
    {"name": "calculate_metric", "description": "Calculate a derived metric",
     "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}, "label": {"type": "string"}}, "required": ["expression", "label"]}}
]

RISK_TOOLS = [
    {"name": "flag_risk", "description": "Flag a risk with severity",
     "input_schema": {"type": "object", "properties": {"risk": {"type": "string"}, "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]}}, "required": ["risk", "severity"]}}
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class ContextPassingChallenge:
    """
    Master explicit context passing to subagents.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_analysis_context(self, document: dict, section: str) -> dict:
        """
        Extract ONLY the relevant data for a specific analysis section.

        For "market_data" section: include market_data and total spending.
        For "competitors" section: include competitors and total market size.
        For "risks" section: include risks and relevant market context.

        Must NOT include unrelated sections. A market analysis subagent
        should not receive risk data, and vice versa.

        Args:
            document: The full document dict.
            section: Which section to extract ("market_data", "competitors", "risks").

        Returns:
            A dict with only the relevant data for that section.
        """
        # TODO: Extract section-specific context from the document.
        # Include: the requested section's data + minimal shared context (e.g., total spending).
        # Exclude: other sections' data.
        raise NotImplementedError("Complete build_analysis_context()")

    def build_subagent_prompt(self, task: str, context: dict) -> str:
        """
        Build a focused prompt for a subagent using the provided context.

        The prompt must:
        - Include a clear task description
        - Include the context data (formatted for readability)
        - Specify expected output format
        - NOT include instructions about other analysis types

        Args:
            task: What the subagent should do.
            context: The scoped context from build_analysis_context.

        Returns:
            A complete prompt string.
        """
        # TODO: Build a focused subagent prompt.
        # Format the context data clearly.
        # Include task description and output format.
        raise NotImplementedError("Complete build_subagent_prompt()")

    def validate_context_scoping(self, prompt: str, section: str) -> dict:
        """
        Validate that a prompt is properly scoped to its section.

        Checks:
        - Contains data from the requested section
        - Does NOT contain data from other sections

        Args:
            prompt: The subagent prompt to validate.
            section: The section the prompt should be scoped to.

        Returns:
            dict with:
            - "is_valid": bool
            - "contains_own_data": bool (has its section's data)
            - "leaks_other_data": bool (has data from other sections)
            - "leaked_sections": list of leaked section names
        """
        # TODO: Check the prompt for proper scoping.
        # For "market_data": should contain spending numbers, should NOT contain competitor names or risk text.
        # For "competitors": should contain company names, should NOT contain risk text.
        # For "risks": should contain risk descriptions, should NOT contain competitor names.
        raise NotImplementedError("Complete validate_context_scoping()")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Context Passing Challenge")
    print("========================")
    print("Goal: Build properly scoped context for each subagent\n")

    challenge = ContextPassingChallenge()

    for section in ["market_data", "competitors", "risks"]:
        print(f"\n--- Section: {section} ---")
        context = challenge.build_analysis_context(DOCUMENT, section)
        prompt = challenge.build_subagent_prompt(f"Analyze {section}", context)
        validation = challenge.validate_context_scoping(prompt, section)
        print(f"  Context keys: {list(context.keys())}")
        print(f"  Prompt length: {len(prompt)} chars")
        print(f"  Valid scoping: {validation['is_valid']}")
        if validation["leaked_sections"]:
            print(f"  LEAKED: {validation['leaked_sections']}")
