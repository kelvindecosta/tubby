"""This module defines functions for miscellaneous utilities"""


import asyncio
import locale
import os
from typing import List, Optional


from simple_term_menu import TerminalMenu
from sty import fg, ef, rs


def clear_screen():
    """Clears terminal screen"""
    if os.name == "nt":
        _ = os.system("cls")
    else:
        _ = os.system("clear")


def prompt_confirm(prompt: str) -> bool:
    """Prompt user for confirmation

    Args:
        prompt (str): question to user

    Returns:
        bool: confirmation
    """
    return len(confirm := input(f"{prompt} [y/N]: ")) > 0 and confirm.lower()[0] == "y"


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


def emoji(text: str) -> str:
    """Returns relevant emoji for `text`

    Args:
        text (str): subject text

    Returns:
        str: emoji
    """
    if text == "companions":
        return "👤"
    elif text == "materials" or "Wood" in text or text == "Bamboo Segment":
        return "🪵"
    elif "Chunk" in text:
        return "🪨"
    elif "Dye" in text:
        return "🎨"
    elif text == "Fabric":
        return "💮"
    elif text == "furnishings":
        return "🪑"
    elif text == "sets":
        return "🏡"
    elif text == "currency":
        return "💰"
    elif text == "mora":
        return "🪙"
    else:
        return "  "


def emoji_boolean(condition: bool) -> str:
    """Returns emoji depending on `condition`

    Args:
        condition (bool): subject condition

    Returns:
        str: emoji
    """
    return "🟢" if condition else "🔴"


def color(text: str, name: str) -> str:
    """Colorizes `text` with `name` color for terminal output

    Args:
        text (str): subject text
        name (str): name of color

    Returns:
        str: colorized text
    """
    return f"{fg(name)}{text}{fg.rs}"


def bold(text: str) -> str:
    """Emboldens `text` for terminal output

    Args:
        text (str): subject text

    Returns:
        str: bold text
    """
    return f"{ef.bold}{text}{rs.bold_dim}"


def italic(text: str) -> str:
    """Italicizes `text` for terminal output

    Args:
        text (str): subject text

    Returns:
        str: italicized text
    """
    return f"{ef.italic}{text}{rs.italic}"


def input_int(prompt: str) -> Optional[int]:
    """Returns valid integer entered by user

    Args:
        prompt (str): message to user

    Returns:
        Optional[int]: valid integer
    """
    result = input(prompt)

    try:
        result = locale.atoi(result)
    except ValueError:
        return None

    return result


def multiply_values(dictionary: dict, num: int) -> dict:
    """Multiplies each value in `dictionary` by `num`

    Args:
        dictionary (dict): subject dictionary
        num (int): multiplier

    Returns:
        dict: mapping of keys to values multiplied by multiplier
    """
    return (
        {key: value * num for key, value in dictionary.items()}
        if dictionary is not None
        else {}
    )


def update_greater(dictionary: dict, key: str, num: int):
    """Maps `key` in `dictionary` to `num` if greater

    Args:
        dictionary (dict): subject dictionary
        key (str): subject key
        num (int): new value
    """
    if key not in dictionary or dictionary[key] < num:
        dictionary[key] = num
