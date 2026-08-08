from __future__ import annotations

import json

import pytest
from flask import request

from creekready.catalog import STAGE_ORDER, action_rank_target
from creekready.provider import ProviderPayload
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
        instruction_candidates = kwargs["instruction_candidates"]
        return ProviderPayload(
            prioritized_instruction_ids=[
                candidate.id
                for candidate in instruction_candidates[
                    : min(3, len(instruction_candidates))
                ]
            ],
            ranked_action_ids=[
                item.id for item in catalog[: action_rank_target(catalog)]
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
        instruction_candidates = kwargs["instruction_candidates"]
        ranked_action_ids = [
            item.id for item in catalog[: action_rank_target(catalog)]
        ]
        if self.kind == "unknown":
            ranked_action_ids[-1] = "attacker.unapproved_action"
        elif self.kind == "duplicate":
            ranked_action_ids[-1] = ranked_action_ids[0]
        elif self.kind == "short":
            ranked_action_ids.pop()
        prioritized_instruction_ids = [instruction_candidates[0].id]
        if self.kind == "instruction_unknown":
            prioritized_instruction_ids = ["alert.instruction.99.deadbeefdead"]
        elif self.kind == "instruction_duplicate":
            prioritized_instruction_ids = [
                instruction_candidates[0].id,
                instruction_candidates[0].id,
            ]
        elif self.kind == "instruction_excess":
            prioritized_instruction_ids = [
                instruction_candidates[0].id,
                instruction_candidates[0].id,
                instruction_candidates[0].id,
                instruction_candidates[0].id,
            ]
        return ProviderPayload(
            prioritized_instruction_ids=prioritized_instruction_ids,
            ranked_action_ids=ranked_action_ids,
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
    assert b"Sends extracted alert instructions" in page.data
    assert "Envía a Featherless las instrucciones extraídas".encode() in script.data
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


def test_forwarded_for_is_ignored_by_default(app_factory):
    app = app_factory()
    observed_addresses: list[str | None] = []

    @app.before_request
    def capture_address():
        observed_addresses.append(request.remote_addr)

    response = app.test_client().get(
        "/api/health",
        headers={"X-Forwarded-For": "203.0.113.10"},
        environ_overrides={"REMOTE_ADDR": "192.0.2.44"},
    )

    assert response.status_code == 200
    assert app.config["TRUSTED_PROXY_HOPS"] == 0
    assert observed_addresses == ["192.0.2.44"]


def test_only_forwarded_for_uses_the_configured_hop_count(app_factory):
    app = app_factory(TRUSTED_PROXY_HOPS="2")
    observed_request: dict[str, str | None] = {}

    @app.before_request
    def capture_request_metadata():
        observed_request.update(
            address=request.remote_addr,
            scheme=request.scheme,
            host=request.host,
            script_root=request.script_root,
        )

    response = app.test_client().get(
        "/api/health",
        headers={
            "X-Forwarded-For": "203.0.113.10, 198.51.100.20",
            "X-Forwarded-Proto": "https",
            "X-Forwarded-Host": "spoofed.example",
            "X-Forwarded-Port": "8443",
            "X-Forwarded-Prefix": "/spoofed",
        },
        environ_overrides={"REMOTE_ADDR": "192.0.2.44"},
    )

    assert response.status_code == 200
    assert app.config["TRUSTED_PROXY_HOPS"] == 2
    assert observed_request == {
        "address": "203.0.113.10",
        "scheme": "http",
        "host": "localhost",
        "script_root": "",
    }


@pytest.mark.parametrize(
    "value",
    ["", "not-a-number", "-1", "1.5", "11", None, True],
)
def test_invalid_trusted_proxy_hops_fail_startup(app_factory, value):
    with pytest.raises(ValueError, match="TRUSTED_PROXY_HOPS"):
        app_factory(TRUSTED_PROXY_HOPS=value)


def test_rate_limit_cannot_be_evaded_with_forwarded_for_by_default(app_factory):
    provider = SuccessfulProvider()
    app = app_factory(
        PlanningService(provider),
        RATELIMIT_ENABLED=True,
        PLAN_RATE_LIMIT="1 per minute",
    )
    limited_client = app.test_client()

    responses = [
        limited_client.post(
            "/api/plan",
            json={"alert_text": FLOOD_ALERT},
            headers={"X-Forwarded-For": forwarded_address},
            environ_overrides={"REMOTE_ADDR": "192.0.2.44"},
        )
        for forwarded_address in ("203.0.113.10", "198.51.100.20")
    ]

    assert [response.status_code for response in responses] == [200, 429]
    assert len(provider.calls) == 1


def test_rate_limit_buckets_use_trusted_forwarded_client_address(app_factory):
    provider = SuccessfulProvider()
    app = app_factory(
        PlanningService(provider),
        RATELIMIT_ENABLED=True,
        PLAN_RATE_LIMIT="1 per minute",
        TRUSTED_PROXY_HOPS=1,
    )
    limited_client = app.test_client()

    def submit(forwarded_address: str):
        return limited_client.post(
            "/api/plan",
            json={"alert_text": FLOOD_ALERT},
            headers={"X-Forwarded-For": forwarded_address},
            environ_overrides={"REMOTE_ADDR": "192.0.2.44"},
        )

    responses = [
        submit("203.0.113.10"),
        submit("198.51.100.20"),
        submit("203.0.113.10"),
    ]

    assert [response.status_code for response in responses] == [200, 200, 429]
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


def test_blank_model_environment_uses_and_reports_default(app_factory, monkeypatch):
    monkeypatch.setenv("FEATHERLESS_API_KEY", "test-key")
    monkeypatch.setenv("FEATHERLESS_MODEL", "   ")

    service = PlanningService.from_environment()
    app = app_factory(service)
    response = app.test_client().get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "provider": "featherless",
        "model": "Qwen/Qwen3-8B",
    }


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
    assert result["ai_trace"]["provider"] == "featherless"
    assert result["ai_trace"]["instruction_candidate_count"] >= 1
    assert result["ai_trace"]["action_candidate_count"] == 5
    assert result["ai_trace"]["model_ranked_action_count"] == 5
    assert result["ai_trace"]["required_action_count"] == 4
    assert result["ai_trace"]["rendered_action_count"] == sum(
        len(stage["items"]) for stage in result["stages"]
    )
    assert all(
        instruction["text"] in FLOOD_ALERT
        for instruction in result["ai_trace"]["prioritized_instructions"]
    )
    assert result["facts"]["location"] == "Cedar Creek, Texas"
    assert result["household_summary"] == "Plan adjusted for: pet."
    assert "prioritized exact alert-instruction IDs" in result["limitations"][0]
    assert [stage["key"] for stage in result["stages"]] == list(STAGE_ORDER)
    assert "household.next.pet" in {
        item["id"] for stage in result["stages"] for item in stage["items"]
    }
    assert len(provider.calls) == 1
    call = provider.calls[0]
    assert "alert_text" not in call
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
    assert call["instruction_candidates"]
    assert all(candidate.text in FLOOD_ALERT for candidate in call["instruction_candidates"])


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
    assert result["ai_trace"] is None
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
    assert result["ai_trace"] is None
    assert result["facts"]["hazard"] == "Flood or flash flood"
    assert "could not be validated" in result["limitations"][0]
    assert provider.calls == 1


@pytest.mark.parametrize("kind", ["unknown", "duplicate", "short"])
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


@pytest.mark.parametrize(
    "kind",
    ["instruction_unknown", "instruction_duplicate", "instruction_excess"],
)
def test_invalid_provider_instruction_ids_fail_closed(app_factory, kind):
    app = app_factory(PlanningService(InvalidSelectionProvider(kind)))

    response = app.test_client().post(
        "/api/plan", json={"alert_text": FLOOD_ALERT, "language": "en"}
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["mode"] == "guided_fallback"
    assert result["ai_trace"] is None
    assert "deadbeefdead" not in json.dumps(result)
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


def test_same_alert_with_different_needs_changes_only_vetted_action_surface(
    app_factory,
):
    provider = SuccessfulProvider()
    app = app_factory(PlanningService(provider))
    plan_without_need = app.test_client().post(
        "/api/plan",
        json={"alert_text": FLOOD_ALERT, "language": "en"},
    ).get_json()
    plan_with_pet = app.test_client().post(
        "/api/plan",
        json={
            "alert_text": FLOOD_ALERT,
            "household_needs": ["pet"],
            "language": "en",
        },
    ).get_json()

    assert (
        plan_without_need["ai_trace"]["prioritized_instructions"]
        == plan_with_pet["ai_trace"]["prioritized_instructions"]
    )
    assert (
        plan_with_pet["ai_trace"]["model_ranked_action_count"]
        == plan_without_need["ai_trace"]["model_ranked_action_count"] + 1
    )
    assert (
        plan_with_pet["ai_trace"]["action_candidate_count"]
        == plan_without_need["ai_trace"]["action_candidate_count"] + 1
    )
    assert "household.next.pet" in {
        item["id"]
        for stage in plan_with_pet["stages"]
        for item in stage["items"]
    }


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
