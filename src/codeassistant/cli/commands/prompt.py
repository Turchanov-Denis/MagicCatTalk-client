import requests

from rich.markdown import Markdown

from utils.config import load_config
from utils.files import (
    read_file,
    read_file_range
)

from utils.console import console


def prompt(
    text: str = "",
    file: str = None,
    lines: str = None
):

    content = ""

    if file:

        if lines and ":" in lines:

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

    parts = []

    if text:
        parts.append(text)

    if content:
        parts.append(content)

    full_prompt = (
        "\n\n".join(parts)
        .strip()
    )

    config = load_config()

    backend_url = config.get(
        "backend_url",
        "http://localhost:8000"
    )

    lora = config.get("lora")

    payload = {
        "prompt": full_prompt
    }

    if lora:
        payload["lora"] = lora

    try:

        response = requests.post(
            f"{backend_url}/v1/generate",
            json=payload,
            timeout=300
        )

    except Exception as e:

        console.print(
            f"[red]Backend error:[/red] {e}"
        )

        return

    if response.status_code != 200:

        console.print(
            f"[red]Request failed:[/red] "
            f"{response.status_code}"
        )

        console.print(response.text)

        return

    data = response.json()

    result = data["response"]

    console.print(
        {
            "backend": backend_url,
            "lora": lora
        }
    )

    console.print(
        Markdown(result)
    )