from abc import ABC, abstractmethod
from typing import Any

import anthropic

from app.config import settings


class BaseAgent(ABC):
    """
    Abstract base class for all JYRY AI agents.

    Every agent must define:
    - agent_id: unique string used by the router to identify this agent
    - process(): receives a raw payload dict, returns a result dict

    The shared Anthropic async client is a class-level singleton —
    one connection pool reused across all agents and requests.
    """

    _client: anthropic.AsyncAnthropic | None = None
    model: str = settings.claude_model
    max_tokens: int = settings.max_tokens

    @classmethod
    def get_client(cls) -> anthropic.AsyncAnthropic:
        if cls._client is None:
            cls._client = anthropic.AsyncAnthropic(
                api_key=settings.anthropic_api_key
            )
        return cls._client

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Unique identifier used by the router, e.g. 'german_teacher'."""
        ...

    @abstractmethod
    async def process(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Core agent logic.

        Args:
            payload: Raw validated dict from the API request.

        Returns:
            Raw dict that will be serialised as JSON to the client.
        """
        ...
