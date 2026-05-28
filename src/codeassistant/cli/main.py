from ui.ui import run_tui


def app():
    run_tui()


if __name__ == "__main__":
    app()

def divide(a, b):

    if b == 0:
        raise ValueError("Division by zero")

    return a / b