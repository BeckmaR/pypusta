import pusta
from pusta.generator.cgen import CGenerator, CGeneratorConfig
import os
import logging
from inspect import getdoc

import pytest

parser = pusta.Pusta()

test_path = os.path.dirname(__file__)
diagram_path = os.path.join(test_path, "diagrams")

out_dir = os.path.join(test_path, "c_gen_out")

if not os.path.exists(out_dir):
    os.mkdir(out_dir)
with open(os.path.join(out_dir, ".gitignore"), 'w') as gitignore:
    gitignore.write('*')


logger = logging.getLogger(__name__)

def test_c_generator(file):
    gs = globals()

    name, ext = os.path.splitext(file)
    path, name = os.path.split(name)
    assert ext == ".pu"
    d = os.path.join(out_dir, name)

    test_func_name = f"do_test_gen_{name}"

    if test_func_name in gs:
        test_func = gs[test_func_name]
        diagram = parser.parse_file(file)
        statechart = diagram.transform()
        config = CGeneratorConfig(d, name)
        generator = CGenerator()
        gs[test_func_name](statechart, generator, config)
    else:
        pytest.skip(f"{test_func_name} not available")


def do_test_gen_simple_state(statechart, generator, config):
    generator.generate(statechart, config)
