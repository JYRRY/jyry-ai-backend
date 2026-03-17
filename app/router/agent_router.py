import logging
from typing import Any

from app.agents.base_agent import BaseAgent
from app.agents.german_teacher.agent import GermanTeacherAgent

logger = logging.getLogger(__name__)


class AgentRouter:
    """
    Central dispatcher for all JYRY AI agents.

    Uses a registry pattern: each agent registers itself under its `agent_id`.
    To add a new agent to the platform, create it and add one line to
    `_register_defaults()` — nothing else needs to change.

    Example:
        router.dispatch("german_teacher", {"task": "free_chat", ...})
    """

    def __init__(self) -> None:
        self._registry: dict[str, BaseAgent] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register all built-in agents. Add new agents here."""
        self.register(GermanTeacherAgent())
        # Future agents — uncomment when ready:
        # self.register(MathTutorAgent())
        # self.register(TranslationAgent())
        # self.register(EnglishTeacherAgent())

    def register(self, agent: BaseAgent) -> None:
        """Add an agent to the registry."""
        self._registry[agent.agent_id] = agent
        logger.info("AgentRouter | Registered agent: %s", agent.agent_id)

    def available_agents(self) -> list[str]:
        """Return all registered agent IDs."""
        return list(self._registry.keys())

    async def dispatch(
        self, agent_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Route a request to the appropriate agent.

        Args:
            agent_id: The target agent's identifier string.
            payload:  Raw request data to pass to the agent.

        Returns:
            The agent's response as a plain dict.

        Raises:
            ValueError: If `agent_id` is not registered.
        """
        agent = self._registry.get(agent_id)
        if agent is None:
            available = self.available_agents()
            raise ValueError(
                f"No agent registered with id '{agent_id}'. "
                f"Available agents: {available}"
            )

        logger.info("AgentRouter | Dispatching to agent: %s", agent_id)
        return await agent.process(payload)


# Module-level singleton — created once at import, shared across all requests
router = AgentRouter()
