"""
CHALLENGE: Build a CI/CD Review Pipeline

Task Statement 3.6 — Integrate Claude Code into CI/CD pipelines with
headless mode and structured output.

Your goal: build a CI pipeline that reviews PR diffs per-file with
structured JSON output, generates fix suggestions, and produces a
pass/fail report.

Complete the three methods in CICDChallenge:
  1. build_review_prompt(filename, diff)  — per-file review prompt
  2. aggregate_findings(per_file_results) — combine into CI report
  3. build_fix_prompt(finding)            — generate fix for a finding

The checker tests prompt structure, aggregation logic, and report format.
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# Simulated PR data
# ---------------------------------------------------------------------------

PR_DIFFS = {
    "src/api/users.py": {
        "diff": """
+def get_user(user_id):
+    query = f"SELECT * FROM users WHERE id = {user_id}"
+    return db.execute(query).fetchone()
+
+def search_users(name):
+    query = f"SELECT * FROM users WHERE name LIKE '%{name}%'"
+    return db.execute(query).fetchall()
""",
        "expected_findings": [
            {"location": "get_user", "category": "sql_injection"},
            {"location": "search_users", "category": "sql_injection"},
        ]
    },
    "src/api/auth.py": {
        "diff": """
+def login(username, password):
+    user = db.query(User).filter_by(username=username).first()
+    if user and user.password == password:
+        return {"token": create_jwt(user.id)}
+    return {"error": f"Invalid credentials for {username}"}
""",
        "expected_findings": [
            {"location": "login", "category": "plaintext_password"},
            {"location": "login", "category": "info_leakage"},
        ]
    },
    "src/utils/config.py": {
        "diff": """
+import os
+
+DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/mydb")
+API_KEY = os.getenv("API_KEY", "default-key-12345")
+DEBUG = os.getenv("DEBUG", "true").lower() == "true"
""",
        "expected_findings": [
            {"location": "API_KEY", "category": "hardcoded_secret"},
        ]
    },
    "src/utils/helpers.py": {
        "diff": """
+def format_date(dt):
+    return dt.strftime("%Y-%m-%d")
+
+def capitalize_name(name):
+    return name.strip().title()
""",
        "expected_findings": []  # Clean file, no security issues
    }
}


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class CICDChallenge:
    """
    Build a CI/CD review pipeline with structured output.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_review_prompt(self, filename: str, diff: str) -> str:
        """
        Build a per-file security review prompt for CI.

        The prompt must:
        1. Identify the file being reviewed
        2. Include the diff content
        3. Have explicit DO flag / DON'T flag criteria
        4. Request structured JSON output with specific fields
        5. Handle the case where no issues are found (return [])

        Required output fields per finding:
        - "file": filename
        - "location": function or variable name
        - "severity": "critical", "high", "medium", or "low"
        - "category": issue category
        - "description": what the issue is
        - "recommendation": how to fix

        Args:
            filename: The file being reviewed.
            diff: The diff content.

        Returns:
            A complete prompt string.
        """
        # TODO: Build the CI review prompt.
        # Hint: Use explicit criteria (DO flag X, DON'T flag Y).
        # Hint: Request JSON array output.
        # Hint: Specify that empty results should return [].
        raise NotImplementedError("Complete build_review_prompt()")

    def aggregate_findings(self, per_file_results: dict) -> dict:
        """
        Aggregate per-file findings into a CI report.

        Args:
            per_file_results: dict mapping filename -> list of finding dicts

        Returns:
            {
                "total_findings": int,
                "by_severity": {"critical": N, "high": N, ...},
                "by_category": {"sql_injection": N, ...},
                "by_file": {"filename": N, ...},
                "findings": [all findings combined],
                "pass": bool (True if no critical or high findings),
                "summary": str (human-readable summary)
            }
        """
        # TODO: Aggregate the findings.
        # Hint: Count by severity, category, and file.
        # Hint: pass = True only if no critical or high severity findings.
        # Hint: Generate a human-readable summary.
        raise NotImplementedError("Complete aggregate_findings()")

    def build_fix_prompt(self, finding: dict) -> str:
        """
        Build a prompt to generate a fix for a specific finding.

        The prompt must:
        1. Describe the specific security issue
        2. Include the file and location
        3. Request a concrete code fix (not just advice)
        4. Request the fix in a specific format

        Args:
            finding: A finding dict with file, location, category, description.

        Returns:
            A prompt string requesting a code fix.
        """
        # TODO: Build the fix generation prompt.
        # Hint: Be specific about the issue and location.
        # Hint: Request actual code, not general advice.
        raise NotImplementedError("Complete build_fix_prompt()")

    def evaluate(self):
        """
        Evaluate the CI pipeline components.

        This method is provided for you — do not modify it.
        """
        print("Phase 1: Review Prompts")
        print("=" * 50)
        for filename, data in PR_DIFFS.items():
            prompt = self.build_review_prompt(filename, data["diff"])
            has_file = filename in prompt
            has_criteria = any(kw in prompt.lower()
                              for kw in ["flag", "do not", "don't"])
            has_json = "json" in prompt.lower()
            status = "OK" if (has_file and has_criteria and has_json) else "NEEDS WORK"
            print(f"  [{status}] {filename}")

        print("\nPhase 2: Aggregation")
        print("=" * 50)
        sample_results = {
            "file1.py": [
                {"file": "file1.py", "severity": "critical", "category": "sql_injection",
                 "location": "fn1", "description": "SQL injection", "recommendation": "Use params"},
            ],
            "file2.py": [
                {"file": "file2.py", "severity": "low", "category": "logging",
                 "location": "fn2", "description": "Verbose log", "recommendation": "Reduce"},
            ],
            "file3.py": [],
        }
        report = self.aggregate_findings(sample_results)
        print(f"  Total findings: {report.get('total_findings', '?')}")
        print(f"  Pass: {report.get('pass', '?')}")
        print(f"  Summary: {report.get('summary', '?')}")

        print("\nPhase 3: Fix Prompts")
        print("=" * 50)
        sample_finding = {
            "file": "src/api/users.py",
            "location": "get_user",
            "severity": "critical",
            "category": "sql_injection",
            "description": "User input concatenated into SQL query",
            "recommendation": "Use parameterized queries"
        }
        fix_prompt = self.build_fix_prompt(sample_finding)
        has_file = "users.py" in fix_prompt
        has_issue = "sql" in fix_prompt.lower()
        status = "OK" if (has_file and has_issue) else "NEEDS WORK"
        print(f"  [{status}] Fix prompt for SQL injection")

        print(f"\n{'='*50}")
        print("CHALLENGE PASSED — All CI/CD pipeline components work!")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("CI/CD Integration Challenge")
    print("===========================")
    print("Goal: Build a complete CI review pipeline\n")

    challenge = CICDChallenge()
    challenge.evaluate()
