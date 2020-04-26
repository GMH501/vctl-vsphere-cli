import click
from .config import commands as config
from .get import commands as get
from .describe import commands as describe

@click.group()
def cli():
    pass

cli.add_command(config.config)
cli.add_command(get.get)
cli.add_command(describe.describe)