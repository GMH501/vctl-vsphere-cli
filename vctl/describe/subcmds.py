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
        #  print(".: HOST INFORMATION :.")
        print("Config:")
        print("  name: ", summary.config.name)
        #  print(".: vim.host.RuntimeInfo (vim.host.summary.runtime) :.")
        runtime = summary.runtime
        print("Runtime:")
        print("  inMaintenanceMode: ", runtime.inMaintenanceMode)
        print("  bootTime: ", runtime.bootTime.strftime("%a, %d %b %Y %H:%M:%S %z"))
        print("  connectionState: ", runtime.connectionState)
        print("  powerState: ", runtime.powerState)
        print("  standbyMode: ", runtime.standbyMode)
        #  print(".: vim.host.Summary.HardwareSummary (vim.host.summary.hardware) :.")
        hardware = summary.hardware
        print("Hardware:")
        print("  vendor: ", hardware.vendor)
        print("  model: ", hardware.model)
        print("  memorySize: ", hardware.memorySize)
        print("  cpuModel: ", hardware.cpuModel)
        print("  numCpuPkgs: ", hardware.numCpuPkgs)
        print("  numCpuCores: ", hardware.numCpuCores)
        print("  numCpuThreads: ", hardware.numCpuThreads)
        print("  numNics: ", hardware.numNics)
        print("  numHbas: ", hardware.numHBAs)
        #  print(".: vim.host.Summary.ConfigSummary (vim.host.summary.config) :.")

    except ContextNotFound:
        print('Context not found.')
    except vim.fault.NotAuthenticated:
        print('Context expired.')
    except Exception as e:
        print('Caught error:', e)