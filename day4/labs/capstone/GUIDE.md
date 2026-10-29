# Capstone guide: build and deploy QuickQuote, step by step

Time: about 90 minutes. Everything here is something you already did on Day 1 for the Shipwave API. Same tools, new small service.

**The story.** FastFreight's traders want a tiny internal service that returns a price for a stock symbol. You will spec it, build it with Copilot, containerize it, and deploy it to your own AKS namespace. Then prove it works.

**Setup, every new terminal:**

```
. C:\EYLAB\ey-aidevops-labs\lab-env.ps1
```

**Working folder:** your fork of the labs repo (from Day 1). All files go under `capstone\` in that fork.

```
cd C:\EYLAB\ey-aidevops-labs
mkdir -Force capstone\app
mkdir -Force capstone\helm
cd capstone
```

---

## Step 1. Write your spec first (10 min)

Create `capstone\spec.md` and write 8 to 10 numbered requirements. Copy the style of your Day 1 `api-container-spec.md`. Cover:

1. App: `GET /quote?symbol=XYZ` returns `{"symbol":"XYZ","price":<float>,"ts":"<ISO8601>"}`. Price is random. `GET /health` returns 200 and `ok`.
2. App port is 8000.
3. Base image pinned to an exact tag (for example `python:3.12-slim`), never `latest`.
4. Runs as non-root, numeric UID 1000 or higher.
5. Healthcheck in the Dockerfile.
6. Helm chart in `helm/` with `image.repository` and `image.tag` as values, a Deployment and a Service named `quickquote` on port 8000.
7. 2 replicas, requests 100m CPU and 128Mi memory, limits 250m CPU and 256Mi memory.
8. Liveness and readiness probes on `/health`.
9. Image name: `<ACR>/<NAMESPACE>/quickquote:v1`.

**Done when:** your spec has numbered, checkable requirements. This file goes in your README (item 1).

## Step 2. Build the app with Copilot (10 min)

Open Copilot Chat in **Agent mode**.

```
Read #file:spec.md. Create capstone/app/main.py (FastAPI) and capstone/app/requirements.txt that meet requirement 1 and 2. Keep it under 30 lines. Edit the files directly.
```

Test it locally first:

```
cd app
pip install -r requirements.txt
uvicorn main:app --port 8000
```

In a second terminal:

```
curl.exe http://localhost:8000/health
curl.exe "http://localhost:8000/quote?symbol=MSFT"
```

**Done when:** `/health` returns `ok` and `/quote` returns JSON. Stop the server with Ctrl+C. (If `uvicorn` is not found, run `pip install fastapi uvicorn`.)

## Step 3. Dockerfile (10 min)

```
Read #file:spec.md. Write capstone/Dockerfile for the app in capstone/app that meets requirements 3, 4 and 5 (pinned base, non-root with a numeric UID, HEALTHCHECK). Also write capstone/.dockerignore. Edit the files directly.
```

Read what it wrote. Check for: a numeric `USER`, no `:latest`, a `HEALTHCHECK` line.

## Step 4. Build, scan, push (15 min)

```
cd C:\EYLAB\ey-aidevops-labs\capstone
$img = "$env:ACR_LOGIN_SERVER/$env:NAMESPACE/quickquote:v1"
docker build -t $img .
docker run --rm --entrypoint id $img
```

The `id` line should show a UID that is **not 0**.

```
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 $img
```

If Trivy exits with 1, read the findings, change the base image or packages, and rebuild. Then push:

```
docker push $img
```

**Done when:** build works, UID is not 0, Trivy exits 0, push succeeds.

## Step 5. Helm chart (20 min)

```
Read #file:spec.md and #file:Dockerfile. Create a Helm chart in capstone/helm/ (Chart.yaml, values.yaml, templates/deployment.yaml, templates/service.yaml) that meets requirements 6, 7 and 8 and uses image.repository and image.tag as values. Edit the files directly.
```

Check the chart:

```
helm lint helm/
```

Install it:

```
helm upgrade --install quickquote helm/ -n $env:NAMESPACE --set image.repository="$env:ACR_LOGIN_SERVER/$env:NAMESPACE/quickquote" --set image.tag=v1 --wait --timeout 3m
kubectl -n $env:NAMESPACE get pods
```

**Done when:** `helm lint` shows 0 charts failed, and the quickquote pods are `Running` and `READY 1/1`.

If a pod is not Ready, run `kubectl -n $env:NAMESPACE describe pod <pod-name>`. The events at the bottom tell you why (wrong image name, failing probe, quota).

## Step 6. Prove it works (10 min)

Terminal 2 (leave it open):

```
kubectl -n $env:NAMESPACE port-forward svc/quickquote 8080:8000
```

Terminal 1:

```
curl.exe http://localhost:8080/health
curl.exe "http://localhost:8080/quote?symbol=MSFT"
```

Take two screenshots:
1. `kubectl -n $env:NAMESPACE get pods` and `helm list -n $env:NAMESPACE` together.
2. The `curl` call to `/quote?symbol=MSFT` returning JSON.

## Step 7. README and submit (15 min)

Edit `capstone\README.md` (the template in the capstone folder of the labs repo). It must contain:

1. Your spec (paste `spec.md` or the prompt).
2. **One thing Copilot got wrong and how you caught it.** Be specific: which file, what was wrong, how you noticed (Trivy, `helm lint`, a pod that was not Ready, `id` showing root).
3. Screenshot of pods and `helm list`.
4. Screenshot of the `/quote` curl.
5. Stretch only: the `terraform plan` summary line.

Commit and push to your fork:

```
git add capstone
git commit -m "capstone: quickquote"
git push
```

Send the trainer your fork link plus the two screenshots before **Wed 4 Nov, end of day IST**.

---

## Stretch (optional): Key Vault with Terraform

Reuse your Block 1 spec. In `capstone\terraform\`, ask Copilot for a Key Vault in your resource group plus one secret holding a fake API key. Remember the three lessons from Block 1: pin `azurerm ~> 4.0`, set `resource_provider_registrations = "none"`, and set `purge_soft_delete_on_destroy = false` inside `features { key_vault { } }`. Run `terraform init`, `plan`, and add the plan summary line to your README. Do not apply unless you are happy to leave it running.

## Stuck? Quick fixes

| Problem | Try |
|---|---|
| `docker` not found or cannot connect | Open a NEW PowerShell window after `lab-env.ps1`, then run `docker version` |
| `unauthorized` on `docker push` | Image name must start with your namespace. Re-run `. lab-env.ps1` (it logs Docker in) |
| `ImagePullBackOff` | Wrong image name or tag. Compare with `kubectl -n $env:NAMESPACE describe pod` |
| Pod `CrashLoopBackOff` | `kubectl -n $env:NAMESPACE logs <pod>`. Often the app port or start command |
| Readiness probe failed | Probe path and port must match the app: `/health` on 8000 |
| Pods Pending | Namespace quota. Check requests and limits match requirement 7 and use 2 replicas |
| Trivy fails | Update the base image tag, rebuild, scan again |

## Score check (self-assess before you submit)

| Item | Points | Your proof |
|---|---|---|
| `/quote` and `/health` respond via port-forward | 30 | screenshot 2 |
| Dockerfile: non-root, pinned base, healthcheck | 20 | `docker run ... id` shows UID not 0, no `:latest`, HEALTHCHECK present |
| Helm chart installs cleanly, probes and resources set | 25 | `helm lint` clean, pods READY |
| README items 1 to 4 | 25 | complete README |
