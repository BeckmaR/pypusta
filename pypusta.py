"""
Parser for PlantUML state diagrams.
"""
import pusta

parser = pusta.Pusta()

diagram = parser.parse_file("tests/diagrams/1.pu")

print(diagram)