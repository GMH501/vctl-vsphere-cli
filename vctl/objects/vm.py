import sys

import click
from pyVmomi import vim

from vctl.helpers.helpers import load_context
from vctl.helpers.vmware import get_obj
from vctl.helpers.auth import inject_token
from vctl.helpers.utils import waiting
from vctl.exceptions.exceptions import ContextNotFound




@click.command()
@click.option('--context', '-c',
            help='the context you want to use for run this command, default is current-context.',
            required=False)
@click.option('--name', '-n',
            help='virtual machine on which you want to create the snapshot.',
            required=True)
@click.option('--state', '-s',
            type=click.Choice(['on', 'off'], case_sensitive=True),
            required=True)
@click.option('--wait', '-w', is_flag=True)
def vm(context, name, state, wait):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not hasattr(vm, '_moId'):
            print('Specified vm not found.')
            return
        try:
            if state == 'on':
                task = vm.PowerOnVM_Task()
            elif state == 'off':
                task = vm.PowerOffVM_Task()
            if wait:
                waiting(task)
        except:
            raise

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except vim.fault.InvalidPowerState:
        sys.stdout.write('\r ')
    except Exception as e:
        print('Caught error:', e)