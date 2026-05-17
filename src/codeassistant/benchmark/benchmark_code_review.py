import json
import time
import re

from pathlib import Path

from rapidfuzz import fuzz


TASKS_PATH = (
    Path(__file__)
    .parent
    / "tasks"
    / "code_review.json"
)

RESULTS_DIR = (
    Path(__file__)
    .parent
    / "results"
)

RESULTS_DIR.mkdir(
    exist_ok=True
)


DESCRIPTION = """
Code review benchmark.

Checks:
- bug detection
- hallucinations
- review quality
"""


PROMPT_TEMPLATE = """
Review the following Python code.

Find bugs, vulnerabilities,
or logic issues.

Rules:
- Be short
- Do not explain
- Return only found issues
- If code is correct return ONLY:
NO_BUGS

Code:

{code}
"""


FUZZY_THRESHOLD = 80


BUG_ALIASES = {

    "possible none access": [

        "none",
        "null",
        "attributeerror",
        "none access",
        "none check"
    ],

    "division by zero": [

        "division by zero",
        "divide by zero",
        "zero division",
        "b == 0",
        "/ 0"
    ],

    "index out of range": [

        "index out of range",
        "out of bounds",
        "items[0]",
        "empty list",
        "indexerror"
    ],

    "mutable default argument": [

        "mutable default",
        "default argument",
        "items=[]",
        "items = []",
        "items=None",
        "items = None"
    ],

    "infinite recursion": [

        "infinite recursion",
        "recursive",
        "maximum recursion",
        "stack overflow"
    ],

    "sql injection": [

        "sql injection",
        "unsafe query",
        "f-string sql",
        "unsanitized"
    ],

    "unsafe eval": [

        "unsafe eval",
        "eval(",
        "arbitrary code",
        "code execution"
    ],

    "file resource leak": [

        "resource leak",
        "file leak",
        "open(",
        "missing close",
        "context manager",
        "with open"
    ],

    "bare except": [

        "bare except",
        "except:",
        "generic exception"
    ]
}


FIX_PATTERNS = {

    "mutable default argument": [

        "items=None",
        "items = None"
    ],

    "file resource leak": [

        "with open"
    ],

    "division by zero": [

        "if b == 0",
        "if b != 0",
        "ZeroDivisionError"
    ],

    "bare except": [

        "except ValueError",
        "except Exception"
    ]
}


def load_tasks():

    with open(
        TASKS_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def clean_response(
    text: str
):

    stop_tokens = [

        "Human:",
        "### Response",

        "<|fim_prefix|>",
        "<|fim_middle|>",
        "<|fim_suffix|>",

        "<|im_end|>",
        "<|endoftext|>"
    ]

    text = text.replace(
        "```python",
        ""
    )

    text = text.replace(
        "```",
        ""
    )

    for token in stop_tokens:

        if token in text:

            text = text.split(token)[0]

    text = re.sub(
        r"^Assistant\s*",
        "",
        text
    )

    return text.strip()


def fuzzy_contains(
    response,
    phrase
):

    response = response.lower()

    phrase = phrase.lower()

    score = fuzz.partial_ratio(
        phrase,
        response
    )

    return (
        score >= FUZZY_THRESHOLD
    )


def contains_fix(
    response,
    bug
):

    patterns = FIX_PATTERNS.get(
        bug,
        []
    )

    for pattern in patterns:

        if fuzzy_contains(
            response,
            pattern
        ):

            return True

    return False


def evaluate_task(
    response,
    expected_bugs
):

    response = clean_response(
        response
    )

    response_lower = (
        response.lower()
    )

    if not expected_bugs:

        hallucination = (
            "no_bugs"
            not in response_lower
        )

        return {

            "passed":
                not hallucination,

            "hallucination":
                hallucination,

            "found":
                []
        }

    found = []

    for bug in expected_bugs:

        aliases = BUG_ALIASES.get(
            bug,
            [bug]
        )

        detected = False

        for alias in aliases:

            if fuzzy_contains(
                response,
                alias
            ):

                detected = True

                break

        if not detected:

            detected = contains_fix(
                response,
                bug
            )

        if detected:

            found.append(bug)

    success = (
        len(found)
        == len(expected_bugs)
    )

    return {

        "passed":
            success,

        "hallucination":
            False,

        "found":
            found
    }


def run_code_review(
    runtime_generate,
    runtime_name="base"
):

    tasks = load_tasks()

    passed = 0
    hallucinations = 0

    total_latency = 0

    results = []

    for task in tasks:

        prompt = (
            PROMPT_TEMPLATE.format(
                code=task["code"]
            )
        )

        start = time.time()

        response = runtime_generate(
            prompt
        )

        response = clean_response(
            response
        )

        latency = (
            time.time() - start
        )

        total_latency += latency

        evaluation = evaluate_task(

            response=response,

            expected_bugs=task[
                "bugs"
            ]
        )

        if evaluation["passed"]:

            passed += 1

        if evaluation[
            "hallucination"
        ]:

            hallucinations += 1

        results.append({

            "id":
                task["id"],

            "passed":
                evaluation[
                    "passed"
                ],

            "hallucination":
                evaluation[
                    "hallucination"
                ],

            "expected_bugs":
                task["bugs"],

            "found_bugs":
                evaluation[
                    "found"
                ],

            "latency":
                latency,

            "response":
                response,

            "code":
                task["code"]
        })

    accuracy = (
        passed / len(tasks)
    ) * 100

    hallucination_rate = (
        hallucinations / len(tasks)
    ) * 100

    avg_latency = (
        total_latency / len(tasks)
    )

    summary = {

        "runtime":
            runtime_name,

        "tasks":
            len(tasks),

        "passed":
            passed,

        "failed":
            len(tasks) - passed,

        "accuracy":
            accuracy,

        "hallucination_rate":
            hallucination_rate,

        "avg_latency":
            avg_latency,

        "results":
            results
    }

    output = (
        RESULTS_DIR
        / f"{runtime_name}_review.json"
    )

    output.write_text(

        json.dumps(
            summary,
            indent=2,
            ensure_ascii=False
        ),

        encoding="utf-8"
    )

    return summary