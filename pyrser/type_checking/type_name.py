# qualified (or not) type names


class TypeName(str):

    def __init__(self, value):
        super().__init__()
        self.value = value
        # split value into composed type and/or qualifiers
        self.components = value.split()

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return self.value.__hash__()

    def __lt__(self, oth) -> bool:
        if isinstance(oth, TypeName):
            return self.value < oth.value
        return self.value < oth

    def __eq__(self, oth) -> bool:
        if isinstance(oth, TypeName):
            return self.value == oth.value
        return self.value == oth

    def get_subcomponents(self) -> list:
        return self.components[1:]

    @property
    def is_polymorphic(self) -> bool:
        """
        Check if one of composed type name is poly
        """
        for c in self.components:
            if c[0] == '?':
                return True
        return False
