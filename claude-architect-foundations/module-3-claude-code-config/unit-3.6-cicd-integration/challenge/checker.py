"""
Checker for Unit 3.6 — CI/CD Integration Challenge

Validates the student's CICDChallenge implementation without
calling the Anthropic API. Tests review prompt structure, aggregation
logic, and fix prompt generation.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    CICDChallenge,
    PR_DIFFS,
)


@pytest.fixture
def challenge():
    return CICDChallenge()


# ---------------------------------------------------------------------------
# Sample data for testing
# ---------------------------------------------------------------------------

SAMPLE_FINDINGS = {
    "src/api/users.py": [
        {"file": "src/api/users.py", "location": "get_user",
         "severity": "critical", "category": "sql_injection",
         "description": "SQL injection via f-string",
         "recommendation": "Use parameterized queries"},
        {"file": "src/api/users.py", "location": "search_users",
         "severity": "critical", "category": "sql_injection",
         "description": "SQL injection via f-string in LIKE",
         "recommendation": "Use parameterized queries"},
    ],
    "src/api/auth.py": [
        {"file": "src/api/auth.py", "location": "login",
         "severity": "critical", "category": "plaintext_password",
         "description": "Plain text password comparison",
         "recommendation": "Use bcrypt or argon2"},
        {"file": "src/api/auth.py", "location": "login",
         "severity": "medium", "category": "info_leakage",
         "description": "Username in error message",
         "recommendation": "Use generic error message"},
    ],
    "src/utils/helpers.py": [],
}


class TestReviewPrompt:
    """Student's build_review_prompt must produce CI-ready prompts."""

    def test_returns_string(self, challenge):
        result = challenge.build_review_prompt("test.py", "+ x = 1")
        assert isinstance(result, str), "Must return a string"

    def test_includes_filename(self, challenge):
        result = challenge.build_review_prompt("src/api/users.py", "+ code")
        assert "src/api/users.py" in result or "users.py" in result, (
            "Prompt must include the filename"
        )

    def test_includes_diff(self, challenge):
        diff = "+ query = f'SELECT * FROM users WHERE id = {user_id}'"
        result = challenge.build_review_prompt("test.py", diff)
        assert "SELECT" in result, "Prompt must include the diff content"

    def test_has_explicit_criteria(self, challenge):
        result = challenge.build_review_prompt("test.py", "+ code").lower()
        has_criteria = any(kw in result for kw in [
            "flag", "do not flag", "don't flag", "do not report",
            "criteria", "only when"
        ])
        assert has_criteria, (
            "Prompt must have explicit DO/DON'T criteria"
        )

    def test_requests_json_output(self, challenge):
        result = challenge.build_review_prompt("test.py", "+ code").lower()
        assert "json" in result, "Prompt must request JSON output"

    def test_specifies_empty_result(self, challenge):
        result = challenge.build_review_prompt("test.py", "+ code")
        assert "[]" in result, (
            "Prompt must specify returning [] when no issues found"
        )

    def test_specifies_required_fields(self, challenge):
        result = challenge.build_review_prompt("test.py", "+ code").lower()
        required_fields = ["file", "severity", "description"]
        for field in required_fields:
            assert field in result, (
                f"Prompt must specify '{field}' as a required output field"
            )


class TestAggregation:
    """Student's aggregate_findings must produce valid CI reports."""

    def test_returns_dict(self, challenge):
        result = challenge.aggregate_findings(SAMPLE_FINDINGS)
        assert isinstance(result, dict), "Must return a dict"

    def test_has_required_fields(self, challenge):
        result = challenge.aggregate_findings(SAMPLE_FINDINGS)
        required = ["total_findings", "by_severity", "findings", "pass"]
        for field in required:
            assert field in result, f"Report missing '{field}'"

    def test_correct_total(self, challenge):
        result = challenge.aggregate_findings(SAMPLE_FINDINGS)
        expected_total = sum(len(findings) for findings in SAMPLE_FINDINGS.values())
        assert result["total_findings"] == expected_total, (
            f"Total should be {expected_total}, got {result['total_findings']}"
        )

    def test_fail_on_critical(self, challenge):
        result = challenge.aggregate_findings(SAMPLE_FINDINGS)
        assert result["pass"] is False, (
            "Should fail when critical findings exist"
        )

    def test_pass_on_clean(self, challenge):
        clean = {"file1.py": [], "file2.py": []}
        result = challenge.aggregate_findings(clean)
        assert result["pass"] is True, (
            "Should pass when no findings exist"
        )

    def test_pass_on_low_severity_only(self, challenge):
        low_only = {
            "file1.py": [
                {"file": "file1.py", "severity": "low", "category": "style",
                 "location": "fn", "description": "Minor", "recommendation": "Fix"}
            ]
        }
        result = challenge.aggregate_findings(low_only)
        assert result["pass"] is True, (
            "Should pass when only low-severity findings exist"
        )

    def test_fail_on_high_severity(self, challenge):
        high_severity = {
            "file1.py": [
                {"file": "file1.py", "severity": "high", "category": "auth",
                 "location": "fn", "description": "Auth bypass",
                 "recommendation": "Fix"}
            ]
        }
        result = challenge.aggregate_findings(high_severity)
        assert result["pass"] is False, (
            "Should fail when high-severity findings exist"
        )

    def test_severity_counts(self, challenge):
        result = challenge.aggregate_findings(SAMPLE_FINDINGS)
        by_severity = result.get("by_severity", {})
        assert by_severity.get("critical", 0) >= 3, (
            "Should count critical findings correctly"
        )

    def test_has_summary(self, challenge):
        result = challenge.aggregate_findings(SAMPLE_FINDINGS)
        summary = result.get("summary", "")
        assert isinstance(summary, str) and len(summary) > 0, (
            "Report must have a non-empty summary string"
        )


class TestFixPrompt:
    """Student's build_fix_prompt must produce actionable fix requests."""

    def test_returns_string(self, challenge):
        finding = {"file": "test.py", "location": "fn",
                    "severity": "critical", "category": "sql_injection",
                    "description": "SQL injection", "recommendation": "Use params"}
        result = challenge.build_fix_prompt(finding)
        assert isinstance(result, str), "Must return a string"

    def test_includes_file(self, challenge):
        finding = {"file": "src/api/users.py", "location": "get_user",
                    "severity": "critical", "category": "sql_injection",
                    "description": "SQL injection", "recommendation": "Use params"}
        result = challenge.build_fix_prompt(finding)
        assert "users.py" in result, "Fix prompt must reference the file"

    def test_includes_issue_description(self, challenge):
        finding = {"file": "test.py", "location": "get_user",
                    "severity": "critical", "category": "sql_injection",
                    "description": "User input concatenated into SQL",
                    "recommendation": "Use parameterized queries"}
        result = challenge.build_fix_prompt(finding).lower()
        assert "sql" in result, "Fix prompt must describe the issue"

    def test_requests_code_not_advice(self, challenge):
        finding = {"file": "test.py", "location": "fn",
                    "severity": "critical", "category": "sql_injection",
                    "description": "SQL injection", "recommendation": "Use params"}
        result = challenge.build_fix_prompt(finding).lower()
        code_keywords = ["code", "function", "fix", "replace", "implementation",
                         "corrected", "updated", "patched"]
        has_code_request = any(kw in result for kw in code_keywords)
        assert has_code_request, (
            "Fix prompt must request actual code, not just advice"
        )


class TestEndToEnd:
    """Full pipeline integration test."""

    def test_pipeline_produces_failing_report(self, challenge):
        """Review + aggregate for our sample PR should produce a failing report."""
        # Build prompts for all files
        for filename, data in PR_DIFFS.items():
            prompt = challenge.build_review_prompt(filename, data["diff"])
            assert isinstance(prompt, str) and len(prompt) > 50

        # Test aggregation with sample data
        report = challenge.aggregate_findings(SAMPLE_FINDINGS)
        assert report["pass"] is False, "Report should fail with critical findings"
        assert report["total_findings"] > 0, "Should have findings"
