from pathlib import Path

from rich.panel import Panel

from utils.config import load_config
from utils.console import console

from codeassistant.cli.commands.setup import setup
from codeassistant.cli.commands.info import info
from codeassistant.cli.commands.prompt import prompt


def print_home():
    config = load_config()
    model_name = config.get("model_id", "Not set")
    lora_name = config.get("lora_path", "Not set")
    items = ['setup', 'config state', 'prompt', 'exit']
    menu = '\n'.join(f'[{i + 1}] {item}' for i, item in enumerate(items))

    content = f"[bold blue]Model:[/bold blue] {model_name}\n\n"+ f"[bold blue]Lora:[/bold blue] {lora_name}\n\n" + menu

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


def parse_prompt_input(raw: str):
    parts = raw.split()

    text = []
    file = None
    lines = None

    i = 0
    while i < len(parts):

        if parts[i] == "-f":
            file = parts[i + 1]
            i += 2
            continue

        if parts[i] == "-s":
            start = parts[i + 1]
            end = parts[i + 2]
            lines = f"{start}:{end}"
            i += 3
            continue

        text.append(parts[i])
        i += 1

    return " ".join(text), file, lines


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
            console.print("""
            [bold green]Prompt mode[/bold green]

            Example:
            › explain this code -f main.py -s 20 30

            Flags:
            -f file path
            -s start end (lines)

            Type 'exit' to leave prompt mode
            """)

            while True:
                raw = input("› ").strip()

                if raw.lower() in ["exit"]:
                    print_home_briefly()
                    break

                if not raw:
                    continue

                text, file, lines = parse_prompt_input(raw)

                prompt(
                    text=text,
                    file=file,
                    lines=lines
                )

            continue

        print("Unknown command:", cmd)
