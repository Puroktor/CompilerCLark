from lark import Lark, InlineTransformer
from lark.lexer import Token
from mel_ast import *

parser = Lark('''
    %import common.NUMBER
    %import common.ESCAPED_STRING
    %import common.CNAME
    %import common.NEWLINE
    %import common.WS

    %ignore WS

    COMMENT: "/*" /(.|\\n|\\r)+/ "*/"
        |  "//" /(.)+/ NEWLINE
    %ignore COMMENT
    
    INT:        "int"
    CHAR:       "char"
    STRING:     "string"
    BOOLEAN:    "boolean"
    DOUBLE:     "double"
    VOID:       "void"

    num: NUMBER  -> literal
    str: ESCAPED_STRING  -> literal
    type: INT | CHAR | STRING | BOOLEAN | DOUBLE
    ident: CNAME

    ADD:     "+"
    SUB:     "-"
    MUL:     "*"
    DIV:     "/"
    MOD:     "%"
    AND:     "&&"
    OR:      "||"
    BIT_AND: "&"
    BIT_OR:  "|"
    GE:      ">="
    LE:      "<="
    NEQUALS: "!="
    EQUALS:  "=="
    GT:      ">"
    LT:      "<"

    call: ident "(" ( expr ( "," expr )* )? ")"
    
    type_list: (type ("," type)*)?
    ?delegate: "delegate" "<" type_list ":" func_return_type ">"
    
    ?group: num | str
        | ident
        | call
        | "(" expr ")"

    ?mult: group
        | mult ( MUL | DIV |  MOD) group  -> bin_op

    ?add: mult
        | add ( ADD | SUB ) mult  -> bin_op

    ?compare1: add
        | add ( GT | LT | GE | LE ) add  -> bin_op

    ?compare2: compare1
        | compare1 ( EQUALS | NEQUALS ) compare1  -> bin_op

    ?logical_and: compare2
        | logical_and AND compare2  -> bin_op

    ?logical_or: logical_and
        | logical_or OR logical_and  -> bin_op

    ?expr: logical_or
    
    ?expr_list: "{" expr ( "," expr )* "}"

    ?var_decl_inner: ident | ident "=" expr  -> assign
        
    ?var_array_decl_inner: ident | ident "=" expr_list  -> assign
    
    ?var_delegate_decl_inner: ident | ident "=" ident  -> assign
    
    ?vars_decl: type var_decl_inner ( "," var_decl_inner )* 
        | type "[]" var_array_decl_inner ( "," var_array_decl_inner )*
        | delegate var_delegate_decl_inner ( "," var_delegate_decl_inner )*

    ?simple_stmt: ident "=" expr  -> assign
        | call

    ?for_stmt_list: vars_decl
        | ( simple_stmt ( "," simple_stmt )* )?  -> stmt_list
    ?for_cond: expr
        |   -> stmt_list
    ?for_body: stmt
        | ";"  -> stmt_list
    
    ?stmt: vars_decl ";"
        | simple_stmt ";"
        | "if" "(" expr ")" stmt ("else" stmt)?  -> if
        | "for" "(" for_stmt_list ";" for_cond ";" for_stmt_list ")" for_body  -> for
        | "while" "(" expr ")" stmt -> while
        | "do" stmt "while" "(" expr ")" -> do_while
        | "{" stmt_list "}"

    stmt_list: ( stmt ";"* )*
    
    ?var_sign: type ident
    ?var_sign_list: (var_sign ("," var_sign)*)?
    
    func_return_type: INT | CHAR | STRING | BOOLEAN | DOUBLE | VOID    
    func: func_return_type ident "(" var_sign_list ")" "{" stmt_list "}"
    
    func_list: func*
    
    ?prog: func_list

    ?start: prog
''', start='start')  # , parser='lalr')


class MelASTBuilder(InlineTransformer):
    def __getattr__(self, item):
        if isinstance(item, str) and item.upper() == item:
            return lambda x: x

        if item in ('bin_op',):
            def get_bin_op_node(*args):
                op = BinOp(args[1].value)
                return BinOpNode(op, args[0], args[2],
                                 **{'token': args[1], 'line': args[1].line, 'column': args[1].column})

            return get_bin_op_node
        else:
            def get_node(*args):
                props = {}
                if len(args) == 1 and isinstance(args[0], Token):
                    props['token'] = args[0]
                    props['line'] = args[0].line
                    props['column'] = args[0].column
                    args = [args[0].value]
                cls = eval(''.join(x.capitalize() for x in item.split('_')) + 'Node')
                return cls(*args, **props)

            return get_node


def parse(prog: str) -> StmtListNode:
    prog = parser.parse(str(prog))
    # print(prog.pretty('  '))
    prog = MelASTBuilder().transform(prog)
    return prog
