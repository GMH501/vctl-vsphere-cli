import sys
import time
from datetime import datetime

import click
from pyVmomi import vim
try:
    from pyVim.task import WaitForTask
except:
    from pyvim.task import WaitForTask

from vctl.helpers.helpers import load_context
from vctl.helpers.vmware import get_obj
from vctl.helpers.auth import inject_token
from vctl.helpers.utils import taskProgress


@click.group()
def snapshot():
    """

    """
    pass

@snapshot.command()
@click.option('--context', '-c',
              help='the context you want to use for run this command, default is current-context.',
              required=False)
@click.option('--vm', '-vm',
              help='virtual machine on which you want to create the snapshot.',
              required=True)
@click.option('--snap-name', '-name',
              help='virtual machine on which you want to create the snapshot.',
              required=True)
@click.option('--description', '-d',
              help='the context you want to use for run this command, default is current-context.',
              required=False)
@click.option('--wait', '-w', is_flag=True)
def create(vm, context, snap_name, description, wait):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], vm)
        if not hasattr(vm, '_moId'):
            print('Specified vm not found.')
            return
        task = vm.CreateSnapshot(snap_name, description, memory=True, quiesce=False)
        if wait:
            try:
                WaitForTask(task, onProgressUpdate=taskProgress)
                sys.stdout.write('\r ')
            except:
                raise
    except Exception as e:
        print('Cught error:', e)


@snapshot.command()
@click.option('--context', '-c',
              help='the context you want to use for run this command, default is current-context.',
              required=False)
@click.option('--vm', '-vm',
              help='virtual machine on which you want to create the snapshot.',
              required=True)
def list(vm, context):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], vm)
        if not hasattr(vm, '_moId'):
            print('Specified vm not found.')
            return
        if vm.snapshot is not None:
            print(vm.snapshot.rootSnapshotList)
            return
        print('The selected vm does not have any snapshots.')
    except Exception as e:
        raise e
