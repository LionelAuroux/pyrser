# qualified (or not) type names

class TypeName(str):

    def __init__(self, value):
        super().__init__()
        self.value = value
        # split value into composed type and/or qualifiers
        self.components = value.split()

    def __str__(self):
        return self.value

    def __lt__(self, oth):
        if isinstance(oth, TypeName):
            return self.value < oth.value
        return self.value < oth

    def __eq__(self, oth):
        if isinstance(oth, TypeName):
            return self.value == oth.value
        return self.value == oth

    def get_subcomponents(self):
        return self.components[1:]

    def is_polymorphic(self):
        return self.value[0] == '?'
