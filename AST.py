from Typing import Type, VarType, ProcType, SecurityLevel, CmdType, Int, Bool, TypeEnvironment, Interface

class Node:
    def __init__(self, pos) -> None:
        self.pos:tuple[int, int] = pos
        self.type_assignment = None
    
    def type_check(self, type_env:TypeEnvironment):
        return NotImplemented
    
    def pprint(self,indent, highlightpos = (), highlighted = False):
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

    def pprint(self,indent, highlightpos = (), highlighted = False):
        for interface in self.interfaces:
            interface.pprint(indent)
        
        for contract in self.contracts:
            contract.pprint(indent)

class Contract(Node):
    def __init__(self, pos, name, type,  fields, methods) -> None:
        super().__init__(pos)
        self.name:str = name
        self.type:Type = type
        self.fields:list[FieldDec] = fields
        self.methods:list[MethodDec] = methods

    def pprint(self,indent, highlightpos = (), highlighted = False):
        string = "\t" * indent + f"contract {self.name}" + " {\n"
        for field in self.fields:
            string += field.pprint(indent+1)
        
        for method in self.methods:
            string += method.pprint(indent+1)

        string += "\t" * indent + "}"

        return string

    def type_check(self, type_env:TypeEnvironment):
        obj = type_env.get_interface(self.type.obj)
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
    
    def pprint(self, indent):
        return "\t"*indent + f"field {self.name} := {self.value.pprint(indent+1)}"
    
    def type_check(self, type_env:TypeEnvironment):
        interface = type_env.lookup("this").obj
        
        field = interface.get_field(self.name)
        if field == None:
            raise Exception(f"{self.name} not included in interface {interface.name}")
        self.type_assignment = field.type
        
        if isinstance(self.type_assignment.obj, Int):
            self.value = int(self.value)
        else:
            self.value = self.value == "T"

        

class MethodDec(Node):
    def __init__(self, pos, name, parameters, statements) -> None:
        super().__init__(pos)
        self.name:str = name
        self.parameters:list[str] = parameters
        self.statements:list[Node] = statements
    
    def pprint(self,indent, highlightpos = (), highlighted = False):
        string = "\t" * indent + f"{self.name}({', '.join(self.parameters)})" + " {\n" 
        for statement in self.statements:
            string += "\t"*indent + statement.pprint(indent+1) + ";\n"
        string += "\t" * indent + "}\n"
        return string
        

    def type_check(self, type_env:TypeEnvironment):
        interface = type_env.lookup("this").obj
        method = interface.get_method(self.name)
        if method == None:
            raise Exception(f"{self.name} not included in interface {interface.name}")
        

        self.type_assignment = method.type

        local_variables = {
            "sender":Type(type_env.get_interface("obj"), SecurityLevel(0, max=True)),
            "value":Type(Int, self.type_assignment.cmd_level.level),
        }

        for var in self.type_assignment.variables:
            local_variables[var] = self.type_assignment.variables[var]

        type_env.push(local_variables)

        cmd_level = CmdType(SecurityLevel(0, max=True))
        for statement in self.statements:
            statement.type_check(type_env)
            cmd_level = cmd_level.join(statement.type_assignment)

            if cmd_level.level > self.type_assignment.cmd_level.level:
                raise TypeError(f"Method tries to access too high at {statement.pos}")

        type_env.pop()

        return self.type_assignment

class ThrowStmt(Node):
    def __init__(self, pos) -> None:
        super().__init__(pos)

    def pprint(self, indent, highlightpos=(), highlighted=False):
        return "\t" * indent + "throw"

class AssignmentStmt(Node):
    def __init__(self, pos, name, expression) -> None:
        super().__init__(pos)
        self.name:Node = name
        self.expression:Node = expression
    
    def type_check(self, type_env: TypeEnvironment):
        self.expression.type_check(type_env)
        self.name.type_check(type_env)

        self.type_assignment = CmdType(self.name.type_assignment.sec)

        if self.type_assignment.level < self.expression.type_assignment.sec:
            raise TypeError(f"Reading from higher than writing to at {self.pos}")
        

    def pprint(self, indent, highlightpos=(), highlighted=False):
        return "\t" * indent + f"{self.name} := {self.expression.pprint(indent+1)}" 


class VariableExpr(Node):
    def __init__(self, pos, name) -> None:
        super().__init__(pos)
        self.name = name

    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = type_env.lookup(self.name)
        return self.type_assignment
    
    def pprint(self, indent, highlightpos=(), highlighted=False):
        return self.name



class FieldExpr(Node):
    def __init__(self, pos, name, field) -> None:
        super().__init__(pos)
        self.name:Node = name
        self.field:str = field
    
    def pprint(self, indent, highlightpos=(), highlighted=False):
        return f"{self.name.pprint(indent+1)}.{self.field}"

    def type_check(self, type_env:TypeEnvironment):
        self.name.type_check(type_env)
        interface = self.name.type_assignment.obj
        self.type_assignment = interface.get_field(self.field).type

        return self.type_assignment
        
class SkipStmt(Node):
    def __init__(self, pos) -> None:
        super().__init__(pos)

    def pprint(self, indent, highlightpos=(), highlighted=False):
        return "\t"*indent + "skip"

    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = CmdType(SecurityLevel(max=True))
        return self.type_assignment
        
class IfStmt(Node):
    def __init__(self, pos, cond, true_stmts, false_stmts) -> None:
        super().__init__(pos)
        self.cond:Node = cond
        self.true_stmts:list[Node] = true_stmts
        self.false_stmts:list[Node] = false_stmts

    def pprint(self, indent, highlightpos=(), highlighted=False):
        string =  "\t"*indent + f"if ({self.cond.pprint()}) " + "{\n"
        for statement in self.true_stmts:
            string += statement.pprint(indent+1) + ";\n"
        string += "\t" * indent + "}"
        if self.false_stmts != []:
            string += "else {"
            for statement in self.false_stmts:
                string +=  statement.pprint(indent+1) + ";\n"
            string += "\t*indent" + "};"
        return string

    def type_check(self, type_env:TypeEnvironment):
        
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
        self.cond:Node = cond
        self.stmts:list[Node] = stmts

    def pprint(self, indent, highlightpos=(), highlighted=False):
        string =  "\t"*indent + f"while ({self.cond.pprint()}) " + "{\n"
        for statement in self.true_stmts:
            string += statement.pprint(indent+1) + ";\n"
        string += "\t" * indent + "};"
        return string

    def type_check(self, type_env:TypeEnvironment):

                
        cmd_lvl = CmdType(SecurityLevel(max=True))
        
        self.cond.type_check(type_env)
        for statement in self.stmts:
            statement.type_check(type_env)
            cmd_lvl = cmd_lvl.join(statement.type_assignment)

        if self.cond.type_assignment.sec > cmd_lvl.level:
            raise TypeError(f"Expression reads from higher than is written to at {self.pos}")


        self.type_assignment = cmd_lvl
            


class BindStmt(Node):
    def __init__(self, pos, name, type, expr, stmts) -> None:
        super().__init__(pos)
        self.name = name
        self.type = type
        self.expr = expr
        self.stmts = stmts

    def pprint(self, indent, highlightpos=(), highlighted=False):
        string =  "\t"*indent + f"if ({self.cond.pprint()}) " + "{\n"
        for statement in self.true_stmts:
            string += statement.pprint(indent+1) + ";\n"
        string += "\t" * indent + "}"
        if self.false_stmts != []:
            string += "else {"
            for statement in self.false_stmts:
                string +=  statement.pprint(indent+1) + ";\n"
            string += "\t*indent" + "}"
        return string

    def type_check(self, type_env:TypeEnvironment):
        type_env.push({self.name:self.type})
        self.expr.type_check(type_env)
        cmd_lvl = CmdType(SecurityLevel(max=True))
        for statement in self.stmts:
            statement.type_check(type_env)
            cmd_lvl = cmd_lvl.join(statement.type_assignment)
        
        if self.expr.type_assignment.sec > cmd_lvl.level:
            raise TypeError(f"Expression reads from higher than is written to at {self.pos}")
        
    

class IntConstantExpr(Node):
    def __init__(self, pos, value) -> None:
        super().__init__(pos)
        self.value = value

    def pprint(self, indent, highlightpos=(), highlighted=False):
        return set(self.value)

    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = Type(Int(), SecurityLevel(min=True))
        return self.type_assignment


        

class BoolConstantExpr(Node):
    def __init__(self, pos, value) -> None:
        super().__init__(pos)
        self.value = value

    def pprint(self, indent, highlightpos=(), highlighted=False):
        return "T" if self.value else "F"

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

            if not isinstance(self.lhs.type_assignment.obj, Int):
                raise TypeError(f"Expected int, but got {type(self.lhs.type_assignment.obj)} {self.lhs.type_assignment.obj}")
            if not isinstance(self.rhs.type_assignment.obj, Int):
                raise TypeError(f"Expected int, but got {type(self.lhs.type_assignment.obj)} {self.rhs.type_assignment.obj}")

            self.type_assignment = Type(Bool(), self.lhs.type_assignment.sec.join(self.rhs.type_assignment.sec))
        #operators on bool that give bools
        elif self.op in ["&&", "||"]:
            if not isinstance(self.lhs.type_assignment.obj, Bool):
                raise TypeError(f"Expected bool, but got {type(self.lhs.type_assignment.obj)} {self.lhs.type_assignment.obj}")
            if not isinstance(self.rhs.type_assignment.obj, Bool):
                raise TypeError(f"Expected bool, but got {type(self.lhs.type_assignment.obj)} {self.rhs.type_assignment.obj}")
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
    
    def pprint(self, indent, highlightpos=(), highlighted=False):
        return self.op + "(" + self.operand.pprint(indent+1) + ")"

    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = self.operand.type_check(type_env)
        return self.type_assignment

class MethodCall(Node):
    def __init__(self, pos, name, method, vars, cost) -> None:
        super().__init__(pos)
        self.name:Node = name
        self.method = method
        self.vars = vars
        self.cost = cost

    def type_check(self, type_env:TypeEnvironment):
        self.name.type_check(type_env)
        interface = self.name.type_assignment.obj

        #TODO: ensure variables are correctly typed

        method = interface.get_method(self.method)
        if method == None:
            raise TypeError(f"Trying to call nonexistant method at {self.pos}")
        self.type_assignment = method.type.cmd_level

        return self.type_assignment
    

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

        # TODO: finish implemenetation

        if method == None:
            raise Exception(f"{self.method} not included in interface {interface.name}")

        for variable in method.vars:
            print(variable)        

        return super().type_check(type_env)