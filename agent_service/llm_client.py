import os, json
from typing import Any, Dict
import httpx
from dotenv import load_dotenv

load_dotenv()
GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://127.0.0.1:8000/v1/chat/completions")
API_KEY = os.environ.get("GATEWAY_API_KEY", "").strip()
MODEL = os.environ.get("VLLM_MODEL", "Qwen/Qwen2.5-3B-Instruct")

async def chat_json(prompt: str, max_tokens: int = 700, temperature: float = 0.7) -> Dict[str, Any]:
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.post(GATEWAY_URL, json=payload, headers=headers)
        if r.status_code >= 400:
            raise RuntimeError(f"Gateway error {r.status_code}: {r.text[:500]}")

        r.raise_for_status()
        data = r.json()

    content = data["choices"][0]["message"]["content"]
    return json.loads(content)
