import click
from pyVmomi import vim, vmodl

from vctl.helpers.vmware import get_obj
from vctl.helpers.helpers import load_context
from vctl.helpers.auth import inject_token
from vctl.exceptions.exceptions import ContextNotFound


@click.command()
@click.option('--context', '-c',
              help='the context you want to use for run this command, default is current-context.',
              required=False)
@click.option('--host', '-h',
              help='the host for which you want to disply the vms.',
              required=False)
def tasks(context, host):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        for task in content,taskManager.recentTask:
            print(task.info)

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caught error:', e)
