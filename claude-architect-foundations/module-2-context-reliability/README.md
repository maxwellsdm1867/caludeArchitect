# Module 2: Context Management & Reliability

**Exam Domain 5 — 15% of scored content**  
**Phase 1 (Foundations) — No prerequisites, parallel with Module 1**

## Why this is Module 2

Context management is the hidden foundation of everything else. Agents fail when context degrades. Tools fail when errors propagate poorly. Multi-agent systems fail when subagents lose provenance information. You need these mental models before building anything complex.

## Units

| Unit | Topic | Key exam concepts |
|------|-------|-------------------|
| [2.1](unit-2.1-context-preservation/overview.html) | Context preservation across long interactions | Progressive summarization risks, "lost in the middle" effect, case facts blocks, trimming tool output |
| [2.2](unit-2.2-escalation-patterns/overview.html) | Escalation & ambiguity resolution | Explicit triggers, sentiment is unreliable, customer preference honoring, policy gaps |
| [2.3](unit-2.3-error-propagation/overview.html) | Error propagation in multi-agent systems | Structured error context, access failures vs empty results, local recovery, anti-patterns |
| [2.4](unit-2.4-codebase-context/overview.html) | Large codebase context management | Context degradation, scratchpad files, subagent delegation, /compact, crash recovery |
| [2.5](unit-2.5-human-review/overview.html) | Human review workflows & confidence calibration | Aggregate accuracy masking, stratified sampling, field-level confidence, validation sets |
| [2.6](unit-2.6-provenance/overview.html) | Information provenance & multi-source synthesis | Claim-source mappings, conflicting sources, temporal data, coverage gap reporting |

## Key mental models

### The context degradation curve

In extended sessions, Claude's reliability follows a curve:
- **Turns 1-10:** Accurate references to specific classes, functions, variables
- **Turns 10-20:** Starts saying "the pattern we discussed" instead of specific names
- **Turns 20+:** References "typical patterns" — a sign context has effectively degraded

**Fix:** Scratchpad files, subagent delegation, structured fact extraction, `/compact`.

### The error propagation pyramid

```
Anti-pattern 1: Silent suppression
  Subagent fails → returns empty results as "success" → coordinator proceeds with missing data

Anti-pattern 2: Catastrophic termination  
  Subagent fails → exception propagates → entire workflow terminates

Correct pattern: Structured propagation
  Subagent fails → returns {error_type, attempted_query, partial_results, alternatives}
  → Coordinator decides: retry? alternative approach? proceed with partial? escalate?
```

### The escalation decision tree

```
Should the agent escalate?
├── Customer explicitly requests human → YES, immediately (don't investigate first)
├── Policy gap (customer's request not covered by policy) → YES
├── No progress after reasonable attempt → YES
├── Customer is frustrated but issue is within capability → NO (offer resolution, escalate if they insist)
└── Agent self-reports low confidence → UNRELIABLE signal (don't use for escalation)
```

## Common exam traps in this domain

1. **Sentiment-based escalation sounds reasonable but fails.** Frustrated customers with simple issues get escalated; calm customers with complex issues don't.
2. **Aggregate accuracy (97%) masks field-level failures.** Always check per-document-type and per-field.
3. **Progressive summarization loses numbers.** "$1,234.56 on order #789" becomes "a refund was discussed."
4. **"Lost in the middle" is real.** Put key findings at the beginning and end of long inputs.
