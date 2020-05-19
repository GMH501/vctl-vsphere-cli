import click
try:
    from pyVim.connect import SmartConnect
except:
    from pyvim.connect import SmartConnect

from vctl.helpers.helpers import (
    load_config, dump_config, setup_config, create_context, load_context)
from vctl.helpers.vmware import get_unverified_context
from vctl.exceptions.context_exceptions import ConfigNotFound, ContextNotFound
from vctl.helpers.auth import inject_token


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
    #ex.: vc config context create -v <vcenter> -u <username> -p <password>
    """
    try:
        si = SmartConnect(host=vcenter,
                          user=username,
                          pwd=password,
                          sslContext=get_unverified_context(),
                          connectionPoolTimeout=-1)
        context = create_context(si, vcenter, username)
        try:
            load_config()
        except ConfigNotFound:
            setup_config()
        finally:
            config = load_config()
            config['contexts'].append(context)
            config['current-context'] = context['name']
            dump_config(config)
            return
    except Exception as e:
        print('Caught exception: ', e)


@click.command()
@click.argument('current', nargs=1)
@click.argument('new', nargs=1)
def rename(current, new):
    """
    Rename a context name from CURRENT name to NEW name.\n
    #ex.: vc config context rename <current> <new>
    """
    if current != new:
        try:
            config = load_config()
            current_context = config['current-context']
            for _context in config['contexts']:
                if _context['name'] == current:
                    if _context['name'] == current_context:
                        _context['name'] = new
                        config['current-context'] = new
                        dump_config(config)
                        return
                    _context['name'] = new
                    dump_config(config)
                    return
            print('Context not found.')
        except ConfigNotFound as e:
            print(e.message)
    return


@click.command()
@click.option('--context', '-c',
              help='the context you want to test.',
              required=False)
def test(context):
    try:
        if not context:
            context = None
        context = load_context(context=context)
        try:
            si = inject_token(context)
        except Exception as e:
            print('Caught error: ', e)
    except ContextNotFound:
        print('Context not found.')


@click.command()
@click.option('--context', '-c',
              help='the context you want to close.',
              required=False)
def close(context):
    try:
        if not context:
            context = None
        context = load_context(context=context)
        try:
            si = inject_token(context)
            content = si.RetrieveContent()
            content.sessionManager.Logout()
        except Exception as e:
            print('Caught error: ', e)
    except ContextNotFound:
        print('Context not found.')


@click.command()
@click.option('--context', '-c',
              help='the context you want to remove.',
              required=False)
def remove(context):
    try:
        config = load_config()
        if not context:
            context = config['current-context']
        for _context in config['contexts']:
            if _context['name'] == context:
                config['contexts'].remove(_context)
                config['current-context'] = ''
                dump_config(config)
                return
        print('Context not found.')
    except ConfigNotFound as e:
        print(e.message)


@click.command()
@click.argument('context', nargs=1)
def use(context):
    """
    Set the current-context in vconfig file.\n
    #ex.: vc config context use <context-name>
    """
    config = load_config()
    current_context = config['current-context']
    if context != current_context:
        for _context in config['contexts']:
            if _context['name'] == context:
                config['current-context'] = context
                dump_config(config)
                print("Switched to context {}.".format(context))
                return
        print('Context not found.')
    return


@click.command()
def contexts():
    """
    Return all contexts in formatted style.
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
                                                              _context['context']['username'],     # nopep8
                                                              _context['context']['vcenter'],      # nopep8
                                                              _context['context']['apiversion']))  # nopep8
            else:
                print('{:<10}{:<30}{:<30}{:<30}{:<30}'.format('',
                                                              _context['name'],
                                                              _context['context']['username'],     # nopep8
                                                             _context['context']['vcenter'],      # nopep8
                                                              _context['context']['apiversion']))  # nopep8
    except ConfigNotFound as exception:
        print(exception.message)
