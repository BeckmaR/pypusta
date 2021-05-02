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
        if name not in self._states:
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

    def create_history_state(self, state):
        if state.parent_name:
            parent_state = self.get_or_add_state(state.parent_name)
            regions = parent_state.get_regions()
            if len(regions) > 1:
                raise Exception("Can't transform history state in parent state with more than one region")
            parent = regions[0]
        else:
            parent = self._active_parent

        if state.is_deep:
            return parent.create_deep_history_state()
        else:
            return parent.create_history_state()

    def consume_TransitionExpression(self, transition):
        src = transition.src
        src_type = self.tname(src)
        src_state = None
        if src_type == "str":
            if src == "[*]":
                src_state = self._active_parent.create_initial_state()
        elif src_type == "RegularState":
            src_state = self.get_or_add_state(src.name)
        elif src_type == "HistoryState":
            src_state = self.create_history_state(src)
        if not src_state:
            raise TypeError(f"Source state type {src_type} of state {src} not handled!")

        dst = transition.dest
        dst_type = self.tname(dst)
        dst_state = None
        if dst_type == "str":
            if dst == "[*]":
                dst_state = self._active_parent.create_final_state()
        elif dst_type == "RegularState":
            if dst.type:
                dst_state = self.create_pseudo_state(dst.name, dst.type.type)
            else:
                dst_state = self.get_or_add_state(dst.name)
        elif dst_type == "HistoryState":
            dst_state = self.create_history_state(dst)
        if not dst_state:
            raise TypeError(f"Destination state type {dst_type} of state {dst} not handled!")

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
        if name not in self._states:
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

    def create_parallel_state(self, name):
        if name not in self._states:
            state = self.add_state(name)
        else:
            state = self._states[name]
            if state.parent != self._active_parent:
                state.parent.remove_child(state)
                self._active_parent.add_child(state)

        return state

    def create_pseudo_state(self, name: str, type: str):
        if type in ["<<entryPoint>>", "<<inputPin>>", "<<expansionInput>>"]:
            state = EntryPoint(name)
        elif type in ["<<exitPoint>>", "<<outputPin>>", "<<expansionOutput>>"]:
            state = ExitPoint(name)
        elif type == "<<choice>>":
            state = Choice(name)
        elif type in ["<<fork>>", "<<join>>"]:
            state = Fork(name)
        elif type == "<<end>>":
            state = self._active_parent.create_final_state()
            self._states[name] = state
            return state
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
        if not type:
            self.get_or_add_state(state_name)

        tname = self.tname(type)
        if tname == "CompositeState":
            prev_parent = self._active_parent
            r = self.create_composite_state(state_name)
            self._active_parent = r
            for expr in type.expressions:
                self.consume_expression(expr)
            self._active_parent = prev_parent
        elif tname == "ParallelState":
            prev_parent = self._active_parent
            pstate = self.create_parallel_state(state_name)

            for i, r in enumerate(type.regions):
                region = Region(str(i))
                pstate.add_child(region)
                self._active_parent = region
                for expr in r.expressions:
                    self.consume_expression(expr)
        elif tname == "PseudoState":
            self.create_pseudo_state(state_name, type.type)
        else:
            self._logger.error(f"State type {tname} of state {state_name} not handled!")

    def consume_StateAliasExpression(self, expression):
        self.add_state(expression.name)

    def consume_ScaleExpression(self, expression):
        pass
