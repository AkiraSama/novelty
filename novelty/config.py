from argparse import Namespace
from pathlib import Path

import toml


class ConfigNamespace:
    def __init__(self, filepath: Path, args_namespace: Namespace = None):
        self.args = args_namespace
        self.config_filepath = filepath
        self.load_config()

    def __getitem__(self, key):
        value = getattr(self.args, key, None)
        if value is not None:
            return value
        return self.cfg[key]

    def __setitem__(self, key, value):
        if hasattr(self.args, key):
            delattr(self.args, key)
        self.cfg[key] = value

    def __delitem__(self, key):
        if hasattr(self.args, key):
            delattr(self.args, key)
        del self.cfg[key]

    def __contains__(self, item):
        return hasattr(self.args, item) or (item in self.cfg)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def load_config(self):
        self.cfg = toml.load(self.config_filepath)
        if self.cfg is None:
            self.cfg = {}
