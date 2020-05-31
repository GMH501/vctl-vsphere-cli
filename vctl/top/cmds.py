import click
from pyVmomi import vim, vmodl

from vctl.helpers.helpers import load_context
from vctl.helpers.auth import inject_token
from vctl.helpers.perf import BuildQuery
from vctl.helpers.vmware import get_obj
from vctl.exceptions.exceptions import ContextNotFound


@click.group()
def top():
    """
    """
    pass


@top.command()
@click.argument('name', nargs=1)
@click.option('--context', '-c',
              help='the context you want to use for run this command, \
                    default is current-context.',
              required=False)
def vm(name, context):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if vm is None:
            raise SystemExit('Virtual Machine not found.')
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
            raise SystemExit('Cannot fetch performance metrics.')
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
        raise SystemExit('Context not found.')
    except vim.fault.NotAuthenticated:
        raise SystemExit('Context expired.')
    except vmodl.MethodFault as e:
        raise SystemExit('Caught vmodl fault: ' + e.msg)
    except Exception as e:
        #print('Caught error:', e)
        raise e


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
        if host is None:
            raise SystemExit('Host not found.')
        perfResults = BuildQuery(
                            content,
                            [
                                'cpu.usage.average',
                                'cpu.usagemhz.average',
                                'mem.usage.average',
                                'mem.active.average',
                                'net.usage.average'
                            ], 
                            host)
        if not perfResults:
            raise SystemExit('Cannot fetch performance metrics.')
        results = [
            perfResults[0].value[0].value[0] / 100,
            perfResults[0].value[1].value[0], 
            perfResults[0].value[2].value[0] / 100,
            round(perfResults[0].value[3].value[0] / (1024 * 1024), 2),
            perfResults[0].value[4].value[0]
        ]
        print('{:<30}{:<20}{:<20}{:<20}{:<20}{:<20}'.format(
                                                'HOST',
                                                'CPU USAGE(%)',
                                                'CPU USAGE(MHz)',
                                                'MEM USAGE(%)',
                                                'MEM ACTIVE(GiB)',
                                                'NET USAGE(KBps)'))
        print('{:<30}{:<20}{:<20}{:<20}{:<20}{:<20}'.format(
                                                host.name,
                                                results[0],
                                                results[1],
                                                results[2],
                                                results[3],
                                                results[4]))
        
    except ContextNotFound:
        raise SystemExit('Context not found.')
    except vim.fault.NotAuthenticated:
        raise SystemExit('Context expired.')
    except vmodl.MethodFault as e:
        raise SystemExit('Caught vmodl fault: ' + e.msg)
    except Exception as e:
        print('Caught error:', e)
