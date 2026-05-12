from datasets import load_dataset
from rich.panel import Panel

from codeassistant.cli.commands.train import train
from utils.config import load_config
from utils.console import console
from codeassistant.cli.commands.setup import setup
from codeassistant.cli.commands.info import info
from codeassistant.cli.commands.prompt import prompt
from codeassistant.inference.inference_engine import runtime

items = ['setup', 'prompt', 'chat history', 'benchmark', 'train lora', 'exit']

def print_home():
    config = load_config()
    model_name = config.get("model_id", "Not set")
    lora_name = config.get("lora_path", "Not set")
    menu = '\n'.join(f'[{i + 1}] {item}' for i, item in enumerate(items))

    content = f"[bold blue]Model:[/bold blue] {model_name}\n\n"+ f"[bold blue]Lora:[/bold blue] {lora_name}\n\n" + menu

    console.print(
        Panel.fit(
            content,
            title="Lorariel",
            padding=(0, 2)
        )
    )


def print_home_briefly():
    menu_line = "  ".join(f"[{i + 1}] {item}" for i, item in enumerate(items))

    console.print(Panel.fit(menu_line, title="AI Assistant"))


def parse_prompt_input(raw: str):
    parts = raw.split()

    text = []
    file = None
    lines = None

    i = 0
    while i < len(parts):

        if parts[i] == "-f":
            file = parts[i + 1]
            i += 2
            continue

        if parts[i] == "-s":
            start = parts[i + 1]
            end = parts[i + 2]
            lines = f"{start}:{end}"
            i += 3
            continue

        text.append(parts[i])
        i += 1

    return " ".join(text), file, lines


def run_tui():
    print_home()

    while True:
        cmd = input("› ").strip()

        if cmd in ["6", "exit", "quit"]:
            break

        if cmd in ["1", "setup"]:
            setup()
            print_home_briefly()
            continue

        if cmd in ["2", "prompt"]:
            console.print("""
            [bold green]Prompt mode[/bold green]

            Example:
            › explain this code -f main.py -s 20 30

            Flags:
            -f file path
            -s start end (lines)

            Type 'exit' to leave prompt mode
            """)

            while True:
                raw = input("› ").strip()

                if raw.lower() in ["exit"]:
                    print_home_briefly()
                    break

                if not raw:
                    continue

                text, file, lines = parse_prompt_input(raw)

                prompt(
                    text=text,
                    file=file,
                    lines=lines
                )

            continue

        if cmd in ["3","chat"]:
            name = input("Chat name: ").strip()

            if not name:
                print("Empty chat name")
                continue

            runtime.load_chat(name)

            console.print(f"\n[green]Switched to chat:[/green] {name}\n")
            print_home_briefly()
            continue

        if cmd in ["4", 'benchmark']:
            print('benchmark')
            continue

        if cmd in ["5", "train"]:
            if cmd in ["5", "train"]:
                config = load_config()

                console.print("\n[bold green]Code Review Train Mode[/bold green]\n")

                # =========================
                # MODEL
                # =========================
                model = input(f"""
            Model (HuggingFace name)

            👉 Example:
            Qwen/Qwen2.5-Coder-3B-Instruct
            meta-llama/Llama-3-8b-instruct

            👉 Press Enter to use config:
            [{config.get("model_id")}]

            › """).strip() or config.get("model_id")

                # =========================
                # DATASET
                # =========================
                dataset_name = input("""
            Dataset (HuggingFace dataset)

            👉 Example:
            ronantakizawa/github-codereview
            openai/openai_humaneval

            👉 Paste dataset name or URL:

            › """).strip()

                if not dataset_name:
                    console.print("[red]Dataset is required[/red]")
                    continue

                # =========================
                # LOAD DATASET (only for schema)
                # =========================
                dataset = load_dataset(dataset_name)["train"]

                # =========================
                # SHOW REAL COLUMNS
                # =========================
                columns = list(dataset.column_names)

                console.print("\n[bold cyan]Available columns:[/bold cyan]")
                console.print(columns)

                # (optional nicer view)
                console.print("\n[dim]Index mapping:[/dim]")
                for i, col in enumerate(columns):
                    console.print(f"[{i}] {col}")

                # =========================
                # INPUT COLUMNS
                # =========================
                input_col = input("""
                Input column (name or index):
                › """).strip()

                if input_col.isdigit():
                    input_col = columns[int(input_col)]

                if not input_col:
                    input_col = "before_code"

                output_col = input("""
                Output column (name or index):
                › """).strip()

                if output_col.isdigit():
                    output_col = columns[int(output_col)]

                if not output_col:
                    output_col = "reviewer_comment"

                context_col = input("""
                Context column (optional, name or index):
                › """).strip()

                if context_col:
                    if context_col.isdigit():
                        context_col = columns[int(context_col)]
                else:
                    context_col = None

                # =========================
                # SYSTEM PROMPT
                # =========================
                default_prompt = """You are a senior software engineer.

            Perform strict code review focusing on:
            - bugs
            - performance issues
            - security issues
            - bad practices
            """

                system_prompt = input(f"""
            System prompt

            👉 Press Enter to use default:

            {default_prompt}

            › """).strip() or default_prompt

                # =========================
                # OUTPUT DIR
                # =========================
                output_dir = input(f"""
            Output directory

            👉 Example:
            lora/codereview-v1
            lora/my-review-model

            👉 Press Enter = auto:

            /lora/{model.split('/')[-1]}

            › """).strip() or f"/lora/{model.split('/')[-1]}"

                # =========================
                # TRAIN START
                # =========================
                train({
                    "model": model,
                    "dataset": dataset_name,
                    "input_col": input_col,
                    "output_col": output_col,
                    "context_col": context_col if context_col else None,
                    "system_prompt": system_prompt,
                    "output_dir": output_dir,
                    "mode": "instruction",
                    "dataset_size": 5000,
                    "training": {
                        "max_steps": 500
                    }
                })
            continue
        print("Unknown command:", cmd)
