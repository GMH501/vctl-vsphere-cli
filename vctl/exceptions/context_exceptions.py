class ContextNotFound(Exception):
    def __init__(self, error='ContextNotFound'):
        super().__init__(error)
        self.message = 'No current-context found in vconfig file.'


class ConfigNotFound(Exception):
    def __init__(self, error='ConfigNotFound'):
        super().__init__(error)
        self.message = 'No contexts found, \
                        consider creating one: vc config context create --help'
