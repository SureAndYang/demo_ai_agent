#!/usr/bin/env python3

from typing import Any, Dict

import pytest

from demo_agent.app import create_app
from demo_agent.app import api as api_module


@pytest.fixture()
def client():
    app = create_app()
    app.testing = True
    with app.test_client() as test_client:
        yield test_client


def test_chat_requires_message_field(client):
    response = client.post("/api/chat", json={})
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Field 'message' is required."


def test_chat_returns_agent_payload(monkeypatch, client):
    fake_payload: Dict[str, Any] = {
        "response": "Hello from stub.",
        "analysis": ["analysis trace"],
        "tool_outputs": ["tool output"],
    }

    def fake_chat_once(_: str) -> Dict[str, Any]:
        return fake_payload

    monkeypatch.setattr(api_module, "_chat_once", fake_chat_once)

    response = client.post("/api/chat", json={"message": "hi"})
    assert response.status_code == 200
    assert response.get_json() == fake_payload


def test_ui_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.content_type
