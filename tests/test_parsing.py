import pusta
import logging
import os

logger = logging.getLogger(__name__)

parser = pusta.Pusta()


def test_parsing(file):
    logger.debug(file)

    diagram = parser.parse_file(file)