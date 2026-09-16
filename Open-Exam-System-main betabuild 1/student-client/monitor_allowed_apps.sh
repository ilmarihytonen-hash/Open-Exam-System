#!/usr/bin/env bash
set -euo pipefail

EXAM_URL="${OES_EXAM_URL:-http://127.0.0.1:8000}"
SESSION_COOKIE="${OES_SESSION_COOKIE:-}"
INTERVAL="${OES_MONITOR_INTERVAL:-1}"
ALLOWED_APPS="${OES_ALLOWED_APPS:-firefox,plasmashell,kwin_wayland,kwin_x11,Xwayland,systemd,dbus-daemon,bash}
"
FORBIDDEN_APPS="${OES_FORBIDDEN_APPS:-chromium,google-chrome,libreoffice,code,konsole,dolphin,telegram,discord}"

report_violation() {
  local process_name="$1"
  echo "$(date --iso-8601=seconds) forbidden_process=$process_name" >&2
  if [[ -n "$SESSION_COOKIE" ]] && command -v curl >/dev/null; then
    curl -fsS -b "oes_session=$SESSION_COOKIE" -H 'Content-Type: application/json' \
      -d "{\"kind\":\"forbidden_process\",\"details\":\"$process_name\"}" \
      "$EXAM_URL/api/student/exams/${OES_EXAM_ID:?OES_EXAM_ID is required}/violations" >/dev/null || true
  fi
}

while true; do
  IFS=',' read -ra forbidden <<< "$FORBIDDEN_APPS"
  for process_name in "${forbidden[@]}"; do
    if pgrep -x "$process_name" >/dev/null; then report_violation "$process_name"; fi
  done
  sleep "$INTERVAL"
done
