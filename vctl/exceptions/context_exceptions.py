class ContextNotFound(Exception):
    def __init__(self, error='Context not found.'):
        super().__init__(error)
        self.message = 'No current-context found in config file.'


class ConfigNotFound(Exception):
    def __init__(self, error='Config file not found.'):
        super().__init__(error)
        self.message = 'No contexts found, \
                        consider creating one: vc config context create --help'
