import re
import sys
import urllib3

import click
from pyVmomi import vim, vmodl
import requests


from vctl.objects.datastore import get_http_cookie
from vctl.helpers.helpers import load_context, scrape
from vctl.helpers.vmware import get_obj
from vctl.helpers.auth import inject_token


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@click.group()
def logs():
    """

    """
    pass


@logs.command()
@click.option('--file', '-f',
              help='Context you want to use for run this command, default is current-context.',
              required=True)            
@click.pass_context
def show(ctx, file):
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not isinstance(vm, vim.VirtualMachine):
            raise SystemExit('Specified vm not found.')
        dc = vm.summary.runtime.host.parent.parent.parent
        log_dir = vm.config.files.logDirectory
        datastore_name = re.findall(r'\[(.*)\]', log_dir)[0]
        folder_name = re.findall(r'\[.*\](.*)', log_dir)[0].strip()
        resource = "/folder/" + folder_name
        if file.startswith('/'):
            file = file[1:]
        resource = resource + file
        http_url = "https://" + context['vcenter'] + ":443" + resource
        params = {"dsName": datastore_name,
                  "dcPath": dc.name}
        headers = {'Content-Type': 'application/octet-stream'}
        http_cookie = get_http_cookie(si._stub.cookie)
        r = requests.get(
                        http_url,
                        params=params,
                        headers=headers,
                        cookies=http_cookie,
                        verify=False,
                        stream=True
                        )
        print(r.text)
    except vmodl.MethodFault as e:
        print("Caught vmodl fault : " + e.msg)
        sys.exit(-1)


@logs.command()
@click.pass_context
def list(ctx):
    name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        vm = get_obj(content, [vim.VirtualMachine], name)
        if not isinstance(vm, vim.VirtualMachine):
            raise SystemExit('Specified vm not found.')
        dc = vm.summary.runtime.host.parent.parent.parent
        log_dir = vm.config.files.logDirectory
        datastore_name = re.findall(r'\[(.*)\]', log_dir)[0]
        folder_name = re.findall(r'\[.*\](.*)', log_dir)[0].strip()
        resource = "/folder/" + folder_name
        http_url = "https://" + context['vcenter'] + ":443" + resource
        params = {"dsName": datastore_name,
                  "dcPath": dc.name}
        headers = {'Content-Type': 'application/octet-stream'}
        http_cookie = get_http_cookie(si._stub.cookie)
        r = requests.get(
                    http_url,
                    params=params,
                    headers=headers,
                    cookies=http_cookie,
                    verify=False)
        if not r:
            print('Caught error: {} {}'.format(r.status_code, r.reason))
            raise SystemExit(-1)
        output = scrape(r.text, search='log')
        print('{:<40}{:<30}{:<20}'.format('NAME',
                                          'LAST-MODIFIED',
                                          'SIZE'))
        for _file in output:
            print('{:<40}{:<30}{:<20}'.format(_file['name'],
                                              _file['lastModified'],
                                              _file['size']))

    except IndexError:
        print('Invalid operation.')
        raise SystemExit(-1)  
    except vmodl.MethodFault as e:
        print("Caught vmodl fault : " + e.msg)
        raise SystemExit(-1)



