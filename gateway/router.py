import os
from typing import Any, Dict
from dotenv import load_dotenv
from .backends.openai_server_backend import OpenAIServerBackend

load_dotenv()

_vllm_url = os.environ.get("VLLM_BASE_URL")
_sglang_url = os.environ.get("SGLANG_BASE_URL")
if not _vllm_url or not _sglang_url:
    # The gateway can still run, but will error on requests until URLs are set.
    _vllm_url = _vllm_url or "http://127.0.0.1:8001"
    _sglang_url = _sglang_url or "http://127.0.0.1:8002"

vllm = OpenAIServerBackend(_vllm_url)
sglang = OpenAIServerBackend(_sglang_url)

def choose_backend(payload: Dict[str, Any]) -> OpenAIServerBackend:
    max_tokens = int(payload.get("max_tokens", 256) or 256)
    messages = payload.get("messages", []) or []
    approx_prompt_len = sum(len((m.get("content") or "")) for m in messages)

    # Policy (tweak freely):
    # - short prompt + small max_tokens -> SGLang
    # - else -> vLLM
    if approx_prompt_len < 1500 and max_tokens <= 256:
        return sglang
    return vllm

async def route_chat(payload: Dict[str, Any], request_id: str, stream: bool):
    primary = choose_backend(payload)
    secondary = vllm if primary is sglang else sglang

    try:
        return await primary.chat(payload, request_id=request_id, stream=stream)
    except Exception:
        # Simple failover
        return await secondary.chat(payload, request_id=request_id, stream=stream)
