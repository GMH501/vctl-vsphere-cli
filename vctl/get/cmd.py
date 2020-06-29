import click

from vctl.get.datastores import datastores
from vctl.get.hosts import hosts
from vctl.get.vms import vms
from vctl.get.networks import networks


@click.group()
def get():
    pass


get.add_command(vms)
get.add_command(hosts)
get.add_command(datastores)
get.add_command(networks)
