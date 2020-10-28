import click
from pyVmomi import vim, vmodl

from vctl.helpers.auth import inject_token
from vctl.helpers.helpers import load_context
from vctl.helpers.vmware import get_obj


@click.group()
@click.option('--context', '-c',
              help='The context to use for run the command, the default is <current-context>.',
              required=False)
@click.argument('host_name', nargs=1,
              required=True)
@click.pass_context
def host(ctx, context, host_name):
    """
    """
    ctx = click.Context
    ctx.name = host_name
    ctx.context = context
    pass


@host.command()
@click.pass_context
def paths(ctx):
    """List all storage paths.
    """
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        host = get_obj(content, [vim.HostSystem], name)
        luns = host.config.storageDevice.multipathInfo.lun
        for lun in luns:
            lun_key = lun.lun
            lun_name = 'None'
            for scsi_lun in host.config.storageDevice.scsiLun:
                if scsi_lun.key == lun_key:
                    lun_name = scsi_lun.canonicalName
                    break
            paths = lun.path
            max_len = str(len(max([path.name for path in paths], key=len)) + 4)
            header_format = '{:<' + max_len + '}{:<11}{}'
            print(header_format.format(
                'PATH NAME',
                'STATE',
                'LUN NAME'
                )
            )
            for path in paths:
                print(header_format.format(
                path.name,
                path.pathState,
                lun_name
                )
            )

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        SystemExit(1)


@host.command()
@click.pass_context
def luns(ctx):
    """List all luns.
    """
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        host = get_obj(content, [vim.HostSystem], name)        
        luns = host.config.storageDevice.scsiLun
        max_len = str(len(max([lun.canonicalName for lun in luns], key=len)) + 4)
        header_format = '{:<' + max_len + '}{:<15}{:<15}{:<8}{}'
        print(header_format.format(
            'NAME',
            'NUM BLOCKS',
            'BLOCK SIZE',
            'SSD',
            'MODEL',

            )
        )
        for lun in luns:
            block = lun.capacity.block if hasattr(lun, 'capacity') else 'None'
            blockSize = lun.capacity.blockSize if hasattr(lun, 'capacity') else 'None'
            ssd = str(lun.ssd) if hasattr(lun, 'ssd') else 'None'
            print(header_format.format(
            lun.canonicalName,
            block,
            blockSize,
            ssd,
            lun.model
            )
        )

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise e #SystemExit(1)
