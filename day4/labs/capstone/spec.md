# QuickQuote Spec

1. `GET /quote?symbol=XYZ` returns JSON with `symbol`, `price`, and `ts` fields.
2. The `symbol` field echoes the requested symbol exactly.
3. The `price` field is a floating-point number and may be random or fake.
4. The `ts` field is an ISO 8601 timestamp.
5. `GET /health` returns HTTP 200 with body `ok`.
6. The application listens on port 8000.
7. The Docker image uses a pinned base image tag and never uses `latest`.
8. The container runs as a non-root user with a numeric UID of 1000 or higher.
9. The Dockerfile includes a `HEALTHCHECK`.
10. The Helm chart defines a `quickquote` Deployment and Service on port 8000 with 2 replicas, probes, and resource requests/limits.