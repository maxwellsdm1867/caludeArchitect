"""
CHALLENGE: Build a Task Complexity Classifier for Plan vs Direct Mode

Task Statement 3.4 — Choose between plan mode and direct execution
based on task complexity assessment.

Your goal: build a classifier that, given a task description, correctly
recommends plan mode or direct execution mode.

Complete the three methods in ComplexityChallenge:
  1. assess_complexity(task_desc)      — return complexity signals
  2. recommend_mode(signals)           — return "plan" or "direct"
  3. classify_task(task_desc)           — full pipeline: assess + recommend

The checker tests classification accuracy across diverse task scenarios.
"""

import json
import anthropic


# ---------------------------------------------------------------------------
# Task scenarios with ground truth
# ---------------------------------------------------------------------------

TASKS = [
    {
        "description": "Fix the off-by-one error in the pagination logic at src/api/pagination.ts line 23. The last page shows duplicate items.",
        "correct_mode": "direct",
        "reason": "Single file, specific line, clear bug description",
    },
    {
        "description": "Migrate the project from Express.js to Fastify. The backend has 45 route handlers, 12 middleware functions, and 30 test files.",
        "correct_mode": "plan",
        "reason": "87+ files, framework migration, architectural decisions required",
    },
    {
        "description": "Add a required 'phone' field to the user registration form. Update the form component, validation schema, and API endpoint.",
        "correct_mode": "direct",
        "reason": "Clear scope (3 files), well-defined change, obvious implementation",
    },
    {
        "description": "Design and implement a new notification system. Need to decide between WebSockets, Server-Sent Events, or polling. Must integrate with existing auth, support multiple channels, and handle offline users.",
        "correct_mode": "plan",
        "reason": "Multiple valid approaches, architectural decision, many integration points",
    },
    {
        "description": "Update the copyright year in the footer component from 2024 to 2025.",
        "correct_mode": "direct",
        "reason": "Single line change, zero risk, trivial",
    },
    {
        "description": "Investigate why the test suite takes 12 minutes to run. Could be database setup, test isolation issues, or excessive mocking.",
        "correct_mode": "plan",
        "reason": "Investigation with unknown root cause, needs exploration",
    },
    {
        "description": "Implement the rate limiting approach that was approved in yesterday's design review: token bucket algorithm using Redis, applied to all /api/v2 endpoints.",
        "correct_mode": "direct",
        "reason": "Plan already approved, implementation details are clear",
    },
    {
        "description": "Add dark mode support across the entire application. Involves theme system, CSS variables, component updates, and user preference persistence.",
        "correct_mode": "plan",
        "reason": "Application-wide change, multiple approaches for theming, affects many components",
    },
    {
        "description": "Fix the broken import in src/utils/date.ts — it references a function that was renamed from formatDate to formatDateTime in the last PR.",
        "correct_mode": "direct",
        "reason": "Single file, obvious fix (rename import)",
    },
    {
        "description": "Restructure the monorepo into a multi-package workspace. Need to split shared code, update build configs, fix circular dependencies, and update CI pipeline.",
        "correct_mode": "plan",
        "reason": "Entire repo restructuring, affects build system, CI, and all packages",
    },
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class ComplexityChallenge:
    """
    Classify development tasks as needing plan mode or direct execution.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def assess_complexity(self, task_desc: str) -> dict:
        """
        Assess the complexity of a development task.

        Must return a dict with these signals:
        {
            "scope": "single" | "multi" | "unknown",
            "clarity": "high" | "medium" | "low",
            "familiarity": "known" | "unknown",
            "risk": "high" | "medium" | "low",
            "has_approved_plan": bool
        }

        Assessment criteria:
        - scope: How many files are affected?
          "single" = 1-3 files, "multi" = 4+ files, "unknown" = investigation
        - clarity: How clear is the implementation approach?
          "high" = obvious fix, "medium" = some decisions, "low" = multiple approaches
        - familiarity: Is the codebase/pattern well-known?
          "known" = clear pattern, "unknown" = needs exploration
        - risk: What is the potential for breaking changes?
          "high" = architectural, "medium" = moderate, "low" = localized
        - has_approved_plan: Is this implementing an already-approved plan?

        Args:
            task_desc: The task description.

        Returns:
            A complexity signals dict.
        """
        # TODO: Assess the task complexity.
        # Hint: Look for keywords that indicate each signal level.
        # Hint: "fix", "typo", "rename" -> single scope, high clarity
        # Hint: "migrate", "restructure", "design" -> multi scope, low clarity
        # Hint: "approved", "decided", "agreed" -> has_approved_plan = True
        raise NotImplementedError("Complete assess_complexity()")

    def recommend_mode(self, signals: dict) -> str:
        """
        Recommend plan mode or direct execution based on complexity signals.

        Decision rules:
        - If has_approved_plan is True -> "direct" (plan already done)
        - If scope is "multi" AND clarity is "low" -> "plan"
        - If scope is "unknown" (investigation) -> "plan"
        - If risk is "high" -> "plan"
        - Otherwise -> "direct"

        Args:
            signals: Complexity signals dict from assess_complexity.

        Returns:
            "plan" or "direct"
        """
        # TODO: Implement the decision logic.
        # Hint: Apply the rules in order of priority.
        # Hint: has_approved_plan overrides everything else.
        raise NotImplementedError("Complete recommend_mode()")

    def classify_task(self, task_desc: str) -> dict:
        """
        Full pipeline: assess complexity and recommend mode.

        Returns:
        {
            "mode": "plan" or "direct",
            "signals": {complexity signals dict},
            "reasoning": brief explanation
        }
        """
        # TODO: Combine assess_complexity and recommend_mode.
        raise NotImplementedError("Complete classify_task()")

    def evaluate(self, tasks=None):
        """
        Evaluate your classifier against all task scenarios.

        This method is provided for you — do not modify it.
        """
        if tasks is None:
            tasks = TASKS

        correct = 0
        total = len(tasks)

        for i, task in enumerate(tasks, 1):
            print(f"\n{'='*60}")
            print(f"Task {i}: {task['description'][:70]}...")
            print(f"{'='*60}")

            result = self.classify_task(task['description'])
            predicted = result['mode']
            expected = task['correct_mode']
            match = predicted == expected

            if match:
                correct += 1

            symbol = "[OK]" if match else "[WRONG]"
            print(f"  {symbol} Predicted: {predicted} | Expected: {expected}")
            print(f"  Signals: {result.get('signals', {})}")
            if not match:
                print(f"  Ground truth: {task['reason']}")

        accuracy = correct / total if total > 0 else 0
        print(f"\n{'='*60}")
        print(f"ACCURACY: {correct}/{total} ({accuracy:.0%})")
        print(f"{'='*60}")

        if accuracy == 1.0:
            print("\nCHALLENGE PASSED — All tasks correctly classified!")
        else:
            print(f"\nNEEDS WORK: Misclassified {total - correct} task(s).")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Plan vs Direct Mode Challenge")
    print("==============================")
    print("Goal: Correctly classify all tasks\n")

    challenge = ComplexityChallenge()
    challenge.evaluate()
