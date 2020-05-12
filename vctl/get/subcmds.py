import click
from pyVmomi import vim

from vctl.helpers.vmware import get_obj
from vctl.helpers.helpers import load_context
from vctl.helpers.auth import inject_token
from vctl.exceptions.context_exceptions import ContextNotFound


@click.command()
@click.option('--context', '-c',
              help='the context you want to use for run this command, \
                    default is current-context.',
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
        print('{:<30}{:<15}{:<10}{:<15}{:<30}'.format('NAME',
                                                      'MEMORY(MB)',
                                                      'CPU',
                                                      'VERSION',
                                                      'PARENT'))
        for host in hosts:
            name = host.name
            parent = host.parent.name
            version = host.config.product.version
            cores = host.hardware.cpuInfo.numCpuCores
            memory_MB = round(host.hardware.memorySize / (1024*1024))
            print('{:<30}{:<15}{:<10}{:<15}{:<30}'.format(name,
                                                          memory_MB,
                                                          cores,
                                                          version,
                                                          parent))

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caught error:', e)


#  @click.command()
#  def clusters():
#      try:
#          context = load_context()
#          si = inject_token(context)
#          content = si.content
#          hosts = get_obj(content, [vim.ComputeResource])
#          print('{:<30}{:<15}{:<15}{:<30}'.format(
#                'NAME', 'MEMORY %', 'CPU %', 'SPEC'))
#          for host in hosts:
#              print('{:<30}{:<15}{:<15}{:<30}'.format(host.name,
#                                                      '',
#                                                      '',
#                                                      host.parent.name))
#  
#      except ContextNotFound:
#          print('Context not found.')
#      except vim.fault.NotAuthenticated:
#          print('Context expired.')
#      except Exception as e:
#          print('Caught error:', e)


@click.command()
def vms():
    try:
        context = load_context()
        si = inject_token(context)
        content = si.content
        vms = get_obj(content, [vim.VirtualMachine])
        print('{:<30}{:<15}{:<15}{:<20}{:<30}'.format('NAME',
                                                      'MEMORY(MB)',
                                                      'CPU',
                                                      'PARENT',
                                                      'STATUS'))
        for vm in vms:
            hardware = vm.config.hardware
            runtime = vm.summary.runtime
            print('{:<30}{:<15}{:<15}{:<20}{:<30}'.format(vm.name,
                                                          hardware.memoryMB,
                                                          hardware.numCPU,
                                                          runtime.host.name,
                                                          runtime.powerState))

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        #print('Caught error:', e)
        raise e
