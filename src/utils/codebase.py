from pathlib import Path

import ast

from rapidfuzz import process

from utils.logger import logger


SUPPORTED = [

    ".py",

    ".js",
    ".ts",
    ".tsx",

    ".java",

    ".cpp",
    ".c",
    ".hpp",

    ".cs",

    ".go",

    ".rs",

    ".php"
]


IGNORE_DIRS = [

    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".idea",
    ".vscode"
]


INTENTS = [

    "explain",
    "review",
    "fix",
    "analyze"
]


MAX_SYMBOL_LINES = 150


class SymbolVisitor(ast.NodeVisitor):

    def __init__(self):

        self.symbols = []

    def visit_FunctionDef(self, node):

        self.symbols.append({

            "type": "function",

            "name": node.name,

            "lineno": node.lineno,

            "end_lineno": node.end_lineno
        })

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):

        self.symbols.append({

            "type": "async_function",

            "name": node.name,

            "lineno": node.lineno,

            "end_lineno": node.end_lineno
        })

        self.generic_visit(node)

    def visit_ClassDef(self, node):

        self.symbols.append({

            "type": "class",

            "name": node.name,

            "lineno": node.lineno,

            "end_lineno": node.end_lineno
        })

        self.generic_visit(node)


def should_ignore(path: Path):

    parts = path.parts

    for part in parts:

        if part in IGNORE_DIRS:
            return True

    return False


def parse_file(path: Path):

    logger.info(
        f"Parsing file: {path}"
    )

    try:

        code = path.read_text(
            encoding="utf-8"
        )

    except Exception as e:

        logger.exception(
            f"Failed to read file: "
            f"{path} ({e})"
        )

        return []

    try:

        tree = ast.parse(code)

    except Exception as e:

        logger.exception(
            f"AST parse failed: "
            f"{path} ({e})"
        )

        return []

    visitor = SymbolVisitor()

    visitor.visit(tree)

    lines = code.splitlines()

    results = []

    for symbol in visitor.symbols:

        end = min(

            symbol["end_lineno"],

            symbol["lineno"]
            + MAX_SYMBOL_LINES
        )

        snippet = "\n".join(

            lines[
                symbol["lineno"] - 1:
                end
            ]
        )

        results.append({

            "file": str(path),

            "type": symbol["type"],

            "name": symbol["name"],

            "lineno": symbol["lineno"],

            "end_lineno": symbol["end_lineno"],

            "code": snippet
        })

    logger.info(
        f"Indexed "
        f"{len(results)} symbols "
        f"from {path}"
    )

    return results


def build_symbol_index():

    logger.info(
        "Building symbol index"
    )

    root = Path.cwd()

    index = {}

    for path in root.rglob("*"):

        if should_ignore(path):
            continue

        if path.suffix not in SUPPORTED:
            continue

        symbols = parse_file(path)

        for symbol in symbols:

            if symbol["name"] not in index:

                index[
                    symbol["name"]
                ] = []

            index[
                symbol["name"]
            ].append(symbol)

    logger.info(
        index.get("main")
    )

    return index


SYMBOL_INDEX = build_symbol_index()

def main():
    print("catGirl1")
def detect_intent(text: str):

    tokens = text.split()

    if not tokens:
        return None

    result = process.extractOne(

        tokens[0],

        INTENTS
    )

    if not result:
        return None

    intent, score, _ = result

    logger.info(
        f"Intent detected: "
        f"{intent} ({score})"
    )

    if score < 70:
        return None

    return intent


def extract_file(text: str):

    tokens = text.split()

    for token in tokens:

        if "." in token:

            for ext in SUPPORTED:

                if token.endswith(ext):

                    logger.info(
                        f"File mention detected: "
                        f"{token}"
                    )

                    return token

    return None


def extract_symbol(text: str):

    tokens = text.split()

    for token in tokens:

        if token in SYMBOL_INDEX:

            logger.info(
                f"Exact symbol match: "
                f"{token}"
            )

            return token

    best = None

    best_score = 0

    for token in tokens:

        result = process.extractOne(

            token,

            SYMBOL_INDEX.keys()
        )

        if not result:
            continue

        name, score, _ = result

        if score > best_score:

            best_score = score

            best = name

    if best_score < 75:

        logger.warning(
            "No symbol match found"
        )

        return None

    logger.info(
        f"Fuzzy symbol match: "
        f"{best} ({best_score})"
    )

    return best


def find_symbol(
        name: str,
        file: str = None
):

    results = SYMBOL_INDEX.get(
        name,
        []
    )

    if not results:

        logger.warning(
            f"Symbol not found: {name}"
        )

        return None

    if len(results) == 1:

        logger.info(
            f"Single symbol resolved: "
            f"{name}"
        )

        return results[0]

    if file:

        for result in results:

            if file in result["file"]:

                logger.info(
                    f"Resolved symbol "
                    f"{name} "
                    f"via file filter"
                )

                return result

    logger.warning(
        f"Ambiguous symbol: {name}"
    )

    return {

        "ambiguous": True,

        "matches": results
    }


def build_auto_context(text: str):

    logger.info(
        f"Building auto context "
        f"for: {text}"
    )

    intent = detect_intent(
        text
    )

    if not intent:

        logger.warning(
            "No intent detected"
        )

        return ""

    symbol = extract_symbol(
        text
    )

    if not symbol:

        logger.warning(
            "No symbol extracted"
        )

        return ""

    file = extract_file(
        text
    )

    found = find_symbol(

        symbol,

        file
    )

    if not found:

        logger.warning(
            "No symbol resolution result"
        )

        return ""

    if found.get("ambiguous"):

        logger.warning(
            f"Ambiguous symbol: "
            f"{symbol}"
        )

        return {

            "ambiguous": True,

            "matches": found["matches"]
        }

    logger.info(
        f"Resolved symbol: "
        f"{found['name']} "
        f"({found['file']})"
    )

    return {

        "ambiguous": False,

        "context": f"""
Intent:
{intent}

Symbol:
{found["name"]}

Type:
{found["type"]}

File:
{found["file"]}

Lines:
{found["lineno"]}-{found["end_lineno"]}

Code:

{found["code"]}
""".strip()
    }


