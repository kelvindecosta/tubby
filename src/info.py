"""This module defines the `tubby info` command"""


import os


import click


from .meta import NAME, VERSION, DESCRIPTION, REPO_URL, LICENSE, AUTHOR
from .utils import bold, italic


@click.command(options_metavar="[options]")
def info():
    """Displays package information"""
    with open(
        os.path.join(os.path.dirname(__file__), "data", "logo.txt"), "r"
    ) as file_pointer:
        logo_text = file_pointer.read().strip()

    output = f"\n{logo_text}\n".split("\n")

    line = 2
    output[line] += f"    {bold(NAME)}"

    line += 3
    output[line] += f"    {italic(DESCRIPTION)}"

    line += 3
    output[line] += f"    {italic('Version')} : {VERSION}"

    line += 1
    output[line] += f"    {italic('License')} : {LICENSE}"

    line += 1
    output[line] += f"    {italic('Author')}  : {AUTHOR}"

    line += 3
    output[line] += f"    {italic('Source')}  : {REPO_URL}"

    print("\n".join(output))
