"""Tools the agent can call. Each returns a short string the LLM can read."""
import subprocess, json

def _run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return (r.stdout or r.stderr).strip()
    except Exception as e:
        return f"ERROR: {e}"

def get_pods(namespace: str) -> str:
    """List pods in namespace with status and restart count."""
    return _run(["kubectl", "-n", namespace, "get", "pods",
                 "-o", "custom-columns=NAME:.metadata.name,STATUS:.status.phase,"
                 "READY:.status.containerStatuses[0].ready,"
                 "RESTARTS:.status.containerStatuses[0].restartCount"])

def get_deployment(namespace: str, name: str) -> str:
    """Ready vs desired replicas for the deployment."""
    out = _run(["kubectl", "-n", namespace, "get", "deploy", name, "-o", "json"])
    try:
        d = json.loads(out)
        spec = d.get("spec", {}).get("replicas", 0)
        status = d.get("status", {})
        return (f"desired={spec} "
                f"ready={status.get('readyReplicas', 0)} "
                f"available={status.get('availableReplicas', 0)} "
                f"unavailable={status.get('unavailableReplicas', 0)}")
    except Exception:
        return out[:400]

def get_logs(namespace: str, name: str) -> str:
    """Last 50 lines of logs from pods matching the deployment label."""
    return _run(["kubectl", "-n", namespace, "logs",
                 "-l", f"app={name}", "--tail=50", "--all-containers=true"])

def get_events(namespace: str, name: str) -> str:
    """Recent Kubernetes events (image pull errors, probe failures) for the deployment's pods."""
    return _run(["kubectl", "-n", namespace, "get", "events", "--sort-by=.lastTimestamp"])[-1800:]

def rollout_history(namespace: str, name: str) -> str:
    return _run(["kubectl", "-n", namespace, "rollout", "history",
                 f"deployment/{name}"])

def rollout_undo(namespace: str, name: str) -> str:
    """IRREVERSIBLE: rolls deployment back to previous revision."""
    return _run(["kubectl", "-n", namespace, "rollout", "undo",
                 f"deployment/{name}"])

# Tool registry the agent reads.
TOOLS = {
    "get_pods":        {"fn": get_pods,        "args": ["namespace"],
                        "desc": "List pods and their status in a namespace."},
    "get_deployment":  {"fn": get_deployment,  "args": ["namespace", "name"],
                        "desc": "Ready vs desired replicas for a deployment."},
    "get_logs":        {"fn": get_logs,        "args": ["namespace", "name"],
                        "desc": "Last 50 log lines from a deployment's pods."},
    "get_events":      {"fn": get_events,      "args": ["namespace", "name"],
                        "desc": "Recent events in the namespace (image pull errors, probe failures)."},
    "rollout_history": {"fn": rollout_history, "args": ["namespace", "name"],
                        "desc": "Deployment rollout revisions."},
    "rollout_undo":    {"fn": rollout_undo,    "args": ["namespace", "name"],
                        "desc": "DESTRUCTIVE: roll a deployment back one revision."},
}
