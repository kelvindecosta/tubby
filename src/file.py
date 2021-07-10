"""This module defines variables and functions for file handling"""


import json
import os
from typing import Optional


CONFIG_DIR: str = os.path.join(os.path.dirname(__file__), "config")
"""Folder for configuration"""


if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)


METADATA_FILE: str = os.path.join(CONFIG_DIR, "metadata.json")
"""File for metadata information"""


def load_metadata() -> Optional[dict]:
    """Loads metadata from file

    Returns:
        Optional[dict]: subject metadata
    """
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as file_pointer:
            return json.load(file_pointer)
    else:
        return None


def save_metadata(metadata: dict):
    """Saves `metadata` to file

    Args:
        metadata (dict): subject metadata
    """
    with open(METADATA_FILE, "w") as file_pointer:
        json.dump(metadata, file_pointer)


INVENTORY_FILE = os.path.join(CONFIG_DIR, "inventory.json")
"""File for inventory information"""


def load_inventory() -> Optional[dict]:
    """Loads inventory from file

    Returns:
        Optional[dict]: subject inventory
    """
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, "r") as file_pointer:
            return json.load(file_pointer)
    else:
        return None


def save_inventory(inventory: dict):
    """Saves `inventory` to file

    Args:
        inventory (dict): subject inventory
    """
    with open(INVENTORY_FILE, "w") as file_pointer:
        json.dump(inventory, file_pointer)


def delete_inventory() -> bool:
    """Deletes inventory file

    Returns:
        bool: whether inventory was deleted
    """
    if os.path.exists(INVENTORY_FILE):
        if (
            len(
                confirm := input(
                    "Are you sure you want to delete your inventory? [y/N]: "
                )
            )
            > 0
            and confirm.lower()[0] == "y"
        ):
            os.remove(INVENTORY_FILE)
            print("Deleted inventory!")
            return True
    else:
        print("Could not find inventory!")
    return False
