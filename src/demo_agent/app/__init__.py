#!/usr/bin/env python3

from flask import Flask
from demo_agent.app.api import api_bp
from demo_agent.app.ui import ui_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(ui_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=8000, debug=True)
