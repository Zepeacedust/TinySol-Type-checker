from TypeChecker import TypeChecker
from Environment import Environment

import sys

assert len(sys.argv) == 2, "Usage is python main.py [FILENAME]"

test = TypeChecker(sys.argv[1])

test.type_check()



test.ast.evaluate(Environment({}))

print(test)