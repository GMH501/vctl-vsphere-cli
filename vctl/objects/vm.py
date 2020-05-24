import sys

import click
from pyVmomi import vim

from vctl.helpers.helpers import load_context
from vctl.helpers.vmware import get_obj
from vctl.helpers.auth import inject_token
from vctl.helpers.utils import waiting
from vctl.exceptions.exceptions import ContextNotFound


@click.group()
@click.option('--context', '-c',
            help='The context to use for run the command, the default is <current-context>.',
            required=False)
@click.option('--name', '-n',
            help='Virtual Machine on which to run the command.',
            required=True)
@click.pass_context
def vm(ctx, context, name):
    ctx = click.Context
    ctx.name = name
    ctx.context = context


@vm.command()
@click.option('--state', '-s',
              help='The desiderd state for the virtual machine.',
              type=click.Choice(['on', 'off']),
              required=True)
@click.option('--wait', '-w', 
              help='Wait for the task to complete.',
              is_flag=True)
@click.pass_context
def power(ctx, state, wait):
    name = ctx.name
    context = ctx.context
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
