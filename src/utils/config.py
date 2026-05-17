from pathlib import Path
import yaml

LOR_DIR = Path.cwd() / ".lor"
CONFIG_PATH = LOR_DIR / "config.yaml"


def load_config():
    if not CONFIG_PATH.exists():
        return {}

    try:

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:

            config = yaml.safe_load(f) or {}

    except Exception:

        return {}

    if not config.get("lora"):
        config["lora"] = None

    return config


def save_config(config: dict):
    LOR_DIR.mkdir(parents=True, exist_ok=True)

    if not config.get("lora"):
        config["lora"] = None

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)


def load_user_config(path):

    file = open(path)

    data = file.read()

    config = eval(data)

    return config["settings"]
