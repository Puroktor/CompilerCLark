from enum import Enum


class SimpleType(Enum):
    INT = 'int'
    STRING = 'string'
    BOOLEAN = 'boolean'
    DOUBLE = 'double'
    VOID = 'void'


class BinOp(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    MOD = '%'
    GE = '>='
    LE = '<='
    NEQUALS = '<>'
    EQUALS = '=='
    GT = '>'
    LT = '<'
    BIT_AND = '&'
    BIT_OR = '|'
    LOGICAL_AND = '&&'
    LOGICAL_OR = '||'


class VarType(Enum):
    SIMPLE = 0,
    ARRAY = 1,
    FUNCTION = 2,
    DELEGATE = 3
