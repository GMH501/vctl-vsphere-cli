import os
import random
import string
import base64
from pathlib import Path

import yaml

from vc.exceptions.context_exceptions import ContextNotFound, ConfigNotFound


def random_string(string_length=5):
    """
    Get random charachters for generating unique context name.
    @return: random charachters.
    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def load_yaml(filename):
    """
    Get yaml file and transform it to dictionary.
    @return: dictionary.
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
    @except: raise ConfigNotFound.\n
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
    cookie = bytes(si._stub.cookie, encoding='utf-8')
    token = base64.b64encode(cookie)
    context_name = '{}-{}'.format(vcenter, random_string())
    return {'context': {'vcenter': vcenter,
                        'username': username,
                        'token': token},
                        'name': context_name}

def load_context(decode=False):
    """
    Get the current context, dictionary styled.
    @return: dictionary.
    @except: raise Exception.
    """
    config = load_config()
    for _context in config['contexts']:
        if _context['name'] == config['current-context']:
            context = _context['context']
            if decode == True:
                token = context['token']
                b_cookie = base64.b64decode(token)
                cookie = b_cookie.decode('UTF-8')
                context['token'] = cookie
                return context
            return context
    raise ContextNotFound('No current-context found in vconfig file.')
