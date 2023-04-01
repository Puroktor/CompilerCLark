import os
import mel_parser


def main():
    with open("tests/test2.jc", "r") as f:
        prog = f.read()
        prog = mel_parser.parse(prog)
        print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
