# Capstone: Scenario-Based Practice

**All domains — Phase 4 (weeks 7–8)**  
**Prerequisites: Modules 1–5**

## How the exam works

The exam picks **4 of 6 scenarios** at random. Each scenario presents a realistic production context and frames multiple questions spanning several domains. You don't get to choose which scenarios appear.

## The 6 scenarios

### Scenario 1: Customer Support Resolution Agent
**Primary domains:** Agentic Architecture (D1), Tool Design & MCP (D2), Context Management (D5)

Build a customer support agent using the Claude Agent SDK with MCP tools (`get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`). Target 80%+ first-contact resolution while knowing when to escalate.

**Key skills tested:** Programmatic prerequisites (verify before refund), structured error responses, escalation criteria with few-shot examples, context preservation across multi-issue conversations, structured handoff summaries.

→ See `notebooks/scenario-1-customer-support.ipynb`

### Scenario 2: Code Generation with Claude Code
**Primary domains:** Claude Code Config (D3), Context Management (D5)

Configure Claude Code for team development workflows. CLAUDE.md hierarchy, custom commands, path-specific rules, plan mode vs direct execution.

**Key skills tested:** CLAUDE.md hierarchy debugging, .claude/rules/ with glob patterns, context: fork for skills, plan mode for architectural changes, iterative refinement.

→ See `notebooks/scenario-2-code-generation.ipynb`

### Scenario 3: Multi-Agent Research System
**Primary domains:** Agentic Architecture (D1), Tool Design & MCP (D2), Context Management (D5)

Coordinator agent delegates to specialized subagents (web search, document analysis, synthesis, reports). Produces comprehensive, cited reports.

**Key skills tested:** Task decomposition (avoiding narrow coverage), explicit context passing, parallel subagent execution, error propagation, provenance tracking, handling conflicting sources.

→ See `notebooks/scenario-3-multi-agent-research.ipynb`

### Scenario 4: Developer Productivity with Claude
**Primary domains:** Tool Design & MCP (D2), Claude Code Config (D3), Agentic Architecture (D1)

Agent helps engineers explore unfamiliar codebases using built-in tools (Read, Write, Bash, Grep, Glob) and MCP servers.

**Key skills tested:** Built-in tool selection (Grep vs Glob), incremental codebase exploration, MCP server configuration, context management in long exploration sessions.

→ See `notebooks/scenario-4-developer-productivity.ipynb`

### Scenario 5: Claude Code for Continuous Integration
**Primary domains:** Claude Code Config (D3), Prompt Engineering (D4)

Claude Code in CI/CD: automated code reviews, test generation, PR feedback. Design prompts for actionable feedback with minimal false positives.

**Key skills tested:** -p flag for non-interactive mode, --output-format json, explicit review criteria, multi-pass review (per-file + cross-file), batch API for overnight analysis, prior findings in context.

→ See `notebooks/scenario-5-ci-cd.ipynb`

### Scenario 6: Structured Data Extraction
**Primary domains:** Prompt Engineering (D4), Context Management (D5)

Extract structured information from unstructured documents with JSON schema validation and high accuracy.

**Key skills tested:** tool_use with JSON schemas, nullable fields, validation-retry loops, few-shot examples for varied document formats, batch processing, human review routing with confidence scores.

→ See `notebooks/scenario-6-data-extraction.ipynb`

## Practice exam format

Each notebook contains:
1. **Scenario context** — the production situation
2. **5-8 multiple choice questions** — same format as the real exam
3. **Hands-on build** — implement the actual system described in the scenario
4. **Failure injections** — deliberately introduce problems and diagnose them
5. **Explanations** — detailed reasoning for each answer

## Study strategy

1. Work through all 6 scenarios (not just 4) since you don't know which will appear
2. Focus on cross-domain connections — most questions require knowledge from multiple domains
3. Practice the "diagnose the production problem" pattern — the exam shows you symptoms and asks for root cause
4. Time yourself: the real exam has a time limit, so practice answering under pressure
