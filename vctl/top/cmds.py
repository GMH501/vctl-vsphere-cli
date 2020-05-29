import click
from pyVmomi import VmomiSupport

from vctl.helpers.helpers import load_context
from vctl.helpers.auth import inject_token
from vctl.helpers.perf import BuildQuery
from vctl.helpers.vmware import get_obj


@click.group()
def top():
    """
    """
    pass


@top.command()
@click.option('--name')
@click.option('--context', '-c',
              help='the context you want to use for run this command, \
                    default is current-context.',
              required=False)
def vm(name, context):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if vm is None:
            return
        perfResults = BuildQuery(content, 'cpu.usage.average', '', vm, time_measure='minutes', unit=1, interval=20)
        print(perfResults)
    except:
        raise
