"""
Checker for Unit 3.1 — CLAUDE.md Hierarchy Challenge

Validates the student's HierarchyChallenge implementation without
calling the Anthropic API. Tests hierarchy design, rule classification,
and validation logic.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    HierarchyChallenge,
    PROJECT_SPEC_1, PROJECT_SPEC_2, PROJECT_SPEC_3,
    ALL_SPECS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create a HierarchyChallenge instance (no API calls)."""
    return HierarchyChallenge()


# ---------------------------------------------------------------------------
# Test 1: Rule Classification
# ---------------------------------------------------------------------------

class TestRuleClassification:
    """Student's classify_rule must correctly identify the level."""

    def test_classify_personal_preference_editor(self, challenge):
        result = challenge.classify_rule("I prefer dark theme in editor")
        assert result == "user", (
            "Personal editor preferences should be user-level"
        )

    def test_classify_personal_preference_verbosity(self, challenge):
        result = challenge.classify_rule("Always explain your reasoning step by step")
        assert result == "user", (
            "Personal verbosity preferences should be user-level"
        )

    def test_classify_personal_preference_git(self, challenge):
        result = challenge.classify_rule("Show me git diff before committing")
        assert result == "user", (
            "Personal workflow preferences should be user-level"
        )

    def test_classify_team_standard_indentation(self, challenge):
        result = challenge.classify_rule("Use 4-space indentation")
        assert result == "project", (
            "Indentation standards are team-wide -> project-level"
        )

    def test_classify_team_standard_testing(self, challenge):
        result = challenge.classify_rule("Use pytest for all testing")
        assert result == "project", (
            "Testing standards are team-wide -> project-level"
        )

    def test_classify_team_standard_type_hints(self, challenge):
        result = challenge.classify_rule("All functions must have type hints")
        assert result == "project", (
            "Type hint requirement is team-wide -> project-level"
        )

    def test_classify_team_standard_database(self, challenge):
        result = challenge.classify_rule("Database is PostgreSQL, not MySQL")
        assert result == "project", (
            "Database choice is team-wide -> project-level"
        )

    def test_classify_directory_specific_framework(self, challenge):
        result = challenge.classify_rule(
            "Use FastAPI for all endpoints",
            context={"directory": "backend"}
        )
        assert result == "directory", (
            "Framework-specific rules are directory-level"
        )

    def test_classify_directory_specific_component(self, challenge):
        result = challenge.classify_rule(
            "React components use PascalCase",
            context={"directory": "frontend"}
        )
        assert result == "directory", (
            "Component naming for a specific area is directory-level"
        )


# ---------------------------------------------------------------------------
# Test 2: Hierarchy Design
# ---------------------------------------------------------------------------

class TestHierarchyDesign:
    """Student's design_hierarchy must produce a valid structure."""

    def test_returns_dict(self, challenge):
        result = challenge.design_hierarchy(PROJECT_SPEC_1)
        assert isinstance(result, dict), "design_hierarchy must return a dict"

    def test_has_three_levels(self, challenge):
        result = challenge.design_hierarchy(PROJECT_SPEC_1)
        assert "user_level" in result, "Hierarchy must have user_level"
        assert "project_level" in result, "Hierarchy must have project_level"
        assert "directory_level" in result, "Hierarchy must have directory_level"

    def test_user_level_not_shared(self, challenge):
        result = challenge.design_hierarchy(PROJECT_SPEC_1)
        user = result.get("user_level", {})
        assert user.get("shared_via_git") is False, (
            "User-level must NOT be shared via git"
        )

    def test_project_level_shared(self, challenge):
        result = challenge.design_hierarchy(PROJECT_SPEC_1)
        project = result.get("project_level", {})
        assert project.get("shared_via_git") is True, (
            "Project-level must be shared via git"
        )

    def test_personal_rules_in_user_level(self, challenge):
        result = challenge.design_hierarchy(PROJECT_SPEC_1)
        user_rules = result.get("user_level", {}).get("rules", [])
        # "I prefer dark theme" should be in user level
        has_personal = any("prefer" in r.lower() or "show me" in r.lower()
                          for r in user_rules)
        assert has_personal, (
            "Personal preferences must be in user-level"
        )

    def test_team_rules_in_project_level(self, challenge):
        result = challenge.design_hierarchy(PROJECT_SPEC_1)
        project_rules = result.get("project_level", {}).get("rules", [])
        has_team = any("indentation" in r.lower() or "type hint" in r.lower()
                       or "postgresql" in r.lower()
                       for r in project_rules)
        assert has_team, (
            "Team-wide standards must be in project-level"
        )

    def test_no_team_rules_in_user_level(self, challenge):
        result = challenge.design_hierarchy(PROJECT_SPEC_1)
        user_rules = result.get("user_level", {}).get("rules", [])
        team_keywords = ["indentation", "type hint", "fastapi", "postgresql",
                         "react", "terraform", "pytest"]
        for rule in user_rules:
            for kw in team_keywords:
                assert kw not in rule.lower(), (
                    f"Team rule '{rule}' should NOT be in user-level"
                )

    def test_directory_level_has_entries(self, challenge):
        result = challenge.design_hierarchy(PROJECT_SPEC_1)
        dirs = result.get("directory_level", {})
        assert len(dirs) > 0, (
            "Directory-level should have at least one entry"
        )

    def test_all_rules_placed(self, challenge):
        """Every rule from the spec must appear somewhere in the hierarchy."""
        result = challenge.design_hierarchy(PROJECT_SPEC_1)

        all_placed_rules = []
        all_placed_rules.extend(result.get("user_level", {}).get("rules", []))
        all_placed_rules.extend(result.get("project_level", {}).get("rules", []))
        for dir_config in result.get("directory_level", {}).values():
            all_placed_rules.extend(dir_config.get("rules", []))

        for rule_spec in PROJECT_SPEC_1["rules"]:
            assert rule_spec["rule"] in all_placed_rules, (
                f"Rule '{rule_spec['rule']}' is missing from the hierarchy"
            )


# ---------------------------------------------------------------------------
# Test 3: Validation Logic
# ---------------------------------------------------------------------------

class TestValidation:
    """Student's validate_hierarchy must catch common mistakes."""

    def test_valid_hierarchy_passes(self, challenge):
        good_hierarchy = {
            "user_level": {
                "path": "~/.claude/CLAUDE.md",
                "shared_via_git": False,
                "rules": ["I prefer dark theme"]
            },
            "project_level": {
                "path": ".claude/CLAUDE.md",
                "shared_via_git": True,
                "rules": ["Use 4-space indentation"],
                "imports": []
            },
            "directory_level": {
                "backend/CLAUDE.md": {
                    "path": "backend/CLAUDE.md",
                    "shared_via_git": True,
                    "rules": ["Use FastAPI"]
                }
            }
        }
        result = challenge.validate_hierarchy(good_hierarchy)
        assert result["valid"] is True, (
            "A correctly designed hierarchy should be valid"
        )

    def test_catches_team_rules_in_user_level(self, challenge):
        bad_hierarchy = {
            "user_level": {
                "path": "~/.claude/CLAUDE.md",
                "shared_via_git": False,
                "rules": ["Use 4-space indentation", "All functions must have type hints"]
            },
            "project_level": {
                "path": ".claude/CLAUDE.md",
                "shared_via_git": True,
                "rules": [],
                "imports": []
            },
            "directory_level": {}
        }
        result = challenge.validate_hierarchy(bad_hierarchy)
        assert result["valid"] is False or len(result.get("errors", [])) > 0, (
            "Should catch team rules placed in user-level"
        )

    def test_catches_unshared_project_level(self, challenge):
        bad_hierarchy = {
            "user_level": {
                "path": "~/.claude/CLAUDE.md",
                "shared_via_git": False,
                "rules": []
            },
            "project_level": {
                "path": ".claude/CLAUDE.md",
                "shared_via_git": False,  # Wrong!
                "rules": ["Use pytest"],
                "imports": []
            },
            "directory_level": {}
        }
        result = challenge.validate_hierarchy(bad_hierarchy)
        assert result["valid"] is False or len(result.get("errors", [])) > 0, (
            "Should catch project-level not shared via git"
        )

    def test_returns_correct_structure(self, challenge):
        hierarchy = challenge.design_hierarchy(PROJECT_SPEC_1)
        result = challenge.validate_hierarchy(hierarchy)
        assert "valid" in result, "Validation result must have 'valid' field"
        assert "errors" in result, "Validation result must have 'errors' field"
        assert "warnings" in result, "Validation result must have 'warnings' field"
        assert isinstance(result["errors"], list), "errors must be a list"
        assert isinstance(result["warnings"], list), "warnings must be a list"


# ---------------------------------------------------------------------------
# Test 4: Accuracy (all specs)
# ---------------------------------------------------------------------------

class TestAccuracy:
    """Student's hierarchy design must place rules correctly across all specs."""

    def test_spec1_accuracy(self, challenge):
        self._check_accuracy(challenge, PROJECT_SPEC_1, "E-Commerce Platform")

    def test_spec2_accuracy(self, challenge):
        self._check_accuracy(challenge, PROJECT_SPEC_2, "Data Pipeline")

    def test_spec3_accuracy(self, challenge):
        self._check_accuracy(challenge, PROJECT_SPEC_3, "API Gateway")

    def _check_accuracy(self, challenge, spec, name):
        hierarchy = challenge.design_hierarchy(spec)
        correct = 0
        total = len(spec["rules"])

        for rule_spec in spec["rules"]:
            rule_text = rule_spec["rule"]
            expected = rule_spec["correct_level"]

            actual = None
            if rule_text in hierarchy.get("user_level", {}).get("rules", []):
                actual = "user"
            elif rule_text in hierarchy.get("project_level", {}).get("rules", []):
                actual = "project"
            else:
                for dir_config in hierarchy.get("directory_level", {}).values():
                    if rule_text in dir_config.get("rules", []):
                        actual = "directory"
                        break

            if actual == expected:
                correct += 1

        accuracy = correct / total if total > 0 else 0
        assert accuracy == 1.0, (
            f"{name}: {correct}/{total} rules correctly placed ({accuracy:.0%}). "
            f"Must be 100%."
        )
