"""
Checker for Unit 3.5 — Iterative Refinement Challenge

Validates the student's RefinementChallenge implementation without
calling the Anthropic API. Tests TDD prompt construction, interview
questions, and retry logic.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from challenge import (
    RefinementChallenge,
    TRANSFORM_SPEC,
    DEPT_MAP,
)


@pytest.fixture
def challenge():
    return RefinementChallenge()


class TestTDDPrompt:
    """Student's build_tdd_prompt must produce a well-structured prompt."""

    def test_returns_string(self, challenge):
        prompt = challenge.build_tdd_prompt(
            TRANSFORM_SPEC, TRANSFORM_SPEC["test_cases"]
        )
        assert isinstance(prompt, str), "build_tdd_prompt must return a string"

    def test_includes_function_name(self, challenge):
        prompt = challenge.build_tdd_prompt(
            TRANSFORM_SPEC, TRANSFORM_SPEC["test_cases"]
        )
        assert "transform_record" in prompt, (
            "Prompt must include the function name"
        )

    def test_includes_test_cases(self, challenge):
        prompt = challenge.build_tdd_prompt(
            TRANSFORM_SPEC, TRANSFORM_SPEC["test_cases"]
        )
        # Should include at least some test data
        assert "john_doe" in prompt, "Prompt must include test case data"
        assert "jane_smith" in prompt, "Prompt must include multiple test cases"

    def test_includes_field_mappings(self, challenge):
        prompt = challenge.build_tdd_prompt(
            TRANSFORM_SPEC, TRANSFORM_SPEC["test_cases"]
        )
        prompt_lower = prompt.lower()
        assert "email" in prompt_lower, "Prompt must mention email transformation"
        assert ("lowercase" in prompt_lower or "lower" in prompt_lower or
                "john@example.com" in prompt_lower), (
            "Prompt must specify email lowercasing"
        )

    def test_includes_department_mapping(self, challenge):
        prompt = challenge.build_tdd_prompt(
            TRANSFORM_SPEC, TRANSFORM_SPEC["test_cases"]
        )
        assert "Engineering" in prompt or "ENG" in prompt, (
            "Prompt must include department mapping"
        )

    def test_not_vague(self, challenge):
        prompt = challenge.build_tdd_prompt(
            TRANSFORM_SPEC, TRANSFORM_SPEC["test_cases"]
        ).lower()
        vague = ["be careful", "try your best", "use judgment"]
        for phrase in vague:
            assert phrase not in prompt, (
                f"TDD prompt should not use vague phrase: '{phrase}'"
            )


class TestInterviewQuestions:
    """Student's build_interview_questions must generate useful questions."""

    def test_returns_list(self, challenge):
        result = challenge.build_interview_questions("Transform database records")
        assert isinstance(result, list), "Must return a list"

    def test_correct_count(self, challenge):
        result = challenge.build_interview_questions("Transform database records")
        assert 3 <= len(result) <= 5, (
            f"Must generate 3-5 questions, got {len(result)}"
        )

    def test_questions_are_strings(self, challenge):
        result = challenge.build_interview_questions("Transform database records")
        for q in result:
            assert isinstance(q, str), "Each question must be a string"
            assert len(q) > 10, "Questions should be substantial"

    def test_questions_are_specific(self, challenge):
        result = challenge.build_interview_questions("Transform database records")
        # Questions should not be too generic
        all_questions = " ".join(result).lower()
        specific_topics = ["format", "field", "type", "error", "edge", "input",
                           "output", "handle", "transform", "map", "convert"]
        has_specific = any(topic in all_questions for topic in specific_topics)
        assert has_specific, (
            "Questions should cover specific aspects like format, fields, "
            "error handling, or transformations"
        )


class TestRefinementFeedback:
    """Student's refine_with_feedback must produce specific retry prompts."""

    def test_returns_string(self, challenge):
        errors = [{"case": 1, "field": "email", "got": "'X'", "expected": "'y'"}]
        result = challenge.refine_with_feedback("def f(): pass", errors)
        assert isinstance(result, str), "Must return a string"

    def test_includes_original_code(self, challenge):
        code = "def transform_record(r): return {}"
        errors = [{"case": 1, "field": "email", "got": "'X'", "expected": "'y'"}]
        result = challenge.refine_with_feedback(code, errors)
        assert "transform_record" in result, (
            "Retry prompt must include the original code"
        )

    def test_includes_specific_errors(self, challenge):
        errors = [
            {"case": 1, "field": "email", "got": "'JOHN@EXAMPLE.COM'",
             "expected": "'john@example.com'"},
            {"case": 2, "field": "is_active", "got": "'N'", "expected": "False"},
        ]
        result = challenge.refine_with_feedback("def f(): pass", errors)
        assert "email" in result, "Retry must mention the failing field"
        assert "JOHN@EXAMPLE.COM" in result or "john@example.com" in result, (
            "Retry must include the actual vs expected values"
        )

    def test_not_vague_feedback(self, challenge):
        errors = [{"case": 1, "field": "email", "got": "'X'", "expected": "'y'"}]
        result = challenge.refine_with_feedback("def f(): pass", errors).lower()
        vague = ["fix the bugs", "try again", "make it work", "fix the issues"]
        for phrase in vague:
            assert phrase not in result, (
                f"Retry prompt should not use vague feedback: '{phrase}'"
            )

    def test_multiple_errors_all_included(self, challenge):
        errors = [
            {"case": 1, "field": "email", "got": "'X'", "expected": "'y'"},
            {"case": 2, "field": "department", "got": "'ENG'", "expected": "'Engineering'"},
            {"case": 3, "field": "is_active", "got": "'Y'", "expected": "True"},
        ]
        result = challenge.refine_with_feedback("def f(): pass", errors)
        assert "email" in result, "Must mention email error"
        assert "department" in result or "ENG" in result, "Must mention department error"
        assert "is_active" in result or "active" in result, "Must mention is_active error"


class TestRunTests:
    """The provided run_tests method should work correctly."""

    def test_correct_function_passes(self, challenge):
        code = '''
def transform_record(record):
    dept_map = {"ENG": "Engineering", "MKT": "Marketing", "SAL": "Sales"}
    return {
        "username": record["usr_nm"],
        "email": record["eml"].strip().lower(),
        "created_at": record["created"] + "T00:00:00Z",
        "is_active": record["active_flag"] == "Y",
        "department": dept_map.get(record["dept_code"], record["dept_code"]),
    }
'''
        result = challenge.run_tests(code, TRANSFORM_SPEC["test_cases"])
        assert result["passed"] == result["total"], (
            f"Correct function should pass all tests: {result}"
        )

    def test_broken_function_fails(self, challenge):
        code = 'def transform_record(r): return {}'
        result = challenge.run_tests(code, TRANSFORM_SPEC["test_cases"])
        assert result["passed"] < result["total"], (
            "Empty function should fail tests"
        )
        assert len(result["errors"]) > 0, "Should report errors"
