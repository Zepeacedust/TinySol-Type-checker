from TypeChecker import TypeChecker
from Environment import Environment

test = TypeChecker("programs/correctly_typed.txt")

test.type_check()



test.ast.evaluate(Environment({}))

print(test)