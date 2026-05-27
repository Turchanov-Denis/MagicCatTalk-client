from pathlib import Path

import yaml

from prompt_toolkit import PromptSession

from rich.panel import Panel

from utils.console import console

session = PromptSession()


LOR_DIR = Path.cwd() / ".magic"

CONFIG_PATH = LOR_DIR / "config.yaml"


DEFAULT_CONFIG = {
    "assistant_name": "MagicCat",
    "character_ASCII": "   /\\_/\\\n  ( o.o )\n===/ * \\===\n  (_\\_/_)\n",
    "theme": {
        "primary": "medium_purple",
        "text": "white",
        "muted": "gray",
        "border": "white",
        "success": "green",
        "warning": "yellow",
        "error": "red",
    },
    "backend_url": "http://localhost:8000",
    "model_id": "Qwen/Qwen2.5-Coder-3B-Instruct",
    "lora": None,
    "active_chat": "default",
    "memory": {
        # сколько максимум токенов
        # отправляется модели
        "max_context_tokens": 4096,
        # когда история превышает:
        # max_context_tokens +
        # summary_trigger_tokens
        # запускается summarize
        "summary_trigger_tokens": 2048,
        # максимальный размер summary
        "summary_max_tokens": 256,
    },
}


def ask(label: str, default: str):

    value = session.prompt(f"{label} " f"[{default}]: ").strip()

    if not value:

        return default

    return value


def init():

    if LOR_DIR.exists():

        console.print("[yellow]" ".magic already exists" "[/yellow]")

        return


    (LOR_DIR / "chats").mkdir(parents=True, exist_ok=True)

    config = DEFAULT_CONFIG.copy()

    config["assistant_name"] = ask("Assistant name", config["assistant_name"])

    config["backend_url"] = ask("Backend URL", config["backend_url"])

    config["model_id"] = ask("Model", config["model_id"])

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:

        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)

    console.print()

    console.print(
        Panel.fit(
            (
                "[bold green]"
                "Project initialized"
                "[/bold green]\n\n"
                f"Path: {LOR_DIR}"
            ),
            border_style="green",
        )
    )

    console.print()
