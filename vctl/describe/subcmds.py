import json
import datetime
import sys

import click
import yaml
from pyVmomi import vim

from vctl.helpers.vmware import get_obj, get_vm_hardware_lists, get_vm_obj
from vctl.helpers.helpers import load_context
from vctl.helpers.auth import inject_token
from vctl.exceptions.context_exceptions import ContextNotFound


@click.command()
@click.argument('host', nargs=1)
@click.option('--context', '-c',
              help='the context you want to use for run this command, \
                    default is current-context.',
              required=False)
@click.option('--output', '-o',
              help='the context you want to use for run this command, \
                    default is current-context.',
              required=False, 
              default='yaml', 
              show_default=True)
def host(host, context, output):
    if output not in ['yaml', 'json']: 
        print('Incorrect value for --output option [json|yaml].')
        return
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        host = get_obj(content, [vim.HostSystem], host)
        if not hasattr(host, '_moId'):
            print('Specified host not found.')
            return
        summary = host.summary
        config = summary.config
        hardware = summary.hardware
        runtime = summary.runtime
        host_obj = {
            'config': {
                'name': config.name,
            },
            'hardware': {
                'vendor':  hardware.vendor,
                'model': hardware.model,
                'memorySize': hardware.memorySize,
                'cpuModel': hardware.cpuModel,
                'numCpuPkgs': hardware.numCpuPkgs,
                'numCpuCores': hardware.numCpuCores,
                'numCpuThreads': hardware.numCpuThreads,
                'numNics': hardware.numNics,
                'numHBAs': hardware.numHBAs
            },
            'runtime': {
                'inMaintenanceMode': runtime.inMaintenanceMode,
                'bootTime': runtime.bootTime.strftime("%a, %d %b %Y %H:%M:%S %z"),
                'connectionState': runtime.connectionState,
                'powerState': runtime.powerState,
                'standbyMode': runtime.standbyMode
            }
        }
        if output == 'json':
            json.dump(host_obj, sys.stdout, indent=4, sort_keys=True)
        #else:
            # yaml.dump(host_obj, sys.stdout, tags=None, default_flow_style=False)
        summary = host.summary
        stats = summary.quickStats
        hardware = host.hardware
        cpuUsage = stats.overallCpuUsage
        memoryCapacity = hardware.memorySize
        memoryCapacityInMB = hardware.memorySize/(1024)
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
@click.option('--output', '-o',
              help='the context you want to use for run this command, \
                    default is current-context.',
              required=False, 
              default='yaml', 
              show_default=True)
def vm(vm, context, output):
    if output not in ['yaml', 'json']: 
        print('Incorrect value for --output option [json|yaml].')
        return
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], vm)
        if not hasattr(vm, '_moId'):
            print('Specified vm not found.')
            return
        vm_obj = get_vm_obj(vm)
        if output == 'json':
            json.dump(vm_obj, sys.stdout, indent=4, sort_keys=False)
        else:
            yaml.dump(vm_obj, sys.stdout, tags=None, default_flow_style=False)


    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caught error:', e)
