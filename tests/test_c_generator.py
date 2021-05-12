import pusta
from pusta.generator.cgen import CGenerator, CGeneratorConfig
import os
import subprocess
import logging
from inspect import getdoc

import textwrap

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


def add_main_file(gen_dir, gen_context):
    header = os.path.basename(gen_context.h_path)

    src = f"""
    #include "{header}"

    int main(int argc, char **argv) {{
        return 0;
    }}
    """

    with open(os.path.join(gen_dir, "main.c"), 'w') as m:
        m.write(textwrap.dedent(src))


def do_compile(gen_dir, gen_context):
    out = gen_context.name
    src = os.path.basename(gen_context.c_path)
    subprocess.run(["gcc", "-Werror", "-o", out, "main.c", src], cwd=gen_dir, check=True)


def test_c_generator(file):
    gs = globals()

    name, ext = os.path.splitext(file)
    path, name = os.path.split(name)
    assert ext == ".pu"
    gen_dir = os.path.join(out_dir, name)

    test_func_name = f"do_test_gen_{name}"

    generator = CGenerator()

    diagram = parser.parse_file(file)
    statechart = diagram.transform()
    config = CGeneratorConfig(gen_dir, name)
    gen_context = generator.generate(statechart, config)
    add_main_file(gen_dir, gen_context)
    do_compile(gen_dir, gen_context)
