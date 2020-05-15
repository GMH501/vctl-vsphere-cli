import json
import datetime

import click
from pyVmomi import vim

from vctl.helpers.vmware import get_obj
from vctl.helpers.helpers import load_context
from vctl.helpers.auth import inject_token
from vctl.exceptions.context_exceptions import ContextNotFound


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
        summary = host.summary
        print("Config:")
        print("  name:              ", summary.config.name)
        runtime = summary.runtime
        print("Runtime:")
        print("  inMaintenanceMode: ", runtime.inMaintenanceMode)
        print("  bootTime:          ", runtime.bootTime.strftime(
                                            "%a, %d %b %Y %H:%M:%S %z"))
        print("  connectionState:   ", runtime.connectionState)
        print("  powerState:        ", runtime.powerState)
        print("  standbyMode:       ", runtime.standbyMode)
        hardware = summary.hardware
        print("Hardware:")
        print("  vendor:            ", hardware.vendor)
        print("  model:             ", hardware.model)
        print("  memorySizeMB:      ", hardware.memorySize)
        print("  cpuModel:          ", hardware.cpuModel)
        print("  numCpuPkgs:        ", hardware.numCpuPkgs)
        print("  numCpuCores:       ", hardware.numCpuCores)
        print("  numCpuThreads:     ", hardware.numCpuThreads)
        print("  numNics:           ", hardware.numNics)
        print("  numHbas:           ", hardware.numHBAs)

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caught error:', e)


import yaml


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
    context = load_context(context=context)
    si = inject_token(context)
    content = si.content
    try:
        vm = get_obj(content, [vim.VirtualMachine], vm)
        summary = vm.summary
        config = summary.config
        guest = summary.guest
        runtime = summary.runtime
        hardware = vm.config.hardware
        vm_obj = {
            'config': {
                'name': config.name, 
                'vmPath': config.vmPathName
            },
            'guest': {
                'hostname':  guest.hostName,
                'guestOS': guest.guestFullName,
                'ipAddress': guest.ipAddress,
                'hwVersion': guest.hwVersion
            },
            'runtime': {
                'host': runtime.host.name,
                'bootTime': runtime.bootTime.strftime("%a, %d %b %Y %H:%M:%S %z"),
                'connectionState': str(runtime.connectionState),
                'powerState': str(runtime.powerState)
            },
            'hardware': {
                'numCPU': hardware.numCPU,
                'numCoresPerSocket': hardware.numCoresPerSocket,
                'memoryMB': hardware.memoryMB,
                'numEthernetCards': config.numEthernetCards,
                'numVirtualDisks': config.numVirtualDisks
            }
        }      
        if output == 'json':
            print(json.dumps(vm_obj, indent=4, sort_keys=True))
        else:
            print(yaml.dump(vm_obj, default_flow_style=False))

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caught error:', e)
