import click


@click.group()
def get():
    pass

@get.command()
@click.option('--vcenter', '-v', 
              help='vcenter you want to conntect to.',
              required=True
              )
def name(vcenter):
    print(vcenter)