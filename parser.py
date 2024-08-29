from lexer import Lexer, TokenType
import AST


class Parser:
    def __init__(self, filename) -> None:
        self.lexer = Lexer(filename)

    def parse(self):
        print(self.contract())
        
        token = self.lexer.next_token()
        while token.type != TokenType.EOF:
            print(token)
            token = self.lexer.next_token()

    def contract(self):
        self.lexer.expect(text="contract")
        
        name = self.lexer.expect(type=TokenType.IDENTIFIER)
        
        self.lexer.expect(text="{")


        fields = []
        while self.lexer.lookahead().text == "field":
            fields.append(self.field())
        
        methods = []

        while self.lexer.lookahead().text != "}":
            methods.append(self.method())
        
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
            self.lexer.expect(text=":=")
            expr = self.expression()
            self.lexer.expect(text="in")
            statements = self.statement()
            
            return AST.BindStmt(name.pos, name.text, expr, statements)
        
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

    def comparison(self):
        first = self.multiplication()
        while self.lexer.lookahead().text in ["==", "<", ">", "<=", ">="]:
            op = self.lexer.expect(type=TokenType.CONTROL)
            rhs = self.multiplication()
            first = AST.BinaryOp(op.pos, op.text, first, rhs)

    def multiplication(self):
        first = self.addition()
        while self.lexer.lookahead().text in ["*", "//"]:
            op = self.lexer.expect(type=TokenType.CONTROL)
            rhs = self.addition()
            first = AST.BinaryOp(op.pos, op.text, first, rhs)

    def addition(self):
        first = self.unary()
        while self.lexer.lookahead().text in ["+", "-"]:
            op = self.lexer.expect(type=TokenType.CONTROL)
            rhs = self.unary()
            first = AST.BinaryOp(op.pos, op.text, first, rhs)

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
        
