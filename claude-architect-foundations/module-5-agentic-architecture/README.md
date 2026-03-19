# Module 5: Agentic Architecture & Orchestration

**Exam Domain 1 — 27% of scored content (highest weight)**  
**Phase 3 (Integration) — Prerequisites: ALL of Modules 1–4**

## Why this is Module 5 (not Module 1)

This is the highest-weighted domain on the exam, but it **integrates everything else**. Agents orchestrate prompts (Module 1), manage context (Module 2), run inside Claude Code (Module 3), and call tools (Module 4). Without those foundations, agent architecture is just theory.

## Units

| Unit | Topic | Key exam concepts |
|------|-------|-------------------|
| [5.1](unit-5.1-agentic-loop.md) | The agentic loop lifecycle | stop_reason ("tool_use" vs "end_turn"), tool result appending, model-driven vs pre-configured |
| [5.2](unit-5.2-coordinator-subagent.md) | Coordinator-subagent patterns | Hub-and-spoke, isolated subagent context, task decomposition, narrow decomposition risks |
| [5.3](unit-5.3-subagent-context.md) | Subagent invocation & context passing | Task tool, allowedTools, explicit context in prompts, parallel Task calls, fork_session |
| [5.4](unit-5.4-enforcement-handoff.md) | Enforcement & handoff patterns | Programmatic vs prompt-based, prerequisite gates, structured handoff summaries |
| [5.5](unit-5.5-hooks.md) | Agent SDK hooks | PostToolUse for normalization, tool call interception for compliance, hooks vs prompts |
| [5.6](unit-5.6-task-decomposition.md) | Task decomposition strategies | Prompt chaining vs dynamic decomposition, per-file + cross-file, adaptive investigation |
| [5.7](unit-5.7-session-management.md) | Session state & resumption | --resume, fork_session, stale context, fresh session + summary |

## Key mental models

### The agentic loop

```python
while True:
    response = client.messages.create(model=MODEL, messages=messages, tools=tools)
    
    if response.stop_reason == "end_turn":
        break  # Model is done — present final response to user
    
    if response.stop_reason == "tool_use":
        # Execute each tool call, append results to messages
        for tool_call in response.content:
            if tool_call.type == "tool_use":
                result = execute_tool(tool_call.name, tool_call.input)
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": [tool_result_block]})
        continue  # Next iteration — model sees tool results and decides next action
```

### Anti-patterns the exam tests

| Anti-pattern | Why it fails |
|---|---|
| Parsing natural language to detect loop termination | "I've completed the first step" triggers false termination |
| Arbitrary iteration caps as primary stopping mechanism | Cuts off legitimate multi-step reasoning |
| Checking for assistant text content as completion | Model may emit text AND tool calls in same response |

### The coordinator-subagent architecture

```
Coordinator (has Task tool + orchestration logic)
├── Subagent A: Web Search (tools: search, fetch)
├── Subagent B: Document Analysis (tools: read, extract)
└── Subagent C: Synthesis (tools: verify_fact only)
    
Key principles:
1. Subagents do NOT inherit coordinator context — pass it explicitly
2. 4-5 tools per subagent max
3. Route ALL communication through coordinator (observability)
4. Parallel execution: emit multiple Task calls in ONE coordinator response
```

### Programmatic enforcement vs prompt-based guidance

```
Must the rule be followed 100% of the time?
├── YES (identity verification, refund limits, compliance) 
│   → Programmatic enforcement (hooks, prerequisite gates)
│   → Prompt instructions have a non-zero failure rate
└── NO (style preferences, best practices, suggestions)
    → Prompt-based guidance is fine
```

This is tested in almost every exam scenario. When financial or safety consequences exist, prompts are never the answer.

## Common exam traps in this domain

1. **Subagents inherit coordinator context.** FALSE — you must pass context explicitly.
2. **Narrow task decomposition is always better.** FALSE — overly narrow decomposition misses coverage (the "creative industries" example where only visual arts were covered).
3. **More tools = more capable agent.** FALSE — 18 tools degrades selection. Scope to 4-5.
4. **Self-review in the same session is effective.** FALSE — independent instance catches more.
5. **Prompt instructions can guarantee compliance.** FALSE for critical business rules.
