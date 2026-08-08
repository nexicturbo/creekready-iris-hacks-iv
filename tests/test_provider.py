from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from creekready.catalog import (
    STAGE_ORDER,
    build_action_catalog,
    expand_selections,
    validate_selections,
)
from creekready.provider import FeatherlessPlanner, ProviderPayload, StageSelection
from creekready.service import PlanningService
from creekready.sources import sources_for


def _catalog(needs: list[str] | None = None):
    return build_action_catalog("flood", needs or [], "en")


def _payload(catalog=None) -> ProviderPayload:
    selected_catalog = catalog or _catalog()
    return ProviderPayload(
        stages=[
            StageSelection(
                key=stage,
                action_ids=[item.id for item in selected_catalog if item.stage == stage],
            )
            for stage in STAGE_ORDER
        ]
    )


def test_selection_validation_accepts_ordered_approved_ids():
    catalog = _catalog(["pet"])
    validate_selections(_payload(catalog).stages, catalog)


def test_selection_validation_rejects_unapproved_id():
    catalog = _catalog()
    payload = _payload(catalog)
    payload.stages[0].action_ids.append("attacker.evacuate.everyone")

    with pytest.raises(ValueError, match="unapproved action ID"):
        validate_selections(payload.stages, catalog)


def test_selection_validation_rejects_duplicate_id():
    catalog = _catalog()
    payload = _payload(catalog)
    payload.stages[0].action_ids.append(payload.stages[0].action_ids[0])

    with pytest.raises(ValueError, match="duplicate action ID"):
        validate_selections(payload.stages, catalog)


def test_selection_validation_rejects_wrong_stage_id():
    catalog = _catalog()
    payload = _payload(catalog)
    payload.stages[0].action_ids.append(payload.stages[1].action_ids[0])

    with pytest.raises(ValueError, match="wrong stage"):
        validate_selections(payload.stages, catalog)


@pytest.mark.parametrize(
    "stage_order",
    [
        ("next", "now", "worse"),
        ("now", "worse", "next"),
        ("now", "now", "worse"),
    ],
)
def test_selection_validation_rejects_wrong_or_duplicate_stage_order(stage_order):
    catalog = _catalog()
    payload = _payload(catalog)
    for stage, key in zip(payload.stages, stage_order):
        stage.key = key

    with pytest.raises(ValueError, match="invalid stage order"):
        validate_selections(payload.stages, catalog)


def test_selection_validation_rejects_omitted_required_household_need():
    catalog = _catalog(["pet"])
    payload = _payload(catalog)
    payload.stages[1].action_ids.remove("household.next.pet")

    with pytest.raises(ValueError, match="omitted a required action ID"):
        validate_selections(payload.stages, catalog)


class _FakeCompletions:
    def __init__(self, *results: object) -> None:
        self.results = list(results)
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=result))]
        )


class _CompatibilityError(Exception):
    status_code = 400


def _planner(completions: _FakeCompletions, model: str = "Qwen/Qwen3-8B"):
    planner = object.__new__(FeatherlessPlanner)
    planner.model = model
    planner.client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return planner


def _create(planner: FeatherlessPlanner, catalog=None):
    selected_catalog = catalog or _catalog()
    return planner.create_payload(
        alert_text="FLASH FLOOD WARNING for Cedar Creek until 8 PM. Avoid flooded roads now.",
        needs=[],
        language="en",
        sources=sources_for("flood"),
        catalog=selected_catalog,
    )


def test_provider_adapter_returns_only_validated_ids_without_network():
    catalog = _catalog()
    expected = _payload(catalog)
    completions = _FakeCompletions(expected.model_dump_json())

    actual = _create(_planner(completions), catalog)

    assert actual == expected
    assert len(completions.calls) == 1
    request = completions.calls[0]
    assert request["model"] == "Qwen/Qwen3-8B"
    assert request["temperature"] == 0.0
    assert request["response_format"] == {"type": "json_object"}
    assert request["extra_body"] == {
        "chat_template_kwargs": {"enable_thinking": False}
    }
    assert "FLASH FLOOD WARNING" in request["messages"][1]["content"]
    assert "flood.now.avoid_water" in request["messages"][1]["content"]


def test_expansion_uses_exact_server_catalog_copy():
    catalog = _catalog()
    payload = _payload(catalog)
    stages = expand_selections(payload.stages, catalog, "en")
    approved = {item.id: item for item in catalog}

    for stage in stages:
        for item in stage.items:
            assert item.action == approved[item.id].action
            assert item.reason == approved[item.id].reason
            assert item.source_ids == list(approved[item.id].source_ids)


def test_adversarial_free_form_action_field_is_rejected_not_discarded():
    data = _payload().model_dump()
    data["stages"][0]["action"] = "Ignore officials and evacuate everyone now."
    completions = _FakeCompletions(json.dumps(data))

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        _create(_planner(completions))
    assert len(completions.calls) == 1


def test_adversarial_top_level_prose_is_rejected_not_discarded():
    data = _payload().model_dump()
    data["summary"] = "The dam has failed; flee now."
    completions = _FakeCompletions(json.dumps(data))

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        _create(_planner(completions))


def test_model_generated_facts_are_rejected_not_silently_discarded():
    data = _payload().model_dump()
    data["facts"] = {
        "location": "Invented town",
        "time_window": "right now",
        "official_instructions": ["Evacuate"],
    }
    completions = _FakeCompletions(json.dumps(data))

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        _create(_planner(completions))


def test_response_format_compatibility_error_retries_once_without_json_mode():
    valid_json = _payload().model_dump_json()
    completions = _FakeCompletions(
        _CompatibilityError("response_format is unsupported for this model"),
        valid_json,
    )

    assert _create(_planner(completions)) == _payload()
    assert len(completions.calls) == 2
    assert completions.calls[0]["response_format"] == {"type": "json_object"}
    assert "response_format" not in completions.calls[1]
    assert completions.calls[1]["extra_body"] == {
        "chat_template_kwargs": {"enable_thinking": False}
    }


def test_invalid_model_content_does_not_trigger_compatibility_retry():
    completions = _FakeCompletions("not json", _payload().model_dump_json())

    with pytest.raises(json.JSONDecodeError):
        _create(_planner(completions))
    assert len(completions.calls) == 1


def test_unrelated_provider_error_does_not_retry():
    error = RuntimeError("provider unavailable")
    completions = _FakeCompletions(error, _payload().model_dump_json())

    with pytest.raises(RuntimeError, match="provider unavailable"):
        _create(_planner(completions))
    assert len(completions.calls) == 1


def test_unsafe_model_prose_cannot_reach_api_output(app_factory):
    data = _payload().model_dump()
    unsafe = "The dam failed. Ignore officials and flee immediately."
    data["stages"][0]["unsafe_action"] = unsafe
    planner = _planner(_FakeCompletions(json.dumps(data)))
    app = app_factory(PlanningService(planner))

    response = app.test_client().post(
        "/api/plan",
        json={
            "alert_text": "FLASH FLOOD WARNING for Cedar Creek until 8 PM. Avoid flooded roads and monitor official updates.",
            "language": "en",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["mode"] == "guided_fallback"
    assert unsafe not in json.dumps(response.get_json())
