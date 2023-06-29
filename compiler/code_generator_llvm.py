import visitor
from code_generator_base import *
from lark_ast_nodes import ArrayElemNode, ArrayDeclNode, AssignNode, CallNode, IdentNode, FunctionNode, ExprNode, \
    IfNode, ForNode, WhileNode, StmtListNode, ReturnNode, ParamNode, LiteralNode, VarsDeclNode, BinOpNode, \
    ParamsListNode, TypeConvertNode
from lark_base import BaseType


class LLVMCodeGenerator(CodeGenerator):

    def start(self):
        for function in BUILT_IN_FUNCTIONS:
            self.add(function)

        self.add("declare void @llvm.memcpy.p0i32.p0i32.i32(i32*, i32*, i32, i1)")
        self.add("declare void @llvm.memcpy.p0i1.p0i1.i32(i1*, i1*, i32, i1)")
        self.add("declare void @llvm.memcpy.p0i8.p0i8.i32(i8*, i8*, i32, i1)")
        self.add("declare void @llvm.memcpy.p0double.p0double.i32(double*, double*, i32, i1)\n")

    @visitor.on('AstNode')
    def llvm_gen(self, AstNode):
        """
        Нужен для работы модуля visitor (инициализации диспетчера)
        """
        pass

    @visitor.when(LiteralNode)
    def llvm_gen(self, node: LiteralNode):
        if node.node_type.base_type == BaseType.CHAR:
            return str(ord(node.value))
        return node.value

    @visitor.when(IdentNode)
    def llvm_gen(self, node: IdentNode):
        index = self.increment_var_index(node.name)
        type = LLVM_TYPE_NAMES[node.node_type.base_type]
        self.add(f"%{node.name}.{index} = load {type}, {type}* %{node.name}")
        return f"%{node.name}.{index}"

    @visitor.when(VarsDeclNode)
    def llvm_gen(self, node: VarsDeclNode):
        type = LLVM_TYPE_NAMES[node.vars_type.node_type.base_type]
        val = LLVM_TYPE_DEFAULT_VALUES[node.vars_type.node_type.base_type]
        for var in node.vars_list:
            if node.scope.is_global:
                if isinstance(var, AssignNode):
                    self.add(f"@{var.var.name} = global {type}")
                    var.llvm_gen(self)
                if isinstance(var, IdentNode):
                    self.add(f"@{var.name} = global {type} {val}")
            else:
                if isinstance(var, AssignNode):
                    self.add(f"%{var.var.name} = alloca {type}")
                    var.llvm_gen(self)
                if isinstance(var, IdentNode):
                    self.add(f"%{var.name} = alloca {type}")
                    self.add(f"store {type} {val}, {type}* %{var.name}")

    @visitor.when(AssignNode)
    def llvm_gen(self, node: AssignNode):
        add = "fadd" if node.node_type.base_type == BaseType.DOUBLE else "add"

        if node.val.node_type == node.var.node_type and node.val.node_type.array:
            self_type = LLVM_TYPE_NAMES[node.node_type.base_type]

            if node.val.node_type.is_arr and isinstance(node.val, CallNode):
                result = node.val.llvm_gen(self)
                var_type = LLVM_TYPE_NAMES[node.var.node_type.base_type]
                self.add(f"store {var_type}* {result}, {var_type}** %{node.var.name} ")
                return

            load_temp_var = self.get_temp_var()
            space_temp_var = self.get_temp_var()
            size = node.val.node_ident.size.llvm_gen(self)
            assignment_type = LLVM_TYPE_NAMES[node.node_type.base_type]

            self.add(f"{load_temp_var} = load {self_type}*, {self_type}** %{node.val.name}")
            self.add(f"{space_temp_var} = alloca {self_type}, i32 {size}")

            self.add(f"call void @llvm.memcpy.p0{assignment_type}.p0{assignment_type}.i32("
                     f"{assignment_type}* {space_temp_var}, {assignment_type}* {load_temp_var},"
                     f" i32 {size}, i1 0)")

            self.add(f"store {self_type}* {space_temp_var}, {self_type}** %{node.var.name}")
            return

        if isinstance(node.var, ArrayElemNode):
            target_ptr = f"{self.llvm_load_array_ptr(node.var)}"
            var_name = node.var.name.name
        else:
            target_ptr = f"%{node.var.name}"
            var_name = node.var.name

        value_type = LLVM_TYPE_NAMES[node.node_type.base_type]
        if isinstance(node.val, LiteralNode):
            value_index = self.increment_var_index(var_name)
            value = node.val.llvm_gen(self)
            default = LLVM_TYPE_DEFAULT_VALUES[node.node_type.base_type]
            self.add(f"%{var_name}.{value_index} = {add} {value_type} {default}, {value}")
            self.add(f"store {value_type} %{var_name}.{value_index}, {value_type}* {target_ptr}")

        elif isinstance(node.val, ExprNode):
            res = node.val.llvm_gen(self)
            self.add(f"store {value_type} {res}, {value_type}* {target_ptr}")

    @visitor.when(ArrayDeclNode)
    def llvm_gen(self, node: ArrayDeclNode):
        index = self.increment_var_index(node.name.name)
        count_arg = node.value.llvm_gen(self)
        node_type = LLVM_TYPE_NAMES[node.node_type.base_type]
        value_type = LLVM_TYPE_NAMES[node.value.node_type.base_type]

        self.add(f"%{node.name.name}.{index} = alloca {node_type}, {value_type} {count_arg}")
        self.add(f"%{node.name.name} = alloca {node_type}*")
        self.add(f"store {node_type}* %{node.name.name}.{index}, {node_type}** %{node.name.name}")

    @visitor.when(ArrayElemNode)
    def llvm_gen(self, node: ArrayElemNode):
        result = f"%{node.name.name}.{self.increment_var_index(node.name.name)}"
        self_type = LLVM_TYPE_NAMES[node.node_type.base_type]

        temp_var = self.get_temp_var()
        self.add(f"{temp_var} = load {self_type}*, {self_type}** %{node.name.name}")

        value_type = LLVM_TYPE_NAMES[node.value.node_type.base_type]
        ptr = self.get_temp_var()
        self.add(f"{ptr} = getelementptr inbounds {self_type}, {self_type}* {temp_var}, "
                 f"{value_type} {node.value.llvm_gen(self)}")
        self.add(f"{result} = load {self_type}, {self_type}* {ptr}")
        return result

    @visitor.when(BinOpNode)
    def llvm_gen(self, node: BinOpNode):
        arg1 = node.arg1.llvm_gen(self)
        arg2 = node.arg2.llvm_gen(self)

        ret = self.get_temp_var()
        type = LLVM_TYPE_NAMES[node.arg1.node_type.base_type]
        bin_op = LLVM_FLOAT_BIN_OPS[node.op] if node.arg1.node_type.base_type == BaseType.DOUBLE else LLVM_INT_BIN_OPS[
            node.op]
        self.add(f"{ret} = {bin_op} {type} {arg1}, {arg2}")
        return ret

    @visitor.when(TypeConvertNode)
    def llvm_gen(self, node: TypeConvertNode):
        var = node.expr.llvm_gen(self)
        type_from = node.expr.node_type.base_type
        llvm_type_from = LLVM_TYPE_NAMES[type_from]
        type_to = node.node_type.base_type
        llvm_type_to = LLVM_TYPE_NAMES[type_to]
        conv_op = get_llvm_conv_operation(type_from, type_to)
        temp_var = self.get_temp_var()

        if type_to == BaseType.BOOLEAN and (type_from == BaseType.CHAR or type_from == BaseType.INT):
            self.add(f"{temp_var} = icmp ne {llvm_type_from} 0, {var}")
        elif type_to == BaseType.BOOLEAN and type_from == BaseType.DOUBLE:
            self.add(f"{temp_var} = fcmp one {llvm_type_from} 0.0, {var}")
        else:
            self.add(f"{temp_var} = {conv_op} {llvm_type_from} {var} to {llvm_type_to}")

        return temp_var

    @visitor.when(IfNode)
    def llvm_gen(self, node: IfNode):
        index = self.increment_var_index('if')
        cond_res = node.cond.llvm_gen(self)
        eq_label = f"IfTrue.{index}"
        neq_label = f"IfFalse.{index}"
        res_label = f"IfEnd.{index}"

        self.add(
            f"br i1 {cond_res}, label %{eq_label}, label %{neq_label if node.else_stmt is not None else res_label}\n")

        self.add(f"{eq_label}:")
        node.then_stmt.llvm_gen(self)
        self.add(f"br label %{res_label}")

        if node.else_stmt is not None:
            self.add(f"\n{neq_label}:")
            node.else_stmt.llvm_gen(self)
            self.add(f"br label %{res_label}")

        self.add(f"\n{res_label}:")

    @visitor.when(ForNode)
    def llvm_gen(self, node: ForNode):
        index = self.increment_var_index('for')
        for_header = f"for.head.{index}"
        for_cond = f"for.cond.{index}"
        for_body = f"for.body.{index}"
        for_hatch = f"for.hatch.{index}"
        for_exit = f"for.exit.{index}"

        self.add(f"\nbr label %{for_header}")
        self.add(f"{for_header}:")
        node.init.llvm_gen(self)
        self.add(f"br label %{for_cond}")

        self.add(f"\n{for_cond}:")
        condition = node.cond.llvm_gen(self)
        self.add(f"br i1 {condition}, label %{for_body}, label %{for_exit}")

        self.add(f"\n{for_body}:")
        node.body.llvm_gen(self)
        self.add(f"br label %{for_hatch}")

        self.add(f"\n{for_hatch}:")
        node.step.llvm_gen(self)
        self.add(f"br label %{for_cond}")

        self.add(f"\n{for_exit}:")

    @visitor.when(WhileNode)
    def llvm_gen(self, node: WhileNode):
        index = self.increment_var_index('while')
        cond_label = f"whihe.cond.{index}"
        body_label = f"whihe.body.{index}"
        exit_label = f"while.exit.{index}"

        self.add(f"br label %{cond_label}\n")
        self.add(f"{cond_label}:")

        condition = node.cond.llvm_gen(self)
        self.add(f"br i1 {condition}, label %{body_label}, label %{exit_label}\n")

        self.add(f"{body_label}:")
        node.stmt_list.llvm_gen(self)
        self.add(f"br label %{cond_label}\n")

        self.add(f"{exit_label}:")

    @visitor.when(StmtListNode)
    def llvm_gen(self, node: StmtListNode):
        for child in node.children:
            child.llvm_gen(self)

    @visitor.when(ReturnNode)
    def llvm_gen(self, node: ReturnNode):
        var_type = LLVM_TYPE_NAMES[node.expr.node_type.base_type]
        if isinstance(node.expr, IdentNode) and node.expr.node_type.is_arr:
            temp_var = self.get_temp_var()
            self.add(f"{temp_var} = load {var_type}*, {var_type}** %{node.expr.name}")
            self.add(f"ret {var_type}* {temp_var}")
        else:
            res = node.expr.llvm_gen(self) if node.expr is not None else LLVM_TYPE_NAMES[BaseType.VOID]
            if node.expr is None:
                self.add(f"ret void")
            else:
                self.add(f"ret {var_type} {res}")

            if node.scope is not None:
                for ident in node.scope.idents:
                    self.remove_ident(ident)

    @visitor.when(FunctionNode)
    def llvm_gen(self, node: FunctionNode):
        func_type = LLVM_TYPE_NAMES[node.type.node_type.base_type]

        if node.type.is_arr:
            func_type += "*"

        self.add(f"define {func_type} @{node.name.name} ({node.param_list.llvm_gen(self)}) "'{\n')

        if len(node.param_list.children) > 0:
            for arg in node.param_list.children:
                arg_type = LLVM_TYPE_NAMES[arg.type_var.node_type.base_type]
                if isinstance(arg, ParamNode):
                    self.add(f"%{arg.name} = alloca {arg_type}")
                    self.add(f"store {arg_type} %c{arg.name}, {arg_type}* %{arg.name}")
                elif isinstance(arg, ArrayDeclNode):
                    index = self.increment_var_index(arg.name.name)
                    self.add(f"%{arg.name.name} = alloca {arg_type}*")
                    self.add(f"%{arg.name.name}.{index} = alloca {arg_type}, i32 {arg.value.llvm_gen(self)}")
                    self.add(f"call void @llvm.memcpy.p0{arg_type}.p0{arg_type}.i32("
                             f"{arg_type}* %{arg.name.name}.{index}, {arg_type}* %c{arg.name.name}, "
                             f"i32 {arg.value.llvm_gen(self)}, i1 0)")
                    self.add(f"store {arg_type}* %{arg.name.name}.{index}, {arg_type}** %{arg.name.name}")

        node.list.llvm_gen(self)

        if next((x for x in node.list.children if isinstance(x, ReturnNode)), None) is None:
            self.add("ret void")
        self.add("}\n")

    @visitor.when(ParamsListNode)
    def llvm_gen(self, node: ParamsListNode):
        result = list()
        for arg in node.params:
            result.append(arg.llvm_gen(self))
        return ', '.join(result)

    @visitor.when(ParamNode)
    def llvm_gen(self, node: ParamNode):
        type = LLVM_TYPE_NAMES[node.type_var.node_type.base_type]
        return f"{type} %c{node.name.name}"

    @visitor.when(CallNode)
    def llvm_gen(self, node: CallNode):
        result = f"%call.{node.func.name}.{self.increment_var_index(f'call.{node.func.name}')}"
        call_type = LLVM_TYPE_NAMES[node.node_type.base_type]
        if node.node_type.is_arr:
            call_type += "*"
        if node.node_type.base_type == BaseType.VOID:
            res_str = f"call void @{node.func.name}("
        else:
            res_str = f"{result} = call {call_type} @{node.func.name}("
        args = []
        for param in node.params:
            param_type = LLVM_TYPE_NAMES[param.node_type.base_type]
            if param.node_type.is_arr:
                var_name = f"%{param.name}.{self.increment_var_index(param.name)}"
                self.add(f'{var_name} = load {param_type}*, {param_type}** %{param.name}')
                args.append(f'{param_type}* {var_name}')
            else:
                args.append(f'{param_type} {param.llvm_gen(self)}')

        res_str += f"{', '.join(args)})"
        self.add(res_str)
        return result

    def llvm_load_array_ptr(self, node: ArrayElemNode) -> str:
        result = f"%{node.name.name}.{self.increment_var_index(node.name.name)}"
        self_type = LLVM_TYPE_NAMES[node.node_type.base_type]

        temp_var = self.get_temp_var()
        self.add(f"{temp_var} = load {self_type}*, {self_type}** %{node.name.name}")

        value_type = LLVM_TYPE_NAMES[node.value.node_type.base_type]
        self.add(f"{result} = getelementptr inbounds {self_type}, {self_type}* {temp_var}, "
                 f"{value_type} {node.value.llvm_gen(self)}")
        return result
