import click
from .auth import commands as auth
from .get import commands as get

@click.group()
def cli():
    pass

cli.add_command(auth.auth)
cli.add_command(get.get)