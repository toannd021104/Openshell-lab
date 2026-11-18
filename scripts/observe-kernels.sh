#!/usr/bin/env bash
set -euo pipefail
# Run manually after both pods are Ready. No host mutation.
namespace=${NAMESPACE:-sandbox-lab}
for pod in baseline kata; do
  echo "=== $pod ==="
  kubectl -n "$namespace" get pod "$pod" -o wide
  kubectl -n "$namespace" exec "$pod" -- sh -c '
    uname -r
    cat /proc/uptime
    cat /proc/cmdline
    cat /proc/sys/kernel/random/boot_id
    nproc
  '
done
