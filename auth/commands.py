from pyvim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl, SoapStubAdapter
from helpers.context_helper import get_unverified_context
import click
import yaml


@click.command()
@click.option('--vcenter', '-v', 
              help='vcenter you want to conntect to.',
              required=True)
@click.option('--username', '-u',
              help='username to connect to vcenter.',
              required=True)
@click.option('--password', '-p',
              help='password to connect to vcenter.',
              required=True)  
def auth(vcenter, username, password):
    try:
        si = SmartConnect(host=vcenter, 
                          user=username, 
                          pwd=password, 
                          sslContext=get_unverified_context())
        context_name = vcenter + random_string
        context = {{'vcenter': vcenter, 
                   'username': username, 
                   'cookie': si._stub.cookie},
                   'name': context_name
                  }
        with open('config.yaml', 'w+') as stream:
            yaml.dump(session, stream)
        Disconnect(si)
        return
    except Exception as e:
        print(e)
        return