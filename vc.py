import click

from helpers import ssl_helper
from auth import commands as auth
#from .group2 import commands as group2

@click.group()
def cli():
    pass

cli.add_command(auth.auth)
    