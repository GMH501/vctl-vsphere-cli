import click
import yaml
from pyVmomi import vim

from vctl.helpers.vmware import get_obj, get_vm_hardware_lists, get_vm_obj, get_host_obj
from vctl.helpers.helpers import load_context, jsonify
from vctl.helpers.auth import inject_token
from vctl.exceptions.exceptions import ContextNotFound


@click.command()
@click.argument('name', nargs=1)
@click.option('--context', '-c',
              help='the context you want to use for run this command, default is current-context.',
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
        host_obj = get_host_obj(host)
        jsonify(host_obj)

    except ContextNotFound:
        print('Context not found.')
        raise SystemExit(-1)
    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(-1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(-1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(-1)


@click.command()
@click.argument('name', nargs=1)
@click.option('--context', '-c',
              help='the context you want to use for run this command, default is current-context.',
              required=False)
def vm(name, context):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not isinstance(vm, vim.VirtualMachine):
            print('Virtual Machine {} not found.'.format(name))
            raise SystemExit(1)
        vm_obj = get_vm_obj(vm)
        jsonify(vm_obj)

    except ContextNotFound:
        print('Context not found.')
        raise SystemExit(-1)
    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(-1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(-1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(-1)

