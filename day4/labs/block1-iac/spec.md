# Spec: Storage + Key Vault (Block 1 guided)

Build Terraform in `day4/block1/main.tf` that provisions, in your resource group (it already exists, created by the trainer):

1. **Provider**: `azurerm` pinned to `~> 4.0`. Features block required.
2. **Variables and Resource Group**: declare `variable "resource_group_name"` and `variable "location"` (no defaults; their values come from environment variables TF_VAR_resource_group_name and TF_VAR_location, already set). Use the existing resource group as a `data` source. Do NOT create it. Use `data.azurerm_resource_group.rg.location` for resources.
3. **Storage Account**
   - Name: `ffsa` + `random_string` suffix (length 6, lower case, numbers only, no special)
   - Location: same as RG
   - Replication: `LRS`
   - Tier: `Standard`
   - Blob versioning: enabled
   - HTTPS only: true
   - Minimum TLS version: `TLS1_2`
4. **Key Vault**
   - Name: `ff-kv-` + the same random suffix
   - SKU: `standard`
   - Soft delete retention: 7 days
   - Purge protection: enabled
   - Tenant ID: from `data.azurerm_client_config.current.tenant_id`
5. **Tags on both resources**
   - `owner  = var.resource_group_name`
   - `course = "ey-aidevops"`
   - `day    = "4"`
6. **Outputs**
   - `storage_account_name`
   - `key_vault_name`

Add `provider "azurerm" { features {} }`. Authentication comes from the ARM_* environment variables: do not put any credentials in the file.
