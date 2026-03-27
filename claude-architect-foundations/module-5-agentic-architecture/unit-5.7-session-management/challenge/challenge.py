"""
CHALLENGE: Manage Session State & Resumption

Task Statement 1.7 — Decide when to resume vs start fresh. Build
structured session summaries. Handle stale context correctly.

Complete the three methods in SessionChallenge:
  1. should_resume(scenario)         — decide resume vs fresh session
  2. build_session_summary(session)  — create a structured summary
  3. detect_stale_context(session, current_state) — find stale assumptions

The checker tests decision logic, summary structure, and staleness detection.
No API calls needed.
"""

import json


# ---------------------------------------------------------------------------
# Test scenarios
# ---------------------------------------------------------------------------

SCENARIOS = [
    {
        "id": "S1",
        "description": "Code review agent paused. Developer pushed 3 new commits overnight.",
        "data_changed": True,
        "expected": "fresh_with_summary"
    },
    {
        "id": "S2",
        "description": "Debug session interrupted by network drop. System unchanged.",
        "data_changed": False,
        "expected": "resume"
    },
    {
        "id": "S3",
        "description": "Data analysis paused. Database migrated to new schema.",
        "data_changed": True,
        "expected": "fresh_with_summary"
    },
    {
        "id": "S4",
        "description": "Research agent interrupted. Source documents unchanged.",
        "data_changed": False,
        "expected": "resume"
    },
    {
        "id": "S5",
        "description": "Security audit paused. 15 PRs merged since last session.",
        "data_changed": True,
        "expected": "fresh_with_summary"
    },
    {
        "id": "S6",
        "description": "Writing assistance paused. User wants to continue from draft.",
        "data_changed": False,
        "expected": "resume"
    },
]

# Test session for summary building
TEST_SESSION = {
    "task": "Security review of auth module",
    "started": "2024-12-14T10:00:00",
    "paused": "2024-12-14T11:30:00",
    "files_reviewed": ["auth.py", "tokens.py", "middleware.py"],
    "findings": [
        {"file": "auth.py", "issue": "Plaintext password comparison", "severity": "critical", "status": "open"},
        {"file": "tokens.py", "issue": "Token expiry not checked", "severity": "high", "status": "open"},
    ],
    "approaches_tried": [
        {"action": "Searched for password handling patterns", "result": "Found plaintext comparison in auth.py"},
        {"action": "Checked token validation flow", "result": "Found missing expiry check"},
    ],
    "remaining_work": ["Review middleware.py", "Check session management", "Cross-file analysis"],
}

# Stale context detection test
PRIOR_SESSION_STATE = {
    "files": {
        "auth.py": {"hash": "abc123", "findings": ["plaintext password"]},
        "api.py": {"hash": "def456", "findings": ["no rate limiting"]},
    },
    "assumptions": [
        "auth.py uses plaintext password comparison",
        "api.py has no rate limiting",
        "No payment processing code exists",
    ]
}

CURRENT_STATE = {
    "files": {
        "auth.py": {"hash": "xyz789"},      # Changed!
        "api.py": {"hash": "def456"},        # Unchanged
        "payments.py": {"hash": "new111"},   # New file!
    }
}


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class SessionChallenge:
    """
    Manage session state: decide when to resume, build summaries,
    and detect stale context.
    """

    def should_resume(self, scenario: dict) -> str:
        """
        Decide whether to resume a session or start fresh.

        Decision rule:
        - If data_changed is True -> "fresh_with_summary"
        - If data_changed is False -> "resume"

        Args:
            scenario: dict with "description", "data_changed" bool.

        Returns:
            "resume" or "fresh_with_summary"
        """
        # TODO: Implement the decision logic.
        raise NotImplementedError("Complete should_resume()")

    def build_session_summary(self, session: dict) -> dict:
        """
        Build a structured summary of a prior session for handoff to a fresh session.

        The summary must include:
        - task: what the session was working on
        - key_findings: list of findings with file, issue, and severity
        - approaches_tried: what was already attempted and the results
        - remaining_work: what still needs to be done
        - files_reviewed: which files have been analyzed

        Must NOT include: full conversation history, raw API responses,
        timestamps, or internal metadata.

        Args:
            session: dict with session state and findings.

        Returns:
            Structured summary dict.
        """
        # TODO: Extract the relevant information from the session.
        # Build a clean summary suitable for passing to a fresh session.
        raise NotImplementedError("Complete build_session_summary()")

    def detect_stale_context(self, prior_state: dict, current_state: dict) -> dict:
        """
        Compare prior session state against current state to find staleness.

        Check for:
        - Files that have changed (different hash)
        - Files that are new (exist in current but not prior)
        - Files that were deleted (exist in prior but not current)
        - Assumptions that may be invalid due to changes

        Args:
            prior_state: dict with "files" (filename -> {hash, findings}) and "assumptions" list.
            current_state: dict with "files" (filename -> {hash}).

        Returns:
            dict with:
            - "is_stale": bool (True if any staleness detected)
            - "changed_files": list of filenames with different hashes
            - "new_files": list of filenames only in current state
            - "deleted_files": list of filenames only in prior state
            - "invalidated_assumptions": list of assumptions that may be wrong
        """
        # TODO: Compare the file hashes between prior and current state.
        # Identify changed, new, and deleted files.
        # Check which assumptions reference changed or deleted files.
        raise NotImplementedError("Complete detect_stale_context()")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Session Management Challenge")
    print("============================\n")

    challenge = SessionChallenge()

    # Test decisions
    print("Resume vs Fresh decisions:")
    for s in SCENARIOS:
        decision = challenge.should_resume(s)
        match = "OK" if decision == s["expected"] else "WRONG"
        print(f"  [{match}] {s['id']}: {decision} ({s['description'][:50]}...)")

    # Test summary
    print("\nSession summary:")
    summary = challenge.build_session_summary(TEST_SESSION)
    print(json.dumps(summary, indent=2))

    # Test staleness
    print("\nStaleness detection:")
    stale = challenge.detect_stale_context(PRIOR_SESSION_STATE, CURRENT_STATE)
    print(json.dumps(stale, indent=2))
