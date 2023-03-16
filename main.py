import os
import mel_parser


def main():
    prog = '''
        void myFunc(int a, boolean b) {
            int[] i = {1, 2 % 3};
            while (1 > 2)
            {
                int a = 5;
            }
            do
            {
                print(a);
            } while (i > 3);
        }
        int test() 
        {
            Write(i+3);
            delegate<int, boolean: void> myDelegate = myFunc;
            Execute(myDelegate);
        }
    '''
    prog = mel_parser.parse(prog)
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
