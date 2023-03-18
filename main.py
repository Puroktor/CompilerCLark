import os
import mel_parser


def main():
    prog = '''
        int i = 0;
        int b = 0;
        void myFunc(int[] a, boolean b) {
            do 
            {
            } while(i > 0 && g);
        }
        
        int i= 1+1;
         
        delegate<:void> test() 
        {
            delegate<int[], boolean : void> delegate = func();
        }
    '''
    prog = mel_parser.parse(prog)
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
