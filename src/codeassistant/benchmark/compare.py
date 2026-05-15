import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# -----------------------------
# GPU CHECK
# -----------------------------
assert torch.cuda.is_available()
print("GPU:", torch.cuda.get_device_name(0))

device = "cuda"

# -----------------------------
# CONFIG
# -----------------------------
base_model_name = "Qwen/Qwen2.5-Coder-3B-Instruct"
lora_path = "../../lora/codereview-lora"

# -----------------------------
# TOKENIZER
# -----------------------------
tokenizer = AutoTokenizer.from_pretrained(
    base_model_name,
    trust_remote_code=True
)

# -----------------------------
# BASE MODEL (GPU ONLY)
# -----------------------------
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    device_map={"": 0},
    torch_dtype=torch.float16,
    trust_remote_code=True
).eval()

# -----------------------------
# LORA MODEL (GPU ONLY)
# -----------------------------
lora_base = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    device_map={"": 0},
    torch_dtype=torch.float16,
    trust_remote_code=True
)

lora_model = PeftModel.from_pretrained(lora_base, lora_path).eval()

# -----------------------------
# TEST CODE
# -----------------------------
code = """
import os

def load_data(path):
    file = open(path, "r")
    data = file.read()
    file.close()
    return data
"""

prompt = f"""### Instruction:
You are a senior software engineer.

Perform a strict code review:
- find bugs
- bad practices
- performance issues
- suggest improvements

### Input:
{code}

### Response:
"""

# -----------------------------
# TOKENIZE (IMPORTANT FIX)
# -----------------------------
def get_inputs():
    inputs = tokenizer(prompt, return_tensors="pt")
    return {k: v.to(device) for k, v in inputs.items()}

# -----------------------------
# GENERATION
# -----------------------------
def generate(model):
    inputs = get_inputs()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=0.2,
            top_p=0.9
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# -----------------------------
# RUN COMPARISON
# -----------------------------
print("\n" + "="*60)
print("🔹 BASE MODEL OUTPUT")
print("="*60)
print(generate(base_model))

print("\n" + "="*60)
print("🔹 LORA MODEL OUTPUT")
print("="*60)
print(generate(lora_model))