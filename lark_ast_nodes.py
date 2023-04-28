from abc import ABC, abstractmethod
from typing import Callable, Tuple, Optional, Union

from lark_base import SimpleType, BinOp, VarType
from semantic_base import TypeDesc, IdentDesc, SemanticException, IdentScope


class AstNode(ABC):
    init_action: Callable[['AstNode'], None] = None

    def __init__(self, row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__()
        self.row = row
        self.line = line
        for k, v in props.items():
            setattr(self, k, v)
        if AstNode.init_action is not None:
            AstNode.init_action(self)
        self.node_type: Optional[TypeDesc] = None
        self.node_ident: Optional[IdentDesc] = None

    @property
    def childs(self) -> Tuple['AstNode', ...]:
        return ()

    @abstractmethod
    def __str__(self) -> str:
        pass

    def to_str_full(self):
        r = ''
        if self.node_ident:
            r = str(self.node_ident)
        elif self.node_type:
            r = str(self.node_type)
        return str(self) + (' : ' + r if r else '')

    @property
    def tree(self) -> [str, ...]:
        res = [str(self)]
        childs_temp = self.childs
        for i, child in enumerate(childs_temp):
            ch0, ch = '├', '│'
            if i == len(childs_temp) - 1:
                ch0, ch = '└', ' '
            res.extend(((ch0 if j == 0 else ch) + ' ' + s for j, s in enumerate(child.tree)))
        return res

    def semantic_error(self, message: str):
        raise SemanticException(message, self.row, self.line)

    def semantic_check(self, checker, scope: IdentScope) -> None:
        checker.semantic_check(self, scope)

    def visit(self, func: Callable[['AstNode'], None]) -> None:
        func(self)
        map(func, self.childs)

    def __getitem__(self, index):
        return self.childs[index] if index < len(self.childs) else None


class ExprNode(AstNode):
    pass


class ExprListNode(ExprNode):
    def __init__(self, *exprs: ExprNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.exprs = exprs

    @property
    def childs(self) -> Tuple[ExprNode, ...]:
        return self.exprs

    def __str__(self) -> str:
        return '{}'


class LiteralNode(ExprNode):
    def __init__(self, literal: str,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.literal = literal
        self.value = eval(literal.replace('\'', '\"'))

    def __str__(self) -> str:
        return '{0} ({1})'.format(self.literal, type(self.value).__name__)


class IdentNode(ExprNode):
    def __init__(self, name: str,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.name = str(name)

    def __str__(self) -> str:
        return str(self.name)


class TypeDescNode(ExprNode):
    def __init__(self, type: SimpleType, complex_type: VarType = VarType.SIMPLE,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.type = type
        self.complex_type = complex_type

    def __str__(self) -> str:
        return str(self.type)


class SimpleTypeNode(TypeDescNode):
    pass


class ArrayTypeNode(TypeDescNode):
    def __init__(self, type: SimpleType,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(type, VarType.ARRAY, row=row, line=line, **props)

    def __str__(self) -> str:
        return '{0}[]'.format(str(self.type))


class ArrayDeclNode(ExprNode):
    def __init__(self, type: SimpleType,
                 size: ExprNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.type = type
        self.size = size

    @property
    def childs(self) -> Tuple[ExprNode, ...]:
        return self.size,

    def __str__(self) -> str:
        return '{0}[]'.format(str(self.type))


class TypeNode(ExprNode):
    def __init__(self, type_desc: TypeDescNode, row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.type_desc = type_desc

    def __str__(self) -> str:
        return str(self.type_desc)


class TypeListNode(ExprNode):
    def __init__(self, *types: TypeNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.types = types

    @property
    def childs(self) -> Tuple[TypeNode]:
        return self.types

    def __str__(self) -> str:
        return 'types'


class TypeConvertNode(ExprNode):
    """Класс для представления в AST-дереве операций конвертации типов данных
       (в языке программирования может быть как expression, так и statement)
    """

    def __init__(self, expr: ExprNode, type_: TypeDesc,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.expr = expr
        self.type = type_
        self.node_type = type_

    def __str__(self) -> str:
        return 'convert {0}'.format(str(self.type))

    @property
    def childs(self) -> ExprNode:
        return self.expr


class FuncParamNode(ExprNode):
    def __init__(self, type: TypeNode, ident: IdentNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.type = type
        self.ident = ident

    @property
    def childs(self) -> Tuple[TypeNode, IdentNode]:
        return self.type, self.ident

    def __str__(self) -> str:
        return 'func-param'


class FuncParamsNode(ExprNode):
    def __init__(self, params: Tuple[FuncParamNode] = (),
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.params = params

    @property
    def childs(self) -> Tuple[FuncParamNode]:
        return self.params

    def __str__(self) -> str:
        return 'params'


class BinOpNode(ExprNode):
    def __init__(self, op: BinOp, arg1: ExprNode, arg2: ExprNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

    @property
    def childs(self) -> Tuple[ExprNode, ExprNode]:
        return self.arg1, self.arg2

    def __str__(self) -> str:
        return str(self.op.value)


class StmtNode(ExprNode):
    pass


class VarsDeclNode(StmtNode):
    def __init__(self, type: TypeNode, *vars: Tuple[AstNode, ...],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.type = type
        self.vars = vars

    @property
    def childs(self) -> Tuple[ExprNode, ...]:
        return (self.type,) + self.vars

    def __str__(self) -> str:
        return 'var'


class VarsDeclListNode(StmtNode):
    def __init__(self, *vars_decl: VarsDeclNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.vars_decl = vars_decl

    @property
    def childs(self) -> Tuple[VarsDeclNode, ...]:
        return self.vars_decl

    def __str__(self) -> str:
        return 'vars_list'


class CallNode(StmtNode):
    def __init__(self, func: IdentNode, *params: Tuple[ExprNode],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.func = func
        self.params = params

    @property
    def childs(self) -> Tuple[IdentNode, ...]:
        # return self.func, (*self.params)
        return (self.func,) + self.params

    def __str__(self) -> str:
        return 'call'


class AssignNode(StmtNode):
    def __init__(self, var: IdentNode, val: ExprNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.var = var
        self.val = val

    @property
    def childs(self) -> Tuple[IdentNode, ExprNode]:
        return self.var, self.val

    def __str__(self) -> str:
        return '='


class ArrayElementNode(StmtNode):
    def __init__(self, var: IdentNode, index: ExprNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.var = var
        self.index = index

    @property
    def childs(self) -> Tuple[IdentNode, ExprNode]:
        return self.var, self.index

    def __str__(self) -> str:
        return 'array_elem'


class IfNode(StmtNode):
    def __init__(self, cond: ExprNode, then_stmt: StmtNode, else_stmt: Optional[StmtNode] = None,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode, Optional[StmtNode]]:
        return (self.cond, self.then_stmt) + ((self.else_stmt,) if self.else_stmt else tuple())

    def __str__(self) -> str:
        return 'if'


class ForNode(StmtNode):
    def __init__(self, init: Union[StmtNode, None], cond: Union[ExprNode, StmtNode, None],
                 step: Union[StmtNode, None], body: Union[StmtNode, None] = None,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.init = init if init else EMPTY_STMT
        self.cond = cond if cond else EMPTY_STMT
        self.step = step if step else EMPTY_STMT
        self.body = body if body else EMPTY_STMT

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return self.init, self.cond, self.step, self.body

    def __str__(self) -> str:
        return 'for'


class WhileNode(StmtNode):
    def __init__(self, cond: ExprNode, body: StmtNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.cond = cond
        self.stmt = body if body else EMPTY_STMT

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode]:
        return self.cond, self.stmt

    def __str__(self) -> str:
        return 'while'


class ReturnNode(StmtNode):
    def __init__(self, expr: ExprNode, row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.expr = expr

    def __str__(self) -> str:
        return 'return {0}'.format(str(self.expr))


class StmtListNode(StmtNode):
    def __init__(self, *stmts: StmtNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.stmts = stmts
        self.program = False

    @property
    def childs(self) -> Tuple[StmtNode, ...]:
        return self.stmts

    def __str__(self) -> str:
        return '...'


class FuncNode(StmtNode):
    def __init__(self, return_type: TypeNode, name: IdentNode,
                 params: FuncParamsNode, body: StmtListNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body

    @property
    def childs(self) -> Tuple[ExprNode, ...]:
        return ((self.params,) if self.params else tuple()) + (self.body,)

    def __str__(self) -> str:
        return '({0}) func {1}'.format(self.return_type, self.name)


class DelegateNode(TypeDescNode):
    def __init__(self, type_list: TypeListNode, return_type: TypeNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(None, VarType.DELEGATE, row=row, line=line, **props)
        self.type_list = type_list
        self.return_type = return_type

    @property
    def childs(self) -> Tuple[TypeListNode, TypeNode]:
        return self.type_list, self.return_type

    def __str__(self) -> str:
        return 'delegate'


EMPTY_STMT = StmtListNode()
EMPTY_IDENT = IdentDesc('', TypeDesc.VOID)
