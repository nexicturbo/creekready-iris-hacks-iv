"""Small, environment-driven Gunicorn configuration for Linux deployments."""

from __future__ import annotations

import os


def positive_int(name: str, default: int) -> int:
    """Return a positive integer setting, falling back on invalid input."""

    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


bind = f"0.0.0.0:{positive_int('PORT', 8000)}"
# One threaded worker keeps the default in-memory rate limit consistent across
# the demo process. Multi-worker deployments should configure a shared limiter
# store with RATELIMIT_STORAGE_URI.
workers = positive_int("WEB_CONCURRENCY", 1)
threads = positive_int("GUNICORN_THREADS", 4)
worker_class = "gthread"
timeout = positive_int("GUNICORN_TIMEOUT", 60)
graceful_timeout = positive_int("GUNICORN_GRACEFUL_TIMEOUT", 30)
keepalive = positive_int("GUNICORN_KEEPALIVE", 5)

accesslog = "-"
errorlog = "-"
capture_output = True
