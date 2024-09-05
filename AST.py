class Node:
    def __init__(self, pos) -> None:
        self.pos = pos
        self.type_assignment = None
    
    def type_check(self, type_env):
        return NotImplemented


class Blockchain(Node):
    def __init__(self, interfaces, contracts, transactions) -> None:
        super().__init__((0,0))
        self.interfaces = interfaces
        self.contracts = contracts
        self.transactions= transactions
    
    def type_check(self, type_env):
        for contract in self.contracts:
            contract.type_check(type_env)


class Contract(Node):
    def __init__(self, pos, name, interface,  fields, methods) -> None:
        super().__init__(pos)
        self.name = name
        self.interface = interface
        self.fields = fields
        self.methods = methods
    
    def pprint(self):
        string = f"contract {self.name}" + " {\n"
        for field in self.fields:
            string += "\t" + field.pprint().replace("\n", "\t\n")
        
        for method in self.methods:
            string += "\t" + method.pprint().replace("\n", "\t\n")

        string += "}"

        return string

    def type_check(self, type_env):
        self.type_assignment = type_env.lookup(self.interface)
        type_env.push({"this":self})
        
        for field in self.fields:
            field.type_check(type_env)

        for method in self.methods:
            method.type_check(type_env)

        type_env.pop()

        return self.type_assignment

class FieldDec(Node):
    def __init__(self,pos, name, value) -> None:
        super().__init__(pos)
        self.name = name
        self.value = value
    
    def type_check(self, type_env):
        interface = type_env.lookup("this").type_assignment
        
        for field in interface.fields:
            if field.name == self.name:
                self.type_assignment = field.type
                return self.type_assignment

        raise Exception(f"{self} not included in interface {interface}")
        

class MethodDec(Node):
    def __init__(self, pos, name, parameters, statements) -> None:
        super().__init__(pos)
        self.name = name
        self.parameters = parameters
        self.statements = statements
    
    def pprint(self):
        string = f"{self.name}({', '.join(self.parameters)})" + " {\n" 
        for statement in self.statements:
            string += "\t" + statement.pprint().replace("\n", "\t\n")
        return string + "\n}\n"
        

    def type_check(self, type_env):
        interface = type_env.lookup("this").type_assignment
        found = False
        for method in interface.methods:
            if method.name == self.name:
                self.type_assignment = method.type
                found = True
                break

        if not found:
            raise Exception(f"{self.name} not included in interface {interface.name}")
        
        for statement in self.statements:
            statement.type_check(type_env)

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

    def type_check(self, type_env):
        self.type_assignment = type_env.lookup(self.name)
        return self.type_assignment



class FieldExpr(Node):
    def __init__(self, pos, name, field) -> None:
        super().__init__(pos)
        self.name = name
        self.field = field
    
    def type_check(self, type_env):
        interface = type_env.lookup(self.name).type_assignment
        for field in interface.fields:
            if field.name == self.field:
                self.type_assignment = field.type
                return self.type_assignment
        
class SkipStmt(Node):
    def __init__(self, pos) -> None:
        super().__init__(pos)

    def type_check(self, type_env):
        return None
        
class IfStmt(Node):
    def __init__(self, pos, cond, true_stmts, false_stmts) -> None:
        super().__init__(pos)
        self.cond = cond
        self.true_stmts = true_stmts
        self.false_stmts = false_stmts

    def type_check(self, type_env):
        # TODO: ensure that the types for the conditional, true, and false statements are compatible
        self.cond.type_check(type_env)
        for statement in self.true_stmts:
            statement.type_check(type_env)
        for statement in self.false_stmts:
            statement.type_check(type_env)
             

class WhileStmt(Node):
    def __init__(self, pos, cond, stmts) -> None:
        super().__init__(pos)
        self.cond = cond
        self.stmts = stmts

    def type_check(self, type_env):
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

    def type_check(self, type_env):
        type_env.push({self.name:self})
        self.expr.type_check(type_env)
        for statement in self.stmts:
            statement.type_check(type_env)
        # TODO: derive type from condition and statements
    

class IntConstantExpr(Node):
    def __init__(self, pos, value) -> None:
        super().__init__(pos)
        self.value = value
    
    def type_check(self, type_env):
        # TODO: Decide what the type is for a constant
        pass

        

class BoolConstantExpr(Node):
    def __init__(self, pos, value) -> None:
        super().__init__(pos)
        self.value = value


    def type_check(self, type_env):
        # TODO: Decide what the type is for a constant
        pass


class BinaryOp(Node):
    def __init__(self, pos, op, lhs, rhs) -> None:
        super().__init__(pos)
        self.op = op
        self.lhs=lhs
        self.rhs = rhs
    
    def type_check(self, type_env):
        self.lhs.type_check(type_env)
        self.rhs.type_check(type_env)


class UnaryOp(Node):
    def __init__(self, pos, op, operand) -> None:
        super().__init__(pos)

class MethodCall(Node):
    def __init__(self, pos, name, method, vars, cost) -> None:
        super().__init__(pos)
        self.name = name
        self.method = method
        self.vars = vars
        self.cost = cost
