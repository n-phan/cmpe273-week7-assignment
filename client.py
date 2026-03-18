import os
import random

import requests


SERVICE_NAME = os.getenv("SERVICE_NAME", "demo-service")
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://registry:8001")


def main() -> None:
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

