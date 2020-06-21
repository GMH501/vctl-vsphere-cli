import sys

import click
from pyVmomi import vim, vmodl

from vctl.helpers.helpers import load_context, jsonify, yamlify
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
        if not isinstance(vm, vim.VirtualMachine):
            print('Specified vm not found.')
            raise SystemExit(1)
        task = vm.CreateSnapshot(name, description, memory=memory, quiesce=quiesce)
        if wait:
            waiting(task)

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(1)


@snapshot.command()
@click.option('--output', '-o',
              help='The desired output format.',
              type=click.Choice(['json', 'yaml']),
              default='json',
              required=False)
@click.pass_context
def list(ctx, output):
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
            if output == 'json':
                jsonify(snap_obj)
            else:
                yamlify(snap_obj)
        else:
            raise SystemExit('The selected vm does not have any snapshots.')

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        SystemExit(1)


@snapshot.command()
@click.option('--name', '-n',
              help='virtual machine on which you want to create the snapshot.',
              required=True)
@click.option('--wait', '-w', is_flag=True)
@click.pass_context
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

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(1)


@snapshot.command()
@click.option('--name', '-n',
              help='Name for the snapshot.',
              required=True)
@click.option('--wait', '-w',
              help='Wait for the task to complete.',
              is_flag=True)
@click.pass_context
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

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(1)
