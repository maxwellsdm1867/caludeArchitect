"""
CHALLENGE: Build a Command & Skill Configuration System

Task Statement 3.2 — Create reusable commands and skills for Claude Code
workflows with proper context isolation.

Your goal: design commands with $ARGUMENTS, organize them hierarchically,
and create skills with context: fork for independent review.

Complete the three methods in CommandSkillChallenge:
  1. build_command(name, purpose, needs_args)  — return a command config
  2. build_skill(name, purpose, needs_fork)    — return a skill config
  3. classify_workflow(workflow_desc)           — "command" or "skill"

The checker tests configuration structure, $ARGUMENTS usage, and
context isolation decisions.
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# Workflow scenarios with ground truth
# ---------------------------------------------------------------------------

WORKFLOWS = [
    {
        "description": "A simple code review that takes a file path and lists issues",
        "correct_type": "command",
        "needs_args": True,
        "needs_fork": False,
        "reason": "Simple prompt template with argument substitution"
    },
    {
        "description": "An independent security audit that must not be influenced by prior conversation about the code",
        "correct_type": "skill",
        "needs_args": True,
        "needs_fork": True,
        "reason": "Needs context isolation (context: fork) for unbiased review"
    },
    {
        "description": "Generate unit tests for a given file",
        "correct_type": "command",
        "needs_args": True,
        "needs_fork": False,
        "reason": "Simple template with file path argument"
    },
    {
        "description": "A deployment workflow that runs tests, builds, deploys, and verifies -- each step needs isolation from previous steps",
        "correct_type": "skill",
        "needs_args": False,
        "needs_fork": True,
        "reason": "Multi-step workflow needing context isolation between steps"
    },
    {
        "description": "Format a file according to team standards",
        "correct_type": "command",
        "needs_args": True,
        "needs_fork": False,
        "reason": "Simple formatting task with file argument"
    },
    {
        "description": "Code quality assessment that produces an unbiased report without being influenced by ongoing development discussion",
        "correct_type": "skill",
        "needs_args": True,
        "needs_fork": True,
        "reason": "Assessment must be independent of development context"
    },
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class CommandSkillChallenge:
    """
    Build command and skill configurations for Claude Code workflows.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_command(self, name: str, purpose: str, needs_args: bool) -> dict:
        """
        Build a Claude Code command configuration.

        The returned config must have:
        {
            "filename": "name.md" or "category/name.md",
            "location": ".claude/commands/",
            "content": "markdown template string",
            "invocation": "/project:name" or "/project:category:name",
            "has_arguments": bool
        }

        Requirements:
        - If needs_args is True, content must include $ARGUMENTS
        - Content must have clear, explicit instructions (not vague)
        - Location must be project-level (.claude/commands/)

        Args:
            name: Command name (e.g., "review", "test/unit")
            purpose: What the command does
            needs_args: Whether the command accepts arguments

        Returns:
            A command config dict.
        """
        # TODO: Build the command configuration.
        # Hint: Include $ARGUMENTS if needs_args is True.
        # Hint: Use explicit DO/DON'T criteria in the template.
        # Hint: Nested names (test/unit) become nested directories.
        raise NotImplementedError("Complete build_command()")

    def build_skill(self, name: str, purpose: str, needs_fork: bool) -> dict:
        """
        Build a Claude Code skill configuration.

        The returned config must have:
        {
            "directory": ".claude/skills/name/",
            "skill_md": {
                "frontmatter": {
                    "name": str,
                    "description": str,
                    "context": "fork" or "default"
                },
                "content": "markdown instructions"
            }
        }

        Requirements:
        - If needs_fork is True, frontmatter must have context: fork
        - SKILL.md must have all required frontmatter fields
        - Content must have detailed, structured instructions

        Args:
            name: Skill name (e.g., "security-audit")
            purpose: What the skill does
            needs_fork: Whether the skill needs context isolation

        Returns:
            A skill config dict.
        """
        # TODO: Build the skill configuration.
        # Hint: Set context: "fork" when needs_fork is True.
        # Hint: SKILL.md needs name, description, and context in frontmatter.
        raise NotImplementedError("Complete build_skill()")

    def classify_workflow(self, workflow_desc: str) -> str:
        """
        Classify a workflow as needing a "command" or "skill".

        Decision criteria:
        - Command: Simple prompt templates, argument substitution, no isolation needed
        - Skill: Complex workflows, needs context isolation, multi-step, independent review

        Args:
            workflow_desc: Description of the workflow.

        Returns:
            "command" or "skill"
        """
        # TODO: Classify the workflow.
        # Hint: Look for keywords indicating isolation needs.
        # Hint: "independent", "unbiased", "isolation" -> skill
        # Hint: "simple", "format", "generate" -> command
        raise NotImplementedError("Complete classify_workflow()")

    def evaluate(self, workflows=None):
        """
        Evaluate your implementations against all workflow scenarios.

        This method is provided for you — do not modify it.
        """
        if workflows is None:
            workflows = WORKFLOWS

        correct = 0
        total = len(workflows)

        for i, wf in enumerate(workflows, 1):
            print(f"\n{'='*60}")
            print(f"Workflow {i}: {wf['description'][:60]}...")
            print(f"{'='*60}")

            # Test classification
            predicted = self.classify_workflow(wf['description'])
            expected = wf['correct_type']
            match = predicted == expected
            if match:
                correct += 1
            symbol = "[OK]" if match else "[WRONG]"
            print(f"  {symbol} Type: {predicted} (expected: {expected})")

            # Test building the correct config
            if expected == "command":
                config = self.build_command(
                    name=f"workflow-{i}",
                    purpose=wf['description'],
                    needs_args=wf['needs_args']
                )
                print(f"  Command: {config.get('invocation', '?')}")
                print(f"  Has $ARGUMENTS: {config.get('has_arguments', False)}")
            else:
                config = self.build_skill(
                    name=f"workflow-{i}",
                    purpose=wf['description'],
                    needs_fork=wf['needs_fork']
                )
                context = config.get('skill_md', {}).get('frontmatter', {}).get('context', '?')
                print(f"  Skill: {config.get('directory', '?')}")
                print(f"  Context: {context}")

        accuracy = correct / total if total > 0 else 0
        print(f"\n{'='*60}")
        print(f"CLASSIFICATION ACCURACY: {correct}/{total} ({accuracy:.0%})")
        print(f"{'='*60}")

        if accuracy == 1.0:
            print("\nCHALLENGE PASSED — All workflows correctly classified and configured!")
        else:
            print(f"\nNEEDS WORK: {total - correct} workflow(s) misclassified.")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Command & Skill Configuration Challenge")
    print("========================================")
    print("Goal: Correctly classify and configure all workflows\n")

    challenge = CommandSkillChallenge()
    challenge.evaluate()
