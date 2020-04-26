import click

from vc.config.subcmds import context

@click.group()
def config():
    pass

@config.group()
def new():
    pass

new.add_command(context)

@config.group()
def view():
    pass