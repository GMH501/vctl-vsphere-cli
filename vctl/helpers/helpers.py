import os
import sys
import json
import base64
import random
import re
import string
from pathlib import Path

import yaml
from bs4 import BeautifulSoup

from vctl.helpers.auth import decode_token
from vctl.exceptions.exceptions import ContextNotFound, ConfigNotFound


def random_string(n=5):
    """Generate a random string of n charachters.

    Args:
        length (int): Number of random string charachters to return.

    Returns:
        String of n charachters.
    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(n))


def load_config(raise_exception=False):
    """
    Get vconfig file and transform it to dictionary.\n
    @return: dictionary.\n
    @except: raise SystemExit.
    """
    home = str(Path.home())
    config_path = os.path.join(home, '.vctl', 'config')
    try:
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except FileNotFoundError:
        if raise_exception:
            raise FileNotFoundError
        else:
            print('Config file not found in default path ~/.vctl/config.')
            raise SystemExit(1)


def setup_config():
    """
    Setup base vconfig file in default path  ~/.vctl/config.
    """
    home = str(Path.home())
    config_path = os.path.join(home, '.vctl', 'config')
    base_config = {'contexts': [], 'current-context': ''}
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as opened_file:
        yaml.dump(base_config, opened_file)


def dump_config(config):
    """
    Dump dictionary styled config into yaml config file.
    """
    home = str(Path.home())
    config_path = os.path.join(home, '.vctl', 'config')
    with open(config_path, 'w') as opened_file:
        yaml.dump(config, opened_file)


def create_context(si, vcenter, username, password=None):
    """Create the context.
    """
    api_version = si._stub.versionId
    apiversion = re.findall('.*/(.*)"', api_version)[0]
    cookie = bytes(si._stub.cookie, encoding='utf-8')
    token = base64.b64encode(cookie)
    context_name = '{}#{}'.format(vcenter, random_string())
    context = {'context': {'vcenter': vcenter,
                        'version': si.content.about.fullName,
                        'apiversion': apiversion,
                        'username': username,
                        'token': token},
                'name': context_name}
    if password:
        context['context']['password'] = bytes(password, encoding='utf-8')
    return context


def load_context(context=None):
    """Get the current context, dictionary styled.\n
    Args:
        context 
    @except: raise ContextNotFound.
    """
    config = load_config()
    decoded_context = None
    if context is None:
        context = config['current-context']
    for _context in config['contexts']:
        if _context['name'] == context:
            context = _context['context']
            context['token'] = decode_token(context['token'])
            if 'password' in context:
                context['password'] = context['password'].decode('utf-8')
            decoded_context = context
            return decoded_context
    if decoded_context is None:
        print('Context {} not found in config file.'.format(context))
        raise SystemExit(1)


def jsonify(obj, sort=False):
    """Dumps the object on standard output, json formatted.

    Args:
        obj (dict): the selected object to dumps.
        sort (bool): sort the keys in the obj dict.
    """
    json.dump(obj, sys.stdout, indent=2, sort_keys=sort)


def yamlify(obj, sort=False):
    """Dumps the object on standard output, yaml formatted.

    Args:
        obj (dict): the selected object to dumps.
        sort (bool): sort the keys in the obj dict.
    """
    yaml.dump(obj, sys.stdout, indent=2, sort_keys=sort)


def scrape(html, search=''):
    output = []
    keys = ['name', 'lastModified', 'size']
    html = html.split('\n')
    valid_lines = [line for line in html if search in line]
    html_data = "".join(valid_lines)
    table_data = [[cell.text for cell in row("td")]
                    for row in BeautifulSoup(html_data, features="html.parser")("tr")]
    for values in table_data:
        struct = dict(zip(keys, values))
        output.append(struct)
    if "Parent" in output[0]['name']:
        output.pop(0)
    return output