import ssl
import random
import string
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


def load_config(filename='config.yaml'):
    """
    Get config.yaml file and transform it to dictionary.
    @return: dictionary.
    """
    with open(filename, 'r') as config_file:
        return yaml.safe_load(config_file)


def dump_config(config, filename='config.yaml'):
    with open('config.yaml', 'w') as config_file:
            yaml.dump(config, config_file)