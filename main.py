
from lexer import Lexer
from parser import Parser
from TypeChecker import TypeChecker
from Environment import Environment

import sys

def parse_command_line():
    run = True
    type_check = True
    filename = None
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--no-check":
            type_check = False
        elif sys.argv[i] == "--no-run":
            run = False
        else:
            if filename == None:
                filename = sys.argv[i]
            else:
                print(f"Invalid argument {sys.argv[i]}, duplicate file name?")
                print("Usage is main.py filename [options]")
                exit()
        i += 1
    if filename == None:
        print("Usage is main.py filename [options]")
        exit()
    return (filename, type_check, run)

def main():

    
    filename, type_check, run = parse_command_line()

    lexer = Lexer(sys.argv[1])

    parser = Parser(lexer)

    ast = parser.parse()

    if type_check:
        type_checker = TypeChecker()

        type_checker.type_check(ast)
        print("Type checking complete")

    if run:
        ast.evaluate(Environment({}))


if __name__ == "__main__":
    main()
