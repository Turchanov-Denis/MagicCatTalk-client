from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from rich.panel import Panel
from rich.table import Table

from codeassistant.cli.commands.benchmark import benchmark
from codeassistant.cli.commands.init import init
from codeassistant.cli.commands.setup import setup
from codeassistant.cli.commands.prompt import prompt
from codeassistant.cli.commands.chat import select_chat

from utils.config import load_config
from utils.console import console


LOR_DIR = Path.cwd() / ".lor"

if not LOR_DIR.exists():

    console.print()

    console.print(
        "[yellow].lor not found[/yellow]"
    )

    console.print(
        "[dim]Initializing project...[/dim]"
    )

    init()


config = load_config()

THEME = config.get(
    "theme",
    {}
)


COMMANDS = {

    "/setup":
        "configure runtime settings",

    "/prompt":
        "enter prompt mode",

    "/chat":
        "select chat",

    "/benchmark":
        "run benchmark suite",

    "/exit":
        "quit Lorariel",
}


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

        "scrollbar.background":
            "bg:default",

        "scrollbar.button":
            "bg:default",
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

        return (
            f"~\\"
            f"{current.relative_to(Path.home())}"
        ).replace("/", "\\")

    except ValueError:

        return str(current)


def print_home():

    config = load_config()

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
        style=THEME["text"]
    )

    for cmd, desc in COMMANDS.items():

        table.add_row(
            cmd,
            desc
        )

    header = (

        f"[{THEME['primary']}]"
        f"{config.get('character_ASCII', '')}"
        f"[/{THEME['primary']}]\n"

        f"[bold {THEME['primary']}]"
        f"model"
        f"[/bold {THEME['primary']}]"
        f"      "
        f"{config.get('model_id', 'Not set')}\n"

        f"[bold {THEME['primary']}]"
        f"lora"
        f"[/bold {THEME['primary']}]"
        f"       "
        f"{config.get('lora', 'Not set')}\n"

        f"[bold {THEME['primary']}]"
        f"chat"
        f"[/bold {THEME['primary']}]"
        f"       "
        f"{config.get('active_chat', 'default')}\n"

        f"[bold {THEME['primary']}]"
        f"directory"
        f"[/bold {THEME['primary']}]"
        f"   "
        f"{get_relative_directory()}\n\n"

        f"[dim]Tips:[/dim] "
        f"write prompt "

        f"[{THEME['primary']}]"
        f"opt."
        f"[/{THEME['primary']}] "

        f"-f file -s 10:20 "
        f"or type "

        f"[{THEME['primary']}]"
        f"\"/\""
        f"[/{THEME['primary']}]"
    )

    console.print()

    console.print(
        Panel.fit(
            header,

            title=(
                f"[bold "
                f"{THEME['text']}]"

                f"{config.get('assistant_name', '')}"

                f"[/bold "
                f"{THEME['text']}]"
            ),

            border_style=THEME["border"],

            padding=(1, 2),
        )
    )

    console.print(table)
    console.print()


def parse_prompt_input(
    raw: str
):

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

            lines = (
                f"{parts[i + 1]}"
                f":"
                f"{parts[i + 2]}"
            )

            i += 3

            continue

        text.append(parts[i])

        i += 1

    return (
        " ".join(text),
        file,
        lines
    )


def run_prompt_mode():

    console.print(
        Panel.fit(
            (

                f"[bold "
                f"{THEME['success']}]"

                f"Prompt mode"

                f"[/bold "
                f"{THEME['success']}]\n\n"

                "Example:\n"

                "› explain this code "
                "-f main.py -s 20 30\n\n"

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

        if raw.lower() in [
            "exit",
            "/exit"
        ]:

            break

        if not raw:
            continue

        text, file, lines = (
            parse_prompt_input(raw)
        )

        prompt(
            text=text,
            file=file,
            lines=lines,
        )


def run_chat_mode():

    select_chat()


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

            if cmd in [
                "exit",
                "quit",
                "/exit"
            ]:

                break

            if cmd in [
                "setup",
                "/setup"
            ]:

                setup()

                continue

            if cmd in [
                "prompt",
                "/prompt"
            ]:

                run_prompt_mode()

                continue

            if cmd in [
                "chat",
                "/chat"
            ]:

                run_chat_mode()

                continue

            if cmd in [
                "benchmark",
                "/benchmark"
            ]:
                benchmark()

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

                text, file, lines = (
                    parse_prompt_input(cmd)
                )

                prompt(
                    text=text,
                    file=file,
                    lines=lines,
                )

        except (
            KeyboardInterrupt,
            EOFError
        ):

            break