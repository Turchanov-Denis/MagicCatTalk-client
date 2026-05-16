from pathlib import Path
import json
from datetime import datetime
from utils.config import load_config, save_config


class ChatStore:
    def __init__(self, base_dir="chats"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # LOAD CHAT FILE
    # -------------------------
    def load(self, name: str):
        file = self.base_dir / f"{name}.json"

        if not file.exists():
            return []

        try:
            return json.loads(file.read_text(encoding="utf-8"))
        except Exception:
            return []

    # -------------------------
    # SAVE CHAT FILE
    # -------------------------
    def save(self, name: str, messages):
        file = self.base_dir / f"{name}.json"
        file.write_text(
            json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # -------------------------
    # LIST FROM CONFIG (MAIN CHANGE)
    # -------------------------
    def list_chats(self):
        config = load_config()
        return config.get("chats", [])

    # -------------------------
    # REGISTER CHAT
    # -------------------------
    def register_chat(self, name: str):
        config = load_config()
        chats = config.get("chats", [])

        # already exists?
        if any(c["name"] == name for c in chats):
            return

        chats.append({"name": name, "created_at": datetime.utcnow().isoformat()})

        config["chats"] = chats
        save_config(config)
