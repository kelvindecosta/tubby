"""This module defines functions for managing inventory"""


import click


from .file import load_inventory, load_metadata, save_inventory
from .query import get_companions, get_furnishing_id
from .reset import create_inventory_schema
from .utils import terminal_menu


def manage_companions(metadata: dict, inventory: dict):
    """Manages companions

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
    """
    names = sorted([c["name"] for c in get_companions(metadata).values()])

    while True:
        menu = terminal_menu(
            [
                f"""{'🟢' if str(get_furnishing_id(metadata, name)) in inventory["companions"] else '  '} {name}"""
                for name in names
            ],
            title="Companions:\n",
        )

        if (choice := menu.show()) is not None:
            c_id = str(get_furnishing_id(metadata, names[choice]))

            if c_id not in inventory["companions"]:
                inventory["companions"][c_id] = True
            else:
                inventory["companions"].pop(c_id)

            save_inventory(inventory)
        else:
            break


@click.command(options_metavar="[options]")
def manage():
    """Manages inventory"""

    if (metadata := load_metadata()) is None:
        print("Housing data not found!")
        exit(1)

    if (inventory := load_inventory()) is None:
        inventory = create_inventory_schema()

    options = sorted(list(inventory.keys()))

    menu = terminal_menu(
        options,
        title="Manage:\n",
    )

    while (choice := menu.show()) is not None:
        dict(companions=manage_companions)[options[choice]](metadata, inventory)