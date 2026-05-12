import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from huggingface_hub import HfApi
from rich.prompt import Confirm

from utils.config import load_config
from utils.chat_store import ChatStore


class ModelRuntime:
    def __init__(self):
        # model state
        self._model = None
        self._tokenizer = None
        self._model_id = None
        self._lora_path = None
        self._lora_active = False

        # chat state
        self._chat_store = ChatStore()
        self._chat_name = "default"
        self._history = self._chat_store.load(self._chat_name)

    # -------------------------
    # CHAT
    # -------------------------
    def load_chat(self, name: str):
        self._chat_name = name
        self._history = self._chat_store.load(name)

    def save_chat(self):
        self._chat_store.save(self._chat_name, self._history)

    def get_history(self):
        return self._history

    # -------------------------
    # MODEL LOAD
    # -------------------------
    def load(self, model_id=None, lora_path=None):
        config = load_config()

        model_id = model_id or config.get("model_id")
        lora_path = lora_path or config.get("lora_path")

        if not model_id:
            raise ValueError("model_id is not set")

        model_id = model_id.replace("\\", "/")

        # check HF model
        try:
            HfApi().model_info(model_id)
        except Exception:
            print(f"\nModel not found: {model_id}")
            if not Confirm.ask("Download anyway?"):
                raise RuntimeError("Aborted")

        # tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_id)

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # model
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype=dtype
        )

        # LoRA
        self._lora_active = False
        if lora_path:
            model = PeftModel.from_pretrained(
                model,
                lora_path,
                is_trainable=False
            )
            self._lora_active = True

        model.eval()

        # store
        self._model = model
        self._tokenizer = tokenizer
        self._model_id = model_id
        self._lora_path = lora_path

    # -------------------------
    # ENSURE
    # -------------------------
    def ensure(self):
        if self._model is None or self._tokenizer is None:
            self.load()

    # -------------------------
    # SYNC CONFIG
    # -------------------------
    def sync(self):
        config = load_config()

        model_id = config.get("model_id")
        lora_path = config.get("lora_path")

        if not model_id:
            return

        model_id = model_id.replace("\\", "/")

        if model_id != self._model_id or lora_path != self._lora_path:
            print(f"\n🔄 Switching model → {model_id}\n")
            self._model = None
            self._tokenizer = None
            self.load(model_id, lora_path)

    # -------------------------
    # GENERATE
    # -------------------------
    def generate(self, prompt: str):
        self.ensure()
        self.sync()

        config = load_config()
        gen = config.get("generation", {})

        max_new_tokens = gen.get("max_new_tokens", 512)
        temperature = gen.get("temperature", 0.2)
        top_p = gen.get("top_p", 0.95)

        tokenizer = self._tokenizer
        model = self._model

        device = next(model.parameters()).device

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                eos_token_id=tokenizer.eos_token_id
            )

        input_len = inputs["input_ids"].shape[1]
        generated = outputs[0][input_len:]

        result = tokenizer.decode(
            generated,
            skip_special_tokens=True
        )

        # -------------------------
        # CHAT MEMORY
        # -------------------------
        self._history.append({
            "role": "user",
            "content": prompt
        })

        self._history.append({
            "role": "assistant",
            "content": result
        })

        self.save_chat()

        return result

    # -------------------------
    # INFO
    # -------------------------
    def info(self):
        return {
            "model_id": self._model_id,
            "lora_path": self._lora_path,
            "lora_active": self._lora_active,
            "chat": self._chat_name,
            "history_len": len(self._history),
            "device": str(next(self._model.parameters()).device) if self._model else None
        }


# singleton
runtime = ModelRuntime()