import click

from vc.get.subcmds import hosts

@click.group()
def get():
    pass

get.add_command(hosts)

