"""This module defines functions for managing inventory"""


import click


from .file import load_inventory, load_metadata, save_inventory
from .query import get_furnishing_crafting_materials, get_furnishing_crafting_recipe
from .reset import create_inventory_schema, update_inventory
from .utils import (
    bold,
    clear_screen,
    color,
    get_relevant_emoji,
    input_int,
    prompt_confirm,
    terminal_menu,
)


def manage_companions(metadata: dict, inventory: dict):
    """Manages companions

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
    """
    names = sorted(metadata["companions"])
    companions = inventory["companions"]

    choice = 0
    while True:
        clear_screen()

        menu = terminal_menu(
            [f"""{"🟢" if companions[name] else "🔴"} {name}""" for name in names],
            title="Companions\n\n  Track whether or not the following are owned:\n",
            cursor_index=choice,
        )

        if (choice := menu.show()) is not None:
            companions[names[choice]] = not companions[names[choice]]
            save_inventory(inventory)
        else:
            break


def manage_materials(metadata: dict, inventory: dict):
    """Manages materials

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
    """
    names = sorted(metadata["materials"], key=lambda m: m.split()[-1])
    materials = inventory["materials"]

    choice = 0
    while True:
        clear_screen()

        menu = terminal_menu(
            [
                f"{get_relevant_emoji(name)} {materials[name]:4d}×  {name}"
                for name in names
            ],
            title="Materials\n\n  Track how many of the following are owned:\n",
            cursor_index=choice,
        )

        if (choice := menu.show()) is not None:
            clear_screen()

            name = names[choice]
            print(f"{name}:\n\n  Old: {materials[name]}")

            if (new_amount := input_int("  New: ")) is None:
                input(bold(color("\nInvalid amount!", "red")))
                continue

            materials[name] = new_amount
            save_inventory(inventory)
        else:
            break


def manage_furnishings(metadata: dict, inventory: dict):
    """Manages furnishings

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
    """
    furnishings_md = metadata["furnishings"]

    names = sorted(
        sorted(
            sorted(furnishings_md.keys()),
            key=lambda name: furnishings_md[name].get("cost", 0),
            reverse=True,
        ),
        key=lambda name: furnishings_md[name].get("materials") is None,
    )
    furnishings = inventory["furnishings"]

    choice = 0
    while True:
        clear_screen()

        menu = terminal_menu(
            [
                f"""{("💰" if furnishings_md[name].get("cost") is not None else "🫖")} {f"📘{'🟢' if  furnishings[name]['blueprint'] else '🔴'}🔨{'🟢' if  furnishings[name]['crafted'] else '🔴'}" if furnishings_md[name].get("materials") is not None else " " * 8}  {furnishings[name]["owned"]:4d}×  {name}"""
                for name in names
            ],
            title="Furnishings\n\n  Legend:\n\n    🫖 = rewarded for trust rank / adeptal mirror quests / events\n    💰 = can be bought from realm depot / traveling salesman\n    📘 = blueprint owned\n    🔨 = crafted atleast once\n\n  Track the following:\n",
            cursor_index=choice,
        )

        if (choice := menu.show()) is not None:
            manage_furnishing(metadata, inventory, names[choice])
        else:
            break


def manage_furnishing(metadata: dict, inventory: dict, f_name: str):
    """Manages furnishing with `f_name`

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
        f_name (int): furnishing name
    """
    furnishing = inventory["furnishings"][f_name]
    recipe = get_furnishing_crafting_recipe(metadata, f_name, 1)

    title = f"""{f_name}:\n"""

    choice = 0
    while True:
        clear_screen()

        if furnishing.get("blueprint") is not None:
            options = ["blueprint", "crafted"]

            menu = terminal_menu(
                [
                    f"""{furnishing["owned"]:4d}× owned""",
                    *[f"""{"🟢" if furnishing[o] else "🔴"} {o}""" for o in options],
                ],
                title=f"{title}{recipe}",
                cursor_index=choice,
                show_search_hint=False,
            )

            choice = menu.show()

            if choice in [1, 2]:
                if choice == 2 and not furnishing["blueprint"]:
                    input(bold(color("\nCannot craft without blueprint!", "red")))
                elif choice == 1 and furnishing["crafted"]:
                    input(
                        bold(
                            color(
                                "\nCannot set blueprint as not owned if already crafted!",
                                "red",
                            )
                        )
                    )
                else:
                    if choice == 2 and not furnishing["crafted"]:
                        crafting_materials = get_furnishing_crafting_materials(
                            metadata, f_name, 1
                        )

                        if prompt_confirm(
                            "\nUse materials for crafting from inventory?"
                        ):
                            if all(
                                inventory["materials"][m_name] >= amount
                                for m_name, amount in crafting_materials.items()
                            ):
                                for m_name, amount in crafting_materials.items():
                                    inventory["materials"][m_name] -= amount
                            else:
                                input(
                                    bold(
                                        color(
                                            "\nNot enough materials for crafting!",
                                            "red",
                                        )
                                    )
                                )
                                continue

                        if prompt_confirm(
                            "Add crafted furnishing to inventory amount?"
                        ):
                            furnishing["owned"] += 1

                    furnishing[options[choice - 1]] = not furnishing[
                        options[choice - 1]
                    ]
                    save_inventory(inventory)
        else:
            choice = None

        if furnishing.get("blueprint") is None or choice == 0:
            clear_screen()

            print(title)
            print(f"""  Old: {furnishing["owned"]}""")

            if (new_amount := input_int("  New: ")) is None:
                input(bold(color("\nInvalid amount!", "red")))
                if choice == 0:
                    continue
                else:
                    break

            num_crafted = new_amount - furnishing["owned"]

            if num_crafted > 0 and furnishing.get("blueprint"):
                crafting_materials = get_furnishing_crafting_materials(
                    metadata, f_name, num_crafted
                )
                print(get_furnishing_crafting_recipe(metadata, f_name, num_crafted))

                if prompt_confirm("Use materials for crafting from inventory?"):
                    if all(
                        inventory["materials"][m_name] >= amount
                        for m_name, amount in crafting_materials.items()
                    ):
                        for m_name, amount in crafting_materials.items():
                            inventory["materials"][m_name] -= amount
                        furnishing["crafted"] = True
                    else:
                        input(
                            bold(
                                color(
                                    "\nNot enough materials for crafting!",
                                    "red",
                                )
                            )
                        )
                        continue

            furnishing["owned"] += num_crafted
            save_inventory(inventory)

        if choice is None:
            break


@click.command(options_metavar="[options]")
def manage():
    """Manages inventory"""

    if (metadata := load_metadata()) is None:
        print(bold(color("Housing data not found!", "red")))
        exit(1)

    if (inventory := load_inventory()) is None:
        inventory = create_inventory_schema()

    update_inventory(metadata, inventory)

    options = list(inventory.keys())

    choice = 0
    while True:
        clear_screen()

        menu = terminal_menu(
            [f"{get_relevant_emoji(o)} {o}" for o in options],
            title="Manage inventory of:\n",
            cursor_index=choice,
            show_search_hint=False,
        )

        if (choice := menu.show()) is not None:
            dict(
                companions=manage_companions,
                materials=manage_materials,
                furnishings=manage_furnishings,
            )[options[choice]](metadata, inventory)
        else:
            break

    clear_screen()
