import os
import ssl
import random
import string
import base64
from pathlib import Path

import yaml


def get_unverified_context():
    """
    Get an unverified ssl context. Used to disable the server certificate
    verification.
    @return: unverified ssl context.
    """
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    return context


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
    except Exception as e:
        raise(e)


def load_config():
    """
    Get config.yaml file and transform it to dictionary.
    @return: dictionary.
    @except: raise FileNotFoundError.
    """
    home = str(Path.home())
    config_path = os.path.join(home, '.vctl', 'vconfig.yaml')
    try:
        return load_yaml(config_path)
    except Exception as e:
        raise(e)
        
def setup_config():
    home = str(Path.home())
    config_path = os.path.join(home, '.vctl', 'vconfig.yaml')
    base_config = {'contexts': [], 'current-context': ''}
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as opened_file:
            yaml.dump(base_config, opened_file)
    except Exception as e:
        raise(e)

def dump_config(config):
    """
    Dump dictionary styled config into yaml config file.
    """
    home = str(Path.home())
    config_path = os.path.join(home, '.vctl', 'vconfig.yaml')
    with open(config_path, 'w') as opened_file:
            yaml.dump(config, opened_file)


def load_context():
    """
    Get the current context, dictionary styled.
    @return: dictionary.
    @except: raise Exception.
    """
    config = load_config()
    for context in config['contexts']:
        if context['name'] == config['current-context']:
            return context
    raise Exception('No current-context found in config file.')

