from pathlib import Path


def read_file(path: str):
    return Path(path).read_text(encoding="utf-8")


def read_file_range(path: str, start: int, end: int):
    content = read_file(path)

    lines = content.splitlines()

    return "\n".join(lines[start:end])
