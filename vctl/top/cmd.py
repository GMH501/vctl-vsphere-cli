import io
import os
import shutil
import sys

from pyVmomi import vim, vmodl
import click

from vctl.helpers.helpers import load_context
from vctl.helpers.auth import inject_token
from vctl.helpers.perf import BuildQuery, print_perfs
from vctl.helpers.vmware import get_obj
from vctl.exceptions.exceptions import ContextNotFound


@click.group()
def top():
    """
    """
    pass


def get_path(file):
    file_path = file
    if not file.startswith('/') or file.startswith(':', 1):
            working_path = os.getcwd()
            file_path = os.path.join(working_path, file)
    return file_path


def get_vms(content, vimtype=[vim.VirtualMachine], name=None):
    """Get the vsphere object associated with a given text name or vimtype.
    """
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                        vimtype,
                                                        True)
    vms = list(container.view)
    container.Destroy()
    return vms


@top.command()
@click.argument('name', nargs=1)
@click.option('--context', '-c',
              help='The context to use for run the command, the default is <current-context>.',
              required=False)
@click.option('--filename', '-f',
              help='The context to use for run the command, the default is <current-context>.',
              required=False)
def vm(name, context, filename):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not isinstance(vm, vim.VirtualMachine):
            print('Virtual machine {} not found.'.format(name))
            raise SystemExit(1)
        perfResults = BuildQuery(
                            content,
                            [
                                'cpu.usage.average',
                                'cpu.usagemhz.average',
                                'mem.usage.average',
                                'net.usage.average'
                            ], 
                            vm)
        if not perfResults:
            print('Cannot fetch performance metrics.')
            raise SystemExit(-1)
        results = [
            perfResults[0].value[0].value[0] / 100,
            perfResults[0].value[1].value[0],
            perfResults[0].value[2].value[0] / 100,
            perfResults[0].value[3].value[0]
        ]
        print('{:<20}{:<20}{:<20}{:<20}{:<20}'.format(
                                        'VM',
                                        'CPU USAGE(%)',
                                        'CPU USAGE(MHz)',
                                        'MEM USAGE(%)',
                                        'NET USAGE(KBps)'))
        print('{:<20}{:<20}{:<20}{:<20}{:<20}'.format(
                                        vm.name,
                                        results[0],
                                        results[1],
                                        results[2],
                                        results[3]))
    
    except ContextNotFound:
        print('Context not found.')
        raise SystemExit()
    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        SystemExit(1)

@top.command()
@click.option('--context', '-c',
              help='The context to use for run the command, the default is <current-context>.',
              required=False)
@click.option('--filename', '-f',
              help='Path of the file containing the vms, one per line.',
              required=True)
@click.option('--csv', '-csv',
              help='Redirect the output in CSV format to specific file.',
              required=False)
def vms(context, filename, csv):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        filename = get_path(filename)
        output = io.StringIO()
        if csv:
            csv = get_path(csv)
        if not csv:
            print('{:<20}{:<20}{:<20}{:<20}{:<20}{:<20}'.format(
                                'VM',
                                'CPU USAGE(%)',
                                'CPU USAGE(MHz)',
                                'MEM USAGE (%)',                              
                                'MEM ACTIVE (GiB)',
                                'NET USAGE(KBps)'))
        f = open(filename, "r")
        vms = f.read().strip().split()
        total = len(vms)
        f.close()
        vc_vms = get_vms(content)
        iteration = 0
        for vm in vc_vms:
            if not len(vms) == 0 and vm.name in vms:       
                perfResults = BuildQuery(
                                    content,
                                    [
                                        'cpu.usage.average',
                                        'cpu.usagemhz.average',
                                        'mem.usage.average',
                                        'mem.active.average',
                                        'net.usage.average'
                                    ], 
                                    vm)
                if not perfResults:
                    if csv:
                        print("vm.name,off", file=output)
                        continue #raise SystemExit(-1)
                        iteration += 1
                    else:
                        print(vm.name)
                        continue #raise SystemExit(-1)
                results = [
                    perfResults[0].value[0].value[0] / 100,
                    perfResults[0].value[1].value[0],
                    perfResults[0].value[2].value[0] / 100,
                    round(perfResults[0].value[3].value[0] / (1024 * 1024), 2),
                    perfResults[0].value[4].value[0]
                ]
                if csv:               
                    print('{},{},{},{},{},{}'.format(
                                                vm.name,
                                                results[0],
                                                results[1],
                                                results[2],
                                                results[3],
                                                results[4]), file=output)
                    iteration += 1
                else:
                    print('{:<20}{:<20}{:<20}{:<20}{:<20}{:<20}'.format(
                                                vm.name,
                                                results[0],
                                                results[1],
                                                results[2],
                                                results[3],
                                                results[4]))
                vms.remove(vm.name)

                if csv:
                    percents = "{0:.1f}".format(100 * (iteration / total))
                    sys.stdout.write('\r{}%'.format(percents))

        if csv:
            for vm in vms:
                print("{},notfound".format(vm), file=output)
                iteration += 1
                percents = "{0:.1f}".format(100 * (iteration / total))
                sys.stdout.write('\r{}%'.format(percents))
            with open (csv, 'w') as fd:
                output.seek (0)
                shutil.copyfileobj (output, fd)
        output.close()

    
    except ContextNotFound:
        print('Context not found.')
        raise SystemExit()
    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise e #SystemExit(1)

@top.command()
@click.argument('name', nargs=1)
@click.option('--context', '-c',
              help='the context you want to use for run this command, \
                    default is current-context.',
              required=False)
def host(name, context):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        host = get_obj(content, [vim.HostSystem], name)
        if not isinstance(host, vim.HostSystem):
            print('Host {} not found.'.format(name))
            raise SystemExit(1)
        perfResults = BuildQuery(
            content,
            [
                'cpu.usage.average',
                'cpu.usagemhz.average',
                'mem.usage.average',
                'mem.active.average',
                'net.usage.average'
            ], 
            host
        )
        if not perfResults:
            print('Cannot fetch performance metrics.')
            raise SystemExit(-1)
        results = [
            perfResults[0].value[0].value[0] / 100,
            perfResults[0].value[1].value[0], 
            perfResults[0].value[2].value[0] / 100,
            round(perfResults[0].value[3].value[0] / (1024 * 1024), 2),
            perfResults[0].value[4].value[0]
        ]
        print('{:<36.33}{:<20}{:<20}{:<20}{:<20}{:<20}'.format(
            'HOST',
            'CPU USAGE(%)',
            'CPU USAGE(MHz)',
            'MEM USAGE(%)',
            'MEM ACTIVE(GiB)',
            'NET USAGE(KBps)'
            )
        )
        print('{:<36.33}{:<20}{:<20}{:<20}{:<20}{:<20}'.format(
            host.name,
            results[0],
            results[1],
            results[2],
            results[3],
            results[4]
            )
        )
        
    except ContextNotFound:
        print('Context not found.')
        raise SystemExit()
    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(1)


@top.command()
@click.option('--context', '-c',
              help='the context you want to use for run this command, \
                    default is current-context.',
              required=False)
def perfs(context):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        print_perfs(content)
        #print(perfs)

    except ContextNotFound:
        print('Context not found.')
        raise SystemExit()
    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(1)