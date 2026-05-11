from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).resolve().parents[4] / "configs" / "default.yaml"


def load_config():
    if not CONFIG_PATH.exists():
        return None

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    if not config.get("model_path") and not config.get("lora_path"):
        return None

    return config


def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)
