import os
from pathlib import Path

import click

from vctl.config.subcmds import (
    create, rename, use, test, remove, close, contexts)


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


@config.group()
def get():
    """
    Return all saved contexts.
    """
    pass

get.add_command(contexts)


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
