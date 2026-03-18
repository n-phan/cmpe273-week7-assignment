import os

import requests
import uvicorn
from fastapi import FastAPI

WORKER_URL = os.getenv("WORKER_URL", "http://service:8000")
SIDECAR_PORT = int(os.getenv("SIDECAR_PORT", "8000"))

app = FastAPI(title="Worker Sidecar Proxy")


@app.get("/work")
def work():
    # Forward the request to the real worker instance.
    resp = requests.get(f"{WORKER_URL}/work", timeout=5)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SIDECAR_PORT)

