#!/usr/bin/env bash
# Start the ocp_vscode viewer (if not already running), rebuild the model, push it
# to the viewer, and open the browser tab.
#
# Usage:  ./view.sh
# Then:   reload the browser tab once (Cmd-R) if it still shows the default model.
set -euo pipefail

PORT=3939
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$HERE/../.venv/bin/python"
URL="http://127.0.0.1:${PORT}/viewer"

# 1) Start the viewer only if nothing is already listening on the port.
if ! lsof -nP -iTCP:${PORT} -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Starting ocp_vscode viewer on ${PORT}..."
  nohup "$PY" -m ocp_vscode --port ${PORT} --up Z >/tmp/ocp_viewer.log 2>&1 &
  # Wait for it to come up.
  for _ in $(seq 1 20); do
    lsof -nP -iTCP:${PORT} -sTCP:LISTEN >/dev/null 2>&1 && break
    sleep 0.5
  done
else
  echo "Viewer already running on ${PORT}."
fi

# 2) Open the browser tab FIRST so it is connected before we push.
open "$URL" 2>/dev/null || true
sleep 2

# 3) Rebuild + push the model (also re-exports STL/STEP via the script's show()).
"$PY" "$HERE/switch_cradle.py" >/tmp/switch_cradle_run.log 2>&1
echo "Pushed model to ${URL}"
echo "If it still shows the default model, reload the tab once (Cmd-R)."
