# Unit 1.2: Few-Shot Prompting for Consistency

**Task Statement 4.2** — Apply few-shot prompting to improve output consistency and quality

## The core principle

When detailed instructions alone produce inconsistent output, **2-4 targeted few-shot examples** are the single most effective fix. The exam treats this as a first-line solution, not a last resort.

Few-shot examples work because they demonstrate *judgment* — not just rules. A rule says "handle ambiguous cases." An example shows what ambiguous looks like and what the correct response is.

## What the exam expects you to know

### Knowledge areas

1. Few-shot examples are **the most effective technique** for achieving consistently formatted, actionable output when instructions alone are inconsistent
2. Examples should demonstrate **ambiguous-case handling** — showing reasoning for why one action was chosen over plausible alternatives
3. Few-shot examples enable the model to **generalize** to novel patterns, not just match pre-specified cases
4. Few-shot examples **reduce hallucination** in extraction tasks (handling informal measurements, varied document structures)

### Skills tested

1. Creating **2-4 targeted examples** for ambiguous scenarios with reasoning
2. Including examples that demonstrate **specific output format** (location, issue, severity, suggested fix)
3. Providing examples that **distinguish acceptable patterns from genuine issues** to reduce false positives while enabling generalization
4. Using examples to handle **varied document structures** (inline citations vs bibliographies, narrative vs tables)
5. Adding examples showing **correct extraction from varied formats** to fix empty/null extraction of required fields

## When few-shot beats instructions

| Situation | Instructions alone | Few-shot wins? |
|-----------|-------------------|----------------|
| Output format inconsistency | Model varies between bullet points, paragraphs, JSON | ✅ Yes — examples set the format |
| Ambiguous tool selection | Model picks wrong tool for edge cases | ✅ Yes — examples show reasoning |
| False positives in code review | Model flags acceptable patterns | ✅ Yes — examples show what to skip |
| Extraction from varied doc formats | Model misses fields in unusual layouts | ✅ Yes — examples show each layout |
| Simple factual task | "What is 2+2?" | ❌ No — no ambiguity to resolve |

## Example structure for the exam

The exam tests whether you know the **anatomy of a good few-shot example**:

```
Example 1 (ambiguous case — chose action A):
  Input: "My order hasn't arrived and I want to cancel"
  Action: lookup_order (not cancel_order)
  Reasoning: Customer said "cancel" but the root issue is non-delivery.
             Look up the order first to check shipping status before canceling.

Example 2 (ambiguous case — chose action B):
  Input: "Cancel order #1234, I already bought it elsewhere"
  Action: cancel_order
  Reasoning: Customer explicitly wants cancellation, not a status check.
             The decision is clear — proceed with cancel directly.
```

Notice: each example includes the **reasoning for why** — this is what enables generalization. Without reasoning, the model just pattern-matches on keywords.

## Hands-on exercises

→ See `notebooks/02-few-shot-extraction.ipynb`

### Exercise 1: Extraction without examples

Run extraction against 5 documents with varied formats (invoice, receipt, contract, email, handwritten note). Observe inconsistent field extraction.

### Exercise 2: Add 3 targeted examples

Add few-shot examples showing correct extraction from each document type. Re-run and measure consistency improvement.

### Failure exercise: Happy-path-only examples

Provide examples that only show clean, well-formatted documents. Run against messy documents. Watch the model hallucinate instead of returning null for missing fields.

## Exam-style practice question

**Scenario:** Your agent handles customer requests but inconsistently selects between `lookup_order` and `check_shipping` for ambiguous queries like "where's my package?" You've added detailed tool descriptions and instructions but the routing is still unreliable.

**Question:** What should you try next?

A) Add a routing classifier that parses user intent before the agent processes the request  
B) Add 3-4 few-shot examples showing correct tool selection for ambiguous queries, with reasoning for why one tool was chosen over the other  
C) Consolidate `lookup_order` and `check_shipping` into a single `order_status` tool  
D) Increase the system prompt detail to 2000+ tokens with comprehensive routing rules  

<details>
<summary>Answer</summary>

**B.** Few-shot examples with reasoning are the most effective technique for resolving ambiguous tool selection when instructions alone aren't working. A is over-engineered for this stage. C changes the architecture instead of fixing the prompt. D adds tokens without adding the *judgment* that examples provide.

</details>

## Next unit

→ [Unit 1.3: Structured Output via tool_use & JSON Schemas](unit-1.3-structured-output.md)
