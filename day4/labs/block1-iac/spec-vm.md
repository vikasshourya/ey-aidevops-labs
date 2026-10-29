# Bonus spec: the smallest VM on Azure (create, see, destroy)

Story: FastFreight needs a throwaway test server for ShipWave. It must be the cheapest possible, private, and gone when you are done.

Work in a NEW folder: `C:\EYLAB\ey-aidevops-labs\day4\vm` (file: `main.tf`).

## Requirements
1. Providers: azurerm pinned to ~> 4.0 and tls pinned to ~> 4.0. In the azurerm provider block set `features {}` and `resource_provider_registrations = "none"`.
2. Variables `resource_group_name` and `location` (no defaults; values come from `TF_VAR_*`). Use a `data` source for the existing resource group. Do not create a new one.
3. Network: one virtual network (10.10.0.0/16) with one subnet (10.10.1.0/24).
4. One network interface in that subnet. NO public IP.
5. One Linux VM: size `Standard_B1s`, Ubuntu 22.04 LTS, OS disk `Standard_LRS`, SSH key login only (generate the key with the `tls_private_key` resource; password login disabled), admin user `ffadmin`.
6. Names: VM `ff-vm-` + `var.resource_group_name`. Tags on every resource: `owner = var.resource_group_name`, `course = "ey-aidevops"`, `day = "4"`.
7. Outputs: `vm_name`, `private_ip`.

## Run
`terraform init`, `terraform fmt`, `terraform validate`, `terraform plan` (read it: how many resources?), `terraform apply -auto-approve`.

Trainer shows the VMs live in the portal. Then:

`terraform destroy -auto-approve`
