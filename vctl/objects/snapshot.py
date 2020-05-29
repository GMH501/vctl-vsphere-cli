import sys

import click
from pyVmomi import vim

from vctl.helpers.helpers import load_context, jsonify
from vctl.helpers.vmware import get_obj, snapshot_tree, snapshot_obj, search_snapshot
from vctl.helpers.auth import inject_token
from vctl.helpers.utils import waiting


@click.group()
def snapshot():
    """

    """
    pass


@snapshot.command()
@click.option('--name', '-n',
              help='virtual machine on which you want to create the snapshot.',
              required=True)
@click.option('--description', '-d',
              help='the context you want to use for run this command, default is current-context.',
              required=False)
@click.option('--memory', '-m', is_flag=True)
@click.option('--quiesce', '-q', is_flag=True)
@click.option('--wait', '-w', is_flag=True)
@click.pass_context
def create(ctx, name, description, memory, quiesce, wait):
    """
    """
    vm = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], vm)
        if not hasattr(vm, '_moId'):
            raise SystemExit('Specified vm not found.')
        task = vm.CreateSnapshot(name, description, memory=memory, quiesce=quiesce)
        if wait:
            waiting(task)
    except Exception as e:
        raise SystemExit('Cught error: ' + e)


@snapshot.command()
def list(ctx):
    vm = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], vm)
        if not hasattr(vm, '_moId'):
            SystemExit('Specified vm not found.')
        if vm.snapshot is not None:
            snap_obj = snapshot_obj(vm.snapshot)
            jsonify(snap_obj)
        else:
            raise SystemExit('The selected vm does not have any snapshots.')
    except Exception as e:
        raise SystemExit('Caught error: ' + e)


@snapshot.command()
@click.option('--name', '-n',
              help='virtual machine on which you want to create the snapshot.',
              required=True)
@click.option('--wait', '-w', is_flag=True)
def remove(ctx, name, wait):
    vm = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], vm)
        if not hasattr(vm, '_moId'):
            SystemExit('Specified vm not found.')
        if vm.snapshot is not None:
            snapshots = vm.snapshot.rootSnapshotList
            snap = search_snapshot(snapshots, name)
            if snap is not None:
                task = snap.RemoveSnapshot_Task(removeChildren=True)
                if wait:
                    waiting(task)
            else:
                SystemExit('Snapshot not found.')
        else:
            SystemExit('The selected vm does not have any snapshots.')
    except Exception as e:
        SystemExit('Caught error:', e)


@snapshot.command()
@click.option('--name', '-n',
              help='Name for the snapshot.',
              required=True)
@click.option('--wait', '-w',
              help='Wait for the task to complete.',
              is_flag=True)
def revert(ctx, name, wait):
    vm = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], vm)
        if not hasattr(vm, '_moId'):
            raise SystemExit('Specified vm not found.')
        if vm.snapshot is not None:
            snapshots = vm.snapshot.rootSnapshotList
            snap = search_snapshot(snapshots, name)
            if snap is not None:
                task = snap.RevertToSnapshot_Task()
                if wait:
                    waiting(task)
                return
            else:
                raise SystemExit('Snapshot not found.')
        else:
            raise SystemExit('The selected vm does not have any snapshots.')
    except Exception as e:
        raise SystemExit('Caught error: ' + e)
