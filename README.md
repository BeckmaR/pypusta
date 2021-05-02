[![Build](https://github.com/BeckmaR/pypusta/actions/workflows/python-app.yml/badge.svg)](https://github.com/BeckmaR/pypusta/actions/workflows/python-app.yml)

# pypusta

Pusta is the **P**lant **U**ML **Sta**te diagram parser.

It is designed to parse the textual description of a [PlantUML State Diagram](https://plantuml.com/state-diagram) and transform it into a semantic model of a statechart, consisting of a hierarchy of states and transitions. This "translational model" in turn could be transformed into another model, for example [SCXML](https://www.w3.org/TR/scxml/https://www.w3.org/TR/scxml/) or C code (neither is implemented yet).

## Parser
Unlike the original PlantUML parser which is implemented in Java and in regex, this project uses a custom-developed [textX](https://github.com/textX/textX) grammar.

## Model
The PlantUML notation is not exactly ideal for transforming into another representation. It has to be traversed top-to-bottom (declaration order matters) and contains expressions that are highly irrelevant for the semantic meaning of the bottom, for example the width of the generated image or colors of states. This package turns this notation into a true tree-like model, stripped of anything that does not matter - colors, notes and other data is parseable but not present in the output. For example, the package turns something like this:
```
@startuml
state "Req(Id)" as ReqId
state "Minor(Id)" as MinorId
state "Major(Id)" as MajorId

state c <<choice>>

Idle --> ReqId
ReqId --> c
c --> MinorId : [Id <= 10]
c --> MajorId : [Id > 10]
@enduml
```
into a model structured like this:
```
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
```
Labels of states and transitions are copied verbatim into the resulting model, the parser itself makes no assumption about the inner syntax of these expressions.
For more examples, see [tests/test_transformation.py](tests/test_transformation.py).
