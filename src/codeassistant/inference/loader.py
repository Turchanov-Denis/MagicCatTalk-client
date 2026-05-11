import torch

from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM

from peft import PeftModel

from utils.config import load_config

tokenizer = None
model = None


def load_model():
    global tokenizer
    global model

    config = load_config()

    model_path = config["model_path"]
    lora_path = config["lora_path"]

    tokenizer = AutoTokenizer.from_pretrained(
        model_path
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map="auto",
        torch_dtype=torch.float16
    )

    if lora_path:
        model = PeftModel.from_pretrained(
            model,
            lora_path
        )

    model.eval()

    return tokenizer, model