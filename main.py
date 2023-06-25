import argparse
import os

import compiler


def main():
    cmd = argparse.ArgumentParser()
    cmd.add_argument('src', nargs='?', type=str, help='Source code file')
    cmd.add_argument('--unit-tests', default=False, action='store_true', help='Test compiler')
    cmd.add_argument('--print-trees', default=False, action='store_true', help='Print AST and Sematic trees')
    args = cmd.parse_args()

    if args.unit_tests:
        compiler.test_compiler()
    else:
        absolute_path = os.path.dirname(__file__)
        src = os.path.join(absolute_path, args.src)
        compiler.compile(src, args.print_trees)


if __name__ == "__main__":
    main()
