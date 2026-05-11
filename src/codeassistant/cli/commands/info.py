from rich.panel import Panel

from utils.console import console
from utils.config import load_config


def info():
    config = load_config()

    text = f"""
Model:
{config["model_path"]}

LoRA:
{config["lora_path"]}
"""

    console.print(
        Panel.fit(
            text,
            title="Lorariel"
        )
    )
