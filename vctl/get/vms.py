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
        max_name_len = str(len(max([vm.name for vm in vms], key=len)) + 4)
        vms_hostnames = [vm.summary.guest.hostName if vm.summary.guest.hostName is not None
                            else 'hostname' for vm in vms]
        max_hostname_len = str(len(max(vms_hostnames, key=len)) + 4)
        header_format = '{:<' + max_name_len + '}{:<' + max_hostname_len + '}{:<15}{:<8}{:<18}{:<15}{:<35}'
        print(header_format.format(
            'NAME',
            'HOSTNAME',
            'MEMORY(MB)',
            'CPU',
            'IPADDRESS',
            'STATUS',
            'HOST'
            )
        )
        for vm in vms:
            hardware = vm.config.hardware
            runtime = vm.summary.runtime
            guest = vm.summary.guest
            print(header_format.format(
                vm.name,
                str(guest.hostName),
                hardware.memoryMB,
                hardware.numCPU,
                str(guest.ipAddress),
                runtime.powerState,
                runtime.host.name
                )
            )

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caught error:', e)
