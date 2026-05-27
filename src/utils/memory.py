from transformers import AutoTokenizer
from utils.config import load_config

tokenizer = None


def get_tokenizer():
    global tokenizer

    if tokenizer is None:
        config = load_config()

        model_id = config.get("model_id")

        if not model_id:
            raise ValueError("model_id missing in config")

        tokenizer = AutoTokenizer.from_pretrained(model_id)

    return tokenizer


def get_memory_config():
    config = load_config()
    return config.get("memory", {})


def get_max_context_tokens():
    memory = get_memory_config()
    return memory.get("max_context_tokens", 4096)


def get_summary_trigger_tokens():
    memory = get_memory_config()
    return memory.get("summary_trigger_tokens", 2048)


def get_summary_max_tokens():
    memory = get_memory_config()
    return memory.get("summary_max_tokens", 256)


def count_tokens(text: str) -> int:
    tokenizer = get_tokenizer()
    return len(tokenizer.encode(text))


def format_message(msg):
    role = msg["role"]
    content = msg["content"]

    return f"{role}: {content}"


def messages_tokens(messages):
    total = 0

    for msg in messages:
        total += count_tokens(format_message(msg))

    return total


def build_recent_window(messages):
    max_context_tokens = get_max_context_tokens()

    selected = []
    total = 0

    for msg in reversed(messages):
        text = format_message(msg)
        size = count_tokens(text)

        if total + size > max_context_tokens:
            break

        selected.append(msg)
        total += size

    selected.reverse()

    return selected


def build_prompt(summary: str, messages, current_prompt: str):
    history = []

    for msg in messages:
        history.append(format_message(msg))

    history_text = "\n\n".join(history)

    parts = []

    if summary:
        parts.append(f"Summary:\n{summary}")

    if history_text:
        parts.append(f"Conversation:\n{history_text}")

    parts.append(f"user: {current_prompt}")
    parts.append("assistant:")

    return "\n\n".join(parts)


def should_summarize(messages):
    total = messages_tokens(messages)

    limit = (
        get_max_context_tokens()
        + get_summary_trigger_tokens()
    )

    return total > limit


def split_for_summary(messages):
    midpoint = len(messages) // 2

    old = messages[:midpoint]
    recent = messages[midpoint:]

    return old, recent


def build_summary_prompt(messages):
    history = []

    for msg in messages:
        history.append(format_message(msg))

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