"""This module defines functions for querying metadata and inventory"""


from functools import reduce
from typing import List, Optional


from .utils import emoji, multiply_values


def get_crafting_recipe(materials: dict) -> Optional[List[str]]:
    """Returns formatted crafting recipe with `materials`

    Args:
        materials (dict): crafting materials

    Returns:
        Optional[List[str]]: recipe
    """
    return (
        [f"{emoji(name)} {amount:4d}×  {name}" for name, amount in materials.items()]
        if materials is not None and len(materials) > 0
        else None
    )


def get_placing_recipe(furnishings: dict) -> [List[str]]:
    """Returns formatted placing recipe with `furnishings`

    Args:
        furnishings (dict): placed furnishings

    Returns:
        [List[str]]: recipe
    """
    return [f"{amount:4d}×  {name}" for name, amount in furnishings.items()]


def get_materials_for_furnishings(metadata: dict, furnishings: dict) -> dict:
    """Returns materials required to craft `furnishings`

    Args:
        metadata (dict): housing metadata
        furnishings (dict): mapping of furnishings to count

    Returns:
        dict: mapping of materials to amount
    """
    return reduce(
        lambda materials, result: {
            **result,
            **{
                m_name: (0 if m_name not in result else result[m_name]) + amount
                for m_name, amount in materials.items()
            },
        },
        (
            multiply_values(
                metadata["furnishings"][f_name].get("materials"), num_crafted
            )
            for f_name, num_crafted in furnishings.items()
        ),
        {},
    )


def get_cost_of_items(metadata: dict, inventory: dict, items: dict) -> dict:
    """Returns cost of `items`

    Args:
        metadata (dict): housing metadata
        inventory (dict): user inventory
        items (dict): mapping of furnishings / sets names to amount required

    Returns:
        dict: mapping of types of cost to total
    """
    return reduce(
        lambda costs, result: {
            **result,
            **{
                cost_type: (0 if cost_type not in result else result[cost_type])
                + amount
                for cost_type, amount in costs.items()
            },
        },
        (
            (
                {
                    (
                        key := "currency" if "currency" in furnishing else "mora"
                    ): furnishing.get(key, 0)
                    * (1 if key == "currency" else 1000)
                    * (
                        (1 if not inventory["furnishings"][name]["blueprint"] else 0)
                        if furnishing.get("materials") is not None
                        else num_required
                    )
                }
            )
            if (furnishing := metadata["furnishings"].get(name)) is not None
            else {"currency": hset["currency"]}
            if "currency" in (hset := metadata["sets"][name])
            else {"mora": hset.get("mora", 0) * 1000}
            for name, num_required in items.items()
        ),
        {},
    )
