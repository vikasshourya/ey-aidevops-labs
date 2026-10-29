# Capstone: QuickQuote (take-home)

**Due:** Wed 4 Nov 2026 EOD IST. **Submit:** send the trainer your GitHub fork link, the README below, and two screenshots.
Trainer reviews and signs off your certificate. Your lab namespace and resource group stay available until then.

> **Start here:** follow `GUIDE.md` in this folder. It walks you through the build step by step, with the exact prompts and commands.

## The ask

Build and deploy **QuickQuote**, a tiny service:

| Endpoint | Behaviour |
|---|---|
| `GET /quote?symbol=XYZ` | Returns `{"symbol":"XYZ","price": <float>,"ts": "<iso8601>"}`. Price can be fake or random. |
| `GET /health` | Returns `200` with body `ok`. |

- Any language. Keep it tiny.
- Container: non-root user, pinned base image (no `:latest`), a healthcheck.
- Deployed to your AKS namespace with a **Helm chart** (probes and resource limits set).
- Image name starts with your namespace: `$env:ACR_LOGIN_SERVER/$env:NAMESPACE/quickquote:v1`.
- Optional stretch: a Terraform Key Vault in your own resource group that stores a fake API key (use the Block 1 spec style).

## Put it in your fork under `capstone/`

```
capstone/
  app/
  Dockerfile
  helm/
  terraform/        (optional stretch)
  README.md
```

## README.md must include

1. The spec you gave Copilot (prompt and any spec file).
2. One thing Copilot got wrong, and how you caught it.
3. Screenshot: `kubectl get pods` and `helm list` for your namespace.
4. Screenshot: `curl` to `/quote?symbol=MSFT` returning JSON.
5. If you did the stretch: the `terraform plan` summary line.

## Scoring (100)

| Item | Points |
|---|---|
| `/quote` and `/health` respond through port-forward | 30 |
| Dockerfile: non-root, pinned base, healthcheck | 20 |
| Helm chart installs cleanly, probes and resources set | 25 |
| README items 1 to 4 | 25 |

## Hints

- Reuse your Day 1 prompts for the Dockerfile and Helm chart.
- Run `trivy image` on your image and fix what it flags.
- If you get stuck, ask Copilot with the exact error and the file attached, and read the fix before accepting it.
