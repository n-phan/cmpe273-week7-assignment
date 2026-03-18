import os
from typing import Dict, List

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

REGISTRY_PORT = int(os.getenv("REGISTRY_PORT", "8001"))

app = FastAPI(title="Service Discovery Registry")

# In-memory registry for this simple assignment.
# Structure: { service_name: { instance_id: url } }
instances: Dict[str, Dict[str, str]] = {}


class RegisterRequest(BaseModel):
    service_name: str
    instance_id: str
    url: str


@app.post("/register")
def register(req: RegisterRequest):
    instances.setdefault(req.service_name, {})
    instances[req.service_name][req.instance_id] = req.url
    return {"status": "ok", "service_name": req.service_name, "instance_id": req.instance_id}


@app.get("/instances/{service_name}")
def get_instances(service_name: str) -> List[str]:
    # Return URLs for all registered instances of the service.
    return list(instances.get(service_name, {}).values())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=REGISTRY_PORT)

