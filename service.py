import os
import random
import time

import requests
import uvicorn
from fastapi import FastAPI


SERVICE_NAME = os.getenv("SERVICE_NAME", "demo-service")
INSTANCE_ID = os.getenv("INSTANCE_ID", "unknown")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))

REGISTRY_URL = os.getenv("REGISTRY_URL", "http://registry:8001")

# Use the container's internal DNS name (set in docker-compose.yml).
SERVICE_URL = os.getenv("SERVICE_URL", f"http://{INSTANCE_ID}:8000")

app = FastAPI(title=f"Worker Instance {INSTANCE_ID}")


@app.get("/work")
def work():
    # Simple payload so you can see which instance got called.
    return {
        "service_name": SERVICE_NAME,
        "instance_id": INSTANCE_ID,
        "random_result": random.randint(1, 1000000),
        "server_time": time.time(),
    }


def register_with_registry() -> None:
    url = f"{REGISTRY_URL}/register"
    payload = {"service_name": SERVICE_NAME, "instance_id": INSTANCE_ID, "url": SERVICE_URL}

    # Retry briefly until the registry comes up.
    for _ in range(20):
        try:
            r = requests.post(url, json=payload, timeout=2)
            if r.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(0.5)

    raise RuntimeError(f"Failed to register with registry at {url}")


@app.on_event("startup")
def on_startup():
    register_with_registry()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)

