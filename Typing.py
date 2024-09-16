class Interface:
    def __init__(self, name, fields, methods) -> None:
        self.name = name
        self.fields:list[Field] = fields
        self.methods:list[Method] = methods
    
    def type_check(self, type_env:"TypeEnvironment") -> None:
        for field in self.fields:
            field.type_check(type_env)
        
        type_env.push({"this":self})

        for method in self.methods:
            method.type_check(type_env)

        type_env.pop()

    def get_method(self, name) -> "Method":
        for method in self.methods:
            if method.name == name:
                return method

    def get_field(self, name) -> "Field":
        for field in self.fields:
            if field.name == name:
                return field

class Int(Interface):
    def __init__(self) -> None:
        super().__init__("int", [], [])

class Bool(Interface):
    def __init__(self) -> None:
        super().__init__("bool", [], [])


class Field:
    def __init__(self, name, type) -> None:
        self.name:str = name
        self.type:VarType = type
    
    def type_check(self, type_env:"TypeEnvironment"):
        self.type.obj = type_env.get_interface(self.type.obj)

class Method:
    def __init__(self, name, vars, type) -> None:
        self.name:str = name
        self.vars:dict[str:Type] = vars
        self.type:ProcType = type
    
    def type_check(self, type_env:"TypeEnvironment"):
        for variable in self.type.variables:
            self.type.variables[variable].obj = type_env.get_interface(self.type.variables[variable].obj)
        self.type.cmd_level = CmdType(SecurityLevel(int(self.type.cmd_level)))

class Type:
    def __init__(self, obj, sec) -> None:
        self.obj:Interface = obj
        self.sec:SecurityLevel = sec

class VarType:
    def __init__(self, type) -> None:
        self.type:Type = type

class CmdType:
    def __init__(self, level) -> None:
        self.level:SecurityLevel = level

    def join(self,other:"CmdType") -> "CmdType":
        if self.level<other.level:
            return self
        return other


class ProcType:
    def __init__(self, variables, cmd_level) -> None:
        self.variables:dict[str:Type] = variables
        self.cmd_level:CmdType = cmd_level

class SecurityLevel:
    def __init__(self, level=0, min=False, max=False) -> None:
        self.level:int = level
        self.extreme:int = 0
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

    def __eq__(self, other) -> bool:
        if self.extreme == other.extreme:
            return self.level == other.level
        return self.level == other.level
    
    def join(self,other: "SecurityLevel") -> "SecurityLevel":
        if self<other:
            return other
        return self



class TypeEnvironment:
    def __init__(self, globals, interfaces) -> None:
        self.stack:list[dict[str,Type]] = [globals]
        self.interfaces:dict[str,Interface] = interfaces

    def push(self, binding:dict[str:Type]) -> None:
        self.stack.append(binding)

    def pop(self) -> None:
        self.stack.pop()

    def lookup(self, name)-> Type:
        ind = len(self.stack) - 1
        while ind >= 0:
            if name in self.stack[ind]:
                return self.stack[ind][name]
            ind -= 1
    
    def get_interface(self, name:str) -> Interface:
        return self.interfaces[name]