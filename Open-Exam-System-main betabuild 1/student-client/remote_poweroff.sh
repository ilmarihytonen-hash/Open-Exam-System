#!/usr/bin/env bash
set -euo pipefail

: "${SSH_HOST:?Set SSH_HOST}"
: "${SSH_USER:?Set SSH_USER}"

read -r -p "Power off $SSH_USER@$SSH_HOST now? [y/N] " answer
[[ "$answer" == "y" || "$answer" == "Y" ]] || exit 0

exec ssh -o BatchMode=yes -o ConnectTimeout=5 "$SSH_USER@$SSH_HOST" 'sudo -n systemctl poweroff'
