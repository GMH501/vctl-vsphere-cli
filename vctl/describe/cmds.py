import click


@click.group()
def describe():
    pass


@describe.command()
def host():
    print('hosts')


@describe.command()
def vm():
    print('vm')
