import sys
import urllib3
import re

import click
from pyVmomi import vim, vmodl
import requests

from vctl.helpers.helpers import load_context, scrape
from vctl.helpers.vmware import get_obj
from vctl.helpers.auth import inject_token
from vctl.exceptions.exceptions import ContextNotFound


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@click.group()
@click.option('--context', '-c',
              help='The context to use for run the command, the default is <current-context>.',
              required=False)
@click.option('--name', '-n',
              help='The name of the virtual machine on which to run the command.',
              required=True)
@click.pass_context
def datastore(ctx, context, name):
    ctx = click.Context
    ctx.name = name
    ctx.context = context
    pass


def get_http_cookie(token):
    cookie_name = token.split("=", 1)[0]
    regex = r'(["|\']([^\s]+)["|\']);.*Path=([^\s]*);'
    find = re.findall(regex, token)[0]
    cookie_value, cookie_path = find[0], find[2]
    cookie_text = " " + cookie_value + "; $Path=" + cookie_path
    return {cookie_name: cookie_text}


def _mkticket( content, url, method='httpGet'):
    spec = vim.SessionManager.HttpServiceRequestSpec()
    spec.url = url
    spec.method = method
    sm = content.sessionManager
    ticket = sm.AcquireGenericServiceTicket(spec=spec)
    return {'vmware_cgi_ticket': ticket.id}


@datastore.command()
@click.option('--datacenter', '-d',
              help='Context you want to use for run this command, default is current-context.',
              required=True)
@click.option('--remote-file', '-r',
              help='Context you want to use for run this command, default is current-context.',
              required=True)
@click.option('--local-file', '-l',
              help='Context you want to use for run this command, default is current-context.',
              required=True)
@click.pass_context
def upload(ctx, datacenter, remote_file, local_file):
    ds_name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        dc = get_obj(content, [vim.Datacenter], datacenter)
        if not dc:
            print('Datacenter not found.')
            raise SystemExit(-1)
        datastore = get_obj(content, [vim.Datastore], ds_name)
        if not datastore:
            print('Datastore not found.')
            raise SystemExit(-1)
        if not remote_file.startswith("/"):
            remote_file = "/" + remote_file
        resource = "/folder" + remote_file
        http_url = "https://" + context['vcenter'] + ":443" + resource
        params = {"dsName": datastore.info.name,
                  "dcPath": dc.name}
        http_cookie = get_http_cookie(si._stub.cookie)
        headers = {'Content-Type': 'application/octet-stream'}
        with open(local_file, "rb") as f:
            requests.put(
                        http_url,
                        params=params,
                        data=f,
                        headers=headers,
                        cookies=http_cookie,
                        verify=False)

    except vmodl.MethodFault as e:
        print("Caught vmodl fault : " + e.msg)
        raise SystemExit(-1)

    raise SystemExit(0)


@datastore.command()
@click.option('--datacenter', '-d',
              help='Context you want to use for run this command, default is current-context.',
              required=True)
@click.option('--folder', '-f',
              help='Context you want to use for run this command, default is current-context.',
              required=False,
              default='/')
@click.pass_context
def browse(ctx, datacenter, folder, json):
    ds_name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        dc = get_obj(content, [vim.Datacenter], datacenter)
        if not dc:
            print('Datacenter not found.')
            raise SystemExit(-1)
        datastore = get_obj(content, [vim.Datastore], ds_name)
        if not datastore:
            print('Datastore not found.')
            raise SystemExit(-1)
        if not folder.startswith('/'):
            folder = "/" + folder
        resource = "/folder" + folder
        http_url = "https://" + context['vcenter'] + ":443" + resource
        params = {"dsName": datastore.info.name,
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
        output = scrape(r.text, search=ds_name)
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


@datastore.command()
@click.option('--datacenter', '-d',
              help='Context you want to use for run this command, default is current-context.',
              required=True)
@click.option('--file', '-f',
              help='File name you want to remove from the datastore.',
              required=False,
              default='/')
@click.pass_context
def delete(ctx, datacenter, file):
    ds_name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        dc = get_obj(content, [vim.Datacenter], datacenter)
        if not dc:
            print('Datacenter not found.')
            raise SystemExit(-1)
        datastore = get_obj(content, [vim.Datastore], ds_name)
        if not datastore:
            print('Datastore not found.')
            raise SystemExit(-1)
        if not folder.startswith('/'):
            folder = "/" + folder
        resource = "/folder" + file
        http_url = "https://" + context['vcenter'] + ":443" + resource
        params = {"dsName": datastore.info.name,
                  "dcPath": dc.name}
        headers = {'Content-Type': 'application/octet-stream'}
        http_cookie = get_http_cookie(si._stub.cookie)
        r = requests.delete(
                            http_url,
                            params=params,
                            headers=headers,
                            cookies=http_cookie,
                            verify=False)
        if not r:
            print('Caught error: {}'.format(r.reason))
            raise SystemExit(-1)
        
    except vmodl.MethodFault as e:
        print("Caught vmodl fault : " + e.msg)
        raise SystemExit(-1)


@datastore.command()
@click.option('--datacenter', '-d',
              help='Context you want to use for run this command, default is current-context.',
              required=True)
@click.option('--file', '-f',
              help='Context you want to use for run this command, default is current-context.',
              required=True)
@click.option('--local', '-l',
              help='Context you want to use for run this command, default is current-context.',
              required=True)             
@click.pass_context
def download(ctx, datacenter, file, local):
    ds_name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        dc = get_obj(content, [vim.Datacenter], datacenter)
        if not dc:
            print('Datacenter not found.')
            raise SystemExit(-1)
        datastore = get_obj(content, [vim.Datastore], ds_name)
        if not datastore:
            print('Datastore not found.')
            raise SystemExit(-1)
        if not file.startswith('/'):
            file = "/" + file
        resource = "/folder" + file
        http_url = "https://" + context['vcenter'] + ":443" + resource
        params = {"dsName": datastore.info.name,
                  "dcPath": dc.name}
        headers = {'Content-Type': 'application/octet-stream'}
        http_cookie = get_http_cookie(si._stub.cookie)
        with open(local, 'wb') as f:
            r = requests.get(
                            http_url,
                            params=params,
                            headers=headers,
                            cookies=http_cookie,
                            verify=False,
                            stream=True
                            )
            total_length = r.headers.get('content-length')
            #print(r.headers)
            total_length = int(total_length)
            dl = 0
            for chunk in r.iter_content(chunk_size=4096): 
                dl += len(chunk)
                f.write(chunk)
                done = dl / total_length
                progress = round(done * 50)
                blanks = 50 - progress
                sys.stdout.write('\r {:<3}% [{}>{}] {}/{}'.format(
                                                        round(done * 100),
                                                        '=' * progress,
                                                        ' ' * blanks,
                                                        dl,
                                                        total_length))

    except vmodl.MethodFault as e:
        print("Caught vmodl fault : " + e.msg)
        sys.exit(-1)