class ContextNotFound(Exception):
    def __init__(self, error='Context not found.'):
        super().__init__(error)


class ConfigNotFound(Exception):
    def __init__(self, error='vctl config file not found.'):
        super().__init__(error)
