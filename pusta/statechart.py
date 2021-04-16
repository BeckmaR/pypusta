import logging
from typing import Optional, List, Iterable

class BaseNode:
    def __init__(self):
        self._parent: Optional[BaseNode] = None
        self._children: List[BaseNode] = list()
        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def parent(self) -> 'BaseNode':
        return self._parent

    @parent.setter
    def parent(self, parent):
        if parent and self._parent:
            raise ValueError(f"Object {self!r} already has a parent: {self._parent!r}")
        self._parent = parent

    @property
    def children(self):
        return list(self._children)

    def add_child(self, child: 'BaseNode'):
        if child in self._children:
            raise ValueError(f"Object {self!r} already has child {child!r}")
        self._children.append(child)
        child.parent = self

    def remove_child(self, child: 'BaseNode'):
        self._children.remove(child)
        child.parent = None

    @property
    def siblings(self) -> List['BaseNode']:
        if not self._parent:
            return []
        pc = self._parent._children
        return list(filter(lambda c: c is not self, pc))

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

    def _str_children(self):
        return sorted(self._children)

    def __str__(self) -> str:
        s = self._str_header()
        children = self._str_children()
        if children:
            s += ":\n"
            for child in children:
                for line in str(child).splitlines():
                    s += f"    {line}\n"
        return s.strip()

    def _cmp(self, other):
        return self.__class__.__name__ < other.__class__.__name__

    def __lt__(self, other):
        my_index = _sort_index(self.__class__)
        other_index = _sort_index(other.__class__)

        if my_index == other_index:
            return self._cmp(other)

        return my_index < other_index


class NamedNode(BaseNode):
    def __init__(self, name: str):
        super().__init__()
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def _str_header(self):
        return f"{self.__class__.__name__} {self.name}"

    def fqn(self):
        if isinstance(self.parent, NamedNode):
            return f"{self.parent.fqn()}.{self.name}"
        else:
            return self.name

    def _cmp(self, other):
        if isinstance(other, NamedNode):
            return self.fqn() < other.fqn()
        else:
            return super()._cmp(other)


class Label(BaseNode):
    def __init__(self, label: str):
        super().__init__()
        self._label = label

    def _str_header(self):
        return self.__class__.__name__

    def _str_children(self):
        if not self._label:
            return list()
        return self._label.splitlines()

    def append_line(self, other: str):
        self._label += '\n' + other
        return self

    def __eq__(self, other):
        if isinstance(other, str):
            return self._label == other
        if isinstance(other, Label):
            return self._label == other._label
        return False


class LabeledNode(BaseNode):
    _label = None

    def __init__(self, label: str = None):
        super().__init__()
        self.label = label

    @property
    def label(self) -> Label:
        return self._label

    @label.setter
    def label(self, value):
        if self._label:
            self._children.remove(self._label)
        if value is None:
            self._label = None
            return
        if isinstance(value, str):
            value = Label(value)
        if not isinstance(value, Label):
            raise TypeError(f"{value!r} is not a Label")
        self.add_child(value)
        self._label = value


class StateContainer(BaseNode):
    def __init__(self):
        super().__init__()
        self._initial_state = None
        self._final_state = None

    def get_states(self) -> List['State']:
        return self.get_children_of_type(State)

    @property
    def initial_state(self) -> 'InitialState':
        return self._initial_state

    def create_initial_state(self):
        if not self._initial_state:
            insta = InitialState()
            self.add_child(insta)
            self._initial_state = insta
        return self._initial_state

    @property
    def final_state(self) -> 'FinalState':
        return self._final_state

    def create_final_state(self):
        if not self._final_state:
            final = FinalState()
            self.add_child(final)
            self._final_state = final
        return self._final_state


class State(NamedNode, LabeledNode):
    def get_transitions(self) -> List['Transition']:
        return self.get_children_of_type(Transition)

    def get_regions(self) -> List['Region']:
        return self.get_children_of_type(Region)


class Transition(BaseNode):
    def __init__(self, label=None):
        super().__init__()
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

    def _str_header(self):
        return f"{self.__class__.__name__} -> {self.destination.fqn()}"


class PseudoState(State):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def _str_header(self):
        return self.name


class InitialState(PseudoState):
    pass


class FinalState(PseudoState):
    pass


class Choice(State):
    pass


class Fork(State):
    pass


class Region(NamedNode, StateContainer):
    pass


class Statechart(StateContainer):
    pass


_cls_sort_order = [Label, Transition, Region, InitialState, State, FinalState, NamedNode, BaseNode, object]


def _merge(mros):
    if not any(mros): # all lists are empty
        return []  # base case
    for candidate, *_ in mros:
        if all(candidate not in tail for _, *tail in mros):
            return [candidate] + _merge([tail if head is candidate else [head, *tail]
                                        for head, *tail in mros])
    else:
        raise TypeError("No legal mro")


def _mro(cls):
    if cls is object:
        return [object]
    return [cls] + _merge([_mro(base) for base in cls.__bases__])


def _sort_index(cls):
    mro = _mro(cls)
    for supercls in mro:
        if supercls in _cls_sort_order:
            return _cls_sort_order.index(supercls)
