import logging
import os
from pusta.statechart import Statechart


class GeneratorConfig:
    class Manager:
        def __init__(self, config: 'GeneratorConfig'):
            self.config = config

        def __enter__(self):
            self.config._open()

        def __exit__(self, type, value, traceback):
            self.config._close()

    def __init__(self, out_dir, name):
        self._out_dir = os.path.abspath(out_dir)
        self._name = name

    @property
    def name(self):
        return self._name

    def _fname(self, name):
        return os.path.join(self._out_dir, name)

    def open(self):
        if not os.path.exists(self._out_dir):
            os.mkdir(self._out_dir)
        return GeneratorConfig.Manager(self)

    def _open(self):
        pass

    def _close(self):
        pass


class Generator:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def generate(self, statechart: Statechart, config: GeneratorConfig = None):
        raise NotImplementedError("Abstract Generator can't generate anything")
