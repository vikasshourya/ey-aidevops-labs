# Spec: "High performance" API backend (Block 3 solo)

Starting point: a NEW folder `day4/block3/main.tf`. Prompt Copilot deliberately with cost blindness, then fix the spec.

## Round 1 — careless prompt
Ask Copilot:

```
Create Azure Terraform for a high-performance API backend in a resource group:
- a web app for a Python API
- a SQL database for the data
- Redis for caching
Make it production-ready.
```

Copilot will reach for Premium plans, General Purpose SQL, Standard Redis. Run:

```
infracost breakdown --path .
```

Note the monthly estimate.

## Round 2 — spec with cost constraints
Rewrite the ask with limits and give it to Copilot again:

```
Create Azure Terraform for a low-traffic API backend in a resource group:
- App Service: Linux, SKU B1 (Basic) only. No Premium, no autoscale.
- SQL Database: SKU Basic (5 DTU), 2GB max size.
- Redis: Basic C0 (250MB) only.
- All resources: LRS/local redundancy. No geo-replication.
- Tags: owner, course=ey-aidevops, day=4
```

Run Infracost again. Note the new monthly estimate.

## Paste back
- Round 1 monthly cost: $______
- Round 2 monthly cost: $______
- Difference: $______ (___x cheaper)
- The one line you will add to EVERY future IaC spec: _______________
