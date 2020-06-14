import click

from vctl.get.datastores import datastores
from vctl.get.hosts import hosts
from vctl.get.vms import vms


@click.group()
def get():
    pass


get.add_command(vms)
get.add_command(hosts)
get.add_command(datastores)
