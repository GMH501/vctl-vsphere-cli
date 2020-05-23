import click

from vctl.config.cmds import config
from vctl.get.cmds import get
from vctl.describe.cmds import describe
from vctl.objects.snapshot import snapshot
from vctl.objects.vm import vm


@click.group()
def vctl():
    pass


vctl.add_command(config)
vctl.add_command(get)
vctl.add_command(describe)
vctl.add_command(snapshot)
vctl.add_command(vm)
