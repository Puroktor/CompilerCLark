import os
import lark_parser


def main():
    with open("./tests/test1.jc", "r") as f:
        prog = f.read()
        prog = lark_parser.parse(prog)
        print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
