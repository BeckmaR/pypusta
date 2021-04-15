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
        self._states[name] = s
        return s

    def get_or_add_state(self, name: str) -> State:
        if not name in self._states:
            self.add_state(name)
        return self._states[name]

    def add_state_to(self, parent_name: str, name: str) -> State:
        parent = self._states[parent_name]
        s = State(name)
        parent.add_child(s)
        return s

    def consume_diagram(self, diagram):
        for expression in diagram._model.expressions:
            self.consume_expression(expression)

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
            src_state = self._statechart.create_initial_state()
        else:
            src_state = self.get_or_add_state(src)

        dst = transition.dest
        if not isinstance(dst, str):
            dst = dst.name
        if dst == "[*]":
            dst_state = self._statechart.create_final_state()
        else:
            dst_state = self.get_or_add_state(dst)
        t = Transition()
        t.source = src_state
        t.destination = dst_state

    def consume_StateDescriptionExpression(self, expression):
        state = self.get_or_add_state(expression.state.name)
        if state.label:
            state.label += '\n' + expression.description
        else:
            state.label = expression.description

    def consume_StateDeclarationExpression(self, expression):
        state_name = expression.name
        type = expression.type
        tname = self.tname(type)
        if tname == "CompositeState":
            state = State(state_name)
            self._active_parent.add_child(state)
            self._states[state_name] = state
            prev_parent = self._active_parent
            self._active_parent = state
            for expr in type.expressions:
                self.consume_expression(expr)
            self._active_parent = prev_parent

