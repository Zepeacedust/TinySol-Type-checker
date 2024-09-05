from lexer import Lexer, TokenType
import AST
import Typing


class Parser:
    def __init__(self, filename) -> None:
        self.lexer = Lexer(filename)

    def parse(self) -> AST.Blockchain:
        interfaces = []
        while self.lexer.lookahead().text == "interface":
            interfaces.append(self.interface())


        contracts = []
        while self.lexer.lookahead().text == "contract":
            contracts.append(self.contract())
        
        transactions = []
        while self.lexer.lookahead().type == TokenType.IDENTIFIER:
            transactions.append(self.transaction())

        return AST.Blockchain(interfaces, contracts, transactions)

    def interface(self):
        self.lexer.expect(text="interface")
        name = self.lexer.expect(type=TokenType.IDENTIFIER)
        self.lexer.expect("{")

        field_types = []
        while self.lexer.lookahead().text == "field":
            field_types.append(self.field_interface())

        method_types = []
        while self.lexer.lookahead().text == "method":
            method_types.append(self.method_interface())

        self.lexer.expect("}")

        return Typing.Interface(field_types, method_types)

    def field_interface(self):
        self.lexer.expect(text="field")
        name = self.lexer.expect(type=TokenType.IDENTIFIER).text
        self.lexer.expect(":")
        level = self.lexer.next_token()
        # TODO: parse level
        self.lexer.expect(";")
        return Typing.Field(name, level)
    
    def method_interface(self):
        self.lexer.expect("method")
        name = self.lexer.expect(type=TokenType.IDENTIFIER)
        self.lexer.expect(":")
        self.lexer.expect("(")
        variables = []
        if self.lexer.lookahead().text != ")":
            pass
        self.lexer.expect(")")
        self.lexer.expect("->")
        out_type = self.lexer.next_token()
        self.lexer.expect(";")

        return Typing.Method(name, variables, out_type)

    def contract(self):
        self.lexer.expect(text="contract")
        
        name = self.lexer.expect(type=TokenType.IDENTIFIER)
        
        self.lexer.expect(":")

        interface = self.lexer.expect(type=TokenType.IDENTIFIER)

        self.lexer.expect(text="{")


        fields = []
        while self.lexer.lookahead().text == "field":
            fields.append(self.field())
        
        methods = []

        while self.lexer.lookahead().text != "}":
            methods.append(self.method())
        
        self.lexer.expect(text="}")

        return AST.Contract(name.pos, name.text, fields, methods)

    def field(self):
        self.lexer.expect(text="field")
        name = self.lexer.expect(type=TokenType.IDENTIFIER)
        self.lexer.expect(text=":=")
        value = self.lexer.expect(type=TokenType.CONSTANT)
        self.lexer.expect(text=";")
        return AST.FieldDec(name.pos, name.text, int(value.text))
    
    def method(self):
        name = self.lexer.expect(type=TokenType.IDENTIFIER)
        self.lexer.expect(text="(")
        parameters = []
        if self.lexer.lookahead().text != ")":
            parameters.append(self.lexer.expect(type=TokenType.IDENTIFIER).text)
            while self.lexer.lookahead().text == ",":
                self.lexer.expect(text=",")
                parameters.append(self.lexer.expect(type=TokenType.IDENTIFIER).text)
        self.lexer.expect(text=")")
        self.lexer.expect(text="{")
        statements = self.statements()
        self.lexer.expect(text="}")
        return AST.MethodDec(name.pos, name.text, parameters, statements)
    

    def statements(self):
        statements= []
        statements.append(self.statement())
        while self.lexer.lookahead().text == ";":
            statements.append(self.statement())
        
        return statements

    def statement(self):
        first = self.lexer.lookahead()
        # expression or assigment are the only ones that can start on an identifer
        if first.type == TokenType.IDENTIFIER:
            expression = self.expression()
            if isinstance(expression, AST.VariableExpr) or isinstance(expression, AST.FieldExpr):
                if self.lexer.lookahead().text == ":=":
                    self.lexer.expect(text=":=")
                    value_expression = self.expression()
                    return AST.AssignementStmt(first.pos, expression, value_expression)
            
            if isinstance(expression, AST.FieldExpr):
                if self.lexer.lookahead().text == "(":
                    vars = []
                    self.lexer.expect(text="(")

                    if self.lexer.lookahead().text != ")":
                        vars.append(self.expression())
                    
                    while self.lexer.lookahead().text == ",":
                        self.lexer.expect(",")
                        vars.append(self.expression())
                    self.lexer.expect(text=")")
                    
                    cost = AST.IntConstantExpr(first.pos, 0)

                    if self.lexer.lookahead().text == ":":
                        self.lexer.expect(text=":")
                        cost = self.expression()
                    
                    
                    return AST.MethodCall(first.pos, expression.name, expression.field, vars, cost)
            return expression
        
        if first.text == "skip":
            self.lexer.expect(text="skip")
            return AST.SkipStmt(first.pos)
        
        if first.text == "throw":
            self.lexer.expect(text="throw")
            return AST.ThrowStmt(first.pos)
        
        if first.text == "var":
            self.lexer.expect(text="var")
            name = self.lexer.expect(type=TokenType.IDENTIFIER)
            self.lexer.expect(":")
            # TODO: better type evaluation, not just feeding the token
            level = self.lexer.next_token()
            self.lexer.expect(text=":=")
            expr = self.expression()
            self.lexer.expect(text="in")
            statements = self.statement()
            
            return AST.BindStmt(name.pos, name.text,level, expr, statements)
        
        if first.text == "if":
            self.lexer.expect(text="if")
            cond = self.expression()

            self.lexer.expect(text="then")
            self.lexer.expect(text="{")
            true_stmts = self.statements()
            self.lexer.expect(text="}")
            
            self.lexer.expect(text="else")
            self.lexer.expect(text="{")
            false_stmts = self.statements()
            self.lexer.expect(text="}")
            
            return AST.IfStmt(first.pos, cond, true_stmts, false_stmts)
        
        if first.text == "while":
            self.lexer.expect(text="while")
            cond = self.expression()
            self.lexer.expect(text="do")
            self.lexer.expect(text="{")
            stmts = self.statements()
            self.lexer.expect(text="}")
            return AST.WhileStmt(first.pos, cond, stmts)
        
    def expression(self):
        first = self.comparison()
        while self.lexer.lookahead().text in ["||", "&&"]:
            op = self.lexer.expect(type=TokenType.CONTROL)
            rhs = self.comparison()
            first = AST.BinaryOp(op.pos, op.text, first, rhs)
        return first

    def comparison(self):
        first = self.multiplication()
        while self.lexer.lookahead().text in ["==", "<", ">", "<=", ">="]:
            op = self.lexer.expect(type=TokenType.CONTROL)
            rhs = self.multiplication()
            first = AST.BinaryOp(op.pos, op.text, first, rhs)
        return first

    def multiplication(self):
        first = self.addition()
        while self.lexer.lookahead().text in ["*", "//"]:
            op = self.lexer.expect(type=TokenType.CONTROL)
            rhs = self.addition()
            first = AST.BinaryOp(op.pos, op.text, first, rhs)
        return first

    def addition(self):
        first = self.unary()
        while self.lexer.lookahead().text in ["+", "-"]:
            op = self.lexer.expect(type=TokenType.CONTROL)
            rhs = self.unary()
            first = AST.BinaryOp(op.pos, op.text, first, rhs)
        return first

    def unary(self):
        first = self.lexer.next_token()
        if first.type == TokenType.CONSTANT:
            if first.text.isdigit():
                curr =  AST.IntConstantExpr(first.pos, int(first.text))
            else:
                curr = AST.BoolConstantExpr(first.pos, first.text=="T")
        
        if first.type == TokenType.IDENTIFIER:
            curr = AST.VariableExpr(first.pos, first.text)
            while self.lexer.lookahead().text == ".":
                self.lexer.expect(text=".")
                field = self.lexer.expect(type=TokenType.IDENTIFIER)
                curr = AST.FieldExpr(first.pos, curr, field.text)

        if first.text == "(":
            curr = self.expression()

            self.lexer.expect(text=")")
        
        return curr
        
