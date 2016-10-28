"""
Fake config library for testing
"""


class Config(object):
    """
    Fake memory only config class
    """
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key, None)

    def getint(self, key):
        return int(self.get(key))

    def set(self, key, val):
        self.data[key] = val
        pass

    def delete(self, key):
        del self.data[key]

    def save(self):
        pass

    def close(self):
        pass


config = Config()
