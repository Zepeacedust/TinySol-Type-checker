
from lexer import Lexer
from parser import Parser
from TypeChecker import TypeChecker
from Environment import Environment

import sys

def main():
    assert len(sys.argv) == 2, "Usage is python main.py [FILENAME]"


    lexer = Lexer(sys.argv[1])

    parser = Parser(lexer)

    ast = parser.parse()

    type_checker = TypeChecker()

    type_checker.type_check(ast)

    ast.evaluate(Environment({}))


if __name__ == "__main__":
    main()
