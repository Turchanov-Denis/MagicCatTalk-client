import typer

from utils.console import console
from utils.config import load_config, save_config


def setup():
    config = load_config()

    console.print("\n[bold cyan]Lorariel Setup[/bold cyan]\n")

    if config.get("model_path"):
        console.print(f"[green]Current model:[/green] {config['model_path']}")
        console.print(f"[green]Current LoRA:[/green] {config.get('lora_path')}\n")

    console.print("Choose model source:\n")
    console.print("[1] Local model path")
    console.print("[2] HuggingFace model")
    console.print("[3] DeepSeek Coder (preset)")
    console.print("[4] Exit\n")

    choice = typer.prompt("Select option", type=int)

    if choice == 1:
        model_path = typer.prompt("Enter local model path (e.g. model/deepseek-coder)")

    elif choice == 2:
        model_path = typer.prompt("Enter HuggingFace model (e.g. Qwen/Qwen2.5-Coder-3B-Instruct)")

    elif choice == 3:
        model_path = "model/deepseek-coder"

    elif choice == 4:
        return

    else:
        console.print("[red]Invalid option[/red]")
        return

    lora_path = typer.prompt(
        "LoRA path (optional)",
        default=""
    )

    config["model_path"] = model_path
    config["lora_path"] = lora_path if lora_path else None

    save_config(config)

    console.print("\n[green]Configuration saved successfully[/green]\n")