import pusta
from pusta.statechart import *
import os
import textx
import logging

parser = pusta.Pusta()

test_path = os.path.dirname(__file__)
diagram_path = os.path.join(test_path, "diagrams")


def test_trafo(file):
    gs = globals()

    name, ext = os.path.splitext(file)
    path, name = os.path.split(name)
    assert ext == ".pu"

    test_func_name = f"do_test_transform_{name}"

    if test_func_name in gs:
        diagram = parser.parse_file(file)
        statechart = diagram.transform()
        gs[test_func_name](statechart)


def do_test_transform_simple_state(statechart):
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
