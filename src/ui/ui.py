from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from rich.panel import Panel
from rich.table import Table

from codeassistant.cli.commands.setup import setup
from codeassistant.cli.commands.prompt import prompt

from utils.config import load_config
from utils.console import console


THEME = {
    "primary": "medium_purple",
    "text": "white",
    "muted": "gray",
    "border": "white",
    "success": "green",
    "warning": "yellow",
    "error": "red",
}


COMMANDS = {
    "/setup": "configure runtime settings",
    "/prompt": "enter prompt mode",
    "/chat": "select chat",
    "/benchmark": "run benchmark suite",
    "/exit": "quit Lorariel",
}

UNICORN = rf"""
   *
    \
    \-\           ___________
    \---\_/\.    /          _)
   (((|||/-|))  /        __)
  _/   ^   (()) \       )
 ('_'    "  --   \     )
     |     (())__/  /\__.--.
     (      --         )\\| 
      |     (||)  _____ |\\\\)
     _|      ||  /      \ |||))
 ___(/_\_  .__ _/        | (()
/_{{______)/  /_{{__/\_____| (\__
------------------------------------------------
"""
COMMAND_COMPLETER = WordCompleter(
    COMMANDS,
    meta_dict=COMMANDS,
    ignore_case=True,
    sentence=True,
)


PROMPT_STYLE = Style.from_dict(
    {
        "completion-menu":
            f"bg:default fg:{THEME['text']}",

        "completion-menu.completion":
            f"bg:default fg:{THEME['text']}",

        "completion-menu.completion.current":
            f"bg:default fg:{THEME['text']} bold",

        "completion-menu.meta.completion":
            f"bg:default fg:{THEME['muted']}",

        "completion-menu.meta.completion.current":
            f"bg:default fg:{THEME['text']}",

        "scrollbar.background": "bg:default",
        "scrollbar.button": "bg:default",
    }
)


session = PromptSession(
    completer=COMMAND_COMPLETER,
    complete_while_typing=True,
    style=PROMPT_STYLE,
)


def get_relative_directory() -> str:
    current = Path.cwd()

    try:
        home = Path.home()

        relative = f"~\\{current.relative_to(home)}"

        return relative.replace("/", "\\")

    except ValueError:
        return str(current)


def print_home():
    config = load_config()

    model_name = config.get("model_id", "Not set")
    lora_name = config.get("lora_path", "Not set")

    current_dir = get_relative_directory()

    table = Table(
        show_header=False,
        box=None,
        padding=(0, 0, 0, 1),
        expand=False,
    )

    table.add_column(
        style=f"bold {THEME['primary']}",
        no_wrap=True,
    )

    table.add_column(
        style=THEME["text"],
    )

    for cmd, desc in COMMANDS.items():
        table.add_row(cmd, desc)

    header = (
        f"[{THEME['primary']}]{UNICORN}[/{THEME['primary']}]\n"

        f"[bold {THEME['primary']}]model[/bold {THEME['primary']}]"
        f"      {model_name}\n"

        f"[bold {THEME['primary']}]lora[/bold {THEME['primary']}]"
        f"       {lora_name}\n"

        f"[bold {THEME['primary']}]directory[/bold {THEME['primary']}]"
        f"   {current_dir}\n\n"

        f"[dim]Tips:[/dim] write prompt "
        f"[{THEME['primary']}]opt.[/{THEME['primary']}] "
        f"-f file -s 10:20 "
        f"or type "
        f"[{THEME['primary']}]\"/\"[/{THEME['primary']}]"
    )

    console.print()

    console.print(
        Panel.fit(
            header,
            title=(
                f"[bold {THEME['text']}]"
                f"Lorariel"
                f"[/bold {THEME['text']}]"
            ),
            border_style=THEME["border"],
            padding=(1, 2),
        )
    )

    console.print(table)
    console.print()


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


def run_prompt_mode():
    console.print(
        Panel.fit(
            (
                f"[bold {THEME['success']}]"
                f"Prompt mode"
                f"[/bold {THEME['success']}]\n\n"

                "Example:\n"
                "› explain this code -f main.py -s 20 30\n\n"

                "[bold]Flags[/bold]\n"
                "-f   file path\n"
                "-s   start end"
            ),
            border_style=THEME["border"],
        )
    )

    while True:
        raw = session.prompt(
            HTML(
                f"<ansi{THEME['primary']}>"
                f"prompt"
                f"</ansi{THEME['primary']}> › "
            )
        ).strip()

        if raw.lower() in ["exit", "/exit"]:
            break

        if not raw:
            continue

        text, file, lines = parse_prompt_input(raw)

        prompt(
            text=text,
            file=file,
            lines=lines,
        )


def run_chat_mode():
    # chats = runtime._chat_store.list_chats()
    #
    # console.print(
    #     f"\n[bold {THEME['primary']}]Chats[/bold {THEME['primary']}]\n"
    # )
    #
    # if chats:
    #     for i, chat in enumerate(chats, start=1):
    #         console.print(
    #             f"[{THEME['success']}][{i}]"
    #             f"[/{THEME['success']}] "
    #
    #             f"{chat['name']} "
    #
    #             f"[dim]"
    #             f"({chat.get('created_at', 'unknown')})"
    #             f"[/dim]"
    #         )
    # else:
    #     console.print(
    #         f"[{THEME['warning']}]"
    #         f"No chats found"
    #         f"[/{THEME['warning']}]"
    #     )
    #
    # console.print(
    #     "\n[dim]Enter chat name to switch/create[/dim]\n"
    # )
    #
    # name = session.prompt(
    #     HTML(
    #         f"<ansi{THEME['primary']}>"
    #         f"chat"
    #         f"</ansi{THEME['primary']}> › "
    #     )
    # ).strip()
    #
    # if not name:
    #     console.print(
    #         f"[{THEME['error']}]"
    #         f"Empty chat name"
    #         f"[/{THEME['error']}]"
    #     )
    #     return
    #
    # runtime._chat_store.register_chat(name)
    # runtime.load_chat(name)
    #
    # console.print(
    #     f"\n[{THEME['success']}]"
    #     f"Switched to chat:"
    #     f"[/{THEME['success']}] "
    #     f"{name}\n"
    # )
    console.print("chat")


def run_tui():
    print_home()

    while True:
        try:
            cmd = session.prompt(
                HTML(
                    f"<ansi{THEME['primary']}>"
                    f"❯"
                    f"</ansi{THEME['primary']}> "
                )
            ).strip()

            if cmd in ["5", "exit", "quit", "/exit"]:
                break

            if cmd in ["1", "setup", "/setup"]:
                setup()
                continue

            if cmd in ["2", "prompt", "/prompt"]:
                run_prompt_mode()
                continue

            if cmd in ["3", "chat", "/chat"]:
                run_chat_mode()
                continue

            if cmd in ["4", "benchmark", "/benchmark"]:
                console.print(
                    f"[{THEME['warning']}]"
                    f"Benchmark mode not implemented"
                    f"[/{THEME['warning']}]"
                )
                continue

            if cmd.startswith("/"):
                console.print(
                    f"[{THEME['error']}]"
                    f"Unknown command:"
                    f"[/{THEME['error']}] "
                    f"{cmd}"
                )
                continue

            if cmd:
                text, file, lines = parse_prompt_input(cmd)

                prompt(
                    text=text,
                    file=file,
                    lines=lines,
                )

        except KeyboardInterrupt:
            break

        except EOFError:
            break