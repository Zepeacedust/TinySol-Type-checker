class Interface:
    def __init__(self, name, fields, methods) -> None:
        self.name = name
        self.fields = fields
        self.methods = methods

class Field:
    def __init__(self, name, type) -> None:
        self.name = name
        self.type = type

class Method:
    def __init__(self, name, vars, type) -> None:
        self.name = name
        self.vars = vars
        self.type = type

class Type:
    def __init__(self) -> None:
        pass

class TypeEnvironment:
    def __init__(self, globals) -> None:
        self.stack = [globals]

    def push(self, binding):
        self.stack.append(binding)

    def pop(self):
        self.stack.pop()

    def lookup(self, name):
        ind = len(self.stack) - 1
        while ind >= 0:
            if name in self.stack[ind]:
                return self.stack[ind][name]
            ind -= 1