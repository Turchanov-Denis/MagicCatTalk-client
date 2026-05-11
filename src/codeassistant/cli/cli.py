import typer
from rich.panel import Panel

from utils.console import console

from codeassistant.cli.commands.setup import setup
from codeassistant.cli.commands.info import info
from codeassistant.cli.commands.prompt import prompt

app = typer.Typer(help="🧠 Lorariel CLI")

app.command()(setup)
app.command()(info)
app.command()(prompt)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        show_home()


def show_home():
    console.print(
        Panel.fit(
            """
🧠 Lorariel CLI

Commands:
  lor setup
  lor info
  lor prompt
""",
            title="Welcome",
        )
    )


if __name__ == "__main__":
    app()