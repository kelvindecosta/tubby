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