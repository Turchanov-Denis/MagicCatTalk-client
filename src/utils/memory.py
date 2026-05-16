import json

from transformers import (
    AutoTokenizer
)

from utils.config import (
    load_config
)


config = load_config()

tokenizer = AutoTokenizer.from_pretrained(
    config["model_id"]
)


MEMORY_CONFIG = config.get(
    "memory",
    {}
)

MAX_CONTEXT_TOKENS = (
    MEMORY_CONFIG.get(
        "max_context_tokens",
        4096
    )
)

SUMMARY_TRIGGER_TOKENS = (
    MEMORY_CONFIG.get(
        "summary_trigger_tokens",
        2048
    )
)

SUMMARY_MAX_TOKENS = (
    MEMORY_CONFIG.get(
        "summary_max_tokens",
        256
    )
)


def count_tokens(text: str) -> int:

    return len(
        tokenizer.encode(text)
    )


def format_message(msg):

    role = msg["role"]

    content = msg["content"]

    return (
        f"{role}: "
        f"{content}"
    )


def messages_tokens(messages):

    total = 0

    for msg in messages:

        total += count_tokens(
            format_message(msg)
        )

    return total


def build_recent_window(messages):

    selected = []

    total = 0

    for msg in reversed(messages):

        text = format_message(msg)

        size = count_tokens(text)

        if (
            total + size
            > MAX_CONTEXT_TOKENS
        ):
            break

        selected.append(msg)

        total += size

    selected.reverse()

    return selected


def build_prompt(
    summary: str,
    messages,
    current_prompt: str
):

    history = []

    for msg in messages:

        history.append(
            format_message(msg)
        )

    history_text = "\n\n".join(
        history
    )

    parts = []

    if summary:

        parts.append(
            f"Summary:\n{summary}"
        )

    if history_text:

        parts.append(
            f"Conversation:\n"
            f"{history_text}"
        )

    parts.append(
        f"user: {current_prompt}"
    )

    parts.append(
        "assistant:"
    )

    return "\n\n".join(parts)


def should_summarize(messages):

    total = messages_tokens(
        messages
    )

    return (
        total >
        (
            MAX_CONTEXT_TOKENS
            + SUMMARY_TRIGGER_TOKENS
        )
    )


def split_for_summary(messages):

    midpoint = (
        len(messages) // 2
    )

    old = messages[:midpoint]

    recent = messages[midpoint:]

    return old, recent


def build_summary_prompt(messages):

    history = []

    for msg in messages:

        history.append(
            format_message(msg)
        )

    text = "\n\n".join(history)

    return f"""
Summarize the conversation.

Focus on:
- technical decisions
- architecture
- active tasks
- unresolved problems
- user goals

Ignore:
- greetings
- repeated code
- unnecessary details

Conversation:

{text}

Summary:
""".strip()