from parser import Parser

import Typing

class TypeChecker:
    def __init__(self, filename) -> None:
        self.parser = Parser(filename)
        self.ast = None

    def type_check(self):
        self.ast = self.parser.parse()
        
        interfaces = {
            "int":Typing.Int(), 
            "bool":Typing.Bool(), 
            "obj":Typing.Interface(
                "obj",
                [
                    Typing.Field("balance", Typing.Type(Typing.Int(), Typing.SecurityLevel(0,max=True)))
                ],
                [
                    Typing.Method("send", {}, Typing.ProcType({}, Typing.CmdType(Typing.SecurityLevel(0,min=True))))
                ]
            )
        }

        for interface in self.ast.interfaces:
            interfaces[interface.name] = interface


        type_environment = Typing.TypeEnvironment({}, interfaces)

        for interface in self.ast.interfaces:
            interface.type_check(type_environment)

        self.ast.type_check(type_environment)

        for contract in self.ast.contracts:
            type_environment.push({"this":contract.type_assignment})

            for method in contract.methods:
                method.type_check(type_environment)

            type_environment.pop()

        for transaction in self.ast.transactions:
            transaction.type_check(type_environment)