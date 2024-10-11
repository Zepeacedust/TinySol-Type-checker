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
    
    def __lt__(self, other:"Interface") -> bool:
        
        for field in other.fields:
            corresponds = self.get_field(field.name)
            if corresponds == None:
                return False
            if not corresponds < field:
                return False
        
        for method in other.methods:
            corresponds = self.get_field(method.name)
            if corresponds == None:
                return False
            if not corresponds < method:
                return False
        
         

class Int(Interface):
    def __init__(self) -> None:
        super().__init__("int", [], [])

class Bool(Interface):
    def __init__(self) -> None:
        super().__init__("bool", [], [])

class Array(Interface):
    def __init__(self, contained):
        super().__init__(f"array<{contained.name}>", [
        ], [
        ])
        
class Field:
    def __init__(self, name, type) -> None:
        self.name:str = name
        self.type:VarType = type
    
    def type_check(self, type_env:"TypeEnvironment"):
        self.type.obj = type_env.get_interface(self.type.obj)
    
    def __lt__(self, other:"Field") -> bool:
        return self.type < other.type

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
    
    def __repr__(self) -> str:
        return f"({self.obj.name}, {self.sec})"

    def __lt__(self, other:"Type") -> bool:
        #TODO: figure out proper interface subtyping
        return self.sec <= other.sec and self.obj.name == other.obj.name

class VarType:
    def __init__(self, type) -> None:
        self.type:Type = type
    
    def __lt__(self, other:"VarType"):
        if not other.type.sec < self.type.sec:
            return False


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

    def __repr__(self) -> str:
        if self.extreme == 0:
            return str(self.level)

        if self.extreme == 1:
            return "max"
        
        if self.extreme == -1:
            return "min"


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
        # TODO: elegantly handle arrays
        if name[-2:] == "[]":
            return Array(self.get_interface(name[:-2]))
        return self.interfaces[name]