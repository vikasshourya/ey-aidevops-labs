# Spec: Observability stack (Block 1 solo)

Add to `day4/block1/main.tf` (or new files in `day4/block1/`) — do NOT remove the Storage + Key Vault from the guided step.

1. **Log Analytics Workspace**
   - Name: `ff-law-<same random suffix>`
   - SKU: `PerGB2018`
   - Retention: 30 days
   - Same tags as guided step
2. **App Service Plan** for the Function App
   - Name: `ff-plan`
   - OS: `Linux`
   - SKU: `Y1` (Consumption)
3. **Function App** (Linux)
   - Name: `ff-func-<same random suffix>`
   - Runtime: Python 3.11
   - Uses the Storage Account from the guided step
   - Application Insights wired to the Log Analytics Workspace
4. **Diagnostic Setting** on the Storage Account
   - Name: `diag-to-law`
   - Target: the Log Analytics Workspace above
   - Enabled logs: `StorageRead`, `StorageWrite`, `StorageDelete` on the `blob` sub-resource
5. **Outputs** (add to the file)
   - `function_app_name`
   - `log_analytics_workspace_id`

Flow: edit → `terraform fmt` → `terraform plan` → `terraform apply` → `python ..\labs\block1-iac\verify.py`.
