"""
CHALLENGE: Build a Code Review Prompt That Achieves 100% Precision

Task Statement 4.1 — Design prompts with explicit criteria to improve
precision and reduce false positives.

Your goal: write a prompt that, when given to Claude, correctly identifies
ONLY genuine comment-vs-code contradictions and skips imprecise-but-acceptable
comments.

Complete the three methods in CodeReviewChallenge:
  1. build_review_prompt(code)  — return a prompt string
  2. parse_findings(response_text) — parse Claude's response into findings
  3. classify_finding(finding, ground_truth) — classify as TP or FP

The checker will test your prompt against three code snippets with known
bugs and traps. You must achieve:
  - 100% recall  (catch all real bugs)
  - 0 false positives (skip all traps)
"""

import json
import anthropic

# ---------------------------------------------------------------------------
# Test code snippets with known ground truth
# ---------------------------------------------------------------------------

SNIPPET_1 = '''
def validate_payment(method: str) -> bool:
    """Only accepts credit cards."""
    valid_methods = ["credit_card", "debit_card", "apple_pay"]
    return method in valid_methods

def get_discount(user_level: str) -> float:
    """Returns the discount rate for premium users."""
    discounts = {"basic": 0.0, "premium": 0.1, "vip": 0.2}
    return discounts.get(user_level, 0.0)

def calculate_shipping(weight_kg: float) -> float:
    """Calculates shipping cost based on package weight."""
    if weight_kg <= 0:
        return 0.0
    return weight_kg * 2.5 + 3.0
'''

GROUND_TRUTH_1 = {
    "true_bugs": [
        {
            "location": "validate_payment",
            "issue": "Comment says 'Only accepts credit cards' but code also accepts debit_card and apple_pay"
        }
    ],
    "traps": [
        {
            "location": "get_discount",
            "reason": "Comment says 'premium users' which is imprecise (also handles basic and vip) but not misleading — function does return discount rates"
        },
        {
            "location": "calculate_shipping",
            "reason": "Comment is a correct high-level description; not mentioning the exact formula is imprecision, not a contradiction"
        }
    ]
}

SNIPPET_2 = '''
def fetch_active_users(include_admins: bool = False) -> list:
    """Returns only regular active users."""
    query = db.query(User).filter(User.is_active == True)
    if include_admins:
        query = query.filter(User.role.in_(["user", "admin"]))
    else:
        query = query.filter(User.role == "user")
    return query.all()

def send_notification(user_id: int, message: str) -> bool:
    """Sends an email notification to the user."""
    channels = get_user_preferences(user_id)
    for channel in channels:
        dispatch(channel, user_id, message)
    return True

def format_currency(amount: float) -> str:
    """Formats amount as USD string."""
    return f"${amount:,.2f}"
'''

GROUND_TRUTH_2 = {
    "true_bugs": [
        {
            "location": "fetch_active_users",
            "issue": "Comment says 'only regular active users' but code can include admins when include_admins=True"
        },
        {
            "location": "send_notification",
            "issue": "Comment says 'sends an email notification' but code dispatches to all user-preferred channels, not just email"
        }
    ],
    "traps": [
        {
            "location": "format_currency",
            "reason": "Comment says 'formats amount as USD string' and code does exactly that — no contradiction"
        }
    ]
}

SNIPPET_3 = '''
def calculate_tax(subtotal: float, state: str) -> float:
    """Calculates sales tax for US orders."""
    tax_rates = {
        "CA": 0.0725, "NY": 0.08, "TX": 0.0625,
        "OR": 0.0, "MT": 0.0, "DE": 0.0
    }
    rate = tax_rates.get(state, 0.05)
    return round(subtotal * rate, 2)

def merge_profiles(primary: dict, secondary: dict) -> dict:
    """Merges two user profiles, keeping primary values on conflict."""
    merged = {**secondary, **primary}
    return merged

def archive_records(records: list, cutoff_days: int = 90) -> list:
    """Archives records older than 90 days."""
    cutoff = datetime.now() - timedelta(days=cutoff_days)
    return [r for r in records if r["created_at"] < cutoff]
'''

GROUND_TRUTH_3 = {
    "true_bugs": [
        {
            "location": "archive_records",
            "issue": "Comment says 'older than 90 days' but cutoff_days is a parameter with a default of 90 — the function can archive records with any cutoff, making '90 days' a hardcoded claim that contradicts the parameterized behavior"
        }
    ],
    "traps": [
        {
            "location": "calculate_tax",
            "reason": "Comment says 'US orders' — the code handles US states with a fallback rate, which is consistent with the description"
        },
        {
            "location": "merge_profiles",
            "reason": "Comment says 'keeping primary values on conflict' — spreading secondary first then primary does exactly this; comment is accurate"
        }
    ]
}

ALL_SNIPPETS = [
    (SNIPPET_1, GROUND_TRUTH_1),
    (SNIPPET_2, GROUND_TRUTH_2),
    (SNIPPET_3, GROUND_TRUTH_3),
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class CodeReviewChallenge:
    """
    Build a code review system that achieves 100% precision
    on comment-vs-code contradiction detection.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_review_prompt(self, code: str) -> str:
        """
        Build a prompt that instructs Claude to review the given code
        for comment-vs-code contradictions.

        Requirements:
        - Must use explicit DO flag / DON'T flag criteria
        - Must distinguish contradiction from imprecision
        - Must request structured output (location, issue, severity)

        Args:
            code: The source code to review.

        Returns:
            A complete prompt string ready to send to Claude.
        """
        # TODO: Write your production-grade review prompt here.
        # Hint: Use the DO/DON'T format from the overview.
        # Hint: Define what counts as a contradiction vs imprecision.
        # Hint: Request a specific output format so parse_findings() works.
        raise NotImplementedError("Complete build_review_prompt()")

    def parse_findings(self, response_text: str) -> list[dict]:
        """
        Parse Claude's response into a list of structured findings.

        Each finding must be a dict with keys:
          - "location": str  (function or class name where the issue is)
          - "issue": str     (description of the contradiction)
          - "severity": str  (e.g., "high", "medium", "low")

        Args:
            response_text: The raw text response from Claude.

        Returns:
            A list of finding dicts.
        """
        # TODO: Parse the response text into structured findings.
        # Hint: If your prompt requests JSON output, use json.loads().
        # Hint: Handle edge cases — what if Claude returns no findings?
        raise NotImplementedError("Complete parse_findings()")

    def classify_finding(self, finding: dict, ground_truth: dict) -> str:
        """
        Classify a single finding as "true_positive" or "false_positive".

        Compare the finding's location against the ground truth:
        - If the location matches a known true bug -> "true_positive"
        - If the location matches a known trap     -> "false_positive"
        - If the location is not in ground truth   -> "false_positive"

        Args:
            finding: A dict with at least a "location" key.
            ground_truth: A dict with "true_bugs" and "traps" lists.

        Returns:
            "true_positive" or "false_positive"
        """
        # TODO: Implement classification logic.
        # Hint: Check finding["location"] against ground_truth["true_bugs"]
        #       and ground_truth["traps"].
        raise NotImplementedError("Complete classify_finding()")

    def run_review(self, code: str) -> list[dict]:
        """
        Run the full review pipeline: build prompt -> call Claude -> parse.

        This method is provided for you — do not modify it.
        """
        prompt = self.build_review_prompt(code)
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return self.parse_findings(response.content[0].text)

    def evaluate(self, snippets=None):
        """
        Evaluate your prompt against all test snippets and print results.

        This method is provided for you — do not modify it.
        """
        if snippets is None:
            snippets = ALL_SNIPPETS

        total_tp = 0
        total_fp = 0
        total_expected = 0

        for i, (code, truth) in enumerate(snippets, 1):
            print(f"\n{'='*60}")
            print(f"Snippet {i}")
            print(f"{'='*60}")

            findings = self.run_review(code)
            print(f"  Findings returned: {len(findings)}")

            expected_bugs = len(truth["true_bugs"])
            total_expected += expected_bugs

            tp = 0
            fp = 0
            for f in findings:
                cls = self.classify_finding(f, truth)
                symbol = "  [TP]" if cls == "true_positive" else "  [FP]"
                print(f"  {symbol} {f.get('location', '???')}: {f.get('issue', '???')}")
                if cls == "true_positive":
                    tp += 1
                else:
                    fp += 1

            total_tp += tp
            total_fp += fp

            print(f"  True positives: {tp}/{expected_bugs}")
            print(f"  False positives: {fp}")

        print(f"\n{'='*60}")
        print("OVERALL RESULTS")
        print(f"{'='*60}")
        recall = total_tp / total_expected if total_expected > 0 else 0
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        print(f"  Recall:    {recall:.0%} ({total_tp}/{total_expected})")
        print(f"  Precision: {precision:.0%} ({total_tp}/{total_tp + total_fp})")
        print(f"  False positives: {total_fp}")

        if recall == 1.0 and total_fp == 0:
            print("\n  CHALLENGE PASSED — 100% recall, 0 false positives!")
        else:
            if recall < 1.0:
                print(f"\n  NEEDS WORK: Missed {total_expected - total_tp} real bug(s).")
            if total_fp > 0:
                print(f"  NEEDS WORK: {total_fp} false positive(s) — tighten your criteria.")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Code Review Precision Challenge")
    print("================================")
    print("Goal: 100% recall, 0 false positives\n")

    challenge = CodeReviewChallenge()
    challenge.evaluate()
