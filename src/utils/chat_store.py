from pathlib import Path

import json

from utils.memory import should_summarize, split_for_summary, build_summary_prompt


class ChatStore:

    def __init__(self):

        self.base_dir = Path.cwd() / ".magic" / "chats"

        self.base_dir.mkdir(parents=True, exist_ok=True)

    def path(self, name: str):

        return self.base_dir / f"{name}.json"

    def load(self, name: str):

        file = self.path(name)

        if not file.exists():

            return {"summary": "", "messages": []}

        try:

            return json.loads(file.read_text(encoding="utf-8"))

        except Exception:

            return {"summary": "", "messages": []}

    def save(self, name: str, data):

        file = self.path(name)

        file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def append(self, name: str, role: str, content: str):

        data = self.load(name)

        data["messages"].append({"role": role, "content": content})

        self.save(name, data)

    def list_chats(self):

        return [x.stem for x in self.base_dir.glob("*.json")]

    def summarize_if_needed(self, name: str, engine):

        data = self.load(name)

        messages = data["messages"]

        if not should_summarize(messages):
            return

        old, recent = split_for_summary(messages)

        prompt = build_summary_prompt(old)

        summary = engine.generate(prompt=prompt, max_new_tokens=256, temperature=0.1)

        previous = data.get("summary", "")

        combined = (previous + "\n\n" + summary).strip()

        data["summary"] = combined

        data["messages"] = recent

        self.save(name, data)
