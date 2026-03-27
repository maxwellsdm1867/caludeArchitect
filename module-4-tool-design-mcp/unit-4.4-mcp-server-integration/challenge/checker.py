"""
Checker for Unit 4.4 — MCP Server Configuration Challenge

Validates MCP configuration building and security auditing
without calling the Anthropic API.
"""

import json
import pytest

from challenge import (
    MCPConfigChallenge,
    TEAM_SERVERS,
    PERSONAL_SERVERS,
    AUDIT_CONFIGS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def challenge():
    """Create an MCPConfigChallenge instance."""
    return MCPConfigChallenge()


# ---------------------------------------------------------------------------
# Test 1: Project Config (.mcp.json)
# ---------------------------------------------------------------------------

class TestProjectConfig:
    """Student's build_project_config must produce secure, valid configs."""

    def test_returns_dict(self, challenge):
        config = challenge.build_project_config(TEAM_SERVERS)
        assert isinstance(config, dict), "build_project_config must return a dict"

    def test_has_mcp_servers_key(self, challenge):
        config = challenge.build_project_config(TEAM_SERVERS)
        assert "mcpServers" in config, "Config must have 'mcpServers' key"

    def test_all_servers_present(self, challenge):
        config = challenge.build_project_config(TEAM_SERVERS)
        servers = config["mcpServers"]
        for spec in TEAM_SERVERS:
            assert spec["name"] in servers, (
                f"Missing server '{spec['name']}' in config"
            )

    def test_secrets_use_env_var_expansion(self, challenge):
        config = challenge.build_project_config(TEAM_SERVERS)
        servers = config["mcpServers"]
        for spec in TEAM_SERVERS:
            server = servers[spec["name"]]
            env = server.get("env", {})
            for secret_key in spec["secrets"]:
                assert secret_key in env, (
                    f"Missing env var '{secret_key}' in server '{spec['name']}'"
                )
                value = env[secret_key]
                assert value.startswith("${") and value.endswith("}"), (
                    f"Secret '{secret_key}' in '{spec['name']}' must use "
                    f"${{ENV_VAR}} expansion, got: '{value}'"
                )

    def test_non_secrets_are_hardcoded(self, challenge):
        config = challenge.build_project_config(TEAM_SERVERS)
        servers = config["mcpServers"]
        for spec in TEAM_SERVERS:
            server = servers[spec["name"]]
            env = server.get("env", {})
            for key, value in spec["env"].items():
                if key not in spec["secrets"]:
                    assert key in env, (
                        f"Missing non-secret env var '{key}' in '{spec['name']}'"
                    )
                    assert not env[key].startswith("${"), (
                        f"Non-secret '{key}' should be hardcoded, not env var expanded"
                    )

    def test_command_preserved(self, challenge):
        config = challenge.build_project_config(TEAM_SERVERS)
        servers = config["mcpServers"]
        for spec in TEAM_SERVERS:
            assert servers[spec["name"]]["command"] == spec["command"], (
                f"Command mismatch for '{spec['name']}'"
            )

    def test_args_preserved(self, challenge):
        config = challenge.build_project_config(TEAM_SERVERS)
        servers = config["mcpServers"]
        for spec in TEAM_SERVERS:
            assert servers[spec["name"]]["args"] == spec["args"], (
                f"Args mismatch for '{spec['name']}'"
            )


# ---------------------------------------------------------------------------
# Test 2: Personal Config (~/.claude.json)
# ---------------------------------------------------------------------------

class TestPersonalConfig:
    """Student's build_personal_config must produce valid personal configs."""

    def test_returns_dict(self, challenge):
        config = challenge.build_personal_config(PERSONAL_SERVERS)
        assert isinstance(config, dict), "build_personal_config must return a dict"

    def test_has_mcp_servers_key(self, challenge):
        config = challenge.build_personal_config(PERSONAL_SERVERS)
        assert "mcpServers" in config, "Config must have 'mcpServers' key"

    def test_all_personal_servers_present(self, challenge):
        config = challenge.build_personal_config(PERSONAL_SERVERS)
        servers = config["mcpServers"]
        for spec in PERSONAL_SERVERS:
            assert spec["name"] in servers, (
                f"Missing personal server '{spec['name']}'"
            )

    def test_personal_secrets_use_env_vars(self, challenge):
        config = challenge.build_personal_config(PERSONAL_SERVERS)
        servers = config["mcpServers"]
        for spec in PERSONAL_SERVERS:
            server = servers[spec["name"]]
            env = server.get("env", {})
            for secret_key in spec["secrets"]:
                if secret_key in env:
                    value = env[secret_key]
                    assert value.startswith("${"), (
                        f"Personal secret '{secret_key}' should use env var expansion"
                    )


# ---------------------------------------------------------------------------
# Test 3: Security Audit
# ---------------------------------------------------------------------------

class TestAudit:
    """Student's audit_config must find security issues."""

    def test_returns_list(self, challenge):
        result = challenge.audit_config(AUDIT_CONFIGS[0]["config"])
        assert isinstance(result, list), "audit_config must return a list"

    def test_finds_hardcoded_password(self, challenge):
        """config_a has a hardcoded DB_PASSWORD."""
        issues = challenge.audit_config(AUDIT_CONFIGS[0]["config"])
        assert len(issues) == 1, (
            f"config_a should have 1 issue (hardcoded password), "
            f"found {len(issues)}"
        )
        assert issues[0]["key"] == "DB_PASSWORD", (
            f"Issue should be about 'DB_PASSWORD', got '{issues[0]['key']}'"
        )

    def test_clean_config_no_issues(self, challenge):
        """config_b uses env var expansion correctly."""
        issues = challenge.audit_config(AUDIT_CONFIGS[1]["config"])
        assert len(issues) == 0, (
            f"config_b should have 0 issues (all env vars expanded), "
            f"found {len(issues)}"
        )

    def test_finds_multiple_secrets(self, challenge):
        """config_c has 2 hardcoded secrets."""
        issues = challenge.audit_config(AUDIT_CONFIGS[2]["config"])
        assert len(issues) == 2, (
            f"config_c should have 2 issues (TOKEN and SECRET_KEY), "
            f"found {len(issues)}"
        )
        issue_keys = {i["key"] for i in issues}
        assert "TOKEN" in issue_keys, "Should flag hardcoded TOKEN"
        assert "SECRET_KEY" in issue_keys, "Should flag hardcoded SECRET_KEY"

    def test_audit_result_structure(self, challenge):
        """Each audit issue must have server, key, issue, fix fields."""
        issues = challenge.audit_config(AUDIT_CONFIGS[0]["config"])
        for issue in issues:
            assert "server" in issue, f"Audit issue missing 'server': {issue}"
            assert "key" in issue, f"Audit issue missing 'key': {issue}"
            assert "issue" in issue, f"Audit issue missing 'issue': {issue}"
            assert "fix" in issue, f"Audit issue missing 'fix': {issue}"

    def test_does_not_flag_non_secrets(self, challenge):
        """Env vars without secret-like names should not be flagged."""
        config = {
            "mcpServers": {
                "test": {
                    "command": "node",
                    "args": ["server.js"],
                    "env": {
                        "HOST": "localhost",
                        "PORT": "3000",
                        "DATABASE_NAME": "mydb",
                    },
                }
            }
        }
        issues = challenge.audit_config(config)
        assert len(issues) == 0, (
            f"Non-secret env vars should not be flagged, found {len(issues)} issue(s)"
        )
