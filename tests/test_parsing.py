import pusta

parser = pusta.Pusta()


def test_parsing(file):
    diagram = parser.parse_file(file)
