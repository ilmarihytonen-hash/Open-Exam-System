#!/usr/bin/env bash
set -euo pipefail

EXAM_URL="${OES_EXAM_URL:-http://127.0.0.1:8000/student/login}"

command -v firefox >/dev/null || { echo "Firefox is required" >&2; exit 1; }
command -v xdg-settings >/dev/null && {
  xdg-settings set default-url-scheme-handler http firefox.desktop || true
  xdg-settings set default-url-scheme-handler https firefox.desktop || true
}

exec firefox --kiosk --new-window "$EXAM_URL"
