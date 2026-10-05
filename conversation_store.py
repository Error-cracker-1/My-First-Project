"""Persistent local storage for AI Chatbot conversations."""
from __future__ import annotations
import json, os, re, tempfile
from datetime import datetime, timezone
from pathlib import Path

FORMAT_VERSION=1
DEFAULT_STORAGE_DIR=Path(".chatbot_data")/"conversations"
_SAFE_NAME=re.compile(r"[^A-Za-z0-9._ -]+")

class ConversationStoreError(Exception):
    pass

class ConversationStore:
    def __init__(self, root=None):
        configured=root or os.getenv("CHATBOT_STORAGE_DIR")
        self.root=Path(configured).expanduser() if configured else DEFAULT_STORAGE_DIR
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sanitize_name(name):
        value=_SAFE_NAME.sub("_", name.strip())
        value=re.sub(r"\s+"," ",value).strip(" .")
        if not value: raise ConversationStoreError("Conversation name cannot be empty.")
        return value[:80]

    def _path_for(self,name): return self.root/f"{self.sanitize_name(name)}.json"

    @staticmethod
    def _validate_history(history):
        if not isinstance(history,list): raise ConversationStoreError("Saved conversation history is invalid.")
        result=[]
        for item in history:
            if not isinstance(item,(list,tuple)) or len(item)!=2: raise ConversationStoreError("Saved conversation contains an invalid message pair.")
            user,bot=item
            if not isinstance(user,str) or not isinstance(bot,str): raise ConversationStoreError("Saved conversation messages must be text.")
            result.append((user,bot))
        return result

    def save(self,name,model,history):
        if not isinstance(model,str) or not model.strip(): raise ConversationStoreError("A valid model ID is required.")
        history=self._validate_history(history)
        path=self._path_for(name)
        payload={"format_version":FORMAT_VERSION,"name":self.sanitize_name(name),"model":model,
                 "saved_at":datetime.now(timezone.utc).isoformat(),
                 "messages":[{"role":"user","content":u,"response":b} for u,b in history]}
        temp_path=None
        try:
            with tempfile.NamedTemporaryFile("w",encoding="utf-8",dir=self.root,prefix=".conversation-",suffix=".tmp",delete=False) as f:
                json.dump(payload,f,ensure_ascii=False,indent=2); f.write("\n"); temp_path=Path(f.name)
            os.replace(temp_path,path)
        except OSError as error:
            if temp_path: temp_path.unlink(missing_ok=True)
            raise ConversationStoreError(f"Could not save conversation: {error}") from error
        return path

    def load(self,name):
        path=self._path_for(name)
        if not path.exists(): raise ConversationStoreError(f"Saved conversation '{self.sanitize_name(name)}' was not found.")
        try:
            with path.open("r",encoding="utf-8") as f: payload=json.load(f)
        except (OSError,json.JSONDecodeError) as error:
            raise ConversationStoreError(f"Saved conversation '{path.stem}' is missing or corrupted.") from error
        if not isinstance(payload,dict) or payload.get("format_version")!=FORMAT_VERSION:
            raise ConversationStoreError("Saved conversation format is unsupported or corrupted.")
        model=payload.get("model")
        messages=payload.get("messages")
        if not isinstance(model,str) or not model.strip() or not isinstance(messages,list):
            raise ConversationStoreError("Saved conversation has invalid model or message data.")
        history=[]
        for message in messages:
            if not isinstance(message,dict) or message.get("role")!="user":
                raise ConversationStoreError("Saved conversation contains invalid message data.")
            u,b=message.get("content"),message.get("response")
            if not isinstance(u,str) or not isinstance(b,str):
                raise ConversationStoreError("Saved conversation messages must be text.")
            history.append((u,b))
        return {"name":payload.get("name",path.stem),"model":model,"saved_at":payload.get("saved_at",""),"history":history}

    def list_names(self):
        try: return sorted(p.stem for p in self.root.glob("*.json") if p.is_file())
        except OSError as error: raise ConversationStoreError(f"Could not list saved conversations: {error}") from error
