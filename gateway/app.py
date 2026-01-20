import os
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv
from .router import route_chat

load_dotenv()
API_KEY = os.environ.get("GATEWAY_API_KEY", "").strip()

app = FastAPI(title="PulseForge Gateway", version="0.1")

def _auth(req: Request):
    if not API_KEY:
        return
    auth = req.headers.get("authorization") or ""
    if auth != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/v1/chat/completions")
async def chat_completions(req: Request):
    _auth(req)
    payload = await req.json()
    request_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"

    if payload.get("stream", False):
        async def gen():
            agen = await route_chat(payload, request_id=request_id, stream=True)
            async for line in agen:
                # pass through SSE lines from worker (already OpenAI-style)
                yield (line + "\n")
        return StreamingResponse(gen(), media_type="text/event-stream")

    resp = await route_chat(payload, request_id=request_id, stream=False)
    return JSONResponse(resp)
