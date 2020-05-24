import os
from pathlib import Path

import click

from vctl.config.subcmds import (
    create, rename, use, test, remove, close)
from vctl.helpers.helpers import load_config
from vctl.exceptions.exceptions import ConfigNotFound


@click.group()
def config():
    """
    Config and contexts related subcommands.
    """
    pass


@config.group()
def context():
    """
    Context related subcommands.
    """
    pass

context.add_command(create)
context.add_command(rename)
context.add_command(use)
context.add_command(test)
context.add_command(remove)
context.add_command(close)


@config.command()
def get_contexts():
    """Return all contexts in table formatted style.
    """
    try:
        config = load_config()
        current_context = config['current-context']
        print('{:<10}{:<30}{:<30}{:<30}{:<30}'.format(
              'CURRENT', 'CONTEXT-NAME', 'USERNAME', 'VCENTER', 'VERSION'))
        for _context in config['contexts']:
            if _context['name'] == current_context:
                print('{:<10}{:<30}{:<30}{:<30}{:<30}'.format('*',
                                                              _context['name'],
                                                              _context['context']['username'],
                                                              _context['context']['vcenter'],
                                                              _context['context']['apiversion']))
            else:
                print('{:<10}{:<30}{:<30}{:<30}{:<30}'.format('',
                                                              _context['name'],
                                                              _context['context']['username'],
                                                             _context['context']['vcenter'],
                                                              _context['context']['apiversion']))
    except ConfigNotFound:
        print('Contexts not found, config file does not exists.')


@config.command()
def view():
    """
    Return vctl configuration file.
    """
    home = str(Path.home())
    config_path = os.path.join(home, '.vctl', 'config')
    try:
        with open(config_path, 'r') as config_file:
            config = config_file.read()
            print(config, end='')
    except FileNotFoundError:
        print('Config file does not exists yet, creating a new context will automatically create it.')
    except Exception as e:
        print("Caught error: ", e)
