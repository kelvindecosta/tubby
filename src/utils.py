"""This module defines functions for miscellaneous utilities"""

import asyncio


def clean_dict(dictionary: dict) -> dict:
    """Recursively removes `None` values from `dictionary`

    Args:
        dictionary (dict): subject dictionary

    Returns:
        dict: dictionary without None values
    """
    for key, value in list(dictionary.items()):
        if isinstance(value, dict):
            clean_dict(value)
        elif value is None:
            dictionary.pop(key)

    return dictionary


async def gather_dict(tasks: dict) -> dict:
    """Gathers dictionary of `tasks`

    Args:
        tasks (dict): subject tasks

    Returns:
        dict: mapping of tasks to results
    """

    async def mark(key, task):
        return key, await task

    return {
        key: result
        for key, result in await asyncio.gather(
            *(mark(key, task) for key, task in tasks.items())
        )
    }
