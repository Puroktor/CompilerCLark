import os
import sys

import lark_parser
import semantic_checker
from semantic_base import SemanticException

OK_TEST_DIR = './tests/ok'
FAIL_TEST_DIR = './tests/fail'


def compile(src, print_trees):
    with open(src, 'r') as f:
        prog = f.read()

    prog = lark_parser.parse(prog)
    if print_trees:
        print('AST дерево')
        print(*prog.tree, sep=os.linesep)

    try:
        checker = semantic_checker.SemanticChecker()
        scope = semantic_checker.prepare_global_scope()
        prog.program = True
        checker.semantic_check(prog, scope)
        semantic_checker.check_program_struct(scope)
        if print_trees:
            print('После семантической проверки')
            print(*prog.tree, sep=os.linesep)

    except SemanticException as e:
        print('Синтаксическая ошибка: {}'.format(e.message), file=sys.stderr)


def test_compiler():
    checker = semantic_checker.SemanticChecker()
    passed_all = True
    for filename in os.listdir(OK_TEST_DIR):
        with open(os.path.join(OK_TEST_DIR, filename), 'r') as f:
            try:
                exec_parsing(checker, f)
            except:
                print('OK тест провален для {0}'.format(filename), file=sys.stderr)
                passed_all = False
    for filename in os.listdir(FAIL_TEST_DIR):
        with open(os.path.join(FAIL_TEST_DIR, filename), 'r') as f:
            try:
                exec_parsing(checker, f)
                print('Fail тест провален для {0}'.format(filename), file=sys.stderr)
                passed_all = False
            except:
                pass

    if passed_all:
        print('Все тесты успешно пройдены')


def exec_parsing(checker, file):
    prog = file.read()
    prog = lark_parser.parse(prog)
    prog.program = True
    scope = semantic_checker.prepare_global_scope()
    checker.semantic_check(prog, scope)
    semantic_checker.check_program_struct(scope)
