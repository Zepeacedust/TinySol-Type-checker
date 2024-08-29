class Node:
    def __init__(self, pos) -> None:
        self.pos = pos

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
    def __init__(self, pos, name, expr, stmts) -> None:
        super().__init__(pos)
        self.name = name
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

class FieldLookupExpr(Node):
    def __init__(self, pos, expr, name) -> None:
        super().__init__(pos)
        self.expr = expr
        self.name = name

class VarLookupExpr(Node)