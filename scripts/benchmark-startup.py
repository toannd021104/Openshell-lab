#!/usr/bin/env python3
"""Manual experiment B: API create-to-Ready wall time; never runs at import."""
import argparse
import csv
import json
import subprocess
import time


def kubectl(*args, capture=False):
    return subprocess.run(["kubectl", *args], check=True, text=True,
                          stdout=subprocess.PIPE if capture else subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", required=True, help="Node labeled sandbox-lab/worker=true")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--output", default="evidence/startup.csv")
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")
    with open(args.output, "w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["round", "runtime", "seconds", "status", "node"])
        for run in range(1, args.runs + 1):
            # Alternate order to reduce ordering bias; image pulls still count.
            runtimes = ["baseline", "kata"] if run % 2 else ["kata", "baseline"]
            for runtime in runtimes:
                name = f"startup-{runtime}-{run}-{time.time_ns()}"
                spec = {"restartPolicy": "Never", "automountServiceAccountToken": False,
                        "nodeSelector": {"kubernetes.io/hostname": args.node,
                                         "sandbox-lab/worker": "true"},
                        "containers": [{"name": "workload", "image": "alpine:3.21.3",
                                        "command": ["sleep", "300"],
                                        "resources": {"requests": {"cpu": "250m", "memory": "128Mi"},
                                                      "limits": {"cpu": "1", "memory": "256Mi"}}}]}
                if runtime == "kata":
                    spec["runtimeClassName"] = "kata-qemu"
                manifest = {"apiVersion": "v1", "kind": "Pod",
                            "metadata": {"name": name, "namespace": "sandbox-lab"}, "spec": spec}
                started = time.monotonic()
                status = "ready"
                try:
                    subprocess.run(["kubectl", "create", "-f", "-"], input=json.dumps(manifest),
                                   text=True, check=True, stdout=subprocess.DEVNULL)
                    kubectl("-n", "sandbox-lab", "wait", "--for=condition=Ready",
                            f"pod/{name}", "--timeout=180s")
                except subprocess.CalledProcessError:
                    status = "failed"
                finally:
                    writer.writerow([run, runtime, round(time.monotonic() - started, 3), status, args.node])
                    output.flush()
                    # Delete only the pod uniquely named by this iteration.
                    kubectl("-n", "sandbox-lab", "delete", "pod", name,
                            "--ignore-not-found", "--wait=true")
                if status != "ready":
                    raise SystemExit("Sample failed; inspect events before comparing results")


if __name__ == "__main__":
    main()
