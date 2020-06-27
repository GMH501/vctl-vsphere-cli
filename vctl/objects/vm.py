import time
import ssl
import sys
import webbrowser

import click
import OpenSSL
from pyVmomi import vim, vmodl

from vctl.exceptions.exceptions import ContextNotFound
from vctl.helpers.auth import inject_token
from vctl.helpers.helpers import load_context, jsonify
from vctl.helpers.utils import waiting
from vctl.helpers.vmware import get_obj, procs_obj
from vctl.objects.logs import logs
from vctl.objects.snapshot import snapshot


@click.group()
@click.option('--context', '-c',
              help='The context to use for run the command, the default is <current-context>.',
              required=False)
@click.argument('vm_name', nargs=1,
              required=True)
@click.pass_context
def vm(ctx, context, vm_name):
    """Commands to manage virtual machine instances.

    # ex.: vctl vm VM_TEST0 register --path [datastore1]VM_TEST0/VM_TEST0.vmx --host esxi.home.lab

    # ex.: vctl vm VM_TEST0 power --state on

    # ex.: vctl vm VM_TEST0 procs -u root -p mypassword
    """
    ctx = click.Context
    ctx.name = vm_name
    ctx.context = context
    pass


vm.add_command(snapshot)
vm.add_command(logs)


@vm.command()
@click.pass_context
def console(ctx):
    """Open the HTML5 console.
    """
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not isinstance(vm, vim.VirtualMachine):
            print('Virtual Machine {} not found.'.format(name))
            raise SystemExit(1)
        vm_moid = vm._moId
        instanceUuid = si.content.about.instanceUuid
        session_manager = content.sessionManager
        session = session_manager.AcquireCloneTicket()
        vc_cert = ssl.get_server_certificate((context['vcenter'], 443))
        vc_pem = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, vc_cert)
        vc_fingerprint = vc_pem.digest('sha1')
        url = "http://" + context['vcenter'] + "/ui/webconsole.html?vmId=" \
            + vm_moid + "&vmName=" + name + "&serverGuid=" + instanceUuid + "&host=" + context['vcenter'] \
            + "&sessionTicket=" + str(session) + "&thumbprint=" + vc_fingerprint.decode('UTF-8')
        webbrowser.open(url, new=2)
        time.sleep(5)


    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(1)


@vm.command()
@click.option('--state', '-s',
              help='The desiderd state for the virtual machine.',
              type=click.Choice(['on', 'off']),
              required=True)
@click.option('--wait', '-w',
              help='Wait for the task to complete.',
              is_flag=True)
@click.pass_context
def power(ctx, state, wait):
    """Virtual machine power option.
    """
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not isinstance(vm, vim.VirtualMachine):
            print('Virtual Machine {} not found.'.format(name))
            raise SystemExit(1)
        if state == 'on':
            task = vm.PowerOnVM_Task()
        elif state == 'off':
            task = vm.PowerOffVM_Task()
        if wait:
            waiting(task)

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(1)


@vm.command()
@click.option('--json',
              help='Json formatted output.',
              is_flag=True)
@click.option('--username', '-user', '-u',
              help='Userame to login to guest operating system.',
              required=True)
@click.option('--password', '-pwd', '-p',
              help='Password to login to guest operating system.',
              required=True)
@click.pass_context
def procs(ctx, json, username, password):
    """List the processes in guest operating system.
    """
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not isinstance(vm, vim.VirtualMachine):
            print('Virtual Machine {} not found.'.format(name))
            raise SystemExit(1)
        tools_status = vm.guest.toolsStatus
        if (tools_status == 'toolsNotInstalled' or
                tools_status == 'toolsNotRunning'):
            print('VMwareTools is either not running or not installed.')
            raise SystemExit(1)
        creds = vim.vm.guest.NamePasswordAuthentication(
            username=username, password=password)
        pm = content.guestOperationsManager.processManager
        processes = pm.ListProcessesInGuest(vm, creds)
        procs_list = procs_obj(processes)
        if json:
            jsonify(procs_list)
        else:
            name_len = str(len(max([proc['name'] for proc in procs_list], key=len)) + 4)
            owner_len = str(len(max([proc['owner'] for proc in procs_list], key=len)) + 4)
            header_format = '{:<' + name_len + '}{:<8}{:<13}{:<' + owner_len + '}{:<35}'
            output_format = '{name:<' + name_len + '}{pid:<8}{exitCode:<13}{owner:<' + owner_len + '}{cmdLine:<75}'
            print(header_format.format(
                'NAME',
                'PID',
                'EXITCODE',
                'OWNER',
                'CMD'
                )
            )
            for proc in procs_list:
                print(output_format.format(**proc))

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(1)


@vm.command()
@click.option('--folder', '-f',
              help='Folder in which register the virtual machine (or template).',
              required=False)
@click.option('--host', '-h',
              help='The host on which register the virtual machine.',
              required=True)
@click.option('--path', '-path',
              help='The path of the vmx file for the virtual machine.',
              required=True)
@click.option('--pool', '-pool',
              help='The pool in which register the virtual machine.',
              required=False)
@click.option('--template', '-t',
              help='Register the virtual machine as a template.',
              is_flag=True)
@click.option('--wait', '-w',
              help='Wait for the task to complete.',
              is_flag=True)
@click.pass_context
def register(ctx, folder, host, path, pool, template, wait):
    """Register the virtual machine in the inventory.
    """
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        if folder is None:
            _folder = get_obj(content, [vim.Folder], 'vm')
        else:
            _folder = get_obj(content, [vim.Folder], folder)
        if not isinstance(_folder, vim.Folder):
            print('Folder {} not found.'.format(folder))
            raise SystemExit(1)  
        if pool is None:
            _pool = get_obj(content, [vim.ResourcePool], 'Resources')
        else:
            _pool = get_obj(content, [vim.ResourcePool], pool)
        if not isinstance(_pool, vim.ResourcePool):
            print('Pool {} not found.'.format(pool))
            raise SystemExit(1)   
        _host = get_obj(content, [vim.HostSystem], host)
        if not isinstance(_host, vim.HostSystem):
            print('Host {} not found.'.format(host))
            raise SystemExit(1)  
        if template:
            _pool = None
        if 'vmtx' in path:
            template = True
            _pool = None
        task = _folder.RegisterVM_Task(
            name=name,
            path=path,
            pool=_pool,
            asTemplate=template,
            host=_host)
        if wait:
            waiting(task)

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(1)


@vm.command()
@click.pass_context
def unregister(ctx):
    """Unregister the virtual machine from the inventory.
    """
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not isinstance(vm, vim.VirtualMachine):
            print('Virtual Machine {} not found.'.format(name))
            raise SystemExit(1)
        vm.UnregisterVM()

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(1)
