import asyncio
from bs4 import Tag
import json
import os
import re
from typing import Optional

from config import DATA_FILE


def clean_dict(dictionary: dict) -> dict:
    """Recursively removes `None` values from a `dictionary`

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
    """Gathers a dictionary of tasks

    Args:
        tasks (dict): dict of tasks to be gathered

    Returns:
        dict: dict of completed tasks
    """

    async def mark(key, task):
        return key, await task

    return {
        key: result
        for key, result in await asyncio.gather(
            *(mark(key, task) for key, task in tasks.items())
        )
    }


def load_data() -> Optional[dict]:
    """Loads data from local save

    Returns:
        Optional[dict]: saved local data
    """
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as fp:
            return json.load(fp)
    else:
        return None


def parse_int(text: str) -> int:
    """Safely parses an integer from `text`

    Args:
        text (str): subject text

    Returns:
        int: parsed integer
    """
    return int(re.sub(r",", "", text))


def parse_tag_text(tag: Tag) -> str:
    """Safely parses the text in a `tag`

    Args:
        tag (Tag): subject tag

    Returns:
        str: parsed text
    """
    return tag.text.strip()


def save_data(data: dict):
    """Saves `data` to file

    Args:
        data (dict): subject data
    """
    with open(DATA_FILE, "w") as fp:
        json.dump(data, fp, indent=2)
