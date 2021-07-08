"""This module defines functions for managing inventory"""


import click
import locale


from .file import load_inventory, load_metadata, save_inventory
from .query import get_companions, get_furnishing_id, get_material_id
from .reset import create_inventory_schema
from .utils import clear_screen, get_relevant_emoji, terminal_menu


def manage_companions(metadata: dict, inventory: dict):
    """Manages companions

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
    """
    names = sorted([c["name"] for c in get_companions(metadata).values()])
    companions = inventory["companions"]

    choice = 0
    while True:
        clear_screen()
        print("Companions\n\n  Track whether or not the following are owned:\n")

        menu = terminal_menu(
            [
                f"""{"🟢" if str(get_furnishing_id(metadata, name)) in companions else "  "} {name}"""
                for name in names
            ],
            cursor_index=choice,
        )

        if (choice := menu.show()) is not None:
            c_id = str(get_furnishing_id(metadata, names[choice]))

            if c_id not in companions:
                companions[c_id] = True
            else:
                companions.pop(c_id)

            save_inventory(inventory)
        else:
            break


def manage_materials(metadata: dict, inventory: dict):
    """Manages materials

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
    """
    names = sorted(
        sorted([m for m in metadata["materials"]["map"]]), key=lambda m: m.split()[-1]
    )

    materials = inventory["materials"]

    if len(materials) == 0:
        materials.update({str(get_material_id(metadata, name)): 0 for name in names})

    choice = 0
    while True:
        clear_screen()
        print("Materials\n\n  Track how many of the following are owned:\n")

        menu = terminal_menu(
            [
                f"{materials[str(get_material_id(metadata, name))]:4d}×  {get_relevant_emoji(name)}  {name}"
                for name in names
            ],
            cursor_index=choice,
            show_search_hint=True,
        )

        if (choice := menu.show()) is not None:
            clear_screen()

            m_id = str(get_material_id(metadata, names[choice]))
            print(f"{names[choice]}:\n  Old: {materials[m_id]}")

            materials[m_id] = locale.atoi(input("  New: "))
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

    options = list(inventory.keys())

    choice = 0
    while True:
        clear_screen()
        print("Manage inventory of:\n")

        menu = terminal_menu(
            [f"  {get_relevant_emoji(o)}  {o}" for o in options],
            cursor_index=choice,
            show_search_hint=False,
        )

        if (choice := menu.show()) is not None:
            dict(companions=manage_companions, materials=manage_materials,)[
                options[choice]
            ](metadata, inventory)
        else:
            break
