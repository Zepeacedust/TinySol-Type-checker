class Interface:
    def __init__(self, name, fields, methods) -> None:
        self.name = name
        self.fields = fields
        self.methods = methods
    
    def type_check(self, type_env):
        for field in self.fields:
            field.type_check(type_env)
        
        type_env.push({"this":self})

        for method in self.methods:
            method.type_check(type_env)

        type_env.pop()

class Int:
    def __init__(self) -> None:
        pass

class Bool:
    def __init__(self) -> None:
        pass


class Field:
    def __init__(self, name, type) -> None:
        self.name = name
        self.type = type
    
    def type_check(self, type_env):
        self.type.obj = type_env.lookup(self.type.obj)

class Method:
    def __init__(self, name, vars, type) -> None:
        self.name = name
        self.vars = vars
        self.type = type
    
    def type_check(self, type_env):
        for variable in self.type.variables:
            self.type.variables[variable] = type_env.lookup(self.type.variables[variable])
        self.type.cmd_level = CmdType(SecurityLevel(int(self.type.cmd_level)))

class Type:
    def __init__(self, obj, sec) -> None:
        self.obj = obj
        self.sec = sec

class VarType:
    def __init__(self, type) -> None:
        self.type = type

class CmdType:
    def __init__(self, level) -> None:
        self.level = level

    def join(self,other):
        if self.level<other.level:
            return self
        return other


class ProcType:
    def __init__(self, variables, cmd_level) -> None:
        self.variables = variables
        self.cmd_level = cmd_level

class SecurityLevel:
    def __init__(self, level=0, min=False, max=False) -> None:
        self.level = level
        self.extreme = 0
        if min:
            self.extreme = -1
        elif max:
            self.extreme = 1

    def __lt__(self, other) -> bool:
        if self.extreme != other.extreme:
            return self.extreme < other.extreme
        return self.level < other.level

    def __le__(self, other) -> bool:
        if self.extreme < other.extreme:
            return True
        if self.extreme > other.extreme:
            return False
        if self.extreme == other.extreme:
            return self.level <= other.level

    def __eq__(self, other):
        if self.extreme == other.extreme:
            return self.level == other.level
        return self.level == other.level
    
    def join(self,other):
        if self<other:
            return other
        return self



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