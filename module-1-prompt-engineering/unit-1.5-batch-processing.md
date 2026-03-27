# Unit 1.5: Batch Processing Strategies

**Task Statement 4.5** — Design efficient batch processing strategies

## The core principle

The **Message Batches API** offers 50% cost savings with a 24-hour processing window and no latency SLA. This makes it ideal for overnight/weekly jobs and completely inappropriate for blocking workflows.

## The decision matrix

| Workflow | Blocking? | Latency requirement | API choice |
|----------|-----------|--------------------|-|
| Pre-merge code review | Yes — devs wait | Seconds to minutes | **Synchronous API** |
| Nightly tech debt report | No | Overnight | **Batch API** |
| Weekly security audit | No | Days | **Batch API** |
| PR comment generation | Yes — blocks merge | Minutes | **Synchronous API** |
| Training data classification | No | Flexible | **Batch API** |

## Key facts for the exam

1. **50% cost savings** — the primary benefit
2. **Up to 24-hour processing window** — no guaranteed latency SLA
3. **custom_id** — your correlation key between requests and responses
4. **No multi-turn tool calling** — cannot execute tools mid-request and return results
5. **Failure handling** — resubmit only failed documents (identified by `custom_id`) with modifications (e.g., chunking oversized docs)

## Exam trap: "often faster than 24 hours"

The exam will present scenarios where someone says "batch usually finishes in a few hours, so let's use it for pre-merge checks." This is WRONG. "Usually fast" is not an SLA. If it takes 23 hours one day, your developers are blocked all day.

## Calculating batch submission frequency

If your SLA requires results within 30 hours and batch processing can take up to 24 hours, you need to submit batches at most every 6 hours (30 - 24 = 6 hour buffer).

## Hands-on exercises

→ See `notebooks/05-batch-api.ipynb`

## Next unit

→ [Unit 1.6: Multi-Instance and Multi-Pass Review](unit-1.6-multi-pass-review.md)
