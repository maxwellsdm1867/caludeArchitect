# Unit 1.3: Structured Output via tool_use & JSON Schemas

**Task Statement 4.3** — Enforce structured output using tool use and JSON schemas

## The core principle

`tool_use` with JSON schemas is the **only reliable way** to guarantee schema-compliant structured output from Claude. Prompting for JSON works sometimes; `tool_use` works every time (for syntax — semantic errors are still possible).

## The tool_choice decision tree

This comes up in nearly every exam scenario. Memorize it.

| tool_choice value | Behavior | Use when |
|---|---|---|
| `"auto"` (default) | Model may return text OR call a tool | You want the model to decide whether extraction applies |
| `"any"` | Model MUST call a tool, picks which one | Multiple extraction schemas, unknown document type |
| `{"type":"tool","name":"..."}` | Model MUST call this specific tool | You need a specific extraction to run first (e.g., metadata before enrichment) |

### Exam trap: `"auto"` doesn't guarantee a tool call

If you set `tool_choice: "auto"` and the model decides the document doesn't need extraction, it returns conversational text instead. Use `"any"` to force it.

## Schema design principles

### Required vs optional (nullable) fields

**Critical exam concept:** If a source document might not contain a field, make that field **nullable/optional** in the schema. If you mark it required, the model will **fabricate a value** to satisfy the schema.

```json
{
  "purchase_date": {"type": ["string", "null"]},
  "warranty_expiry": {"type": ["string", "null"]}
}
```

### The enum + "other" pattern

For extensible categories:

```json
{
  "document_type": {
    "enum": ["invoice", "receipt", "contract", "other"]
  },
  "document_type_detail": {
    "type": ["string", "null"],
    "description": "If document_type is 'other', describe the type here"
  }
}
```

### The "unclear" escape valve

For ambiguous data:

```json
{
  "payment_status": {
    "enum": ["paid", "unpaid", "partial", "unclear"]
  }
}
```

## What schemas DON'T prevent

Strict JSON schemas via tool_use **eliminate syntax errors** but **do not prevent semantic errors**:

- Line items that don't sum to the stated total
- Values placed in the wrong field
- Dates in the wrong format despite format instructions
- Fabricated values for nullable fields when the model is uncertain

For semantic validation, you need a **validation-retry loop** (Unit 1.4).

## Hands-on exercises

→ See `notebooks/03-tool-use-schemas.ipynb`

### Exercise 1: Define an extraction tool

Build a tool with required fields, nullable fields, enum + "other" pattern. Process documents with missing fields.

### Failure exercise: All fields required

Mark every field as required. Process a document missing several fields. Watch the model hallucinate values to satisfy the schema. Then make them nullable.

### Exercise 2: tool_choice modes

Test the same extraction with `"auto"`, `"any"`, and forced selection. Observe when `"auto"` skips extraction.

## Exam-style practice question

**Scenario:** Your extraction pipeline processes invoices from multiple vendors. Some invoices include warranty information, others don't. Your JSON schema marks `warranty_expiry` as required. In production, 30% of extractions contain fabricated warranty dates.

**Question:** What's the most effective fix?

A) Add "do not fabricate warranty dates" to the system prompt  
B) Change `warranty_expiry` to a nullable field in the schema  
C) Add a validation step that checks warranty dates against a database  
D) Use `tool_choice: "any"` instead of forced tool selection  

<details>
<summary>Answer</summary>

**B.** The fabrication happens because the model must fill required fields. Making it nullable gives the model permission to return null when the information isn't present. A might help sometimes but isn't reliable. C is downstream validation, not prevention. D doesn't address schema design.

</details>

## Next unit

→ [Unit 1.4: Validation, Retry, and Feedback Loops](unit-1.4-validation-retry.md)
