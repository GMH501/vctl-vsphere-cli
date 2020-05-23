import click
import yaml
from pyVmomi import vim

from vctl.helpers.vmware import get_obj, get_vm_hardware_lists, get_vm_obj, get_host_obj
from vctl.helpers.helpers import load_context, jsonify
from vctl.helpers.auth import inject_token
from vctl.exceptions.exceptions import ContextNotFound


@click.command()
@click.argument('host', nargs=1)
@click.option('--context', '-c',
              help='the context you want to use for run this command, \
                    default is current-context.',
              required=False)
def host(host, context):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        host = get_obj(content, [vim.HostSystem], host)
        if not hasattr(host, '_moId'):
            print('Specified host not found.')
            return
        host_obj = get_host_obj(host)
        jsonify(host_obj)
        return
        summary = host.summary
        stats = summary.quickStats
        hardware = host.hardware
        cpuUsage = stats.overallCpuUsage
        memoryCapacity = hardware.memorySize
        memoryCapacityInMB = hardware.memorySize / 1024
        memoryUsage = stats.overallMemoryUsage
        freeMemoryPercentage = 100 - (
            (float(memoryUsage) / memoryCapacityInMB) * 100
        )
        usageMemoryPercentage = (
            (float(memoryUsage) / memoryCapacityInMB) * 100
        )
        print("--------------------------------------------------")
        print("Host name: ", host.name)
        # dump(host)
        print("Host CPU usage: ", cpuUsage)
        print("Host memory usage: ", memoryUsage / 1024, "GiB")
        print("Free memory percentage: " + str(freeMemoryPercentage) + "%")
        print("Usage memory percentage: " + str(usageMemoryPercentage) + "%")
        print("--------------------------------------------------")
    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caught error:', e)


@click.command()
@click.argument('vm', nargs=1)
@click.option('--context', '-c',
              help='the context you want to use for run this command, \
                    default is current-context.',
              required=False)
def vm(vm, context):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], vm)
        if not hasattr(vm, '_moId'):
            print('Specified vm not found.')
            return
        vm_obj = get_vm_obj(vm)
        jsonify(vm_obj)

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caught error:', e)
