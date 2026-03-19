# Unit 1.6: Multi-Instance and Multi-Pass Review

**Task Statement 4.6** — Design multi-instance and multi-pass review architectures

## The core principle

A model that just generated code **retains its reasoning context**, making it less likely to question its own decisions. An independent review instance (without that reasoning context) catches more bugs.

## Key concepts

### Self-review bias

When Claude generates code and then reviews it in the same session, it has access to the reasoning that led to each decision. This makes it systematically less likely to catch:
- Assumptions it made during generation
- Edge cases it considered and dismissed
- Patterns it chose that have subtle flaws

### Independent instance review

Spawn a **new Claude instance** with only the code (not the generation reasoning). This instance evaluates the code on its merits, without being anchored to the original reasoning.

### Multi-pass for large PRs

For reviews spanning many files (the exam uses 14-file PR as its example):

```
Pass 1: Per-file local analysis
  → Each file reviewed individually for local issues
  → Consistent depth across all files

Pass 2: Cross-file integration analysis  
  → Focus on data flow between files
  → API contract consistency
  → Shared state mutations
```

This prevents **attention dilution** — the root cause of inconsistent review depth when all files are analyzed together.

## Exam trap: "use a bigger context window"

A larger context window does NOT solve attention dilution. The model can hold more text but still allocates attention unevenly. Splitting into focused passes is the correct solution.

## Hands-on exercises

→ See `notebooks/06-multi-pass-review.ipynb`

## Module 1 complete

→ Continue to [Module 2: Context Management & Reliability](../module-2-context-reliability/)
