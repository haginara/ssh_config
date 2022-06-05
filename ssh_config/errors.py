""" SSH Config Error"""

class EmptySSHConfig(Exception):
    """Exception"""

    def __init__(self, path):
        super().__init__(f"Empty SSH Config: {path}")


class WrongSSHConfig(Exception):
    """Exception"""

    def __init__(self, path):
        super().__init__(f"Wrong SSH Config: {path}")


class HostExistsError(Exception):
    """Exception"""

    def __init__(self, name):
        super().__init__(f"Host already exists, {name}")


class KeywordError(Exception):
    def __init__(self, keyword):
        super().__init__(f"Not supported keyword: {keyword}")
