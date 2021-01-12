import click
from .commands.admin import admin


@click.group()
def cli():
    'A command line interface for BrightID'
    pass

cli.add_command(admin)