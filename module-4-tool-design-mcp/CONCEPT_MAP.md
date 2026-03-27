# Module 4 Concept Coverage Map
## Domain 2: Tool Design & MCP Integration (18% of exam)

This map tracks every testable concept from the exam guide against our learning materials.

### Task Statement 2.1 — Effective tool descriptions and boundaries
**Covered in: Unit 4.1 + Cheat Sheet Section 1**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Tool descriptions are the primary selection mechanism (not classifiers, not few-shot) | Knowledge | Unit 4.1 Sec 1 |
| Production description pattern: what + when + when NOT + output | Knowledge | Unit 4.1 Sec 2 |
| Negative boundaries ("Do NOT use for X -- use Y instead") eliminate ambiguity | Knowledge | Unit 4.1 Sec 2 |
| Disambiguation between similar tools via boundary descriptions | Knowledge | Unit 4.1 Sec 1, Sec 3 |
| Split vs consolidate decision: distinct triggers vs shared usage pattern | Knowledge | Unit 4.1 Sec 4 |
| Edge case handling: "If ambiguous, ask user to clarify" | Knowledge | Unit 4.1 Sec 4 |
| Writing production-grade tool descriptions with positive triggers and negative boundaries | Skill | Unit 4.1 Challenge |
| Diagnosing tool misselection and suggesting description improvements | Skill | Unit 4.1 Challenge |

### Task Statement 2.2 — Structured error responses for MCP tools
**Covered in: Unit 4.2 + Cheat Sheet Section 2**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| isError flag signals tool failure in MCP protocol | Knowledge | Unit 4.2 Sec 1 |
| errorCategory classifies failure type for routing recovery | Knowledge | Unit 4.2 Sec 1 |
| isRetryable boolean is the critical retry/escalate signal | Knowledge | Unit 4.2 Sec 2 |
| retryAfterMs provides backoff hint for transient failures | Knowledge | Unit 4.2 Sec 2 |
| userMessage provides safe message for end users (no internal details) | Knowledge | Unit 4.2 Sec 2 |
| Local recovery first (retry, fallback), propagation second (escalate to user) | Knowledge | Unit 4.2 Sec 3 |
| Plain error strings are always wrong -- agent needs structured metadata | Knowledge | Unit 4.2 Sec 1 |
| Building structured error responses with correct retry/category mapping | Skill | Unit 4.2 Challenge |
| Deciding recovery action from error metadata (retry, escalate, correct, inform) | Skill | Unit 4.2 Challenge |

### Task Statement 2.3 — Tool distribution and tool_choice configuration
**Covered in: Unit 4.3 + Cheat Sheet Section 3**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| 4-5 tools per agent max; 18 tools degrades selection reliability | Knowledge | Unit 4.3 Sec 1 |
| Scoped access: each agent gets role-specific tools | Knowledge | Unit 4.3 Sec 2 |
| Cross-role tools: duplicate high-frequency tools across agents to avoid routing overhead | Knowledge | Unit 4.3 Sec 2 |
| Coordinator/router pattern: lightweight router selects domain agent | Knowledge | Unit 4.3 Sec 2 |
| tool_choice "auto": model decides if tool call needed | Knowledge | Unit 4.3 Sec 4 |
| tool_choice "any": model must call some tool (pipeline steps) | Knowledge | Unit 4.3 Sec 4 |
| tool_choice forced {"name":"X"}: must call specific tool (first step) | Knowledge | Unit 4.3 Sec 4 |
| Distributing tools across agents respecting the 4-5 tool limit | Skill | Unit 4.3 Challenge |
| Designing router tools for multi-agent coordination | Skill | Unit 4.3 Challenge |
| Configuring tool_choice for pipeline ordering guarantees | Skill | Unit 4.3 Challenge |

### Task Statement 2.4 — MCP server integration
**Covered in: Unit 4.4 + Cheat Sheet Section 4**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| .mcp.json in project root = shared team tooling (version controlled) | Knowledge | Unit 4.4 Sec 1 |
| ~/.claude.json = personal/experimental servers (not shared) | Knowledge | Unit 4.4 Sec 1 |
| Both configs discovered at connection time, servers available simultaneously | Knowledge | Unit 4.4 Sec 2 |
| ${ENV_VAR} expansion for secrets in .mcp.json (never hardcode) | Knowledge | Unit 4.4 Sec 2 |
| Community server evaluation: source review, description quality, security audit | Knowledge | Unit 4.4 Sec 4 |
| MCP resources as read-only data sources alongside tools | Knowledge | Unit 4.4 Sec 3 |
| Building secure .mcp.json with environment variable expansion for secrets | Skill | Unit 4.4 Challenge |
| Auditing MCP configs for hardcoded secrets | Skill | Unit 4.4 Challenge |
| Choosing correct config file (project vs personal) based on sharing requirements | Skill | Unit 4.4 Challenge |

### Task Statement 2.5 — Built-in tools (Read, Write, Edit, Bash, Grep, Glob)
**Covered in: Unit 4.5 + Cheat Sheet Section 5**

| Concept | Knowledge/Skill | Covered |
|---------|----------------|---------|
| Grep searches FILE CONTENT (function definitions, imports, patterns) | Knowledge | Unit 4.5 Sec 1 |
| Glob searches FILE PATHS (find files by name, extension, pattern) | Knowledge | Unit 4.5 Sec 1 |
| Edit requires unique old_string; use context or replace_all for non-unique | Knowledge | Unit 4.5 Sec 4 |
| Write for new files or complete rewrites; Edit for partial modifications | Knowledge | Unit 4.5 Sec 2 |
| Incremental exploration: Glob (structure) -> Read (key files) -> Grep (specifics) | Knowledge | Unit 4.5 Sec 2 |
| Bash for command execution (scripts, packages, system checks) | Knowledge | Unit 4.5 Sec 2 |
| Selecting the correct built-in tool for each codebase task | Skill | Unit 4.5 Challenge |
| Explaining why a specific tool is correct for a given task | Skill | Unit 4.5 Challenge |

---

## Coverage Verification

- Task Statement 2.1: 8/8 concepts covered
- Task Statement 2.2: 9/9 concepts covered
- Task Statement 2.3: 10/10 concepts covered
- Task Statement 2.4: 9/9 concepts covered
- Task Statement 2.5: 8/8 concepts covered
- **Total: 44/44 testable concepts from Domain 2**

## Cross-Reference: Exam Scenarios Using Domain 2

| Scenario | How Domain 2 appears |
|----------|---------------------|
| Scenario 1: Multi-agent customer service | Tool descriptions for disambiguation, 4-5 tool limit, tool distribution across agents |
| Scenario 2: MCP-based development tools | .mcp.json for team sharing, secret management, community server evaluation |
| Scenario 3: Code assistant | Built-in tool selection (Grep vs Glob), Edit unique matching, incremental exploration |
| Scenario 5: CI/CD pipeline | Structured errors for MCP tools, tool_choice forced for pipeline ordering |
