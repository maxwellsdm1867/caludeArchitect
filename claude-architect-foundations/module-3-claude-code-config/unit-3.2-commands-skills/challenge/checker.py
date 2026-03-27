"""
Checker for Unit 3.2 — Commands & Skills Challenge

Validates the student's CommandSkillChallenge implementation without
calling the Anthropic API. Tests command construction, skill construction,
and workflow classification logic.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    CommandSkillChallenge,
    WORKFLOWS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create a CommandSkillChallenge instance (no API calls)."""
    return CommandSkillChallenge()


# ---------------------------------------------------------------------------
# Test 1: Command Construction
# ---------------------------------------------------------------------------

class TestCommandConstruction:
    """Student's build_command must produce valid command configs."""

    def test_command_returns_dict(self, challenge):
        result = challenge.build_command("review", "Review code", True)
        assert isinstance(result, dict), "build_command must return a dict"

    def test_command_has_required_fields(self, challenge):
        result = challenge.build_command("review", "Review code", True)
        required = ["filename", "location", "content", "invocation"]
        for field in required:
            assert field in result, f"Command config missing '{field}'"

    def test_command_has_arguments_when_needed(self, challenge):
        result = challenge.build_command("review", "Review code", True)
        assert "$ARGUMENTS" in result.get("content", ""), (
            "Command with needs_args=True must include $ARGUMENTS in content"
        )

    def test_command_no_arguments_when_not_needed(self, challenge):
        result = challenge.build_command("deploy", "Deploy to staging", False)
        # Not strictly required to exclude $ARGUMENTS, but has_arguments should be False
        assert result.get("has_arguments") is False, (
            "Command with needs_args=False should have has_arguments=False"
        )

    def test_command_project_level_location(self, challenge):
        result = challenge.build_command("review", "Review code", True)
        location = result.get("location", "")
        assert ".claude/commands" in location, (
            "Commands must be in .claude/commands/ (project-level)"
        )
        assert "~" not in location, (
            "Commands should NOT be in user-level (~/.claude/commands/)"
        )

    def test_command_content_not_vague(self, challenge):
        result = challenge.build_command("review", "Review code for issues", True)
        content = result.get("content", "").lower()
        vague_phrases = ["be thorough", "use your judgment", "be careful"]
        for phrase in vague_phrases:
            assert phrase not in content, (
                f"Command content should not use vague phrase: '{phrase}'"
            )

    def test_nested_command_invocation(self, challenge):
        result = challenge.build_command("test/unit", "Run unit tests", True)
        invocation = result.get("invocation", "")
        assert "test" in invocation and "unit" in invocation, (
            "Nested command name should produce nested invocation"
        )


# ---------------------------------------------------------------------------
# Test 2: Skill Construction
# ---------------------------------------------------------------------------

class TestSkillConstruction:
    """Student's build_skill must produce valid skill configs."""

    def test_skill_returns_dict(self, challenge):
        result = challenge.build_skill("security-audit", "Audit code", True)
        assert isinstance(result, dict), "build_skill must return a dict"

    def test_skill_has_frontmatter(self, challenge):
        result = challenge.build_skill("security-audit", "Audit code", True)
        skill_md = result.get("skill_md", {})
        assert "frontmatter" in skill_md, "Skill must have frontmatter"
        fm = skill_md["frontmatter"]
        assert "name" in fm, "Frontmatter must have 'name'"
        assert "description" in fm, "Frontmatter must have 'description'"
        assert "context" in fm, "Frontmatter must have 'context'"

    def test_skill_fork_when_needed(self, challenge):
        result = challenge.build_skill("security-audit", "Independent review", True)
        context = result.get("skill_md", {}).get("frontmatter", {}).get("context")
        assert context == "fork", (
            "Skill with needs_fork=True must have context: fork"
        )

    def test_skill_no_fork_when_not_needed(self, challenge):
        result = challenge.build_skill("helper", "Simple helper", False)
        context = result.get("skill_md", {}).get("frontmatter", {}).get("context")
        assert context != "fork", (
            "Skill with needs_fork=False should NOT have context: fork"
        )

    def test_skill_has_content(self, challenge):
        result = challenge.build_skill("security-audit", "Audit code", True)
        content = result.get("skill_md", {}).get("content", "")
        assert len(content) > 20, (
            "Skill content should have meaningful instructions"
        )

    def test_skill_directory_path(self, challenge):
        result = challenge.build_skill("security-audit", "Audit code", True)
        directory = result.get("directory", "")
        assert ".claude/skills" in directory, (
            "Skills must be in .claude/skills/"
        )


# ---------------------------------------------------------------------------
# Test 3: Workflow Classification
# ---------------------------------------------------------------------------

class TestClassification:
    """Student's classify_workflow must correctly classify workflows."""

    def test_simple_review_is_command(self, challenge):
        result = challenge.classify_workflow(
            "A simple code review that takes a file path and lists issues"
        )
        assert result == "command", (
            "Simple code review is a command"
        )

    def test_independent_audit_is_skill(self, challenge):
        result = challenge.classify_workflow(
            "An independent security audit that must not be influenced by prior conversation"
        )
        assert result == "skill", (
            "Independent audit needing isolation is a skill"
        )

    def test_test_generation_is_command(self, challenge):
        result = challenge.classify_workflow(
            "Generate unit tests for a given file"
        )
        assert result == "command", (
            "Simple test generation is a command"
        )

    def test_multi_step_deployment_is_skill(self, challenge):
        result = challenge.classify_workflow(
            "A deployment workflow with multiple steps needing isolation"
        )
        assert result == "skill", (
            "Multi-step workflow needing isolation is a skill"
        )

    def test_formatting_is_command(self, challenge):
        result = challenge.classify_workflow(
            "Format a file according to team standards"
        )
        assert result == "command", (
            "Simple formatting is a command"
        )

    def test_unbiased_assessment_is_skill(self, challenge):
        result = challenge.classify_workflow(
            "Code quality assessment that produces an unbiased report"
        )
        assert result == "skill", (
            "Unbiased assessment needing isolation is a skill"
        )


# ---------------------------------------------------------------------------
# Test 4: Full Pipeline
# ---------------------------------------------------------------------------

class TestFullPipeline:
    """End-to-end tests for building configs based on classification."""

    def test_command_workflow_produces_valid_command(self, challenge):
        wf = WORKFLOWS[0]  # Simple code review
        wf_type = challenge.classify_workflow(wf["description"])
        assert wf_type == "command"

        config = challenge.build_command("review", wf["description"], wf["needs_args"])
        assert "$ARGUMENTS" in config.get("content", ""), (
            "Review command should have $ARGUMENTS"
        )

    def test_skill_workflow_produces_forked_skill(self, challenge):
        wf = WORKFLOWS[1]  # Independent security audit
        wf_type = challenge.classify_workflow(wf["description"])
        assert wf_type == "skill"

        config = challenge.build_skill("security-audit", wf["description"], wf["needs_fork"])
        context = config.get("skill_md", {}).get("frontmatter", {}).get("context")
        assert context == "fork", (
            "Security audit skill must have context: fork"
        )

    def test_all_workflows_classified_correctly(self, challenge):
        correct = 0
        for wf in WORKFLOWS:
            predicted = challenge.classify_workflow(wf["description"])
            if predicted == wf["correct_type"]:
                correct += 1

        accuracy = correct / len(WORKFLOWS)
        assert accuracy == 1.0, (
            f"Classification accuracy: {accuracy:.0%} ({correct}/{len(WORKFLOWS)}). "
            f"Must be 100%."
        )
