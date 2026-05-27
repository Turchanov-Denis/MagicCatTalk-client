import re

import requests
from transformers import AutoTokenizer

from utils.console import console

from utils.config import load_config

from utils.tools import read_file

from utils.chat_store import ChatStore

from utils.memory import build_recent_window, build_prompt

from utils.codebase import build_auto_context

from utils.logger import logger

store = ChatStore()

# SYSTEM_PROMPT = """
# You are a code assistant.
#
# Rules:
# - Answer ONLY using provided context
# - Do NOT invent code
# - Do NOT hallucinate architecture
# - If information is missing say:
#   "Not enough context"
# - Focus ONLY on provided code
# """.strip()


def count_tokens(tokenizer, text: str):
    if not text:
        return 0
    return len(tokenizer.encode(text))


def extract_mentions(text: str):
    return re.findall(r"@([^\s]+)", text)


def build_selected_context(selected):
    return f"""
            Symbol:
            {selected["name"]}
            
            Type:
            {selected["type"]}
            
            File:
            {selected["file"]}
            
            Lines:
            {selected["lineno"]}-{selected["end_lineno"]}
            
            Code:
            
            {selected["code"]}
            """.strip()


def prompt(text: str = "", use_chat: bool = True):
    result = build_auto_context(text)
    auto_context = ""
    code_query = bool(result)

    if isinstance(result, dict):
        if result.get("ambiguous"):
            matches = result["matches"]
            console.print()
            console.print("[yellow]" "Multiple symbols found:" "[/yellow]")
            console.print()
            for i, match in enumerate(matches, start=1):
                console.print(f"[cyan]{i}.[/cyan] " f"{match['file']}")

            console.print()
            choice = input("Select file number: ").strip()
            try:
                index = int(choice) - 1
                selected = matches[index]

            except Exception:
                console.print("[red]" "Invalid selection" "[/red]")
                return

            auto_context = build_selected_context(selected)
        else:
            auto_context = result.get("context", "")

    elif isinstance(result, str):
        auto_context = result

    mentions = extract_mentions(text)
    parts = []

    if auto_context:
        parts.append(auto_context)

    for mention in mentions:
        if auto_context:
            if mention in auto_context:
                continue
        try:
            content = read_file(mention)
            parts.append(f"File: {mention}\nContent:\n{content}")

        except Exception:

            pass

    if text:
        parts.append(text)

    user_prompt = "\n\n".join(parts).strip()

    if not user_prompt:
        console.print("[red]" "Empty prompt" "[/red]")

        return

    config = load_config()
    tokenizer = AutoTokenizer.from_pretrained(config.get("model_id"), trust_remote_code=True)
    backend_url = config.get("backend_url")
    lora = config.get("lora")
    final_prompt = (
        # f"{SYSTEM_PROMPT}\n\n"
        f"{user_prompt}"
    )

    chat_name = config.get("active_chat", "default")

    if use_chat:
        data = store.load(chat_name)
        recent = build_recent_window(data["messages"])
        final_prompt = build_prompt(summary=data.get("summary", ""), messages=recent, current_prompt=user_prompt)

        request_tokens = count_tokens(tokenizer,text)
        code_tokens = count_tokens(tokenizer,auto_context)

        memory_text = "\n".join(msg.get("content","") for msg in recent)
        memory_tokens = count_tokens(tokenizer, memory_text)
        total_tokens = count_tokens(tokenizer,final_prompt)

        console.print(
            f"[dim]"
            f"ctx {total_tokens}"
            f" | user {request_tokens}"
            f" | code {code_tokens}"
            f" | memory {memory_tokens}"
            f"[/dim]"
        )


    payload = {"prompt": final_prompt}
    if lora:
        payload["lora"] = lora

    response_text = ""
    logger.info(f"Sending prompt to backend: {payload}")

    try:
        response = requests.post(
            f"{backend_url}/v1/generate/stream", json=payload, stream=True, timeout=300
        )
        response.raise_for_status()

    except Exception as e:

        console.print(f"[red]" f"Backend error:" f"[/red] {e}")
        return

    try:
        logger.info(f"responce: {response}")
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                response_text += chunk
                console.file.write(chunk)
                console.file.flush()

    except KeyboardInterrupt:
        console.print("\n[yellow]" "Generation interrupted" "[/yellow]")

    except Exception as e:
        console.print(f"\n[red]" f"Stream error:" f"[/red] {e}")

    finally:
        console.print()

    if use_chat:
        store.append(chat_name, "user", user_prompt)
        store.append(chat_name, "assistant", response_text)


def main():
    print("catGirl")
