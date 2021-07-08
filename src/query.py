"""This module defines functions for querying metadata and inventory"""


def get_companions(metdata: dict) -> dict:
    """Gets all companions

    Args:
        metdata (dict): housing metadata

    Returns:
        dict: mapping of companion ids to companions
    """
    furnishings = metdata["furnishings"]["list"]
    category = metdata["categories"]["map"]["Companion"]

    return {i: f for i, f in enumerate(furnishings) if f["category"] == category}


def get_furnishings(metdata: dict) -> dict:
    """Gets all furnishings

    Args:
        metdata (dict): housing metadata

    Returns:
        dict: mapping of furnishing ids to furnishings
    """
    furnishings = metdata["furnishings"]["list"]
    category = metdata["categories"]["map"]["Companion"]

    return {i: f for i, f in enumerate(furnishings) if f["category"] != category}


def get_furnishing_crafting_materials(
    metadata: dict, f_id: int, num_crafted: int
) -> dict:

    return (
        {m_id: amount * num_crafted for m_id, amount in crafting_materials.items()}
        if (
            crafting_materials := metadata["furnishings"]["list"][f_id].get("materials")
        )
        is not None
        else None
    )
