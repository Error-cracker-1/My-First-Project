from flask import Flask, jsonify, render_template, request
from app import MODELS, MODEL_ALIASES, ask_ai, classify_error, create_chat, model_display_name
from config import ChatbotConfig
from conversation_store import ConversationStore, ConversationStoreError
import secrets

config = ChatbotConfig.from_env()
store = ConversationStore()
app = Flask(__name__)
_sessions = {}

def get_session():
    sid = request.cookies.get("chatbot_session") or secrets.token_urlsafe(24)
    if sid not in _sessions:
        _sessions[sid] = {"model": config.model, "chat": create_chat(config.model), "history": []}
    return sid, _sessions[sid]

def response(data, sid, status=200):
    out = jsonify(data)
    out.status_code = status
    if request.cookies.get("chatbot_session") != sid:
        out.set_cookie("chatbot_session", sid, httponly=True, samesite="Lax")
    return out

@app.get("/")
def index():
    return render_template("index.html", version="2.0")

@app.get("/api/status")
def status():
    try:
        sid, s = get_session()
        return response({"ok": True, "version": "2.0", "model": s["model"],
                         "model_name": model_display_name(s["model"]), "history": len(s["history"])}, sid)
    except Exception as e:
        return jsonify({"ok": False, "error": classify_error(e)}), 500

@app.get("/api/models")
def models():
    return jsonify({"models": [{"key": k, "name": n, "id": m} for k, (n, m) in MODELS.items()],
                    "aliases": MODEL_ALIASES})

@app.post("/api/chat")
def chat():
    sid, s = get_session()
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    if not isinstance(message, str) or not message.strip():
        return response({"ok": False, "error": "Message cannot be empty."}, sid, 400)
    if len(message) > 20000:
        return response({"ok": False, "error": "Message is limited to 20,000 characters."}, sid, 400)
    answer, error = ask_ai(message.strip(), s["chat"])
    if error:
        return response({"ok": False, "error": error}, sid, 502)
    s["history"].append((message.strip(), answer))
    return response({"ok": True, "message": answer, "history": s["history"]}, sid)

@app.post("/api/model")
def switch_model():
    sid, s = get_session()
    data = request.get_json(silent=True) or {}
    selected = str(data.get("model", "")).strip().lower()
    selected = MODELS[selected][1] if selected in MODELS else MODEL_ALIASES.get(selected, selected)
    supported = {m for _, m in MODELS.values()}
    if selected not in supported:
        return response({"ok": False, "error": "Unsupported Gemini model."}, sid, 400)
    try:
        s["chat"] = create_chat(selected)
        s["model"] = selected
        s["history"] = []
        return response({"ok": True, "model": selected, "model_name": model_display_name(selected), "history": []}, sid)
    except Exception as e:
        return response({"ok": False, "error": classify_error(e)}, sid, 502)

@app.get("/api/history")
def history():
    sid, s = get_session()
    return response({"ok": True, "history": s["history"]}, sid)

@app.post("/api/clear")
def clear():
    sid, s = get_session()
    try:
        s["chat"] = create_chat(s["model"])
        s["history"] = []
        return response({"ok": True, "history": []}, sid)
    except Exception as e:
        return response({"ok": False, "error": classify_error(e)}, sid, 502)

@app.get("/api/saves")
def saves():
    sid, _ = get_session()
    try:
        return response({"ok": True, "saves": store.list_names()}, sid)
    except ConversationStoreError as e:
        return response({"ok": False, "error": str(e)}, sid, 500)

@app.post("/api/save")
def save():
    sid, s = get_session()
    name = (request.get_json(silent=True) or {}).get("name", "")
    if not isinstance(name, str) or not name.strip():
        return response({"ok": False, "error": "A conversation name is required."}, sid, 400)
    if not s["history"]:
        return response({"ok": False, "error": "There is no conversation to save yet."}, sid, 400)
    try:
        return response({"ok": True, "name": store.save(name, s["model"], s["history"]).stem}, sid)
    except ConversationStoreError as e:
        return response({"ok": False, "error": str(e)}, sid, 400)

@app.post("/api/load")
def load():
    sid, s = get_session()
    name = (request.get_json(silent=True) or {}).get("name", "")
    try:
        saved = store.load(name)
        supported = {m for _, m in MODELS.values()}
        if saved["model"] not in supported:
            raise ConversationStoreError("The saved conversation uses an unsupported model.")
        s["chat"] = create_chat(saved["model"], saved["history"])
        s["model"], s["history"] = saved["model"], saved["history"]
        return response({"ok": True, "name": saved["name"], "model": saved["model"],
                         "model_name": model_display_name(saved["model"]), "history": saved["history"]}, sid)
    except ConversationStoreError as e:
        return response({"ok": False, "error": str(e)}, sid, 400)
    except Exception as e:
        return response({"ok": False, "error": classify_error(e)}, sid, 502)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
