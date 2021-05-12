from pusta.generator.output import IndentedWriter
from pusta.generator.types import Type, CompositeType, type_registry


Type('void')
Type('int')
Type('bool')
Type('char')
Type('unsigned int')


class CEnum(CompositeType):
    def __init__(self, name, enumerators=None):
        super().__init__(name, enumerators)

    @property
    def name(self):
        return f"enum {super().name}"

    def __str__(self):
        writer = IndentedWriter()

        s = f"{self.name} {{"
        writer.append(s)
        writer.incr()
        writer.append(",\n".join([str(m) for m in self.members]))
        writer.decr()
        writer.append("};")
        return str(writer)


class CStruct(CompositeType):
    def __init__(self, name, members=None):
        super().__init__(name, members)

    @property
    def name(self):
        return f"struct {super().name}"

    def __str__(self):
        writer = IndentedWriter()
        writer.append(f"{self.name} {{")
        writer.incr()
        for m in self.members:
            if isinstance(m, str):
                m = m.rstrip(';')
            writer.append(f"{m};")
        writer.decr()
        writer.append("};")
        return str(writer)
