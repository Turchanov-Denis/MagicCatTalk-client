from rich.panel import Panel
from utils.console import console

from codeassistant.cli.commands.setup import setup
from codeassistant.cli.commands.info import info
from codeassistant.cli.commands.prompt import prompt


def run_tui():
    console.print(
        Panel.fit(
            """
🧠 Lorariel

[1] setup
[2] info
[3] prompt
[4] exit
""",
            title="AI Assistant",
        )
    )

    while True:
        cmd = input("› ").strip()

        # -----------------------
        # EXIT
        # -----------------------
        if cmd in ["4", "exit", "quit"]:
            break

        # -----------------------
        # ROUTER (ВОТ ЧЕГО НЕ ХВАТАЛО)
        # -----------------------
        if cmd in ["1", "setup"]:
            setup()
            continue

        if cmd in ["2", "info"]:
            info()
            continue

        if cmd in ["3", "prompt"]:
            prompt()
            continue

        print("Unknown command:", cmd)