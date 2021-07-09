"""This module defines functions for querying metadata and inventory"""


def get_furnishing_crafting_materials(
    metadata: dict, f_name: str, num_crafted: int
) -> dict:
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
