"""
Checker for Unit 3.3 — Path-Specific Rules Challenge

Validates the student's RulesChallenge implementation without
calling the Anthropic API. Tests glob matching, rule construction,
and coverage validation.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    RulesChallenge,
    PROJECT_FILES, REQUIREMENTS, ALL_DATA,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create a RulesChallenge instance (no API calls)."""
    return RulesChallenge()


# ---------------------------------------------------------------------------
# Test 1: Glob Matching
# ---------------------------------------------------------------------------

class TestGlobMatching:
    """Student's match_files must correctly match glob patterns."""

    def test_double_star_test_files(self, challenge):
        matched = challenge.match_files("**/*.test.ts", PROJECT_FILES)
        expected = [f for f in PROJECT_FILES if f.endswith(".test.ts")]
        assert set(matched) == set(expected), (
            f"**/*.test.ts should match all .test.ts files. "
            f"Got {matched}, expected {expected}"
        )

    def test_double_star_spec_files(self, challenge):
        matched = challenge.match_files("**/*.spec.ts", PROJECT_FILES)
        expected = [f for f in PROJECT_FILES if f.endswith(".spec.ts")]
        assert set(matched) == set(expected), (
            f"**/*.spec.ts should match all .spec.ts files"
        )

    def test_migrations_pattern(self, challenge):
        matched = challenge.match_files("**/migrations/**/*.sql", PROJECT_FILES)
        expected = [f for f in PROJECT_FILES if "migrations/" in f and f.endswith(".sql")]
        assert set(matched) == set(expected), (
            f"**/migrations/**/*.sql should match only migration SQL files. "
            f"Got {matched}, expected {expected}"
        )

    def test_seeds_pattern(self, challenge):
        matched = challenge.match_files("**/seeds/**/*.sql", PROJECT_FILES)
        expected = [f for f in PROJECT_FILES if "seeds/" in f and f.endswith(".sql")]
        assert set(matched) == set(expected), (
            f"**/seeds/**/*.sql should match only seed SQL files"
        )

    def test_github_workflows(self, challenge):
        matched = challenge.match_files(".github/**/*.yml", PROJECT_FILES)
        expected = [f for f in PROJECT_FILES if f.startswith(".github/") and f.endswith(".yml")]
        assert set(matched) == set(expected), (
            f".github/**/*.yml should match CI config files"
        )

    def test_no_false_matches(self, challenge):
        """Migration pattern should NOT match seed files."""
        matched = challenge.match_files("**/migrations/**/*.sql", PROJECT_FILES)
        for f in matched:
            assert "seeds" not in f, (
                f"Migration pattern matched seed file: {f}"
            )

    def test_returns_list(self, challenge):
        result = challenge.match_files("**/*.ts", PROJECT_FILES)
        assert isinstance(result, list), "match_files must return a list"


# ---------------------------------------------------------------------------
# Test 2: Rules Configuration
# ---------------------------------------------------------------------------

class TestRulesConfig:
    """Student's build_rules_config must produce valid rule files."""

    def test_returns_dict(self, challenge):
        result = challenge.build_rules_config(PROJECT_FILES, REQUIREMENTS)
        assert isinstance(result, dict), "build_rules_config must return a dict"

    def test_has_rule_files(self, challenge):
        result = challenge.build_rules_config(PROJECT_FILES, REQUIREMENTS)
        assert len(result) >= len(REQUIREMENTS), (
            f"Should have at least {len(REQUIREMENTS)} rule files, got {len(result)}"
        )

    def test_rules_have_frontmatter(self, challenge):
        result = challenge.build_rules_config(PROJECT_FILES, REQUIREMENTS)
        for name, config in result.items():
            assert "frontmatter" in config, f"Rule '{name}' missing frontmatter"
            assert "paths" in config["frontmatter"], (
                f"Rule '{name}' frontmatter missing 'paths'"
            )
            assert isinstance(config["frontmatter"]["paths"], list), (
                f"Rule '{name}' paths must be a list"
            )
            assert len(config["frontmatter"]["paths"]) > 0, (
                f"Rule '{name}' has empty paths list"
            )

    def test_rules_have_content(self, challenge):
        result = challenge.build_rules_config(PROJECT_FILES, REQUIREMENTS)
        for name, config in result.items():
            content = config.get("content", "")
            assert len(content.strip()) > 10, (
                f"Rule '{name}' has insufficient content"
            )

    def test_testing_rule_has_test_patterns(self, challenge):
        result = challenge.build_rules_config(PROJECT_FILES, REQUIREMENTS)
        # Find the testing rule
        test_rule = None
        for name, config in result.items():
            patterns = config.get("frontmatter", {}).get("paths", [])
            for p in patterns:
                if ".test." in p or ".spec." in p:
                    test_rule = config
                    break
        assert test_rule is not None, (
            "Must have a rule targeting test files"
        )


# ---------------------------------------------------------------------------
# Test 3: Coverage Validation
# ---------------------------------------------------------------------------

class TestCoverageValidation:
    """Student's validate_coverage must correctly compute precision/recall."""

    def test_returns_correct_structure(self, challenge):
        rules = challenge.build_rules_config(PROJECT_FILES, REQUIREMENTS)
        result = challenge.validate_coverage(rules, PROJECT_FILES, REQUIREMENTS)
        assert "overall_precision" in result, "Must have overall_precision"
        assert "overall_recall" in result, "Must have overall_recall"
        assert "per_rule" in result, "Must have per_rule"

    def test_perfect_patterns_give_perfect_coverage(self, challenge):
        # Build with correct patterns from REQUIREMENTS
        perfect_rules = {}
        for req in REQUIREMENTS:
            perfect_rules[f"{req['name']}.md"] = {
                "frontmatter": {"paths": req["target_patterns"]},
                "content": f"Rules for {req['name']}"
            }

        result = challenge.validate_coverage(perfect_rules, PROJECT_FILES, REQUIREMENTS)
        assert result["overall_recall"] == 1.0, (
            "Perfect patterns should give 100% recall"
        )

    def test_precision_and_recall_are_floats(self, challenge):
        rules = challenge.build_rules_config(PROJECT_FILES, REQUIREMENTS)
        result = challenge.validate_coverage(rules, PROJECT_FILES, REQUIREMENTS)
        assert isinstance(result["overall_precision"], float), (
            "overall_precision must be a float"
        )
        assert isinstance(result["overall_recall"], float), (
            "overall_recall must be a float"
        )


# ---------------------------------------------------------------------------
# Test 4: End-to-End Accuracy
# ---------------------------------------------------------------------------

class TestAccuracy:
    """Full pipeline must achieve 100% precision and recall."""

    def test_full_pipeline_precision(self, challenge):
        rules = challenge.build_rules_config(PROJECT_FILES, REQUIREMENTS)
        result = challenge.validate_coverage(rules, PROJECT_FILES, REQUIREMENTS)
        assert result["overall_precision"] == 1.0, (
            f"Precision is {result['overall_precision']:.0%}, must be 100%. "
            f"Some patterns match files they shouldn't."
        )

    def test_full_pipeline_recall(self, challenge):
        rules = challenge.build_rules_config(PROJECT_FILES, REQUIREMENTS)
        result = challenge.validate_coverage(rules, PROJECT_FILES, REQUIREMENTS)
        assert result["overall_recall"] == 1.0, (
            f"Recall is {result['overall_recall']:.0%}, must be 100%. "
            f"Some expected files are not matched by any pattern."
        )

    def test_no_pattern_overlap_between_migrations_and_seeds(self, challenge):
        rules = challenge.build_rules_config(PROJECT_FILES, REQUIREMENTS)

        migration_matched = set()
        seed_matched = set()

        for name, config in rules.items():
            patterns = config.get("frontmatter", {}).get("paths", [])
            for p in patterns:
                if "migration" in p.lower():
                    migration_matched.update(challenge.match_files(p, PROJECT_FILES))
                elif "seed" in p.lower():
                    seed_matched.update(challenge.match_files(p, PROJECT_FILES))

        overlap = migration_matched & seed_matched
        assert len(overlap) == 0, (
            f"Migration and seed patterns should not overlap. "
            f"Both match: {overlap}"
        )
