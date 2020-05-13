import click

from vctl.get.subcmds import hosts, vms


@click.group()
def get():
    pass


get.add_command(vms)
get.add_command(hosts)
#get.add_command(clusters)
