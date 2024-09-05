class Interface:
    def __init__(self, fields, methods) -> None:
        self.fields = fields
        self.methods = methods

class Field:
    def __init__(self, name, type) -> None:
        self.name = name
        self.type = type

class Method:
    def __init__(self, name, vars, own_type) -> None:
        self.name = name
        self.vars = vars
        self.own_type = own_type

class Type:
    def __init__(self) -> None:
        pass

class TypeEnvironment:
    pass