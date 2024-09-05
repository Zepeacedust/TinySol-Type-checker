class Node:
    def __init__(self, pos) -> None:
        self.pos = pos

class Blockchain(Node):
    def __init__(self, interfaces, contracts, transactions) -> None:
        super().__init__((0,0))
        self.interfaces = interfaces
        self.contracts = contracts
        self.transactions=transactions


class Contract(Node):
    def __init__(self, pos, name, fields, methods) -> None:
        super().__init__(pos)
        self.name = name
        self.fields = fields
        self.methods = methods

class FieldDec(Node):
    def __init__(self,pos, name, value) -> None:
        super().__init__(pos)
        self.name = name
        self.value = value

class MethodDec(Node):
    def __init__(self, pos, name, parameters, statements) -> None:
        super().__init__(pos)
        self.name = name
        self.parameters = parameters
        self.statements = statements

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

class FieldExpr(Node):
    def __init__(self, pos, name, field) -> None:
        super().__init__(pos)
        self.name = name
        self.field = field

class SkipStmt(Node):
    def __init__(self, pos) -> None:
        super().__init__(pos)

        
class IfStmt(Node):
    def __init__(self, pos, cond, true_stmts, false_stmts) -> None:
        super().__init__(pos)
        self.cond = cond
        self.true_stmts = true_stmts
        self.false_stmts = false_stmts

class WhileStmt(Node):
    def __init__(self, pos, cond, stmts) -> None:
        super().__init__(pos)
        self.cond = cond
        self.stmts = stmts

class BindStmt(Node):
    def __init__(self, pos, name, level, expr, stmts) -> None:
        super().__init__(pos)
        self.name = name
        self.level = level
        self.expr = expr
        self.stmts = stmts

class IntConstantExpr(Node):
    def __init__(self, pos, value) -> None:
        super().__init__(pos)
        self.value = value
        

class BoolConstantExpr(Node):
    def __init__(self, pos, value) -> None:
        super().__init__(pos)
        self.value = value

class BinaryOp(Node):
    def __init__(self, pos, op, lhs, rhs) -> None:
        super().__init__(pos)

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