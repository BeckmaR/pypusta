from pusta.generator import Generator, GeneratorConfig
from pusta.generator.cgen.ctypes import *
from pusta.generator.cgen.model import *
from pusta.statechart import *

import logging

import os


def _prefix(s, prefix):
    if prefix:
        return f"{prefix}_{s}"
    else:
        return s


def _c_escape(s):
    s = s.replace('.', '_')
    return s


class CSwitch:
    def __init__(self, var, cases=None):
        if not cases:
            cases = {}
        self._var = var
        self._cases = cases

    @property
    def cases(self):
        return self._cases

    def __str__(self):
        w = IndentedWriter()
        w.append(f"switch ({self._var}) {{")
        w.incr()
        for case, exprs in self._cases.items():
            if case != "default":
                w.append(f"case {case}:")
            else:
                w.append("default:")
            w.incr()
            for e in exprs:
                w.append(e)
            w.decr()
        w.decr()
        w.append('}')
        return str(w)


class CDecl:
    def __init__(self, type: Type, name, static=False, pointer_level=0):
        self._type = type
        self._name = name
        self._static = static
        self._plevel = pointer_level

    def __str__(self):
        s = "static " if self._static else ""
        s += f"{self._type.name} {self._plevel * '*'}{self._name}"
        return s

    def pointer(self):
        self._plevel += 1
        return self

    @property
    def name(self):
        return self._name


class CParam(CDecl):
    def __init__(self, type: Type, name, pointer_level=0):
        super().__init__(type, name, static=False, pointer_level=pointer_level)


class CFunc(CDecl):
    def __init__(self, name, parameters=None, expressions=None, ret_type=None, static=False):
        if not ret_type:
            ret_type = type_registry['void']
        if not parameters:
            parameters = []
        if not expressions:
            expressions = []
        super().__init__(type=ret_type, name=name, static=static)
        self._params = parameters
        self._exprs = expressions
        self._ret_type = ret_type

    @property
    def expressions(self):
        return self._exprs

    @property
    def parameters(self):
        return self._params

    def _do_declare(self):
        return f"{super().__str__()}({', '.join([str(p) for p in self._params])})"

    def declare(self):
        return f"{self._do_declare()};"

    def __str__(self):
        writer = IndentedWriter()
        writer.append(self._do_declare() + " {")
        writer.incr()
        for e in self._exprs:
            writer.append(str(e))
        writer.decr()
        writer.append("}")
        return str(writer)

    def __call__(self, *args, **kwargs):
        return f"{self.name}({', '.join([str(a) for a in args])})"



class CComment:
    def __init__(self, content=None):
        self.lines = []
        if content:
            for line in str(content).splitlines():
                self.lines.append(line)

    def append(self, s):
        for line in s.splitlines():
            self.lines.append(line)

    def __str__(self):
        s = "/*\n"
        for line in self.lines:
            s += f" * {line}\n"
        s += " */"
        return s


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

        self._logger = logging.getLogger(self.__class__.__name__)

        self._state_enum = None
        self._context_struct = None
        self._run_cycle_func = None

        self._state_handlers = dict()
        states = self.statechart.get_contents_of_type(AbstractState)
        for state in states:
            handler = CStateHandler(state)
            self._state_handlers[state] = handler
            self._logger.debug(f"Creating handler for state {state.fqn()}")
            if (parent := state.get_parent_of_type(AbstractState)) is not None:
                handler.parent = self._state_handlers[parent]
                handler.parent.children.append(handler)

        for state in states:
            self._make_state_eval_fn(state)
            self._make_state_entry_fn(state)

    def _write(self, file, content, newlines=1):
        if not isinstance(content, str):
            content = str(content)

        file.write(content.strip())
        file.write('\n' * (newlines + 1))

    def generate(self):
        with self.config.open():
            self.h_path = self.config.h_file.name
            self.c_path = self.config.c_file.name
            self.make_header()
            self.make_source()

    def make_header(self):
        header = self.config.h_file

        self._write(header, self.make_file_comment(), 2)
        self._write(header, self.state_enum)
        self._write(header, self.context_struct)
        self._write(header, self.run_cycle.declare())

    def make_source(self):
        src = self.config.c_file

        self._write(src, f"#include \"{os.path.basename(self.h_path)}\"", newlines=2)
        for handler in self._state_handlers.values():
            self._write(src, handler.entry)
            self._write(src, handler.evaluate)
        self._write(src, self.run_cycle)

    def _make_state_enum(self):
        def _enumerator(e):
            return _c_escape(_prefix(e, self.name).upper())

        enum = CEnum(_prefix("states", self.name))
        enum.members.append(_enumerator("no_state"))

        for s, h in self._state_handlers.items():
            e = _enumerator(s.fqn())
            self._logger.debug(f"Making enumerator {e}")
            enum.members.append(e)
            h.enumerator = e

        return enum

    def make_file_comment(self):
        comment = CComment()
        comment.append(str(self.statechart))
        return str(comment)

    def make_event_enum(self):
        return ""

    def _make_context_struct(self):
        s = CStruct(_prefix("context", self.name))
        s.members.append(f"{self.state_enum.name} active_state")
        return s

    def _ctx_param(self):
        return CParam(self.context_struct, "ctx").pointer()

    def _make_run_cycle(self):
        f = CFunc(_prefix("run_cycle", self.name))
        ctx = self._ctx_param()
        f.parameters.append(ctx)
        sw = CSwitch(f"{ctx.name}->active_state")
        for handler in self._state_handlers.values():
            if handler.original_state.is_leaf():
                sw.cases[handler.enumerator] = [
                    f"// State {handler.original_state.fqn()}",
                    f"{handler.evaluate(ctx.name)};",
                    "break;"
                ]
        f.expressions.append(sw)
        return f

    def _make_state_eval_fn(self, state):
        handler = self._state_handlers[state]
        name = _prefix(_prefix("eval", _c_escape(state.fqn())), self.name)
        param = self._ctx_param()
        handler.evaluate = CFunc(name, static=True, parameters=[param])

        for transition in state.get_transitions():
            handler.evaluate.expressions.append(CComment(transition))

        if handler.parent:
            handler.evaluate.expressions.append("")
            handler.evaluate.expressions.append(handler.parent.evaluate(param.name) + ';')

    def _make_state_entry_fn(self, state):
        handler = self._state_handlers[state]
        name = _prefix(_prefix("entry", _c_escape(state.fqn())), self.name)
        param = self._ctx_param()
        handler.entry = CFunc(name, static=True, parameters=[param])

        if handler.parent:
            handler.entry.expressions.append(handler.parent.entry(param.name) + ";")

    def _make_state_exit_fn(self, state):
        handler = self._state_handlers[state]
        name = _prefix(_prefix("exit", _c_escape(state.fqn())), self.name)
        param = self._ctx_param()
        handler.entry = CFunc(name, static=True, parameters=[param])

        if handler.parent:
            handler.entry.expressions.append(handler.parent.exit(param.name) + ";")

    @property
    def state_enum(self):
        if self._state_enum is None:
            self._logger.debug("Creating state enum")
            self._state_enum = self._make_state_enum()
        return self._state_enum

    @property
    def context_struct(self):
        if self._context_struct is None:
            self._context_struct = self._make_context_struct()
        return self._context_struct

    @property
    def run_cycle(self):
        if self._run_cycle_func is None:
            self._logger.debug("Creating run cycle function")
            self._run_cycle_func = self._make_run_cycle()
        return self._run_cycle_func
