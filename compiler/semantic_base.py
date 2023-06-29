from typing import Any, Dict, Optional, Tuple
from enum import Enum

from lark_base import BaseType, BinOp

VOID, INT, DOUBLE, BOOLEAN, CHAR = BaseType.VOID, BaseType.INT, BaseType.DOUBLE, BaseType.BOOLEAN, BaseType.CHAR


class TypeDesc:
    """Класс для описания типа данных.
    """

    VOID: 'TypeDesc'
    INT: 'TypeDesc'
    DOUBLE: 'TypeDesc'
    BOOLEAN: 'TypeDesc'
    CHAR: 'TypeDesc'

    INT_ARRAY: 'TypeDesc'
    DOUBLE_ARRAY: 'TypeDesc'
    BOOLEAN_ARRAY: 'TypeDesc'
    CHAR_ARRAY: 'TypeDesc'

    def __init__(self, base_type_: Optional[BaseType] = None,
                 return_type: Optional['TypeDesc'] = None, params: Optional[Tuple['TypeDesc']] = None,
                 array: bool = False) -> None:
        self.base_type = base_type_
        self.return_type = return_type
        self.params = params
        self.array = array

    @property
    def func(self) -> bool:
        return self.return_type is not None

    @property
    def is_arr(self) -> bool:
        return self.array

    @property
    def is_simple(self) -> bool:
        return not self.func and not self.array

    def __eq__(self, other: 'TypeDesc'):
        if self.func != other.func:
            return False
        if not self.func:
            return self.array == other.array and self.base_type == other.base_type
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
    def from_base_type(base_type_: BaseType) -> 'TypeDesc':
        return getattr(TypeDesc, base_type_.name)

    @staticmethod
    def from_array_base_type(arr_type: BaseType) -> 'TypeDesc':
        return getattr(TypeDesc, f"{arr_type.name}_ARRAY")

    @staticmethod
    def from_str(str_decl: str, array: bool = False) -> 'TypeDesc':
        try:
            base_type_ = BaseType(str_decl)
            if array:
                return TypeDesc.from_array_base_type(base_type_)
            else:
                return TypeDesc.from_base_type(base_type_)
        except:
            raise SemanticException('Неизвестный тип {}'.format(str_decl))

    def __str__(self) -> str:
        if not self.func:
            return str(self.base_type) + ('[]' if self.is_arr else '')
        else:
            res = str(self.return_type)
            res += ' ('
            for param in self.params:
                if res[-1] != '(':
                    res += ', '
                res += str(param)
            res += ')'
        return res


for base_type in BaseType:
    setattr(TypeDesc, base_type.name, TypeDesc(base_type))
    tmp = TypeDesc(base_type)
    tmp.array = True
    setattr(TypeDesc, f"{base_type.name}_ARRAY", tmp)


class ScopeType(Enum):
    """Перечисление для "области" декларации переменных
    """

    GLOBAL = 'global'
    GLOBAL_LOCAL = 'global.local'  # переменные относятся к глобальной области, но описаны в скобках (теряем имена)
    PARAM = 'param'
    LOCAL = 'local'

    def __str__(self):
        return self.value


class IdentDesc:

    def __init__(self, name: str, type_: TypeDesc, scope: ScopeType = ScopeType.GLOBAL, index: int = 0) -> None:
        self.name = name
        self.type = type_
        self.scope = scope
        self.index = index
        self.built_in = False

    def element_desc(self):
        name = str(self.type.base_type).replace("array ", "")
        tp = self.type.from_str(name)
        return IdentDesc(self.name, tp, self.scope, self.index)

    def __str__(self) -> str:
        return '{}, {}, {}'.format(self.type, self.scope, 'built-in' if self.built_in else self.index)


class ArrayDesc(IdentDesc):

    def __init__(self, name: str, type_: TypeDesc, size: int, scope: ScopeType = ScopeType.GLOBAL,
                 index: int = 0) -> None:
        super().__init__(name, type_, scope, index)
        self.size = size

    def __str__(self) -> str:
        return f'{self.type}[{self.size}], {self.scope}, {"built-in" if self.built_in else self.index}'


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
            ident.scope = ScopeType.LOCAL if func_scope else \
                ScopeType.GLOBAL if self == global_scope else ScopeType.GLOBAL_LOCAL

        old_ident = self.get_ident(ident.name)
        if old_ident:
            error = False
            if ident.scope == ScopeType.PARAM:
                if old_ident.scope == ScopeType.PARAM:
                    error = True
            elif ident.scope == ScopeType.LOCAL:
                if old_ident.scope not in (ScopeType.GLOBAL, ScopeType.GLOBAL_LOCAL):
                    error = True
            else:
                error = True
            if error:
                raise SemanticException('Идентификатор {} уже объявлен'.format(ident.name))

        if not ident.type.func:
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
        self.message = message
        if row or col:
            self.message += " ("
            if row:
                self.message += f'строка: {format(row)}'
                if col:
                    self.message += ', '
            if row:
                self.message += f'позиция: {format(col)}'
            self.message += ")"


TYPE_CONVERTIBILITY = {
    BOOLEAN: (INT, CHAR, DOUBLE),
    CHAR: (INT, BOOLEAN, DOUBLE),
    INT: (DOUBLE, BOOLEAN, CHAR),
    DOUBLE: (BOOLEAN, INT, CHAR),
}

BIN_OP_TYPE_COMPATIBILITY = {
    BinOp.ADD: {
        (INT, INT): INT,
        (DOUBLE, DOUBLE): DOUBLE,
        (CHAR, CHAR): CHAR
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
        (INT, INT): BOOLEAN,
        (DOUBLE, DOUBLE): BOOLEAN,
        (CHAR, CHAR): BOOLEAN,
    },
    BinOp.LT: {
        (INT, INT): BOOLEAN,
        (DOUBLE, DOUBLE): BOOLEAN,
        (CHAR, CHAR): BOOLEAN,
    },
    BinOp.GE: {
        (INT, INT): BOOLEAN,
        (DOUBLE, DOUBLE): BOOLEAN,
        (CHAR, CHAR): BOOLEAN,
    },
    BinOp.LE: {
        (INT, INT): BOOLEAN,
        (DOUBLE, DOUBLE): BOOLEAN,
        (CHAR, CHAR): BOOLEAN,
    },
    BinOp.EQUALS: {
        (INT, INT): BOOLEAN,
        (DOUBLE, DOUBLE): BOOLEAN,
        (CHAR, CHAR): BOOLEAN,
    },
    BinOp.NEQUALS: {
        (INT, INT): BOOLEAN,
        (DOUBLE, DOUBLE): BOOLEAN,
        (CHAR, CHAR): BOOLEAN,
    },

    BinOp.LOGICAL_AND: {
        (BOOLEAN, BOOLEAN): BOOLEAN
    },
    BinOp.LOGICAL_OR: {
        (BOOLEAN, BOOLEAN): BOOLEAN
    },
}

BUILT_IN_FUNCTIONS = '''
    void print_int(int var){}
    void print_double(double var){}
    void print_char(char var){}
    int read_int(){}
    double read_double(){}
    char read_char(){}
    void print_str(char str[]) {}
    void _main() {}
'''
