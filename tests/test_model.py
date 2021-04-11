import pusta
import os
import textx
import logging

parser = pusta.Pusta()

test_path = os.path.dirname(__file__)
diagram_path = os.path.join(test_path, "diagrams")


def test_model(file):
    gs = globals()

    name, ext = os.path.splitext(file)
    path, name = os.path.split(name)
    assert ext == ".pu"

    test_func_name = f"do_test_diagram_{name}"

    assert test_func_name in gs, f"Test function not available for diagram {file}!"

    diagram = parser.parse_file(file)
    gs[test_func_name](diagram)


def do_test_diagram_simple_state(diagram):
    transitions = textx.get_children_of_type("TransitionExpression", diagram._model)
    assert len(transitions) == 2

    assert transitions[0].src == '[*]'
    assert transitions[0].dest.name == 'State1'

    assert transitions[1].src.name == 'State1'
    assert transitions[1].dest == '[*]'


def do_test_diagram_state_description(diagram):
    transitions = textx.get_children_of_type("TransitionExpression", diagram._model)
    assert len(transitions) == 4

    assert transitions[0].src == '[*]'
    assert transitions[0].dest.name == 'State1'

    assert transitions[1].src.name == 'State1'
    assert transitions[1].dest == '[*]'

    assert transitions[2].src.name == 'State1'
    assert transitions[2].dest.name == 'State2'

    assert transitions[3].src.name == 'State2'
    assert transitions[3].dest == '[*]'

    descriptions = textx.get_children_of_type("StateDescriptionExpression", diagram._model)
    assert len(descriptions) == 2
    assert descriptions[0].description == "this is a string"
    assert descriptions[1].description == "this is another string"


def do_test_diagram_meta_expr_1(diagram):
    transitions = textx.get_children_of_type("TransitionExpression", diagram._model)
    assert len(transitions) == 4

    assert transitions[0].src == '[*]'
    assert transitions[0].dest.name == 'State1'

    assert transitions[1].src.name == 'State1'
    assert transitions[1].dest == '[*]'

    assert transitions[2].src.name == 'State1'
    assert transitions[2].dest.name == 'State2'

    assert transitions[3].src.name == 'State2'
    assert transitions[3].dest == '[*]'

    descriptions = textx.get_children_of_type("StateDescriptionExpression", diagram._model)
    assert len(descriptions) == 2
    assert descriptions[0].description == "this is a string"
    assert descriptions[1].description == "this is another string"


def do_test_diagram_composite_states_2(diagram):
    transitions = textx.get_children_of_type("TransitionExpression", diagram._model)
    assert len(transitions) == 9

    composites = textx.get_children_of_type("CompositeDeclarationExpression", diagram._model)
    assert len(composites) == 3

    assert composites[0].name == "NotShooting"
    assert composites[1].name == "Configuring"
    assert composites[2].name == "NewValuePreview"

    sub_transitions = textx.get_children_of_type("TransitionExpression", composites[0])
    assert len(sub_transitions) == 3

    sub_transitions = textx.get_children_of_type("TransitionExpression", composites[1])
    assert len(sub_transitions) == 5

    sub_transitions = textx.get_children_of_type("TransitionExpression", composites[2])
    assert len(sub_transitions) == 1

    assert composites[2].parent == composites[1]


def do_test_diagram_transition_description(diagram):
    transitions = textx.get_children_of_type("TransitionExpression", diagram._model)
    assert len(transitions) == 9

    expected_descriptions = [
        None,
        None,
        "EvConfig",
        "EvConfig",
        None,
        "EvNewValue",
        "EvNewValueRejected",
        "EvNewValueSaved",
        None
    ]

    for i, t in enumerate(transitions):
        assert t.description == expected_descriptions[i]


def do_test_diagram_composite_states_1(diagram):
    transitions = textx.get_children_of_type("TransitionExpression", diagram._model)
    assert len(transitions) == 2

    composites = textx.get_children_of_type("CompositeDeclarationExpression", diagram._model)
    assert len(composites) == 5

    names = ["A", "X", "Y", "B", "Z"]

    for i, s in enumerate(composites):
        assert s.name == names[i]

    assert composites[1].parent == composites[0]
    assert composites[2].parent == composites[0]
    assert composites[4].parent == composites[3]


def do_test_diagram_long_state_names(diagram):
    transitions = textx.get_children_of_type("TransitionExpression", diagram._model)
    assert len(transitions) == 11

    alias = textx.get_children_of_type("StateAliasExpression", diagram._model)
    assert len(alias) == 1
    assert alias[0].longname == r"Accumulate Enough Data\nLong State Name"
    assert alias[0].name == "long1"


def do_test_diagram_history_states(diagram):
    transitions = textx.get_children_of_type("TransitionExpression", diagram._model)
    assert len(transitions) == 14

    assert transitions[8].dest.is_deep is False

    assert transitions[10].dest.parent_name == "State3"
    assert transitions[10].dest.history.is_deep is True


def do_test_diagram_fork_join(diagram):
    transitions = textx.get_children_of_type("TransitionExpression", diagram._model)
    assert len(transitions) == 7

    fork_joins = textx.get_children_of_type("ForkDeclarationExpression", diagram._model)
    assert len(fork_joins) == 2

    assert fork_joins[0].type == "<<fork>>"
    assert fork_joins[1].type == "<<join>>"
