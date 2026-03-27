"""
Checker for Unit 2.6 — Provenance Challenge

Validates the student's ProvenanceChallenge implementation without
calling the Anthropic API. Tests synthesis prompt construction, response
parsing, and provenance verification logic.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    ProvenanceChallenge,
    DATASET_1, DATASET_2, DATASET_3,
    ALL_DATASETS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create a ProvenanceChallenge instance (no API calls)."""
    return ProvenanceChallenge()


# ---------------------------------------------------------------------------
# Mock API responses — correct provenance synthesis
# ---------------------------------------------------------------------------

MOCK_SYNTHESIS_1 = json.dumps({
    "claims": [
        {
            "topic": "revenue",
            "value": None,
            "sources": [
                {"name": "Annual Report", "date": "2024-03-15", "value": "$4.2 billion"},
                {"name": "TechCrunch", "date": "2024-12-01", "value": "$4.5 billion (projected)"},
                {"name": "Goldman Sachs", "date": "2024-09-20", "value": "$4.3 billion (estimated)"}
            ],
            "status": "conflicting"
        },
        {
            "topic": "employees",
            "value": None,
            "sources": [
                {"name": "Annual Report", "date": "2024-03-15", "value": "15000"},
                {"name": "TechCrunch", "date": "2024-12-01", "value": "16200"},
                {"name": "Goldman Sachs", "date": "2024-09-20", "value": "15500"}
            ],
            "status": "conflicting"
        },
        {
            "topic": "headquarters",
            "value": "San Francisco, CA",
            "sources": [{"name": "Annual Report", "date": "2024-03-15", "value": "San Francisco, CA"}],
            "status": "single_source"
        },
        {
            "topic": "ceo",
            "value": "Jane Smith",
            "sources": [{"name": "Annual Report", "date": "2024-03-15", "value": "Jane Smith"}],
            "status": "single_source"
        },
        {
            "topic": "market_cap",
            "value": "$28 billion",
            "sources": [{"name": "Goldman Sachs", "date": "2024-09-20", "value": "$28 billion"}],
            "status": "single_source"
        },
        {
            "topic": "ESG rating",
            "value": None,
            "sources": [],
            "status": "not_found"
        }
    ],
    "conflicts": [
        {"topic": "revenue", "values_by_source": {"Annual Report": "$4.2B", "TechCrunch": "$4.5B", "Goldman Sachs": "$4.3B"}},
        {"topic": "employees", "values_by_source": {"Annual Report": "15000", "TechCrunch": "16200", "Goldman Sachs": "15500"}}
    ],
    "coverage_gaps": ["ESG rating"],
    "overall_confidence": "medium"
})

MOCK_SYNTHESIS_2 = json.dumps({
    "claims": [
        {
            "topic": "compliance_deadline",
            "value": None,
            "sources": [
                {"name": "Federal Register Vol 89, No 45", "date": "2024-03-01", "value": "September 1, 2025"},
                {"name": "Federal Register Vol 89, No 198", "date": "2024-10-15", "value": "March 1, 2026"},
                {"name": "Banking Compliance Handbook", "date": "2024-06-01", "value": "September 1, 2025"}
            ],
            "status": "conflicting"
        }
    ],
    "conflicts": [
        {"topic": "compliance_deadline", "values_by_source": {"Old regulation": "Sep 2025", "Amendment": "Mar 2026"}}
    ],
    "coverage_gaps": ["required certifications"],
    "overall_confidence": "medium"
})


# ---------------------------------------------------------------------------
# Test 1: Synthesis Prompt Construction
# ---------------------------------------------------------------------------

class TestPromptConstruction:
    """Student's build_synthesis_prompt must enforce provenance tracking."""

    def test_prompt_returns_string(self, challenge):
        prompt = challenge.build_synthesis_prompt(DATASET_1["sources"], DATASET_1["query"])
        assert isinstance(prompt, str), "build_synthesis_prompt must return a string"

    def test_prompt_contains_sources(self, challenge):
        prompt = challenge.build_synthesis_prompt(DATASET_1["sources"], DATASET_1["query"])
        assert "Annual Report" in prompt or "annual_report" in prompt, (
            "Prompt must include the source data"
        )

    def test_prompt_contains_query(self, challenge):
        prompt = challenge.build_synthesis_prompt(DATASET_1["sources"], DATASET_1["query"])
        assert "revenue" in prompt.lower(), "Prompt must include the query topics"

    def test_prompt_requires_conflict_detection(self, challenge):
        prompt = challenge.build_synthesis_prompt(DATASET_1["sources"], DATASET_1["query"]).lower()
        has_conflict_instruction = any(
            kw in prompt for kw in ["conflict", "disagree", "different value",
                                     "contradicting", "discrepancy"]
        )
        assert has_conflict_instruction, (
            "Prompt must instruct the model to detect and report conflicts"
        )

    def test_prompt_requires_gap_reporting(self, challenge):
        prompt = challenge.build_synthesis_prompt(DATASET_1["sources"], DATASET_1["query"]).lower()
        has_gap_instruction = any(
            kw in prompt for kw in ["gap", "not found", "missing", "coverage",
                                     "not in any source", "absent"]
        )
        assert has_gap_instruction, (
            "Prompt must instruct the model to report coverage gaps"
        )

    def test_prompt_requires_source_mapping(self, challenge):
        prompt = challenge.build_synthesis_prompt(DATASET_1["sources"], DATASET_1["query"]).lower()
        has_mapping_instruction = any(
            kw in prompt for kw in ["source", "cite", "attribution", "map",
                                     "provenance", "which source"]
        )
        assert has_mapping_instruction, (
            "Prompt must require claim-to-source mapping"
        )

    def test_prompt_not_naive_synthesis(self, challenge):
        prompt = challenge.build_synthesis_prompt(DATASET_1["sources"], DATASET_1["query"]).lower()
        naive_phrases = [
            "write a coherent summary",
            "synthesize into a paragraph",
            "combine all sources",
        ]
        for phrase in naive_phrases:
            assert phrase not in prompt, (
                f"Prompt should NOT use naive synthesis instruction: '{phrase}'"
            )


# ---------------------------------------------------------------------------
# Test 2: Response Parsing
# ---------------------------------------------------------------------------

class TestParsing:
    """Student's parse_synthesis must return structured provenance data."""

    def test_parse_returns_dict(self, challenge):
        result = challenge.parse_synthesis(MOCK_SYNTHESIS_1)
        assert isinstance(result, dict), "parse_synthesis must return a dict"

    def test_parse_has_claims(self, challenge):
        result = challenge.parse_synthesis(MOCK_SYNTHESIS_1)
        assert "claims" in result, "Synthesis must have 'claims' key"
        assert isinstance(result["claims"], list), "claims must be a list"

    def test_parse_has_coverage_gaps(self, challenge):
        result = challenge.parse_synthesis(MOCK_SYNTHESIS_1)
        assert "coverage_gaps" in result, "Synthesis must have 'coverage_gaps' key"
        assert isinstance(result["coverage_gaps"], list), "coverage_gaps must be a list"

    def test_parse_detects_conflicts(self, challenge):
        result = challenge.parse_synthesis(MOCK_SYNTHESIS_1)
        conflicting = [c for c in result.get("claims", []) if c.get("status") == "conflicting"]
        assert len(conflicting) > 0, "Should detect conflicting claims"

    def test_parse_detects_gaps(self, challenge):
        result = challenge.parse_synthesis(MOCK_SYNTHESIS_1)
        gaps = result.get("coverage_gaps", [])
        assert any("esg" in g.lower() for g in gaps), (
            "Should detect ESG rating as a coverage gap"
        )


# ---------------------------------------------------------------------------
# Test 3: Provenance Verification
# ---------------------------------------------------------------------------

class TestVerification:
    """Student's verify_provenance must check conflicts and gaps."""

    def test_returns_dict(self, challenge):
        synthesis = challenge.parse_synthesis(MOCK_SYNTHESIS_1)
        result = challenge.verify_provenance(synthesis, DATASET_1["expected"])
        assert isinstance(result, dict), "verify_provenance must return a dict"

    def test_has_required_keys(self, challenge):
        synthesis = challenge.parse_synthesis(MOCK_SYNTHESIS_1)
        result = challenge.verify_provenance(synthesis, DATASET_1["expected"])
        assert "conflicts_found" in result
        assert "conflicts_missed" in result
        assert "gaps_found" in result
        assert "gaps_missed" in result
        assert "score" in result

    def test_finds_revenue_conflict(self, challenge):
        synthesis = challenge.parse_synthesis(MOCK_SYNTHESIS_1)
        result = challenge.verify_provenance(synthesis, DATASET_1["expected"])
        assert any("revenue" in c.lower() for c in result["conflicts_found"]), (
            "Should detect revenue conflict"
        )

    def test_finds_esg_gap(self, challenge):
        synthesis = challenge.parse_synthesis(MOCK_SYNTHESIS_1)
        result = challenge.verify_provenance(synthesis, DATASET_1["expected"])
        assert any("esg" in g.lower() for g in result["gaps_found"]), (
            "Should detect ESG rating gap"
        )

    def test_perfect_score_for_correct_synthesis(self, challenge):
        synthesis = challenge.parse_synthesis(MOCK_SYNTHESIS_1)
        result = challenge.verify_provenance(synthesis, DATASET_1["expected"])
        assert result["score"] >= 0.70, (
            f"Correct synthesis should have high score, got {result['score']:.0%}"
        )


# ---------------------------------------------------------------------------
# Test 4: End-to-End (uses mocked API)
# ---------------------------------------------------------------------------

class TestEndToEnd:
    """End-to-end test using mocked Claude responses."""

    def _mock_call(self, challenge, dataset, mock_response):
        """Helper: mock the API and run the synthesis."""
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=mock_response)]

        with patch.object(challenge.client.messages, "create", return_value=mock_msg):
            return challenge.run_synthesis(dataset)

    def test_dataset_1_detects_conflicts(self, challenge):
        result = self._mock_call(challenge, DATASET_1, MOCK_SYNTHESIS_1)
        v = result["verification"]
        assert len(v["conflicts_found"]) > 0

    def test_dataset_1_detects_gaps(self, challenge):
        result = self._mock_call(challenge, DATASET_1, MOCK_SYNTHESIS_1)
        v = result["verification"]
        assert len(v["gaps_found"]) > 0

    def test_dataset_2_detects_deadline_conflict(self, challenge):
        result = self._mock_call(challenge, DATASET_2, MOCK_SYNTHESIS_2)
        v = result["verification"]
        assert any("deadline" in c.lower() for c in v["conflicts_found"])
