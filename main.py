import click

from scrape import scrape


@click.group(
    help="A manager for the housing system",
    options_metavar="[options]",
    subcommand_metavar="<command> [args]",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
def main():
    """The main program."""
    pass


main.add_command(scrape)

if __name__ == "__main__":
    main()