## MagicCat

This project was created as a diploma work.

Minimal local AI coding assistant for code generation, retrieval and project analysis.

```text
   /\_/\\
  ( o.o )
===/ * \===
  (_\_/_)
```




## Features

- custom LLM backend https://github.com/Turchanov-Denis/MagicCatTalk-server
- automatic code part search - codebase
- file mentions with `@file.py`
- code explanation and review
- long-term memory
- LoRA support

## Installation

### Clone repository

```bash
git clone https://github.com/Turchanov-Denis/MagicCatTalk-client
cd MagicCatTalk-client
```

### Install dependencies

```bash
uv sync

uv pip install -e .
```

## Run

```bash
magic
```
Then init will do its job
## License

MIT