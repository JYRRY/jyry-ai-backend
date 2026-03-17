import json
import logging
from typing import Any

from app.agents.base_agent import BaseAgent
from app.agents.german_teacher.prompts import get_system_prompt
from app.agents.german_teacher.schemas import (
    GermanTeacherRequest,
    GermanTeacherResponse,
    GoetheScore,
)

logger = logging.getLogger(__name__)


class GermanTeacherAgent(BaseAgent):
    """
    JYRY AI German Teacher — the first agent in the JYRY platform.

    Supports three task types:
    - correct_writing : Correct text and return a Goethe-style score (JSON output)
    - explain_grammar : Explain a grammar topic at the student's level
    - free_chat       : Open-ended teaching conversation
    """

    @property
    def agent_id(self) -> str:
        return "german_teacher"

    async def process(self, payload: dict[str, Any]) -> dict[str, Any]:
        req = GermanTeacherRequest(**payload)
        client = self.get_client()

        system_prompt = get_system_prompt(req.level, req.language)
        user_message = self._build_user_message(req)

        logger.info(
            "GermanTeacherAgent | task=%s level=%s lang=%s",
            req.task, req.level, req.language,
        )

        response = await client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        raw_text: str = response.content[0].text
        model_used: str = response.model

        if req.task == "correct_writing":
            return self._parse_scored_response(req, raw_text, model_used)

        # explain_grammar and free_chat — plain text response
        return GermanTeacherResponse(
            task=req.task,
            level=req.level,
            original_text=req.text,
            explanation=raw_text,
            model_used=model_used,
        ).model_dump()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_user_message(self, req: GermanTeacherRequest) -> str:
        prefixes: dict[str, str] = {
            "correct_writing": (
                f"Bitte korrigiere meinen deutschen Text (Niveau {req.level}):\n\n"
            ),
            "explain_grammar": (
                f"Bitte erkläre diesen deutschen Grammatikpunkt für Niveau {req.level}:\n\n"
            ),
            "free_chat": f"[Schüler, Niveau {req.level}] ",
        }
        return prefixes[req.task] + req.text

    def _parse_scored_response(
        self,
        req: GermanTeacherRequest,
        raw: str,
        model_used: str,
    ) -> dict[str, Any]:
        """
        Parse Claude's JSON response for correct_writing tasks.

        Claude sometimes wraps JSON in markdown fences (```json ... ```) —
        we strip those before parsing. If JSON is genuinely malformed, we
        return a graceful fallback with the raw text instead of crashing.
        """
        try:
            cleaned = (
                raw.strip()
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
            data = json.loads(cleaned)

            score = GoetheScore(**data["score"])

            return GermanTeacherResponse(
                task=req.task,
                level=req.level,
                original_text=req.text,
                corrected_text=data.get("corrected_text"),
                corrections=data.get("corrections", []),
                explanation=data.get("explanation", ""),
                score=score,
                encouragement=data.get("encouragement", ""),
                model_used=model_used,
            ).model_dump()

        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.warning(
                "GermanTeacherAgent | Failed to parse JSON response: %s", exc
            )
            # Graceful fallback — the student still gets a response
            return GermanTeacherResponse(
                task=req.task,
                level=req.level,
                original_text=req.text,
                explanation=raw,
                encouragement="",
                model_used=model_used,
            ).model_dump()
