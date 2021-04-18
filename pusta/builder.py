from pusta.statechart import *
from typing import Dict
import logging


class StatechartBuilder:
    def __init__(self):
        self._statechart = Statechart()
        self._states: Dict[str, State] = dict()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._active_parent = self._statechart

    @staticmethod
    def tname(o):
        return o.__class__.__name__

    @property
    def statechart(self):
        return self._statechart

    def add_state(self, name: str) -> State:
        s = State(name)
        self._active_parent.add_child(s)
        r = Region('0')
        self._states[name] = s
        return s

    def get_or_add_state(self, name: str) -> State:
        if not name in self._states:
            self.add_state(name)
        return self._states[name]

    def after_transformation_cleanup(self):
        return self.remove_empty_regions()

    def remove_empty_regions(self):
        for r in self._statechart.get_contents_of_type(Region):
            if len(r.children) == 0:
                r.parent.remove_child(r)

    def consume_diagram(self, diagram):
        try:
            for expression in diagram._model.expressions:
                self.consume_expression(expression)
            self.after_transformation_cleanup()
        except Exception:
            self._logger.exception("Exception during diagram transformation")
            raise

    def consume_expression(self, expression):
        clsname = expression.__class__.__name__
        self._logger.debug(f"Consuming {clsname}")
        consumer_name = f"consume_{clsname}"
        consumer = getattr(self, consumer_name, None)
        if not consumer:
            self._logger.error(f"No consumer for {clsname}!")
        else:
            consumer(expression)

    def consume_TransitionExpression(self, transition):
        src = transition.src
        if not isinstance(src, str):
            src = src.name
        if src == "[*]":
            src_state = self._active_parent.create_initial_state()
        else:
            src_state = self.get_or_add_state(src)

        dst = transition.dest
        if dst == "[*]":
            dst_state = self._active_parent.create_final_state()
        else:
            if dst.type:
                dst_state = self.create_pseudo_state(dst.name, dst.type.type)
            else:
                dst_state = self.get_or_add_state(dst.name)
        t = Transition(transition.description)
        t.source = src_state
        t.destination = dst_state

    def consume_StateDescriptionExpression(self, expression):
        state = self.get_or_add_state(expression.state.name)
        if state.label:
            state.label.append_line(expression.description)
        else:
            state.label = expression.description

    def create_composite_state(self, name):
        if not name in self._states:
            state = self.add_state(name)
        else:
            state = self._states[name]
            if state.parent != self._active_parent:
                state.parent.remove_child(state)
                self._active_parent.add_child(state)

        r = Region('0')
        state.add_child(r)
        self._active_parent = r
        return r

    def create_pseudo_state(self, name: str, type: str):
        if type in ["<<entryPoint>>", "<<inputPin>>"]:
            state = EntryPoint(name)
        elif type in ["<<exitPoint>>", "<<outputPin>>"]:
            state = ExitPoint(name)
        else:
            raise ValueError(f"Pseudo state type {type} not handled!")

        self._active_parent.add_child(state)

        if name in self._states:
            old_state = self._states[name]
            for c in old_state.children:
                old_state.remove_child(c)
                state.add_child(c)
            old_state.parent.remove_child(old_state)

        self._states[name] = state
        return state

    def consume_StateDeclarationExpression(self, expression):
        state_name = expression.name
        type = expression.type
        tname = self.tname(type)

        if tname == "CompositeState":
            prev_parent = self._active_parent
            r = self.create_composite_state(state_name)
            self._active_parent = r
            for expr in type.expressions:
                self.consume_expression(expr)
            self._active_parent = prev_parent
        elif tname == "PseudoState":
            self.create_pseudo_state(state_name, type.type)
        else:
            self._logger.error(f"State type {tname} not handled!")

    def consume_StateAliasExpression(self, expression):
        self.add_state(expression.name)

    def consume_ScaleExpression(self, expression):
        pass

