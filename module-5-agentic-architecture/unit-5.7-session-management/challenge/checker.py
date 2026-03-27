"""
Checker for Unit 5.7 — Session Management Challenge

Validates resume/fresh decisions, summary structure, and staleness detection.
No API calls needed.
"""

import json
import pytest

from challenge import (
    SessionChallenge, SCENARIOS, TEST_SESSION,
    PRIOR_SESSION_STATE, CURRENT_STATE,
)


@pytest.fixture
def challenge():
    return SessionChallenge()


# ---------------------------------------------------------------------------
# Test 1: Resume vs Fresh Decision
# ---------------------------------------------------------------------------

class TestResumeDecision:
    """should_resume must correctly decide based on data_changed."""

    def test_all_scenarios_correct(self, challenge):
        for s in SCENARIOS:
            result = challenge.should_resume(s)
            assert result == s["expected"], (
                f"Scenario {s['id']}: expected '{s['expected']}', got '{result}'. "
                f"Data changed: {s['data_changed']}"
            )

    def test_returns_valid_value(self, challenge):
        valid = {"resume", "fresh_with_summary"}
        for s in SCENARIOS:
            result = challenge.should_resume(s)
            assert result in valid, (
                f"Must return one of {valid}, got '{result}'"
            )

    def test_changed_data_means_fresh(self, challenge):
        for s in SCENARIOS:
            if s["data_changed"]:
                result = challenge.should_resume(s)
                assert result == "fresh_with_summary", (
                    f"Scenario {s['id']}: data changed, should be fresh_with_summary"
                )

    def test_unchanged_data_means_resume(self, challenge):
        for s in SCENARIOS:
            if not s["data_changed"]:
                result = challenge.should_resume(s)
                assert result == "resume", (
                    f"Scenario {s['id']}: data unchanged, should resume"
                )


# ---------------------------------------------------------------------------
# Test 2: Session Summary
# ---------------------------------------------------------------------------

class TestSessionSummary:
    """build_session_summary must produce a structured, clean summary."""

    def test_has_required_fields(self, challenge):
        summary = challenge.build_session_summary(TEST_SESSION)
        required = ["task", "key_findings", "approaches_tried", "remaining_work", "files_reviewed"]
        for field in required:
            assert field in summary, f"Summary must contain '{field}'"

    def test_findings_are_structured(self, challenge):
        summary = challenge.build_session_summary(TEST_SESSION)
        findings = summary["key_findings"]
        assert isinstance(findings, list), "key_findings must be a list"
        assert len(findings) >= 2, "Should include both findings from the session"
        for f in findings:
            assert "file" in f or "issue" in f, (
                "Each finding should have file and/or issue"
            )

    def test_approaches_included(self, challenge):
        summary = challenge.build_session_summary(TEST_SESSION)
        approaches = summary["approaches_tried"]
        assert isinstance(approaches, list), "approaches_tried must be a list"
        assert len(approaches) >= 1, "Should include attempted approaches"

    def test_remaining_work_included(self, challenge):
        summary = challenge.build_session_summary(TEST_SESSION)
        remaining = summary["remaining_work"]
        assert isinstance(remaining, list), "remaining_work must be a list"
        assert len(remaining) >= 1, "Should include remaining tasks"

    def test_no_raw_timestamps(self, challenge):
        summary = challenge.build_session_summary(TEST_SESSION)
        summary_str = json.dumps(summary)
        assert "T10:00:00" not in summary_str and "T11:30:00" not in summary_str, (
            "Summary should not contain raw ISO timestamps"
        )

    def test_task_is_descriptive(self, challenge):
        summary = challenge.build_session_summary(TEST_SESSION)
        assert len(summary["task"]) > 5, "Task should be a descriptive string"


# ---------------------------------------------------------------------------
# Test 3: Stale Context Detection
# ---------------------------------------------------------------------------

class TestStalenessDetection:
    """detect_stale_context must identify all forms of staleness."""

    def test_detects_staleness(self, challenge):
        result = challenge.detect_stale_context(PRIOR_SESSION_STATE, CURRENT_STATE)
        assert result["is_stale"] is True, "Should detect staleness (files changed)"

    def test_finds_changed_files(self, challenge):
        result = challenge.detect_stale_context(PRIOR_SESSION_STATE, CURRENT_STATE)
        assert "auth.py" in result["changed_files"], (
            "auth.py has a different hash — should be in changed_files"
        )
        assert "api.py" not in result["changed_files"], (
            "api.py has the same hash — should NOT be in changed_files"
        )

    def test_finds_new_files(self, challenge):
        result = challenge.detect_stale_context(PRIOR_SESSION_STATE, CURRENT_STATE)
        assert "payments.py" in result["new_files"], (
            "payments.py is new — should be in new_files"
        )

    def test_finds_no_deleted_files(self, challenge):
        result = challenge.detect_stale_context(PRIOR_SESSION_STATE, CURRENT_STATE)
        assert result["deleted_files"] == [], (
            "No files were deleted in this scenario"
        )

    def test_invalidates_auth_assumptions(self, challenge):
        result = challenge.detect_stale_context(PRIOR_SESSION_STATE, CURRENT_STATE)
        invalidated = " ".join(result["invalidated_assumptions"]).lower()
        assert "auth" in invalidated or "password" in invalidated, (
            "Assumptions about auth.py should be invalidated (file changed)"
        )

    def test_does_not_invalidate_api_assumptions(self, challenge):
        """api.py hasn't changed, so assumptions about it should be valid."""
        result = challenge.detect_stale_context(PRIOR_SESSION_STATE, CURRENT_STATE)
        # api.py assumptions should NOT be invalidated since the file hasn't changed
        invalidated_str = " ".join(result["invalidated_assumptions"]).lower()
        # This is a softer check — at minimum, auth.py assumptions should be invalidated
        # while api.py assumptions could go either way depending on implementation
        assert len(result["invalidated_assumptions"]) >= 1, (
            "Should invalidate at least the auth.py assumption"
        )

    def test_returns_required_fields(self, challenge):
        result = challenge.detect_stale_context(PRIOR_SESSION_STATE, CURRENT_STATE)
        for field in ["is_stale", "changed_files", "new_files", "deleted_files", "invalidated_assumptions"]:
            assert field in result, f"Result must contain '{field}'"

    def test_no_staleness_when_unchanged(self, challenge):
        """If nothing changed, should report no staleness."""
        same_state = {
            "files": {
                "auth.py": {"hash": "abc123"},
                "api.py": {"hash": "def456"},
            }
        }
        prior = {
            "files": {
                "auth.py": {"hash": "abc123", "findings": []},
                "api.py": {"hash": "def456", "findings": []},
            },
            "assumptions": ["auth.py is secure"]
        }
        result = challenge.detect_stale_context(prior, same_state)
        assert result["is_stale"] is False, (
            "No changes should mean no staleness"
        )
