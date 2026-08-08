from __future__ import annotations

import json

import pytest

from creekready.catalog import STAGE_ORDER
from creekready.provider import ProviderPayload, StageSelection
from creekready.service import PlanningService


FLOOD_ALERT = (
    "FLASH FLOOD WARNING for Cedar Creek, Texas until 8:00 PM. "
    "Avoid flooded roads and follow instructions from local emergency officials."
)


class SuccessfulProvider:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def create_payload(self, **kwargs) -> ProviderPayload:
        self.calls.append(kwargs)
        catalog = kwargs["catalog"]
        return ProviderPayload(
            stages=[
                StageSelection(
                    key="now",
                    action_ids=[item.id for item in catalog if item.stage == "now"],
                ),
                StageSelection(
                    key="next",
                    action_ids=[item.id for item in catalog if item.stage == "next"],
                ),
                StageSelection(
                    key="worse",
                    action_ids=[item.id for item in catalog if item.stage == "worse"],
                ),
            ],
        )


class FailingProvider:
    def __init__(self) -> None:
        self.calls = 0

    def create_payload(self, **_kwargs):
        self.calls += 1
        raise RuntimeError("simulated provider outage")


class InvalidSelectionProvider:
    def __init__(self, kind: str):
        self.kind = kind

    def create_payload(self, **kwargs):
        catalog = kwargs["catalog"]
        ids_by_stage = {
            stage: [item.id for item in catalog if item.stage == stage]
            for stage in STAGE_ORDER
        }
        if self.kind == "unknown":
            ids_by_stage["now"].append("attacker.unapproved_action")
        elif self.kind == "duplicate":
            ids_by_stage["now"].append(ids_by_stage["now"][0])
        elif self.kind == "wrong_stage":
            ids_by_stage["now"].append(ids_by_stage["next"][0])
        return ProviderPayload(
            stages=[
                StageSelection(
                    key=stage,
                    action_ids=ids_by_stage[stage],
                )
                for stage in STAGE_ORDER
            ]
        )


def _assert_security_headers(response) -> None:
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["Content-Security-Policy"] == (
        "default-src 'self'; style-src 'self'; script-src 'self'; "
        "img-src 'self' data:; connect-src 'self'"
    )
    assert response.headers["Permissions-Policy"] == (
        "camera=(), geolocation=(), microphone=()"
    )


def test_health_reports_guided_fallback_without_provider(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "provider": "guided_fallback",
        "model": None,
    }
    assert response.headers["Cache-Control"] == "no-store"


def test_frontend_assets_are_served_with_explicit_featherless_disclosure(client):
    page = client.get("/")
    script = client.get("/static/app.js")
    styles = client.get("/static/styles.css")
    favicon = client.get("/static/favicon.svg")

    assert page.status_code == 200
    assert script.status_code == 200
    assert styles.status_code == 200
    assert favicon.status_code == 200
    assert b"Sends this alert to Featherless" in page.data
    assert "Envía este aviso a Featherless".encode() in script.data
    assert b"Featherless AI assist configured" in script.data
    assert b"Featherless planner available" not in script.data


def test_plan_rate_limit_is_json_and_stops_provider_calls(app_factory):
    provider = SuccessfulProvider()
    app = app_factory(
        PlanningService(provider),
        RATELIMIT_ENABLED=True,
        PLAN_RATE_LIMIT="2 per minute",
    )
    limited_client = app.test_client()

    responses = [
        limited_client.post("/api/plan", json={"alert_text": FLOOD_ALERT})
        for _ in range(3)
    ]

    assert [response.status_code for response in responses] == [200, 200, 429]
    assert responses[-1].get_json() == {
        "error": "Too many plan requests. Wait a minute and try again."
    }
    assert len(provider.calls) == 2


def test_health_reports_configured_provider_and_model(app_factory, monkeypatch):
    provider = SuccessfulProvider()
    monkeypatch.setenv("FEATHERLESS_MODEL", "test/model")
    app = app_factory(PlanningService(provider))

    response = app.test_client().get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "provider": "featherless",
        "model": "test/model",
    }
    assert provider.calls == []


@pytest.mark.parametrize(
    ("body", "content_type"),
    [
        (None, None),
        ("not json", "text/plain"),
        ("{", "application/json"),
        (json.dumps(["not", "an", "object"]), "application/json"),
    ],
)
def test_plan_rejects_missing_or_non_object_json(client, body, content_type):
    response = client.post("/api/plan", data=body, content_type=content_type)

    assert response.status_code == 400
    assert response.get_json() == {"error": "Send a JSON request body."}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"alert_text": "too short"},
        {
            "alert_text": "Official emergency warning remains active across county",
        },
        {"alert_text": FLOOD_ALERT, "language": "fr"},
        {"alert_text": FLOOD_ALERT, "household_needs": ["spaceship"]},
        {"alert_text": FLOOD_ALERT, "household_needs": ["pet"] * 6},
        {"alert_text": "x" * 8001},
    ],
)
def test_plan_rejects_invalid_fields_with_422(client, payload):
    response = client.post("/api/plan", json=payload)

    assert response.status_code == 422
    assert isinstance(response.get_json()["error"], str)
    assert response.get_json()["error"]


def test_plan_rejects_twelve_word_alert_at_validation_boundary(client):
    response = client.post(
        "/api/plan",
        json={
            "alert_text": "one two three four five six seven eight nine ten eleven twelve",
        },
    )

    assert response.status_code == 422
    assert "more of the official alert" in response.get_json()["error"]


def test_plan_accepts_thirteen_word_alert_at_validation_boundary(client):
    response = client.post(
        "/api/plan",
        json={
            "alert_text": (
                "official alert one two three four five six seven eight nine ten eleven"
            ),
        },
    )

    assert response.status_code == 200
    assert response.get_json()["mode"] == "guided_fallback"


def test_duplicate_household_needs_are_deduplicated(client):
    response = client.post(
        "/api/plan",
        json={
            "alert_text": FLOOD_ALERT,
            "household_needs": ["pet", "pet", "older_adult", "pet"],
            "language": "en",
        },
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["household_summary"] == "Plan adjusted for: pet, older adult."
    next_actions = [
        item["action"]
        for item in result["stages"][1]["items"]
        if item["id"].startswith("household.next.")
    ]
    assert len(next_actions) == 2
    assert sum("pet" in action.lower() for action in next_actions) == 1


def test_configured_provider_success_is_returned_without_network(app_factory):
    provider = SuccessfulProvider()
    app = app_factory(PlanningService(provider))

    response = app.test_client().post(
        "/api/plan",
        json={
            "alert_text": FLOOD_ALERT,
            "household_needs": ["pet"],
            "language": "en",
        },
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["mode"] == "featherless"
    assert result["facts"]["location"] == "Cedar Creek, Texas"
    assert result["household_summary"] == "Plan adjusted for: pet."
    assert "only ranked pre-approved" in result["limitations"][0]
    assert [stage["key"] for stage in result["stages"]] == list(STAGE_ORDER)
    assert "household.next.pet" in {
        item["id"] for stage in result["stages"] for item in stage["items"]
    }
    assert len(provider.calls) == 1
    call = provider.calls[0]
    assert call["alert_text"] == FLOOD_ALERT
    assert call["needs"] == ["pet"]
    assert call["language"] == "en"
    assert {source.id for source in call["sources"]} == {
        "ALERT-TEXT",
        "NWS-FLOOD",
        "READY-PLAN",
    }
    assert {item.id for item in call["catalog"]} >= {
        "flood.now.avoid_water",
        "household.next.pet",
    }


def test_use_ai_false_skips_configured_provider_and_stays_local(app_factory):
    provider = SuccessfulProvider()
    app = app_factory(PlanningService(provider))

    response = app.test_client().post(
        "/api/plan",
        json={"alert_text": FLOOD_ALERT, "language": "en", "use_ai": False},
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["mode"] == "guided_fallback"
    assert "turned off for this request" in result["limitations"][0]
    assert provider.calls == []


def test_configured_provider_failure_uses_bounded_fallback(app_factory):
    provider = FailingProvider()
    app = app_factory(PlanningService(provider))

    response = app.test_client().post(
        "/api/plan",
        json={"alert_text": FLOOD_ALERT, "language": "en"},
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["mode"] == "guided_fallback"
    assert result["facts"]["hazard"] == "Flood or flash flood"
    assert "could not be validated" in result["limitations"][0]
    assert provider.calls == 1


@pytest.mark.parametrize("kind", ["unknown", "duplicate", "wrong_stage"])
def test_invalid_provider_ids_fail_closed_to_bounded_fallback(app_factory, kind):
    app = app_factory(PlanningService(InvalidSelectionProvider(kind)))

    response = app.test_client().post(
        "/api/plan", json={"alert_text": FLOOD_ALERT, "language": "en"}
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["mode"] == "guided_fallback"
    assert "attacker.unapproved_action" not in json.dumps(result)
    assert "could not be validated" in result["limitations"][0]


def test_ai_mode_preserves_all_five_household_needs(app_factory):
    provider = SuccessfulProvider()
    app = app_factory(PlanningService(provider))
    needs = ["children", "older_adult", "pet", "limited_mobility", "no_vehicle"]

    response = app.test_client().post(
        "/api/plan",
        json={
            "alert_text": FLOOD_ALERT,
            "household_needs": needs,
            "language": "en",
        },
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["mode"] == "featherless"
    returned_ids = {
        item["id"] for stage in result["stages"] for item in stage["items"]
    }
    assert {f"household.next.{need}" for need in needs} <= returned_ids


@pytest.mark.parametrize(
    ("method", "path", "kwargs", "expected_status"),
    [
        ("get", "/api/health", {}, 200),
        ("post", "/api/plan", {"json": {}}, 422),
        ("post", "/api/plan", {"data": "not json"}, 400),
    ],
)
def test_security_headers_are_set_on_success_and_validation_errors(
    client, method, path, kwargs, expected_status
):
    response = getattr(client, method)(path, **kwargs)

    assert response.status_code == expected_status
    _assert_security_headers(response)


def test_oversized_request_returns_json_413_with_security_headers(app_factory):
    app = app_factory(MAX_CONTENT_LENGTH=256)
    response = app.test_client().post(
        "/api/plan",
        json={"alert_text": "flood warning " * 100},
    )

    assert response.status_code == 413
    assert response.is_json
    assert "too large" in response.get_json()["error"].lower()
    _assert_security_headers(response)
