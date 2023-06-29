import visitor
from lark_ast_nodes import *
from semantic_base import *


def type_convert(expr: ExprNode, type_: TypeDesc, except_node: Optional[AstNode] = None,
                 comment: Optional[str] = None) -> ExprNode:
    """Метод преобразования ExprNode узла AST-дерева к другому типу
    :param expr: узел AST-дерева
    :param type_: требуемый тип
    :param except_node: узел, у которого будет исключение
    :param comment: комментарий
    :return: узел AST-дерева с операцией преобразования
    """

    if expr.node_type is None:
        except_node.semantic_error('Тип выражения не определен')
    if expr.node_type == type_:
        return expr
    if expr.node_type.is_simple and type_.is_simple and \
            expr.node_type.base_type in TYPE_CONVERTIBILITY and type_.base_type in TYPE_CONVERTIBILITY:
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
            node.node_type = TypeDesc.BOOLEAN
        elif isinstance(node.value, int):
            node.node_type = TypeDesc.INT
        elif isinstance(node.value, float):
            node.node_type = TypeDesc.DOUBLE
        elif isinstance(node.value, str) and len(node.value) == 1:
            node.node_type = TypeDesc.CHAR
        else:
            node.semantic_error('Неизвестный тип {} для {}'.format(type(node.value), node.value))
        node.scope = scope

    @visitor.when(IdentNode)
    def semantic_check(self, node: IdentNode, scope: IdentScope):
        ident = scope.get_ident(node.name)
        if ident is None:
            node.semantic_error('Идентификатор {} не найден'.format(node.name))
        node.node_type = ident.type
        node.node_ident = ident

    @visitor.when(BinOpNode)
    def semantic_check(self, node: BinOpNode, scope: IdentScope) -> None:
        node.arg1.semantic_check(self, scope)
        node.arg2.semantic_check(self, scope)

        if node.arg1.node_type.is_simple or node.arg2.node_type.is_simple:
            compatibility = BIN_OP_TYPE_COMPATIBILITY[node.op]
            args_types = (node.arg1.node_type.base_type, node.arg2.node_type.base_type)
            if args_types in compatibility:
                node.node_type = TypeDesc.from_base_type(compatibility[args_types])
                return

            if node.arg2.node_type.base_type in TYPE_CONVERTIBILITY:
                for arg2_type in TYPE_CONVERTIBILITY[node.arg2.node_type.base_type]:
                    args_types = (node.arg1.node_type.base_type, arg2_type)
                    if args_types in compatibility:
                        node.arg2 = type_convert(node.arg2, TypeDesc.from_base_type(arg2_type))
                        node.node_type = TypeDesc.from_base_type(compatibility[args_types])
                        return
            if node.arg1.node_type.base_type in TYPE_CONVERTIBILITY:
                for arg1_type in TYPE_CONVERTIBILITY[node.arg1.node_type.base_type]:
                    args_types = (arg1_type, node.arg2.node_type.base_type)
                    if args_types in compatibility:
                        node.arg1 = type_convert(node.arg1, TypeDesc.from_base_type(arg1_type))
                        node.node_type = TypeDesc.from_base_type(compatibility[args_types])
                        return

        node.semantic_error("Оператор {} не применим к типам ({}, {})".format(
            node.op, node.arg1.node_type, node.arg2.node_type
        ))

    @visitor.when(VarsDeclNode)
    def semantic_check(self, node: VarsDeclNode, scope: IdentScope):
        if str(node.vars_type) not in BaseType.list():
            node.semantic_error(f"Неизвестный тип {node.vars_type}")
        for var in node.vars_list:
            var_node: IdentNode = var.var if isinstance(var, AssignNode) else var
            try:
                scope.add_ident(IdentDesc(var_node.name, TypeDesc.from_str(str(node.vars_type))))
            except SemanticException as e:
                var_node.semantic_error(e.message)
            var.semantic_check(self, scope)
        node.vars_type.node_type = TypeDesc.from_str(node.vars_type.name)
        node.scope = scope
        node.node_type = TypeDesc.VOID

    @visitor.when(ArrayDeclNode)
    def semantic_check(self, node: ArrayDeclNode, scope: IdentScope) -> None:
        if str(node.type_var) not in BaseType.list():
            node.semantic_error(f"Неизвестный тип {node.type_var}")

        try:
            node.value.semantic_check(self, scope)
            scope.add_ident(ArrayDesc(str(node.name), TypeDesc.from_str(str(node.type_var), True),
                                      type_convert(node.value, TypeDesc.INT, node)))
        except SemanticException as e:
            node.semantic_error(e.message)
        node.node_type = TypeDesc.from_str(str(node.type_var), True)

    @visitor.when(ArrayElemNode)
    def semantic_check(self, node: ArrayElemNode, scope: IdentScope) -> None:
        node.name.semantic_check(self, scope)
        node.value.semantic_check(self, scope)
        curr_ident = scope.get_ident(str(node.name))
        if not isinstance(curr_ident, ArrayDesc):
            node.semantic_error(f"{node.name} не массив")

        node.node_type = scope.get_ident(str(node.name)).toIdentDesc().type

    @visitor.when(AssignNode)
    def semantic_check(self, node: AssignNode, scope: IdentScope) -> None:
        node.var.semantic_check(self, scope)
        node.val.semantic_check(self, scope)

        if node.var.node_ident is not None and node.val.node_ident is not None \
                and type(node.var.node_ident) != type(node.val.node_ident):
            node.semantic_error("несовместимые типы")

        node.val = type_convert(node.val, node.var.node_type, node, 'присваиваемое значение')
        node.node_type = node.var.node_type

    @visitor.when(IfNode)
    def semantic_check(self, node: IfNode, scope: IdentScope) -> None:
        node.cond.semantic_check(self, scope)
        node.cond = type_convert(node.cond, TypeDesc.BOOLEAN, None, 'условие')
        node.then_stmt.semantic_check(self, IdentScope(scope))
        if node.else_stmt:
            node.else_stmt.semantic_check(self, IdentScope(scope))
        node.node_type = TypeDesc.VOID

    @visitor.when(ForNode)
    def semantic_check(self, node: ForNode, scope: IdentScope) -> None:
        scope = IdentScope(scope)
        node.init.semantic_check(self, scope)
        if node.cond == EMPTY_STMT:
            node.cond = LiteralNode('true')
        node.cond.semantic_check(self, scope)
        node.cond = type_convert(node.cond, TypeDesc.BOOLEAN, None, 'условие')
        node.step.semantic_check(self, scope)
        node.body.semantic_check(self, IdentScope(scope))
        node.node_type = TypeDesc.VOID
        node.scope = scope

    @visitor.when(WhileNode)
    def semantic_check(self, node: WhileNode, scope: IdentScope) -> None:
        scope = IdentScope(scope)
        if node.cond == EMPTY_STMT:
            node.cond = LiteralNode('true')
        node.cond.semantic_check(self, scope)
        node.cond = type_convert(node.cond, TypeDesc.BOOLEAN, None, 'условие')
        node.stmt_list.semantic_check(self, IdentScope(scope))
        node.node_type = TypeDesc.VOID

    @visitor.when(StmtListNode)
    def semantic_check(self, node: StmtListNode, scope: IdentScope) -> None:
        if not node.program:
            scope = IdentScope(scope)
        for expr in node.exprs:
            expr.semantic_check(self, scope)
        node.node_type = TypeDesc.VOID

    @visitor.when(ParamNode)
    def semantic_check(self, node: ParamNode, scope: IdentScope) -> None:
        try:
            node.name.node_ident = scope.add_ident(IdentDesc(node.name.name, TypeDesc.from_str(str(node.type_var), node.is_arr)))
        except:
            raise node.name.semantic_error(f'Параметр {node.name.name} уже объявлен')
        node.type_var.node_type = TypeDesc.from_str(node.type_var.name)
        node.node_type = TypeDesc.VOID

    @visitor.when(ReturnTypeNode)
    def semantic_check(self, node: ReturnTypeNode, scope: IdentScope) -> None:
        if node.type is None:
            node.semantic_error(f"Неизвестный тип: {type}")
        node.node_type = TypeDesc.from_str(node.type.name)

    @visitor.when(ReturnNode)
    def semantic_check(self, node: ReturnNode, scope: IdentScope) -> None:
        func = scope.curr_func
        if func is None:
            node.semantic_error('Оператор return применим только в функции')

        if node.expr is not None:
            node.expr.semantic_check(self, IdentScope(scope))
            node.expr = type_convert(node.expr, func.func.type.return_type, node, 'возвращаемое значение')

        node.node_type = TypeDesc.VOID
        node.scope = scope

    @visitor.when(FunctionNode)
    def semantic_check(self, node: FunctionNode, scope: IdentScope) -> None:
        if scope.curr_func:
            node.semantic_error(
                "Объявление функции ({}) внутри другой функции не поддерживается".format(node.name.name))
        parent_scope = scope
        node.type.semantic_check(self, scope)
        scope = IdentScope(scope)

        # временно хоть какое-то значение, чтобы при добавлении параметров находить scope функции
        scope.func = EMPTY_IDENT
        params = []
        for param in node.param_list.children:
            # при проверке параметров происходит их добавление в scope
            param.semantic_check(self, scope)
            params.append(TypeDesc.from_str(str(param.type_var), param.is_arr))

        ret = TypeDesc.from_str(str(node.type.type), node.type.is_arr)
        type_ = TypeDesc(None, ret, tuple(params), node.type.is_arr)
        if node.type.is_arr:
            func_ident = ArrayDesc(node.name.name, type_, 1)
        else:
            func_ident = IdentDesc(node.name.name, type_)
        scope.func = func_ident
        node.name.node_type = type_
        try:
            node.name.node_ident = parent_scope.curr_global.add_ident(func_ident)
        except SemanticException as e:
            node.name.semantic_error("Повторное объявление функции {}".format(node.name.name))
        node.list.semantic_check(self, scope)
        node.node_type = TypeDesc.VOID

    @visitor.when(CallNode)
    def semantic_check(self, node: CallNode, scope: IdentScope) -> None:
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
            node.semantic_error(
                'Фактические типы ({1}) аргументов функции {0} не совпадают с формальными ({2}) и не приводимы'.format(
                    func.name, fact_params_str, decl_params_str
                ))
        else:
            node.params = tuple(params)
            node.func.node_type = func.type
            node.func.node_ident = func
            node.node_type = func.type.return_type


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


def check_program_struct(scope):
    main_func = scope.get_ident('main')
    main_type_ = TypeDesc(None, TypeDesc.from_str('int'), tuple())
    not_present = main_func is None or main_func.type != main_type_
    if not_present:
        raise SemanticException('Главная функция void main() отсутствует')
