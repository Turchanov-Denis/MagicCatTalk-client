import typer

from ui.tui import run_tui

from codeassistant.cli.commands.setup import setup
from codeassistant.cli.commands.info import info
from codeassistant.cli.commands.prompt import prompt


app = typer.Typer()

app.command()(setup)
app.command()(info)
app.command()(prompt)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        run_tui()


if __name__ == "__main__":
    app()