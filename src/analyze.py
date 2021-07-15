"""This module defines functions for analysing inventory"""


import click


from .file import load_inventory, load_metadata
from .query import get_crafting_recipe, get_cost_of_items, get_materials_for_furnishings
from .reset import create_inventory_schema, update_inventory
from .utils import (
    bold,
    clear_screen,
    color,
    emoji,
    emoji_boolean,
    multiply_values,
    terminal_menu,
    update_greater,
)


def perform_analysis(metadata: dict, inventory: dict) -> dict:
    """Analyses `inventory`

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory

    Returns:
        dict: analysis
    """
    furnishings = inventory["furnishings"]
    sets = inventory["sets"]

    analysis = {
        "materials": {
            "milestones": [
                "🪑📘🟢🔨🔴",
                "🪑🔨🔴    ",
                "🎁👤🟢📘🟢",
                "🎁👤🟢    ",
                "🏡📘🟢    ",
                "🏡        ",
                "🫖        ",
            ],
            "legend": [
                "for one of each furnishing whose blueprint is owned and hasn't been crafted yet",
                "for one of each furnishing that hasn't been crafted yet",
                "for largest count of each missing furnishing for all gift sets with atleast one gifting companion and whose blueprints are owned",
                "for largest count of each missing furnishing for all gift sets with atleast one gifting companion",
                "for largest count of each missing furnishing for all sets whose blueprints are owned",
                "for largest count of each missing furnishing for all sets",
                "for larger of largest count of each missing furnishing for all sets and one of each furnishing that hasn't been crafted yet",
            ],
        },
        "currency": {
            "milestones": [
                "🪑📘🔴        ",
                "🎁👤🟢📘🔴    ",
                "🎁👤🟢📘🟢🪑🔴",
                "🎁👤🟢🪑🔴    ",
                "🏡📘🔴        ",
                "🏡🪑🔴        ",
                "🫖            ",
            ],
            "legend": [
                "all missing blueprints for furnishings",
                "all missing blueprints for gift sets with atleast one gifting companion",
                "all missing furnishings (including blueprints) for  for all gift sets with atleast one gifting companion and whose blueprints are owned",
                "all missing furnishings (including blueprints) for  for all gift sets with atleast one gifting companion",
                "all missing blueprints for sets",
                "all missing furnishings (including blueprints) for all sets",
                "all missing blueprints for furnishings and sets, all missing furnishings for all sets and one of all other furnishings",
            ],
        },
        "furnishings": {},
        "sets": {},
    }

    materials_anal = analysis["materials"]
    materials_anal["results"] = [{} for _ in materials_anal["legend"]]

    currency_anal = analysis["currency"]
    currency_anal["results"] = [{} for _ in currency_anal["legend"]]

    furnishings_anal = analysis["furnishings"]

    for f_name, furnishing in furnishings.items():
        if (
            furnishing_blueprint := furnishing.get("blueprint")
        ) is not None and not furnishing.get("crafted"):
            materials_anal["results"][1][f_name] = 1
            materials_anal["results"][6][f_name] = 1

            if furnishing_blueprint:
                materials_anal["results"][0][f_name] = 1
            else:
                currency_anal["results"][0][f_name] = 1
                currency_anal["results"][6][f_name] = 1

            furnishings_anal[f_name] = 1

        elif furnishing_blueprint is None and furnishing["owned"] == 0:
            currency_anal["results"][6][f_name] = 1
            furnishings_anal[f_name] = 1

    for s_name, hset in sets.items():
        set_blueprint = hset["owned"]
        has_gifting_companions = "companions" in hset and not all(
            gifted
            for c_name, gifted in hset["companions"].items()
            if inventory["companions"][c_name]
        )

        if not set_blueprint:
            currency_anal["results"][4][s_name] = 1
            currency_anal["results"][6][s_name] = 1

            if has_gifting_companions:
                currency_anal["results"][1][s_name] = 1

        for f_name, num_required in metadata["sets"][s_name]["furnishings"].items():
            if (num_owned := furnishings[f_name]["owned"]) < num_required:
                num_missing = num_required - num_owned

                update_greater(materials_anal["results"][5], f_name, num_missing)
                update_greater(materials_anal["results"][6], f_name, num_missing)

                update_greater(furnishings_anal, f_name, num_missing)

                if (
                    furnishing_blueprint := furnishings[f_name].get("blueprint")
                ) is None:
                    update_greater(currency_anal["results"][5], f_name, num_missing)
                    update_greater(currency_anal["results"][6], f_name, num_missing)
                elif not furnishing_blueprint:
                    currency_anal["results"][5][f_name] = 1

                if has_gifting_companions:
                    update_greater(materials_anal["results"][3], f_name, num_missing)

                    if set_blueprint:
                        update_greater(
                            materials_anal["results"][2], f_name, num_missing
                        )

                        if furnishing_blueprint is None:
                            update_greater(
                                currency_anal["results"][2], f_name, num_missing
                            )
                        elif not furnishing_blueprint:
                            currency_anal["results"][2][f_name] = 1

                    if furnishing_blueprint is None:
                        update_greater(currency_anal["results"][3], f_name, num_missing)
                    elif not furnishing_blueprint:
                        currency_anal["results"][3][f_name] = 1

                if set_blueprint:
                    update_greater(materials_anal["results"][4], f_name, num_missing)

    materials_anal["results"] = list(
        map(
            lambda furnishings: get_materials_for_furnishings(metadata, furnishings),
            materials_anal["results"],
        )
    )

    currency_anal["results"] = list(
        map(
            lambda items: get_cost_of_items(metadata, items),
            currency_anal["results"],
        )
    )

    return analysis


def summarize_materials(metadata: dict, inventory: dict, analysis: dict):
    """Summarizes `analysis` of materials

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
        analysis (dict): useful statistics
    """
    materials_anal = analysis["materials"]

    results = materials_anal["results"]

    clear_screen()

    legend = "\n".join(
        f"""    {materials_anal["milestones"][i]} = {materials_anal["legend"][i]}"""
        for i in range(len(results))
    )

    print(f"Materials:\n\n  Legend:\n\n    💼         = in inventory\n{legend}")

    print(
        f"""\n │ {"Item":24} │ {"💼        "} │ {" │ ".join(f"{m}" for m in materials_anal["milestones"])} │\n ┼{'─' * 26}┼{"┼".join(f"{'─' * 12}" for i in range(len(results) + 1))}┼"""
    )

    print(
        "\n".join(
            f""" │ {emoji(name)}  {name:20} │ {(amount := inventory["materials"][name]):10d} │ {" │ ".join(color(f"{(required := r.get(name, 0)):10d}", "green" if amount >= required else "red") for r in results)} │"""
            for name in sorted(metadata["materials"], key=lambda m: m.split()[-1])
        )
    )

    input()


def summarize_currency(analysis: dict):
    """Summarizes `analysis` for currency

    Args:
        analysis (dict): useful statistics
    """
    currency_anal = analysis["currency"]

    results = currency_anal["results"]

    clear_screen()

    legend = "\n".join(
        f"""    {currency_anal["milestones"][i]} = {currency_anal["legend"][i]}"""
        for i in range(len(results))
    )

    print(f"Currency:\n\n  Legend:\n\n{legend}")

    print(
        f"""\n │ {"Type":14} │ {" │ ".join(f"{m}" for m in currency_anal["milestones"])} │\n ┼{'─' * 16}┼{"┼".join(f"{'─' * 16}" for i in range(len(results)))}┼"""
    )

    print(
        "\n".join(
            f""" │ {emoji(name)}  {name:10} │ {" │ ".join(f"{(required := r.get(name, 0)):14d}" for r in results)} │"""
            for name in ["currency", "mora"]
        )
    )

    input()


def summarize_furnishings(metadata: dict, inventory: dict, analysis: dict):
    """Summarizes `analysis` for furnishings

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
        analysis (dict): useful statistics
    """
    furnishings_md = metadata["furnishings"]
    furnishings = inventory["furnishings"]
    furnishings_anal = analysis["furnishings"]

    names = sorted(
        furnishings_anal.keys(),
        key=lambda name: (
            furnishings[name].get("blueprint") is None,
            furnishings[name].get("crafted", False),
            not furnishings[name].get("blueprint", False),
            furnishings_md[name].get("cost") is None,
            -(x := furnishings[name]["owned"]) / (furnishings_anal[name] + x),
            name,
        ),
    )

    choice = 0
    while True:
        clear_screen()

        menu = terminal_menu(
            [
                f"""{"💰" if furnishings_md[name].get("cost") is not None else "🫖"} {f"📘{emoji_boolean(furnishings[name]['blueprint'])}🔨{emoji_boolean(furnishings[name]['crafted'])}" if furnishings_md[name].get("materials") is not None else " " * 8}  ({(owned := furnishings[name]["owned"]):2d}/{furnishings_anal[name] + owned:2d})  {name}"""
                for name in names
            ],
            title="Furnishings\n\n  Legend:\n\n    🫖 = rewarded for trust rank / adeptal mirror quests / events\n    💰 = can be bought from realm depot / traveling salesman\n    📘 = blueprint owned\n    🔨 = crafted atleast once\n\n  Track the following:\n",
            cursor_index=choice,
        )

        if (choice := menu.show()) is not None:
            clear_screen()

            materials = metadata["furnishings"][(f_name := names[choice])].get(
                "materials"
            )

            recipe = (
                "\n".join(map(lambda x: f"  {x}", recipe))
                if (
                    recipe := get_crafting_recipe(
                        multiply_values(
                            materials, (num_missing := furnishings_anal[f_name])
                        )
                    )
                )
                is not None
                else None
            )

            recipe = (
                f"\n Materials:\n\n{recipe}\n"
                if (blueprint := furnishings[f_name].get("blueprint")) is not None
                else ""
            )

            cost_str = (
                f"\n Cost : {cost * (num_missing if not blueprint else 1):4d}"
                if (cost := furnishings_md[f_name].get("cost")) is not None
                else ""
            )

            print(f"{f_name}:\n\n {num_missing:4d}×  missing\n{recipe}{cost_str}")

            input()
        else:
            break


@click.command(options_metavar="[options]")
def analyze():
    """Performs analysis on inventory"""

    if (metadata := load_metadata()) is None:
        print(bold(color("Housing data not found!", "red")))
        exit(1)

    if (inventory := load_inventory()) is None:
        inventory = create_inventory_schema()

    update_inventory(metadata, inventory)

    analysis = perform_analysis(metadata, inventory)

    options = list(analysis.keys())

    choice = 0
    while True:
        clear_screen()

        menu = terminal_menu(
            [f"{emoji(o)} {o}" for o in options],
            title="Analyze:\n",
            cursor_index=choice,
            show_search_hint=False,
        )

        if (choice := menu.show()) is not None:
            dict(
                materials=lambda a: summarize_materials(metadata, inventory, a),
                currency=summarize_currency,
                furnishings=lambda a: summarize_furnishings(metadata, inventory, a),
            )[options[choice]](analysis)
        else:
            break

    clear_screen()
