import sys
import time
import json
import datetime

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


def snapshot_obj(snap):
    output = {
        'snapshotInfo': {
            'currentSnapshot': snap.currentSnapshot._moId,
            'rootSnapshotList': snapshot_tree(snap.rootSnapshotList)
        }
    }
    return output


def snapshot_tree(snap_list):
    output = []
    for snapshot in snap_list:
        snap_info = {}
        snap_info['snapshot'] = snapshot.snapshot._moId
        snap_info['name'] = snapshot.name
        snap_info['createTime'] = snapshot.createTime.strftime(
                                            "%a, %d %b %Y %H:%M:%S %z"
                                            )
        snap_info['state'] = snapshot.state
        snap_info['quiesced'] = snapshot.quiesced
        output.append(snap_info)
        if snapshot.childSnapshotList != []:
            snap_info['childSnapshotList'] = snapshot_tree(snapshot.childSnapshotList)
    return output


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


