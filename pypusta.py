"""
Parser for PlantUML state diagrams.
"""
import pusta

parser = pusta.Pusta()

diagram = parser.parse_file("tests/diagrams/5.pu")

print(diagram)