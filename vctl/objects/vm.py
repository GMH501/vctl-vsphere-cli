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
              help='The name of the virtual machine on which to run the command.',
              required=True)
@click.pass_context
def vm(ctx, context, name):
    ctx = click.Context
    ctx.name = name
    ctx.context = context
    pass


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
            SystemExit('Specified vm not found.')
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
        SystemExit('Context not found.')
    except vim.fault.NotAuthenticated:
        SystemExit('Context expired.')
    except vim.fault.InvalidPowerState:
        sys.stdout.write('\r ')
    except Exception as e:
        SystemExit('Caught error:', e)


@vm.command()
@click.option('--username', '-user', '-u',
              help='The desiderd state for the virtual machine.',
              required=True)
@click.option('--password', '-pwd', '-p', 
              help='Wait for the task to complete.',
              required=True)
@click.pass_context
def get_procs(ctx, username, password):
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not hasattr(vm, '_moId'):
            SystemExit('Specified vm not found.')
        tools_status = vm.guest.toolsStatus
        if (tools_status == 'toolsNotInstalled' or
                tools_status == 'toolsNotRunning'):
            SystemExit(
                "VMwareTools is either not running or not installed."
                )
        creds = vim.vm.guest.NamePasswordAuthentication(
            username=username, password=password)
        try:
            pm = content.guestOperationsManager.processManager
            procs = pm.ListProcessesInGuest(vm, creds)
            print(procs)
        except:
            raise

    except ContextNotFound:
        SystemExit('Context not found.')
    except vim.fault.NotAuthenticated:
        SystemExit('Context expired.')
    except vim.fault.InvalidPowerState:
        sys.stdout.write('\r ')
    except Exception as e:
        SystemExit('Caught error:', e)
