from pathlib import Path

from git import Repo

from utils.console import (
    console
)

from utils.config import (
    load_config
)

from codeassistant.cli.commands.prompt import (
    prompt
)


SUPPORTED_EXTENSIONS = [

    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".c"
]


IGNORED_PATHS = [

    "benchmark/results",
    "logs",
    "__pycache__",
    ".git"
]


REVIEW_TEMPLATE = """
Perform code review for the following code changes.

Requirements:
- Specify file name
- Specify changed lines
- Find bugs
- Find vulnerabilities
- Find logic issues
- Suggest improvements
- Keep response short

File:
{file}

Changed lines:
{lines}

Git diff:

{diff}

Additional context:

{context}
"""


MAX_REVIEW_FILES = 10

MAX_CHUNKS_PER_FILE = 3


def split_diff_by_hunks(
    patch,
    max_tokens
):

    max_chars = (
        max_tokens * 4
    )

    hunks = []

    current = []

    for line in patch.splitlines():

        if line.startswith("@@"):

            if current:

                hunks.append(
                    "\n".join(current)
                )

                current = []

        current.append(line)

    if current:

        hunks.append(
            "\n".join(current)
        )

    chunks = []

    current_chunk = ""

    for hunk in hunks:

        if (

            len(current_chunk)
            + len(hunk)

            > max_chars
        ):

            if current_chunk.strip():

                chunks.append(
                    current_chunk
                )

            current_chunk = ""

        current_chunk += (
            hunk + "\n"
        )

    if current_chunk.strip():

        chunks.append(
            current_chunk
        )

    return chunks[
        :MAX_CHUNKS_PER_FILE
    ]


def get_repo():

    try:

        return Repo(
            Path.cwd(),
            search_parent_directories=True
        )

    except Exception:

        console.print(
            "[red]"
            "Git repository not found"
            "[/red]"
        )

        return None


def get_last_commit_diff(
    repo
):

    commit = repo.head.commit

    if not commit.parents:

        return commit.diff(
            create_patch=True
        )

    return commit.parents[0].diff(
        commit,
        create_patch=True
    )


def extract_changed_lines(
    patch
):

    changed = []

    for line in patch.splitlines():

        if line.startswith("@@"):

            changed.append(line)

    return "\n".join(changed)


def extract_line_numbers(
    changed_lines
):

    ranges = []

    for line in changed_lines.splitlines():

        if "@@" not in line:

            continue

        try:

            part = (
                line.split("+")[1]
                .split(" ")[0]
            )

            ranges.append(part)

        except Exception:

            continue

    return ranges


def build_context(
    repo,
    file_path,
    line_ranges,
    radius=30
):

    full_path = (
        Path(repo.working_tree_dir)
        / file_path
    )

    if not full_path.exists():

        return ""

    if (
        full_path.suffix
        not in SUPPORTED_EXTENSIONS
    ):

        return ""

    try:

        lines = full_path.read_text(
            encoding="utf-8"
        ).splitlines()

    except Exception:

        return ""

    collected = []

    for item in line_ranges:

        try:

            start = int(
                item.split(",")[0]
            )

        except Exception:

            continue

        left = max(
            0,
            start - radius
        )

        right = min(
            len(lines),
            start + radius
        )

        chunk = "\n".join(
            lines[left:right]
        )

        collected.append(chunk)

    return "\n\n".join(
        collected
    )


def code_review():

    config = load_config()

    memory_config = config.get(
        "memory",
        {}
    )

    review_config = config.get(
        "review",
        {}
    )

    max_context_tokens = (
        memory_config.get(
            "max_context_tokens",
            4096
        )
    )

    repo = get_repo()

    if not repo:

        return

    console.print()

    console.print(
        "[yellow]"
        "Collecting git changes..."
        "[/yellow]"
    )

    diffs = get_last_commit_diff(
        repo
    )

    reviewed = 0

    all_reviews = []

    for diff in diffs:

        if reviewed >= MAX_REVIEW_FILES:

            break

        try:

            patch = diff.diff.decode(

                "utf-8",

                errors="ignore"
            )

        except Exception:

            continue

        if not patch.strip():

            continue

        file_path = (

            diff.b_path
            or diff.a_path
            or "unknown"
        )

        if any(

            ignored in file_path

            for ignored in IGNORED_PATHS
        ):

            continue

        extension = (
            Path(file_path).suffix
        )

        if (
            extension
            not in SUPPORTED_EXTENSIONS
        ):

            continue

        changed_lines = (
            extract_changed_lines(
                patch
            )
        )

        line_ranges = (
            extract_line_numbers(
                changed_lines
            )
        )

        context = build_context(

            repo,

            file_path,

            line_ranges
        )

        available_tokens = (
            max_context_tokens
            // 2
        )

        diff_chunks = (
            split_diff_by_hunks(

                patch,

                available_tokens
            )
        )

        reviewed += 1

        for index, chunk in enumerate(

            diff_chunks,

            start=1
        ):

            final_prompt = (
                REVIEW_TEMPLATE.format(

                    file=file_path,

                    lines=changed_lines,

                    diff=chunk,

                    context=context
                )
            )

            console.print()

            console.print(

                "[cyan]"

                f"Reviewing "
                f"{file_path} "
                f"(chunk "
                f"{index}/"
                f"{len(diff_chunks)})"

                "[/cyan]"
            )

            console.print()

            response = prompt(

                text=final_prompt,

                use_chat=False
            )

            if response:

                all_reviews.append({

                    "file":
                        file_path,

                    "chunk":
                        index,

                    "review":
                        response
                })

    if all_reviews:

        console.print()

        console.print(
            "[green]"
            "Review completed"
            "[/green]"
        )

        console.print()

        for item in all_reviews:

            console.print(

                "[yellow]"
                f"File: "
                f"{item['file']} "
                f"(chunk "
                f"{item['chunk']})"
                "[/yellow]"
            )

            console.print(
                item["review"]
            )

            console.print()