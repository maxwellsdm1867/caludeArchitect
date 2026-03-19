# Unit 1.1: Explicit Criteria over Vague Instructions

**Task Statement 4.1** — Design prompts with explicit criteria to improve precision and reduce false positives

## The core principle

When Claude reviews code, extracts data, or makes decisions, **specificity of instructions determines precision**. This is the single most common failure mode in production Claude deployments and the exam tests it heavily.

The fundamental insight: telling a model to "be careful" or "be conservative" gives it no actionable criteria. The model has no calibrated sense of what conservative means in your context. You must define the exact conditions under which a finding should be reported.

## What the exam expects you to know

### Knowledge areas

1. **Explicit criteria > vague instructions.** "Flag comments only when claimed behavior contradicts actual code behavior" works. "Check that comments are accurate" doesn't.

2. **General instructions fail.** "Be conservative," "only report high-confidence findings," and "focus on important issues" do NOT measurably improve precision. The exam uses these as distractors.

3. **False positive impact on trust.** If your comment-accuracy category has a 40% false positive rate, developers stop trusting ALL categories — including the ones that are actually accurate. One bad category poisons the whole system.

### Skills tested

1. Writing specific review criteria that define which issues to report (bugs, security) vs skip (minor style, local patterns)
2. Temporarily disabling high false-positive categories to restore trust while you fix the prompts
3. Defining explicit severity criteria with concrete code examples for each severity level

## Concepts

### The vague-to-precise spectrum

Here's the same task at different precision levels:

**Level 1 — Useless:**
```
Review this code and report any issues.
```
Problems: no scope definition, no severity criteria, no guidance on what counts as an "issue."

**Level 2 — Still bad:**
```
Review this code carefully. Be conservative and only report high-confidence findings.
```
Problems: "carefully" and "conservative" are not actionable. The model will still report stylistic preferences and subjective improvements because it doesn't know what "conservative" means in your context.

**Level 3 — Getting better:**
```
Review this code for bugs and security issues. Do not report style preferences or minor naming issues.
```
Problems: "bugs" is still broad. What counts as a bug vs a design choice?

**Level 4 — Production-grade:**
```
Review code comments against actual code behavior. Flag a comment ONLY when:
1. The comment claims the code does X, but the code actually does Y (direct contradiction)
2. The comment states a constraint that the code does not enforce

DO NOT flag:
- Comments that are slightly imprecise but not misleading
- Comments about future behavior or design intent
- Missing comments or undocumented code
```

This is what the exam expects. Notice: no mention of "confidence" or "conservatism" — just categorical rules about what to flag and what to skip.

### Why "be conservative" fails

The model doesn't have an internal dial labeled "conservatism." When you say "be conservative," it might:
- Report fewer issues overall (including real bugs)
- Add hedging language ("this might be an issue") without changing what it reports
- Apply its own undefined sense of importance (which doesn't match yours)

None of these behaviors reduce false positives in the categories you care about. Specific categorical criteria do.

### The false positive trust problem

Imagine your review system reports findings in four categories:

| Category | Accuracy | Volume |
|----------|----------|--------|
| Null pointer risks | 95% | Low |
| Comment accuracy | 60% | High |
| Security issues | 90% | Low |
| Style violations | 70% | Medium |

Developers experience the system as: "it keeps flagging stuff that isn't actually wrong." They start ignoring ALL findings — including the 95%-accurate null pointer risks. The correct fix isn't "make all categories more conservative." It's:

1. Temporarily disable comment-accuracy and style categories
2. Rebuild those prompts with explicit criteria and few-shot examples
3. Re-enable once false positive rate is acceptable

The exam tests whether you understand this targeted approach vs a blanket "be more conservative" instruction.

## Hands-on exercises

### Exercise 1: The vague prompt (run this first — it will fail)

Open `notebooks/01-explicit-vs-vague.ipynb` and run the vague prompt against the test code. Before running, predict:
- How many findings will it report?
- Which will be true bugs vs false positives?

Then run it and check your predictions.

### Exercise 2: The precise prompt

In the same notebook, run the precise prompt against the same code. Compare:
- Did it find the real bug? (the `validate_payment` comment contradiction)
- How many false positives did it produce?
- Did it correctly skip the imprecise-but-not-wrong comments?

### Exercise 3: Write your own criteria (this is the real skill)

The notebook gives you a new code snippet with a different set of comment issues. Write your own explicit criteria prompt from scratch. Target:
- Catch all real contradictions
- Zero false positives on imprecise-but-acceptable comments

### Failure exercise: The "high-confidence" trap

In the notebook, try adding "only report high-confidence findings" to the vague prompt. Run it 5 times. Count:
- Does it consistently reduce false positives? (Spoiler: no)
- Does it sometimes suppress real bugs? (Spoiler: yes)

This exercise exists to burn into your brain: **confidence-based filtering does not work.**

## Exam-style practice question

**Scenario:** Your CI pipeline uses Claude to review pull requests. Developers report that the comment-accuracy check has a 45% false positive rate. Other categories (null safety, error handling) are accurate at 92%. Developer trust in the entire review system is declining.

**Question:** What is the most effective first step to address this?

A) Add "only flag high-confidence comment issues" to the review prompt  
B) Temporarily disable the comment-accuracy category and rebuild its prompt with explicit contradiction criteria and few-shot examples  
C) Increase the model temperature to encourage more diverse review approaches  
D) Switch to a larger model with better reasoning capabilities  

<details>
<summary>Answer</summary>

**B.** Disabling the noisy category restores trust in the accurate categories immediately, while you fix the underlying prompt. Option A is the classic trap — "high-confidence" doesn't measurably improve precision. Option C is nonsensical (lower temperature helps precision). Option D doesn't address the prompt quality issue.

</details>

## Key takeaways for the exam

1. When you see "the system produces too many false positives" in a question, look for the answer that adds **specific categorical criteria** — not confidence filtering
2. When you see "be conservative" or "only report high-confidence findings" in an answer option, it's almost certainly a distractor
3. The correct answer for precision problems is always about **defining what counts as a finding** with explicit rules, not about asking the model to self-filter
4. Disabling a bad category is a valid production strategy — it's better than keeping a noisy category that erodes trust in good ones

## Next unit

→ [Unit 1.2: Few-shot Prompting for Consistency](unit-1.2-few-shot-prompting.md)
