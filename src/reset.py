"""This module defines functions for reseting data"""


def create_metadata_schema():
    """Creates schema for metadata"""
    metadata = {
        key: {"map": {}, "list": []}
        for key in [
            "categories",
            "subcategories",
            "types",
            "materials",
            "furnishings",
            "sets",
        ]
    }

    metadata["cache"] = {}

    return metadata


def create_inventory_schema():
    """Creates schema for inventory"""
    inventory = {
        key: {}
        for key in [
            "companions",
            "materials",
            "furnishings",
            "sets",
        ]
    }

    return inventory