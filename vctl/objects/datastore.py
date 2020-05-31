import sys
import requests
import urllib3
import re

import click
from bs4 import BeautifulSoup
from pyVmomi import vim, vmodl

from vctl.helpers.helpers import load_context, jsonify
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
        datastore = get_obj(content, [vim.Datastore], ds_name)
        if not remote_file.startswith("/"):
            remote_file = "/" + remote_file
        resource = "/folder" + remote_file
        params = {"dsName": datastore.info.name,
                  "dcPath": dc.name}
        http_url = "https://" + context['vcenter'] + ":443" + resource
        client_cookie = si._stub.cookie
        cookie_name = client_cookie.split("=", 1)[0]
        find = re.findall(r'(["|\']([a-z0-9]+-)+[a-z0-9]+["|\']);.*Path=([^\s]*);', client_cookie)[0]
        cookie_value, cookie_path = find[0], find[2]
        cookie_text = " " + cookie_value + "; $Path=" + cookie_path
        cookie = dict()
        cookie[cookie_name] = cookie_text
        headers = {'Content-Type': 'application/octet-stream'}
        with open(local_file, "rb") as f:
            requests.put(
                        http_url,
                        params=params,
                        data=f,
                        headers=headers,
                        cookies=cookie,
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
def browse(ctx, datacenter, folder):
    ds_name = ctx.name
    context = ctx.context
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        dc = get_obj(content, [vim.Datacenter], datacenter)
        datastore = get_obj(content, [vim.Datastore], ds_name)
        if not folder.startswith('/'):
            folder = "/" + folder
        resource = "/folder" + folder
        params = {"dsName": datastore.info.name,
                  "dcPath": dc.name}
        http_url = "https://" + context['vcenter'] + ":443" + resource
        client_cookie = si._stub.cookie
        cookie_name = client_cookie.split("=", 1)[0]
        find = re.findall(r'(["|\']([a-z0-9]+-)+[a-z0-9]+["|\']);.*Path=([^\s]*);', client_cookie)[0]
        cookie_value, cookie_path = find[0], find[2]
        cookie_text = " " + cookie_value + "; $Path=" + cookie_path
        cookie = dict()
        cookie[cookie_name] = cookie_text
        headers = {'Content-Type': 'application/octet-stream'}
        r = requests.get(
                    http_url,
                    params=params,
                    headers=headers,
                    cookies=cookie,
                    verify=False)
        html = r.text.split('\n')
        valid_lines = [line for line in html if ds_name in line]
        html_data = "".join(valid_lines)
        table_data = [[cell.text for cell in row("td")]
                        for row in BeautifulSoup(html_data, features="html.parser")("tr")]
        keys = ['name', 'lastModified', 'size']
        output = []
        for values in table_data:
            output.append(dict(zip(keys, values)))
        if "Parent" in output[0]['name']:
            output.pop(0)
        jsonify(output)
        
    except vmodl.MethodFault as e:
        print("Caught vmodl fault : " + e.msg)
        raise SystemExit(-1)

    raise SystemExit(0)