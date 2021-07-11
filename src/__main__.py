"""This module defines the behaviour of the package
in a top-level script environment.

The following command executes this script:

```bash
python -m tubby
```
"""


import click


from .analyze import analyze
from .backup import backup
from .download import download
from .manage import manage
from .meta import DESCRIPTION
from .reset import reset


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
main.add_command(analyze)
main.add_command(backup)
main.add_command(reset)


if __name__ == "__main__":
    main()
