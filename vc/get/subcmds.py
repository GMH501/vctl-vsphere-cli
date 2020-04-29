import click
from pyvim.connect import SmartConnectNoSSL

from vc.helpers.vmware import get_obj
from vc.helpers.helpers import load_context
from vc.helpers.auth import inject_token
from vc.exceptions.context_exceptions import ContextNotFound


@click.command()
def hosts():
    try:
        context = load_context(decode=True)
        si = inject_token(context)
        print(si)
    except ContextNotFound as e:
        print(e.message)