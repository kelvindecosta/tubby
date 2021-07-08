"""This module defines functions for miscellaneous utilities"""


import asyncio
import os
from typing import List


from simple_term_menu import TerminalMenu


def clear_screen():
    """Clears terminal screen"""
    if os.name == "nt":
        _ = os.system("cls")
    else:
        _ = os.system("clear")


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


def terminal_menu(
    options: List[str], show_search_hint: bool = True, **kwargs
) -> TerminalMenu:
    """Creates a terminal menu instance

    Args:
        options (List[str]): list of menu options
        show_search_hint (bool, optional): show search hint. Defaults to True.

    Returns:
        TerminalMenu: menu instancce
    """
    return TerminalMenu(
        options,
        menu_cursor_style=("fg_cyan", "bold"),
        clear_menu_on_exit=False,
        show_search_hint=show_search_hint,
        **kwargs,
    )


def get_relevant_emoji(text: str) -> str:
    """Returns relevant emoji for `text`

    Args:
        text (str): subject text

    Returns:
        str: emoji
    """
    if text == "companions":
        return "👤"
    elif text == "materials" or "Wood" in text or text == "Bamboo Segment":
        return "🪵 "
    elif "Chunk" in text:
        return "🪨 "
    elif "Dye" in text:
        return "🖌️ "
    elif text == "Fabric":
        return "🏳️ "
    elif text == "furnishings":
        return "🪑"
    elif text == "sets":
        return "🛋️ "
    else:
        return "  "