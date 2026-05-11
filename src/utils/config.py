from pathlib import Path
import yaml

DEFAULT_CONFIG = {
    "model_path": None,
    "lora_path": None
}

BASE_DIR = Path(__file__).resolve().parents[3]
CONFIG_PATH = BASE_DIR / "configs" / "default.yaml"


def load_config():
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_PATH, "r") as f:
        data = yaml.safe_load(f) or {}

    return DEFAULT_CONFIG | data


def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)