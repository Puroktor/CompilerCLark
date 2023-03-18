import os
import mel_parser


def main():
    prog = '''
        void myFunc(int a, boolean b) {
            int i = 2.3;
        
        }
        int test() 
        {
        }
    '''
    prog = mel_parser.parse(prog)
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
