import sys

import click
from pyVmomi import vim, vmodl

from vctl.helpers.helpers import load_context, jsonify
from vctl.helpers.vmware import get_obj, procs_obj
from vctl.helpers.auth import inject_token
from vctl.helpers.utils import waiting
from vctl.exceptions.exceptions import ContextNotFound
from vctl.objects.snapshot import snapshot
from vctl.objects.logs import logs


@click.group()
@click.option('--context', '-c',
              help='The context to use for run the command, the default is <current-context>.',
              required=False)
@click.option('--name', '-n',
              help='The name of the virtual machine on which to run the command.',
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
        try:
            if state == 'on':
                task = vm.PowerOnVM_Task()
            elif state == 'off':
                task = vm.PowerOffVM_Task()
            if wait:
                waiting(task)
        except:
            raise

    except ContextNotFound:
        raise SystemExit('Context not found.')
    except vim.fault.NotAuthenticated:
        raise SystemExit('Context expired.')
    except vmodl.MethodFault as e:
        raise SystemExit('Caught vmodl fault: ' + e.msg)
    except Exception as e:
        print('Caught error:', e)


@vm.command()
@click.option('--username', '-user', '-u',
              help='The desiderd state for the virtual machine.',
              required=True)
@click.option('--password', '-pwd', '-p',
              help='Wait for the task to complete.',
              required=True)
@click.pass_context
def get_procs(ctx, username, password):
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not hasattr(vm, '_moId'):
            raise SystemExit('Specified vm not found.')
        tools_status = vm.guest.toolsStatus
        if (tools_status == 'toolsNotInstalled' or
                tools_status == 'toolsNotRunning'):
            raise SystemExit(
                'VMwareTools is either not running or not installed.')
        creds = vim.vm.guest.NamePasswordAuthentication(
            username=username, password=password)
        try:
            pm = content.guestOperationsManager.processManager
            processes = pm.ListProcessesInGuest(vm, creds)
            procs_list = procs_obj(processes)
            jsonify(procs_list)
        except:
            raise

    except ContextNotFound:
        raise SystemExit('Context not found.')
    except vim.fault.NotAuthenticated:
        raise SystemExit('Context expired.')
    except vmodl.MethodFault as e:
        raise SystemExit('Caught vmodl fault: ' + e.msg)
    except Exception as e:
        print('Caught error:', e)


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
        if not hasattr(vm, '_moId'):
            raise SystemExit('Specified vm not found.')
        try:
            vm.UnregisterVM()
        except:
            raise

    except ContextNotFound:
        raise SystemExit('Context not found.')
    except vim.fault.NotAuthenticated:
        raise SystemExit('Context expired.')
    except vmodl.MethodFault as e:
        raise SystemExit('Caught vmodl fault: ' + e.msg)
    except Exception as e:
        print('Caught error:', e)


@vm.command()
@click.option('--folder', '-f',
              help='Context you want to use for run this command, default is current-context.',
              required=False)
@click.option('--host', '-h',
              help='Virtual Machine on which to create the snapshot.',
              required=True)
@click.option('--path', '-path',
              help='Name for the snapshot.',
              required=True)
@click.option('--pool', '-pool',
              help='Name for the snapshot.',
              required=False)
@click.option('--template', '-t',
              help='Wait for the task to complete.',
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
        if folder is not None:
            folder = get_obj(content, [vim.Folder], folder)
        else:
            folder = get_obj(content, [vim.Folder], 'vm')
        if pool is not None:
            pool = get_obj(content, [vim.ResourcePool], pool)
        else:
            pool = get_obj(content, [vim.ResourcePool], 'Resources')
        host = get_obj(content, [vim.HostSystem], host)
        if not hasattr(host, '_moId'):
            raise SystemExit('Specified host not found.')
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
        raise SystemExit('Context not found.')
    except vim.fault.NotAuthenticated:
        raise SystemExit('Context expired.')
    except vmodl.MethodFault as e:
        raise SystemExit('Caught vmodl fault: ' + e.msg)
    except Exception as e:
        print('Caught error:', e)


###
import ssl
import sys
import time
import OpenSSL
import webbrowser
###

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
            raise SystemExit('Specified vm not found.')
        vm_moid = vm._moId
        instanceUuid = si.content.about.instanceUuid
        session_manager = content.sessionManager
        session = session_manager.AcquireCloneTicket()
        vc_cert = ssl.get_server_certificate((context['vcenter'], 443))
        vc_pem = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                                 vc_cert)
        vc_fingerprint = vc_pem.digest('sha1')
        url = "http://" + context['vcenter'] + "/ui/webconsole.html?vmId=" \
              + str(vm_moid) + "&vmName=" + name + "&serverGuid=" + instanceUuid + "&host=" + context['vcenter'] \
              + "&sessionTicket=" + session + "&thumbprint=" + vc_fingerprint.decode('UTF-8')
        webbrowser.open(url, new=2)
        time.sleep(5)
    except:
        raise


