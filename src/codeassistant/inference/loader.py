import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from huggingface_hub import HfApi
from rich.prompt import Confirm

from utils.config import load_config

tokenizer = None
model = None


def load_model():
    global tokenizer, model

    config = load_config()

    model_id = config.get("model_id")
    lora_path = config.get("lora_path")

    if not model_id:
        raise ValueError("model_id (HF repo id) is not set")

    if "\\" in model_id or ":" in model_id:
        raise ValueError(f"Invalid HF repo id: {model_id}")

    api = HfApi()

    # -------------------------
    # CHECK MODEL EXISTS
    # -------------------------
    try:
        api.model_info(model_id)
    except Exception:
        print(f"\nModel not found on HuggingFace: {model_id}")

        if not Confirm.ask("Download it anyway from HuggingFace?"):
            raise RuntimeError("Model loading aborted by user")

        print("Downloading model...\n")

    # -------------------------
    # TOKENIZER
    # -------------------------
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # -------------------------
    # MODEL
    # -------------------------
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        torch_dtype=dtype
    )

    # -------------------------
    # LORA (optional)
    # -------------------------
    if lora_path:
        from pathlib import Path

        lora_path = Path(lora_path).expanduser().resolve()

        if not lora_path.exists():
            raise FileNotFoundError(f"LoRA path not found: {lora_path}")

        model = PeftModel.from_pretrained(
            model,
            str(lora_path),
            is_trainable=False
        )

    model.eval()

    return tokenizer, model