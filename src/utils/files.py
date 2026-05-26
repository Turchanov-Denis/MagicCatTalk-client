from pathlib import Path


DEFAULT_IGNORE = [

    ".git",
    ".venv",
    "__pycache__",
    "node_modules",

    ".idea",
    ".vscode"
]


FILE_CACHE = []


def load_gitignore():

    gitignore = Path.cwd() / ".gitignore"

    if not gitignore.exists():
        return []

    try:

        lines = gitignore.read_text(
            encoding="utf-8"
        ).splitlines()

    except Exception:

        return []

    patterns = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        patterns.append(line)

    return patterns


GITIGNORE = load_gitignore()


def should_ignore(path: Path):

    path_str = str(path)

    for part in path.parts:

        if part in DEFAULT_IGNORE:
            return True

    for pattern in GITIGNORE:

        pattern = pattern.replace(
            "/",
            ""
        )

        if pattern in path_str:
            return True

    return False


def build_file_cache():

    files = []

    for path in Path.cwd().rglob("*"):

        if not path.is_file():
            continue

        if should_ignore(path):
            continue

        files.append(

            str(
                path.relative_to(
                    Path.cwd()
                )
            )
        )

    return sorted(files)


def refresh_file_cache():

    global FILE_CACHE

    FILE_CACHE = build_file_cache()


def list_project_files():

    return FILE_CACHE