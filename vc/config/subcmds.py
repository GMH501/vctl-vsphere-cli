import click
from pyvim.connect import SmartConnect

from vc.helpers.helpers import (get_unverified_context, load_config, dump_config, setup_config,
                                create_context)

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
def create(vcenter, username, password):
    """
    Open new context.\n
    ex.: vc config context create -v <vcenter> -u <username> -p <password>
    """
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


@click.command()
@click.argument('current', nargs=1)
@click.argument('new', nargs=1)
def rename(current, new):
    """
    Rename a context name from CURRENT name to NEW name.\n
    ex.: vc config context rename <current> <new>
    """
    config = load_config()
    current_context = config['current-context']
    for context in config['contexts']:
        if context['name'] == current:
            if context['name'] == current_context:
                context['name'] = new
                config['current-context'] = new
                dump_config(config)
                return
            context['name'] = new
            dump_config(config)
            return
    print('Context {} not found'.format(current))


@click.command()
def contexts():
    """
    Return all contexts in formatted style.
    """
    try:
        config = load_config()
        current_context = config['current-context']
        print('{:<10}{:<30}{:<30}{:<30}'.format('CURRENT', 'CONTEXT-NAME', 'VCENTER', 'USERNAME'))
        for _context in config['contexts']:
            if _context['name'] == current_context:
                print('{:<10}{:<30}{:<30}{:<30}'.format('*',
                                                        _context['name'],
                                                        _context['context']['vcenter'],
                                                        _context['context']['username']))
            else:
                print('{:<10}{:<30}{:<30}{:<30}'.format('',
                                                        _context['name'],
                                                        _context['context']['vcenter'],
                                                        _context['context']['username']))
    except FileNotFoundError:
        print('No contexts found, consider opening new one with: vc config open')
