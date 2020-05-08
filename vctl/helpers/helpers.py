import os
import base64
import random
import re
import string
from pathlib import Path

import yaml

from vctl.helpers.auth import decode_token
from vctl.exceptions.context_exceptions import ContextNotFound, ConfigNotFound


def random_string(string_length=5):
    """
    Get random charachters for generating unique context name.\n
    @return: random charachters.
    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def load_yaml(filename):
    """
    Get yaml file and transform it to dictionary.\n
    @return: dictionary.\n
    @except: raise FileNotFoundError.
    """
    try:
        with open(filename, 'r') as config_file:
            return yaml.safe_load(config_file)
    except:
        raise FileNotFoundError


def load_config():
    """
    Get vconfig file and transform it to dictionary.\n
    @return: dictionary.\n
    @except: raise ConfigNotFound.
    """
    home = str(Path.home())
    config_path = os.path.join(home, '.vctl', 'vconfig.yaml')
    try:
        return load_yaml(config_path)
    except FileNotFoundError:
        raise ConfigNotFound('vconfig file not found in default path.')

def setup_config():
    """
    Setup basic vconfig file in default path.
    """
    home = str(Path.home())
    config_path = os.path.join(home, '.vctl', 'vconfig.yaml')
    base_config = {'contexts': [], 'current-context': ''}
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as opened_file:
            yaml.dump(base_config, opened_file)
    except Exception as e:
        raise e

def dump_config(config):
    """
    Dump dictionary styled config into yaml config file.
    """
    home = str(Path.home())
    config_path = os.path.join(home, '.vctl', 'vconfig.yaml')
    with open(config_path, 'w') as opened_file:
        yaml.dump(config, opened_file)


def create_context(si, vcenter, username):
    api_version = si._stub.versionId
    apiversion = re.findall('.*/(.*)"', api_version)[0]
    cookie = bytes(si._stub.cookie, encoding='utf-8')
    token = base64.b64encode(cookie)
    context_name = '{}#{}'.format(vcenter, random_string())
    return {'context': {'vcenter': vcenter,
                        'version': si.content.about.fullName,
                        'apiversion': apiversion,
                        'username': username,
                        'token': token},
                        'name': context_name}

def load_context(context=None):
    """
    Get the current context, dictionary styled.\n
    @return: dictionary.\n
    @except: raise ContextNotFound.
    """
    config = load_config()
    if context:
        for _context in config['contexts']:
            if _context['name'] == context:
                context = _context['context']
                context['token'] = decode_token(context['token'])
                return context
    else:
        for _context in config['contexts']:
            if _context['name'] == config['current-context']:
                context = _context['context']
                context['token'] = decode_token(context['token'])
                return context
    raise ContextNotFound('Context not found in vcconfig file.')
