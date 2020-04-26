import click
from pyvim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl, SoapStubAdapter
import yaml

from vc.helpers.helpers import get_unverified_context, random_string, load_config, dump_config, setup_config, create_context

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
def context(vcenter, username, password):
    try:
        si = SmartConnect(host=vcenter, 
                          user=username, 
                          pwd=password, 
                          sslContext=get_unverified_context())
        context = create_context(si, vcenter, username)
        try: 
            load_config()
        except FileNotFoundError:
            setup_config()
        finally:
            config = load_config()
            config['contexts'].append(context)
            config['current-context'] = context['name']
            dump_config(config)
            return
    except Exception as e:
        print(e)

