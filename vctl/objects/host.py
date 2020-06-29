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

##### host.config.storageDevice.scsiLun[]

@host.command()
@click.pass_context
def paths(ctx):
    """List all the paths state.
    """
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        host = get_obj(content, [vim.HostSystem], name)
        paths = host.config.storageDevice.multipathInfo.lun
        #paths = host.configManager.storageSystem.multipathStateInfo.path
        print(paths)
        return
        max_len = str(len(max([path.name for path in paths], key=len)) + 4)
        header_format = '{:<' + max_len + '}{}'
        print(header_format.format(
            'NAME',
            'STATE'
            )
        )
        for path in paths:
            print(header_format.format(
            path.name,
            path.pathState
            )
        )
        return

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
def datastores(ctx):
    """List all datastores.
    """
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        host = get_obj(content, [vim.HostSystem], name)        
        volumes = host.configManager.storageSystem.fileSystemVolumeInfo.mountInfo
            #print(str(datastore.volume.type) + "   " + str(datastore.volume.extent[0].diskName))
        paths = host.configManager.storageSystem.multipathStateInfo.path
        max_len = str(len(max([path.name for path in paths], key=len)) + 4)
        header_format = '{:<' + max_len + '}{}'
        print(header_format.format(
            'NAME',
            'STATE'
            )
        )
        for path in paths:
            print(header_format.format(
            path.name,
            path.pathState
            )
        )
        return

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        SystemExit(1)
