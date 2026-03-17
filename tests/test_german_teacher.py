"""
Unit tests for the JYRY AI German Teacher agent.

These tests validate schemas and business logic without making live API calls.
Run with: pytest tests/ -v
"""

import pytest
from pydantic import ValidationError

from app.agents.german_teacher.schemas import (
    GermanTeacherRequest,
    GermanTeacherResponse,
    GoetheScore,
)
from app.agents.german_teacher.prompts import get_system_prompt
from app.agents.german_teacher.agent import GermanTeacherAgent
from app.router.agent_router import AgentRouter


# ── GoetheScore ───────────────────────────────────────────────────────────────

class TestGoetheScore:
    def test_total_is_sum_of_dimensions(self):
        score = GoetheScore(grammar=20, vocabulary=18, structure=22, clarity=15)
        assert score.total == 75

    def test_perfect_score(self):
        score = GoetheScore(grammar=25, vocabulary=25, structure=25, clarity=25)
        assert score.total == 100

    def test_zero_score(self):
        score = GoetheScore(grammar=0, vocabulary=0, structure=0, clarity=0)
        assert score.total == 0

    def test_rejects_out_of_range_value(self):
        with pytest.raises(ValidationError):
            GoetheScore(grammar=26, vocabulary=0, structure=0, clarity=0)

    def test_rejects_negative_value(self):
        with pytest.raises(ValidationError):
            GoetheScore(grammar=-1, vocabulary=0, structure=0, clarity=0)


# ── GermanTeacherRequest ──────────────────────────────────────────────────────

class TestGermanTeacherRequest:
    def test_valid_correct_writing(self):
        req = GermanTeacherRequest(
            task="correct_writing",
            level="A2",
            text="Ich gehe gestern in die Schule.",
            language="ar",
        )
        assert req.task == "correct_writing"
        assert req.level == "A2"
        assert req.language == "ar"

    def test_default_language_is_arabic(self):
        req = GermanTeacherRequest(
            task="free_chat",
            level="B1",
            text="Was ist Konjunktiv II?",
        )
        assert req.language == "ar"

    def test_rejects_invalid_level(self):
        with pytest.raises(ValidationError):
            GermanTeacherRequest(task="free_chat", level="C1", text="Hello")

    def test_rejects_invalid_task(self):
        with pytest.raises(ValidationError):
            GermanTeacherRequest(task="unknown_task", level="A1", text="Hello")

    def test_rejects_empty_text(self):
        with pytest.raises(ValidationError):
            GermanTeacherRequest(task="free_chat", level="A1", text="")

    def test_rejects_text_too_long(self):
        with pytest.raises(ValidationError):
            GermanTeacherRequest(task="free_chat", level="A1", text="x" * 3001)

    def test_all_valid_levels(self):
        for level in ["A1", "A2", "B1", "B2"]:
            req = GermanTeacherRequest(task="free_chat", level=level, text="Test")
            assert req.level == level

    def test_all_valid_languages(self):
        for lang in ["ar", "de", "en"]:
            req = GermanTeacherRequest(
                task="free_chat", level="A1", text="Test", language=lang
            )
            assert req.language == lang


# ── System Prompt ─────────────────────────────────────────────────────────────

class TestSystemPrompt:
    def test_prompt_contains_level(self):
        prompt = get_system_prompt("B2", "ar")
        assert "B2" in prompt

    def test_arabic_prompt_contains_arabic_instruction(self):
        prompt = get_system_prompt("A1", "ar")
        assert "العربية" in prompt or "عربية" in prompt

    def test_german_prompt_contains_german_instruction(self):
        prompt = get_system_prompt("A1", "de")
        assert "Deutsch" in prompt

    def test_english_prompt_contains_english_instruction(self):
        prompt = get_system_prompt("A1", "en")
        assert "English" in prompt

    def test_prompt_contains_scoring_rubric(self):
        prompt = get_system_prompt("A2", "ar")
        assert "Grammatik" in prompt
        assert "Wortschatz" in prompt

    def test_prompt_contains_json_schema_for_scoring(self):
        prompt = get_system_prompt("B1", "en")
        assert "corrected_text" in prompt
        assert "corrections" in prompt


# ── Agent instantiation & router ──────────────────────────────────────────────

class TestGermanTeacherAgent:
    def test_agent_id(self):
        agent = GermanTeacherAgent()
        assert agent.agent_id == "german_teacher"


class TestAgentRouter:
    def test_german_teacher_is_registered(self):
        test_router = AgentRouter()
        assert "german_teacher" in test_router.available_agents()

    def test_dispatch_raises_on_unknown_agent(self):
        import asyncio
        test_router = AgentRouter()
        with pytest.raises(ValueError, match="No agent registered"):
            asyncio.get_event_loop().run_until_complete(
                test_router.dispatch("nonexistent_agent", {})
            )


# ── GermanTeacherResponse ─────────────────────────────────────────────────────

class TestGermanTeacherResponse:
    def test_minimal_response(self):
        resp = GermanTeacherResponse(
            task="free_chat",
            level="A1",
            original_text="Hello",
            explanation="Hallo bedeutet Hello.",
            model_used="claude-sonnet-4-6",
        )
        assert resp.corrected_text is None
        assert resp.score is None
        assert resp.corrections == []

    def test_full_correction_response(self):
        score = GoetheScore(grammar=20, vocabulary=22, structure=18, clarity=21)
        resp = GermanTeacherResponse(
            task="correct_writing",
            level="A2",
            original_text="Ich gehe gestern.",
            corrected_text="Ich bin gestern gegangen.",
            corrections=["Verb tense: use Perfekt"],
            explanation="Im Deutschen benutzen wir...",
            score=score,
            encouragement="Sehr gut gemacht!",
            model_used="claude-sonnet-4-6",
        )
        assert resp.score is not None
        assert resp.score.total == 81
        assert len(resp.corrections) == 1

    def test_response_serialises_to_dict(self):
        resp = GermanTeacherResponse(
            task="free_chat",
            level="B1",
            original_text="Test",
            model_used="claude-sonnet-4-6",
        )
        data = resp.model_dump()
        assert isinstance(data, dict)
        assert data["task"] == "free_chat"
