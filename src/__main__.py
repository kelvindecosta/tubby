"""This module defines the behaviour of the package
in a top-level script environment.

The following command executes this script:

```bash
python -m tubby
```
"""


import click


from .download import download
from .manage import manage
from .meta import DESCRIPTION


@click.group(
    help=DESCRIPTION,
    options_metavar="[options]",
    subcommand_metavar="<command> [args]",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
def main():
    """The main program."""


main.add_command(download)
main.add_command(manage)


if __name__ == "__main__":
    main()
