import typer

from utils.files import (
    read_file,
    read_file_range
)

from codeassistant.inference.generate import generate

from rich.markdown import Markdown
from utils.console import console


def prompt(
    text: str = "",
    file: str = typer.Option(None, "-f"),
    lines: str = typer.Option(None, "-l")
):
    content = ""

    if file:
        if lines:
            start, end = map(
                int,
                lines.split(":")
            )

            content = read_file_range(
                file,
                start,
                end
            )

        else:
            content = read_file(file)

    full_prompt = f"""
{text}

{content}
"""

    result = generate(full_prompt)

    console.print(
        Markdown(result)
    )