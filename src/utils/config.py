from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "default.yaml"


def load_config():
    if not CONFIG_PATH.exists():
        return {}

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    except Exception:
        return {}

    if not config.get("lora_path"):
        config["lora_path"] = None

    return config


def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if config.get("model_id"):
        config["model_id"] = str(Path(config["model_id"]).expanduser())

    if not config.get("lora_path"):
        config["lora_path"] = None

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            config,
            f,
            sort_keys=False,
            allow_unicode=True
        )