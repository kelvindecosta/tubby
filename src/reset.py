"""This module defines functions for reseting data"""


from .file import save_inventory


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


def update_inventory(metadata, inventory):
    save = False

    for c_name in metadata["companions"]:
        if (save := c_name not in (companions := inventory["companions"])) :
            companions[c_name] = False

    for m_name in metadata["materials"]:
        if (save := m_name not in (materials := inventory["materials"])) :
            materials[m_name] = 0

    for f_name in (furnishings_md := metadata["furnishings"]) :
        furnishings = inventory["furnishings"]
        if (
            save := (
                f_name not in furnishings
                or (
                    furnishings[f_name].get("blueprint") is None
                    and furnishings_md[f_name].get("materials") is not None
                )
            )
        ) :
            furnishings.setdefault(f_name, {})
            furnishings[f_name].setdefault("owned", 0)

            if furnishings_md[f_name].get("materials") is not None:
                furnishings[f_name].update(dict(blueprint=False, crafted=False))

    if save:
        save_inventory(inventory)
