# Module 1: Prompt Engineering & Structured Output

**Exam Domain 4 — 20% of scored content**  
**Phase 1 (Foundations) — No prerequisites**

## Why this is Module 1

Every other domain depends on writing good prompts. Tool descriptions are prompts. Agent system prompts are prompts. CLAUDE.md files are prompts. Escalation criteria are prompts with few-shot examples. Master this and everything else clicks.

## What the exam tests

The exam doesn't test whether you can write a prompt. It tests whether you know **which prompting technique to reach for** in a specific production scenario, and **why the alternatives fail**. The distractors are always things that sound reasonable but don't work.

## Units

| Unit | Topic | Key exam concepts |
|------|-------|-------------------|
| [1.1](unit-1.1-explicit-criteria.md) | Explicit criteria over vague instructions | Precision vs "be conservative", categorical criteria, false positive impact |
| [1.2](unit-1.2-few-shot-prompting.md) | Few-shot prompting for consistency | 2-4 targeted examples, ambiguous-case reasoning, format consistency |
| [1.3](unit-1.3-structured-output.md) | Structured output via tool_use & JSON schemas | tool_choice modes, nullable fields, enum + "other" pattern |
| [1.4](unit-1.4-validation-retry.md) | Validation, retry, and feedback loops | Retry-with-error-feedback, when retries work vs don't, detected_pattern |
| [1.5](unit-1.5-batch-processing.md) | Batch processing strategies | Message Batches API, 50% savings, 24h window, custom_id, no multi-turn |
| [1.6](unit-1.6-multi-pass-review.md) | Multi-instance and multi-pass review | Self-review bias, independent instances, per-file + cross-file passes |

## Notebooks

| Notebook | What you'll build |
|----------|-------------------|
| [01-explicit-vs-vague.ipynb](notebooks/01-explicit-vs-vague.ipynb) | Compare vague vs precise review prompts against real code |
| [02-few-shot-extraction.ipynb](notebooks/02-few-shot-extraction.ipynb) | Build extraction with/without few-shot examples, measure accuracy |
| [03-tool-use-schemas.ipynb](notebooks/03-tool-use-schemas.ipynb) | Define extraction tools with JSON schemas, test nullable fields |
| [04-validation-retry.ipynb](notebooks/04-validation-retry.ipynb) | Build a validation-retry loop with error feedback |
| [05-batch-api.ipynb](notebooks/05-batch-api.ipynb) | Submit batch jobs, handle failures by custom_id |
| [06-multi-pass-review.ipynb](notebooks/06-multi-pass-review.ipynb) | Same-session review vs independent instance review |

## Key mental models

### The precision ladder

```
Worst:  "Review this code"
Bad:    "Review this code carefully and report issues"  
Meh:    "Review this code, be conservative, only report high-confidence findings"
Good:   "Flag comments only when claimed behavior contradicts actual code behavior"
Best:   [Good] + 3 few-shot examples showing borderline cases with reasoning
```

Each step up the ladder reduces false positives dramatically. The exam tests whether you know to jump to "Good" or "Best" rather than trying to improve "Meh."

### The structured output decision tree

```
Need structured output?
├── Need guaranteed schema compliance? → tool_use with JSON schema
│   ├── Know which schema to use? → tool_choice: forced (specific tool name)
│   ├── Multiple schemas, unknown doc type? → tool_choice: "any"
│   └── Model should decide whether to extract? → tool_choice: "auto"
└── Schema compliance optional? → prompt-based JSON (unreliable, avoid in production)
```

### When to retry vs give up

```
Extraction failed validation?
├── Format/structural error (wrong date format, missing field that exists in doc) → RETRY with error feedback
├── Semantic error (values don't sum, contradictory fields) → RETRY with self-correction prompt
└── Information absent from source document → DO NOT RETRY (it won't appear on retry)
```

## Common exam traps in this domain

1. **"Be conservative" sounds right but fails.** The exam will present "add instructions to be conservative" as a distractor. It never works — the model has no calibrated sense of "conservative."

2. **Few-shot examples vs detailed instructions.** When both are answer options and the problem is inconsistent output format, few-shot examples win. The exam tests this repeatedly.

3. **tool_choice: "auto" doesn't guarantee a tool call.** The model may return text instead. Use "any" to force a tool call, or forced selection for a specific tool.

4. **Strict schemas eliminate syntax errors, NOT semantic errors.** The model can produce valid JSON where line items don't sum to the total. Schema compliance ≠ correctness.

5. **Batch API has no latency SLA.** "Usually finishes in a few hours" is NOT an acceptable basis for blocking workflows. Exam questions test this distinction explicitly.
