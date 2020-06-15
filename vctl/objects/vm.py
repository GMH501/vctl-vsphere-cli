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
@click.argument('name', nargs=1,
              required=True)
@click.pass_context
def vm(ctx, context, name):
    ctx = click.Context
    ctx.name = name
    ctx.context = context
    pass


vm.add_command(snapshot)
vm.add_command(logs)


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
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not hasattr(vm, '_moId'):
            raise SystemExit('Specified vm not found.')
        if state == 'on':
            task = vm.PowerOnVM_Task()
        elif state == 'off':
            task = vm.PowerOffVM_Task()
        if wait:
            waiting(task)

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


@vm.command()
@click.option('--json',
              help='Json formatted output.',
              is_flag=True)
@click.option('--username', '-user', '-u',
              help='The desiderd state for the virtual machine.',
              required=True)
@click.option('--password', '-pwd', '-p',
              help='Wait for the task to complete.',
              required=True)
@click.pass_context
def get_procs(ctx, json, username, password):
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not isinstance(vm, vim.VirtualMachine):
            print('Specified vm not found.')
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
                if proc['exitCode'] == None:
                    proc['exitCode'] = 'None'
                print(output_format.format(**proc))

    except ContextNotFound:
        print('Context not found.')
        raise SystemExit(1)
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
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not isinstance(vm, vim.VirtualMachine):
            print('Specified vm not found.')
            raise SystemExit(1)
        vm.UnregisterVM()

    except ContextNotFound:
        print('Context not found.')
        raise SystemExit(1)
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
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        if folder is None:
            folder = get_obj(content, [vim.Folder], 'vm')
        else:
            folder = get_obj(content, [vim.Folder], folder)
        if not isinstance(folder, vim.Folder):
            print('Specified folder not found.')
            raise SystemExit(1)     
        if pool is None:
            pool = get_obj(content, [vim.ResourcePool], 'Resources')
        else:
            pool = get_obj(content, [vim.ResourcePool], pool)
        if not isinstance(pool, vim.ResourcePool):
            print('Specified pool not found.')
            raise SystemExit(1)    
        host = get_obj(content, [vim.HostSystem], host)
        if not isinstance(host, vim.HostSystem):
            print('Specified host not found.')
            raise SystemExit(1)
        if template:
            pool = None
        if 'vmtx' in path:
            template = True
            pool = None
        task = folder.RegisterVM_Task(
            name=name,
            path=path,
            pool=pool,
            asTemplate=template,
            host=host)
        if wait:
            waiting(task)

    except ContextNotFound:
        print('Context not found.')
        raise SystemExit(1)
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
def open_console(ctx):
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not isinstance(vm, vim.VirtualMachine):
            print('Specified vm not found.')
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

    except ContextNotFound:
        print('Context not found.')
        raise SystemExit(1)
    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise 
