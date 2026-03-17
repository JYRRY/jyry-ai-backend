import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.router.agent_router import router as agent_router

logger = logging.getLogger(__name__)

v1_router = APIRouter()


# ── Request schema for the generic /chat endpoint ─────────────────────────────

class AgentRequest(BaseModel):
    """
    Generic request envelope for all agents.

    The `agent_id` tells the router which agent to invoke.
    The `payload` is passed as-is to that agent's process() method.
    """

    agent_id: str = Field(
        ...,
        examples=["german_teacher"],
        description="ID of the target agent (see GET /agents for options).",
    )
    payload: dict[str, Any] = Field(
        ...,
        description="Agent-specific request data.",
        examples=[
            {
                "task": "correct_writing",
                "level": "A2",
                "text": "Ich gehe gestern in die Schule.",
                "language": "ar",
            }
        ],
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@v1_router.get(
    "/agents",
    summary="List available agents",
    description="Returns all agent IDs currently registered in the router.",
)
async def list_agents() -> dict[str, list[str]]:
    return {"agents": agent_router.available_agents()}


@v1_router.post(
    "/chat",
    summary="Send a task to an agent",
    description=(
        "Routes the request to the specified agent and returns its response. "
        "Use GET /agents to discover valid agent IDs."
    ),
)
async def chat(request: AgentRequest) -> dict[str, Any]:
    try:
        result = await agent_router.dispatch(request.agent_id, request.payload)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Unhandled error in agent '%s'", request.agent_id)
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {exc}",
        )
