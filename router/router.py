"""Minimal OpenAI-compatible model router.

Text/code requests -> self-hosted GLM replicas (sticky per session for cache hits).
Requests containing images -> an external vision model.
"""
import hashlib
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

SELF_HOSTED = [u for u in os.getenv("GLM_REPLICAS", "http://localhost:30000").split(",") if u]
SELF_MODEL = os.getenv("GLM_MODEL", "glm-5.3")
VISION_URL = os.getenv("VISION_URL", "https://api.example-vision-provider.com")
VISION_MODEL = os.getenv("VISION_MODEL", "vision-model")
VISION_KEY = os.getenv("VISION_API_KEY", "")

app = FastAPI()


def has_image(body: dict) -> bool:
    for msg in body.get("messages", []):
        content = msg.get("content")
        if isinstance(content, list) and any(p.get("type") == "image_url" for p in content):
            return True
    return False


def pick_replica(body: dict, session: str | None) -> str:
    """Hash the session id (or the system prompt) so the same conversation keeps
    hitting the same replica and reuses its prefix/KV cache."""
    msgs = body.get("messages", [])
    key = session or (str(msgs[0].get("content")) if msgs else "")
    idx = int(hashlib.sha256(key.encode()).hexdigest(), 16) % len(SELF_HOSTED)
    return SELF_HOSTED[idx]


@app.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()
    if has_image(body):
        url, headers = VISION_URL, {"Authorization": f"Bearer {VISION_KEY}"}
        body["model"] = VISION_MODEL
        route = "external-vision"
    else:
        url, headers = pick_replica(body, request.headers.get("x-session-id")), {}
        body["model"] = SELF_MODEL
        route = url
    async with httpx.AsyncClient(timeout=600) as client:
        r = await client.post(f"{url}/v1/chat/completions", json=body, headers=headers)
    return JSONResponse(r.json(), status_code=r.status_code, headers={"x-routed-to": route})


@app.get("/healthz")
def health():
    return {"replicas": SELF_HOSTED, "vision": VISION_URL}
