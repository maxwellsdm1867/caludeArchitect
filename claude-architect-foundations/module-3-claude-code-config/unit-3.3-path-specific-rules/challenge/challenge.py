"""
CHALLENGE: Build a Path-Specific Rules Configuration System

Task Statement 3.3 — Write path-specific rules using .claude/rules/
with YAML frontmatter and glob patterns.

Your goal: design .claude/rules/ files that target the correct files
using glob patterns, avoiding the pitfalls of duplicated directory
CLAUDE.md files.

Complete the three methods in RulesChallenge:
  1. build_rules_config(project_files, requirements)  — return rules config
  2. match_files(pattern, file_list)                   — match glob patterns
  3. validate_coverage(rules, file_list, expected)     — validate precision/recall

The checker tests glob pattern accuracy, coverage, and conflict detection.
"""

import json
import fnmatch
import anthropic


# ---------------------------------------------------------------------------
# Project file trees with requirements
# ---------------------------------------------------------------------------

PROJECT_FILES = [
    "src/api/users.ts",
    "src/api/users.test.ts",
    "src/api/orders.ts",
    "src/api/orders.test.ts",
    "src/api/orders.spec.ts",
    "src/auth/login.ts",
    "src/auth/login.test.ts",
    "src/billing/invoice.ts",
    "src/billing/invoice.test.ts",
    "src/database/migrations/001_users.sql",
    "src/database/migrations/002_orders.sql",
    "src/database/seeds/users.sql",
    "src/database/seeds/orders.sql",
    "src/utils/helpers.ts",
    "src/utils/helpers.test.ts",
    "src/config/database.ts",
    "src/config/redis.ts",
    "package.json",
    "tsconfig.json",
    "README.md",
    ".github/workflows/ci.yml",
]

REQUIREMENTS = [
    {
        "name": "testing",
        "description": "All test files must follow testing standards",
        "target_patterns": ["**/*.test.ts", "**/*.spec.ts"],
        "expected_files": [
            "src/api/users.test.ts", "src/api/orders.test.ts",
            "src/api/orders.spec.ts", "src/auth/login.test.ts",
            "src/billing/invoice.test.ts", "src/utils/helpers.test.ts",
        ],
        "not_expected": [
            "src/api/users.ts", "src/auth/login.ts", "package.json",
        ],
    },
    {
        "name": "migrations",
        "description": "SQL migration files must follow strict schema rules",
        "target_patterns": ["**/migrations/**/*.sql"],
        "expected_files": [
            "src/database/migrations/001_users.sql",
            "src/database/migrations/002_orders.sql",
        ],
        "not_expected": [
            "src/database/seeds/users.sql", "src/database/seeds/orders.sql",
        ],
    },
    {
        "name": "seeds",
        "description": "SQL seed files follow relaxed data loading rules",
        "target_patterns": ["**/seeds/**/*.sql"],
        "expected_files": [
            "src/database/seeds/users.sql",
            "src/database/seeds/orders.sql",
        ],
        "not_expected": [
            "src/database/migrations/001_users.sql",
        ],
    },
    {
        "name": "ci-config",
        "description": "CI configuration files have change management rules",
        "target_patterns": [".github/**/*.yml"],
        "expected_files": [
            ".github/workflows/ci.yml",
        ],
        "not_expected": [
            "package.json", "tsconfig.json",
        ],
    },
]

ALL_DATA = (PROJECT_FILES, REQUIREMENTS)


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class RulesChallenge:
    """
    Build and validate .claude/rules/ configurations with glob patterns.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_rules_config(self, project_files: list, requirements: list) -> dict:
        """
        Build a .claude/rules/ configuration for the given requirements.

        The returned config must have this structure:
        {
            "rule_name.md": {
                "frontmatter": {
                    "paths": ["glob_pattern_1", "glob_pattern_2"]
                },
                "content": "markdown instructions for matched files"
            },
            ...
        }

        Requirements:
        - Each requirement should have its own rule file
        - Glob patterns must match expected files and exclude not_expected files
        - Content must have meaningful instructions (not empty)

        Args:
            project_files: List of file paths in the project.
            requirements: List of requirement dicts with target patterns.

        Returns:
            A dict mapping rule filenames to their configs.
        """
        # TODO: Build the rules configuration.
        # Hint: Use the target_patterns from each requirement.
        # Hint: Write meaningful content for each rule.
        raise NotImplementedError("Complete build_rules_config()")

    def match_files(self, pattern: str, file_list: list) -> list:
        """
        Match a glob pattern against a list of file paths.

        Must handle:
        - "**" for recursive directory matching
        - "*" for single-level matching
        - Exact filename matching

        Args:
            pattern: A glob pattern (e.g., "**/*.test.ts")
            file_list: List of file paths to match against.

        Returns:
            List of matching file paths.
        """
        # TODO: Implement glob matching.
        # Hint: "**" matches across directory boundaries.
        # Hint: "*" matches within a single directory level.
        # Hint: fnmatch can help, but you need to handle ** specially.
        raise NotImplementedError("Complete match_files()")

    def validate_coverage(self, rules: dict, file_list: list,
                          requirements: list) -> dict:
        """
        Validate that the rules config provides correct coverage.

        For each requirement, check:
        - Precision: of files matched by the rule's patterns, how many are expected?
        - Recall: of expected files, how many are matched by the rule's patterns?

        Args:
            rules: Rules config dict from build_rules_config.
            file_list: List of project files.
            requirements: List of requirement dicts.

        Returns:
            {
                "overall_precision": float (0-1),
                "overall_recall": float (0-1),
                "per_rule": [
                    {
                        "name": str,
                        "precision": float,
                        "recall": float,
                        "matched": [list of matched files],
                        "expected": [list of expected files]
                    }
                ]
            }
        """
        # TODO: Implement coverage validation.
        # Hint: For each rule, get its patterns from frontmatter.
        # Hint: Use match_files to find which project files match.
        # Hint: Compare matched files against expected files from requirements.
        raise NotImplementedError("Complete validate_coverage()")

    def evaluate(self, data=None):
        """
        Evaluate your rules configuration against all requirements.

        This method is provided for you — do not modify it.
        """
        if data is None:
            data = ALL_DATA

        project_files, requirements = data

        print("Building rules configuration...")
        rules = self.build_rules_config(project_files, requirements)
        print(f"Rules created: {len(rules)}")
        for name, config in rules.items():
            patterns = config.get("frontmatter", {}).get("paths", [])
            print(f"  {name}: {patterns}")

        print("\nValidating coverage...")
        coverage = self.validate_coverage(rules, project_files, requirements)

        print(f"\nOverall Precision: {coverage['overall_precision']:.0%}")
        print(f"Overall Recall: {coverage['overall_recall']:.0%}")

        for rule_result in coverage.get("per_rule", []):
            print(f"\n  {rule_result['name']}:")
            print(f"    Precision: {rule_result['precision']:.0%}")
            print(f"    Recall: {rule_result['recall']:.0%}")
            print(f"    Matched: {rule_result['matched']}")

        if (coverage['overall_precision'] == 1.0 and
                coverage['overall_recall'] == 1.0):
            print("\nCHALLENGE PASSED — 100% precision and recall!")
        else:
            if coverage['overall_precision'] < 1.0:
                print("\nNEEDS WORK: Some patterns match files they shouldn't.")
            if coverage['overall_recall'] < 1.0:
                print("NEEDS WORK: Some expected files are not matched.")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Path-Specific Rules Challenge")
    print("==============================")
    print("Goal: 100% precision, 100% recall on glob patterns\n")

    challenge = RulesChallenge()
    challenge.evaluate()
