from abc import ABC, abstractmethod
from typing import AsyncIterator, Union, Dict, Any

class Backend(ABC):
    @abstractmethod
    async def chat(self, payload: Dict[str, Any], request_id: str, stream: bool) -> Union[Dict[str, Any], AsyncIterator[str]]:
        ...
