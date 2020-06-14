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
@click.option('--host', '-h',
              help='the host for which you want to disply the vms.',
              required=False)
def vms(context, host):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        if host:
            host = get_obj(content, [vim.HostSystem], host)
            vms = host.vm
        else:
            vms = get_obj(content, [vim.VirtualMachine])
        print('{:<20}{:<30}{:<15}{:<10}{:<15}{:<15}{:<35}'.format(
                                                    'NAME',
                                                    'HOSTNAME',
                                                    'MEMORY(MB)',
                                                    'CPU',
                                                    'IPADDRESS',
                                                    'STATUS',
                                                    'HOST'
                                                    ))
        for vm in vms:
            hardware = vm.config.hardware
            runtime = vm.summary.runtime
            guest = vm.summary.guest
            print('{:<20}{:<30}{:<15}{:<10}{:<15}{:<15}{:<35}'.format(
                                                        str(vm.name),
                                                        str(guest.hostName),
                                                        str(hardware.memoryMB),
                                                        str(hardware.numCPU),
                                                        str(guest.ipAddress),
                                                        str(runtime.powerState),
                                                        str(runtime.host.name)
                                                        ))

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caughterror:', e)
