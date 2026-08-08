import os

from creekready import create_app


app = create_app()


def debug_enabled() -> bool:
    """Flask debug mode is opt-in; it is off for every unrecognized value."""

    return os.getenv("FLASK_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=debug_enabled())
