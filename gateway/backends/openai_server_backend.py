from typing import AsyncIterator, Dict, Any, Union
import httpx
from .base import Backend

class OpenAIServerBackend(Backend):
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def chat(self, payload: Dict[str, Any], request_id: str, stream: bool) -> Union[Dict[str, Any], AsyncIterator[str]]:
        url = f"{self.base_url}/v1/chat/completions"

        async with httpx.AsyncClient(timeout=None) as client:
            if stream:
                async def agen() -> AsyncIterator[str]:
                    async with client.stream("POST", url, json=payload) as r:
                        r.raise_for_status()
                        async for line in r.aiter_lines():
                            if line:
                                yield line
                return agen()

            r = await client.post(url, json=payload)
            r.raise_for_status()
            return r.json()
