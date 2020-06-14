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
              help='the cluster for which you want to run the command.',
              required=False)
def hosts(context, cluster):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        if cluster:
            cluster = get_obj(content, [vim.ClusterComputeResource], cluster)
            if not hasattr(cluster, 'host'):
                print('Invalid argument.')
                return
            hosts = cluster.host
        else:
            hosts = get_obj(content, [vim.HostSystem])
            #  max_len = len(max([host.name for host in hosts], key=len))
        print('{:<36}{:<15}{:<8}{:<8}{:<15}{:<10}{:<35}'.format(
                                                    'NAME',
                                                    'MEMORY(MB)',
                                                    'CPU',
                                                    'VMS',
                                                    'DATASTORES',
                                                    'VERSION',
                                                    'PARENT'))
        for host in hosts:
            name = host.name
            memory_MB = round(host.hardware.memorySize / (1024 * 1024))
            cores = host.hardware.cpuInfo.numCpuCores
            num_vms = len(host.vm)
            num_ds = len(host.datastore)
            version = host.config.product.version
            parent = host.parent.name
            print('{:<36.33}{:<15}{:<8}{:<8}{:<15}{:<10}{:<35}'.format(
                                                        name,
                                                        memory_MB,
                                                        cores,
                                                        num_vms,
                                                        num_ds,
                                                        version,
                                                        parent))

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caught error:', e)
