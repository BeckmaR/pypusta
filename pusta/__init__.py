import textx
import textx.export
import os
import logging

_logger = logging.getLogger(__name__)


class Diagram:
    def __init__(self, model):
        self._model = model

    def export(self, path):
        textx.export.model_export(self._model, path)


class Pusta:
    _grammar_path = os.path.join(os.path.dirname(__file__), 'state.tx')

    def __init__(self):
        self._parser = textx.metamodel_from_file(self._grammar_path)

    def parse(self, s):
        return Diagram(self._parser.model_from_str(s))

    def parse_file(self, p):
        return Diagram(self._parser.model_from_file(p))


