"""This module defines functions for querying metadata and inventory"""

from typing import Optional


from .utils import get_relevant_emoji


def get_furnishing_crafting_materials(
    metadata: dict, f_name: str, num_crafted: int
) -> Optional[dict]:
    """Returns materials required for `num_crafted` `f_name` furnishings

    Args:
        metadata (dict): housing metadata
        f_name (str): furnishing name
        num_crafted (int): number of crafted furnishings

    Returns:
        dict: mapping of materials to amount
    """

    return (
        {m_name: amount * num_crafted for m_name, amount in crafting_materials.items()}
        if (crafting_materials := metadata["furnishings"][f_name].get("materials"))
        is not None
        else None
    )


def get_furnishing_crafting_recipe(
    metadata: dict, f_name: str, num_crafted: int
) -> str:
    """Generates recipe string for `num_crafted` `fname` furnishings

    Args:
        metadata (dict): housing metadata
        f_name (str): furnishing name
        num_crafted (int): number of crafted furnishings

    Returns:
        str: recipe
    """
    if (
        materials := get_furnishing_crafting_materials(metadata, f_name, num_crafted)
    ) is not None:
        recipe = [
            f"  {get_relevant_emoji(m_name)} {amount:4d}×  {m_name}"
            for m_name, amount in materials.items()
        ]
        recipe = "\n".join(recipe)
        return f"\n Materials (for {num_crafted:4d}×):\n\n{recipe}\n"

    return ""
