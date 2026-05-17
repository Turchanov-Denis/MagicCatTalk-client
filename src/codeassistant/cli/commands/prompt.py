import requests

from utils.console import (
    console
)

from utils.config import (
    load_config
)

from utils.tools import (
    read_file,
    read_file_range
)

from utils.chat_store import (
    ChatStore
)

from utils.memory import (
    build_recent_window,
    build_prompt
)

store = ChatStore()


def prompt(
        text: str = "",
        file: str = None,
        lines: str = None,
        use_chat: bool = True
):
    content = ""

    if file:

        if (
                lines
                and ":" in lines
        ):

            start, end = map(
                int,
                lines.split(":")
            )

            content = (
                read_file_range(
                    file,
                    start,
                    end
                )
            )

        else:

            content = read_file(
                file
            )

    parts = []

    if text:
        parts.append(text)

    if content:
        parts.append(content)

    user_prompt = (
        "\n\n".join(parts)
        .strip()
    )

    if not user_prompt:
        console.print(
            "[red]"
            "Empty prompt"
            "[/red]"
        )

        return

    config = load_config()

    backend_url = config.get(
        "backend_url"
    )

    lora = config.get(
        "lora"
    )

    final_prompt = user_prompt

    chat_name = config.get(
        "active_chat",
        "default"
    )

    if use_chat:
        data = store.load(
            chat_name
        )

        recent = build_recent_window(
            data["messages"]
        )

        final_prompt = build_prompt(

            summary=data.get(
                "summary",
                ""
            ),

            messages=recent,

            current_prompt=user_prompt
        )

    payload = {
        "prompt": final_prompt
    }

    if lora:
        payload["lora"] = lora

    response_text = ""

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
            f"[red]"
            f"Backend error:"
            f"[/red] {e}"
        )

        return

    try:

        for chunk in response.iter_content(
                chunk_size=None,
                decode_unicode=True
        ):

            if chunk:
                response_text += chunk

                console.file.write(
                    chunk
                )

                console.file.flush()

    except KeyboardInterrupt:

        console.print(
            "\n[yellow]"
            "Generation interrupted"
            "[/yellow]"
        )

    except Exception as e:

        console.print(
            f"\n[red]"
            f"Stream error:"
            f"[/red] {e}"
        )

    finally:

        console.print()

    if use_chat:
        store.append(
            chat_name,
            "user",
            user_prompt
        )

        store.append(
            chat_name,
            "assistant",
            response_text
        )
