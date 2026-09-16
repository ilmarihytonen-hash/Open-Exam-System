#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "This local maintenance shell must be started with sudo: sudo $0" >&2
  exit 1
fi

cd "$(dirname "$(readlink -f "$0")")/.."
export OES_ROOT_SHELL=1
printf 'OES maintenance root shell. Type exit to leave.\n'
exec /bin/bash --login
