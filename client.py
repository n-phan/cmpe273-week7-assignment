import os
import random
import time

import requests


SERVICE_NAME = os.getenv("SERVICE_NAME", "demo-service")
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://registry:8001")
MESH_PROXY_URL = os.getenv("MESH_PROXY_URL", "")


def main() -> None:
    # Optional mesh-style flow:
    # Client calls a local proxy ("sidecar-style") that does instance discovery + routing.
    if MESH_PROXY_URL:
        mesh_url = f"{MESH_PROXY_URL}/work"
        payload = None

        # `depends_on` only waits for container start, not for the server to be ready.
        last_error: Exception | None = None
        for attempt in range(30):
            try:
                resp = requests.get(mesh_url, timeout=2)
                resp.raise_for_status()
                payload = resp.json()
                break
            except requests.RequestException as e:
                last_error = e
                # Avoid a tight loop; mesh-proxy may not have bound the port yet.
                time.sleep(0.25)
                continue

        if payload is None:
            raise RuntimeError(f"Failed to reach mesh proxy at {mesh_url}: {last_error}")

        print("Discovered instance URLs:", payload.get("discovered_instance_urls"))
        print("Chosen random instance:", payload.get("chosen_instance_url"))
        print("Trace id:", payload.get("trace_id"))
        print("Worker response:", payload.get("worker_response"))
        return

    instances_url = f"{REGISTRY_URL}/instances/{SERVICE_NAME}"

    # Wait a moment for workers to register.
    urls = []
    for _ in range(20):
        r = requests.get(instances_url, timeout=5)
        r.raise_for_status()
        urls = r.json()
        if urls:
            break
        continue
    if not urls:
        raise RuntimeError(f"No instances registered for service_name={SERVICE_NAME}")

    chosen = random.choice(urls)
    resp = requests.get(f"{chosen}/work", timeout=5)
    resp.raise_for_status()

    print("Discovered instance URLs:", urls)
    print("Chosen random instance:", chosen)
    print("Worker response:", resp.json())


if __name__ == "__main__":
    main()

