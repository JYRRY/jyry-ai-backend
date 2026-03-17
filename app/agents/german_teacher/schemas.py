from typing import Literal

from pydantic import BaseModel, Field, computed_field

# ── Type aliases ──────────────────────────────────────────────────────────────

CefrLevel = Literal["A1", "A2", "B1", "B2"]
TaskType = Literal["correct_writing", "explain_grammar", "free_chat"]
ExplanationLanguage = Literal["ar", "de", "en"]


# ── Request ───────────────────────────────────────────────────────────────────

class GermanTeacherRequest(BaseModel):
    """Incoming request to the German Teacher agent."""

    task: TaskType = Field(
        ...,
        description=(
            "correct_writing: Correct and score the student's text. "
            "explain_grammar: Explain a grammar point. "
            "free_chat: Open-ended question or conversation."
        ),
    )
    level: CefrLevel = Field(..., description="Student's CEFR level.")
    text: str = Field(
        ...,
        min_length=1,
        max_length=3000,
        description="The student's text, question, or topic.",
    )
    language: ExplanationLanguage = Field(
        default="ar",
        description="Language for explanations: ar=Arabic, de=German, en=English.",
    )


# ── Score ─────────────────────────────────────────────────────────────────────

class GoetheScore(BaseModel):
    """
    Goethe-Institut style scoring rubric.
    Each dimension is 0–25, total is 0–100 (computed, never stored).
    """

    grammar: int = Field(..., ge=0, le=25, description="Grammatik (0–25)")
    vocabulary: int = Field(..., ge=0, le=25, description="Wortschatz (0–25)")
    structure: int = Field(..., ge=0, le=25, description="Struktur (0–25)")
    clarity: int = Field(..., ge=0, le=25, description="Verständlichkeit (0–25)")

    @computed_field
    @property
    def total(self) -> int:
        return self.grammar + self.vocabulary + self.structure + self.clarity


# ── Response ──────────────────────────────────────────────────────────────────

class GermanTeacherResponse(BaseModel):
    """Full response returned by the German Teacher agent."""

    task: TaskType
    level: CefrLevel
    original_text: str

    # Only populated for correct_writing tasks
    corrected_text: str | None = None
    corrections: list[str] = []
    score: GoetheScore | None = None

    # Always populated
    explanation: str = ""
    encouragement: str = ""
    model_used: str = ""
