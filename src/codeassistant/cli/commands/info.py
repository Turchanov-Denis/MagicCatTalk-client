from rich.panel import Panel
from utils.console import console
from utils.config import load_config

def info():
    config = load_config()

    # Проверка на пустой конфиг или отсутствие путей
    if not config or not config.get("model_id"):
        console.print("[yellow]No configure,  use setup[/yellow]")
        return

    text = f"""
Model:
{config["model_id"]}

LoRA:
{config.get("lora_path") or "None"}
"""

    console.print(
        Panel.fit(
            text.strip(),
            title="Lorariel"
        )
    )
