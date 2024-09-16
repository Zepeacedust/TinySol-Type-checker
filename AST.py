from Typing import Type, VarType, ProcType, SecurityLevel, CmdType, Int, Bool, TypeEnvironment, Interface

class Node:
    def __init__(self, pos) -> None:
        self.pos:tuple[int, int] = pos
        self.type_assignment = None
    
    def type_check(self, type_env:TypeEnvironment):
        return NotImplemented


class Blockchain(Node):
    def __init__(self, interfaces, contracts, transactions) -> None:
        super().__init__((0,0))
        self.interfaces:list[Interface] = interfaces
        self.contracts:list[Contract] = contracts
        self.transactions:list[Transaction] = transactions
    
    def type_check(self, type_env:TypeEnvironment):
        for contract in self.contracts:
            contract.type_check(type_env)


class Contract(Node):
    def __init__(self, pos, name, type,  fields, methods) -> None:
        super().__init__(pos)
        self.name:str = name
        self.type:Type = type
        self.fields:list[FieldDec] = fields
        self.methods:list[MethodDec] = methods
    
    def pprint(self):
        string = f"contract {self.name}" + " {\n"
        for field in self.fields:
            string += "\t" + field.pprint().replace("\n", "\t\n")
        
        for method in self.methods:
            string += "\t" + method.pprint().replace("\n", "\t\n")

        string += "}"

        return string

    def type_check(self, type_env:TypeEnvironment):
        obj = type_env.lookup(self.type.obj)
        self.type_assignment = Type(obj, self.type.sec)
        type_env.push({self.name:self.type_assignment})
        type_env.push({"this":self.type_assignment})
        
        for field in self.fields:
            field.type_check(type_env)

        type_env.pop()

        return self.type_assignment

class FieldDec(Node):
    def __init__(self,pos, name, value) -> None:
        super().__init__(pos)
        self.name:str = name
        self.value = value
    
    def type_check(self, type_env:TypeEnvironment):
        interface = type_env.lookup("this").obj
        
        for field in interface.fields:
            if field.name == self.name:
                self.type_assignment = field.type
                return self.type_assignment

        raise Exception(f"{self} not included in interface {interface}")
        

class MethodDec(Node):
    def __init__(self, pos, name, parameters, statements) -> None:
        super().__init__(pos)
        self.name:str = name
        self.parameters:list[str] = parameters
        self.statements:list[Node] = statements
    
    def pprint(self):
        string = f"{self.name}({', '.join(self.parameters)})" + " {\n" 
        for statement in self.statements:
            string += "\t" + statement.pprint().replace("\n", "\t\n")
        return string + "\n}\n"
        

    def type_check(self, type_env:TypeEnvironment):
        interface = type_env.lookup("this").obj
        method = interface.get_method()


        if method == None:
            raise Exception(f"{self.name} not included in interface {interface.name}")
        
        cmd_level = CmdType(SecurityLevel(0, max=True))
        for statement in self.statements:
            statement.type_check(type_env)
            cmd_level = cmd_level.join(statement.type_assignment)

            if cmd_level.level < self.type_assignment.cmd_level.level:
                raise TypeError(f"Method tries to accesst to high at {statement.pos}")

        return self.type_assignment

class ThrowStmt(Node):
    def __init__(self, pos) -> None:
        super().__init__(pos)


class AssignementStmt(Node):
    def __init__(self, pos, name, expression) -> None:
        super().__init__(pos)
        self.name = name
        self.expression = expression


class VariableExpr(Node):
    def __init__(self, pos, name) -> None:
        super().__init__(pos)
        self.name = name

    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = type_env.lookup(self.name)
        return self.type_assignment



class FieldExpr(Node):
    def __init__(self, pos, name, field) -> None:
        super().__init__(pos)
        self.name = name
        self.field = field
    
    def type_check(self, type_env:TypeEnvironment):
        self.name.type_check(type_env)
        interface = self.name.type_assignment.obj
        for field in interface.fields:
            if field.name == self.field:
                self.type_assignment = field.type
                return self.type_assignment
        
class SkipStmt(Node):
    def __init__(self, pos) -> None:
        super().__init__(pos)

    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = CmdType(SecurityLevel(max=True))
        return self.type_assignment
        
class IfStmt(Node):
    def __init__(self, pos, cond, true_stmts, false_stmts) -> None:
        super().__init__(pos)
        self.cond = cond
        self.true_stmts = true_stmts
        self.false_stmts = false_stmts

    def type_check(self, type_env:TypeEnvironment):
        # TODO: ensure that the types for the conditional, true, and false statements are compatible
        
        cmd_lvl = CmdType(SecurityLevel(max=True))
        
        self.cond.type_check(type_env)
        for statement in self.true_stmts:
            statement.type_check(type_env)
            cmd_lvl = cmd_lvl.join(statement.type_assignment)
        for statement in self.false_stmts:
            statement.type_check(type_env)
            cmd_lvl = cmd_lvl.join(statement.type_assignment)

        if self.cond.type_assignment.sec > cmd_lvl.level:
            raise TypeError(f"Expression reads from higher than is written to at {self.pos}")
        
        self.type_assignment=cmd_lvl
             


class WhileStmt(Node):
    def __init__(self, pos, cond, stmts) -> None:
        super().__init__(pos)
        self.cond = cond
        self.stmts = stmts

    def type_check(self, type_env:TypeEnvironment):
        # TODO: derive type from condition and statements
        self.cond.type_check(type_env)
        for statement in self.stmts:
            statement.type_check(type_env)
            


class BindStmt(Node):
    def __init__(self, pos, name, type, expr, stmts) -> None:
        super().__init__(pos)
        self.name = name
        self.type = type
        self.expr = expr
        self.stmts = stmts

    def type_check(self, type_env:TypeEnvironment):
        type_env.push({self.name:self})
        self.expr.type_check(type_env)
        cmd_lvl = CmdType(SecurityLevel(max=True))
        for statement in self.stmts:
            statement.type_check(type_env)
            cmd_lvl = cmd_lvl.join(statement.type_assignment)
        
        if self.expr.type_assignment.sec > cmd_lvl.level:
            raise TypeError(f"Expression reads from higher than is written to at {self.pos}")
        
        # TODO: derive type from condition and statements
    

class IntConstantExpr(Node):
    def __init__(self, pos, value) -> None:
        super().__init__(pos)
        self.value = value
    
    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = Type(Int(), SecurityLevel(min=True))
        return self.type_assignment


        

class BoolConstantExpr(Node):
    def __init__(self, pos, value) -> None:
        super().__init__(pos)
        self.value = value


    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = Type(Bool(), SecurityLevel(min=True))
        return self.type_assignment



class BinaryOp(Node):
    def __init__(self, pos, op, lhs, rhs) -> None:
        super().__init__(pos)
        self.op = op
        self.lhs=lhs
        self.rhs = rhs
    
    def type_check(self, type_env:TypeEnvironment):
        self.lhs.type_check(type_env)
        self.rhs.type_check(type_env)

        #operators on ints that give ints
        if self.op in ["+", "-", "*"]:
            assert isinstance(self.lhs.type_assignment, Int) 
            assert isinstance(self.rhs.type_assignment, Int)
            self.type_assignment = Type(Int(), self.lhs.type_assignment.sec.join(self.rhs.type_assignment.sec))
            self.type_assignment = Type(Int(), self.lhs.type_assignment.join(self.rhs.type_assignment))
        #operators on ints that give bools
        elif self.op in ["<",">",">=","<="]:
            assert isinstance(self.lhs.type_assignment, Int) 
            assert isinstance(self.rhs.type_assignment, Int)
            self.type_assignment = Type(Bool(), self.lhs.type_assignment.sec.join(self.rhs.type_assignment.sec))
        #operators on bool that give bools
        elif self.op in ["and", "or"]:
            if not isinstance(self.lhs.type_assignment, Bool):
                raise TypeError(f"Expected bool, but got {type(self.lhs.type_assignment)} {self.lhs.type_assignment}")
            assert isinstance(self.rhs.type_assignment, Bool)
            self.type_assignment = Type(Bool(), self.lhs.type_assignment.sec.join(self.rhs.type_assignment.sec))
        #operations on comparable types that give bools
        elif self.op == "==":
            if not type(self.lhs.type_assignment.obj) == type(self.rhs.type_assignment.obj):
                raise TypeError(f"Incomparable types {type(self.lhs.type_assignment.obj)} and {type(self.rhs.type_assignment.obj)} at {self.pos}")
            self.type_assignment = Type(Bool(), self.lhs.type_assignment.sec.join(self.rhs.type_assignment.sec))


        return self.type_assignment


class UnaryOp(Node):
    def __init__(self, pos, op, operand) -> None:
        super().__init__(pos)
        self.op = op
        self.operand = operand
    
    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = self.operand.type_check(type_env)
        return self.type_assignment

class MethodCall(Node):
    def __init__(self, pos, name, method, vars, cost) -> None:
        super().__init__(pos)
        self.name = name
        self.method = method
        self.vars = vars
        self.cost = cost

    def type_check(self, type_env:TypeEnvironment):
        self.name.type_check(type_env)
        interface = self.name.type_assignment.obj

        #TODO: ensure variables are correctly typed

        for method in interface.methods:
            if method.name == self.method:
                
                self.type_assignment = method.type.cmd_level
                return self.type_assignment
        return super().type_check(type_env)
    

class Transaction(Node):
    def __init__(self, pos, caller, callee, method, variables, cost) -> None:
        super().__init__(pos)
        self.caller = caller
        self.callee = callee
        self.method = method
        self.variables = variables
        self.cost = cost
    
    def type_check(self, type_env:TypeEnvironment):
        interface = type_env.lookup(self.callee).obj

        method = interface.get_method(self.method)

        if method == None:
            raise Exception(f"{self.method} not included in interface {interface.name}")

        for variable in method.vars:
            print(variable)        

        return super().type_check(type_env)