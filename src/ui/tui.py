from pathlib import Path

from rich.panel import Panel

from utils.config import load_config
from utils.console import console

from codeassistant.cli.commands.setup import setup
from codeassistant.cli.commands.info import info
from codeassistant.cli.commands.prompt import prompt


def print_home():
    config = load_config() or {}
    model_name = Path(config.get("model_path", "Not set")).name

    items = ['setup', 'config state', 'prompt', 'exit']
    menu = '\n'.join(f'[{i + 1}] {item}' for i, item in enumerate(items))

    content = f"[bold blue]Model:[/bold blue] {model_name}\n\n" + menu

    console.print(
        Panel.fit(
            content,
            title="Lorariel",
            padding=(0, 2)
        )
    )


def print_home_briefly():
    items = ['setup', 'config state', 'prompt', 'exit']
    menu_line = "  ".join(f"[{i + 1}] {item}" for i, item in enumerate(items))

    console.print(Panel.fit(menu_line, title="AI Assistant"))


def run_tui():
    print_home()

    while True:
        cmd = input("› ").strip()

        if cmd in ["4", "exit", "quit"]:
            break

        if cmd in ["1", "setup"]:
            setup()
            print_home_briefly()
            continue

        if cmd in ["2", "config state"]:
            info()
            print_home_briefly()
            continue

        if cmd in ["3", "prompt"]:
            prompt()
            continue

        print("Unknown command:", cmd)
