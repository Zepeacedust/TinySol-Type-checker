from parser import Parser

import Typing

class TypeChecker:
    def __init__(self, filename) -> None:
        self.parser = Parser(filename)

    def type_check(self):
        ast = self.parser.parse()
        
        globals = {}

        for interface in ast.interfaces:
            globals[interface.name] = interface
            print(interface.name)

        for contract in ast.contracts:
            globals[contract.name] = contract

        print(globals)

        type_environment = Typing.TypeEnvironment(globals)

        ast.type_check(type_environment)