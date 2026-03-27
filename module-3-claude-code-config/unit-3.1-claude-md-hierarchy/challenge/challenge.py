"""
CHALLENGE: Design a CLAUDE.md Hierarchy for a Multi-Team Project

Task Statement 3.1 — Configure Claude Code projects using CLAUDE.md
hierarchy, @import, rules, and memory.

Your goal: design a complete CLAUDE.md hierarchy that correctly places
rules at the appropriate level (user, project, directory) and uses
@import for modularity.

Complete the three methods in HierarchyChallenge:
  1. design_hierarchy(project_spec)  — return a hierarchy config dict
  2. classify_rule(rule, hierarchy)  — determine which level a rule belongs to
  3. validate_hierarchy(hierarchy)   — check for common mistakes

The checker will test your hierarchy against multiple project specs.
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# Project specifications with known correct placements
# ---------------------------------------------------------------------------

PROJECT_SPEC_1 = {
    "name": "E-Commerce Platform",
    "teams": ["backend", "frontend", "mobile", "infra"],
    "rules": [
        {"rule": "Use 4-space indentation", "correct_level": "project"},
        {"rule": "I prefer dark theme in editor", "correct_level": "user"},
        {"rule": "Use FastAPI for all endpoints", "correct_level": "directory", "directory": "backend"},
        {"rule": "React components use PascalCase", "correct_level": "directory", "directory": "frontend"},
        {"rule": "All functions must have type hints", "correct_level": "project"},
        {"rule": "Terraform files must have plan output before apply", "correct_level": "directory", "directory": "infra"},
        {"rule": "Show me git diff before committing", "correct_level": "user"},
        {"rule": "Database is PostgreSQL, not MySQL", "correct_level": "project"},
    ]
}

PROJECT_SPEC_2 = {
    "name": "Data Pipeline",
    "teams": ["ingestion", "processing", "analytics"],
    "rules": [
        {"rule": "Use pytest for all testing", "correct_level": "project"},
        {"rule": "I like verbose error messages", "correct_level": "user"},
        {"rule": "Ingestion jobs must have idempotency checks", "correct_level": "directory", "directory": "ingestion"},
        {"rule": "Processing uses Apache Spark", "correct_level": "directory", "directory": "processing"},
        {"rule": "Analytics dashboards use Plotly", "correct_level": "directory", "directory": "analytics"},
        {"rule": "All data schemas use Pydantic", "correct_level": "project"},
        {"rule": "Always explain your reasoning step by step", "correct_level": "user"},
    ]
}

PROJECT_SPEC_3 = {
    "name": "API Gateway",
    "teams": ["core", "auth", "rate-limiting"],
    "rules": [
        {"rule": "Use Go 1.22 standard library", "correct_level": "project"},
        {"rule": "Auth middleware must validate JWT signatures", "correct_level": "directory", "directory": "auth"},
        {"rule": "Rate limiter uses sliding window algorithm", "correct_level": "directory", "directory": "rate-limiting"},
        {"rule": "I prefer concise code comments", "correct_level": "user"},
        {"rule": "All handlers must return structured JSON errors", "correct_level": "project"},
        {"rule": "Core routing uses chi router", "correct_level": "directory", "directory": "core"},
    ]
}

ALL_SPECS = [PROJECT_SPEC_1, PROJECT_SPEC_2, PROJECT_SPEC_3]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class HierarchyChallenge:
    """
    Design and validate CLAUDE.md hierarchies for multi-team projects.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def design_hierarchy(self, project_spec: dict) -> dict:
        """
        Design a CLAUDE.md hierarchy for the given project specification.

        The returned hierarchy must have this structure:
        {
            "user_level": {
                "path": "~/.claude/CLAUDE.md",
                "shared_via_git": False,
                "rules": [list of rule strings]
            },
            "project_level": {
                "path": ".claude/CLAUDE.md",
                "shared_via_git": True,
                "rules": [list of rule strings],
                "imports": [list of @import file paths]
            },
            "directory_level": {
                "dirname/CLAUDE.md": {
                    "path": "dirname/CLAUDE.md",
                    "shared_via_git": True,
                    "rules": [list of rule strings]
                },
                ...
            }
        }

        Args:
            project_spec: dict with "name", "teams", and "rules" fields.

        Returns:
            A hierarchy config dict.
        """
        # TODO: Place each rule at the correct level.
        # Hint: Personal preferences -> user level
        # Hint: Team-wide standards -> project level
        # Hint: Team/directory-specific -> directory level
        # Hint: Consider using @import for modularity
        raise NotImplementedError("Complete design_hierarchy()")

    def classify_rule(self, rule_text: str, context: dict = None) -> str:
        """
        Classify a rule as belonging to "user", "project", or "directory" level.

        Classification criteria:
        - "user": Personal preferences (editor style, verbosity, display prefs)
        - "project": Team-wide standards (language, testing, coding style)
        - "directory": Package/module-specific (framework, tool, pattern for one area)

        Args:
            rule_text: The rule to classify.
            context: Optional dict with "directory" hint.

        Returns:
            "user", "project", or "directory"
        """
        # TODO: Implement rule classification logic.
        # Hint: Look for keywords that indicate personal vs team vs scoped rules.
        raise NotImplementedError("Complete classify_rule()")

    def validate_hierarchy(self, hierarchy: dict) -> dict:
        """
        Validate a CLAUDE.md hierarchy for common mistakes.

        Checks:
        1. User-level should NOT contain team rules
        2. Project-level must be shared via git
        3. Directory-level files must be shared via git
        4. No duplicate rules across levels
        5. Project-level should use @import if it has many rules

        Args:
            hierarchy: A hierarchy config dict.

        Returns:
            {
                "valid": bool,
                "errors": [list of error strings],
                "warnings": [list of warning strings]
            }
        """
        # TODO: Implement validation logic.
        # Hint: Check each of the 5 conditions above.
        raise NotImplementedError("Complete validate_hierarchy()")

    def evaluate(self, specs=None):
        """
        Evaluate your hierarchy design against all project specs.

        This method is provided for you — do not modify it.
        """
        if specs is None:
            specs = ALL_SPECS

        total_correct = 0
        total_rules = 0

        for i, spec in enumerate(specs, 1):
            print(f"\n{'='*60}")
            print(f"Project: {spec['name']}")
            print(f"{'='*60}")

            hierarchy = self.design_hierarchy(spec)
            validation = self.validate_hierarchy(hierarchy)

            print(f"  Valid: {validation['valid']}")
            if validation['errors']:
                print(f"  Errors: {validation['errors']}")
            if validation['warnings']:
                print(f"  Warnings: {validation['warnings']}")

            # Check rule placement
            for rule_spec in spec['rules']:
                total_rules += 1
                rule_text = rule_spec['rule']
                expected_level = rule_spec['correct_level']

                # Find where the rule was actually placed
                actual_level = None
                if rule_text in hierarchy.get('user_level', {}).get('rules', []):
                    actual_level = "user"
                elif rule_text in hierarchy.get('project_level', {}).get('rules', []):
                    actual_level = "project"
                else:
                    for dir_name, dir_config in hierarchy.get('directory_level', {}).items():
                        if rule_text in dir_config.get('rules', []):
                            actual_level = "directory"
                            break

                correct = actual_level == expected_level
                if correct:
                    total_correct += 1
                symbol = "[OK]" if correct else "[WRONG]"
                print(f"  {symbol} '{rule_text}' -> {actual_level} (expected: {expected_level})")

        accuracy = total_correct / total_rules if total_rules > 0 else 0
        print(f"\n{'='*60}")
        print(f"ACCURACY: {total_correct}/{total_rules} ({accuracy:.0%})")
        print(f"{'='*60}")

        if accuracy == 1.0:
            print("\nCHALLENGE PASSED — All rules placed at the correct level!")
        else:
            print(f"\nNEEDS WORK: {total_rules - total_correct} rule(s) misplaced.")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("CLAUDE.md Hierarchy Challenge")
    print("==============================")
    print("Goal: Place every rule at the correct hierarchy level\n")

    challenge = HierarchyChallenge()
    challenge.evaluate()
