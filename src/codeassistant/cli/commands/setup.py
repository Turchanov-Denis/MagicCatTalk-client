import typer
from utils.console import console
from utils.config import load_config, save_config

def setup():
    # Если load_config вернул None, берем пустой словарь
    config = load_config() or {}

    console.print("\n[bold cyan]Lorariel Setup[/bold cyan]\n")

    if config.get("model_path"):
        console.print(f"[green]Current model:[/green] {config['model_path']}")
        console.print(f"[green]Current LoRA:[/green] {config.get('lora_path')}\n")

    console.print("Choose model source:\n")
    console.print("[1] Local path\n[2] HuggingFace\n[3] DeepSeek Coder\n[4] Exit\n")

    choice = typer.prompt("Select option", type=int)

    if choice == 1:
        model_path = typer.prompt("Enter local path")
    elif choice == 2:
        model_path = typer.prompt("Enter HF repo")
    elif choice == 3:
        model_path = "deepseek-ai/deepseek-coder-1.3b-instruct" # лучше полный путь
    else:
        return

    lora_path = typer.prompt("LoRA path (optional)", default="")

    # Обновляем словарь (теперь он точно существует)
    config.update({
        "model_path": model_path,
        "lora_path": lora_path if lora_path else None
    })

    save_config(config)
    console.print("\n[green]Saved successfully[/green]\n")
