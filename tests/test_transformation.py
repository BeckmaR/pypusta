import pusta
from pusta.statechart import *
import os
import logging
from inspect import getdoc

import pytest

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
        assert docstring is not None
        assert str(statechart) == docstring
        gs[test_func_name](statechart)
    else:
        pytest.skip(f"{test_func_name} not available")


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
    siblings = dest_state.siblings
    assert len(siblings) == 2
    assert statechart.initial_state in siblings
    assert statechart.final_state in siblings

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


def do_test_transform_composite_states_1(statechart):
    """
    Statechart:
        State A:
            Region 0:
                State X:
                    Transition -> Z
                State Y
        State B:
            Region 0:
                State Z:
                    Transition -> Y
    """


def do_test_transform_composite_states_2(statechart):
    """
    Statechart:
        InitialState:
            Transition -> NotShooting
        State Configuring:
            Transition -> Idle
            Region 0:
                InitialState:
                    Transition -> NewValueSelection
                State NewValuePreview:
                    Transition -> NewValueSelection
                    Transition -> NewValueSelection
                    Region 0:
                        State State1:
                            Transition -> State2
                        State State2
                State NewValueSelection:
                    Transition -> NewValuePreview
        State NotShooting:
            Region 0:
                InitialState:
                    Transition -> Idle
                State Idle:
                    Transition -> Configuring
    """

    assert len(statechart.children) == 3

    assert len(statechart.get_contents_of_type(Transition)) == 9


def do_test_transform_arrow_direction(statechart):
    """
    Statechart:
        InitialState:
            Transition -> First
        State First:
            Transition -> Second
        State Last
        State Second:
            Transition -> Third
        State Third:
            Transition -> Last
    """


def do_test_transform_blank_state_decl(statechart):
    """
    Statechart:
        InitialState:
            Transition -> entry1
        State Foo
        State Foo1:
            Transition -> entry2
        State Somp:
            Region 0:
                EntryPoint entry1:
                    Transition -> sin
                EntryPoint entry2:
                    Transition -> sin
                ExitPoint exitA:
                    Transition -> Foo
                State sin:
                    Transition -> sin2
                State sin2:
                    Transition -> exitA
    """


def do_test_transform_entry_exit_point(statechart):
    """
    Statechart:
        InitialState:
            Transition -> entry1
        State Foo
        State Foo1:
            Transition -> entry2
        State Somp:
            Region 0:
                EntryPoint entry1:
                    Transition -> sin
                EntryPoint entry2:
                    Transition -> sin
                ExitPoint exitA:
                    Transition -> Foo
                State sin:
                    Transition -> sin2
                State sin2:
                    Transition -> exitA
    """


def do_test_transform_inline_pseudostate(statechart):
    """
    Statechart:
        InitialState:
            Transition -> entry1
        State Foo
        State Foo1:
            Transition -> entry2
        State Somp:
            Region 0:
                EntryPoint entry1:
                    Transition -> sin
                EntryPoint entry2:
                    Transition -> sin
                ExitPoint exitA:
                    Transition -> Foo
                State sin:
                    Transition -> sin2
                State sin2:
                    Transition -> exitA
    """


def do_test_transform_entry_exit_pin(statechart):
    """
    Statechart:
        InitialState:
            Transition -> entry1
        State Foo
        State Foo1:
            Transition -> entry2
        State Somp:
            Region 0:
                EntryPoint entry1:
                    Transition -> sin
                EntryPoint entry2:
                    Transition -> sin
                ExitPoint exitA:
                    Transition -> Foo
                State sin:
                    Transition -> sin2
                State sin2:
                    Transition -> exitA
    """


def do_test_transform_expansions(statechart):
    """
    Statechart:
        InitialState:
            Transition -> entry1
        State Foo
        State Foo1:
            Transition -> entry2
        State Somp:
            Region 0:
                EntryPoint entry1:
                    Transition -> sin
                EntryPoint entry2:
                    Transition -> sin
                ExitPoint exitA:
                    Transition -> Foo
                State sin:
                    Transition -> sin2
                State sin2:
                    Transition -> exitA
    """


def do_test_transform_transition_description(statechart):
    """
    Statechart:
        InitialState:
            Transition -> NotShooting
        State Configuring:
            Transition -> Idle:
                Label:
                    EvConfig
            Region 0:
                InitialState:
                    Transition -> NewValueSelection
                State NewValuePreview:
                    Transition -> NewValueSelection:
                        Label:
                            EvNewValueRejected
                    Transition -> NewValueSelection:
                        Label:
                            EvNewValueSaved
                    Region 0:
                        State State1:
                            Transition -> State2
                        State State2
                State NewValueSelection:
                    Transition -> NewValuePreview:
                        Label:
                            EvNewValue
        State NotShooting:
            Region 0:
                InitialState:
                    Transition -> Idle
                State Idle:
                    Transition -> Configuring:
                        Label:
                            EvConfig
    """


def do_test_transform_long_state_names(statechart):
    """
    Statechart:
        InitialState:
            Transition -> State1
        State State1:
            Transition -> State2:
                Label:
                    Succeeded
            Transition -> FinalState:
                Label:
                    Aborted
        State State2:
            Transition -> State3:
                Label:
                    Succeeded
            Transition -> FinalState:
                Label:
                    Aborted
        State State3:
            Transition -> State3:
                Label:
                    Failed
            Transition -> FinalState:
                Label:
                    Succeeded / Save Result
            Transition -> FinalState:
                Label:
                    Aborted
            Region 0:
                InitialState:
                    Transition -> long1
                State long1:
                    Label:
                        Just a test
                    Transition -> long1:
                        Label:
                            New Data
                    Transition -> ProcessData:
                        Label:
                            Enough Data
                State ProcessData
        FinalState
    """


def do_test_transform_pseudostates(statechart):
    """
    Statechart:
        InitialState:
            Transition -> choice1:
                Label:
                    from start
                    to choice
        Choice choice1:
            Transition -> fork1:
                Label:
                    from choice
                    to fork
            Transition -> join2:
                Label:
                    from choice
                    to join
            Transition -> FinalState:
                Label:
                    from choice
                    to end
        Fork fork1:
            Transition -> State1:
                Label:
                    from fork
                    to state
            Transition -> State2:
                Label:
                    from fork
                    to state
        Fork join2:
            Transition -> FinalState:
                Label:
                    from join
                    to end
        State State1:
            Transition -> FinalState:
                Label:
                    from state
                    to end
        State State2:
            Transition -> join2:
                Label:
                    from state
                    to join
        FinalState
    """


def do_test_transform_choice(statechart):
    """
    Statechart:
        Choice c:
            Transition -> MinorId:
                Label:
                    [Id <= 10]
            Transition -> MajorId:
                Label:
                    [Id > 10]
        State Idle:
            Transition -> ReqId
        State MajorId
        State MinorId
        State ReqId:
            Transition -> c

    """


def do_test_transform_fork_join(statechart):
    """
    Statechart:
        InitialState:
            Transition -> fork_state
        Fork fork_state:
            Transition -> State2
            Transition -> State3
        Fork join_state:
            Transition -> State4
        State State2:
            Transition -> join_state
        State State3:
            Transition -> join_state
        State State4:
            Transition -> FinalState
        FinalState
    """


def do_test_transform_notes(statechart):
    """
    Statechart:
        InitialState:
            Transition -> Active
        State Active:
            Transition -> Inactive
        State Inactive
    """


def do_test_transform_line_color(statechart):
    """
    Statechart:
        State S1:
            Transition -> S2
            Transition -> S3
            Transition -> S4
            Transition -> S5
        State S2
        State S3
        State S4
        State S5
        State X1:
            Transition -> X2
        State X2
        State Y1:
            Transition -> Y2
        State Y2
        State Z1:
            Transition -> Z2
        State Z2
    """


def do_test_transform_inline_color(statechart):
    """
    Statechart:
        State CurrentSite:
            Region 0:
                State AlarmSupression
                State HardwareSetup:
                    Region 0:
                        State Controller:
                            Transition -> Devices
                        State Devices
                        State Site:
                            Transition -> Controller
                State PresentationSetup:
                    Region 0:
                        State Groups:
                            Transition -> PlansAndGraphics
                        State PlansAndGraphics
                State Schedule
                State Trends
    """


def do_test_transform_meta_expr_1(statechart):
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


def do_test_transform_history_states(statechart):
    """
    Statechart:
        InitialState:
            Transition -> State1
        State State1:
            Transition -> State2:
                Label:
                    Succeeded
            Transition -> FinalState:
                Label:
                    Aborted
        State State2:
            Transition -> State3:
                Label:
                    Succeeded
            Transition -> FinalState:
                Label:
                    Aborted
            Transition -> State3.0.HistoryState:
                Label:
                    Resume
            Transition -> State3.0.DeepHistoryState:
                Label:
                    DeepResume
        State State3:
            Transition -> State2:
                Label:
                    Pause
            Transition -> State3:
                Label:
                    Failed
            Transition -> FinalState:
                Label:
                    Succeeded / Save Result
            Transition -> FinalState:
                Label:
                    Aborted
            Region 0:
                InitialState:
                    Transition -> long1
                DeepHistoryState
                HistoryState
                State long1:
                    Label:
                        Just a test
                    Transition -> long1:
                        Label:
                            New Data
                    Transition -> ProcessData:
                        Label:
                            Enough Data
                State ProcessData
        FinalState
    """


def do_test_transform_concurrent_state_horizontal(statechart):
    """
    Statechart:
        InitialState:
            Transition -> Active
        State Active:
            Region 0:
                InitialState:
                    Transition -> NumLockOff
                State NumLockOff:
                    Transition -> NumLockOn:
                        Label:
                            EvNumLockPressed
                State NumLockOn:
                    Transition -> NumLockOff:
                        Label:
                            EvNumLockPressed
            Region 1:
                InitialState:
                    Transition -> CapsLockOff
                State CapsLockOff:
                    Transition -> CapsLockOn:
                        Label:
                            EvCapsLockPressed
                State CapsLockOn:
                    Transition -> CapsLockOff:
                        Label:
                            EvCapsLockPressed
            Region 2:
                InitialState:
                    Transition -> ScrollLockOff
                State ScrollLockOff:
                    Transition -> ScrollLockOn:
                        Label:
                            EvCapsLockPressed
                State ScrollLockOn:
                    Transition -> ScrollLockOff:
                        Label:
                            EvCapsLockPressed
    """


def do_test_transform_concurrent_state_vertical(statechart):
    """
    Statechart:
        InitialState:
            Transition -> Active
        State Active:
            Region 0:
                InitialState:
                    Transition -> NumLockOff
                State NumLockOff:
                    Transition -> NumLockOn:
                        Label:
                            EvNumLockPressed
                State NumLockOn:
                    Transition -> NumLockOff:
                        Label:
                            EvNumLockPressed
            Region 1:
                InitialState:
                    Transition -> CapsLockOff
                State CapsLockOff:
                    Transition -> CapsLockOn:
                        Label:
                            EvCapsLockPressed
                State CapsLockOn:
                    Transition -> CapsLockOff:
                        Label:
                            EvCapsLockPressed
            Region 2:
                InitialState:
                    Transition -> ScrollLockOff
                State ScrollLockOff:
                    Transition -> ScrollLockOn:
                        Label:
                            EvCapsLockPressed
                State ScrollLockOn:
                    Transition -> ScrollLockOff:
                        Label:
                            EvCapsLockPressed
    """
