import click
from pyVmomi import vim
from pyvim.connect import SmartConnectNoSSL

from vc.helpers.vmware import get_obj
from vc.helpers.helpers import load_context


@click.command()
def hosts():
    #context = load_context(decode=True)
    si = SmartConnectNoSSL(host='127.0.0.1', user='user', pwd='pass')
    if si is not None:
        print('hosts')