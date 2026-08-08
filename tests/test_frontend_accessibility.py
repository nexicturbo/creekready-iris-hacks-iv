from __future__ import annotations

import re
from html.parser import HTMLParser


class _MarkupAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        self.elements.append((tag, {key: value or "" for key, value in attrs}))


def _parse(page: bytes) -> _MarkupAudit:
    audit = _MarkupAudit()
    audit.feed(page.decode("utf-8"))
    return audit


def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    light, dark = sorted(
        (_relative_luminance(first), _relative_luminance(second)), reverse=True
    )
    return (light + 0.05) / (dark + 0.05)


def _css_color(css: str, variable: str) -> str:
    match = re.search(rf"--{re.escape(variable)}:\s*(#[0-9a-fA-F]{{6}})", css)
    assert match, f"missing --{variable} color"
    return match.group(1)


def test_frontend_id_references_and_skip_target_are_valid(client):
    audit = _parse(client.get("/").data)
    ids = [attrs["id"] for _, attrs in audit.elements if attrs.get("id")]

    assert len(ids) == len(set(ids)), "HTML IDs must be unique"
    id_set = set(ids)
    assert any(
        tag == "a" and attrs.get("class") == "skip-link" and attrs.get("href") == "#planner"
        for tag, attrs in audit.elements
    )
    assert "planner" in id_set

    for _, attrs in audit.elements:
        for attribute in ("aria-describedby", "aria-labelledby", "aria-errormessage"):
            for referenced_id in attrs.get(attribute, "").split():
                assert referenced_id in id_set, f"{attribute} references missing #{referenced_id}"


def test_frontend_exposes_keyboard_and_live_region_semantics(client):
    audit = _parse(client.get("/").data)
    by_id = {
        attrs["id"]: (tag, attrs)
        for tag, attrs in audit.elements
        if attrs.get("id")
    }

    assert by_id["top"][1]["tabindex"] == "-1"
    assert by_id["planner"][1]["tabindex"] == "-1"
    assert by_id["system-pill"][1]["aria-atomic"] == "true"
    assert by_id["loading-panel"][1]["aria-atomic"] == "true"
    assert by_id["tool-status"][1]["aria-atomic"] == "true"
    assert by_id["read-plan"][1]["aria-pressed"] == "false"
    assert by_id["alert-text"][1]["aria-errormessage"] == "error-message"


def test_frontend_contrast_and_accessibility_modes(client):
    css = client.get("/static/styles.css").get_data(as_text=True)
    paper = _css_color(css, "paper")
    muted = _css_color(css, "muted")
    coral = _css_color(css, "coral")
    coral_deep = _css_color(css, "coral-deep")
    control_line = _css_color(css, "control-line")

    assert _contrast(muted, paper) >= 4.5
    assert _contrast(coral_deep, paper) >= 4.5
    assert _contrast("#ffffff", coral) >= 4.5
    assert _contrast(control_line, paper) >= 3
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert "@media (prefers-contrast: more)" in css
    assert "@media (forced-colors: active)" in css
    assert ".results[hidden] { display: none !important; }" in css


def test_frontend_has_bounded_requests_and_defensive_plan_rendering(client):
    script = client.get("/static/app.js").get_data(as_text=True)

    assert "const HEALTH_TIMEOUT_MS" in script
    assert "const PLAN_TIMEOUT_MS" in script
    assert script.count("new AbortController()") >= 2
    assert "function isValidPlan(plan)" in script
    assert "if (!isValidPlan(data))" in script
    # ALERT-TEXT is a valid source without an external URL. Runtime validation
    # must accept its empty string while safeHttpUrl suppresses the link.
    assert 'typeof source.url === "string"' in script
    assert "isNonemptyText(source.url" not in script
    assert "prefersReducedMotion()" in script
    assert "card.tabIndex = -1" in script
