# Unit 1.4: Validation, Retry, and Feedback Loops

**Task Statement 4.4** — Implement validation, retry, and feedback loops for extraction quality

## The core principle

When extraction fails validation, **retry-with-error-feedback** works — but only when the information exists in the source document. Retrying for absent information is wasted compute.

## The retry decision

```
Validation failed?
├── Format mismatch (date format wrong, number has currency symbol)
│   → RETRY with: original doc + failed extraction + specific error
│   → Success rate: HIGH
├── Structural error (field in wrong place, nested incorrectly)  
│   → RETRY with: original doc + failed extraction + specific error
│   → Success rate: HIGH
├── Semantic error (values don't sum, contradictory fields)
│   → RETRY with: self-correction prompt ("extract calculated_total alongside stated_total")
│   → Success rate: MEDIUM
└── Information absent from source document
    → DO NOT RETRY — the data doesn't exist
    → Return null/incomplete with confidence flag
```

## Key concepts

### Retry-with-error-feedback pattern

Don't just retry blindly. Include the specific validation error:

```python
retry_prompt = f"""The previous extraction from this document failed validation.

Original document: {document}

Failed extraction: {failed_result}

Validation error: {specific_error}
# e.g., "purchase_date '2024-13-01' is not a valid date — month cannot exceed 12"

Please re-extract, correcting the specific error noted above."""
```

### Self-correction for semantic validation

For catching internal contradictions:

```json
{
  "stated_total": "$1,250.00",
  "calculated_total": "$1,350.00",
  "line_items": [...],
  "conflict_detected": true,
  "conflict_description": "Sum of line items ($1,350) does not match stated total ($1,250)"
}
```

### The detected_pattern field

For building feedback loops on code review findings:

```json
{
  "location": "auth.py:42",
  "issue": "Unchecked null return",
  "severity": "high",
  "detected_pattern": "method_call_without_null_check"
}
```

When developers dismiss findings, `detected_pattern` lets you analyze which patterns produce false positives systematically.

## Hands-on exercises

→ See `notebooks/04-validation-retry.ipynb`

## Next unit

→ [Unit 1.5: Batch Processing Strategies](unit-1.5-batch-processing.md)
