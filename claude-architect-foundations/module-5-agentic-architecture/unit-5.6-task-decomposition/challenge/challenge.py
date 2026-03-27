"""
CHALLENGE: Design Task Decomposition Strategies

Task Statement 1.6 — Choose between prompt chaining and dynamic
decomposition. Implement per-file + cross-file analysis.

Complete the three methods in DecompositionChallenge:
  1. choose_strategy(task_description) — select the right decomposition
  2. analyze_per_file(filename, code)  — per-file analysis summary
  3. analyze_cross_file(summaries)     — cross-file integration review

The checker tests strategy selection, per-file extraction, and cross-file
bug detection. Uses mock API responses.
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# Test codebase with cross-file bugs
# ---------------------------------------------------------------------------

CODEBASE = {
    "api/routes.py": '''def create_user():
    """Create user. Expects {email: str, name: str}."""
    data = request.json
    user = UserService.create(email=data["email"], name=data["name"])
    return jsonify({"user_id": user.id}), 201

def get_user(user_id: int):
    """Get user by ID."""
    user = UserService.get_by_id(user_id)
    return jsonify({"userId": user.id, "name": user.name})
''',
    "services/user_service.py": '''class UserService:
    @staticmethod
    def create(email: str, name: str) -> User:
        return User(email=email, name=name)

    @staticmethod
    def get_by_id(user_id: str) -> User:
        """Get user by string ID."""
        return db.query(User).filter(User.id == user_id).first()
''',
    "models/user.py": '''@dataclass
class User:
    id: int  # Auto-generated integer
    email: str
    name: str
'''
}

# Known cross-file bugs
KNOWN_BUGS = {
    "type_mismatch": {
        "files": ["api/routes.py", "services/user_service.py"],
        "description": "Route passes int user_id, service expects str"
    },
    "key_inconsistency": {
        "files": ["api/routes.py"],
        "description": "create_user returns 'user_id', get_user returns 'userId'"
    }
}

# Task descriptions for strategy classification
TASK_DESCRIPTIONS = [
    {"task": "Process 1000 invoices: extract fields, validate, format for database", "expected": "prompt_chaining"},
    {"task": "Debug a production error across frontend, backend, and database", "expected": "dynamic"},
    {"task": "Review a 30-file pull request for bugs and integration issues", "expected": "per_file_cross_file"},
    {"task": "Translate 50 documents: translate, review, format", "expected": "prompt_chaining"},
    {"task": "Research AI impact on creative industries and produce a report", "expected": "dynamic"},
    {"task": "Analyze a 10-file microservice for API contract violations", "expected": "per_file_cross_file"},
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class DecompositionChallenge:
    """
    Design and implement task decomposition strategies.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def choose_strategy(self, task_description: str) -> str:
        """
        Choose the right decomposition strategy for a given task.

        Strategies:
        - "prompt_chaining": Fixed step sequence for predictable pipelines
        - "dynamic": Model-driven decomposition for variable tasks
        - "per_file_cross_file": Per-file + cross-file for multi-file analysis

        Decision criteria:
        - Predictable pipeline (extract/validate/format) -> prompt_chaining
        - Variable investigation (debug/research) -> dynamic
        - Multi-file analysis (review/audit) -> per_file_cross_file

        Args:
            task_description: Natural language description of the task.

        Returns:
            One of: "prompt_chaining", "dynamic", "per_file_cross_file"
        """
        # TODO: Analyze the task description and return the correct strategy.
        # Look for keywords/patterns that indicate which strategy fits.
        raise NotImplementedError("Complete choose_strategy()")

    def analyze_per_file(self, filename: str, code: str) -> dict:
        """
        Analyze a single file and produce a structured summary for cross-file review.

        The summary must include:
        - functions: list of function names with parameter and return types
        - data_contracts: JSON keys, field names, or data structures produced/consumed
        - local_issues: any bugs visible within this file alone

        Args:
            filename: The file's path.
            code: The file's source code.

        Returns:
            dict with "functions", "data_contracts", and "local_issues".
        """
        # TODO: Parse the code and extract structured information.
        # This should work WITHOUT calling the API — parse the code strings directly.
        # Hint: Look for function names, parameter types, return keys, etc.
        raise NotImplementedError("Complete analyze_per_file()")

    def analyze_cross_file(self, file_summaries: dict) -> list:
        """
        Analyze per-file summaries for cross-file integration bugs.

        Check for:
        - Type mismatches: one file passes type X, another expects type Y
        - Key inconsistencies: different JSON keys for the same concept
        - API contract violations: caller and callee disagree on interface

        Args:
            file_summaries: dict mapping filename -> per-file summary dict.

        Returns:
            List of cross-file bugs, each: {"bug_type": "...", "files": [...], "description": "..."}
        """
        # TODO: Compare the file summaries to find integration bugs.
        # Look for: type mismatches in function parameters,
        #           inconsistent JSON keys across files,
        #           caller/callee interface mismatches.
        raise NotImplementedError("Complete analyze_cross_file()")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Task Decomposition Challenge")
    print("============================\n")

    challenge = DecompositionChallenge()

    # Test strategy selection
    print("Strategy Selection:")
    for td in TASK_DESCRIPTIONS:
        strategy = challenge.choose_strategy(td["task"])
        match = "OK" if strategy == td["expected"] else "WRONG"
        print(f"  [{match}] {td['task'][:50]}... -> {strategy}")

    # Test per-file analysis
    print("\nPer-File Analysis:")
    summaries = {}
    for filename, code in CODEBASE.items():
        summary = challenge.analyze_per_file(filename, code)
        summaries[filename] = summary
        print(f"  {filename}: {len(summary.get('functions', []))} functions")

    # Test cross-file analysis
    print("\nCross-File Analysis:")
    bugs = challenge.analyze_cross_file(summaries)
    for bug in bugs:
        print(f"  [{bug['bug_type']}] {bug['description'][:60]}")
