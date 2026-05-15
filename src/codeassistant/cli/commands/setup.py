import requests
import typer

from rich.markdown import Markdown

from huggingface_hub import HfApi

from utils.console import console

from utils.config import (
    load_config,
    save_config
)


def validate_hf_model(
    repo_id: str
) -> bool:

    try:

        HfApi().model_info(repo_id)

        return True

    except Exception:

        return False


def fetch_loras(
    backend_url: str
):

    try:

        response = requests.get(
            f"{backend_url}/v1/loras",
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "loras",
            []
        )

    except Exception as e:

        console.print(
            f"[red]Failed to fetch LoRAs:[/red] {e}"
        )

        return []


def fetch_lora_info(
    backend_url: str,
    name: str
):

    try:

        response = requests.get(
            f"{backend_url}/v1/loras/{name}",
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        console.print(
            f"[red]Failed to fetch LoRA info:[/red] {e}"
        )

        return None


def lora_menu(
    config,
    backend_url,
    lora_name
):

    while True:

        console.print(
            f"\n[bold cyan]{lora_name}[/bold cyan]\n"
        )

        console.print(
            "[1] Description"
        )

        console.print(
            "[2] Install"
        )

        console.print(
            "[3] Back\n"
        )

        choice = typer.prompt(
            "Select option",
            type=int
        )

        # -------------------------
        # DESCRIPTION
        # -------------------------

        if choice == 1:

            info = fetch_lora_info(
                backend_url,
                lora_name
            )

            if not info:

                return

            readme = info.get(
                "readme"
            )

            if not readme:

                console.print(
                    "\n[yellow]README not found[/yellow]\n"
                )

                continue

            console.print()

            console.print(
                Markdown(readme)
            )

            console.print()

            continue

        # -------------------------
        # INSTALL
        # -------------------------

        if choice == 2:

            config["lora"] = lora_name

            save_config(config)

            console.print(
                f"\n[green]LoRA installed:[/green] "
                f"{lora_name}\n"
            )

            return

        # -------------------------
        # BACK
        # -------------------------

        if choice == 3:
            return


def setup():

    config = load_config() or {}

    backend_url = config.get(
        "backend_url",
        "http://localhost:8000"
    )

    console.print(
        "\n[bold cyan]Lorariel Setup[/bold cyan]\n"
    )

    if config.get("model_id"):

        console.print(
            f"[green]Current model:[/green] "
            f"{config['model_id']}"
        )

    console.print(
        f"[green]Current LoRA:[/green] "
        f"{config.get('lora')}\n"
    )

    console.print("Setup options:\n")

    console.print(
        "[1] Set HuggingFace model"
    )

    console.print(
        "[2] Select LoRA"
    )

    console.print(
        "[3] Remove LoRA"
    )

    console.print(
        "[4] Exit\n"
    )

    choice = typer.prompt(
        "Select option",
        type=int
    )

    # -------------------------
    # MODEL
    # -------------------------

    if choice == 1:

        repo_id = typer.prompt(
            "Enter HF model "
            "(e.g. Qwen/Qwen2.5-Coder-3B)"
        ).strip()

        if not repo_id:

            console.print(
                "[red]Empty model id[/red]"
            )

            return

        if not validate_hf_model(
            repo_id
        ):

            console.print(
                "[red]Model not found on HuggingFace[/red]"
            )

            if not typer.confirm(
                "Continue anyway?"
            ):
                return

        config["model_id"] = repo_id

        save_config(config)

        console.print(
            "\n[green]Model updated[/green]\n"
        )

        return

    # -------------------------
    # SELECT LORA
    # -------------------------

    if choice == 2:

        loras = fetch_loras(
            backend_url
        )

        if not loras:

            console.print(
                "\n[yellow]No compatible LoRAs found[/yellow]\n"
            )

            return

        console.print(
            "\n[bold]Available LoRAs:[/bold]\n"
        )

        for index, lora in enumerate(
            loras,
            start=1
        ):

            name = lora["name"]



            console.print(
                f"[{index}] "
                f"{name} "
            )

        console.print()

        selected = typer.prompt(
            "Select LoRA",
            type=int
        )

        if (
            selected < 1
            or selected > len(loras)
        ):

            console.print(
                "[red]Invalid selection[/red]"
            )

            return

        chosen_lora = loras[
            selected - 1
        ]["name"]

        lora_menu(
            config,
            backend_url,
            chosen_lora
        )

        return

    # -------------------------
    # REMOVE LORA
    # -------------------------

    if choice == 3:

        config["lora"] = None

        save_config(config)

        console.print(
            "\n[green]LoRA removed[/green]\n"
        )

        return

    return