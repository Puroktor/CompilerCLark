from typing import Any, Dict, Optional, Tuple
from enum import Enum

from lark_base import SimpleType, BinOp, VarType

VOID, INT, DOUBLE, BOOL, STR = SimpleType.VOID, SimpleType.INT, SimpleType.DOUBLE, SimpleType.BOOLEAN, SimpleType.STRING


class TypeDesc:
    """Класс для описания типа данных.
    """

    VOID: 'TypeDesc'
    INT: 'TypeDesc'
    DOUBLE: 'TypeDesc'
    BOOL: 'TypeDesc'
    STR: 'TypeDesc'

    def __init__(self, simple_type_: Optional[SimpleType] = None, var_type: VarType = VarType.SIMPLE,
                 return_type: Optional['TypeDesc'] = None, params: Optional[Tuple['TypeDesc']] = None) -> None:
        # Примитивный тип данных
        self.simple_type = simple_type_

        self.var_type = var_type

        # Для функции или делегата
        self.return_type = return_type
        self.params = params

    def __eq__(self, other: 'TypeDesc'):
        if self.var_type != other.var_type:
            return False
        if not self.var_type:
            return self.simple_type == other.simple_type
        else:
            if self.return_type != other.return_type:
                return False
            if len(self.params) != len(other.params):
                return False
            for i in range(len(self.params)):
                if self.params[i] != other.params[i]:
                    return False
            return True

    @staticmethod
    def from_simple_type(simple_type_: SimpleType) -> 'TypeDesc':
        return getattr(TypeDesc, simple_type_.name)

    @property
    def is_simple(self) -> bool:
        return self.var_type == VarType.SIMPLE

    @property
    def func(self) -> bool:
        return self.var_type == VarType.FUNCTION

    def __str__(self) -> str:
        if not self.var_type:
            return str(self.simple_type)
        elif self.var_type == VarType.ARRAY:
            return '{0}[]'.format(str(self.simple_type))
        else:
            res = str(self.return_type)
            res += ' ('
            for param in self.params:
                if res[-1] != '(':
                    res += ', '
                res += str(param)
            res += ')'
        return res


for simple_type in SimpleType:
    setattr(TypeDesc, simple_type.name, TypeDesc(simple_type))


class ScopeType(Enum):
    """Перечисление для "области" декларации переменных
    """

    GLOBAL = 'global'
    PARAM = 'param'
    LOCAL = 'local'

    def __str__(self):
        return self.value


class IdentDesc:
    """Класс для описания переменых
    """

    def __init__(self, name: str, type_: TypeDesc, scope: ScopeType = ScopeType.GLOBAL, index: int = 0) -> None:
        self.name = name
        self.type = type_
        self.scope = scope
        self.index = index
        self.built_in = False

    def __str__(self) -> str:
        return '{}, {}, {}'.format(self.type, self.scope, 'built-in' if self.built_in else self.index)


class IdentScope:
    """Класс для представлений областей видимости переменных во время семантического анализа
    """

    def __init__(self, parent: Optional['IdentScope'] = None) -> None:
        self.idents: Dict[str, IdentDesc] = {}
        self.func: Optional[IdentDesc] = None
        self.parent = parent
        self.var_index = 0
        self.param_index = 0

    @property
    def is_global(self) -> bool:
        return self.parent is None

    @property
    def curr_global(self) -> 'IdentScope':
        curr = self
        while curr.parent:
            curr = curr.parent
        return curr

    @property
    def curr_func(self) -> Optional['IdentScope']:
        curr = self
        while curr and not curr.func:
            curr = curr.parent
        return curr

    def add_ident(self, ident: IdentDesc) -> IdentDesc:
        func_scope = self.curr_func
        global_scope = self.curr_global

        if ident.scope != ScopeType.PARAM:
            ident.scope = ScopeType.LOCAL if func_scope else ScopeType.GLOBAL

        old_ident = self.get_ident(ident.name)
        if old_ident:
            error = False
            if ident.scope == ScopeType.PARAM:
                if old_ident.scope == ScopeType.PARAM:
                    error = True
            elif ident.scope == ScopeType.LOCAL:
                if old_ident.scope != ScopeType.GLOBAL:
                    error = True
            else:
                error = True
            if error:
                raise SemanticException('Идентификатор {} уже объявлен'.format(ident.name))

        if not ident.type.var_type == VarType.FUNCTION:
            if ident.scope == ScopeType.PARAM:
                ident.index = func_scope.param_index
                func_scope.param_index += 1
            else:
                ident_scope = func_scope if func_scope else global_scope
                ident.index = ident_scope.var_index
                ident_scope.var_index += 1

        self.idents[ident.name] = ident
        return ident

    def get_ident(self, name: str) -> Optional[IdentDesc]:
        scope = self
        ident = None
        while scope:
            ident = scope.idents.get(name)
            if ident:
                break
            scope = scope.parent
        return ident


class SemanticException(Exception):
    """Класс для исключений во время семантического анализа
    """

    def __init__(self, message, row: int = None, col: int = None, **kwargs: Any) -> None:
        if row or col:
            message += " ("
            if row:
                message += 'строка: {}'.format(row)
                if col:
                    message += ', '
            if row:
                message += 'позиция: {}'.format(col)
            message += ")"
        self.message = message


def can_type_convert_to(from_type: TypeDesc, to_type: TypeDesc) -> bool:
    if from_type.var_type or to_type.var_type:
        if from_type.var_type == VarType.ARRAY and to_type.var_type == VarType.ARRAY:
            return True
        else:
            return False
    return from_type.simple_type in TYPE_CONVERTIBILITY and to_type.simple_type in TYPE_CONVERTIBILITY[to_type.simple_type]


TYPE_CONVERTIBILITY = {
    INT: (DOUBLE, BOOL, STR),
    DOUBLE: (STR,),
    BOOL: (STR,)
}

BIN_OP_TYPE_COMPATIBILITY = {
    BinOp.ADD: {
        (INT, INT): INT,
        (DOUBLE, DOUBLE): DOUBLE,
        (STR, STR): STR
    },
    BinOp.SUB: {
        (INT, INT): INT,
        (DOUBLE, DOUBLE): DOUBLE
    },
    BinOp.MUL: {
        (INT, INT): INT,
        (DOUBLE, DOUBLE): DOUBLE
    },
    BinOp.DIV: {
        (INT, INT): INT,
        (DOUBLE, DOUBLE): DOUBLE
    },
    BinOp.MOD: {
        (INT, INT): INT,
        (DOUBLE, DOUBLE): DOUBLE
    },

    BinOp.GT: {
        (INT, INT): BOOL,
        (DOUBLE, DOUBLE): BOOL,
        (STR, STR): BOOL,
    },
    BinOp.LT: {
        (INT, INT): BOOL,
        (DOUBLE, DOUBLE): BOOL,
        (STR, STR): BOOL,
    },
    BinOp.GE: {
        (INT, INT): BOOL,
        (DOUBLE, DOUBLE): BOOL,
        (STR, STR): BOOL,
    },
    BinOp.LE: {
        (INT, INT): BOOL,
        (DOUBLE, DOUBLE): BOOL,
        (STR, STR): BOOL,
    },
    BinOp.EQUALS: {
        (INT, INT): BOOL,
        (DOUBLE, DOUBLE): BOOL,
        (STR, STR): BOOL,
    },
    BinOp.NEQUALS: {
        (INT, INT): BOOL,
        (DOUBLE, DOUBLE): BOOL,
        (STR, STR): BOOL,
    },

    BinOp.BIT_AND: {
        (INT, INT): INT
    },
    BinOp.BIT_OR: {
        (INT, INT): INT
    },

    BinOp.LOGICAL_AND: {
        (BOOL, BOOL): BOOL
    },
    BinOp.LOGICAL_OR: {
        (BOOL, BOOL): BOOL
    },
}
