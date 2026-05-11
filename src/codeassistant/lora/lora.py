import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# -----------------------------
# MODEL
# -----------------------------
base_model = "Qwen/Qwen2.5-Coder-3B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(base_model)

model = AutoModelForCausalLM.from_pretrained(
    base_model,
    device_map="auto",
    torch_dtype=torch.float16
)

# 👉 подключаем LoRA
model = PeftModel.from_pretrained(model, "../../../lora/codereview-lora")

model.eval()

# -----------------------------
# TEST CODE
# -----------------------------
code = """
def load_data(path):
    file = open(path, "r")
    data = file.read()
    file.close()
    return data
"""

prompt = f"""### Instruction:
You are a senior software engineer.

Perform strict code review.

### Input:
{code}

### Response:
"""

inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

# -----------------------------
# GENERATION
# -----------------------------
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        temperature=0.2,
        top_p=0.9
    )

print(tokenizer.decode(outputs[0], skip_special_tokens=True))