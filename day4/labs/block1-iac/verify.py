"""Verify Block 1 from your Terraform state (no Azure CLI needed).
Run from the folder that holds your main.tf, after terraform apply:
    cd C:\\EYLAB\\ey-aidevops-labs\\day4\\block1
    python ..\\labs\\block1-iac\\verify.py
Paste the whole scorecard into the lab page.
"""
import json, subprocess, sys

# (terraform type(s), label, points, part)
CHECKS = [
    (("azurerm_storage_account",), "Storage Account", 20, "guided"),
    (("azurerm_key_vault",), "Key Vault", 20, "guided"),
    (("azurerm_log_analytics_workspace",), "Log Analytics Workspace", 15, "solo"),
    (("azurerm_service_plan", "azurerm_app_service_plan"), "App Service Plan (Consumption)", 15, "solo"),
    (("azurerm_linux_function_app", "azurerm_function_app"), "Function App", 15, "solo"),
    (("azurerm_monitor_diagnostic_setting",), "Diagnostic setting on the storage account", 15, "solo"),
]


def walk(mod):
    for r in mod.get("resources", []):
        yield r
    for m in mod.get("child_modules", []):
        yield from walk(m)


def main():
    p = subprocess.run(["terraform", "show", "-json"], capture_output=True, text=True, shell=(sys.platform == "win32"))
    if p.returncode != 0 or not p.stdout.strip():
        sys.exit("Could not read state. Run this from the folder with your main.tf, after terraform apply.\n" + p.stderr[:300])
    root = json.loads(p.stdout).get("values", {}).get("root_module", {})
    res = list(walk(root))
    types = {}
    for r in res:
        types.setdefault(r["type"], []).append(r)

    score = 0
    print("\nBlock 1 scorecard (from Terraform state)\n" + "-" * 44)
    for tfs, label, pts, part in CHECKS:
        ok = any(t in types for t in tfs)
        score += pts if ok else 0
        print(f"  [{'PASS' if ok else 'MISS'}] {label}  ({part})")

    notes = []
    for r in types.get("azurerm_storage_account", []):
        v = r["values"]
        if v.get("min_tls_version") != "TLS1_2":
            notes.append("Storage Account: min_tls_version is not TLS1_2")
        if not v.get("https_traffic_only_enabled", v.get("enable_https_traffic_only", True)):
            notes.append("Storage Account: HTTPS only is off")
    for r in types.get("azurerm_key_vault", []):
        if not r["values"].get("purge_protection_enabled"):
            notes.append("Key Vault: purge protection is not enabled")
    for r in res:
        tags = r["values"].get("tags") or {}
        if r["type"] in ("azurerm_storage_account", "azurerm_key_vault") and tags.get("course") != "ey-aidevops":
            notes.append(f"{r['type']}: missing tag course=ey-aidevops")
    print("-" * 44)
    print(f"Score: {score} / 100")
    for n in sorted(set(notes)):
        print("  note:", n)
    print(f"Resources in state: {len(res)}")


if __name__ == "__main__":
    main()
