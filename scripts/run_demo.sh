#!/usr/bin/env bash

set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
Usage: scripts/run_demo.sh

Starts the FastAPI service on http://127.0.0.1:8000 and the Streamlit
dashboard on http://127.0.0.1:8501 from one terminal.

This script uses .venv/bin/python when it is available.
EOF
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

API_HOST="127.0.0.1"
API_PORT="8000"
DASHBOARD_HOST="127.0.0.1"
DASHBOARD_PORT="8501"
API_URL="http://${API_HOST}:${API_PORT}"
DASHBOARD_URL="http://${DASHBOARD_HOST}:${DASHBOARD_PORT}"

API_PID=""
DASHBOARD_PID=""
INTERRUPTED="0"

shutdown_services() {
  if [[ -n "${API_PID}" ]] && kill -0 "${API_PID}" 2>/dev/null; then
    kill "${API_PID}" 2>/dev/null || true
  fi

  if [[ -n "${DASHBOARD_PID}" ]] && kill -0 "${DASHBOARD_PID}" 2>/dev/null; then
    kill "${DASHBOARD_PID}" 2>/dev/null || true
  fi

  wait "${API_PID}" "${DASHBOARD_PID}" 2>/dev/null || true
}

on_interrupt() {
  INTERRUPTED="1"
  echo
  echo "Shutting down demo services..."
  shutdown_services
  echo "Demo stopped cleanly."
  exit 0
}

on_exit() {
  local exit_code="$1"

  if [[ "${INTERRUPTED}" == "1" ]]; then
    return
  fi

  if [[ "${exit_code}" -ne 0 ]]; then
    shutdown_services
  fi
}

trap 'on_interrupt' INT TERM
trap 'on_exit $?' EXIT

echo "Starting FastAPI on ${API_URL}"
"${PYTHON_BIN}" -m uvicorn src.api.main:app --host "${API_HOST}" --port "${API_PORT}" &
API_PID=$!

echo "Starting Streamlit on ${DASHBOARD_URL}"
API_BASE_URL="${API_URL}" "${PYTHON_BIN}" -m streamlit run dashboard/app.py \
  --server.address="${DASHBOARD_HOST}" \
  --server.port="${DASHBOARD_PORT}" \
  --server.headless=true &
DASHBOARD_PID=$!

echo
echo "API: ${API_URL}"
echo "API docs: ${API_URL}/docs"
echo "Dashboard: ${DASHBOARD_URL}"
echo
echo "Press Ctrl+C to stop both services."
echo

status=0
while true; do
  if ! kill -0 "${API_PID}" 2>/dev/null; then
    echo "FastAPI exited unexpectedly."
    status=1
    break
  fi

  if ! kill -0 "${DASHBOARD_PID}" 2>/dev/null; then
    echo "Streamlit exited unexpectedly."
    status=1
    break
  fi

  sleep 1
done

shutdown_services
exit "${status}"
