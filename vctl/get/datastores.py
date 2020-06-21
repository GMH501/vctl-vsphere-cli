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
    ds_provisioned = ds_capacity - ds_freespace + ds_uncommitted
    ds_freespace = summary.freeSpace
    print("")
    print("Name                  : {}".format(summary.name))
    print("URL                   : {}".format(summary.url))
    print("Capacity              : {} GB".format(sizeof_fmt(ds_capacity)))
    print("Free Space            : {} GB".format(sizeof_fmt(ds_freespace)))
    print("Uncommitted           : {} GB".format(sizeof_fmt(ds_uncommitted)))
    print("Provisioned           : {} GB".format(sizeof_fmt(ds_provisioned)))
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
        datastores = get_obj(content, [vim.Datastore])
        max_len = str(len(max([ds.name for ds in datastores], key=len)) + 4)
        header_format = '{:<' + max_len + '}{:<17}{:<19}{:<13}{:<10}{:<8}{}'
        output_format = '{:<' + max_len + '}{:<17.2f}{:<19.2f}{:<13.2f}{:<10}{:<8}{}'
        print(header_format.format(
            'NAME',
            'CAPACITY(GB)',
            'PROVSIONED(GB)', # TODO Aggiungere USED
            'FREE(GB)',
            'HOSTS',
            'VMS',
            'URL'
            )
        )
        for ds in datastores:
            summary = ds.summary
            print(output_format.format(
                summary.name,
                "", #summary.capacity / 1024 / 1024 / 1024,
                "", #(summary.capacity - summary.freeSpace + summary.uncommitted) / 1024 / 1024 / 1024,
                "", # summary.freeSpace / 1024 / 1024 / 1024,
                len(ds.host),
                len(ds.vm),
                "" #summary.url
                )
            )

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caught error:', e)
        raise e