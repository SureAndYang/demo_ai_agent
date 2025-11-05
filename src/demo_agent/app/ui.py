#!/usr/bin/env python3

from flask import Blueprint, Response


ui_bp = Blueprint("chat_ui", __name__)

PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>demo_agent Chat</title>
    <style>
      :root { color-scheme: light dark; font-family: system-ui, sans-serif; }
      body { margin: 0; padding: 0; display: flex; justify-content: center; background: #f4f4f8; }
      .chat-shell { width: min(720px, 100vw); margin: 40px; background: #ffffff; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.1); padding: 24px; }
      h1 { margin-top: 0; font-size: 1.5rem; }
      #log { height: 420px; overflow-y: auto; border: 1px solid #e0e0e6; border-radius: 8px; padding: 16px; background: #fafafb; }
      .bubble { margin-bottom: 16px; padding: 12px 14px; border-radius: 10px; max-width: 82%; white-space: pre-wrap; }
      .bubble:last-child { margin-bottom: 0; }
      .user { background: #2979ff; color: white; margin-left: auto; text-align: right; }
      .agent { background: #eceff1; color: #212121; margin-right: auto; }
      .error { background: #ffebee; color: #c62828; margin-right: auto; }
      form { display: flex; gap: 12px; margin-top: 24px; }
      input[type="text"] { flex: 1; border-radius: 8px; border: 1px solid #cfd8dc; padding: 12px; font-size: 1rem; }
      button { border: none; border-radius: 8px; padding: 12px 18px; background: #2979ff; color: white; font-weight: 600; cursor: pointer; }
      button:disabled { background: #90caf9; cursor: not-allowed; }
    </style>
  </head>
  <body>
    <main class="chat-shell">
      <h1>demo_agent Chat</h1>
      <section id="log" aria-live="polite"></section>
      <form id="chat-form" autocomplete="off">
        <input id="chat-input" type="text" name="message" placeholder="Ask me anything..." required>
        <button id="chat-submit" type="submit">Send</button>
      </form>
    </main>
    <script>
      const form = document.getElementById("chat-form");
      const input = document.getElementById("chat-input");
      const submit = document.getElementById("chat-submit");
      const log = document.getElementById("log");

      function appendBubble(role, text) {
        const bubble = document.createElement("div");
        bubble.className = "bubble " + role;
        bubble.textContent = text;
        log.appendChild(bubble);
        log.scrollTop = log.scrollHeight;
      }

      async function sendMessage(evt) {
        evt.preventDefault();
        const text = input.value.trim();
        if (!text) return;

        appendBubble("user", text);
        input.value = "";
        input.focus();
        submit.disabled = true;

        try {
          const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
          });

          if (!response.ok) {
            const errorBody = await response.json().catch(() => ({}));
            const message = errorBody.error || "Request failed.";
            throw new Error(message);
          }

          const payload = await response.json();
          appendBubble("agent", payload.response || "[no response]");
        } catch (err) {
          appendBubble("error", err.message);
        } finally {
          submit.disabled = false;
        }
      }

      form.addEventListener("submit", sendMessage);
    </script>
  </body>
</html>
"""


@ui_bp.route("/", methods=["GET"])
def home() -> Response:
    return Response(PAGE, mimetype="text/html")
