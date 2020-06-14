import click

from vctl.describe.subcmds import host, vm


@click.group()
def describe():
    pass


describe.add_command(host)
describe.add_command(vm)
