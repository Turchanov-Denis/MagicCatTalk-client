import torch

from codeassistant.inference.loader import (
    tokenizer,
    model,
    load_model
)

from utils.config import load_config


# if model is None:
#     load_model()


def generate(prompt: str):
    config = load_config()

    generation = config["generation"]

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    ).to("cuda")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=generation["max_new_tokens"],
            temperature=generation["temperature"],
            top_p=generation["top_p"]
        )

    return tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )