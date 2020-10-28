import click

from vctl.config.cmd import config
from vctl.context.cmd import context
from vctl.get.cmd import get
from vctl.describe.cmd import describe
from vctl.objects.guest import guest
from vctl.objects.host import host
from vctl.objects.vm import vm
from vctl.objects.datastore import datastore
from vctl.run.cmd import run
from vctl.top.cmd import top
from vctl.perfs.cmd import perfs

@click.group()
def vctl():

    pass


vctl.add_command(config)
vctl.add_command(context)
vctl.add_command(run)
vctl.add_command(get)
vctl.add_command(guest)
vctl.add_command(host)
vctl.add_command(describe)
vctl.add_command(vm)
vctl.add_command(datastore)
vctl.add_command(top)
vctl.add_command(perfs)
