Start JupyterLab and ensure the Jupyter MCP server can connect.

1. Check if JupyterLab is already running on port 8888 using `lsof -i :8888`
2. If NOT running, start it in the background:
   ```
   jupyter lab --port 8888 --IdentityProvider.token claude_architect_token --ip 127.0.0.1 --no-browser &>/tmp/jupyter.log &
   ```
   Wait 4 seconds, then verify it responds with: `curl -s -o /dev/null -w "%{http_code}" "http://localhost:8888/api/status?token=claude_architect_token"`
3. If already running, just confirm it's healthy with the same curl check.
4. Report the status to the user: running/started, PID, and URL.
5. Remind the user that Jupyter MCP tools are available for notebook operations (if the MCP server is connected).
