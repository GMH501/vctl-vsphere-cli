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
              help='The context to use for run the command, the default is <current-context>.',
              required=False)
def vm(name, context):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not isinstance(vm, vim.VairtualMachine):
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
        raise SystemExit(1)


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
                            host)
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
