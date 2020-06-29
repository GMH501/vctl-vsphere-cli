import click
from pyVmomi import vim, vmodl

from vctl.helpers.vmware import get_obj
from vctl.helpers.helpers import load_context
from vctl.helpers.auth import inject_token
from vctl.exceptions.exceptions import ContextNotFound


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
        header_format = '{:<' + max_len + '}{:<17}{:<13}{:<13}{:<18}{:<10}{:<8}{:<10}{}'
        output_format = '{:<' + max_len + '}{:<17.2f}{:<13.2f}{:<13.2f}{:<18.2f}{:<10}{:<8}{:<10}{}'
        print(header_format.format(
            'NAME',
            'CAPACITY(GB)',
            'FREE(GB)',
            'USED(GB)',
            'PROVSIONED(%)',
            'HOSTS',
            'VMS',
            'TYPE',
            'ACCESSIBLE'
            )
        )
        for ds in datastores:
            summary = ds.summary
            uncommitted = summary.uncommitted if summary.uncommitted else 0
            print(output_format.format(
                summary.name,
                summary.capacity / 1024 / 1024 / 1024,
                summary.freeSpace / 1024 / 1024 / 1024,
                (summary.capacity - summary.freeSpace) / 1024 / 1024 / 1024,
                (summary.capacity - summary.freeSpace + uncommitted) * 100 / summary.capacity,
                len(ds.host),
                len(ds.vm),
                summary.type,
                summary.accessible
                )
            )

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(-1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(-1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(-1)