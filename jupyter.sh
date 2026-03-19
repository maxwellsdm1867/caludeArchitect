#!/bin/bash
# Start/stop JupyterLab for Claude MCP integration
# Usage: ./jupyter.sh [start|stop|status]

PORT=8888
TOKEN="claude_architect_token"
LOG="/tmp/jupyter.log"

case "${1:-start}" in
  start)
    if lsof -i :$PORT &>/dev/null; then
      echo "JupyterLab already running on port $PORT"
      echo "PID: $(lsof -ti :$PORT | head -1)"
    else
      echo "Starting JupyterLab on port $PORT..."
      jupyter lab --port $PORT --IdentityProvider.token $TOKEN --ip 127.0.0.1 --no-browser &>$LOG &
      sleep 3
      if curl -s -o /dev/null -w "" "http://localhost:$PORT/api/status?token=$TOKEN" 2>/dev/null; then
        echo "JupyterLab started (PID: $!)"
        echo "URL: http://localhost:$PORT/?token=$TOKEN"
      else
        echo "Failed to start. Check $LOG"
        exit 1
      fi
    fi
    ;;
  stop)
    PID=$(lsof -ti :$PORT 2>/dev/null)
    if [ -n "$PID" ]; then
      kill $PID
      echo "Stopped JupyterLab (PID: $PID)"
    else
      echo "JupyterLab not running"
    fi
    ;;
  status)
    if lsof -i :$PORT &>/dev/null; then
      echo "JupyterLab running on port $PORT (PID: $(lsof -ti :$PORT | head -1))"
    else
      echo "JupyterLab not running"
    fi
    ;;
  *)
    echo "Usage: $0 [start|stop|status]"
    ;;
esac
