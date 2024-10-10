from Typing import Type, VarType, ProcType, SecurityLevel, CmdType, Int, Bool, TypeEnvironment, Interface

from Environment import Environment, Reference

class Node:
    def __init__(self, pos) -> None:
        self.pos:tuple[int, int] = pos
        self.type_assignment = None
    
    def type_check(self, type_env:TypeEnvironment):
        return NotImplemented
    
    def pprint(self,indent, highlightpos = (), highlighted = False):
        return NotImplemented
    
    def evaluate(self, env:Environment):
        pass

class Expression(Node):
    def __init__(self, pos) -> None:
        super().__init__(pos)
        self.type_assignment: Type

class Statement(Node):
    def __init__(self, pos) -> None:
        super().__init__(pos)
        self.type_assignment: CmdType

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

    def evaluate(self, env: Environment):
        for contract in self.contracts:
            env.push({contract.name:Reference(contract)})
        
        for transaction in self.transactions:
            transaction.evaluate(env)

        for contract in self.contracts:
            env.pop()


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
        self.value:Expression = value
    
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
        self.statements:list[Statement] = statements
    
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

            if cmd_level.level < self.type_assignment.cmd_level.level:
                raise TypeError(f"Method of level {self.type_assignment.cmd_level.level} tries to access {cmd_level.level} at {statement.pos}")

        type_env.pop()

        return self.type_assignment

class ThrowStmt(Statement):
    def __init__(self, pos) -> None:
        super().__init__(pos)

    def type_check(self, type_env: TypeEnvironment):
        self.type_assignment = CmdType(SecurityLevel(0, max=True))
        return self.type_assignment
        
    def pprint(self, indent, highlightpos=(), highlighted=False):
        return "\t" * indent + "throw"

    def evaluate(self, env: Environment):
        raise Exception(f"Throws error at {self.pos}")

class AssignmentStmt(Statement):
    def __init__(self, pos, name, expression) -> None:
        super().__init__(pos)
        self.name:Expression = name
        self.expression:Expression = expression
    
    def type_check(self, type_env: TypeEnvironment):
        self.expression.type_check(type_env)
        self.name.type_check(type_env)

        if not self.expression.type_assignment < self.name.type_assignment:
            raise TypeError(f"Assigning type {self.expression.type_assignment} to variable of type {self.name.type_assignment}at {self.pos}")
        
        self.type_assignment = CmdType(self.name.type_assignment.sec)

    def evaluate(self, env: Environment):
        ref = self.name.evaluate(env)
        ref.value = self.expression.evaluate(env)
        return super().evaluate(env)

    def pprint(self, indent, highlightpos=(), highlighted=False):
        return "\t" * indent + f"{self.name} := {self.expression.pprint(indent+1)}" 

class VarAssignmentStmt(Statement):
    def __init__(self, pos, var_name, expression) -> None:
        super().__init__(pos)
        self.var_name = var_name
        self.expression:Expression = expression
    
    def type_check(self, type_env: TypeEnvironment):
        self.expression.type_check(type_env)

        if not self.expression.type_assignment < type_env.lookup(self.var_name):
            raise TypeError(f"Assigning type {self.expression.type_assignment} to variable of type {type_env.lookup(self.var_name)}at {self.pos}")
        
        self.type_assignment = CmdType(type_env.lookup(self.var_name).sec)

    def evaluate(self, env: Environment):
        env.lookup(self.var_name).value = self.expression.evaluate(env)

class FieldAssignmentStmt(Statement):
    def __init__(self, pos, contract, field_name, expression) -> None:
        super().__init__(pos)
        self.contract:Expression = contract
        self.field_name = field_name
        self.expression:Expression = expression
    
    def type_check(self, type_env: TypeEnvironment):
        self.expression.type_check(type_env)
        self.contract.type_check(type_env)

        field = self.contract.type_assignment.obj.get_field(self.field_name)

        if not self.expression.type_assignment < field.type:
            raise TypeError(f"Assigning type {self.expression.type_assignment} to variable of type {field.type} at {self.pos}")
        
        self.type_assignment = CmdType(field.type.sec)
        return self.type_assignment
    
    def evaluate(self, env: Environment):
        contract = self.contract.evaluate(env)
        for field in contract.fields:
            if field.name == self.field_name:
                field.value = self.expression.evaluate(env)

class VariableExpr(Expression):
    def __init__(self, pos, name) -> None:
        super().__init__(pos)
        self.name:str = name

    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = type_env.lookup(self.name)
        return self.type_assignment
    
    def pprint(self, indent, highlightpos=(), highlighted=False):
        return self.name
    
    def evaluate(self, env: Environment):
        return env.lookup(self.name).value



class FieldExpr(Expression):
    def __init__(self, pos, name, field) -> None:
        super().__init__(pos)
        self.name:Expression = name
        self.field:str = field
    
    def pprint(self, indent, highlightpos=(), highlighted=False):
        return f"{self.name.pprint(indent+1)}.{self.field}"

    def type_check(self, type_env:TypeEnvironment):
        self.name.type_check(type_env)
        interface = self.name.type_assignment.obj
        self.type_assignment = interface.get_field(self.field).type

        return self.type_assignment
    
    def evaluate(self, env: Environment):
        contract = self.name.evaluate(env)
        for field in contract.fields:
            if field.name == self.field:
                return field.value
                
        
class SkipStmt(Statement):
    def __init__(self, pos) -> None:
        super().__init__(pos)

    def pprint(self, indent, highlightpos=(), highlighted=False):
        return "\t"*indent + "skip"

    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = CmdType(SecurityLevel(max=True))
        return self.type_assignment
        
class IfStmt(Statement):
    def __init__(self, pos, cond, true_stmts, false_stmts) -> None:
        super().__init__(pos)
        self.cond:Expression = cond
        self.true_stmts:list[Statement] = true_stmts
        self.false_stmts:list[Statement] = false_stmts

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
    
    def evaluate(self, env: Environment):
        if self.cond.evaluate(env):
            for stmt in self.true_stmts:
                stmt.evaluate(env)
        else:
            for stmt in self.false_stmts:
                stmt.evaluate(env)
        


class WhileStmt(Statement):
    def __init__(self, pos, cond, stmts) -> None:
        super().__init__(pos)
        self.cond:Expression = cond
        self.stmts:list[Statement] = stmts

    def pprint(self, indent, highlightpos=(), highlighted=False):
        string =  "\t"*indent + f"while ({self.cond.pprint()}) " + "{\n"
        for statement in self.stmts:
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
            raise TypeError(f"Expression reads from {self.cond.type_assignment.sec} but writes to {cmd_lvl.level} at {self.pos}")


        self.type_assignment = cmd_lvl
    
    def evaluate(self, env: Environment):
        while self.cond.evaluate(env):
            for stmt in self.stmts:
                stmt.evaluate(env)


class BindStmt(Statement):
    def __init__(self, pos, name, type, expr, stmts) -> None:
        super().__init__(pos)
        self.name:str = name
        #todo: finish typing
        self.type = type
        self.expr:Expression = expr
        self.stmts:list[Statement] = stmts

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
        #TODO: finish typing
        type_env.push({self.name:self.type})
        self.expr.type_check(type_env)
        cmd_lvl = CmdType(SecurityLevel(max=True))
        for statement in self.stmts:
            statement.type_check(type_env)
            cmd_lvl = cmd_lvl.join(statement.type_assignment)
        
        if self.expr.type_assignment.sec > cmd_lvl.level:
            raise TypeError(f"Expression reads from higher than is written to at {self.pos}")
    
    def evaluate(self, env: Environment):
        env.push({self.name:Reference(self.expr.evaluate(env))})
        for statement in self.stmts:
            statement.evaluate(env)
        env.pop()
    

class IntConstantExpr(Expression):
    def __init__(self, pos, value) -> None:
        super().__init__(pos)
        self.value:int = value

    def pprint(self, indent, highlightpos=(), highlighted=False):
        return set(self.value)

    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = Type(type_env.get_interface("int"), SecurityLevel(0,min=True))
        return self.type_assignment
    
    def evaluate(self, env: Environment):
        return self.value


        

class BoolConstantExpr(Expression):
    def __init__(self, pos, value) -> None:
        super().__init__(pos)
        self.value:str = value

    def pprint(self, indent, highlightpos=(), highlighted=False):
        return "T" if self.value else "F"

    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = Type(type_env.get_interface("bool"), SecurityLevel(0,min=True))
        return self.type_assignment

    def evaluate(self, env: Environment):
        return self.value



class BinaryOp(Expression):
    def __init__(self, pos, op, lhs, rhs) -> None:
        super().__init__(pos)
        self.op:str = op
        self.lhs:Expression = lhs
        self.rhs:Expression = rhs
    
    def type_check(self, type_env:TypeEnvironment):
        self.lhs.type_check(type_env)
        self.rhs.type_check(type_env)

        #operators on ints that give ints
        if self.op in ["+", "-", "*"]:
            assert isinstance(self.lhs.type_assignment.obj, Int) 
            assert isinstance(self.rhs.type_assignment.obj, Int)
            self.type_assignment = Type(Int(), self.lhs.type_assignment.sec.join(self.rhs.type_assignment.sec))
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
    def evaluate(self, env: Environment):
        lhs = self.lhs.evaluate(env)
        rhs = self.rhs.evaluate(env)
        if self.op == "+":
            return lhs + rhs
        if self.op == "-":
            return lhs - rhs
        if self.op == "*":
            return lhs * rhs
        if self.op == "<":
            return lhs < rhs
        if self.op == ">":
            return lhs + rhs
        if self.op == ">=":
            return lhs >= rhs
        if self.op == "<=":
            return lhs <= rhs
        if self.op == "==":
            return lhs == rhs
        if self.op == "&&":
            return lhs and rhs
        if self.op == "||":
            return lhs or rhs


class UnaryOp(Expression):
    def __init__(self, pos, op, operand) -> None:
        super().__init__(pos)
        self.op:str = op
        self.operand:Expression = operand
    
    def pprint(self, indent, highlightpos=(), highlighted=False):
        return self.op + "(" + self.operand.pprint(indent+1) + ")"

    def type_check(self, type_env:TypeEnvironment):
        self.type_assignment = self.operand.type_check(type_env)
        return self.type_assignment

    def evaluate(self, env: Environment):
        return - self.operand.evaluate(env)
    
class MethodCall(Statement):
    def __init__(self, pos, name, method, vars, cost) -> None:
        super().__init__(pos)
        self.name:Expression = name
        self.method:str = method
        self.vars:list[Expression] = vars
        self.cost:Expression = cost

    def type_check(self, type_env:TypeEnvironment):
        self.name.type_check(type_env)
        self.cost.type_check(type_env)
        interface = self.name.type_assignment.obj
        
        method = interface.get_method(self.method)

        if method == None:
            raise TypeError(f"Trying to call nonexistant method at {self.pos}")
        
        self.type_assignment = method.type.cmd_level

        # note that dict preserves order
        var_types = list(method.type.variables.items()) 
        for var in range(len(method.type.variables)):
            self.vars[var].type_check(type_env)
            if not self.vars[var].type_assignment < var_types[var][1]:
                raise TypeError(f"Invalid parameter, expected {var_types[var][1]} but got {self.vars[var].type_assignment} at {self.pos}")

        balance_level = interface.get_field("balance").type.sec

        if balance_level < self.type_assignment.level:
            raise TypeError(f"Implicit write to balance writing to {balance_level} with method level {self.type_assignment.level} at {self.pos}")


        return self.type_assignment
    
    def evaluate(self, env: Environment):
        callee:Contract = self.name.evaluate(env)
        for method in callee.methods:
            if method.name == self.method:
                break
        
        method_env = {
            "value": Reference(self.cost.evaluate(env)),
            "caller": env.lookup("this"),
            "this": Reference(callee)
        }

        for field in env.lookup("this").value.fields:
            if field.name == "balance":
                field.value -= self.cost

        for field in callee.fields:
            if field.name == "balance":
                field.value += self.cost

        for ind in range(len(self.vars)):
            method_env[method.parameters[ind]] = self.vars[ind].evaluate()

        env.push(method_env)

        for statement in method.statements:
            statement.evaluate(env)

        env.pop()
    

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

        var_types = list(method.type.variables.items()) 
        for var in range(len(method.type.variables)):
            self.variables[var].type_check(type_env)
            if not self.variables[var].type_assignment < var_types[var][1]:
                raise TypeError(f"Invalid parameter, expected {var_types[var][1]} but got {self.variables[var].type_assignment} at {self.pos}")


        return super().type_check(type_env)
    
    def evaluate(self, env: Environment):
        callee:Contract = env.lookup(self.callee).value
        caller:Contract = env.lookup(self.caller).value
        for method in callee.methods:
            if method.name == self.method:
                break
        
        method_env = {
            "value": Reference(self.cost),
            "caller": Reference(caller),
            "this": Reference(callee)
        }

        for field in caller.fields:
            if field.name == "balance":
                field.value -= self.cost

        for field in callee.fields:
            if field.name == "balance":
                field.value += self.cost
        for ind in range(len(self.variables)):
            method_env[method.parameters[ind]] = self.vars[ind].evaluate()

        env.push(method_env)

        for statement in method.statements:
            statement.evaluate(env)

        env.pop()
    
class PrintStmt(Statement):
    def __init__(self, pos, expression) -> None:
        super().__init__(pos)
        self.expression:Expression = expression
    
    def type_check(self, type_env: TypeEnvironment):
        self.type_assignment = CmdType(SecurityLevel(max=True))
        return self.type_assignment

    def evaluate(self, env: Environment):
        print(self.expression.evaluate(env))


class UnsafeStmt(Statement):
    def __init__(self, pos, stmt):
        self.stmt = stmt
        super().__init__(pos)
    def evaluate(self, env):
        return self.stmt.evaluate(env)
    
    def type_check(self, type_env):
        self.type_assignment = CmdType(SecurityLevel(max=True))
        return self.type_assignment

class ArrayConstant(Expression):
    def __init__(self, pos, indices):
        super().__init__(pos)
        self.indices:list[Expression] = indices
    
    def type_check(self, type_env: TypeEnvironment):
        for index in self.indices:
            index.type_check(type_env)
        
    def evaluate(self, env: Environment):
        out = []
        for index in self.indices:
            out.append(Reference(index.evaluate(env)))
        return out

class ArrayAccess(Expression):
    def __init__(self, pos, array, index):
        super().__init__(pos)
        self.array:Expression = array
        self.index:Expression = index
    
    def type_check(self, type_env: TypeEnvironment):
        self.array.type_check(type_env)
        self.index.type_check(type_env)
        assert isinstance(self.index.type_assignment, Int), f"Index must be int, not {self.index.type_assignment.obj} at {self.pos}"
        self.type_assignment = self.array.type_assignment
        self.type_assignment.sec = self.type_assignment.sec.join(self.index.type_assignment.sec)
        return self.type_assignment

    def evaluate(self, env: Environment):
        array = self.array.evaluate(env)
        index = self.index.evaluate()
        return array[index]

class ArrayAssignemnt(Statement):
    def __init__(self, pos) -> None:
        super().__init__(pos)
        