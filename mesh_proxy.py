import os
import random
import time
import uuid

import requests
import uvicorn
from fastapi import FastAPI, HTTPException

SERVICE_NAME = os.getenv("SERVICE_NAME", "demo-service")
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://registry:8001")

MESH_PORT = int(os.getenv("MESH_PORT", "9000"))

app = FastAPI(title="Mesh Proxy (Sidecar-style)")


def discover_instances() -> list[str]:
    instances_url = f"{REGISTRY_URL}/instances/{SERVICE_NAME}"

    # Retry briefly until the workers have registered.
    for _ in range(20):
        try:
            r = requests.get(instances_url, timeout=2)
            r.raise_for_status()
            urls = r.json()
            if urls:
                return urls
        except requests.RequestException:
            pass
        time.sleep(0.25)

    raise HTTPException(
        status_code=503,
        detail=f"No instances registered for service_name={SERVICE_NAME}",
    )


@app.get("/work")
def work():
    trace_id = uuid.uuid4().hex

    urls = discover_instances()

    # If sidecars/workers are still warming up, try multiple endpoints.
    last_error: Exception | None = None
    shuffled_urls = random.sample(urls, k=len(urls))
    chosen: str | None = None
    resp_json = None

    for url in shuffled_urls:
        try:
            chosen = url
            resp = requests.get(f"{url}/work", timeout=5)
            resp.raise_for_status()
            resp_json = resp.json()
            break
        except requests.RequestException as e:
            last_error = e

    if resp_json is None or chosen is None:
        raise HTTPException(status_code=502, detail=f"All endpoints failed: {last_error}")

    return {
        "service_name": SERVICE_NAME,
        "trace_id": trace_id,
        "discovered_instance_urls": urls,
        "chosen_instance_url": chosen,
        "worker_response": resp_json,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=MESH_PORT)

