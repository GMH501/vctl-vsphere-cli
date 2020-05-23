class ContextNotFound(Exception):
    def __init__(self):
        self.msg = 'Context not found.'


class ConfigNotFound(Exception):
    def __init__(self):
        self.msg = 'Config file not found.'
