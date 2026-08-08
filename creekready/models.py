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


class ActionPlan(BaseModel):
    mode: Literal["featherless", "guided_fallback"]
    generated_at: str
    disclaimer: str
    facts: AlertFacts
    household_summary: str = Field(min_length=1, max_length=240)
    stages: list[PlanStage] = Field(min_length=3, max_length=3)
    sources: list[SourceReference] = Field(min_length=1, max_length=5)
    limitations: list[str] = Field(min_length=1, max_length=5)
