"""
CHALLENGE: Configure MCP Servers for a Production Project

Task Statement 2.4 — Configure MCP servers for team and personal use,
manage secrets, and evaluate community servers.

Your goal: build MCP configurations that are secure (no hardcoded secrets),
correctly scoped (team vs personal), and follow best practices.

Complete the three methods in MCPConfigChallenge:
  1. build_project_config(servers)  — create .mcp.json content
  2. build_personal_config(servers) — create ~/.claude.json content
  3. audit_config(config)           — find security issues in a config

The checker will test your configs for security, structure, and correctness.
"""

import json


# ---------------------------------------------------------------------------
# Server specifications
# ---------------------------------------------------------------------------

TEAM_SERVERS = [
    {
        "name": "postgres",
        "command": "npx",
        "args": ["-y", "@mcp/postgres-server"],
        "env": {
            "POSTGRES_HOST": "db.company.com",
            "POSTGRES_DB": "analytics",
            "POSTGRES_USER": "readonly_user",
            "POSTGRES_PASSWORD": "secret",  # THIS IS A SECRET
        },
        "secrets": ["POSTGRES_PASSWORD"],
    },
    {
        "name": "slack",
        "command": "npx",
        "args": ["-y", "@mcp/slack-server"],
        "env": {
            "SLACK_TOKEN": "secret",  # THIS IS A SECRET
            "SLACK_DEFAULT_CHANNEL": "#engineering",
        },
        "secrets": ["SLACK_TOKEN"],
    },
    {
        "name": "github",
        "command": "npx",
        "args": ["-y", "@mcp/github-server"],
        "env": {
            "GITHUB_TOKEN": "secret",  # THIS IS A SECRET
            "GITHUB_ORG": "mycompany",
        },
        "secrets": ["GITHUB_TOKEN"],
    },
]

PERSONAL_SERVERS = [
    {
        "name": "my-custom-tool",
        "command": "python",
        "args": ["/home/dev/mcp-servers/custom-tool.py"],
        "env": {
            "CUSTOM_API_KEY": "secret",
        },
        "secrets": ["CUSTOM_API_KEY"],
    },
]

# Configs to audit (some have security issues)
AUDIT_CONFIGS = [
    {
        "label": "config_a",
        "config": {
            "mcpServers": {
                "database": {
                    "command": "npx",
                    "args": ["-y", "@mcp/postgres"],
                    "env": {
                        "DB_HOST": "prod.db.com",
                        "DB_PASSWORD": "p@ssw0rd123",
                    },
                }
            }
        },
        "expected_issues": 1,
    },
    {
        "label": "config_b",
        "config": {
            "mcpServers": {
                "api": {
                    "command": "node",
                    "args": ["./server.js"],
                    "env": {
                        "API_KEY": "${API_KEY}",
                        "API_URL": "https://api.example.com",
                    },
                }
            }
        },
        "expected_issues": 0,
    },
    {
        "label": "config_c",
        "config": {
            "mcpServers": {
                "service1": {
                    "command": "npx",
                    "args": ["-y", "@mcp/service1"],
                    "env": {
                        "TOKEN": "xoxb-real-token",
                        "SECRET_KEY": "sk-abc123",
                        "ENDPOINT": "https://api.example.com",
                    },
                }
            }
        },
        "expected_issues": 2,
    },
]


# ---------------------------------------------------------------------------
# Challenge class — complete the TODO sections
# ---------------------------------------------------------------------------

class MCPConfigChallenge:
    """
    Build secure MCP configurations for team and personal use.
    """

    def build_project_config(self, servers: list[dict]) -> dict:
        """
        Build a .mcp.json configuration for shared team use.

        Args:
            servers: List of server specs (name, command, args, env, secrets).

        Returns:
            A dict representing .mcp.json content.
            - Secrets must use ${ENV_VAR} expansion
            - Non-secrets can be hardcoded
            - Structure: {"mcpServers": {"name": {"command":..., "args":..., "env":...}}}

        Rules:
        - For each key in 'secrets' list, use ${KEY_NAME} instead of the value
        - For non-secret env vars, use the original value
        """
        # TODO: Build the .mcp.json config with proper secret handling.
        # Hint: Loop through servers, check if each env key is in secrets list.
        # Hint: If it's a secret, replace value with ${KEY_NAME}.
        raise NotImplementedError("Complete build_project_config()")

    def build_personal_config(self, servers: list[dict]) -> dict:
        """
        Build a ~/.claude.json configuration for personal use.

        Args:
            servers: List of personal server specs.

        Returns:
            A dict representing ~/.claude.json content.
            Same format as project config.
            Secrets should still use ${ENV_VAR} for consistency.
        """
        # TODO: Build personal config. Same structure, same secret handling.
        raise NotImplementedError("Complete build_personal_config()")

    def audit_config(self, config: dict) -> list[dict]:
        """
        Audit an MCP config for security issues.

        Check for:
        - Hardcoded values in env keys that look like secrets
          (contains: token, key, secret, password, credential)
        - Only flag if the value does NOT start with "${" (env var expansion)

        Args:
            config: A dict representing an MCP config.

        Returns:
            List of issue dicts, each with:
            - "server": str (server name)
            - "key": str (the env var name with the issue)
            - "issue": str (description of the problem)
            - "fix": str (how to fix it)
        """
        # TODO: Scan config for hardcoded secrets.
        # Hint: Check each env key name against secret_patterns.
        # Hint: If the value doesn't start with "${", it's hardcoded.
        raise NotImplementedError("Complete audit_config()")


# ---------------------------------------------------------------------------
# Run the challenge locally
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("MCP Server Configuration Challenge")
    print("====================================\n")

    challenge = MCPConfigChallenge()

    # Test project config
    print("1. Project Config (.mcp.json):")
    try:
        project = challenge.build_project_config(TEAM_SERVERS)
        print(json.dumps(project, indent=2))
    except NotImplementedError as e:
        print(f"   Not implemented: {e}")

    # Test personal config
    print("\n2. Personal Config (~/.claude.json):")
    try:
        personal = challenge.build_personal_config(PERSONAL_SERVERS)
        print(json.dumps(personal, indent=2))
    except NotImplementedError as e:
        print(f"   Not implemented: {e}")

    # Test audit
    print("\n3. Config Audits:")
    try:
        for audit in AUDIT_CONFIGS:
            issues = challenge.audit_config(audit["config"])
            status = "PASS" if len(issues) == audit["expected_issues"] else "FAIL"
            print(f"   [{status}] {audit['label']}: "
                  f"{len(issues)} issue(s) (expected {audit['expected_issues']})")
            for issue in issues:
                print(f"      - {issue['server']}.{issue['key']}: {issue['issue']}")
    except NotImplementedError as e:
        print(f"   Not implemented: {e}")
