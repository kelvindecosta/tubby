"""This module defines functions for analysing inventory"""


import click


from .file import load_inventory, load_metadata
from .query import get_materials_for_furnishings
from .reset import create_inventory_schema, update_inventory
from .utils import bold, clear_screen, color, emoji, terminal_menu, update_greater


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
    }

    materials_anal = analysis["materials"]
    materials_anal["results"] = [{} for _ in materials_anal["legend"]]

    for f_name, furnishing in furnishings.items():
        if (
            blueprint := furnishing.get("blueprint")
        ) is not None and not furnishing.get("crafted"):
            materials_anal["results"][1][f_name] = 1
            materials_anal["results"][6][f_name] = 1

            if blueprint:
                materials_anal["results"][0][f_name] = 1

    for s_name, hset in sets.items():
        blueprint = hset["owned"]
        has_gifting_companions = "companions" in hset and not all(
            gifted
            for c_name, gifted in hset["companions"].items()
            if inventory["companions"][c_name]
        )

        for f_name, num_required in metadata["sets"][s_name]["furnishings"].items():
            if (num_owned := furnishings[f_name]["owned"]) < num_required:
                num_missing = num_required - num_owned

                update_greater(materials_anal["results"][5], f_name, num_missing)
                update_greater(materials_anal["results"][6], f_name, num_missing)

                if has_gifting_companions:
                    update_greater(materials_anal["results"][3], f_name, num_missing)

                    if blueprint:
                        update_greater(
                            materials_anal["results"][2], f_name, num_missing
                        )

                if blueprint:
                    update_greater(materials_anal["results"][4], f_name, num_missing)

    materials_anal["results"] = list(
        map(
            lambda f: get_materials_for_furnishings(metadata, f),
            materials_anal["results"],
        )
    )

    return analysis


def analyze_materials(metadata: dict, inventory: dict, analysis: dict):
    """Displays `analysis` of `maaterials`

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

    print(f"Materials:\n\n  Legend:\n    💼         = in inventory\n{legend}")

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

    options = ["materials", "currency", "furnishings", "sets"]

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
            dict(materials=analyze_materials)[options[choice]](
                metadata, inventory, analysis
            )
        else:
            break

    clear_screen()
