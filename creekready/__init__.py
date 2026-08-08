from __future__ import annotations

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import ValidationError

from .service import PlanRequest, PlanningService


def create_app(test_config: dict | None = None) -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.from_mapping(
        MAX_CONTENT_LENGTH=32 * 1024,
        JSON_SORT_KEYS=False,
        TESTING=False,
        PLAN_RATE_LIMIT=os.getenv("PLAN_RATE_LIMIT", "12 per minute"),
        RATELIMIT_ENABLED=True,
        RATELIMIT_HEADERS_ENABLED=True,
        RATELIMIT_STORAGE_URI=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
    )
    if test_config:
        app.config.update(test_config)
    if app.config["TESTING"] and not (test_config or {}).get("RATELIMIT_ENABLED"):
        app.config["RATELIMIT_ENABLED"] = False
    app.json.ensure_ascii = False

    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=[],
        storage_uri=app.config["RATELIMIT_STORAGE_URI"],
        headers_enabled=app.config["RATELIMIT_HEADERS_ENABLED"],
        enabled=app.config["RATELIMIT_ENABLED"],
    )
    # Flask-Limiter's route wrapper holds a weak reference in v4; the app must
    # retain the extension for the full lifetime of an application-factory app.
    app.extensions["creekready_limiter"] = limiter

    service = PlanningService.from_environment()
    app.extensions["planning_service"] = service

    @app.after_request
    def set_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'",
        )
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), geolocation=(), microphone=()"
        )
        if request.path.startswith("/api/"):
            response.headers.setdefault("Cache-Control", "no-store")
        return response

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "provider": "featherless" if service.provider_configured else "guided_fallback",
                "model": os.getenv("FEATHERLESS_MODEL", "Qwen/Qwen3-8B")
                if service.provider_configured
                else None,
            }
        )

    @app.post("/api/plan")
    @limiter.limit(app.config["PLAN_RATE_LIMIT"])
    def make_plan():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Send a JSON request body."}), 400

        try:
            plan_request = PlanRequest.model_validate(payload)
            result = service.create_plan(plan_request)
        except ValidationError as exc:
            first = exc.errors(include_url=False)[0]
            return jsonify({"error": first.get("msg", "Check the submitted alert.")}), 422

        return jsonify(result.model_dump(mode="json"))

    @app.errorhandler(413)
    def too_large(_error):
        return jsonify({"error": "That alert is too large. Keep it under 8,000 characters."}), 413

    @app.errorhandler(429)
    def rate_limited(_error):
        return jsonify(
            {"error": "Too many plan requests. Wait a minute and try again."}
        ), 429

    return app
