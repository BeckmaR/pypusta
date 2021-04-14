import pusta
from pusta.statechart import *
import os
import logging
from inspect import getdoc

parser = pusta.Pusta()

test_path = os.path.dirname(__file__)
diagram_path = os.path.join(test_path, "diagrams")

logger = logging.getLogger(__name__)


def test_trafo(file):
    gs = globals()

    name, ext = os.path.splitext(file)
    path, name = os.path.split(name)
    assert ext == ".pu"

    test_func_name = f"do_test_transform_{name}"

    if test_func_name in gs:
        test_func = gs[test_func_name]
        diagram = parser.parse_file(file)
        statechart = diagram.transform()
        docstring = getdoc(test_func)
        if docstring:
            assert str(statechart) == docstring
        gs[test_func_name](statechart)


def do_test_transform_simple_state(statechart):
    """
    Statechart:
        InitialState:
            Transition -> State1
        State State1:
            Transition -> FinalState
        FinalState
    """
    logger.debug(statechart)
    states = statechart.get_states()
    assert len(states) == 3

    transitions = statechart.get_contents_of_type(Transition)
    assert len(transitions) == 2

    assert statechart.initial_state is not None
    assert statechart.final_state is not None

    transitions = statechart.initial_state.get_transitions()
    assert len(transitions) == 1

    dest_state = transitions[0].destination
    assert dest_state.name == "State1"

    transitions = dest_state.get_transitions()
    assert len(transitions) == 1

    assert transitions[0].destination == statechart.final_state


def do_test_transform_state_description(statechart):
    """
    Statechart:
        InitialState:
            Transition -> State1
        State State1:
            Label:
                this is a string
                this is another string
            Transition -> FinalState
            Transition -> State2
        State State2:
            Transition -> FinalState
        FinalState
    """
    logger.debug(str(statechart))
    states = statechart.get_states()
    assert len(states) == 4

    transitions = statechart.get_contents_of_type(Transition)
    assert len(transitions) == 4

    assert statechart.initial_state is not None
    assert statechart.final_state is not None

    transitions = statechart.initial_state.get_transitions()
    assert len(transitions) == 1
    dest_state = transitions[0].destination
    assert dest_state.name == "State1"
    assert dest_state.label == "this is a string\nthis is another string"

    transitions = dest_state.get_transitions()
    assert len(transitions) == 2
    dest_state = transitions[0].destination
    assert dest_state == statechart.final_state
    dest_state = transitions[1].destination
    assert dest_state.name == "State2"

    transitions = dest_state.get_transitions()
    assert len(transitions) == 1

    assert transitions[0].destination == statechart.final_state
