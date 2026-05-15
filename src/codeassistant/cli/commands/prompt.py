import requests

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

    if not full_prompt:

        console.print(
            "[red]Empty prompt[/red]"
        )

        return

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

    console.print(
        {
            "backend": backend_url,
            "lora": lora
        }
    )

    try:

        response = requests.post(
            f"{backend_url}/v1/generate/stream",
            json=payload,
            stream=True,
            timeout=300
        )

        response.raise_for_status()

    except Exception as e:

        console.print(
            f"[red]Backend error:[/red] {e}"
        )

        return

    try:

        for chunk in response.iter_content(
            chunk_size=None,
            decode_unicode=True
        ):

            if chunk:

                console.file.write(chunk)
                console.file.flush()

    except KeyboardInterrupt:

        console.print(
            "\n[yellow]Generation interrupted[/yellow]"
        )

    except Exception as e:

        console.print(
            f"\n[red]Stream error:[/red] {e}"
        )

    finally:

        console.print()