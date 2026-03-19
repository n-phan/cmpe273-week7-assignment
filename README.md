# CMPE273 Week 7 - Microservice Discovery (Optional Mesh Discovery)

## Overview
This repository demonstrates service discovery with REST calls and Docker Compose.

Components:
- `registry`: stores registered instance URLs in memory
- `service` (two instances): registers itself with the registry on startup and serves `GET /work`
- `client`: discovers registered instance URLs and calls a random instance

## Run
From this directory:
```bash
docker compose up --build
```

The `client` container runs once and prints:
- discovered instance URLs
- chosen random instance
- the response from the chosen instance

## Run client again
In another terminal:
```bash
docker compose run --rm client
```

## Sample Output
Because the client selects a random instance, the chosen URL and worker response may correspond to either `service1` or `service2`.
```text
Discovered instance URLs: ['http://service1-sidecar:8000', 'http://service2-sidecar:8000']
Chosen random instance: http://service2-sidecar:8000
Worker response: {'service_name': 'demo-service', 'instance_id': 'service2', 'random_result': 483921, 'server_time': 1700000000.123}
```
<img width="3164" height="2074" alt="image" src="https://github.com/user-attachments/assets/1226bcc5-db21-45a2-b6e0-8bd0c1d8b4f4" />

## Architecture Diagram
<img width="1660" height="338" alt="image" src="https://github.com/user-attachments/assets/2d135532-135c-419c-aaa5-fde6bd9b653b" />

## Optional: Service Mesh Discovery (Istio / Linkerd)
Service meshes typically discover and route traffic using:
- **Sidecar proxies** (one per application container), commonly Envoy-based (Istio) or lightweight proxies (Linkerd)
- **Control plane** that configures sidecars, learns service endpoints, and applies routing/security policies

Conceptual call flow:
`Client app -> Sidecar proxy -> Service mesh routing -> Target sidecar proxy -> Target service`

Relation to this assignment:
- In this repo, `client.py` calls a proxy (`mesh-proxy`) and that proxy does discovery and routing using the existing `registry`.
- In a real service mesh, applications typically call a logical service name, and the mesh sidecars handle endpoint selection automatically.

Common benefits of service meshes include:
- traffic routing (load balancing, retries, timeouts, weighted routing)
- observability (metrics/tracing collected at the proxy layer)
- security (commonly mTLS and consistent auth/z policies)

### Implementation in this repo (proxy-based approximation)
Because this assignment uses plain Docker Compose (no Kubernetes mesh control plane), the “service mesh” behavior is approximated with explicit proxy containers.

New services/roles:
- `mesh-proxy` (acts like the client-sidecar/router)
  - exposes `GET /work`
  - queries `registry` for `demo-service` instances
  - randomly selects an endpoint and forwards the request to `GET /work`
- `service_sidecar` (acts like a target-sidecar)
  - exposes `GET /work`
  - forwards the request to the real worker container (`service1` or `service2`)

Registration behavior:
- `service1` and `service2` register the *sidecar URLs* (`service1-sidecar:8000`, `service2-sidecar:8000`) so that discovery returns proxy endpoints instead of raw worker endpoints.

Resulting call path in this repo:
`client -> mesh-proxy -> (service1-sidecar | service2-sidecar) -> (service1 | service2)`
