import click

from vctl.config import cmds as cmds_config
from vctl.get import cmds as cmds_get
from vctl.describe import cmds as cmds_describe

@click.group()
def cli():
    pass

cli.add_command(cmds_config.config)
cli.add_command(cmds_get.get)
cli.add_command(cmds_describe.describe)

if __name__ == "__main__":
    cli()