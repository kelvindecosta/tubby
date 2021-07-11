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
