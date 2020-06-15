import click

from vctl.config.cmd import config
from vctl.get.cmd import get
from vctl.describe.cmd import describe
from vctl.objects.guest import guest
from vctl.objects.vm import vm
from vctl.objects.datastore import datastore
from vctl.top.cmd import top


@click.group()
def vctl():

    pass


vctl.add_command(config)
vctl.add_command(get)
vctl.add_command(guest)
vctl.add_command(describe)
vctl.add_command(vm)
vctl.add_command(datastore)
vctl.add_command(top)
