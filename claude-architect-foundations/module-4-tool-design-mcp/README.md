# Module 4: Tool Design & MCP Integration

**Exam Domain 2 — 18% of scored content**  
**Phase 2 (Tooling) — Prerequisites: Modules 1, 2**

## Why this is Module 4

Tool descriptions are prompts (Module 1). Error responses need the patterns from context management (Module 2). You need both before designing production tool interfaces.

## Units

| Unit | Topic | Key exam concepts |
|------|-------|-------------------|
| [4.1](unit-4.1-tool-descriptions.md) | Effective tool descriptions & boundaries | Descriptions as primary selection mechanism, disambiguation, splitting vs consolidating |
| [4.2](unit-4.2-structured-errors.md) | Structured error responses for MCP tools | isError flag, errorCategory, isRetryable, local recovery vs propagation |
| [4.3](unit-4.3-tool-distribution.md) | Tool distribution & tool_choice config | 4-5 tools per agent max, scoped access, cross-role tools, tool_choice modes |
| [4.4](unit-4.4-mcp-server-integration.md) | MCP server integration | .mcp.json vs ~/.claude.json, env variable expansion, MCP resources, community servers |
| [4.5](unit-4.5-builtin-tools.md) | Built-in tools (Read, Write, Edit, Bash, Grep, Glob) | Grep for content, Glob for paths, Edit unique text matching, incremental codebase exploration |

## Key mental models

### Tool descriptions are your #1 lever

When tool selection is unreliable, the problem is almost always **inadequate descriptions**. Not few-shot examples, not routing classifiers, not tool consolidation. Descriptions first.

A minimal description: `"Retrieves customer information"`  
A production description:
```
Retrieves customer account details by customer ID, email, or phone number.
Use this tool when the user asks about their account, profile, or membership.
Do NOT use for order lookups — use lookup_order instead.
Input: customer_id (string) OR email (string) OR phone (string)
Output: {name, email, phone, account_status, membership_tier, created_date}
Edge case: If multiple matches found, returns all matches — agent should ask user to disambiguate.
```

### The 4-5 tool limit

Giving an agent 18 tools degrades selection reliability by increasing decision complexity. Scope each agent to 4-5 tools relevant to its role. Add one cross-role tool for high-frequency needs (e.g., `verify_fact` for the synthesis agent) while routing complex cases through the coordinator.

### MCP server scoping

```
.mcp.json (project root)     ← shared team tooling, version controlled
  - Uses ${ENV_VAR} for credentials (never commit secrets)
  - All devs get these tools when they clone the repo

~/.claude.json               ← personal/experimental servers
  - Your experimental MCP servers
  - Not shared with teammates
  
Both are discovered at connection time and available simultaneously.
```
