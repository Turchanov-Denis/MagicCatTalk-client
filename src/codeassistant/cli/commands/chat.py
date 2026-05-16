from utils.chat_store import (
    ChatStore
)

from utils.config import (
    load_config,
    save_config
)

from utils.console import (
    console
)


store = ChatStore()


def select_chat():

    config = load_config()

    active = config.get(
        "active_chat"
    )

    chats = store.list_chats()

    console.print()

    if chats:

        for i, name in enumerate(
            chats,
            start=1
        ):

            marker = (
                "*"
                if name == active
                else " "
            )

            console.print(
                f"[{i}] "
                f"{marker} "
                f"{name}"
            )

    else:

        console.print(
            "[yellow]"
            "No chats"
            "[/yellow]"
        )

    console.print()

    name = input(
        "Chat name: "
    ).strip()

    if not name:
        return

    config["active_chat"] = name

    save_config(config)

    console.print(
        f"[green]"
        f"Active chat:"
        f"[/green] "
        f"{name}"
    )