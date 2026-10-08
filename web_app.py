from flask import Flask, jsonify, render_template, request
from app import (
    MODELS,
    MODEL_ALIASES,
    ask_ai,
    classify_error,
    model_display_name,
    safe_create_chat,
)
from config import ChatbotConfig
from conversation_store import ConversationStore, ConversationStoreError
import secrets


config = ChatbotConfig.from_env()
store = ConversationStore()
app = Flask(__name__)

# Browser sessions are kept in memory while the server is running.
# Each browser session has an independent set of model sessions.
_sessions = {}


def _new_session():
    chat = safe_create_chat(config.model)
    if chat is None:
        raise RuntimeError("Unable to start the configured Gemini model.")
    return {
        "model": config.model,
        "chat": chat,
        "history": [],
        "models": {
            config.model: {
                "chat": chat,
                "history": [],
            }
        },
    }


def get_session():
    sid = request.cookies.get("chatbot_session") or secrets.token_urlsafe(24)
    if sid not in _sessions:
        _sessions[sid] = _new_session()
    return sid, _sessions[sid]


def response(data, sid, status=200):
    out = jsonify(data)
    out.status_code = status
    if request.cookies.get("chatbot_session") != sid:
        out.set_cookie("chatbot_session", sid, httponly=True, samesite="Lax")
    return out


def _sync_active_session(session):
    active = session["models"][session["model"]]
    session["chat"] = active["chat"]
    session["history"] = active["history"]


@app.get("/")
def index():
    return render_template("index.html", version="2.0")


@app.get("/api/status")
def status():
    try:
        sid, session = get_session()
        return response(
            {
                "ok": True,
                "version": "2.0",
                "model": session["model"],
                "model_name": model_display_name(session["model"]),
                "history": len(session["history"]),
                "sessions": len(session["models"]),
            },
            sid,
        )
    except Exception as error:
        return jsonify({"ok": False, "error": classify_error(error)}), 500


@app.get("/api/models")
def models():
    return jsonify(
        {
            "models": [
                {"key": key, "name": name, "id": model_id}
                for key, (name, model_id) in MODELS.items()
            ],
            "aliases": MODEL_ALIASES,
        }
    )


@app.post("/api/chat")
def chat():
    try:
        sid, session = get_session()
    except Exception as error:
        return jsonify({"ok": False, "error": classify_error(error)}), 502

    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str) or not message.strip():
        return response({"ok": False, "error": "Message cannot be empty."}, sid, 400)
    if len(message) > 20000:
        return response(
            {"ok": False, "error": "Message is limited to 20,000 characters."},
            sid,
            400,
        )

    answer, error = ask_ai(message.strip(), session["chat"])
    if error:
        return response({"ok": False, "error": error}, sid, 502)

    session["history"].append((message.strip(), answer))
    return response(
        {"ok": True, "message": answer, "history": session["history"]},
        sid,
    )


@app.post("/api/model")
def switch_model():
    try:
        sid, session = get_session()
    except Exception as error:
        return jsonify({"ok": False, "error": classify_error(error)}), 502

    data = request.get_json(silent=True) or {}
    selected = str(data.get("model", "")).strip().lower()
    selected = MODELS[selected][1] if selected in MODELS else MODEL_ALIASES.get(selected, selected)

    supported = {model_id for _, model_id in MODELS.values()}
    if selected not in supported:
        return response({"ok": False, "error": "Unsupported Gemini model."}, sid, 400)

    if selected == session["model"]:
        return response(
            {
                "ok": True,
                "model": selected,
                "model_name": model_display_name(selected),
                "history": session["history"],
            },
            sid,
        )

    try:
        if selected not in session["models"]:
            new_chat = safe_create_chat(selected)
            if new_chat is None:
                return response(
                    {"ok": False, "error": "Could not start the selected Gemini model."},
                    sid,
                    502,
                )
            session["models"][selected] = {"chat": new_chat, "history": []}

        session["model"] = selected
        _sync_active_session(session)

        return response(
            {
                "ok": True,
                "model": selected,
                "model_name": model_display_name(selected),
                "history": session["history"],
            },
            sid,
        )
    except Exception as error:
        return response({"ok": False, "error": classify_error(error)}, sid, 502)


@app.get("/api/history")
def history():
    try:
        sid, session = get_session()
        return response({"ok": True, "history": session["history"]}, sid)
    except Exception as error:
        return jsonify({"ok": False, "error": classify_error(error)}), 502


@app.post("/api/clear")
def clear():
    try:
        sid, session = get_session()
        new_chat = safe_create_chat(session["model"])
        if new_chat is None:
            return response(
                {"ok": False, "error": "Could not start a new Gemini conversation."},
                sid,
                502,
            )
        session["models"][session["model"]] = {"chat": new_chat, "history": []}
        _sync_active_session(session)
        return response({"ok": True, "history": []}, sid)
    except Exception as error:
        return jsonify({"ok": False, "error": classify_error(error)}), 502


@app.get("/api/saves")
def saves():
    try:
        sid, _ = get_session()
        return response({"ok": True, "saves": store.list_names()}, sid)
    except ConversationStoreError as error:
        return response({"ok": False, "error": str(error)}, sid, 500)
    except Exception as error:
        return jsonify({"ok": False, "error": classify_error(error)}), 502


@app.post("/api/save")
def save():
    try:
        sid, session = get_session()
    except Exception as error:
        return jsonify({"ok": False, "error": classify_error(error)}), 502

    data = request.get_json(silent=True) or {}
    name = data.get("name", "")

    if not isinstance(name, str) or not name.strip():
        return response({"ok": False, "error": "A conversation name is required."}, sid, 400)
    if not session["history"]:
        return response(
            {"ok": False, "error": "There is no conversation to save yet."},
            sid,
            400,
        )

    try:
        saved_path = store.save(name, session["model"], session["history"])
        return response({"ok": True, "name": saved_path.stem}, sid)
    except ConversationStoreError as error:
        return response({"ok": False, "error": str(error)}, sid, 400)


@app.post("/api/load")
def load():
    try:
        sid, session = get_session()
    except Exception as error:
        return jsonify({"ok": False, "error": classify_error(error)}), 502

    data = request.get_json(silent=True) or {}
    name = data.get("name", "")

    if not isinstance(name, str) or not name.strip():
        return response({"ok": False, "error": "A conversation name is required."}, sid, 400)

    try:
        saved = store.load(name)
        supported = {model_id for _, model_id in MODELS.values()}
        if saved["model"] not in supported:
            raise ConversationStoreError("The saved conversation uses an unsupported model.")

        new_chat = safe_create_chat(saved["model"], saved["history"])
        if new_chat is None:
            return response(
                {"ok": False, "error": "Could not restore the Gemini conversation."},
                sid,
                502,
            )

        session["models"][saved["model"]] = {
            "chat": new_chat,
            "history": saved["history"],
        }
        session["model"] = saved["model"]
        _sync_active_session(session)

        return response(
            {
                "ok": True,
                "name": saved["name"],
                "model": saved["model"],
                "model_name": model_display_name(saved["model"]),
                "history": saved["history"],
            },
            sid,
        )
    except ConversationStoreError as error:
        return response({"ok": False, "error": str(error)}, sid, 400)
    except Exception as error:
        return response({"ok": False, "error": classify_error(error)}, sid, 502)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
