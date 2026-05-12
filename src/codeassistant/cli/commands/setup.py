import typer
from pathlib import Path
from utils.console import console
from utils.config import load_config, save_config
from huggingface_hub import HfApi


def validate_hf_model(repo_id: str) -> bool:
    try:
        HfApi().model_info(repo_id)
        return True
    except Exception:
        return False


def setup():
    config = load_config() or {}

    console.print("\n[bold cyan]Lorariel Setup[/bold cyan]\n")

    if config.get("model_id"):
        console.print(f"[green]Current model:[/green] {config['model_id']}")
        console.print(f"[green]Current LoRA:[/green] {config.get('lora_path')}\n")

    console.print("Setup options:\n")
    console.print("[1] Set HuggingFace model")
    console.print("[2] Set LoRA path")
    console.print("[3] Exit\n")

    choice = typer.prompt("Select option", type=int)

    # -------------------------
    # MODEL
    # -------------------------
    if choice == 1:
        repo_id = typer.prompt(
            "Enter HF model (e.g. Qwen/Qwen2.5-Coder-3B)"
        ).strip()

        if not repo_id:
            console.print("[red]Empty model id[/red]")
            return

        if not validate_hf_model(repo_id):
            console.print("[red]Model not found on HuggingFace[/red]")
            if not typer.confirm("Continue anyway?"):
                return

        config["model_id"] = repo_id
        save_config(config)

        console.print("\n[green]Model updated[/green]\n")
        return

    # -------------------------
    # LORA
    # -------------------------
    if choice == 2:
        lora_path = typer.prompt(
            "Enter LoRA path (optional, empty = disable)"
        ).strip()

        if lora_path:
            lora_path = str(Path(lora_path).expanduser().resolve())

            if not Path(lora_path).exists():
                console.print("[red]LoRA path not found[/red]")
                return

            config["lora_path"] = lora_path
        else:
            config["lora_path"] = None

        save_config(config)

        console.print("\n[green]LoRA updated[/green]\n")
        return

    # -------------------------
    # EXIT
    # -------------------------
    return