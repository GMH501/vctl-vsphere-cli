import click

from vctl.config.cmds import config
from vctl.get.cmds import get
from vctl.describe.cmds import describe
from vctl.objects.snapshot import snapshot


@click.group()
def cli():
    pass

cli.add_command(config)
cli.add_command(get)
cli.add_command(describe)
cli.add_command(snapshot)

if __name__ == "__main__":
    cli()