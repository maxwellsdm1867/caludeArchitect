# Module 5 Concept Coverage Map
## Domain 1: Agentic Architecture & Orchestration (27% of exam — highest weight)

This map tracks every testable concept from the exam guide against our learning materials.

### Task Statement 1.1 — The agentic loop lifecycle
**Covered in: Unit 5.1 + Cheat Sheet Section 1**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| stop_reason-driven control flow ("tool_use" vs "end_turn") | Knowledge | Unit 5.1 Sec 1 |
| Tool result appending: append full assistant response + tool results to messages | Knowledge | Unit 5.1 Sec 2 |
| Model-driven vs pre-configured loops (model decides, not your code) | Knowledge | Unit 5.1 Sec 1 |
| Anti-pattern: parsing natural language for termination | Knowledge | Unit 5.1 Sec 2 |
| Anti-pattern: iteration caps as primary stopping mechanism | Knowledge | Unit 5.1 Sec 2 |
| Anti-pattern: checking for text content as completion signal | Knowledge | Unit 5.1 Sec 2 |
| Safety caps as safety nets (not primary mechanism) | Knowledge | Unit 5.1 Sec 1 |
| Building a while-loop agent with stop_reason control | Skill | Unit 5.1 Challenge |
| Handling mixed content responses (text + tool_use blocks) | Skill | Unit 5.1 Challenge |

### Task Statement 1.2 — Coordinator-subagent patterns
**Covered in: Unit 5.2 + Cheat Sheet Section 2**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Hub-and-spoke architecture: coordinator dispatches to focused subagents | Knowledge | Unit 5.2 Sec 1 |
| Subagents do NOT inherit coordinator context (must pass explicitly) | Knowledge | Unit 5.2 Sec 1 |
| Tool scoping: 4-5 tools per subagent (18+ degrades selection) | Knowledge | Unit 5.2 Sec 2 |
| All communication flows through coordinator (no direct subagent comms) | Knowledge | Unit 5.2 Sec 2 |
| Parallel dispatch: multiple Task calls in one coordinator response | Knowledge | Unit 5.2 Sec 2 |
| Building a coordinator that dispatches to scoped subagents | Skill | Unit 5.2 Challenge |
| Designing subagent tool sets for focused domains | Skill | Unit 5.2 Challenge |
| Synthesizing results from multiple subagents | Skill | Unit 5.2 Challenge |

### Task Statement 1.3 — Subagent invocation & context passing
**Covered in: Unit 5.3 + Cheat Sheet Section 3**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Task tool: fresh context, only the prompt you provide | Knowledge | Unit 5.3 Sec 1 |
| fork_session: snapshot of current context (for exploratory branches) | Knowledge | Unit 5.3 Sec 1 |
| allowedTools parameter for programmatic tool scoping | Knowledge | Unit 5.3 Sec 1 |
| Explicit context in prompts: include only what the subagent needs | Knowledge | Unit 5.3 Sec 2 |
| Parallel Task calls for independent subtasks | Knowledge | Unit 5.3 Sec 1 |
| Task vs fork_session: when to use each | Knowledge | Unit 5.3 Sec 1 |
| Building focused subagent prompts with explicit data and output format | Skill | Unit 5.3 Challenge |
| Scoping context to prevent pollution | Skill | Unit 5.3 Challenge |
| Validating context isolation between subagents | Skill | Unit 5.3 Challenge |

### Task Statement 1.4 — Enforcement & handoff patterns
**Covered in: Unit 5.4 + Cheat Sheet Section 4**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Programmatic enforcement for critical rules (financial, safety, compliance) | Knowledge | Unit 5.4 Sec 1 |
| Prompt-based guidance for non-critical rules (style, best practices) | Knowledge | Unit 5.4 Sec 1 |
| Prompts have non-zero failure rate — unacceptable for critical rules | Knowledge | Unit 5.4 Sec 1 |
| Prerequisite gates: block tool execution until condition is verified in code | Knowledge | Unit 5.4 Sec 1 |
| Structured handoff summaries (what/state/remaining, not transcripts) | Knowledge | Unit 5.4 Sec 2 |
| Building code-level prerequisite gates | Skill | Unit 5.4 Challenge |
| Designing structured handoff summaries | Skill | Unit 5.4 Challenge |
| Classifying rules as programmatic vs prompt-based | Skill | Unit 5.4 Challenge |

### Task Statement 1.5 — Agent SDK hooks
**Covered in: Unit 5.5 + Cheat Sheet Section 5**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| PostToolUse hooks for output normalization (dates, currencies, formats) | Knowledge | Unit 5.5 Sec 1 |
| PreToolCall hooks for access control and input validation | Knowledge | Unit 5.5 Sec 1 |
| Hooks are deterministic (code-level, not model-level) | Knowledge | Unit 5.5 Sec 2 |
| Hooks vs prompts: hooks for guarantees, prompts for guidance | Knowledge | Unit 5.5 Sec 2 |
| PII redaction via PostToolUse hooks | Knowledge | Unit 5.5 Sec 2 |
| Implementing PostToolUse hooks for data normalization | Skill | Unit 5.5 Challenge |
| Implementing PreToolCall hooks for role-based access control | Skill | Unit 5.5 Challenge |
| Building a full hook pipeline (pre-check + post-normalization) | Skill | Unit 5.5 Challenge |

### Task Statement 1.6 — Task decomposition strategies
**Covered in: Unit 5.6 + Cheat Sheet Section 6**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Prompt chaining for predictable pipelines (extract/validate/format) | Knowledge | Unit 5.6 Sec 1 |
| Dynamic decomposition for variable tasks (research, debugging) | Knowledge | Unit 5.6 Sec 1 |
| Per-file + cross-file analysis for multi-file reviews | Knowledge | Unit 5.6 Sec 2 |
| Narrow decomposition risk: misses coverage (creative industries example) | Knowledge | Unit 5.6 Sec 3 |
| Attention dilution: large inputs cause shallow analysis | Knowledge | Unit 5.6 Sec 2 |
| Selecting the right decomposition strategy for a task | Skill | Unit 5.6 Challenge |
| Building per-file analysis summaries for cross-file review | Skill | Unit 5.6 Challenge |
| Detecting cross-file integration bugs (type mismatches, API contracts) | Skill | Unit 5.6 Challenge |

### Task Statement 1.7 — Session state & resumption
**Covered in: Unit 5.7 + Cheat Sheet Section 7**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| --resume: restores full prior context (appropriate when data unchanged) | Knowledge | Unit 5.7 Sec 1 |
| Stale context danger: resumed session operates on outdated assumptions | Knowledge | Unit 5.7 Sec 2 |
| Fresh session + summary pattern: avoids stale context | Knowledge | Unit 5.7 Sec 1 |
| fork_session for parallel exploration with shared context | Knowledge | Unit 5.7 Sec 1 |
| Deciding when to resume vs start fresh based on data changes | Skill | Unit 5.7 Challenge |
| Building structured session summaries for fresh sessions | Skill | Unit 5.7 Challenge |
| Detecting stale context by comparing prior and current state | Skill | Unit 5.7 Challenge |

---

## Coverage Verification

- Task Statement 1.1: 9/9 concepts covered
- Task Statement 1.2: 8/8 concepts covered
- Task Statement 1.3: 9/9 concepts covered
- Task Statement 1.4: 8/8 concepts covered
- Task Statement 1.5: 8/8 concepts covered
- Task Statement 1.6: 8/8 concepts covered
- Task Statement 1.7: 7/7 concepts covered
- **Total: 57/57 testable concepts from Domain 1**

## Key Exam Traps (Domain 1)

| Trap | Truth |
|------|-------|
| Subagents inherit coordinator context | FALSE — must pass explicitly |
| Narrow decomposition is always better | FALSE — misses coverage |
| More tools = more capable agent | FALSE — 18+ tools degrades selection |
| Self-review in same session is effective | FALSE — independent instance catches more |
| Prompt instructions guarantee compliance | FALSE — non-zero failure rate |
| Checking for text means model is done | FALSE — text and tool_use can coexist |
| --resume is always efficient | FALSE — stale context when data changed |

## Cross-Reference: Exam Scenarios Using Domain 1

| Scenario | How Domain 1 appears |
|----------|---------------------|
| Scenario 1: Agentic coding assistant | Agentic loop, tool management, session resumption |
| Scenario 2: Customer service agent | Coordinator-subagent, enforcement gates, handoff summaries |
| Scenario 3: Research assistant | Dynamic decomposition, parallel subagents, context passing |
| Scenario 4: Multi-agent pipeline | Hooks for normalization, task decomposition, cross-file analysis |
| Scenario 5: CI/CD review agent | Per-file + cross-file, stale context management, safety caps |
| Scenario 6: Compliance system | Programmatic enforcement, PreToolCall hooks, prerequisite gates |
