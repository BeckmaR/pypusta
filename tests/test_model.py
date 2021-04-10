import pusta
import os
import textx

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
