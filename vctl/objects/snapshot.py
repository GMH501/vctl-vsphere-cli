import sys
import time
import json
import datetime

import click
from pyVmomi import vim

from vctl.helpers.helpers import load_context
from vctl.helpers.vmware import get_obj, snapshot_tree, snapshot_obj, search_snapshot
from vctl.helpers.auth import inject_token
from vctl.helpers.utils import taskProgress

try:
    from pyVim.task import WaitForTask
except:
    from pyvim.task import WaitForTask


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
@click.option('--name', '-n',
              help='virtual machine on which you want to create the snapshot.',
              required=True)
@click.option('--description', '-d',
              help='the context you want to use for run this command, default is current-context.',
              required=False)
@click.option('--wait', '-w', is_flag=True)
def create(vm, context, name, description, wait):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], vm)
        if not hasattr(vm, '_moId'):
            print('Specified vm not found.')
            return
        task = vm.CreateSnapshot(name, description, memory=True, quiesce=False)
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
            json.dump(snapshot_obj(vm.snapshot), sys.stdout, indent=4, sort_keys=False)
            return
        print('The selected vm does not have any snapshots.')
    except Exception as e:
        raise e


@snapshot.command()
@click.option('--context', '-c',
              help='the context you want to use for run this command, default is current-context.',
              required=False)
@click.option('--vm', '-vm',
              help='virtual machine on which you want to create the snapshot.',
              required=True)
@click.option('--name', '-n',
              help='virtual machine on which you want to create the snapshot.',
              required=True)
@click.option('--wait', '-w', is_flag=True)
def remove(vm, context, name, wait):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], vm)
        if not hasattr(vm, '_moId'):
            print('Specified vm not found.')
            return
        if vm.snapshot is not None:
            snapshots = vm.snapshot.rootSnapshotList
            snap = search_snapshot(snapshots, name)
            if snap is not None:
                task = snap.RemoveSnapshot_Task(removeChildren=True)
                if wait:
                    try:
                        WaitForTask(task, onProgressUpdate=taskProgress)
                        sys.stdout.write('\r ')
                    except:
                        raise
                return
            print('Snapshot not found.')
            return
        print('The selected vm does not have any snapshots.')
    except Exception as e:
        raise e

@snapshot.command()
@click.option('--context', '-c',
              help='the context you want to use for run this command, default is current-context.',
              required=False)
@click.option('--vm', '-vm',
              help='virtual machine on which you want to create the snapshot.',
              required=True)
@click.option('--name', '-n',
              help='virtual machine on which you want to create the snapshot.',
              required=True)
@click.option('--wait', '-w', is_flag=True)
def revert(vm, context, name, wait):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], vm)
        if not hasattr(vm, '_moId'):
            print('Specified vm not found.')
            return
        if vm.snapshot is not None:
            snapshots = vm.snapshot.rootSnapshotList
            snap = search_snapshot(snapshots, name)
            if snap is not None:
                task = snap.RevertToSnapshot_Task()
                if wait:
                    try:
                        WaitForTask(task, onProgressUpdate=taskProgress)
                        sys.stdout.write('\r ')
                    except:
                        raise
                return
            print('Snapshot not found.')
            return
        print('The selected vm does not have any snapshots.')
    except Exception as e:
        raise e
