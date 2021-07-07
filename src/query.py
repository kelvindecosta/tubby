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


def get_furnishing_id(metdata: dict, name: str) -> int:
    """Get id for furnishing with `name`

    Args:
        metdata (dict): housing metadata
        name (str): furnishing name

    Returns:
        int: furnishing id
    """
    return metdata["furnishings"]["map"][name]