"""
CHALLENGE: Build an Iterative Refinement Pipeline

Task Statement 3.5 — Apply iterative refinement patterns to improve
Claude Code output quality.

Your goal: build a refinement pipeline that uses test-driven iteration
to converge on correct output automatically, and the interview pattern
to gather requirements before generating.

Complete the three methods in RefinementChallenge:
  1. build_tdd_prompt(spec, test_cases)   — prompt with test cases as spec
  2. build_interview_questions(task_desc) — generate clarifying questions
  3. refine_with_feedback(code, errors)   — retry with specific error feedback

The checker tests convergence speed and output correctness.
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# Test specifications
# ---------------------------------------------------------------------------

TRANSFORM_SPEC = {
    "function_name": "transform_record",
    "description": "Transform a database record from legacy format to new API format",
    "test_cases": [
        {
            "input": {
                "usr_nm": "john_doe",
                "eml": "JOHN@EXAMPLE.COM",
                "created": "2024-01-15",
                "active_flag": "Y",
                "dept_code": "ENG"
            },
            "expected": {
                "username": "john_doe",
                "email": "john@example.com",
                "created_at": "2024-01-15T00:00:00Z",
                "is_active": True,
                "department": "Engineering"
            }
        },
        {
            "input": {
                "usr_nm": "jane_smith",
                "eml": "jane@test.org",
                "created": "2023-06-01",
                "active_flag": "N",
                "dept_code": "MKT"
            },
            "expected": {
                "username": "jane_smith",
                "email": "jane@test.org",
                "created_at": "2023-06-01T00:00:00Z",
                "is_active": False,
                "department": "Marketing"
            }
        },
        {
            "input": {
                "usr_nm": "bob_jones",
                "eml": "  Bob@Company.IO  ",
                "created": "2024-12-25",
                "active_flag": "Y",
                "dept_code": "SAL"
            },
            "expected": {
                "username": "bob_jones",
                "email": "bob@company.io",
                "created_at": "2024-12-25T00:00:00Z",
                "is_active": True,
                "department": "Sales"
            }
        }
    ],
    "field_mappings": {
        "usr_nm": "username (no change)",
        "eml": "email (lowercase, strip whitespace)",
        "created": "created_at (append T00:00:00Z)",
        "active_flag": "is_active (Y->True, N->False)",
        "dept_code": "department (ENG->Engineering, MKT->Marketing, SAL->Sales)"
    }
}

DEPT_MAP = {"ENG": "Engineering", "MKT": "Marketing", "SAL": "Sales",
            "HR": "Human Resources", "FIN": "Finance"}


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class RefinementChallenge:
    """
    Build iterative refinement pipelines using TDD and interview patterns.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_tdd_prompt(self, spec: dict, test_cases: list) -> str:
        """
        Build a prompt that uses test cases as the specification.

        The prompt must:
        1. Include the function name and description
        2. Include ALL test cases with input/output pairs
        3. Include field mapping rules
        4. Request ONLY the Python function code

        Args:
            spec: The transform specification dict.
            test_cases: List of input/expected pairs.

        Returns:
            A complete prompt string.
        """
        # TODO: Build the test-driven prompt.
        # Hint: Include test cases as concrete examples.
        # Hint: Include the field mapping rules.
        # Hint: Request only the function code, no explanation.
        raise NotImplementedError("Complete build_tdd_prompt()")

    def build_interview_questions(self, task_desc: str) -> list:
        """
        Generate clarifying questions for a vague task description.

        Must return 3-5 questions that would elicit:
        1. Input format details
        2. Output format requirements
        3. Edge case handling
        4. Specific transformation rules
        5. Error handling expectations

        Args:
            task_desc: A vague task description.

        Returns:
            A list of 3-5 question strings.
        """
        # TODO: Generate clarifying questions.
        # Hint: Think about what information you'd need to write the function.
        # Hint: Questions should be specific enough to get actionable answers.
        raise NotImplementedError("Complete build_interview_questions()")

    def refine_with_feedback(self, original_code: str,
                              test_errors: list) -> str:
        """
        Build a retry prompt with specific error feedback.

        The prompt must:
        1. Include the original code
        2. Include specific test failure details
        3. Request a corrected version
        4. NOT use vague feedback like "fix the bugs"

        Args:
            original_code: The code that failed tests.
            test_errors: List of dicts with "case", "field", "got", "expected".

        Returns:
            A prompt string for the retry.
        """
        # TODO: Build the retry prompt with specific error feedback.
        # Hint: Include the exact field-level errors.
        # Hint: Include the original code for context.
        # Hint: Be specific about what went wrong.
        raise NotImplementedError("Complete refine_with_feedback()")

    def run_tests(self, code_str: str, test_cases: list) -> dict:
        """
        Execute generated code against test cases.

        This method is provided for you — do not modify it.
        """
        namespace = {}
        try:
            exec(code_str, namespace)
        except Exception as e:
            return {"passed": 0, "total": len(test_cases),
                    "errors": [{"case": 0, "field": "exec", "got": str(e), "expected": "no error"}]}

        func_name = TRANSFORM_SPEC["function_name"]
        if func_name not in namespace:
            return {"passed": 0, "total": len(test_cases),
                    "errors": [{"case": 0, "field": "missing", "got": "not found",
                                "expected": func_name}]}

        transform_fn = namespace[func_name]
        passed = 0
        errors = []

        for i, tc in enumerate(test_cases, 1):
            try:
                result = transform_fn(tc["input"])
                case_ok = True
                for key, expected_val in tc["expected"].items():
                    if key not in result:
                        errors.append({"case": i, "field": key, "got": "MISSING", "expected": expected_val})
                        case_ok = False
                    elif result[key] != expected_val:
                        errors.append({"case": i, "field": key, "got": repr(result[key]),
                                       "expected": repr(expected_val)})
                        case_ok = False
                if case_ok:
                    passed += 1
            except Exception as e:
                errors.append({"case": i, "field": "exception", "got": str(e), "expected": "no error"})

        return {"passed": passed, "total": len(test_cases), "errors": errors}

    def evaluate(self):
        """
        Evaluate the full TDD pipeline.

        This method is provided for you — do not modify it.
        """
        spec = TRANSFORM_SPEC
        test_cases = spec["test_cases"]

        print("Phase 1: Test-Driven Prompt")
        print("=" * 50)
        prompt = self.build_tdd_prompt(spec, test_cases)
        print(f"Prompt length: {len(prompt)} chars")
        assert "transform_record" in prompt, "Prompt must include function name"
        print("  [OK] Prompt includes function name")

        print("\nPhase 2: Interview Questions")
        print("=" * 50)
        questions = self.build_interview_questions("Transform some database records")
        print(f"Questions generated: {len(questions)}")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")
        assert 3 <= len(questions) <= 5, "Must generate 3-5 questions"
        print("  [OK] Question count is valid")

        print("\nPhase 3: Refinement with Feedback")
        print("=" * 50)
        sample_errors = [
            {"case": 1, "field": "email", "got": "'JOHN@EXAMPLE.COM'", "expected": "'john@example.com'"},
            {"case": 2, "field": "is_active", "got": "'N'", "expected": "False"},
        ]
        retry_prompt = self.refine_with_feedback("def transform_record(r): pass", sample_errors)
        print(f"Retry prompt length: {len(retry_prompt)} chars")
        assert "JOHN@EXAMPLE.COM" in retry_prompt or "john@example.com" in retry_prompt, (
            "Retry prompt must include specific error details"
        )
        print("  [OK] Retry prompt includes specific errors")

        print("\nCHALLENGE PASSED — All refinement components work correctly!")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Iterative Refinement Challenge")
    print("==============================")
    print("Goal: Build TDD prompt, interview questions, and retry logic\n")

    challenge = RefinementChallenge()
    challenge.evaluate()
