from typing import List

import visitor
from lark_ast_nodes import *
from semantic_base import *

BUILT_IN_FUNCTIONS = '''
    string read() { }
    void print(string str) { }
    void println(string str) { }
    double parseDouble(string str) { }
    int parseInt(string str) { }
    int length(string str) { }
'''


def type_convert(expr: ExprNode, type_: TypeDesc, except_node: Optional[AstNode] = None,
                 comment: Optional[str] = None) -> ExprNode:
    """Метод преобразования ExprNode узла AST-дерева к другому типу
    :param expr: узел AST-дерева
    :param type_: требуемый тип
    :param except_node: узел, о которого будет исключение
    :param comment: комментарий
    :return: узел AST-дерева c операцией преобразования
    """

    if expr.node_type is None:
        except_node.semantic_error('Тип выражения не определен')
    if expr.node_type == type_:
        return expr
    if expr.node_type.is_simple and type_.is_simple and \
            expr.node_type.simple_type in TYPE_CONVERTIBILITY and type_.simple_type in TYPE_CONVERTIBILITY[
        expr.node_type.simple_type]:
        return TypeConvertNode(expr, type_)
    else:
        (except_node if except_node else expr).semantic_error('Тип {0}{2} не конвертируется в {1}'.format(
            expr.node_type, type_, ' ({})'.format(comment) if comment else ''
        ))


class SemanticChecker:
    @visitor.on('AstNode')
    def semantic_check(self, AstNode):
        """
        Нужен для работы модуля visitor (инициализации диспетчера)
        """
        pass

    @visitor.when(LiteralNode)
    def semantic_check(self, node: LiteralNode, scope: IdentScope):
        if isinstance(node.value, bool):
            node.node_type = TypeDesc.BOOL
        # проверка должна быть позже bool, т.к. bool наследник от int
        elif isinstance(node.value, int):
            node.node_type = TypeDesc.INT
        elif isinstance(node.value, float):
            node.node_type = TypeDesc.DOUBLE
        elif isinstance(node.value, str):
            node.node_type = TypeDesc.STR
        else:
            node.semantic_error('Неизвестный тип {} для {}'.format(type(node.value), node.value))

    @visitor.when(IdentNode)
    def semantic_check(self, node: IdentNode, scope: IdentScope):
        ident = scope.get_ident(node.name)
        if ident is None:
            node.semantic_error('Идентификатор {} не найден'.format(node.name))
        node.node_type = ident.type
        node.node_ident = ident

    @visitor.when(BinOpNode)
    def semantic_check(self, node: BinOpNode, scope: IdentScope):
        node.arg1.semantic_check(self, scope)
        node.arg2.semantic_check(self, scope)

        if node.arg1.node_type.is_simple or node.arg2.node_type.is_simple:
            compatibility = BIN_OP_TYPE_COMPATIBILITY[node.op]
            args_types = (node.arg1.node_type.simple_type, node.arg2.node_type.simple_type)
            if args_types in compatibility:
                node.node_type = TypeDesc.from_simple_type(compatibility[args_types])
                return

            if node.arg2.node_type.simple_type in TYPE_CONVERTIBILITY:
                for arg2_type in TYPE_CONVERTIBILITY[node.arg2.node_type.simple_type]:
                    args_types = (node.arg1.node_type.simple_type, arg2_type)
                    if args_types in compatibility:
                        node.arg2 = type_convert(node.arg2, TypeDesc.from_simple_type(arg2_type))
                        node.node_type = TypeDesc.from_simple_type(compatibility[args_types])
                        return
            if node.arg1.node_type.simple_type in TYPE_CONVERTIBILITY:
                for arg1_type in TYPE_CONVERTIBILITY[node.arg1.node_type.simple_type]:
                    args_types = (arg1_type, node.arg2.node_type.simple_type)
                    if args_types in compatibility:
                        node.arg1 = type_convert(node.arg1, TypeDesc.from_simple_type(arg1_type))
                        node.node_type = TypeDesc.from_simple_type(compatibility[args_types])
                        return

        node.semantic_error("Оператор {} не применим к типам ({}, {})".format(
            node.op, node.arg1.node_type, node.arg2.node_type
        ))

    @visitor.when(CallNode)
    def semantic_check(self, node: CallNode, scope: IdentScope):
        func = scope.get_ident(node.func.name)
        if func is None:
            node.semantic_error('Функция {} не найдена'.format(node.func.name))
        if not func.type.func:
            node.semantic_error('Идентификатор {} не является функцией'.format(func.name))
        if len(func.type.params) != len(node.params):
            node.semantic_error('Кол-во аргументов {} не совпадает (ожидалось {}, передано {})'.format(
                func.name, len(func.type.params), len(node.params)
            ))
        params = []
        error = False
        decl_params_str = fact_params_str = ''
        for i in range(len(node.params)):
            param: ExprNode = node.params[i]
            param.semantic_check(self, scope)
            if len(decl_params_str) > 0:
                decl_params_str += ', '
            decl_params_str += str(func.type.params[i])
            if len(fact_params_str) > 0:
                fact_params_str += ', '
            fact_params_str += str(param.node_type)
            try:
                params.append(type_convert(param, func.type.params[i]))
            except:
                error = True
        if error:
            node.semantic_error('Фактические типы ({1}) аргументов функции {0} не совпадают с формальными ({2})\
                                            и не приводимы'.format(
                func.name, fact_params_str, decl_params_str
            ))
        else:
            node.params = tuple(params)
            node.func.node_type = func.type
            node.func.node_ident = func
            node.node_type = func.type.return_type

    @visitor.when(AssignNode)
    def semantic_check(self, node: AssignNode, scope: IdentScope):
        node.var.semantic_check(self, scope)
        node.val.semantic_check(self, scope)
        node.val = type_convert(node.val, node.var.node_type, node, 'присваиваемое значение')
        node.node_type = node.var.node_type

    @visitor.when(VarsDeclNode)
    def semantic_check(self, node: VarsDeclNode, scope: IdentScope):
        node.type.semantic_check(self, scope)
        for var in node.vars:
            var_node: IdentNode = var.var if isinstance(var, AssignNode) else var
            try:
                scope.add_ident(IdentDesc(var_node.name, node.type.node_type))
            except SemanticException as e:
                var_node.semantic_error(e.message)
            var.semantic_check(self, scope)
        node.node_type = TypeDesc.VOID

    @visitor.when(ReturnNode)
    def semantic_check(self, node: ReturnNode, scope: IdentScope):
        node.val.semantic_check(self, IdentScope(scope))
        func = scope.curr_func
        if func is None:
            node.semantic_error('Оператор return применим только к функции')
        node.val = type_convert(node.val, func.func.type.return_type, node, 'возвращаемое значение')
        node.node_type = TypeDesc.VOID

    @visitor.when(IfNode)
    def semantic_check(self, node: IfNode, scope: IdentScope):
        node.cond.semantic_check(self, scope)
        node.cond = type_convert(node.cond, TypeDesc.BOOL, None, 'условие')
        node.then_stmt.semantic_check(self, IdentScope(scope))
        if node.else_stmt:
            node.else_stmt.semantic_check(self, IdentScope(scope))
        node.node_type = TypeDesc.VOID

    @visitor.when(WhileNode)
    def semantic_check(self, node: WhileNode, scope: IdentScope):
        node.cond.semantic_check(self, scope)
        node.cond = type_convert(node.cond, TypeDesc.BOOL, None, 'условие')
        node.stmt.semantic_check(self, IdentScope(scope))
        node.node_type = TypeDesc.VOID

    @visitor.when(ForNode)
    def semantic_check(self, node: ForNode, scope: IdentScope):
        scope = IdentScope(scope)
        node.init.semantic_check(self, scope)
        if node.cond == EMPTY_STMT:
            node.cond = LiteralNode('true')
        node.cond.semantic_check(self, scope)
        node.cond = type_convert(node.cond, TypeDesc.BOOL, None, 'условие')
        node.step.semantic_check(self, scope)
        node.body.semantic_check(self, IdentScope(scope))
        node.node_type = TypeDesc.VOID

    @visitor.when(FuncParamNode)
    def semantic_check(self, node: FuncParamNode, scope: IdentScope):
        node.type.semantic_check(self, scope)
        node.ident.node_type = TypeDesc(node.type.type_desc.type, node.type.type_desc.complex_type)
        try:
            node.ident.node_ident = scope.add_ident(IdentDesc(node.ident.name, node.ident.node_type, ScopeType.PARAM))
        except SemanticException:
            raise node.ident.semantic_error('Параметр {} уже объявлен'.format(node.ident.name))
        node.node_type = TypeDesc.VOID

    @visitor.when(FuncNode)
    def semantic_check(self, node: FuncNode, scope: IdentScope):
        if scope.curr_func:
            node.semantic_error(
                "Объявление функции ({}) внутри другой функции не поддерживается".format(node.name.name))
        parent_scope = scope
        node.return_type.semantic_check(self, scope)
        scope = IdentScope(scope)

        # временно хоть какое-то значение, чтобы при добавлении параметров находить scope функции
        scope.func = EMPTY_IDENT
        params: List[TypeDesc] = []
        for param in node.params.params:
            # при проверке параметров происходит их добавление в scope
            param.semantic_check(self, scope)
            params.append(param.node_type)

        type_ = TypeDesc(None, VarType.FUNCTION, node.return_type.node_type, tuple(params))
        func_ident = IdentDesc(node.name.name, type_)
        scope.func = func_ident
        node.name.node_type = type_
        try:
            node.name.node_ident = parent_scope.curr_global.add_ident(func_ident)
        except SemanticException as e:
            node.name.semantic_error("Повторное объявление функции {}".format(node.name.name))
        node.body.semantic_check(self, scope)
        node.node_type = TypeDesc.VOID

    @visitor.when(StmtListNode)
    def semantic_check(self, node: StmtListNode, scope: IdentScope):
        if not node.program:
            scope = IdentScope(scope)
        for stmt in node.stmts:
            stmt.semantic_check(self, scope)
        node.node_type = TypeDesc.VOID


def prepare_global_scope() -> IdentScope:
    import lark_parser
    prog = lark_parser.parse(BUILT_IN_FUNCTIONS)
    checker = SemanticChecker()
    scope = IdentScope()
    checker.semantic_check(prog, scope)
    for name, ident in scope.idents.items():
        ident.built_in = True
    scope.var_index = 0
    return scope
