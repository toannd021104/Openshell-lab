#!/usr/bin/env bash
set -euo pipefail
mode=${1:?Usage: create-sandbox.sh openshell-only|dual}
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
args=(sandbox create --cpu 1 --memory 2Gi --policy "$root/openshell/policy.yaml" --no-tty)
case "$mode" in
  openshell-only) args+=(--name opencode-openshell-only) ;;
  dual) args+=(--name opencode-dual --driver-config-json
    '{"kubernetes":{"pod":{"runtime_class_name":"kata-qemu"}}}') ;;
  *) echo "Expected openshell-only or dual" >&2; exit 2 ;;
esac
# Foreground connection intentionally stays attached. Use a separate terminal.
exec openshell "${args[@]}" -- sleep infinity
