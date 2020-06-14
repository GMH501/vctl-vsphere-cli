import click
from pyVmomi import vim, vmodl

from vctl.helpers.vmware import get_obj
from vctl.helpers.helpers import load_context
from vctl.helpers.auth import inject_token
from vctl.exceptions.exceptions import ContextNotFound


def sizeof_fmt(num):
    """
    Returns the human readable version of a file size
    :param num:
    :return:
    """
    for item in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, item)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


def print_datastore_info(ds_obj):
    summary = ds_obj.summary
    ds_capacity = summary.capacity
    ds_freespace = summary.freeSpace
    ds_uncommitted = summary.uncommitted if summary.uncommitted else 0
    ds_provisioned = ds_capacity - ds_freespace + ds_uncommitted
    ds_overp = ds_provisioned - ds_capacity
    ds_overp_pct = (ds_overp * 100) / ds_capacity \
        if ds_capacity else 0
    print("")
    print("Name                  : {}".format(summary.name))
    print("URL                   : {}".format(summary.url))
    print("Capacity              : {} GB".format(sizeof_fmt(ds_capacity)))
    print("Free Space            : {} GB".format(sizeof_fmt(ds_freespace)))
    print("Uncommitted           : {} GB".format(sizeof_fmt(ds_uncommitted)))
    print("Provisioned           : {} GB".format(sizeof_fmt(ds_provisioned)))
    if ds_overp > 0:
        print("Over-provisioned      : {} GB / {} %".format(
            sizeof_fmt(ds_overp),
            ds_overp_pct))
    print("Hosts                 : {}".format(len(ds_obj.host)))
    print("Virtual Machines      : {}".format(len(ds_obj.vm)))


@click.command()
@click.option('--context', '-c',
              help='the context you want to use for run this command, default is current-context.',
              required=False)
def datastores(context):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        ds_obj_list = get_obj(content, [vim.Datastore])
        for ds in ds_obj_list:
            print_datastore_info(ds)

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caught error:', e)
