"""Deploy health-check + rollback agent, with a human approval gate.

Reads NAMESPACE and the model settings that lab-env.ps1 loads from your lab card,
investigates a deployment, decides healthy/unhealthy, proposes a rollback,
asks the operator, then acts.  Everything is logged to audit.log.

Usage:
  python agent.py --deployment shipwave-api
"""
import argparse, json, os, sys, time, requests
from pathlib import Path
from tools import TOOLS

AUDIT = Path(__file__).parent / "audit.log"

# ---------- LLM call via Foundry gateway ---------------------------------
# lab-env.ps1 sets these from your lab card
GATEWAY = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
KEY     = os.environ.get("AZURE_OPENAI_API_KEY", "")
MODEL   = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")

def ask_llm(messages, tools):
    r = requests.post(f"{GATEWAY}/openai/v1/chat/completions",
        headers={"api-key": KEY, "Content-Type": "application/json"},
        json={"model": MODEL, "messages": messages, "tools": tools, "tool_choice": "auto"},
        timeout=90)
    if r.status_code >= 400:
        sys.exit(f"Model call failed {r.status_code}: {r.text[:300]}")
    return r.json()["choices"][0]["message"]

# ---------- Audit log ----------------------------------------------------
def audit(event, **data):
    with AUDIT.open("a") as f:
        f.write(json.dumps({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "who": os.environ.get("USERNAME", "unknown"),
            "event": event, **data}) + "\n")

# ---------- Tool schema the LLM sees -------------------------------------
def tool_schema():
    out = []
    for name, t in TOOLS.items():
        out.append({"type": "function", "function": {
            "name": name, "description": t["desc"],
            "parameters": {"type": "object",
                "properties": {a: {"type": "string"} for a in t["args"]},
                "required": t["args"]}}})
    return out

# ---------- Approval gate ------------------------------------------------
def approve(action, args):
    print(f"\n>>> PROPOSED ACTION: {action}({args})")
    print(">>> Type 'yes' to approve, anything else to abort.")
    reply = input(">>> ").strip().lower()
    return reply == "yes"

# ---------- Main loop ----------------------------------------------------
def run(namespace, deployment):
    audit("start", namespace=namespace, deployment=deployment)
    messages = [
        {"role": "system", "content":
            "You are a Kubernetes deploy health-check agent. "
            "Use the tools to investigate the given deployment. "
            "Decide healthy or unhealthy. If unhealthy and a previous revision "
            "exists, propose exactly ONE rollout_undo call. Never run it directly "
            "without the operator approving first."},
        {"role": "user", "content":
            f"Deployment '{deployment}' in namespace '{namespace}'. "
            "Investigate and decide."},
    ]
    for step in range(6):
        msg = ask_llm(messages, tool_schema())
        messages.append(msg)
        calls = msg.get("tool_calls") or []
        if not calls:
            print(f"\nAGENT: {msg.get('content','')}")
            audit("done", verdict=msg.get("content",""))
            return
        for c in calls:
            name = c["function"]["name"]
            args = json.loads(c["function"]["arguments"] or "{}")
            audit("tool_proposed", name=name, args=args)
            # Destructive tools require explicit approval
            if name == "rollout_undo":
                if not approve(name, args):
                    audit("rejected", name=name, args=args)
                    print("Aborted."); return
                audit("approved", name=name, args=args)
            result = TOOLS[name]["fn"](**args)
            audit("tool_result", name=name, result=result[:400])
            print(f"\n[{name}] {result[:300]}")
            messages.append({"role": "tool", "tool_call_id": c["id"],
                             "content": result[:2000]})
    audit("stopped", reason="max_steps")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--namespace", default=os.environ.get("NAMESPACE", "default"))
    p.add_argument("--deployment", required=True)
    a = p.parse_args()
    if not GATEWAY or not KEY:
        sys.exit("Model settings missing. Run: . C:\\EYLAB\\ey-aidevops-labs\\lab-env.ps1")
    run(a.namespace, a.deployment)
