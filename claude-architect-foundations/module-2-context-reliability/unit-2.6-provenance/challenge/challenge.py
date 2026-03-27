"""
CHALLENGE: Build a Provenance-Tracked Multi-Source Synthesis System

Task Statement 5.6 — Implement provenance tracking and multi-source synthesis
with conflict detection and coverage gap reporting.

Your goal: build a synthesis system that maps every claim to its source, detects
conflicts between sources, and reports coverage gaps.

Complete the three methods in ProvenanceChallenge:
  1. build_synthesis_prompt(sources, query) — prompt with provenance tracking rules
  2. parse_synthesis(response_text) — parse the provenance-tracked synthesis
  3. verify_provenance(synthesis, expected) — check conflicts detected and gaps reported

The checker will test your system against multi-source datasets with known
conflicts and gaps.
"""

import json
import anthropic

# ---------------------------------------------------------------------------
# Test datasets with known conflicts and gaps
# ---------------------------------------------------------------------------

DATASET_1 = {
    "name": "company_profile",
    "sources": {
        "annual_report": {
            "source_name": "Acme Corp 2024 Annual Report",
            "source_date": "2024-03-15",
            "source_type": "official_filing",
            "data": {
                "revenue": "$4.2 billion",
                "employees": 15000,
                "headquarters": "San Francisco, CA",
                "ceo": "Jane Smith"
            }
        },
        "news_article": {
            "source_name": "TechCrunch Article",
            "source_date": "2024-12-01",
            "source_type": "news",
            "data": {
                "revenue": "$4.5 billion (projected)",
                "employees": 16200,
                "new_product": "AcmeAI Platform"
            }
        },
        "analyst_report": {
            "source_name": "Goldman Sachs Research",
            "source_date": "2024-09-20",
            "source_type": "analyst",
            "data": {
                "revenue": "$4.3 billion (estimated)",
                "market_cap": "$28 billion",
                "growth_rate": "18% YoY"
            }
        }
    },
    "query": "Provide a profile of Acme Corp: revenue, employee count, headquarters, CEO, market cap, ESG rating.",
    "expected": {
        "conflicts": ["revenue"],
        "gaps": ["ESG rating"],
        "single_source": ["headquarters", "ceo", "market_cap"]
    }
}

DATASET_2 = {
    "name": "regulatory_deadline",
    "sources": {
        "old_regulation": {
            "source_name": "Federal Register Vol 89, No 45",
            "source_date": "2024-03-01",
            "source_type": "government",
            "data": {
                "compliance_deadline": "September 1, 2025",
                "penalty_amount": "$50,000 per violation",
                "affected_entities": "All federally chartered banks"
            }
        },
        "amendment": {
            "source_name": "Federal Register Vol 89, No 198",
            "source_date": "2024-10-15",
            "source_type": "government",
            "data": {
                "compliance_deadline": "March 1, 2026",
                "penalty_amount": "$50,000 per violation",
                "additional_requirement": "Annual third-party audit"
            }
        },
        "industry_guide": {
            "source_name": "Banking Compliance Handbook 2024",
            "source_date": "2024-06-01",
            "source_type": "industry_publication",
            "data": {
                "compliance_deadline": "September 1, 2025",
                "implementation_cost": "$2-5 million per institution",
                "affected_entities": "All federally chartered banks"
            }
        }
    },
    "query": "What is the compliance deadline, penalty amount, affected entities, implementation cost, and required certifications?",
    "expected": {
        "conflicts": ["compliance_deadline"],
        "gaps": ["required certifications"],
        "single_source": ["implementation_cost", "additional_requirement"]
    }
}

DATASET_3 = {
    "name": "product_comparison",
    "sources": {
        "manufacturer_spec": {
            "source_name": "NovaChip X100 Datasheet",
            "source_date": "2024-08-01",
            "source_type": "manufacturer",
            "data": {
                "clock_speed": "4.8 GHz",
                "cores": 16,
                "tdp": "125W",
                "price": "$499"
            }
        },
        "review_site": {
            "source_name": "TechReviews.com Benchmark",
            "source_date": "2024-11-15",
            "source_type": "review",
            "data": {
                "clock_speed": "4.6 GHz (measured boost)",
                "benchmark_score": 42500,
                "tdp": "140W (measured under load)",
                "price": "$479 (street price)"
            }
        },
        "retailer": {
            "source_name": "MicroCenter Product Page",
            "source_date": "2024-12-05",
            "source_type": "retailer",
            "data": {
                "price": "$459 (holiday sale)",
                "availability": "In stock",
                "warranty": "3 years"
            }
        }
    },
    "query": "What are the specs for NovaChip X100: clock speed, cores, TDP, price, benchmark score, and power efficiency rating?",
    "expected": {
        "conflicts": ["clock_speed", "tdp", "price"],
        "gaps": ["power efficiency rating"],
        "single_source": ["cores", "benchmark_score", "warranty"]
    }
}

ALL_DATASETS = [DATASET_1, DATASET_2, DATASET_3]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class ProvenanceChallenge:
    """
    Build a provenance-tracked synthesis system that maps claims to sources,
    detects conflicts, and reports coverage gaps.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_synthesis_prompt(self, sources: dict, query: str) -> str:
        """
        Build a prompt that synthesizes with full provenance tracking.

        The prompt must:
        - Map every claim to its source(s) with date
        - Detect and report conflicts (same topic, different values)
        - Note temporal differences between sources
        - Report coverage gaps (topics in query but not in any source)
        - NOT fabricate data to fill gaps

        Args:
            sources: Dict of source data.
            query: The research query string.

        Returns:
            A complete prompt string ready to send to Claude.
        """
        # TODO: Write a provenance synthesis prompt.
        # Hint: Define explicit rules for conflict detection.
        # Hint: Tell the model to check each query topic against all sources.
        # Hint: Require coverage gap reporting for unfound topics.
        raise NotImplementedError("Complete build_synthesis_prompt()")

    def parse_synthesis(self, response_text: str) -> dict:
        """
        Parse the synthesis response into structured provenance data.

        The result must have:
          - "claims": list of {topic, value, sources, status}
          - "conflicts": list of {topic, values_by_source}
          - "coverage_gaps": list of str
          - "overall_confidence": str

        Args:
            response_text: The raw text response from Claude.

        Returns:
            A dict with structured provenance data.
        """
        # TODO: Parse the provenance synthesis response.
        # Hint: Use json.loads() if you requested JSON output.
        # Hint: Handle malformed responses gracefully.
        raise NotImplementedError("Complete parse_synthesis()")

    def verify_provenance(self, synthesis: dict, expected: dict) -> dict:
        """
        Verify that the synthesis correctly identified conflicts and gaps.

        Args:
            synthesis: The parsed synthesis result.
            expected: Dict with "conflicts", "gaps", "single_source" lists.

        Returns:
            A dict with:
              - "conflicts_found": list of detected conflict topics
              - "conflicts_missed": list of expected but undetected conflicts
              - "gaps_found": list of reported gaps
              - "gaps_missed": list of expected but unreported gaps
              - "score": float (0-1)
        """
        # TODO: Compare detected conflicts/gaps against expected.
        # Hint: Check if expected conflicts appear in synthesis conflicts.
        # Hint: Check if expected gaps appear in synthesis coverage_gaps.
        # Hint: Use case-insensitive matching for topic names.
        raise NotImplementedError("Complete verify_provenance()")

    def run_synthesis(self, dataset: dict) -> dict:
        """
        Run the provenance synthesis pipeline for a single dataset.

        This method is provided — do not modify it.
        """
        prompt = self.build_synthesis_prompt(dataset["sources"], dataset["query"])
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        synthesis = self.parse_synthesis(response.content[0].text)
        verification = self.verify_provenance(synthesis, dataset["expected"])
        return {"synthesis": synthesis, "verification": verification}

    def evaluate(self, datasets=None):
        """
        Evaluate provenance tracking across all test datasets.

        This method is provided — do not modify it.
        """
        if datasets is None:
            datasets = ALL_DATASETS

        total_score = 0

        for dataset in datasets:
            print(f"\n{'='*60}")
            print(f"Dataset: {dataset['name']}")
            print(f"{'='*60}")

            result = self.run_synthesis(dataset)
            v = result["verification"]

            print(f"  Conflicts found: {v['conflicts_found']}")
            print(f"  Conflicts missed: {v['conflicts_missed']}")
            print(f"  Gaps found: {v['gaps_found']}")
            print(f"  Gaps missed: {v['gaps_missed']}")
            print(f"  Score: {v['score']:.0%}")

            total_score += v["score"]

        avg_score = total_score / len(datasets)
        print(f"\n{'='*60}")
        print("OVERALL RESULTS")
        print(f"{'='*60}")
        print(f"  Average score: {avg_score:.0%}")

        if avg_score >= 0.80:
            print("\n  CHALLENGE PASSED — 80%+ provenance accuracy!")
        else:
            print(f"\n  NEEDS WORK — score below 80%.")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Provenance Tracking Challenge")
    print("================================")
    print("Goal: 80%+ conflict detection and gap reporting accuracy\n")

    challenge = ProvenanceChallenge()
    challenge.evaluate()
