# code_review.py

from pathlib import Path

from git import Repo

from utils.console import console

from codeassistant.cli.commands.prompt import (
    prompt,
    build_code_review_prompt
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


MAX_REVIEW_FILES = 10

MAX_CHUNKS_PER_FILE = 5

MAX_CHUNK_LINES = 120


# -------------------------
# split large hunk
# -------------------------

def split_large_hunk(
        hunk: str,
        max_lines: int
):

    lines = hunk.splitlines()

    chunks = []

    current = []

    for line in lines:

        current.append(line)

        if len(current) >= max_lines:

            chunks.append(
                "\n".join(current)
            )

            current = []

    if current:

        chunks.append(
            "\n".join(current)
        )

    return chunks


# -------------------------
# split diff by hunks
# -------------------------

def split_diff_by_hunks(
        patch: str
):

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

    for hunk in hunks:

        if len(hunk.splitlines()) > MAX_CHUNK_LINES:

            chunks.extend(

                split_large_hunk(

                    hunk,

                    MAX_CHUNK_LINES
                )
            )

        else:

            chunks.append(hunk)

    return chunks[:MAX_CHUNKS_PER_FILE]


# -------------------------
# git repo
# -------------------------

def get_repo():

    try:

        return Repo(

            Path.cwd(),

            search_parent_directories=True
        )

    except Exception:

        console.print(
            "[red]Git repository not found[/red]"
        )

        return None


# -------------------------
# last commit diff
# -------------------------

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


# -------------------------
# changed lines
# -------------------------

def extract_changed_lines(
        patch
):

    changed = []

    for line in patch.splitlines():

        if line.startswith("@@"):

            changed.append(line)

    return "\n".join(changed)


# -------------------------
# parse changed line ranges
# -------------------------

def extract_line_numbers(
        changed_lines
):

    ranges = []

    for line in changed_lines.splitlines():

        if "@@" not in line:
            continue

        try:

            part = line.split("+")[1]

            part = part.split(" ")[0]

            ranges.append(part)

        except Exception:

            continue

    return ranges


# -------------------------
# surrounding context
# -------------------------

def build_context(
        repo,
        file_path,
        line_ranges,
        radius=10
):

    full_path = (

        Path(repo.working_tree_dir)

        / file_path
    )

    if not full_path.exists():

        return ""

    if full_path.suffix not in SUPPORTED_EXTENSIONS:

        return ""

    try:

        lines = full_path.read_text(

            encoding="utf-8"

        ).splitlines()

    except Exception:

        return ""

    collected = []

    for item in line_ranges[:2]:

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

    return "\n\n".join(collected)


# -------------------------
# main review command
# -------------------------

def code_review():

    repo = get_repo()

    if not repo:
        return

    console.print()
    console.print(
        "[yellow]Collecting git changes...[/yellow]"
    )

    diffs = get_last_commit_diff(
        repo
    )

    reviewed = 0

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

        extension = Path(
            file_path
        ).suffix

        if extension not in SUPPORTED_EXTENSIONS:

            continue

        changed_lines = extract_changed_lines(
            patch
        )

        line_ranges = extract_line_numbers(
            changed_lines
        )

        context = build_context(

            repo,

            file_path,

            line_ranges
        )

        diff_chunks = split_diff_by_hunks(
            patch
        )

        if len(diff_chunks) >= MAX_CHUNKS_PER_FILE:

            console.print(

                "[yellow]"
                "Large diff truncated"
                "[/yellow]"
            )

        reviewed += 1

        for index, chunk in enumerate(

                diff_chunks,

                start=1
        ):

            console.print(

                "[cyan]"

                f"Reviewing "

                f"{file_path} "

                f"({index}/"

                f"{len(diff_chunks)})"

                "[/cyan]"
            )

            final_prompt = build_code_review_prompt(

                file_path=file_path,

                changed_lines=changed_lines,

                diff_chunk=chunk,

                context=context
            )

            prompt(

                text=final_prompt,

                use_chat=False
            )

            console.print()