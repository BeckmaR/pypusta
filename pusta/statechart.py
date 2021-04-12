import logging
from typing import Optional, List, Set


class BaseNode:
    def __init__(self):
        self._parent: Optional[BaseNode] = None
        self._children: Set[BaseNode] = set()

    @property
    def parent(self) -> 'BaseNode':
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    def add_child(self, child: 'BaseNode'):
        self._children.add(child)
        child.parent = self

    def get_children_of_type(self, cls) -> List:
        return list(filter(lambda o: isinstance(o, cls), self._children))

    def get_parent_of_type(self, cls):
        if isinstance(self._parent, cls):
            return self._parent
        elif self._parent:
            return self._parent.get_parent_of_type(cls)
        else:
            return None

    def get_contents(self):
        contents = []
        for c in self._children:
            contents.append(c)
            contents.extend(c.get_contents())
        return contents

    def get_contents_of_type(self, cls):
        return list(filter(lambda o: isinstance(o, cls), self.get_contents()))

    def _str_header(self):
        return f"{self.__class__.__name__}"

    def __str__(self) -> str:
        s = self._str_header()
        if self._children:
            s += ":\n"
            for child in self._children:
                for line in str(child).splitlines(keepends=True):
                    s += "  " + line
        return s


class NamedNode(BaseNode):
    def __init__(self, name: str):
        super().__init__()
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def _str_header(self):
        return f"{self.__class__.__name__} {self._name}"


class LabeledNode(BaseNode):
    def __init__(self, label: str):
        super().__init__()
        self._label = label

    @property
    def label(self):
        return self._label


class AbstractState(BaseNode):
    def get_transitions(self) -> List['Transition']:
        return self.get_children_of_type(Transition)


class State(NamedNode, AbstractState):
    pass


class Transition(LabeledNode):
    def __init__(self, label=None):
        super().__init__(label)
        self._src = None
        self._dst = None

    @property
    def source(self) -> State:
        return self._src

    @source.setter
    def source(self, src: State):
        self._src = src
        if src:
            src.add_child(self)

    @property
    def destination(self) -> State:
        return self._dst

    @destination.setter
    def destination(self, dst: State):
        self._dst = dst


class CompositeState(State):
    def get_regions(self) -> List['Region']:
        return self.get_children_of_type(Region)


class PseudoState(AbstractState):
    pass


class NamedPseudoState(State, PseudoState):
    pass


class InitialState(PseudoState):
    pass


class FinalState(PseudoState):
    pass


class Choice(NamedPseudoState):
    pass


class Fork(NamedPseudoState):
    pass


class Region(BaseNode):
    def get_states(self) -> List[State]:
        return self.get_children_of_type(State)


class Statechart(BaseNode):
    def __init__(self):
        super().__init__()
        self._initial_state = None
        self._final_state = None

    def get_states(self) -> List[AbstractState]:
        return self.get_children_of_type(AbstractState)

    @property
    def initial_state(self) -> InitialState:
        return self._initial_state

    def create_initial_state(self):
        if not self._initial_state:
            insta = InitialState()
            self.add_child(insta)
            self._initial_state = insta
        return self._initial_state

    @property
    def final_state(self) -> FinalState:
        return self._final_state

    def create_final_state(self):
        if not self._final_state:
            final = FinalState()
            self.add_child(final)
            self._final_state = final
        return self._final_state
