Stop the JupyterLab server running on port 8888.

1. Find the JupyterLab process using `lsof -ti :8888`
2. If found, kill it with `kill <pid>` and confirm it stopped
3. If not found, tell the user it's not running
