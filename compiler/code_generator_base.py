from typing import List, Dict

from lark_base import BaseType, BinOp

TEMP_VAR_NAME = 'temp'
STR_CONST_NAME = '_str'

LLVM_TYPE_NAMES = {
    BaseType.VOID: 'void',
    BaseType.BOOLEAN: 'i1',
    BaseType.CHAR: 'i8',
    BaseType.INT: 'i32',
    BaseType.DOUBLE: 'double',
}

LLVM_TYPE_DEFAULT_VALUES = {
    BaseType.BOOLEAN: '0',
    BaseType.CHAR: '0',
    BaseType.INT: '0',
    BaseType.DOUBLE: '0.0',
}

LLVM_INT_BIN_OPS = {
    BinOp.ADD: 'add',
    BinOp.SUB: 'sub',
    BinOp.MUL: 'mul',
    BinOp.DIV: 'sdiv',
    BinOp.MOD: 'srem',
    BinOp.GE: 'icmp sge',
    BinOp.LE: 'icmp sle',
    BinOp.NEQUALS: 'icmp ne',
    BinOp.EQUALS: 'icmp eq',
    BinOp.GT: 'icmp sgt',
    BinOp.LT: 'icmp slt',
    BinOp.LOGICAL_AND: 'and',
    BinOp.LOGICAL_OR: 'or'
}

LLVM_FLOAT_BIN_OPS = {
    BinOp.ADD: 'fadd',
    BinOp.SUB: 'fsub',
    BinOp.MUL: 'fmul',
    BinOp.DIV: 'fdiv',
    BinOp.MOD: 'frem',
    BinOp.GE: 'fcmp oge',
    BinOp.LE: 'fcmp ole',
    BinOp.NEQUALS: 'fcmp one',
    BinOp.EQUALS: 'fcmp oeq',
    BinOp.GT: 'fcmp ogt',
    BinOp.LT: 'fcmp olt',
    BinOp.LOGICAL_AND: 'and',
    BinOp.LOGICAL_OR: 'or'
}

BUILT_IN_FUNCTIONS = [
    "declare i32 @read_int()",
    "declare double @read_double()",
    "declare i8 @read_char()",
    "declare void @print_int(i32)",
    "declare void @print_double(double)",
    "declare void @print_char(i8)",
    "declare void @print_str(i8*)"
]


def get_llvm_conv_operation(arg_from: BaseType, arg_to: BaseType) -> str:
    if ((arg_from == BaseType.BOOLEAN or arg_from == BaseType.CHAR) and (arg_to == BaseType.INT)) \
            or (arg_from == BaseType.BOOLEAN and arg_to == BaseType.CHAR):
        return "zext"

    if (arg_from == BaseType.INT and (arg_to == BaseType.BOOLEAN or arg_to == BaseType.CHAR)) \
            or (arg_from == BaseType.CHAR and arg_to == BaseType.BOOLEAN):
        return "trunc"

    if arg_from == BaseType.DOUBLE and (arg_to == BaseType.BOOLEAN or arg_to == BaseType.INT or arg_to == BaseType.CHAR):
        return "fptosi"

    if (arg_from == BaseType.INT or arg_from == BaseType.BOOLEAN or arg_from == BaseType.CHAR) and arg_to == BaseType.DOUBLE:
        return "sitofp"


class CodeLine:
    def __init__(self, code: str):
        self.code = code

    def __str__(self):
        return "{0}\n".format(self.code)


class CodeGenerator:
    def __init__(self):
        self.code_lines: List[CodeLine] = []
        self.var_counter: Dict[str, int] = {}

    def add_first(self, code: str):
        self.code_lines.insert(0, CodeLine(code))

    def add(self, code: str):
        self.code_lines.append(CodeLine(code))

    def __str__(self):
        code = ""
        for line in self.code_lines:
            code += str(line)
        return code

    def increment_var_index(self, var_name: str) -> int:
        index = 0
        if var_name in self.var_counter:
            index = self.var_counter[var_name]
        self.var_counter[var_name] = index + 1
        return index

    def get_temp_var(self):
        return f'%{TEMP_VAR_NAME}.{self.increment_var_index(TEMP_VAR_NAME)}'

    def remove_ident(self, ident: str):
        self.var_counter.pop(ident, None)

    def llvm_gen(self, AstNode):
        pass
