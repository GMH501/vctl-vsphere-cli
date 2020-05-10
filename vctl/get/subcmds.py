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
def hosts(context):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        hosts = get_obj(content, [vim.HostSystem])
        print('{:<30}{:<15}{:<15}{:<20}{:<30}'.format('NAME',
                                                      'MEMORY %',
                                                      'CPU %',
                                                      'PARENT',
                                                      'VERSION'))
        for host in hosts:
            name = host.name
            parent = host.parent.name
            version = host.config.product.fullName
            print('{:<30}{:<15}{:<15}{:<20}{:<30}'.format(name,
                                                          '',
                                                          '',
                                                          parent,
                                                          version))

    except ContextNotFound:
        print('Context not found.')
    except Exception as e:
        print('Caught error:', e)


@click.command()
def clusters():
    try:
        context = load_context()
        si = inject_token(context)
        content = si.content
        hosts = get_obj(content, [vim.ComputeResource])
        print('{:<30}{:<15}{:<15}{:<30}'.format(
              'NAME', 'MEMORY %', 'CPU %', 'SPEC'))
        for host in hosts:
            print('{:<30}{:<15}{:<15}{:<30}'.format(host.name,
                                                    '',
                                                    '',
                                                    host.parent.name))

    except ContextNotFound:
        print('Context not found.')
    except Exception as e:
        print('Caught error:', e)


@click.command()
def vms():
    try:
        context = load_context()
        si = inject_token(context)
        content = si.content
        vms = get_obj(content, [vim.VirtualMachine])
        print('{:<30}{:<15}{:<15}{:<20}{:<30}'.format('NAME',
                                                      'MEMORY %',
                                                      'CPU %',
                                                      'PARENT',
                                                      'SPEC'))
        for vm in vms:
            print('{:<30}{:<15}{:<15}{:<20}{:<30}'.format(vm.name,
                                                          '',
                                                          '',
                                                          '',
                                                          ''))
    except ContextNotFound:
        print('Context not found.')
    except Exception as e:
        print('Caught error:', e)
