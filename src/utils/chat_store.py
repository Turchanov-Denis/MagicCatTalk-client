from pathlib import Path
import json


class ChatStore:
    def __init__(self, base_dir="chats"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def load(self, name: str):
        file = self.base_dir / f"{name}.json"

        if not file.exists():
            return []

        return json.loads(file.read_text(encoding="utf-8"))

    def save(self, name: str, messages):
        file = self.base_dir / f"{name}.json"

        file.write_text(
            json.dumps(messages, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )