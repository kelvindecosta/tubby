"""This module defines functions for miscellaneous utilities"""


import asyncio
from typing import List

from simple_term_menu import TerminalMenu


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


def terminal_menu(options: List[str], **kwargs) -> TerminalMenu:
    """Creates a terminal menu instance

    Args:
        options (List[str]): list of menu options

    Returns:
        TerminalMenu: menu instancce
    """
    return TerminalMenu(
        [f"{o:{n}}" for o in options if (n := max(map(lambda x: len(x), options)))],
        menu_cursor_style=("fg_cyan", "bold"),
        clear_menu_on_exit=False,
        clear_screen=True,
        **kwargs,
    )
