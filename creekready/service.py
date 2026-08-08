from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .catalog import (
    build_action_catalog,
    build_ranked_stages,
    expand_instruction_ids,
)
from .fallback import (
    build_fallback_stages,
    build_instruction_candidates,
    detect_hazard,
    extract_facts,
)
from .models import AITrace, ActionPlan
from .provider import FeatherlessPlanner
from .sources import sources_for


ALLOWED_NEEDS = {"children", "older_adult", "pet", "limited_mobility", "no_vehicle"}
DEFAULT_FEATHERLESS_MODEL = "Qwen/Qwen3-8B"
logger = logging.getLogger(__name__)


class PlanRequest(BaseModel):
    alert_text: str = Field(min_length=40, max_length=8000)
    household_needs: list[str] = Field(default_factory=list, max_length=5)
    language: Literal["en", "es"] = "en"
    use_ai: bool = True

    @field_validator("alert_text")
    @classmethod
    def normalize_alert(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized.split()) < 13:
            raise ValueError("Paste more of the official alert so the plan has enough context.")
        return normalized

    @field_validator("household_needs")
    @classmethod
    def validate_needs(cls, value: list[str]) -> list[str]:
        unique = list(dict.fromkeys(value))
        if not set(unique).issubset(ALLOWED_NEEDS):
            raise ValueError("One or more household needs are not supported.")
        return unique


class PlanningService:
    def __init__(self, provider: FeatherlessPlanner | None = None):
        self.provider = provider

    @classmethod
    def from_environment(cls) -> "PlanningService":
        api_key = os.getenv("FEATHERLESS_API_KEY", "").strip()
        if not api_key:
            return cls()
        model = os.getenv("FEATHERLESS_MODEL", "").strip() or DEFAULT_FEATHERLESS_MODEL
        return cls(FeatherlessPlanner(api_key=api_key, model=model))

    @property
    def provider_configured(self) -> bool:
        return self.provider is not None

    @property
    def provider_model(self) -> str | None:
        if self.provider is None:
            return None
        configured = getattr(self.provider, "model", None)
        if isinstance(configured, str) and configured.strip():
            return configured.strip()
        return os.getenv("FEATHERLESS_MODEL", "").strip() or DEFAULT_FEATHERLESS_MODEL

    def create_plan(self, request: PlanRequest) -> ActionPlan:
        hazard_key = detect_hazard(request.alert_text)
        sources = sources_for(hazard_key)
        catalog = build_action_catalog(
            hazard_key, request.household_needs, request.language
        )
        instruction_candidates = build_instruction_candidates(request.alert_text)
        bounded_facts = extract_facts(request.alert_text, hazard_key, request.language)
        generated_at = datetime.now(timezone.utc).isoformat()
        disclaimer = (
            "CreekReady summarizes the alert you provide. It does not predict emergencies, observe live conditions, or replace instructions from officials."
            if request.language == "en"
            else "CreekReady resume el aviso que usted proporciona. No predice emergencias, no observa condiciones en vivo ni reemplaza las instrucciones oficiales."
        )

        household_summary = self._household_summary(
            request.household_needs, request.language
        )

        if request.use_ai and self.provider:
            try:
                payload = self.provider.create_payload(
                    needs=request.household_needs,
                    language=request.language,
                    sources=sources,
                    catalog=catalog,
                    instruction_candidates=instruction_candidates,
                )
                ranked_stages = build_ranked_stages(
                    payload.ranked_action_ids,
                    catalog,
                    request.language,
                )
                prioritized_instructions = expand_instruction_ids(
                    payload.prioritized_instruction_ids,
                    instruction_candidates,
                )
                return ActionPlan(
                    mode="featherless",
                    generated_at=generated_at,
                    disclaimer=disclaimer,
                    # Keep the fact panel on the conservative local extractor even
                    # when AI creates the household plan. The model cannot introduce
                    # a place, time, or official instruction into this trusted panel.
                    facts=bounded_facts,
                    household_summary=household_summary,
                    stages=ranked_stages,
                    sources=sources,
                    limitations=self._ai_limitations(request.language),
                    ai_trace=AITrace(
                        instruction_candidate_count=len(instruction_candidates),
                        prioritized_instructions=prioritized_instructions,
                        action_candidate_count=len(catalog),
                        model_ranked_action_count=len(payload.ranked_action_ids),
                        required_action_count=sum(
                            action.required for action in catalog
                        ),
                        rendered_action_count=sum(
                            len(stage.items) for stage in ranked_stages
                        ),
                    ),
                )
            except Exception as exc:
                logger.warning(
                    "Featherless generation failed; using guided fallback (%s)",
                    type(exc).__name__,
                )
                provider_note = (
                    "The live AI request could not be validated, so CreekReady switched to its bounded official-guidance fallback."
                    if request.language == "en"
                    else "La respuesta de IA no pudo validarse; CreekReady cambió a su modo de respaldo basado en orientación oficial."
                )
        elif not request.use_ai:
            provider_note = (
                "Featherless was turned off for this request; the alert was processed by this CreekReady server and was not forwarded to Featherless."
                if request.language == "en"
                else "Featherless se desactivó para esta solicitud; este servidor de CreekReady procesó el aviso sin reenviarlo a Featherless."
            )
        else:
            provider_note = (
                "Live Featherless mode is not configured; this result uses CreekReady's deterministic official-guidance fallback."
                if request.language == "en"
                else "El modo Featherless no está configurado; este resultado usa el respaldo determinista basado en orientación oficial."
            )

        return ActionPlan(
            mode="guided_fallback",
            generated_at=generated_at,
            disclaimer=disclaimer,
            facts=bounded_facts,
            household_summary=household_summary,
            stages=build_fallback_stages(hazard_key, request.household_needs, request.language),
            sources=sources,
            limitations=[
                provider_note,
                (
                    "Verify the original alert for exact locations, timing, and changes."
                    if request.language == "en"
                    else "Verifique el aviso original para ubicaciones, horarios y cambios exactos."
                ),
            ],
            ai_trace=None,
        )

    @staticmethod
    def _household_summary(needs: list[str], language: str) -> str:
        if language == "es":
            need_labels = {
                "children": "niños",
                "older_adult": "adulto mayor",
                "pet": "mascotas",
                "limited_mobility": "movilidad limitada",
                "no_vehicle": "sin vehículo",
            }
            needs_label = ", ".join(need_labels[need] for need in needs)
            return (
                f"Plan ajustado para: {needs_label}."
                if needs_label
                else "No se seleccionaron necesidades adicionales."
            )
        needs_label = ", ".join(needs).replace("_", " ")
        return (
            f"Plan adjusted for: {needs_label}."
            if needs_label
            else "No additional household needs selected."
        )

    @staticmethod
    def _ai_limitations(language: str) -> list[str]:
        if language == "es":
            return [
                "Featherless priorizó identificadores de instrucciones textuales del aviso y ordenó acciones preaprobadas; no redactó ese contenido.",
                "CreekReady no usa datos en vivo del clima, carreteras o evacuaciones. Verifique el aviso original para conocer cambios.",
            ]
        return [
            "Featherless prioritized exact alert-instruction IDs and ranked pre-approved actions; it authored none of that content.",
            "CreekReady does not use live weather, road, or evacuation data. Verify the original alert for changes.",
        ]
