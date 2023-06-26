from abc import abstractmethod, ABC
from typing import Optional, Tuple, Union

from code_generator_base import CodeGenerator, LLVM_INT_BIN_OPS, LLVM_TYPE_NAMES, LLVM_FLOAT_BIN_OPS, TEMP_VAR_NAME, \
    get_llvm_conv_operation
from lark_base import BinOp, BaseType
from semantic_base import TypeDesc, IdentDesc, SemanticException, IdentScope, is_built_in_func


class AstNode(ABC):

    def __init__(self, line: Optional[int] = None, column: Optional[int] = None, **props):
        super().__init__()
        self.line = line
        self.column = column
        for k, v in props.items():
            setattr(self, k, v)
        self.node_type: Optional[TypeDesc] = None
        self.node_ident: Optional[IdentDesc] = None

    @property
    def children(self) -> Tuple['AstNode', ...]:
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
        res = [self.to_str_full()]
        children_temp = self.children
        for i, child in enumerate(children_temp):
            ch0, ch = '├', '│'
            if i == len(children_temp) - 1:
                ch0, ch = '└', ' '
            res.extend(((ch0 if j == 0 else ch) + ' ' + s for j, s in enumerate(child.tree)))
        return tuple(res)

    def semantic_error(self, message: str):
        raise SemanticException(message, self.line, self.column)

    def semantic_check(self, checker, scope: IdentScope):
        checker.semantic_check(self, scope)

    def llvm_gen(self, generator):
        generator.llvm_gen(self)

    def __getitem__(self, index):
        return self.children[index] if index < len(self.children) else None


class ExprNode(AstNode):
    def llvm_load(self, gen: CodeGenerator) -> str:
        pass


class StmtNode(ExprNode):
    def to_str_full(self):
        return str(self)


class StmtListNode(StmtNode):
    def __init__(self, *exprs: StmtNode,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.exprs = exprs
        self.program = False

    @property
    def children(self) -> Tuple[StmtNode, ...]:
        return self.exprs

    def __str__(self) -> str:
        return '...'


class LiteralNode(ExprNode):
    def __init__(self, literal: str,
                 line: Optional[int] = None, column: Optional[int] = None, **props):
        super().__init__(line=line, column=column, **props)
        self.literal = literal
        self.value = eval(literal)

    def llvm_load(self, gen: CodeGenerator) -> str:
        if self.node_type.base_type == BaseType.CHAR:
            return str(ord(self.value))
        return self.value

    def __str__(self) -> str:
        return '{0} ({1})'.format(self.literal, type(self.value).__name__)


class IdentNode(ExprNode):
    def __init__(self, name: str,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.name = str(name)

    def llvm_load(self, gen: CodeGenerator) -> str:
        index = gen.increment_var_index(self.name)
        type = LLVM_TYPE_NAMES[self.node_type.base_type]
        gen.add(f"%{self.name}.{index} = load {type}, {type}* %{self.name}")
        return f"%{self.name}.{index}"

    def __str__(self) -> str:
        return str(self.name)


class BinOpNode(ExprNode):
    def __init__(self, op: BinOp, arg1: ExprNode, arg2: ExprNode,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.is_simple = (isinstance(arg1, LiteralNode) or (isinstance(arg1, BinOpNode) and arg1.is_simple)) \
                         and (isinstance(arg2, LiteralNode) or (isinstance(arg2, BinOpNode) and arg2.is_simple))

    @property
    def children(self) -> Tuple[ExprNode, ExprNode]:
        return self.arg1, self.arg2

    def llvm_load(self, gen: CodeGenerator) -> str:
        arg1 = self.arg1.llvm_load(gen)
        arg2 = self.arg2.llvm_load(gen)

        ret = gen.get_temp_var()
        type = LLVM_TYPE_NAMES[self.arg1.node_type.base_type]
        bin_op = LLVM_FLOAT_BIN_OPS[self.op] if self.arg1.node_type.base_type == BaseType.DOUBLE else LLVM_INT_BIN_OPS[
            self.op]
        gen.add(f"{ret} = {bin_op} {type} {arg1}, {arg2}")
        return ret

    def __str__(self) -> str:
        return str(self.op.value)


class VarsDeclNode(StmtNode):
    def __init__(self, vars_type: IdentNode, *vars_list: Tuple[AstNode, ...],
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.vars_type = vars_type
        self.vars_list = vars_list

    @property
    def children(self) -> Tuple[ExprNode, ...]:
        return (self.vars_type,) + self.vars_list

    def __str__(self) -> str:
        return 'var'


class CallNode(StmtNode):
    def __init__(self, func: IdentNode, *params: Tuple[ExprNode],
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.func = func
        self.params = params

    def llvm_load(self, gen: CodeGenerator) -> str:
        result = f"%call.{self.func.name}.{gen.increment_var_index(f'call.{self.func.name}')}"

        if len(self.params) == 0 and is_built_in_func(self.func.name):
            if self.func.name == "read_int":
                gen.add(f"call i32 (i8*, ...) @scanf(i8* getelementptr inbounds "
                        f"([3 x i8], [3 x i8]* @formatInt, i32 0, i32 0), i32* @int.0.0)")
                gen.add(f"{result} = load i32, i32* @int.0.0")

            elif self.func.name == "read_char":
                gen.add(f"call i32 (i8*, ...) @scanf(i8* getelementptr inbounds "
                        f"([3 x i8], [3 x i8]* @formatChar, i32 0, i32 0), i8* @char.0.0)")
                gen.add(f"{result} = load i8, i8* @char.0.0")

            elif self.func.name == "read_double":
                gen.add(f"call i32 (i8*, ...) @scanf(i8* getelementptr inbounds "
                        f"([3 x i8], [3 x i8]* @formatDouble, i32 0, i32 0), double* @double.0.0)")
                gen.add(f"{result} = load double, double* @double.0.0")

            return result

        elif len(self.params) == 1 and is_built_in_func(self.func.name):
            var = self.params[0].llvm_load(gen)

            if self.func.name == "print_double" and self.params[0].node_type.base_type == BaseType.DOUBLE:
                gen.add(f"{result} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds "
                        f"([3 x i8], [3 x i8]* @formatDouble, i32 0, i32 0), double {var})")

            elif self.func.name == "print_int" and self.params[0].node_type.base_type == BaseType.INT:
                gen.add(f"{result} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds "
                        f"([3 x i8], [3 x i8]* @formatInt, i32 0, i32 0), i32 {var})")

            elif self.func.name == "print_char" and self.params[0].node_type.base_type == BaseType.CHAR:
                gen.add(f"{result} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds "
                        f"([3 x i8], [3 x i8]* @formatChar, i32 0, i32 0), i8 {var})")

            return result

        call_type = LLVM_TYPE_NAMES[self.node_type.base_type]
        if self.node_type.is_arr:
            call_type += "*"
        if self.node_type.base_type == BaseType.VOID:
            res_str = f"call void @{self.func.name}("
        else:
            res_str = f"{result} = call {call_type} @{self.func.name}("
        args = []
        for param in self.params:
            param_type = LLVM_TYPE_NAMES[param.node_type]
            if param.node_type.is_arr:
                var_name = f"%{param.name}.{gen.increment_var_index(param.name)}"
                gen.add(f'{var_name} = load {param_type}*, {param_type}** %{param.name}')
                args.append(f'{param_type}* {var_name}')
            else:
                args.append(f'{param_type} {param.llvm_load(gen)}')

        res_str += f"{', '.join(args)})"
        gen.add(res_str)
        return result

    @property
    def children(self) -> Tuple[IdentNode, ...]:
        return (self.func,) + self.params

    def __str__(self) -> str:
        return 'call'


class AssignNode(StmtNode):
    def __init__(self, var: IdentNode, val: ExprNode,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.var = var
        self.val = val

    @property
    def children(self) -> Tuple[IdentNode, ExprNode]:
        return self.var, self.val

    def __str__(self) -> str:
        return '='


class IfNode(StmtNode):
    def __init__(self, cond: ExprNode, then_stmt: StmtNode, else_stmt: Optional[StmtNode] = None,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    @property
    def children(self) -> Tuple[ExprNode, StmtNode, Optional[StmtNode]]:
        return (self.cond, self.then_stmt) + ((self.else_stmt,) if self.else_stmt else tuple())

    def __str__(self) -> str:
        return 'if'


class ForNode(AstNode):
    def __init__(self, init: StmtListNode, cond: ExprNode,
                 step: StmtListNode, body: Union[StmtNode, None] = None,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.init = init if init else EMPTY_STMT
        self.cond = cond if cond else EMPTY_STMT
        self.step = step if step else EMPTY_STMT
        self.body = body if body else EMPTY_STMT

    @property
    def children(self) -> Tuple[AstNode, ...]:
        return self.init, self.cond, self.step, self.body

    def __str__(self) -> str:
        return 'for'


class WhileNode(StmtNode):
    def __init__(self, cond: ExprNode, stmt_list: StmtNode,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.cond = cond
        self.stmt_list = stmt_list if stmt_list else EMPTY_STMT

    @property
    def children(self) -> Tuple['AstNode', ...]:
        return self.cond, self.stmt_list

    def __str__(self) -> str:
        return 'while'


class ArrayDeclNode(StmtNode):
    def __init__(self, type_var: IdentNode, name: IdentNode, value: ExprNode,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.type_var = type_var
        self.name = name
        self.value = value

    @property
    def children(self) -> Tuple[ExprNode, ...]:
        return self.type_var, self.name, self.value

    def __str__(self) -> str:
        return 'array-decl'


class ArrayElemNode(ExprNode):
    def __init__(self, name: IdentNode, value: ExprNode,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.name = name
        self.value = value

    def llvm_load(self, gen: CodeGenerator) -> str:
        result = f"%{self.name.name}.{gen.increment_var_index(self.name.name)}"
        self_type = LLVM_TYPE_NAMES[self.node_type.base_type]

        temp_var = gen.get_temp_var()
        gen.add(f"{temp_var} = load {self_type}*, {self_type}** %{self.name.name}")

        value_type = LLVM_TYPE_NAMES[self.value.node_type.base_type]
        ptr = gen.get_temp_var()
        gen.add(f"{ptr} = getelementptr inbounds {self_type}, "
                f"{self_type}* {temp_var}, "
                f"{value_type} {self.value.llvm_load(gen)}")
        gen.add(f"{result} = load {self_type}, {self_type}* {ptr}")
        return result

    def llvm_load_ptr(self, gen: CodeGenerator) -> str:
        result = f"%{self.name.name}.{gen.increment_var_index(self.name.name)}"
        self_type = LLVM_TYPE_NAMES[self.node_type.base_type]

        temp_var = gen.get_temp_var()
        gen.add(f"{temp_var} = load {self_type}*, {self_type}** %{self.name.name}")

        value_type = LLVM_TYPE_NAMES[self.value.node_type.base_type]
        gen.add(f"{result} = getelementptr inbounds {self_type}, "
                f"{self_type}* {temp_var}, "
                f"{value_type} {self.value.llvm_load(gen)}")
        return result

    @property
    def children(self) -> Tuple[ExprNode, ...]:
        return self.name, self.value

    def __str__(self) -> str:
        return 'element[]'


class ParamNode(StmtNode):
    def __init__(self, type_var: IdentNode, name: IdentNode, arr: Optional[str] = None,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.type_var = type_var
        self.name = name
        self.is_arr = arr is not None

    @property
    def children(self) -> Tuple[IdentNode, ExprNode]:
        return self.type_var, self.name

    def llvm_load(self, gen: CodeGenerator) -> str:
        type = LLVM_TYPE_NAMES[self.type_var.name]
        return f"{type} %c{self.name.name}"

    def __str__(self) -> str:
        return f'param {"[]" if self.is_arr else ""}'


class ParamsListNode(StmtNode):
    def __init__(self, *params: Tuple[ParamNode],
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.params = params

    @property
    def children(self) -> Tuple[ParamNode]:
        return self.params

    def llvm_load(self, gen: CodeGenerator) -> str:
        result = list()
        for arg in self.params:
            result.append(arg.llvm_load(gen))
        return ', '.join(result)

    def __str__(self) -> str:
        return 'params_list'


class ReturnTypeNode(ExprNode):
    def __init__(self, type: IdentNode, arr: Optional[str] = None,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.type = type
        self.is_arr = arr is not None

    @property
    def children(self) -> Tuple[ExprNode, ...]:
        return self.type,

    def __str__(self) -> str:
        return f'returns {"array" if self.is_arr else ""}'


class FunctionNode(StmtNode):
    def __init__(self, type: ReturnTypeNode, name: IdentNode, param_list: ParamsListNode, stmt_list: StmtListNode,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.type = type
        self.name = name
        self.param_list = param_list
        self.list = stmt_list

    @property
    def children(self) -> Tuple[ExprNode, ...]:
        return self.type, self.name, self.param_list, self.list

    def __str__(self) -> str:
        return 'function'


class ReturnNode(ExprNode):
    def __init__(self, expr: Optional[ExprNode] = None,
                 column: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(column=column, line=line, **props)
        self.expr = expr

    @property
    def children(self) -> Tuple[ExprNode, ...]:
        return [self.expr] if self.expr else list()

    def __str__(self) -> str:
        return 'return'


class _GroupNode(AstNode):
    """Класс для группировки других узлов (вспомогательный, в синтаксисе нет соотвествия)
    """

    def __init__(self, name: str, *childs: AstNode,
                 column: Optional[int] = None, line: Optional[int] = None, **props) -> None:
        super().__init__(column=column, line=line, **props)
        self.name = name
        self._childs = childs

    def __str__(self) -> str:
        return self.name

    @property
    def childs(self) -> Tuple['AstNode', ...]:
        return self._childs


class TypeConvertNode(ExprNode):
    """Класс для представления в AST-дереве операций конвертации типов данных
       (в языке программирования может быть как expression, так и statement)
    """

    def __init__(self, expr: ExprNode, type_: TypeDesc,
                 column: Optional[int] = None, line: Optional[int] = None, **props) -> None:
        super().__init__(column=column, line=line, **props)
        self.expr = expr
        self.type = type_
        self.node_type = type_

    def llvm_load(self, gen: CodeGenerator) -> str:
        var = self.expr.llvm_load(gen)
        type_from = self.expr.node_type.base_type
        llvm_type_from = LLVM_TYPE_NAMES[type_from]
        type_to = self.node_type.base_type
        llvm_type_to = LLVM_TYPE_NAMES[type_to]
        conv_op = get_llvm_conv_operation(type_from, type_to)
        temp_var = gen.get_temp_var()

        if type_to == BaseType.BOOLEAN and (type_from == BaseType.CHAR or type_from == BaseType.INT):
            gen.add(f"{temp_var} = icmp ne {llvm_type_from} 0, {var}")
        elif type_to == BaseType.BOOLEAN and type_from == BaseType.DOUBLE:
            gen.add(f"{temp_var} = fcmp one {llvm_type_from} 0.0, {var}")
        else:
            gen.add(f"{temp_var} = {conv_op} {llvm_type_from} {var} to {llvm_type_to}")

        return temp_var

    def __str__(self) -> str:
        return 'convert'

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return _GroupNode(str(self.type), self.expr),


EMPTY_IDENT = IdentDesc('', TypeDesc.VOID)
EMPTY_STMT = StmtListNode()
