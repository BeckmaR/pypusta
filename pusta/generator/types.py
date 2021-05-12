
class TypeRegistry:
    def __init__(self):
        self._types = dict()

    def __getitem__(self, item):
        return self._types.__getitem__(item)

    def register(self, name, type):
        if name in self._types:
            raise KeyError(f"Type {name} exists already")
        self._types[name] = type

type_registry = TypeRegistry()

class Type:
    def __init__(self, name):
        self._name = name
        type_registry.register(name, self)

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self.name


class CompositeType(Type):
    def __init__(self, name, members=None):
        super().__init__(name)
        if not members:
            members = []
        self._members = members

    @property
    def members(self):
        return self._members