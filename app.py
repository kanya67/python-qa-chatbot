"""Public web app for the Python Q&A chatbot."""

from collections import defaultdict, deque
import os
import threading
import time
from typing import Any

from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessageParam
from werkzeug.middleware.proxy_fix import ProxyFix

from chatbot_core import answer_question, ask_openai


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None
MAX_QUESTION_LENGTH = 1200
MAX_HISTORY_MESSAGES = 12


@app.get("/")
def index() -> str:
    return render_template("index.html", ai_enabled=client is not None)


@app.errorhandler(413)
def request_too_large(_error: Any) -> tuple[Any, int]:
    return jsonify(error="Request is too large."), 413


@app.errorhandler(429)
def too_many_requests(_error: Any) -> tuple[Any, int]:
    return jsonify(error="Too many questions too quickly. Please wait a minute and try again."), 429


@app.post("/api/chat")
@limiter.limit("15 per minute")
def chat() -> tuple[Any, int] | Any:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Send a JSON object with a question."), 400

    question = payload.get("question")
    if not isinstance(question, str) or not question.strip():
        return jsonify(error="Enter a question before sending."), 400
    question = question.strip()
    if len(question) > MAX_QUESTION_LENGTH:
        return jsonify(
            error=f"Questions must be {MAX_QUESTION_LENGTH} characters or fewer."
        ), 400

    raw_history = payload.get("history", [])
    if not isinstance(raw_history, list):
        return jsonify(error="Conversation history must be a list."), 400

    history: list[ChatCompletionMessageParam] = []
    for message in raw_history[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(message, dict):
            return jsonify(error="Conversation history contains an invalid message."), 400
        role = message.get("role")
        content = message.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            return jsonify(error="Conversation history contains an invalid message."), 400
        content = content.strip()
        if len(content) > MAX_QUESTION_LENGTH:
            return jsonify(error="A conversation message is too long."), 400
        if content:
            history.append({"role": role, "content": content})

    if question.lower() in {"help", "topics"}:
        return jsonify(
            answer=(
                "Try asking about Python basics, variables, data types, lists, "
                "tuples, dictionaries, sets, conditionals, loops, functions, "
                "classes, exceptions, modules, pip, virtual environments, or "
                "list comprehensions."
            ),
            source="knowledge_base",
        )

    if client is None:
        return jsonify(answer=answer_question(question), source="knowledge_base")

    try:
        answer = ask_openai(client, question, history)
    except (OpenAIError, RuntimeError):
        app.logger.exception("Could not generate an answer for a chat request.")
        return jsonify(
            error="The AI assistant is temporarily unavailable. Please try again."
        ), 502

    return jsonify(answer=answer, source="ai")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
