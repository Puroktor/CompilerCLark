import os
import lark_parser
import semantic_checker
from semantic_base import SemanticException


def main():
    with open("./tests/test1.jc", "r") as f:
        prog = f.read()

    prog = lark_parser.parse(prog)
    print('AST дерево')
    print(*prog.tree, sep=os.linesep)

    try:
        print('После семантической проверки')
        checker = semantic_checker.SemanticChecker()
        scope = semantic_checker.prepare_global_scope()
        prog.program = True
        checker.semantic_check(prog, scope)
        print(*prog.tree, sep=os.linesep)
    except SemanticException as e:
        print('Синтаксическая ошибка: {}'.format(e.message))


if __name__ == "__main__":
    main()
