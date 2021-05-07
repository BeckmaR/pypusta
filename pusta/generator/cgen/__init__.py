from pusta.generator import Generator, GeneratorConfig
from pusta.statechart import *

import os


class IndentedWriter:
    def __init__(self, indent=4*' '):
        self._indent = indent
        self._cur_indent = 0
        self.lines = []

    def incr(self):
        self._cur_indent += 1

    def decr(self):
        if self._cur_indent > 0:
            self._cur_indent -= 1

    def _add_line(self, l):
        self.lines.append((self._cur_indent * self._indent) + l.strip())

    def append(self, s):
        for l in s.splitlines():
            self._add_line(l)

    def __str__(self):
        s = ''
        for line in self.lines:
            s += line + '\n'
        return s


def _prefix(s, prefix):
    if prefix:
        return f"{prefix}_{s}"
    else:
        return s


class CEnum:
    def __init__(self, name, enumerators=None, prefix=None):
        self._name = name
        self._prefix = prefix
        if not enumerators:
            enumerators = []
        self._enumerators = enumerators

    def append(self, enumerator):
        self._enumerators.append(enumerator)

    def _make_enumerator(self, e):
        return _prefix(e, self._prefix).upper()

    def __str__(self):
        writer = IndentedWriter()

        s = f"enum {self._name} {{"
        writer.append(s)
        writer.incr()
        writer.append(",\n".join([self._make_enumerator(e)
                      for e in self._enumerators]))
        writer.decr()
        writer.append("};")
        return str(writer)


class CDecl:
    def __init__(self, type, name, static=False, pointer_level=0):
        self._type = type
        self._name = name
        self._static = static
        self._plevel = 0


class CFunc(CDecl):
    def __init__(self, name, parameters=None, expressions=None, ret_type='void', static=False):
        if not parameters:
            parameters = []
        if not expressions:
            expressions = []
        super().__init__(type=ret_type, name=name, static=static)
        self._params = parameters
        self._exprs = expressions

    @property
    def expressions(self):
        return self._exprs

    @property
    def parameters(self):
        return self._params

    def _do_declare(self):
        tokens = []
        if self._static:
            tokens.append("static")
        tokens.append(self._ret_type)
        tokens.append(self._plevel * '*' + self._name + f"({', '.join(self._params)})")
        return " ".join(tokens)

    def declare(self):
        return f"{self._do_declare};"

    def __str__(self):
        writer = IndentedWriter()
        writer.append(self._do_declare + " {")
        writer.incr()
        for e in self._exprs:
            writer.append(str(e))
        writer.decr()
        writer.append("}")
        return str(writer)


class CStruct:
    def __init__(self, name, members=None):
        if not members:
            members = []
        self._name = name
        self._members = members

    @property
    def members(self):
        return self._members

    def __str__(self):
        writer = IndentedWriter()
        writer.append(f"struct {self._name} {{")
        writer.incr()
        for m in self._members:
            if isinstance(m, str):
                m = m.rstrip(';')
            writer.append(f"{m};")
        writer.decr()
        writer.append("};")
        return str(writer)


class CGeneratorConfig(GeneratorConfig):
    def __init__(self, out_dir, name):
        super().__init__(out_dir, name)
        self.h_file = None
        self.c_file = None

    def _open(self):
        c_path = self._fname(f"{self._name}.c")
        h_path = self._fname(f"{self._name}.h")
        self.c_file = open(self._fname(c_path), 'w')
        self.h_file = open(self._fname(h_path), 'w')

    def _close(self):
        self.c_file.close()
        self.h_file.close()


class CGenerator(Generator):
    def __init__(self):
        super().__init__()

    def generate(self, statechart: Statechart, config: CGeneratorConfig):
        context = CGeneratorContext(statechart, config)
        context.generate()
        return context


class CGeneratorContext:
    def __init__(self, statechart, config):
        self.statechart = statechart
        self.config = config
        self.name = config.name

    def generate(self):
        with self.config.open():
            self.h_path = self.config.h_file.name
            self.c_path = self.config.c_file.name
            self.make_header()
            self.make_source()

    def make_header(self):
        header = self.config.h_file

        header.write(self.make_state_enum())
        header.write('\n')
        header.write(self.make_context_struct())

    def make_source(self):
        src = self.config.c_file

        src.write(f"#include \"{os.path.basename(self.h_path)}\"")

    def make_state_enum(self):
        enum = CEnum(_prefix("states", self.name), prefix=self.name)
        enum.append("no_state")

        states = self.statechart.get_contents_of_type(AbstractState)
        for s in states:
            enum.append(s.name)

        self._state_enum = enum
        return str(enum)

    def make_event_enum(self):
        return ""

    def make_context_struct(self):
        s = CStruct(_prefix("context", self.name))
        s.members.append(f"enum {self._state_enum._name} active_state")
        return str(s)
