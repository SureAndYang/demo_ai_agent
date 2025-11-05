#!/usr/bin/env python3

from http import HTTPStatus
from flask import Blueprint, jsonify, request
from demo_agent.agent.policy import Message
from demo_agent.agent.runtime import Runner
from demo_agent.utils import logger


runner = Runner()
api_bp = Blueprint("chat_api", __name__)


def _chat_once(user_text: str) -> dict:
    conversation = [Message(role="user", content=user_text)]
    prompt = runner.prompt.generator(conversation, runner.memory, runner.tools)
    responses = runner.advisor(prompt, print_response=False)
    conversation.extend(responses)
    history_name = runner.memory.policy.history
    runner.memory.insert(history_name, conversation, one_message=True)
    final_text = next(
        (msg.content for msg in reversed(responses) if msg.channel == "final"),
        "",
    )
    analysis = [msg.content for msg in responses if msg.channel == "analysis"]
    tool_outputs = [msg.content for msg in responses if msg.channel == "commentary"]
    return {
        "response": final_text.strip(),
        "analysis": analysis,
        "tool_outputs": tool_outputs,
    }


@api_bp.route("/chat", methods=["POST"])
def chat() -> tuple:
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON payload."}), HTTPStatus.BAD_REQUEST

    user_text = (payload.get("message") or "").strip()
    if not user_text:
        return jsonify({"error": "Field 'message' is required."}), HTTPStatus.BAD_REQUEST

    try:
        data = _chat_once(user_text)
    except Exception as exc:  # pragma: no cover
        logger.exception("Chat request failed: %s", exc)
        return jsonify({"error": "Agent failed to respond."}), HTTPStatus.INTERNAL_SERVER_ERROR

    return jsonify(data), HTTPStatus.OK
