from __future__ import annotations

import pytest

from app import debug_enabled


def test_flask_debug_defaults_off(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    assert debug_enabled() is False


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "on"])
def test_flask_debug_can_be_explicitly_enabled(
    monkeypatch: pytest.MonkeyPatch, value: str
):
    monkeypatch.setenv("FLASK_DEBUG", value)
    assert debug_enabled() is True


@pytest.mark.parametrize("value", ["0", "false", "debug", "anything"])
def test_flask_debug_rejects_unrecognized_values(
    monkeypatch: pytest.MonkeyPatch, value: str
):
    monkeypatch.setenv("FLASK_DEBUG", value)
    assert debug_enabled() is False
