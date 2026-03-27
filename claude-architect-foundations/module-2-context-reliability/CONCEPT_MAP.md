# Module 2 Concept Coverage Map
## Domain 5: Context Management & Reliability (15% of exam)

This map tracks every testable concept from the exam guide against our learning materials.

### Task Statement 5.1 — Context preservation across long interactions
**Covered in: Unit 2.1 + Cheat Sheet Section 1**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Context degradation curve: turns 1-10 accurate, 10-20 vague, 20+ generic | Knowledge | Unit 2.1 Sec 1 |
| Progressive summarization loses specific numbers, dates, identifiers | Knowledge | Unit 2.1 Sec 2 |
| "Lost in the middle" effect — middle of long contexts gets less attention | Knowledge | Unit 2.1 Sec 1 |
| Structured case facts blocks preserve critical data in system prompts | Knowledge | Unit 2.1 Sec 3 |
| Trimming tool output: extract structured findings before discarding raw output | Knowledge | Unit 2.1 Sec 2 |
| Building structured fact extraction that survives context compression | Skill | Unit 2.1 Challenge |
| Placing key data at context boundaries (beginning/end) for maximum attention | Skill | Unit 2.1 Sec 3, Challenge |

### Task Statement 5.2 — Escalation & ambiguity resolution
**Covered in: Unit 2.2 + Cheat Sheet Section 2**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Sentiment-based escalation fails in both directions (over-escalation + under-escalation) | Knowledge | Unit 2.2 Sec 1 |
| Customer explicit request for human overrides all other escalation logic | Knowledge | Unit 2.2 Sec 2 |
| Policy gaps require escalation — agent cannot invent policy | Knowledge | Unit 2.2 Sec 2 |
| Agent self-assessed confidence is unreliable for escalation decisions | Knowledge | Unit 2.2 Sec 3 |
| "No progress after N attempts" as a concrete escalation trigger | Knowledge | Unit 2.2 Sec 2 |
| Designing explicit trigger conditions (observable, deterministic) | Skill | Unit 2.2 Challenge |
| Handling frustrated-but-simple vs calm-but-complex scenarios | Skill | Unit 2.2 Challenge |
| Honoring customer preference for human interaction immediately | Skill | Unit 2.2 Sec 2 |

### Task Statement 5.3 — Error propagation in multi-agent systems
**Covered in: Unit 2.3 + Cheat Sheet Section 3**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Silent suppression anti-pattern: returning empty results as "success" on failure | Knowledge | Unit 2.3 Sec 1 |
| Catastrophic termination anti-pattern: exception kills entire workflow | Knowledge | Unit 2.3 Sec 1 |
| Structured error propagation: error_type + attempted_query + partial_results + alternatives | Knowledge | Unit 2.3 Sec 2 |
| Access failures ("couldn't look") vs empty results ("looked, found nothing") | Knowledge | Unit 2.3 Sec 3 |
| Local recovery: coordinator uses error context to retry, fallback, or proceed with partial | Knowledge | Unit 2.3 Sec 2 |
| Implementing structured error objects for subagent communication | Skill | Unit 2.3 Challenge |
| Building coordinators that distinguish failure types and choose recovery actions | Skill | Unit 2.3 Challenge |
| Avoiding silent suppression in try/except patterns | Skill | Unit 2.3 Sec 1, Challenge |

### Task Statement 5.4 — Large codebase context management
**Covered in: Unit 2.4 + Cheat Sheet Section 4**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Context degradation curve applies to codebase sessions (specific → vague → generic) | Knowledge | Unit 2.4 Sec 1 |
| Scratchpad files persist across compaction, crashes, subagent boundaries | Knowledge | Unit 2.4 Sec 2 |
| /compact is lossy — write to scratchpad before compacting | Knowledge | Unit 2.4 Sec 2 |
| Subagent delegation for scope exceeding single-context capacity | Knowledge | Unit 2.4 Sec 3 |
| "Bigger context window" does not fix lost-in-the-middle effect | Knowledge | Unit 2.4 Sec 1 |
| Building structured scratchpad content from session decisions | Skill | Unit 2.4 Challenge |
| Resuming sessions from scratchpad files after compaction or crash | Skill | Unit 2.4 Challenge |
| Delegating module-scoped work to subagents with shared scratchpad | Skill | Unit 2.4 Sec 3 |

### Task Statement 5.5 — Human review workflows & confidence calibration
**Covered in: Unit 2.5 + Cheat Sheet Section 5**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Aggregate accuracy masks per-field failures (97% overall, 32% on specific fields) | Knowledge | Unit 2.5 Sec 1 |
| Per-document-type accuracy reveals category-level problems | Knowledge | Unit 2.5 Sec 2 |
| Per-field accuracy is the actionable measurement level | Knowledge | Unit 2.5 Sec 2 |
| Stratified sampling over-represents hard cases in validation sets | Knowledge | Unit 2.5 Sec 2 |
| Field-level confidence enables targeted human review (review one field, not whole doc) | Knowledge | Unit 2.5 Sec 3 |
| Validation sets must represent production distribution, including hard cases | Knowledge | Unit 2.5 Sec 2 |
| Building field-level confidence routing systems | Skill | Unit 2.5 Challenge |
| Computing per-field accuracy breakdowns from raw extraction data | Skill | Unit 2.5 Challenge |
| Designing stratified validation sets for extraction systems | Skill | Unit 2.5 Sec 2 |

### Task Statement 5.6 — Information provenance & multi-source synthesis
**Covered in: Unit 2.6 + Cheat Sheet Section 6**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Claim-source mappings: every claim maps to its source(s) with date | Knowledge | Unit 2.6 Sec 1 |
| Conflicting sources: report ALL values with sources, don't silently pick one | Knowledge | Unit 2.6 Sec 2 |
| Temporal data prioritization: note dates, prefer recent for time-sensitive data | Knowledge | Unit 2.6 Sec 2 |
| Coverage gap reporting: explicitly state what was NOT found | Knowledge | Unit 2.6 Sec 3 |
| "Coherent summary" hides conflicts — surfaces claim-source mappings instead | Knowledge | Unit 2.6 Sec 1 |
| Building provenance-tracked synthesis with conflict detection | Skill | Unit 2.6 Challenge |
| Implementing coverage gap reporting for unfound topics | Skill | Unit 2.6 Challenge |
| Handling temporal conflicts (growth vs disagreement) with source dates | Skill | Unit 2.6 Sec 2, Challenge |

---

## Coverage Verification

- Task Statement 5.1: 7/7 concepts covered
- Task Statement 5.2: 8/8 concepts covered
- Task Statement 5.3: 8/8 concepts covered
- Task Statement 5.4: 8/8 concepts covered
- Task Statement 5.5: 9/9 concepts covered
- Task Statement 5.6: 8/8 concepts covered
- **Total: 48/48 testable concepts from Domain 5**

## Cross-Reference: Exam Scenarios Using Domain 5

| Scenario | How Domain 5 appears |
|----------|---------------------|
| Scenario 1: Customer Support | Escalation triggers, context preservation across long conversations, policy gap handling |
| Scenario 2: Multi-Agent Research | Error propagation between subagents, provenance tracking, conflict detection |
| Scenario 3: Codebase Migration | Context degradation curve, scratchpad files, /compact, subagent delegation |
| Scenario 4: Document Extraction | Aggregate accuracy masking, per-field confidence, stratified sampling, human review routing |
| Scenario 5: CI/CD Pipeline | Error propagation in pipeline stages, structured error context for recovery |
| Scenario 6: Data Extraction | Multi-source synthesis, coverage gap reporting, field-level review workflows |
