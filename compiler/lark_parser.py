import os

from lark import Lark, InlineTransformer
from lark.lexer import Token
from lark_ast_nodes import *
from lark_base import BinOp

absolute_path = os.path.dirname(__file__)
parser = Lark.open(os.path.join(absolute_path, "syntax.lark"), start='start', lexer='standard', propagate_positions=True)


class ASTBuilder(InlineTransformer):
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
                if len(args) != 0:
                    props = {'line': args[0].line, 'column': args[0].column}
                if len(args) == 1 and isinstance(args[0], Token):
                    props['token'] = args[0]
                    args = [args[0].value]
                cls = eval(''.join(x.capitalize() for x in item.split('_')) + 'Node')
                return cls(*args, **props)

            return get_node


def parse(prog: str) -> StmtListNode:
    prog = parser.parse(str(prog))
    prog = ASTBuilder().transform(prog)
    return prog
