"""This module defines functions for reseting data"""


def create_metadata_schema():
    """Creates schema for metadata"""
    metadata = {key: [] for key in ["companions", "materials"]}
    metadata.update(
        {
            key: {}
            for key in [
                "furnishings",
                "sets",
            ]
        }
    )

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
