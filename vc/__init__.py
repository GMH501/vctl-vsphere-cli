import click
from .auth import commands as auth

@click.group()
def cli():
    pass

cli.add_command(auth.auth)