import argparse
import os
import sys

import lark_parser
import semantic_checker
from semantic_base import SemanticException

OK_TEST_DIR = 'tests/ok'
FAIL_TEST_DIR = 'tests/fail'


def print_trees(src):
    absolute_path = os.path.dirname(__file__)
    with open(os.path.join(absolute_path, src), 'r') as f:
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
        semantic_checker.check_program_struct(scope)
        print(*prog.tree, sep=os.linesep)
    except SemanticException as e:
        print('Синтаксическая ошибка: {}'.format(e.message), file=sys.stderr)


def test_compiler():
    checker = semantic_checker.SemanticChecker()
    for filename in os.listdir(OK_TEST_DIR):
        with open(os.path.join(OK_TEST_DIR, filename), 'r') as f:
            try:
                exec_parsing(checker, f)
            except:
                print('OK тест провален для {0}'.format(filename), file=sys.stderr)
    for filename in os.listdir(FAIL_TEST_DIR):
        with open(os.path.join(FAIL_TEST_DIR, filename), 'r') as f:
            try:
                exec_parsing(checker, f)
                print('Fail тест провален для {0}'.format(filename), file=sys.stderr)
            except:
                pass


def exec_parsing(checker, file):
    prog = file.read()
    prog = lark_parser.parse(prog)
    prog.program = True
    scope = semantic_checker.prepare_global_scope()
    checker.semantic_check(prog, scope)
    semantic_checker.check_program_struct(scope)


def main():
    cmd = argparse.ArgumentParser()
    cmd.add_argument('src', nargs='?', type=str, help='Source code file')
    cmd.add_argument('--unit-tests', default=False, action='store_true', help='Test compiler')
    args = cmd.parse_args()

    if args.unit_tests:
        test_compiler()
    else:
        print_trees(args.src)


if __name__ == "__main__":
    main()
