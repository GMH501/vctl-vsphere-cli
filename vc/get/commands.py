import click


@click.group()
def get():
    pass

@get.command()
def clusters():
    print(hosts)

@get.command()
def hosts():
    print(hosts)

@get.command()
def vms():
    print(vms)