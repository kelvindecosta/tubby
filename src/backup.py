"""This module defines functions for creating backups"""


import os
import json


import click


from .file import load_inventory, save_inventory
from .utils import bold, color, prompt_confirm


@click.command(options_metavar="[options]")
@click.argument("path", type=click.STRING, metavar="<path>")
@click.option(
    "-i", "--import", "export", flag_value=False, help="Import inventory from <path>"
)
@click.option(
    "-e", "--export", "export", flag_value=True, help="Export inventory to <path>"
)
def backup(path: str, export: bool):
    """Creates or loads inventory backup"""

    if export or os.path.isfile(path):
        if prompt_confirm(
            f"Are you sure you want to {'import inventory from' if not export else 'export inventory to'} '{path}'?"
        ):
            if not export:
                with open(path, "r") as file_pointer:
                    inventory = json.load(file_pointer)
                    save_inventory(inventory)

                    print(bold(color("Imported backup!", "green")))
            else:
                if (inventory := load_inventory()) is not None:
                    if not os.path.exists(path):
                        os.makedirs(os.path.dirname(path), exist_ok=True)

                    with open(path, "w") as file_pointer:
                        json.dump(inventory, file_pointer)

                    print(bold(color("Exported backup!", "green")))
                else:
                    print(bold(color("Could load inventory!", "red")))
    else:
        print(bold(color(f"Could not find path '{path}'", "red")))
