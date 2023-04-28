from enum import Enum


class VarType(Enum):
    INT = 'int'
    CHAR = 'char'
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
