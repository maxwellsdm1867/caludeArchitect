"""
CHALLENGE: Build a Scratchpad-Based Context Management System

Task Statement 5.4 — Apply context management techniques for large codebase interactions.

Your goal: build a system that generates structured scratchpad content from
session decisions and verifies that key details survive context compaction.

Complete the three methods in CodebaseContextChallenge:
  1. build_scratchpad(decisions) — generate structured scratchpad content
  2. build_resume_prompt(scratchpad) — build a system prompt for post-compaction resumption
  3. verify_recall(recall_text, required_details) — check if details survived compaction

The checker will test your scratchpad against sessions with specific class names,
file paths, and architectural decisions that must be recoverable.
"""

import json
import anthropic

# ---------------------------------------------------------------------------
# Test sessions with specific decisions to preserve
# ---------------------------------------------------------------------------

SESSION_1 = {
    "name": "payment_refactoring",
    "decisions": [
        {"turn": 1, "type": "rename", "old": "PaymentGatewayService", "new": "PaymentProcessor", "file": "src/payments/gateway.py"},
        {"turn": 3, "type": "extract", "class": "PaymentValidator", "file": "src/payments/validator.py"},
        {"turn": 5, "type": "pattern", "description": "Event-driven: PaymentProcessor emits PaymentCompleted event"},
        {"turn": 7, "type": "deprecate", "endpoint": "POST /api/v1/process-payment"},
        {"turn": 9, "type": "create", "file": "scripts/migrate_payment_configs.py", "purpose": "database schema migration"},
        {"turn": 11, "type": "create", "endpoint": "POST /api/v2/payments", "description": "New event-driven payment endpoint"}
    ],
    "required_details": {
        "PaymentProcessor": "renamed class",
        "PaymentValidator": "extracted class",
        "PaymentCompleted": "event name",
        "/api/v1/process-payment": "deprecated endpoint",
        "migrate_payment_configs.py": "migration script",
        "/api/v2/payments": "new endpoint",
        "src/payments/validator.py": "new file path"
    }
}

SESSION_2 = {
    "name": "auth_migration",
    "decisions": [
        {"turn": 1, "type": "rename", "old": "JWTAuthenticator", "new": "TokenAuthService", "file": "src/auth/jwt_handler.py"},
        {"turn": 3, "type": "config", "change": "Switch from HS256 to RS256 signing algorithm"},
        {"turn": 5, "type": "feature", "description": "Add refresh token rotation with 7-day expiry"},
        {"turn": 7, "type": "deprecate", "endpoint": "GET /auth/legacy/token"},
        {"turn": 9, "type": "create", "file": "src/auth/key_manager.py", "purpose": "RSA key pair management"},
        {"turn": 11, "type": "create", "endpoint": "POST /auth/v2/token", "description": "New token endpoint with RS256"}
    ],
    "required_details": {
        "TokenAuthService": "renamed class",
        "RS256": "new algorithm",
        "HS256": "old algorithm",
        "key_manager.py": "new file",
        "/auth/legacy/token": "deprecated endpoint",
        "/auth/v2/token": "new endpoint",
        "7-day": "refresh token expiry"
    }
}

SESSION_3 = {
    "name": "notification_overhaul",
    "decisions": [
        {"turn": 1, "type": "rename", "old": "NotificationSender", "new": "EventDispatcher", "file": "src/notifications/dispatcher.py"},
        {"turn": 3, "type": "pattern", "description": "Replace polling with WebSocket push via /ws/events"},
        {"turn": 5, "type": "config", "change": "Max batch size: 100 events per dispatch cycle"},
        {"turn": 7, "type": "create", "class": "PriorityQueue", "file": "src/notifications/priority_queue.py"},
        {"turn": 9, "type": "schema", "table": "event_log", "columns": ["event_id", "priority", "dispatched_at", "acknowledged"]},
        {"turn": 11, "type": "deprecate", "endpoint": "GET /api/v1/notifications/poll"}
    ],
    "required_details": {
        "EventDispatcher": "renamed class",
        "WebSocket": "transport change",
        "/ws/events": "WebSocket endpoint",
        "100": "batch size limit",
        "PriorityQueue": "new class",
        "event_log": "new table",
        "/api/v1/notifications/poll": "deprecated endpoint"
    }
}

ALL_SESSIONS = [SESSION_1, SESSION_2, SESSION_3]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class CodebaseContextChallenge:
    """
    Build a scratchpad-based context management system that preserves
    architectural decisions across context compaction.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_scratchpad(self, decisions: list) -> str:
        """
        Generate structured scratchpad content from a list of session decisions.

        The scratchpad must:
        - Include all class renames (old -> new)
        - Include all file paths (new and modified)
        - Include all endpoint changes (new, deprecated)
        - Include all configuration changes
        - Be structured for easy reference (not narrative prose)

        Args:
            decisions: List of decision dicts with type, names, files, etc.

        Returns:
            A string containing the scratchpad content (Markdown or structured text).
        """
        # TODO: Build a structured scratchpad from the decisions.
        # Hint: Group by category (renames, new files, endpoints, config changes).
        # Hint: Use clear section headers the model can scan.
        # Hint: Include specific names, paths, and values — not summaries.
        raise NotImplementedError("Complete build_scratchpad()")

    def build_resume_prompt(self, scratchpad: str) -> str:
        """
        Build a system prompt for resuming after context compaction.

        The prompt must:
        - Include the scratchpad content
        - Instruct the model to use it as the source of truth
        - Tell the model to reference exact names and paths, not paraphrases

        Args:
            scratchpad: The scratchpad content string.

        Returns:
            A complete system prompt string.
        """
        # TODO: Build a system prompt that injects the scratchpad.
        # Hint: Delimit the scratchpad clearly.
        # Hint: Instruct the model to use exact values from the scratchpad.
        raise NotImplementedError("Complete build_resume_prompt()")

    def verify_recall(self, recall_text: str, required_details: dict) -> dict:
        """
        Verify that a recall text contains all required details.

        Args:
            recall_text: The model's response when asked to list all decisions.
            required_details: Dict of {detail_string: description}.

        Returns:
            A dict with:
              - "total": int
              - "found": int
              - "missing": list of str
              - "recall_rate": float
        """
        # TODO: Check each required detail against the recall text.
        # Hint: Simple string containment check for each key in required_details.
        raise NotImplementedError("Complete verify_recall()")

    def run_session_test(self, session: dict) -> dict:
        """
        Test scratchpad-based recall for a single session.

        This method is provided — do not modify it.
        """
        scratchpad = self.build_scratchpad(session["decisions"])
        system_prompt = self.build_resume_prompt(scratchpad)

        # Simulate fresh context after compaction
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content":
                "List ALL architectural decisions from the session. Include "
                "specific class names, file paths, endpoints, and config changes."}],
        )

        recall = response.content[0].text
        verification = self.verify_recall(recall, session["required_details"])
        verification["scratchpad"] = scratchpad
        verification["recall"] = recall
        return verification

    def evaluate(self, sessions=None):
        """
        Evaluate scratchpad recall across all test sessions.

        This method is provided — do not modify it.
        """
        if sessions is None:
            sessions = ALL_SESSIONS

        total_details = 0
        total_found = 0

        for session in sessions:
            print(f"\n{'='*60}")
            print(f"Session: {session['name']}")
            print(f"{'='*60}")

            result = self.run_session_test(session)
            total_details += result["total"]
            total_found += result["found"]

            print(f"  Details checked: {result['total']}")
            print(f"  Details found:   {result['found']}")
            print(f"  Recall rate:     {result['recall_rate']:.0%}")
            if result["missing"]:
                print(f"  Missing: {result['missing']}")

        print(f"\n{'='*60}")
        print("OVERALL RESULTS")
        print(f"{'='*60}")
        rate = total_found / total_details if total_details > 0 else 0
        print(f"  Total details: {total_details}")
        print(f"  Found: {total_found}")
        print(f"  Recall rate: {rate:.0%}")

        if rate >= 0.90:
            print("\n  CHALLENGE PASSED — 90%+ recall rate!")
        else:
            print(f"\n  NEEDS WORK — recall rate below 90%.")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Codebase Context Management Challenge")
    print("================================")
    print("Goal: 90%+ detail recall after simulated compaction\n")

    challenge = CodebaseContextChallenge()
    challenge.evaluate()
