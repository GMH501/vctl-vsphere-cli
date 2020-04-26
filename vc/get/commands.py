import click


@click.group()
def get():
    pass

@get.command()
def hosts():
    print(vcenter)