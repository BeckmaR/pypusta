import textx
import textx.export
import os
import logging
import pusta.builder

_logger = logging.getLogger(__name__)


class Diagram:
    def __init__(self, model):
        self._model = model

    def export(self, path):
        textx.export.model_export(self._model, path)

    def transform(self):
        builder = pusta.builder.StatechartBuilder()
        builder.consume_diagram(self)
        return builder.statechart


class Pusta:
    _grammar_path = os.path.join(os.path.dirname(__file__), 'state.tx')

    def __init__(self):
        self._parser = textx.metamodel_from_file(self._grammar_path, use_regexp_group=True)

    def parse(self, s):
        return Diagram(self._parser.model_from_str(s))

    def parse_file(self, p):
        _logger.info(f"Parsing file {p}")
        return Diagram(self._parser.model_from_file(p))
