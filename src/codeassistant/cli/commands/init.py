from pathlib import Path

import yaml

from prompt_toolkit import PromptSession

from rich.panel import Panel

from utils.console import console

session = PromptSession()


LOR_DIR = Path.cwd() / ".lor"

CONFIG_PATH = LOR_DIR / "config.yaml"


DEFAULT_CONFIG = {

    "assistant_name": "Lorariel",

    "character_ASCII": (
        "*\n"
        " \\\n"
        " \\-\\           ___________\n"
        " \\---\\_/\\\\.    /          _)\n"
        "(((|||/-|))  /        __)\n"
        "_/   ^   (()) \\\\       )\n"
        "('_'    \"  --   \\\\     )\n"
        "\n"
        "  |     (())__/  /\\\\__.--.\n"
        "  (      --         )\\\\\\\\|\n"
        "   |     (||)  _____ |\\\\\\\\\\\\)\n"
        "  _|      ||  /      \\\\ |||))\n"
        "___(/_\\_  .__ _/        | (())\n"
        "/_{{______)/  /_{{__/\\\\_____| (\\\\__"
    ),

    "theme": {

        "primary": "medium_purple",

        "text": "white",

        "muted": "gray",

        "border": "white",

        "success": "green",

        "warning": "yellow",

        "error": "red",
    },

    "backend_url":
        "http://localhost:8000",

    "model_id":
        "Qwen/Qwen2.5-Coder-3B-Instruct",

    "lora":
        None,

    "active_chat":
        "default",

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
    }
}


def ask(label: str, default: str):

    value = session.prompt(f"{label} " f"[{default}]: ").strip()

    if not value:

        return default

    return value


def init():

    # -------------------------
    # EXISTS
    # -------------------------

    if LOR_DIR.exists():

        console.print("[yellow]" ".lor already exists" "[/yellow]")

        return

    # -------------------------
    # CREATE DIRS
    # -------------------------

    (LOR_DIR / "chats").mkdir(parents=True, exist_ok=True)

    (LOR_DIR / "cache").mkdir()

    (LOR_DIR / "sessions").mkdir()

    # -------------------------
    # COPY DEFAULTS
    # -------------------------

    config = DEFAULT_CONFIG.copy()

    # -------------------------
    # INPUTS
    # -------------------------

    config["assistant_name"] = ask("Assistant name", config["assistant_name"])

    config["backend_url"] = ask("Backend URL", config["backend_url"])

    config["model_id"] = ask("Model", config["model_id"])

    # -------------------------
    # SAVE
    # -------------------------

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:

        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)

    # -------------------------
    # UI
    # -------------------------

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
