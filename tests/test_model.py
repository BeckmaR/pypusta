import pusta
import os
import textx
import logging

parser = pusta.Pusta()

test_path = os.path.dirname(__file__)
diagram_path = os.path.join(test_path, "diagrams")


def test_diagram_1():
    file = os.path.join(diagram_path, "1.pu")
    diagram = parser.parse_file(file)

    transitions = textx.get_children_of_type("TransitionExpression", diagram._model)
    assert len(transitions) == 2

    assert transitions[0].src == '[*]'
    assert transitions[0].dest.name == 'State1'

    assert transitions[1].src.name == 'State1'
    assert transitions[1].dest == '[*]'


def test_diagram_2():
    file = os.path.join(diagram_path, "2.pu")
    diagram = parser.parse_file(file)

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


def test_diagram_3():
    file = os.path.join(diagram_path, "3.pu")
    diagram = parser.parse_file(file)

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


def test_diagram_4():
    file = os.path.join(diagram_path, "4.pu")
    diagram = parser.parse_file(file)

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


def test_diagram_5():
    file = os.path.join(diagram_path, "5.pu")
    diagram = parser.parse_file(file)

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


def test_diagram_6():
    file = os.path.join(diagram_path, "6.pu")
    diagram = parser.parse_file(file)

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


def test_diagram_7():
    file = os.path.join(diagram_path, "7.pu")
    diagram = parser.parse_file(file)

    transitions = textx.get_children_of_type("TransitionExpression", diagram._model)
    assert len(transitions) == 11

    alias = textx.get_children_of_type("StateAliasExpression", diagram._model)
    assert len(alias) == 1
    assert alias[0].longname == r"Accumulate Enough Data\nLong State Name"
    assert alias[0].name == "long1"


def test_diagram_8():
    file = os.path.join(diagram_path, "8.pu")
    diagram = parser.parse_file(file)

    transitions = textx.get_children_of_type("TransitionExpression", diagram._model)
    assert len(transitions) == 14

    assert transitions[8].dest.is_deep is False

    assert transitions[10].dest.parent_name == "State3"
    assert transitions[10].dest.history.is_deep is True
