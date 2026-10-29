# Day 4 — Automate: block-by-block design (for review, not yet built)

Date: Thu 29 Oct 2026, 09:00–13:00 IST. 11 participants, virtual. Trainer: Anil. HTML pages distributed via GitHub.

Theme: **Automate** — close the 4-day arc. Spec-driven IaC through a PR pipeline, build a working DevOps agent, and see cost of what AI builds.

## Day shape
| Slot | Mins | Content |
|---|---|---|
| Recap | 10 | Days 1–3 recap, Day 4 arc, scoreboard reset |
| Block 1 | 70 | Terraform + AI + GitHub + PR → Azure |
| Block 2 | 70 | Build a DevOps agent (rollback with approval) |
| Break | 20 | — |
| Block 3 | 60 | FinOps — cost of what AI builds |
| Closing lab + debrief | 20 | Mystery app vibe-deploy OR chaos round + 4-day debrief + capstone briefing |

Trainer talk ~25%, participant work ~75%. Co-facilitator unblocks in chat.

---

## Block 1 — Vibe-code IaC, ship via PR to Azure (70 min)

Teaches: Terraform fundamentals, spec-driven authoring, GitOps-for-IaC, PR-based deploy.

### Concept (10 min)
- Terraform refresher: providers, resources, state, plan vs apply, drift.
- Why spec-driven beats "write terraform for storage": pinned provider version, naming convention, tags, soft-delete, versioning — all stated as numbered requirements.
- One visual: local apply vs PR → Actions → apply flow. Why PR flow is production practice.
- One real example: a 3-line prompt vs a 15-line spec, side by side on the same ask.

### Guided (25 min)
Trainer demos, participants follow in their own `rg-ff-uNN`.
1. Open `spec/block1_storage.md` — numbered requirements:
   - azurerm provider pinned ~> 4.0
   - RG `rg-ff-uNN` (already exists, data source)
   - Storage Account: Standard_LRS, versioning on, HTTPS only, min TLS 1.2
   - Key Vault: soft-delete on, purge-protection on
   - Tags: `owner`, `course=ey-aidevops`, `day=4`
   - Naming: `ff{uNN}sa<rand>`, `ff{uNN}-kv-<rand>`
2. Copilot writes `main.tf` from spec. Trainer calls out what Copilot gets wrong (deprecated args, missing dependencies, wrong API version).
3. `terraform init / fmt / validate / plan / apply` locally.
4. Open Azure Portal → show the resources live.
5. Commit, push to a branch, open PR.
6. GitHub Actions runs `terraform plan` on PR (comment on PR with plan output). Merge → `apply` on main.
7. Checkpoint pause: everyone's PR green?

### Solo (30 min)
New spec: `spec/block1_solo.md` — Log Analytics workspace + Function App (consumption plan) + diagnostic settings on the storage account wired to the workspace.
- Full flow: vibe `main.tf` → `plan` locally → PR → Actions green → merge → apply → verify in portal.
- Paste into HTML page: (a) PR URL, (b) `az resource list -g rg-ff-uNN -o table` output.
- Checker: `verify_block1.py` compares `az resource list` JSON to expected resource types; name match not required, type match required.

### Debrief (5 min) + quiz
- What Copilot got wrong this time. One lesson.
- Quiz (3 questions, in HTML page):
  1. Why pin the provider version in the spec?
  2. What does `terraform plan` show that `apply` does not?
  3. Why run `plan` on PR instead of only `apply` on merge?

### What gets pasted back
- PR URL
- `az resource list` output
- Quiz answers

---

## Block 2 — Build a DevOps agent (70 min)

Teaches: agent loop, tool use, human approval gates, audit trail. One agent, not three. Scope confirmed: deploy health-check + rollback with approval.

### Concept (10 min)
- What makes something an "agent" vs a script: loop, tools, decide, approval gate.
- Anatomy of this agent: inputs (deployment name, namespace), tools (`kubectl get`, `kubectl logs`, metrics query, `kubectl rollout undo`), decision (healthy/unhealthy), approval, action, audit log.
- Why approval gate matters in prod — the "trust but verify" thesis applied to agents.
- One visual: the loop. One real example: a broken deploy, what the agent sees step by step.

### Guided (25 min)
Starter files in `day4/agent/`:
- `agent.py` — skeleton: loop, tool registry, LLM call, approval prompt, audit log writer. Marked `# TODO` where logic goes.
- `tools.py` — ready: `get_pods`, `get_logs`, `get_metrics` (stub), `rollout_undo`, `rollout_history`.
- `incident.yaml` — one broken deployment the trainer will apply to each namespace.
- `audit.log` — append-only JSON lines.

Trainer walks through:
1. Read the skeleton together. Mark the 4 TODOs.
2. Fill TODO 1 (define the tool schema for the LLM) with Copilot.
3. Fill TODO 2 (health check logic: ready replicas vs desired, error rate from logs) with Copilot.
4. Fill TODO 3 (approval gate: print proposed action, wait for `yes`).
5. Fill TODO 4 (audit log: who, what, when, why).
6. Run against a healthy deploy — agent says "healthy, no action". Run against the broken deploy — agent proposes rollback, waits for approval.
7. Checkpoint: everyone's agent runs end-to-end.

### Solo (30 min)
Extend the agent. Pick one (or both if fast):
- **Add a check**: HTTP error rate > 5% in the last 60s → unhealthy. Use `kubectl logs` or a metrics stub.
- **Tighten approval**: require typing the deployment name (not just `yes`), and refuse to rollback if the previous revision is also broken.

Paste into HTML page: (a) the code diff, (b) audit log output for one healthy and one broken run.

### Debrief (5 min) + quiz
- Where the agent could still go wrong (hallucinated kubectl, wrong namespace, loop runaway).
- Quiz (3 questions):
  1. Why is the approval gate not just a safety feature but a learning feature for the operator?
  2. What's in the audit log that a plain `kubectl rollout undo` command doesn't give you?
  3. Name one scenario where this agent should refuse to act, even with approval.

### What gets pasted back
- Code diff of their extension
- Audit log for test runs
- Quiz answers

---

## Block 3 — FinOps: what did AI just cost you? (60 min)

Teaches: cost of AI-generated infra, cost estimation in CI, actuals from the portal. Shorter block (60 min, not 70) to make room for the closing lab.

### Concept (10 min)
- The AI-era FinOps problem: AI writes IaC in minutes; a wrong SKU runs for months.
- Three cost signals: estimate (Infracost on plan), budget (Azure Budgets), actuals (`az consumption usage list`).
- One visual: cost pipeline — plan → infracost → PR comment → merge → actuals.
- One real example: the Block 1 Function App on Premium plan vs Consumption — 100x difference.

### Guided (20 min)
1. Install/configure Infracost on the Block 1 repo (trainer-provided API key via lab card).
2. Run `infracost breakdown --path .` against Block 1 Terraform. See monthly cost.
3. Add Infracost to the Actions workflow — PR now gets a cost diff comment.
4. Run `az consumption usage list -g rg-ff-uNN` for yesterday's spend.
5. Open Azure Cost Analysis in portal for their RG.

### Solo (25 min)
Spec: `spec/block3_solo.md` — the same Function App, but with Copilot deliberately asked for "high performance". It will suggest Premium plan + Standard storage. Participant must:
- Run Infracost — see the cost jump.
- Edit the spec with cost constraints ("Consumption plan, LRS, no premium tiers").
- Re-run Infracost — see cost drop.
- Paste: before/after Infracost output + the spec diff.

### Debrief (5 min) + quiz
- Where cost snuck in. What the spec should always say.
- Quiz (3 questions):
  1. Why is Infracost on PR better than Azure Budgets alone?
  2. Name one Azure resource where AI commonly picks an expensive default.
  3. What's one line you will add to every IaC spec from Monday?

### What gets pasted back
- Infracost before/after
- Spec diff
- Quiz answers

---

## Closing lab + 4-day debrief (20 min)

Pick ONE closing lab (choose at dry run based on energy):

### Option A — Mystery app vibe-deploy (15 min lab + 5 min debrief)
- Trainer drops a one-line spec in chat: "a URL shortener with Redis, exposed via Ingress, `/health` returning 200".
- First to a working `/health` 200 on their AKS namespace wins. Share screen.
- Uses: spec, Copilot, Terraform (if needed), Helm, deploy, verify. Pure Day 1–4 payoff.

### Option B — Break my deploy (15 min lab + 5 min debrief)
- Trainer breaks a running app on AKS in each namespace (bad image or missing secret).
- Participants run their Block 2 agent + Copilot + kubectl to find and fix.
- Scoreboard by time-to-green.

### 4-day debrief (5 min)
- The thread across 4 days: spec > prompt, verify with numbers, approval gates, cost.
- Capstone briefing: take-home, submit via PR within 5 days (details in `day4/capstone.md`).
- Certificate + LinkedIn one-liner handed out.
- Optional 30-day follow-up office hour announced.

---

## Capstone (take-home, after class)

Handed out in the closing block, deadline Wed 4 Nov 2026 EOD.

### Spec (given)
Build and deploy "QuickQuote" — a tiny micro-app:
- `/quote?symbol=XYZ` returns a fake stock quote JSON.
- `/health` returns 200.
- Containerized, deployed to their AKS namespace via Helm, infra provisioned via Terraform (ACR already exists, so only app-specific resources).
- GitHub Actions pipeline: on PR plan + build, on merge deploy.

### Deliverables (via PR to their fork)
- `app/` — code (any language)
- `Dockerfile`
- `helm/` — chart
- `terraform/` — any extra Azure resources (e.g. a Key Vault for an API key)
- `.github/workflows/` — pipeline
- `README.md` — spec they used + what Copilot got wrong + screenshot of Azure Portal showing resources + screenshot of `/quote` response

### Verification (trainer async)
- `verify_capstone.py` script in repo — participant runs it, pastes output in the PR description.
- Trainer reviews PR, comments, approves. Certificate on approval.

---

## Files to build (not yet started)

| File | Purpose |
|---|---|
| `day4/index.html` | Day 4 landing page |
| `day4/block1.html` | Block 1 lab page |
| `day4/block2.html` | Block 2 lab page |
| `day4/block3.html` | Block 3 lab page |
| `day4/closing.html` | Closing lab + debrief + capstone briefing |
| `day4/spec/block1_storage.md` | Block 1 guided spec |
| `day4/spec/block1_solo.md` | Block 1 solo spec |
| `day4/spec/block3_solo.md` | Block 3 solo spec |
| `day4/agent/agent.py` | Agent skeleton with TODOs |
| `day4/agent/tools.py` | Ready tool implementations |
| `day4/agent/incident.yaml` | Broken deployment |
| `day4/capstone.md` | Take-home capstone brief |
| `day4/verify_block1.py` | Block 1 checker |
| `day4/verify_capstone.py` | Capstone checker |
| `.github/workflows/terraform.yml` | PR plan + merge apply |
| `.github/workflows/infracost.yml` | Cost diff on PR |

## Open items before build
- Infracost API key provisioning (free tier is enough for 11 users).
- Confirm the broken-deploy incident is namespace-scoped and reversible per participant.
- Confirm `az consumption` returns data for same-day usage (sometimes delayed 24h — may need to show yesterday's spend from Days 1–3).
- Capstone deadline: Wed 4 Nov vs Fri 6 Nov — your call.
- Choose Option A or B for the closing lab at the dry run.
