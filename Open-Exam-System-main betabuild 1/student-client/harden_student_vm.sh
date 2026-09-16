#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this on the dedicated student VM with sudo." >&2
  exit 1
fi

# Lock root password authentication while retaining the root account for recovery.
passwd --lock root

install -d -m 0755 /etc/ssh/sshd_config.d
cat >/etc/ssh/sshd_config.d/oes-student-hardening.conf <<'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
EOF

if command -v sshd >/dev/null; then
  sshd -t
  systemctl reload ssh || systemctl reload sshd || true
fi

printf '%s\n' 'Student VM hardening applied: root password locked and SSH root/password authentication disabled.'
