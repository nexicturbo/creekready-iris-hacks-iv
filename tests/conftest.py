from __future__ import annotations

import pytest

from creekready import create_app
from creekready.service import PlanningService


@pytest.fixture
def app_factory(monkeypatch: pytest.MonkeyPatch):
    """Create an app around an explicitly supplied, network-free service."""

    def make_app(service: PlanningService | None = None, **config):
        selected_service = service or PlanningService()
        monkeypatch.setattr(
            PlanningService,
            "from_environment",
            classmethod(lambda cls: selected_service),
        )
        return create_app({"TESTING": True, **config})

    return make_app


@pytest.fixture
def app(app_factory):
    return app_factory()


@pytest.fixture
def client(app):
    return app.test_client()
