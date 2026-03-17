import logging

from fastapi import FastAPI

from app.api.v1.endpoints import v1_router
from app.config import settings

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="JYRY AI Backend",
    version="0.1.0",
    description=(
        "Multi-agent AI teaching platform by JYRY GROUP. "
        "Currently powered by the German Teacher agent (A1–B2)."
    ),
)

app.include_router(v1_router, prefix="/api/v1")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "env": settings.app_env,
        "model": settings.claude_model,
    }
