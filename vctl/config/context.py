import base64
import re

import click
from pyVmomi import vim, vmodl

from vctl.helpers.helpers import (
    load_config, dump_config, setup_config, create_context, load_context)
from vctl.helpers.vmware import get_unverified_context
from vctl.exceptions.exceptions import ConfigNotFound, ContextNotFound
from vctl.helpers.auth import inject_token

try:
    from pyVim.connect import SmartConnect
except:
    from pyvim.connect import SmartConnect


@click.group()
def context():
    """
    Context related subcommands.
    """
    pass


@context.command()
@click.option('--vcenter', '-v',
              help='vCenter you want to conntect to.',
              required=True)
@click.option('--username', '-u',
              help='Username to use for connecting to vcenter.',
              required=True)
@click.option('--password', '-p',
              help='Password to use with the username.',
              required=True)
@click.option('--save',
              help='Save the password for refreshing the context.',
              is_flag=True)
def create(vcenter, username, password, save):
    """Create new context towards the specified vcenter.

    # ex.: vctl config context create -v <vcenter> -u <username> -p <password>
    """
    try:
        si = SmartConnect(host=vcenter,
                          user=username,
                          pwd=password,
                          sslContext=get_unverified_context(),
                          connectionPoolTimeout=-1)
        if not save:
            password = None
        context = create_context(si, vcenter, username, password)
        try:
            load_config(raise_exception=True)
        except FileNotFoundError:
            setup_config()
        finally:
            config = load_config()
            config['contexts'].append(context)
            config['current-context'] = context['name']
            dump_config(config)
            return
    except Exception as e:
        print('Caught exception: ', e)


@context.command()
@click.argument('current', nargs=1)
@click.argument('new', nargs=1)
def rename(current, new):
    """Rename a context name from <current> name to <new> name.

    # ex.: vctl config context rename <current> <new>
    """
    if current != new:
        try:
            config = load_config()
            current_context = config['current-context']
            for _context in config['contexts']:
                if _context['name'] == current:
                    _context['name'] = new
                    if current == current_context:
                        config['current-context'] = new
                    dump_config(config)
                    return
            print('Context not found.')
        except (ConfigNotFound, ContextNotFound):
            print('Context not found.')
    return


@context.command()
@click.option('--context', '-c',
              help='The context you want to test.',
              required=False)
def refresh(context):
    try:
        config = load_config()
        inner_context = load_context(context=context)
        if not 'password' in inner_context:
            print('Password not found in context.')
            raise SystemExit(1)
        if not context:
            context = config['current-context']
        si = SmartConnect(host=inner_context['vcenter'],
            user=inner_context['username'],
            pwd=inner_context['password'],
            sslContext=get_unverified_context(),
            connectionPoolTimeout=-1)
        cookie = bytes(si._stub.cookie, encoding='utf-8')
        token = base64.b64encode(cookie)
        for _context in config['contexts']:
            if _context['name'] == context:
                _context['context']['token'] = token
                dump_config(config)

    except vim.fault.NotAuthenticated:
        raise SystemExit('Context is expired.')
    except vmodl.MethodFault as e:
        raise SystemExit('Caught vmodl fault: ' + e.msg)
    except Exception as e:
        #print('Caught error:', e)
        raise


@context.command()
@click.option('--context', '-c',
              help='The context you want to test.',
              required=False)
def test(context):
    try:
        context = load_context(context=context)
        try:
            si = inject_token(context)
            token = context['token'].split('=')[1]
            sId = re.findall(r'[0-9a-z][^\s]*[0-9a-z]', token)[0]
            print(sId)
            is_valid = si.content.sessionManager.SessionIsActive(sId, context['username'])
            print(is_valid)
            print(si.content)
            if is_valid:
                raise SystemExit('Context is active.')
        except:
            raise

    except vim.fault.NotAuthenticated:
        raise SystemExit('Context is expired.')
    except vmodl.MethodFault as e:
        raise SystemExit('Caught vmodl fault: ' + e.msg)
    except Exception as e:
        print('Caught error:', e)


@context.command()
@click.option('--context', '-c',
              help='The context you want to close.',
              required=False)
def close(context):
    """Close the <context> towards the vcenter.\n
    The default <context> is current-context.

    # ex.: vctl config context close [-c <context>]
    """
    try:
        context = load_context(context=context)
        try:
            si = inject_token(context)
            content = si.RetrieveContent()
            content.sessionManager.Logout()
        except Exception as e:
            print('Caught error: ', e)
    except (ConfigNotFound, ContextNotFound):
        print('Context not found.')


@context.command()
@click.option('--context', '-c',
              help='The context you want to remove.',
              required=False)
def remove(context):
    """Remove the <context> from the config file.\n
    The default <context> is current-context.

    # ex.: vctl config context remove [-c <context>]
    """
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
    except (ConfigNotFound, ContextNotFound):
        print('Context not found.')


@context.command()
@click.argument('context', nargs=1)
def use(context):
    """Set the current-context.

    # ex.: vctl config context use <context>.
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
