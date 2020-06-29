from datetime import datetime

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
@click.option('--cluster', '-cl',
              help='The cluster for which you want to run the command.',
              required=False)
def hosts(context, cluster):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        if cluster:
            cluster_resource = get_obj(content, [vim.ClusterComputeResource], cluster)
            if not isinstance(cluster, vim.ClusterComputeResource):
                print('Cluster {} not found.'.format(cluster))
                raise SystemExit(1)
            hosts = cluster_resource.host
        else:
            hosts = get_obj(content, [vim.HostSystem])
        max_len = str(len(max([host.name for host in hosts], key=len)) + 4)
        header_format = '{:<' + max_len + '}{:<15}{:<8}{:<8}{:<15}{:<17}{:<16}{:<10}{:<12}{:<35}'
        print(header_format.format(
            'NAME',
            'MEMORY(MB)',
            'CPU',
            'VMS',
            'DATASTORES',
            'CONNECT STATE',
            'POWER STATE',
            'AGE',
            'VERSION',
            'PARENT'
            )
        )
        for host in hosts:
            name = host.name
            memory_MB = round(host.hardware.memorySize / (1024 * 1024))
            cores = host.hardware.cpuInfo.numCpuCores
            num_vms = len(host.vm)
            num_ds = len(host.datastore)
            version = host.config.product.version if hasattr(host.config, 'product') else None
            connectionState = str(host.runtime.connectionState)
            powerState = str(host.runtime.powerState)
            age = (datetime.now() - host.runtime.bootTime.replace(tzinfo=None)).days \
                    if host.runtime.bootTime is not None else None
            parent = host.parent.name
            print(header_format.format(
                name,
                memory_MB,
                cores,
                num_vms,
                num_ds,
                connectionState,
                powerState,
                str(age),
                str(version),
                parent
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
