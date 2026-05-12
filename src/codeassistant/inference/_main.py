import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# -----------------------------
# GPU CHECK
# -----------------------------
assert torch.cuda.is_available()
print("GPU:", torch.cuda.get_device_name(0))

# -----------------------------
# MODEL
# -----------------------------
model_name = "Qwen/Qwen2.5-Coder-3B-Instruct"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    trust_remote_code=True
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    quantization_config=bnb_config,
    trust_remote_code=True
)

model.eval()

# -----------------------------
# CODE
# -----------------------------
code = """
def load_data(path):
    file = open(path, "r")
    data = file.read()
    file.close()
    return data
"""

# -----------------------------
# MANUAL CHAT FORMAT (FIX)
# -----------------------------
prompt = f"""<|im_start|>user
You are a senior software engineer.

Perform strict code review:
- find bugs
- bad practices
- performance issues

Code:
{code}
<|im_end|>
<|im_start|>assistant
"""

# -----------------------------
# TOKENIZE (IMPORTANT FIX)
# -----------------------------
inputs = tokenizer(
    prompt,
    return_tensors="pt"
)

inputs = {k: v.to("cuda") for k, v in inputs.items()}

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