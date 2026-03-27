"""
CHALLENGE: Built-in Tool Selection Engine

Task Statement 2.5 — Choose the right built-in tool for codebase
exploration and modification tasks.

Your goal: implement a tool selection engine that correctly maps
codebase tasks to the right built-in tool.

Complete the three methods in BuiltinToolChallenge:
  1. select_tool(task)             — pick the right built-in tool
  2. explain_selection(task, tool) — explain why this tool is correct
  3. suggest_usage(task, tool)     — suggest how to use the tool

The checker will test your selections against 15 tasks with known
correct tools.
"""

import json


# ---------------------------------------------------------------------------
# Tasks with known correct tools
# ---------------------------------------------------------------------------

TASKS = [
    # Glob tasks (path search)
    {"id": 1, "task": "Find all TypeScript files in the src/ directory", "correct_tool": "Glob"},
    {"id": 2, "task": "List all Dockerfile variants in the project", "correct_tool": "Glob"},
    {"id": 3, "task": "Find all files named 'config' with any extension", "correct_tool": "Glob"},

    # Grep tasks (content search)
    {"id": 4, "task": "Find where the class 'UserService' is defined", "correct_tool": "Grep"},
    {"id": 5, "task": "Find all files that import the 'requests' library", "correct_tool": "Grep"},
    {"id": 6, "task": "Find all TODO comments in the codebase", "correct_tool": "Grep"},

    # Read tasks
    {"id": 7, "task": "Read the contents of package.json", "correct_tool": "Read"},
    {"id": 8, "task": "Check what's in the .env.example file", "correct_tool": "Read"},

    # Edit tasks
    {"id": 9, "task": "Change the database port from 5432 to 5433 in config.yaml (appears once)", "correct_tool": "Edit"},
    {"id": 10, "task": "Rename the function 'old_handler' to 'new_handler' everywhere in routes.py", "correct_tool": "Edit"},
    {"id": 11, "task": "Add a new import statement after the existing imports in main.py", "correct_tool": "Edit"},

    # Write tasks
    {"id": 12, "task": "Create a new requirements.txt file from scratch", "correct_tool": "Write"},
    {"id": 13, "task": "Create a new test file test_utils.py", "correct_tool": "Write"},

    # Bash tasks
    {"id": 14, "task": "Run the pytest test suite", "correct_tool": "Bash"},
    {"id": 15, "task": "Install project dependencies with pip", "correct_tool": "Bash"},
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class BuiltinToolChallenge:
    """
    Select the correct built-in tool for codebase tasks.
    """

    def select_tool(self, task: str) -> str:
        """
        Given a task description, return the correct built-in tool name.

        Args:
            task: A description of a codebase task.

        Returns:
            One of: "Grep", "Glob", "Read", "Edit", "Write", "Bash"

        Decision rules:
        - Searching for files by name/pattern -> Glob
        - Searching for text inside files -> Grep
        - Reading a known file -> Read
        - Modifying part of an existing file -> Edit
        - Creating a new file -> Write
        - Running a command or script -> Bash
        """
        # TODO: Implement the decision logic.
        # Hint: Look for keywords in the task description.
        # Hint: "find files" / "list files" / "by name" -> Glob
        # Hint: "find where" / "find all uses" / "search for" -> Grep
        # Hint: "read" / "check what's in" -> Read
        # Hint: "change" / "rename" / "replace" / "add to" -> Edit
        # Hint: "create new" -> Write
        # Hint: "run" / "install" / "execute" -> Bash
        raise NotImplementedError("Complete select_tool()")

    def explain_selection(self, task: str, tool: str) -> str:
        """
        Explain why a specific tool is the correct choice for a task.

        Args:
            task: The task description.
            tool: The selected tool name.

        Returns:
            A string explanation (1-2 sentences).
        """
        # TODO: Return a brief explanation of why the tool is correct.
        # Hint: Reference the key distinction (e.g., "content vs path search").
        raise NotImplementedError("Complete explain_selection()")

    def suggest_usage(self, task: str, tool: str) -> str:
        """
        Suggest how to use the tool for this specific task.

        Args:
            task: The task description.
            tool: The selected tool name.

        Returns:
            A usage example string (e.g., 'Glob(pattern="**/*.ts")').
        """
        # TODO: Return a concrete usage example.
        # Hint: Include relevant parameters from the task description.
        raise NotImplementedError("Complete suggest_usage()")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Built-in Tool Selection Challenge")
    print("==================================")
    print(f"Tasks: {len(TASKS)}\n")

    challenge = BuiltinToolChallenge()

    correct = 0
    total = len(TASKS)

    for t in TASKS:
        try:
            selected = challenge.select_tool(t["task"])
            is_correct = selected == t["correct_tool"]
            tag = "PASS" if is_correct else "FAIL"
            if is_correct:
                correct += 1

            print(f"  [{tag}] {t['task'][:55]}...")
            if not is_correct:
                print(f"         Selected: {selected} | Correct: {t['correct_tool']}")
            else:
                try:
                    explanation = challenge.explain_selection(t["task"], selected)
                    print(f"         Reason: {explanation[:80]}")
                except NotImplementedError:
                    pass
        except NotImplementedError:
            print(f"  [SKIP] {t['task'][:55]}... (not implemented)")

    print(f"\nScore: {correct}/{total}")
    if correct == total:
        print("CHALLENGE PASSED -- 100% tool selection accuracy!")
