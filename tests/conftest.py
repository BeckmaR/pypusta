import pytest
import os

_path = os.path.dirname(__file__)
_diagrams = os.path.join(_path, "diagrams")

def pytest_generate_tests(metafunc):
    if "file" in metafunc.fixturenames:
        files = os.listdir(_diagrams)
        diagrams = [f for f in files if f.endswith(".pu")]
        diagrams = map(lambda f: os.path.join(_diagrams, f), diagrams)
        metafunc.parametrize("file", diagrams)