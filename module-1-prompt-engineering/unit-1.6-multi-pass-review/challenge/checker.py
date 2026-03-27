"""
Checker for Unit 1.6 — Multi-Pass Review Challenge
====================================================
Run with: python checker.py
    or:   pytest checker.py -v
"""

import pytest
from challenge import (
    MultiPassChallenge,
    SAMPLE_CONTEXTS,
    SAMPLE_FILES,
    SAMPLE_INTEGRATION_FINDINGS,
    SAMPLE_LOCAL_FINDINGS,
    SAMPLE_LOCAL_REVIEW_OUTPUTS,
)


@pytest.fixture
def challenge():
    return MultiPassChallenge()


# ── 1. should_use_independent_review ──────────────────────────────────────


class TestShouldUseIndependentReview:
    """Tests for the independent review decision logic."""

    def test_generated_in_session_always_independent(self, challenge):
        """Code generated in the current session must use independent review."""
        ctx = {"generated_in_session": True, "file_count": 1, "is_critical": False}
        assert challenge.should_use_independent_review(ctx) is True

    def test_critical_code_always_independent(self, challenge):
        """Critical code must always use independent review."""
        ctx = {"generated_in_session": False, "file_count": 1, "is_critical": True}
        assert challenge.should_use_independent_review(ctx) is True

    def test_large_pr_uses_independent(self, challenge):
        """PRs with more than 3 files should use independent review."""
        ctx = {"generated_in_session": False, "file_count": 8, "is_critical": False}
        assert challenge.should_use_independent_review(ctx) is True

    def test_small_non_critical_non_generated_is_same_session(self, challenge):
        """Small, non-critical, externally-written code can use same-session."""
        ctx = {"generated_in_session": False, "file_count": 2, "is_critical": False}
        assert challenge.should_use_independent_review(ctx) is False

    def test_exactly_three_files_is_same_session(self, challenge):
        """Exactly 3 files (not > 3) does not trigger the file count rule."""
        ctx = {"generated_in_session": False, "file_count": 3, "is_critical": False}
        assert challenge.should_use_independent_review(ctx) is False

    def test_four_files_uses_independent(self, challenge):
        """4 files (> 3) triggers the file count rule."""
        ctx = {"generated_in_session": False, "file_count": 4, "is_critical": False}
        assert challenge.should_use_independent_review(ctx) is True

    def test_returns_bool(self, challenge):
        """Return value must be a boolean."""
        result = challenge.should_use_independent_review(SAMPLE_CONTEXTS[0])
        assert isinstance(result, bool)

    def test_all_sample_contexts(self, challenge):
        """Verify expected results for all sample contexts."""
        expected = [True, False, True, True, True]
        for ctx, exp in zip(SAMPLE_CONTEXTS, expected):
            result = challenge.should_use_independent_review(ctx)
            assert result == exp, (
                f"Context {ctx} should return {exp}, got {result}"
            )


# ── 2. split_into_passes ─────────────────────────────────────────────────


class TestSplitIntoPasses:
    """Tests for pass splitting logic."""

    def test_returns_dict_with_required_keys(self, challenge):
        """Must return dict with local_passes and integration_pass."""
        result = challenge.split_into_passes(SAMPLE_FILES)
        assert isinstance(result, dict)
        assert "local_passes" in result
        assert "integration_pass" in result

    def test_one_local_pass_per_file(self, challenge):
        """Each file gets its own local pass."""
        result = challenge.split_into_passes(SAMPLE_FILES)
        assert len(result["local_passes"]) == len(SAMPLE_FILES)

    def test_local_pass_structure(self, challenge):
        """Each local pass has 'file' and 'pass_type' keys."""
        result = challenge.split_into_passes(SAMPLE_FILES)
        for lp in result["local_passes"]:
            assert "file" in lp
            assert lp["pass_type"] == "local"

    def test_local_pass_file_references_original(self, challenge):
        """Each local pass 'file' value is the original file dict."""
        result = challenge.split_into_passes(SAMPLE_FILES)
        for i, lp in enumerate(result["local_passes"]):
            assert lp["file"] == SAMPLE_FILES[i]

    def test_integration_pass_has_all_files(self, challenge):
        """Integration pass must contain all PR files."""
        result = challenge.split_into_passes(SAMPLE_FILES)
        ip = result["integration_pass"]
        assert ip["files"] == SAMPLE_FILES

    def test_integration_pass_type(self, challenge):
        """Integration pass must have pass_type 'integration'."""
        result = challenge.split_into_passes(SAMPLE_FILES)
        assert result["integration_pass"]["pass_type"] == "integration"

    def test_cross_file_pairs_detected(self, challenge):
        """Cross-file import pairs are correctly identified."""
        result = challenge.split_into_passes(SAMPLE_FILES)
        pairs = result["integration_pass"]["cross_file_pairs"]
        # auth/login.py imports auth/session.py
        assert ["auth/login.py", "auth/session.py"] in pairs
        # auth/middleware.py imports auth/session.py
        assert ["auth/middleware.py", "auth/session.py"] in pairs
        # api/routes.py imports auth/middleware.py and auth/login.py
        assert ["api/routes.py", "auth/middleware.py"] in pairs
        assert ["api/routes.py", "auth/login.py"] in pairs

    def test_cross_file_pairs_count(self, challenge):
        """Correct number of cross-file pairs."""
        result = challenge.split_into_passes(SAMPLE_FILES)
        pairs = result["integration_pass"]["cross_file_pairs"]
        # login->session, middleware->session, routes->middleware, routes->login
        assert len(pairs) == 4

    def test_no_imports_yields_empty_pairs(self, challenge):
        """Files with no imports produce no cross-file pairs."""
        files = [
            {"name": "a.py", "content": "x = 1", "imports": []},
            {"name": "b.py", "content": "y = 2", "imports": []},
        ]
        result = challenge.split_into_passes(files)
        assert result["integration_pass"]["cross_file_pairs"] == []


# ── 3. build_local_review_prompt ──────────────────────────────────────────


class TestBuildLocalReviewPrompt:
    """Tests for local review prompt construction."""

    def test_starts_with_review_instruction(self, challenge):
        """Prompt must start with the specified review instruction."""
        prompt = challenge.build_local_review_prompt(SAMPLE_FILES[0])
        assert prompt.startswith(
            "Review the following file for bugs, edge cases, and design issues."
        )

    def test_contains_focus_only_instruction(self, challenge):
        """Prompt must instruct reviewer to focus only on this file."""
        prompt = challenge.build_local_review_prompt(SAMPLE_FILES[0])
        assert "Focus ONLY on issues within this single file" in prompt

    def test_contains_filename(self, challenge):
        """Prompt must contain the filename."""
        prompt = challenge.build_local_review_prompt(SAMPLE_FILES[0])
        assert "auth/login.py" in prompt

    def test_contains_file_content(self, challenge):
        """Prompt must contain the file content."""
        prompt = challenge.build_local_review_prompt(SAMPLE_FILES[0])
        assert SAMPLE_FILES[0]["content"] in prompt

    def test_contains_code_block(self, challenge):
        """Prompt must wrap content in triple backtick code block."""
        prompt = challenge.build_local_review_prompt(SAMPLE_FILES[0])
        assert "```" in prompt

    def test_asks_for_structured_findings(self, challenge):
        """Prompt must ask for categorized findings."""
        prompt = challenge.build_local_review_prompt(SAMPLE_FILES[0])
        assert "Category" in prompt or "category" in prompt
        assert "Severity" in prompt or "severity" in prompt

    def test_returns_string(self, challenge):
        """Return value must be a string."""
        result = challenge.build_local_review_prompt(SAMPLE_FILES[0])
        assert isinstance(result, str)


# ── 4. build_integration_review_prompt ────────────────────────────────────


class TestBuildIntegrationReviewPrompt:
    """Tests for integration review prompt construction."""

    def test_starts_with_file_count(self, challenge):
        """Prompt must start with 'You are reviewing a {N}-file pull request.'"""
        prompt = challenge.build_integration_review_prompt(
            SAMPLE_FILES, SAMPLE_LOCAL_REVIEW_OUTPUTS
        )
        assert prompt.startswith(f"You are reviewing a {len(SAMPLE_FILES)}-file pull request.")

    def test_mentions_per_file_reviews_completed(self, challenge):
        """Prompt must state that per-file reviews are already completed."""
        prompt = challenge.build_integration_review_prompt(
            SAMPLE_FILES, SAMPLE_LOCAL_REVIEW_OUTPUTS
        )
        assert "Per-file reviews have already been completed" in prompt

    def test_focuses_on_cross_file_issues(self, challenge):
        """Prompt must instruct focus on cross-file issues."""
        prompt = challenge.build_integration_review_prompt(
            SAMPLE_FILES, SAMPLE_LOCAL_REVIEW_OUTPUTS
        )
        assert "cross-file" in prompt.lower() or "cross-file" in prompt

    def test_includes_local_findings(self, challenge):
        """Prompt must include per-file findings from local reviews."""
        prompt = challenge.build_integration_review_prompt(
            SAMPLE_FILES, SAMPLE_LOCAL_REVIEW_OUTPUTS
        )
        for finding in SAMPLE_LOCAL_REVIEW_OUTPUTS:
            assert finding["findings"] in prompt

    def test_includes_file_contents(self, challenge):
        """Prompt must include the content of each file."""
        prompt = challenge.build_integration_review_prompt(
            SAMPLE_FILES, SAMPLE_LOCAL_REVIEW_OUTPUTS
        )
        for f in SAMPLE_FILES:
            assert f["content"] in prompt

    def test_includes_all_filenames(self, challenge):
        """Prompt must mention every filename."""
        prompt = challenge.build_integration_review_prompt(
            SAMPLE_FILES, SAMPLE_LOCAL_REVIEW_OUTPUTS
        )
        for f in SAMPLE_FILES:
            assert f["name"] in prompt

    def test_contains_section_headers(self, challenge):
        """Prompt must contain the Per-File Findings and File Contents headers."""
        prompt = challenge.build_integration_review_prompt(
            SAMPLE_FILES, SAMPLE_LOCAL_REVIEW_OUTPUTS
        )
        assert "== Per-File Findings ==" in prompt
        assert "== File Contents ==" in prompt

    def test_returns_string(self, challenge):
        """Return value must be a string."""
        result = challenge.build_integration_review_prompt(
            SAMPLE_FILES, SAMPLE_LOCAL_REVIEW_OUTPUTS
        )
        assert isinstance(result, str)


# ── 5. merge_findings ─────────────────────────────────────────────────────


class TestMergeFindings:
    """Tests for findings merging and deduplication."""

    def test_returns_list(self, challenge):
        """Must return a list."""
        result = challenge.merge_findings(
            SAMPLE_LOCAL_FINDINGS, SAMPLE_INTEGRATION_FINDINGS
        )
        assert isinstance(result, list)

    def test_deduplicates_by_description(self, challenge):
        """Findings with identical descriptions (case-insensitive) are deduplicated."""
        result = challenge.merge_findings(
            SAMPLE_LOCAL_FINDINGS, SAMPLE_INTEGRATION_FINDINGS
        )
        descriptions = [f["description"].lower() for f in result]
        assert len(descriptions) == len(set(descriptions)), (
            "Duplicate descriptions found in merged results"
        )

    def test_prefers_integration_finding_on_duplicate(self, challenge):
        """When local and integration have same description, keep integration."""
        # "Missing null check on db.find_user result" appears in both
        result = challenge.merge_findings(
            SAMPLE_LOCAL_FINDINGS, SAMPLE_INTEGRATION_FINDINGS
        )
        for f in result:
            if "null check" in f["description"].lower():
                # Integration version has multi-file reference
                assert "," in f["file"], (
                    "Duplicate should prefer the integration finding which "
                    "references multiple files (contains a comma)"
                )
                break
        else:
            pytest.fail("Expected finding about null check not found in results")

    def test_sorted_by_severity(self, challenge):
        """Results must be sorted: high first, then medium, then low."""
        result = challenge.merge_findings(
            SAMPLE_LOCAL_FINDINGS, SAMPLE_INTEGRATION_FINDINGS
        )
        severity_order = {"high": 0, "medium": 1, "low": 2}
        severities = [severity_order[f["severity"]] for f in result]
        assert severities == sorted(severities), (
            f"Findings not sorted by severity. Got: "
            f"{[f['severity'] for f in result]}"
        )

    def test_all_findings_preserved_except_duplicates(self, challenge):
        """Total count should be local + integration minus duplicates."""
        result = challenge.merge_findings(
            SAMPLE_LOCAL_FINDINGS, SAMPLE_INTEGRATION_FINDINGS
        )
        # Local has 4 findings, integration has 3.
        # "Missing null check on db.find_user result" is a duplicate.
        # Unique total = 4 + 3 - 1 = 6
        assert len(result) == 6

    def test_no_duplicates_all_preserved(self, challenge):
        """When no duplicates exist, all findings are included."""
        local = [
            {"file": "a.py", "category": "bug", "severity": "high",
             "description": "Issue A"},
        ]
        integration = [
            {"file": "a.py, b.py", "category": "bug", "severity": "medium",
             "description": "Issue B"},
        ]
        result = challenge.merge_findings(local, integration)
        assert len(result) == 2

    def test_empty_inputs(self, challenge):
        """Empty finding lists produce empty result."""
        result = challenge.merge_findings([], [])
        assert result == []

    def test_only_local_findings(self, challenge):
        """Integration findings empty; all local findings returned."""
        local = [
            {"file": "a.py", "category": "bug", "severity": "high",
             "description": "Issue A"},
        ]
        result = challenge.merge_findings(local, [])
        assert len(result) == 1
        assert result[0]["description"] == "Issue A"

    def test_only_integration_findings(self, challenge):
        """Local findings empty; all integration findings returned."""
        integration = [
            {"file": "a.py, b.py", "category": "bug", "severity": "low",
             "description": "Issue B"},
        ]
        result = challenge.merge_findings([], integration)
        assert len(result) == 1
        assert result[0]["description"] == "Issue B"

    def test_finding_dicts_have_required_keys(self, challenge):
        """Each merged finding must have file, category, severity, description."""
        result = challenge.merge_findings(
            SAMPLE_LOCAL_FINDINGS, SAMPLE_INTEGRATION_FINDINGS
        )
        for f in result:
            assert "file" in f
            assert "category" in f
            assert "severity" in f
            assert "description" in f


# ── Run ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    raise SystemExit(exit_code)
