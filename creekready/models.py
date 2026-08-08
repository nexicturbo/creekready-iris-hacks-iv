from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    id: str
    title: str
    agency: str
    url: str
    excerpt: str


class AlertFacts(BaseModel):
    headline: str = Field(min_length=1, max_length=180)
    hazard: str = Field(min_length=1, max_length=80)
    location: str = Field(min_length=1, max_length=160)
    time_window: str = Field(min_length=1, max_length=160)
    official_instructions: list[str] = Field(default_factory=list, max_length=4)
    confidence: Literal["high", "medium", "low"]


class ActionItem(BaseModel):
    id: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9_.-]+$")
    action: str = Field(min_length=1, max_length=220)
    reason: str = Field(min_length=1, max_length=240)
    source_ids: list[str] = Field(min_length=1, max_length=3)


class PlanStage(BaseModel):
    key: Literal["now", "next", "worse"]
    title: str = Field(min_length=1, max_length=80)
    subtitle: str = Field(min_length=1, max_length=140)
    items: list[ActionItem] = Field(min_length=1, max_length=8)


class PrioritizedInstruction(BaseModel):
    """Exact alert wording selected by Featherless via a server-owned ID."""

    id: str = Field(
        min_length=1,
        max_length=80,
        pattern=r"^[a-z0-9_.-]+$",
    )
    # A request is already capped at 8,000 characters. Keeping that same bound
    # lets the server return the exact selected sentence without truncating or
    # rewriting user-provided alert wording.
    text: str = Field(min_length=1, max_length=8000)


class AITrace(BaseModel):
    """Auditable, prose-free evidence of the bounded model decision surface."""

    provider: Literal["featherless"] = "featherless"
    instruction_candidate_count: int = Field(ge=1, le=32)
    prioritized_instructions: list[PrioritizedInstruction] = Field(
        min_length=1,
        max_length=3,
    )
    action_candidate_count: int = Field(ge=3, le=9)
    model_ranked_action_count: int = Field(ge=1, le=5)
    required_action_count: int = Field(ge=3, le=8)
    rendered_action_count: int = Field(ge=3, le=9)


class ActionPlan(BaseModel):
    mode: Literal["featherless", "guided_fallback"]
    generated_at: str
    disclaimer: str
    facts: AlertFacts
    household_summary: str = Field(min_length=1, max_length=240)
    stages: list[PlanStage] = Field(min_length=3, max_length=3)
    sources: list[SourceReference] = Field(min_length=1, max_length=5)
    limitations: list[str] = Field(min_length=1, max_length=5)
    # Guided fallback never populates this field and therefore never presents a
    # deterministic plan as AI-prioritized.
    ai_trace: AITrace | None = None
