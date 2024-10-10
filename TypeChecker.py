from parser import Parser

import Typing

class TypeChecker:
    def __init__(self) -> None:
        # add more functionality or remove class
        pass

    def type_check(self, ast):
        
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

        for interface in ast.interfaces:
            interfaces[interface.name] = interface


        type_environment = Typing.TypeEnvironment({}, interfaces)

        for interface in ast.interfaces:
            interface.type_check(type_environment)

        ast.type_check(type_environment)

        for contract in ast.contracts:
            type_environment.push({"this":contract.type_assignment})

            for method in contract.methods:
                method.type_check(type_environment)

            type_environment.pop()

        for transaction in ast.transactions:
            transaction.type_check(type_environment)