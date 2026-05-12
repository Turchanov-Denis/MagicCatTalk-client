from utils.files import read_file, read_file_range
from codeassistant.inference.inference_engine import runtime
from rich.markdown import Markdown
from utils.console import console


def prompt(
    text: str = "",
    file: str = None,
    lines: str = None
):
    content = ""

    if file:
        if lines and ":" in lines:
            start, end = map(int, lines.split(":"))
            content = read_file_range(file, start, end)
        else:
            content = read_file(file)

    parts = []

    if text:
        parts.append(text)

    if content:
        parts.append(content)

    full_prompt = "\n\n".join(parts).strip()

    result = runtime.generate(full_prompt)

    console.print(Markdown(result))