"""This module defines functions for managing inventory"""


import click


from .file import load_inventory, load_metadata, save_inventory
from .query import get_crafting_recipe, get_placing_recipe, get_set_materials
from .reset import create_inventory_schema, update_inventory
from .utils import (
    bold,
    clear_screen,
    color,
    emoji,
    emoji_boolean,
    input_int,
    multiply_values,
    prompt_confirm,
    terminal_menu,
)


def manage_companions(metadata: dict, inventory: dict):
    """Manages companions

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
    """
    names = sorted(metadata["companions"].keys())
    companions = inventory["companions"]

    choice = 0
    while True:
        clear_screen()

        menu = terminal_menu(
            [f"{emoji_boolean(companions[name])} {name}" for name in names],
            title="Companions\n\n  Track whether or not the following are owned:\n",
            cursor_index=choice,
        )

        if (choice := menu.show()) is not None:
            c_name = names[choice]
            companions[c_name] = not companions[c_name]

            if not companions[c_name]:
                for s_name in metadata["companions"][c_name]["sets"]:
                    inventory["sets"][s_name][c_name] = False

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
            get_crafting_recipe({name: materials[name] for name in names}),
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
                f"""{"💰" if furnishings_md[name].get("cost") is not None else "🫖"} {f"📘{emoji_boolean(furnishings[name]['blueprint'])}🔨{emoji_boolean(furnishings[name]['crafted'])}" if furnishings_md[name].get("materials") is not None else " " * 8}  {furnishings[name]["owned"]:4d}×  {name}"""
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
    """Manages `f_name` furnishing

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
        f_name (int): furnishing name
    """
    furnishing = inventory["furnishings"][f_name]
    materials = metadata["furnishings"][f_name].get("materials")

    recipe = (
        "\n".join(map(lambda x: f"  {x}", recipe))
        if (recipe := get_crafting_recipe(materials)) is not None
        else None
    )

    title = f"{f_name}:\n"

    choice = 0
    while True:
        clear_screen()

        if (blueprint := furnishing.get("blueprint")) is not None:
            options = ["blueprint", "crafted"][: 2 if blueprint else 1]

            menu = terminal_menu(
                [
                    f"""{furnishing["owned"]:4d}× owned""",
                    *[f"{emoji_boolean(furnishing[o])} {o}" for o in options],
                ],
                title=f"{title}\n Materials:\n\n{recipe}\n",
                cursor_index=choice,
                show_search_hint=False,
            )

            choice = menu.show()

            if choice in [1, 2]:
                if (crafted := furnishing["crafted"]) and choice == 1:
                    input(
                        bold(
                            color(
                                "\nCannot set blueprint as not owned if already crafted!",
                                "red",
                            )
                        )
                    )
                else:
                    if choice == 2 and not crafted:
                        if prompt_confirm(
                            "\nConsume materials from inventory to craft furnishing?"
                        ):
                            if all(
                                inventory["materials"][m_name] >= amount
                                for m_name, amount in materials.items()
                            ):
                                for m_name, amount in materials.items():
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

        if blueprint is None or choice == 0:
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

            if num_crafted > 0 and blueprint:
                crafting_materials = multiply_values(materials, num_crafted)

                crafting_recipe = "\n".join(
                    map(lambda x: f"  {x}", get_crafting_recipe(crafting_materials))
                )

                print(f"\n Materials:\n\n{crafting_recipe}\n")

                if prompt_confirm(
                    f"Consume materials from inventory to craft {num_crafted:4d} furnishings?"
                ):
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


def manage_sets(metadata: dict, inventory: dict):
    """Manages sets

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
    """
    sets_md = metadata["sets"]
    names = sorted(
        sorted(sets_md.keys()), key=lambda name: sets_md[name].get("companions") is None
    )

    choice = 0
    while True:
        clear_screen()

        menu = terminal_menu(
            [
                f"""{"🎁" if sets_md[name].get("companions") is not None else "🏡"}{emoji_boolean(inventory["sets"][name]["owned"])}  {name}"""
                for name in names
            ],
            title="Sets\n\n  Legend:\n\n    🎁 = gift set\n    🏡 = furniture set\n\n  Track the following:\n",
            cursor_index=choice,
        )

        if (choice := menu.show()) is not None:
            manage_set(metadata, inventory, names[choice])
        else:
            break


def manage_set(metadata: dict, inventory: dict, s_name: str):
    """Manages `s_name` set

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
        s_name (str): set name
    """
    hset = inventory["sets"][s_name]
    furnishings = metadata["sets"][s_name].get("furnishings")

    placing_recipe = "\n".join(
        map(lambda x: f"     {x}", get_placing_recipe(furnishings))
    )
    placing_recipe = f"\n Furnishings:\n\n{placing_recipe}\n"

    crafting_recipe = "\n".join(
        map(
            lambda x: f"  {x}",
            crafting_recipe
            if (
                crafting_recipe := get_crafting_recipe(
                    dict(
                        sorted(
                            get_set_materials(metadata, s_name).items(),
                            key=lambda item: item[0].split()[-1],
                        )
                    )
                )
            )
            is not None
            else [],
        )
    )
    crafting_recipe = (
        f"\n Materials:\n\n{crafting_recipe}\n" if len(crafting_recipe) > 0 else ""
    )

    companions = hset.get("companions")

    choice = 0
    while True:
        clear_screen()

        owned = hset["owned"]

        companion_names = (
            [c_name for c_name in companions if inventory["companions"][c_name]]
            if companions is not None
            and owned
            and all(
                amount <= inventory["furnishings"][f_name]["owned"]
                for f_name, amount in furnishings.items()
            )
            else []
        )

        menu = terminal_menu(
            [
                f"""{emoji_boolean(owned)} blueprint""",
                *[
                    f"""{emoji_boolean(companions[c_name])} 🎁 {c_name}"""
                    for c_name in companion_names
                ],
            ],
            title=f"{s_name}:\n{placing_recipe}{crafting_recipe}",
            cursor_index=choice,
        )

        if (choice := menu.show()) is not None:
            if choice == 0:
                if any(companions[c_name] for c_name in companion_names) and owned:
                    input(
                        bold(
                            color(
                                "Cannot set blueprint as not owned if gifts already received!",
                                "red",
                            )
                        )
                    )
                    continue
                hset["owned"] = not hset["owned"]
            elif owned:
                companions[companion_names[choice - 1]] = not companions[
                    companion_names[choice - 1]
                ]
            else:
                continue
            save_inventory(inventory)
        else:
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
            [f"{emoji(o)} {o}" for o in options],
            title="Manage inventory of:\n",
            cursor_index=choice,
            show_search_hint=False,
        )

        if (choice := menu.show()) is not None:
            dict(
                companions=manage_companions,
                materials=manage_materials,
                furnishings=manage_furnishings,
                sets=manage_sets,
            )[options[choice]](metadata, inventory)
        else:
            break

    clear_screen()
