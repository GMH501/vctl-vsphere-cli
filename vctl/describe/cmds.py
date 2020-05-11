import click

from vctl.describe.subcmds import host

@click.group()
def describe():
    pass


describe.add_command(host)


@describe.command()
def vm():
    print('vm')


