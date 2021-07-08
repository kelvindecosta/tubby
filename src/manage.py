"""This module defines functions for managing inventory"""


import click


from .file import load_inventory, load_metadata, save_inventory
from .query import get_companions, get_furnishings, get_furnishing_crafting_materials
from .reset import create_inventory_schema
from .utils import (
    bold,
    clear_screen,
    color,
    get_relevant_emoji,
    input_int,
    terminal_menu,
)


def manage_companions(metadata: dict, inventory: dict):
    """Manages companions

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
    """
    companions_md = dict(
        sorted(get_companions(metadata).items(), key=lambda item: item[1]["name"])
    )
    companions = inventory["companions"]

    choice = 0
    while True:
        clear_screen()

        menu = terminal_menu(
            [
                f"""{"🟢" if str(i) in companions else "🔴"} {c["name"]}"""
                for i, c in companions_md.items()
            ],
            title="Companions\n\n  Track whether or not the following are owned:\n",
            cursor_index=choice,
        )

        if (choice := menu.show()) is not None:
            c_id = str(list(companions_md.keys())[choice])

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
    materials_md = dict(
        sorted(
            enumerate(metadata["materials"]["list"]),
            key=lambda item: item[1].split()[-1],
        )
    )
    materials = inventory["materials"]

    if len(materials) == 0:
        materials.update({str(i): 0 for i in materials_md})

    choice = 0
    while True:
        clear_screen()

        menu = terminal_menu(
            [
                f"{materials[str(i)]:4d}×  {get_relevant_emoji(m)}  {m}"
                for i, m in materials_md.items()
            ],
            title="Materials\n\n  Track how many of the following are owned:\n",
            cursor_index=choice,
        )

        if (choice := menu.show()) is not None:
            clear_screen()

            m_id = str(list(materials_md.keys())[choice])
            print(f"{materials_md[int(m_id)]}:\n\n  Old: {materials[m_id]}")

            if (new_amount := input_int("  New: ")) is None:
                input(bold(color("\nInvalid amount!", "red")))
                continue

            materials[m_id] = new_amount
            save_inventory(inventory)
        else:
            break


def manage_furnishings(metadata: dict, inventory: dict):
    """Manages furnishings

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
    """
    furnishings_md = dict(
        sorted(get_furnishings(metadata).items(), key=lambda item: item[1]["name"])
    )
    furnishings_md = dict(
        sorted(
            furnishings_md.items(),
            key=lambda item: item[1].get("cost") is None,
        )
    )
    furnishings_md = dict(
        sorted(
            furnishings_md.items(),
            key=lambda item: item[1].get("materials") is None,
        )
    )
    furnishings = inventory["furnishings"]

    if len(furnishings) == 0:
        furnishings.update(
            {
                str(i): dict(owned=0)
                if f.get("materials") is None
                else dict(owned=0, blueprint=False, crafted=False)
                for i, f in furnishings_md.items()
            }
        )

    choice = 0
    while True:
        clear_screen()

        menu = terminal_menu(
            [
                f"""{("💰        " if f.get("cost") is not None else "          ") if f.get("materials") is None else f"📘{'🟢' if  furnishings[str(i)]['blueprint'] else '🔴'}  🔨{'🟢' if  furnishings[str(i)]['crafted'] else '🔴'}"}  {furnishings[str(i)]["owned"]:4d}×  {f["name"]}"""
                for i, f in furnishings_md.items()
            ],
            title="Furnishings\n\n  Key:\n\n    💰 = purchaseable\n    📘 = blueprint owned\n    🔨 = crafted atleast once\n\n  Track the following:\n",
            cursor_index=choice,
        )

        if (choice := menu.show()) is not None:
            manage_furnishing(metadata, inventory, list(furnishings_md.keys())[choice])
        else:
            break


def manage_furnishing(metadata: dict, inventory: dict, f_id: int):
    """Manages furnishing with `f_id`

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
        f_id (int): furnishing id
    """
    furnishing = inventory["furnishings"][str(f_id)]

    title = f"""{metadata["furnishings"]["list"][f_id]["name"]}:\n"""

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
                title=title,
                cursor_index=choice,
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
                            metadata, f_id, 1
                        )
                        print("\nRequired crafting materials:\n")
                        print(
                            *[
                                f"{amount:4d}×  {get_relevant_emoji(name)}  {name}"
                                for m_id, amount in crafting_materials.items()
                                if (name := metadata["materials"]["list"][int(m_id)])
                            ],
                            sep="\n",
                        )

                        if (
                            len(
                                (
                                    deduct := input(
                                        "\nUse materials for crafting from inventory? [y/N]: "
                                    )
                                )
                            )
                            > 0
                            and deduct.lower()[0] == "y"
                        ):
                            if all(
                                inventory["materials"][str(m_id)] >= amount
                                for m_id, amount in crafting_materials.items()
                            ):
                                for m_id, amount in crafting_materials.items():
                                    inventory["materials"][str(m_id)] -= amount
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

                        if (
                            len(
                                (
                                    deduct := input(
                                        "\nAdd crafted furnishing to inventory amount? [y/N]: "
                                    )
                                )
                            )
                            > 0
                            and deduct.lower()[0] == "y"
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
                continue

            num_crafted = new_amount - furnishing["owned"]

            if num_crafted > 0 and furnishing.get("blueprint"):
                crafting_materials = get_furnishing_crafting_materials(
                    metadata, f_id, num_crafted
                )
                print(f"\nRequired crafting materials for {num_crafted} furnishings:\n")
                print(
                    *[
                        f"{amount:4d}×  {get_relevant_emoji(name)}  {name}"
                        for m_id, amount in crafting_materials.items()
                        if (name := metadata["materials"]["list"][int(m_id)])
                    ],
                    sep="\n",
                )

                if (
                    len(
                        (
                            deduct := input(
                                "\nUse materials for crafting from inventory? [y/N]: "
                            )
                        )
                    )
                    > 0
                    and deduct.lower()[0] == "y"
                ):
                    if all(
                        inventory["materials"][str(m_id)] >= amount
                        for m_id, amount in crafting_materials.items()
                    ):
                        for m_id, amount in crafting_materials.items():
                            inventory["materials"][str(m_id)] -= amount
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
        print("Housing data not found!")
        exit(1)

    if (inventory := load_inventory()) is None:
        inventory = create_inventory_schema()

    options = list(inventory.keys())

    choice = 0
    while True:
        clear_screen()

        menu = terminal_menu(
            [f"{get_relevant_emoji(o)}  {o}" for o in options],
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
