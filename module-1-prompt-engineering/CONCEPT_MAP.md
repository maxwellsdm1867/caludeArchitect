# Module 1 Concept Coverage Map
## Domain 4: Prompt Engineering & Structured Output (20% of exam)

This map tracks every testable concept from the exam guide against our learning materials.

### Task Statement 4.1 — Explicit criteria to reduce false positives
**Covered in: Unit 1.1 + Cheat Sheet Section 1**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Explicit criteria > vague instructions ("flag when X contradicts Y" vs "check accuracy") | Knowledge | Unit 1.1 Sec 1 |
| "Be conservative" / "only report high-confidence" fail to improve precision | Knowledge | Unit 1.1 Sec 2 |
| False positive rates in one category erode trust in accurate categories | Knowledge | Unit 1.1 Sec 3 |
| Writing specific DO flag / DON'T flag review criteria | Skill | Unit 1.1 Sec 4, Challenge |
| Temporarily disabling high-FP categories to restore trust | Skill | Unit 1.1 Sec 3 |
| Defining severity criteria with concrete code examples per level | Skill | Unit 1.1 Challenge |

### Task Statement 4.2 — Few-shot prompting for consistency
**Covered in: Unit 1.2 + Cheat Sheet Section 2**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Few-shot = most effective for consistent, actionable output when instructions fail | Knowledge | Unit 1.2 Sec 1 |
| Examples demonstrate ambiguous-case handling (reasoning for choice over alternatives) | Knowledge | Unit 1.2 Sec 3 |
| Few-shot enables generalization to novel patterns (not just pattern matching) | Knowledge | Unit 1.2 Sec 3 |
| Few-shot reduces hallucination in extraction (informal measurements, varied formats) | Knowledge | Unit 1.2 Sec 5 |
| Creating 2-4 targeted examples with reasoning for ambiguous scenarios | Skill | Unit 1.2 Sec 3, Challenge |
| Including examples showing specific output format for consistency | Skill | Unit 1.2 Challenge |
| Examples distinguishing acceptable patterns from genuine issues | Skill | Unit 1.2 Sec 4 |
| Examples for varied document structures (citations, bibliographies, etc.) | Skill | Unit 1.2 Sec 5 |
| Examples showing correct extraction with varied formats, null handling | Skill | Unit 1.2 Challenge |

### Task Statement 4.3 — Structured output via tool_use and JSON schemas
**Covered in: Unit 1.3 + Cheat Sheet Section 3**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| tool_use + JSON schemas = guaranteed schema compliance, no syntax errors | Knowledge | Unit 1.3 Sec 1 |
| tool_choice: "auto" vs "any" vs forced — behavior differences | Knowledge | Unit 1.3 Sec 2 |
| Strict schemas eliminate syntax errors but NOT semantic errors | Knowledge | Unit 1.3 Sec 4 |
| Required vs optional fields; enum + "other" + detail pattern | Knowledge | Unit 1.3 Sec 3 |
| Defining extraction tools with JSON schemas | Skill | Unit 1.3 Challenge |
| Setting tool_choice: "any" for guaranteed output when doc type unknown | Skill | Unit 1.3 Challenge |
| Forcing specific tool for ordering (metadata before enrichment) | Skill | Unit 1.3 Sec 2 |
| Designing nullable fields to prevent fabrication | Skill | Unit 1.3 Challenge |
| Adding enum "unclear" + "other" + detail fields | Skill | Unit 1.3 Sec 3, Challenge |
| Format normalization rules alongside strict schemas | Skill | Unit 1.3 Sec 3 |

### Task Statement 4.4 — Validation, retry, and feedback loops
**Covered in: Unit 1.4 + Cheat Sheet Section 4**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Retry-with-error-feedback: append specific validation errors on retry | Knowledge | Unit 1.4 Sec 3 |
| Retries are ineffective when information is absent from source | Knowledge | Unit 1.4 Sec 2 |
| detected_pattern field for systematic false-positive analysis | Knowledge | Unit 1.4 Sec 5 |
| Semantic vs syntax validation errors (values don't sum vs wrong format) | Knowledge | Unit 1.4 Sec 2 |
| Implementing retry with original doc + failed extraction + specific error | Skill | Unit 1.4 Challenge |
| Identifying when retries will be ineffective (absent data) | Skill | Unit 1.4 Challenge |
| Adding detected_pattern to enable FP analysis | Skill | Unit 1.4 Sec 5 |
| Self-correction: calculated_total vs stated_total + conflict_detected | Skill | Unit 1.4 Sec 4 |

### Task Statement 4.5 — Batch processing strategies
**Covered in: Unit 1.5 + Cheat Sheet Section 5**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Message Batches API: 50% savings, 24h window, no latency SLA | Knowledge | Unit 1.5 Sec 1 |
| Batch for non-blocking only; synchronous for blocking workflows | Knowledge | Unit 1.5 Sec 2 |
| No multi-turn tool calling within batch requests | Knowledge | Unit 1.5 Sec 3 |
| custom_id for correlating request/response pairs | Knowledge | Unit 1.5 Sec 3 |
| Matching API to latency requirements (sync vs batch) | Skill | Unit 1.5 Challenge |
| Calculating submission frequency from SLA constraints | Skill | Unit 1.5 Sec 4, Challenge |
| Handling batch failures: resubmit by custom_id, chunk oversized docs | Skill | Unit 1.5 Sec 6, Challenge |
| Prompt refinement on sample set before batch processing | Skill | Unit 1.5 Sec 7 |

### Task Statement 4.6 — Multi-instance and multi-pass review
**Covered in: Unit 1.6 + Cheat Sheet Section 6**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Self-review limitations: retains reasoning context → misses own issues | Knowledge | Unit 1.6 Sec 2 |
| Independent instances (no prior context) are more effective | Knowledge | Unit 1.6 Sec 3 |
| Multi-pass: per-file local + cross-file integration to avoid attention dilution | Knowledge | Unit 1.6 Sec 4 |
| Using independent Claude instance for review (no generation context) | Skill | Unit 1.6 Challenge |
| Splitting large reviews: per-file passes + integration pass | Skill | Unit 1.6 Challenge |
| Running verification passes with confidence alongside findings | Skill | Unit 1.6 Challenge |

---

## Coverage Verification

- Task Statement 4.1: 6/6 concepts covered
- Task Statement 4.2: 9/9 concepts covered
- Task Statement 4.3: 10/10 concepts covered
- Task Statement 4.4: 8/8 concepts covered
- Task Statement 4.5: 8/8 concepts covered
- Task Statement 4.6: 6/6 concepts covered
- **Total: 47/47 testable concepts from Domain 4**

## Cross-Reference: Exam Scenarios Using Domain 4

| Scenario | How Domain 4 appears |
|----------|---------------------|
| Scenario 5: CI/CD | Explicit criteria for review prompts, multi-pass review, batch for overnight analysis |
| Scenario 6: Data Extraction | tool_use schemas, nullable fields, validation-retry, few-shot for varied formats, batch processing |
