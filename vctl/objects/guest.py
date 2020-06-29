import re
import time
import sys

import click
from pyVmomi import vim, vmodl
import requests

from vctl.exceptions.exceptions import ContextNotFound
from vctl.helpers.auth import inject_token
from vctl.helpers.helpers import load_context, jsonify
from vctl.helpers.utils import waiting
from vctl.helpers.vmware import get_obj, procs_obj


@click.group()
@click.option('--context', '-c',
              help='The context to use for run the command, the default is <current-context>.',
              required=False)
@click.argument('name', nargs=1,
              required=True)
@click.pass_context
def guest(ctx, context, name):
    ctx = click.Context
    ctx.name = name
    ctx.context = context
    pass


@guest.command()
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
def envs(ctx, username, password, json):
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
        variables = pm.ReadEnvironmentVariableInGuest(vm, creds)
        for variable in variables:
            print(variable)

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(1)


@guest.command()
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
                if proc['exitCode'] is None:
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


@guest.command()
@click.option('--from-remote', "remote",
              help='Initiate the file transfer from remote (guest) to local (client)',
              nargs=2,
              required=False)
@click.option('--from-local', "local",
              help='Initiate the file transfer from local (client) to guest (remote).',
              nargs=2,
              required=False)
@click.option('--username', '-user', '-u',
              help='The desiderd state for the virtual machine.',
              required=True)
@click.option('--password', '-pwd', '-p',
              help='Wait for the task to complete.',
              required=True)
@click.pass_context
def transfer(ctx, from_local, from_remote, username, password):
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
        fm = content.guestOperationsManager.fileManager
        url = fm.InitiateFileTransferToGuest(
            vm,
            creds,
            '/pippo',
            vim.vm.guest.FileManager.FileAttributes(),
            0,
            False
        )
        url = re.sub(r"^https://\*:", "https://" + context['vcenter'] + ":", url)
        resp = requests.put(url, data=fileinmemory, verify=False)
        if not resp.status_code == 200:
            print("Error while uploading file")
        else:
            print("Successfully uploaded file") ### TODO TO_COMPLETE
 

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
