import click
from pyVmomi import vim

from vc.helpers.vmware import get_obj
from vc.helpers.helpers import load_context
from vc.helpers.auth import inject_token
from vc.exceptions.context_exceptions import ContextNotFound


@click.command()
def hosts():
    try:
        context = load_context()
        si = inject_token(context)
        content = si.RetrieveContent()
        hosts = get_obj(content, [vim.HostSystem])
        print(hosts[0].config)

    except ContextNotFound as e:
        print(e.message)
