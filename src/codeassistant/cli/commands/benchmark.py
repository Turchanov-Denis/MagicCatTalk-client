import requests
from rich.panel import Panel
from codeassistant.benchmark.benchmark_code_review import (
    DESCRIPTION,
    run_code_review
)

from utils.config import (
    load_config
)

from utils.console import (
    console
)


def benchmark():

    console.print()

    console.print(
        Panel.fit(
            DESCRIPTION,
            title="Code Review Benchmark"
        )
    )

    console.print()

    console.print(
        "[1] Base model"
    )

    console.print(
        "[2] LoRA adapter"
    )

    console.print()

    choice = input(
        "Select runtime: "
    ).strip()

    config = load_config()

    backend = config.get(
        "backend_url"
    )

    selected_lora = None

    runtime_name = "base"

    if choice == "2":

        response = requests.get(
            f"{backend}/v1/loras"
        )

        response.raise_for_status()

        data = response.json()

        loras = data["loras"]

        console.print()

        for i, lora in enumerate(
            loras,
            start=1
        ):

            console.print(
                f"[{i}] "
                f"{lora['name']}"
            )

        console.print()

        idx = int(
            input(
                "Select LoRA: "
            )
        ) - 1

        selected_lora = (
            loras[idx]["name"]
        )

        runtime_name = (
            selected_lora
        )

    def runtime_generate(
        prompt
    ):

        payload = {

            "prompt":
                prompt
        }

        if selected_lora:

            payload["lora"] = (
                selected_lora
            )

        response = requests.post(

            f"{backend}/v1/generate",

            json=payload,

            timeout=300
        )

        response.raise_for_status()

        return response.json()[
            "response"
        ]

    console.print()

    console.print(
        "[yellow]"
        "Running benchmark..."
        "[/yellow]"
    )

    console.print()

    result = run_code_review(

        runtime_generate,

        runtime_name=runtime_name
    )

    console.print()

    console.print(
        f"Tasks: "
        f"{result['tasks']}"
    )

    console.print(
        f"Passed: "
        f"{result['passed']}"
    )

    console.print(
        f"Failed: "
        f"{result['failed']}"
    )

    console.print(
        f"Accuracy: "
        f"{result['accuracy']:.2f}%"
    )

    console.print(
        f"Hallucination rate: "
        f"{result['hallucination_rate']:.2f}%"
    )

    console.print(
        f"Avg latency: "
        f"{result['avg_latency']:.2f}s"
    )

    console.print()

    console.print(
        "[green]"
        "Results saved"
        "[/green]"
    )