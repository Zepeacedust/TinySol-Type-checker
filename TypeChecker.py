from parser import Parser

class TypeChecker:
    def __init__(self, filename) -> None:
        self.parser = Parser(filename)

    def type_check(self):
        ast = self.parser.parse()
        
        ast.type_check()