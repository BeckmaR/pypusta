from pusta.statechart import *
from typing import Dict
import logging


class StatechartBuilder:
    def __init__(self):
        self._statechart = Statechart()
        self._states: Dict[str, State] = dict()
        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def statechart(self):
        return self._statechart

    def add_state(self, name: str) -> State:
        s = State(name)
        self._statechart.add_child(s)
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

