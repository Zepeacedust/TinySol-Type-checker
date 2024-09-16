from parser import Parser

import Typing

class TypeChecker:
    def __init__(self, filename) -> None:
        self.parser = Parser(filename)

    def type_check(self):
        ast = self.parser.parse()
        
        globals = {"int":Typing.Int(), "bool":Typing.Bool()}

        for interface in ast.interfaces:
            globals[interface.name] = interface

        print(globals)

        type_environment = Typing.TypeEnvironment(globals)

        for interface in ast.interfaces:
            interface.type_check(type_environment)

        ast.type_check(type_environment)

        for contract in ast.contracts:
            type_environment.push({"this":contract.type_assignment})

            for method in contract.methods:
                method.type_check(type_environment)

            type_environment.pop()