import visitor
from code_generator_base import *
from lark_ast_nodes import ArrayElemNode, ArrayDeclNode, AssignNode, CallNode, IdentNode, FunctionNode, ExprNode, \
    IfNode, ForNode, WhileNode, StmtListNode, ReturnNode, ParamNode, LiteralNode, VarsDeclNode
from lark_base import BaseType


class LLVMCodeGenerator(CodeGenerator):

    def start(self):
        self.add("declare i32 @printf(i8*, ...) nounwind")
        self.add("declare i32 @scanf(i8*, ...) nounwind\n")

        self.add("declare void @llvm.memcpy.p0i32.p0i32.i32(i32*, i32*, i32, i1)")
        self.add("declare void @llvm.memcpy.p0i1.p0i1.i32(i1*, i1*, i32, i1)")
        self.add("declare void @llvm.memcpy.p0i8.p0i8.i32(i8*, i8*, i32, i1)")
        self.add("declare void @llvm.memcpy.p0double.p0double.i32(double*, double*, i32, i1)\n")

        self.add(f"@int.0.0 = global i32 0")
        self.add(f"@char.0.0 = global i8 0")
        self.add(f"@double.0.0 = global double 0.0\n")

        self.add("@formatInt = private constant [3 x i8] c\"%d\\00\"")
        self.add("@formatDouble = private constant [3 x i8] c\"%f\\00\"")
        self.add("@formatChar = private constant [3 x i8] c\"%c\\00\"\n")

    @visitor.on('AstNode')
    def llvm_gen(self, AstNode):
        """
        Нужен для работы модуля visitor (инициализации диспетчера)
        """
        pass

    @visitor.when(VarsDeclNode)
    def llvm_gen(self, node: VarsDeclNode):
        type = LLVM_TYPE_NAMES[node.vars_type.node_type.base_type]
        val = LLVM_TYPE_DEFAULT_VALUES[node.vars_type.node_type.base_type]
        for node in node.vars_list:
            if isinstance(node, AssignNode):
                self.add(f"%{node.var.name} = alloca {type}")
                node.llvm_gen(self)
            if isinstance(node, IdentNode):
                self.add(f"%{node.name} = alloca {type}")
                self.add(f"store {type} {val}, {type}* %{node.name}")

    @visitor.when(AssignNode)
    def llvm_gen(self, node: AssignNode):
        add = "fadd" if node.node_type.base_type == BaseType.DOUBLE else "add"

        if node.val.node_type == node.var.node_type and node.val.node_type.array:
            self_type = LLVM_TYPE_NAMES[node.node_type.base_type]

            if node.val.node_type.is_arr and isinstance(node.val, CallNode):
                result = node.val.llvm_load(self)
                var_type = LLVM_TYPE_NAMES[node.var.node_type.base_type]
                self.add(f"store {var_type}* {result}, {var_type}** %{node.var.name} ")
                return

            load_temp_var = self.get_temp_var()
            space_temp_var = self.get_temp_var()
            size = node.val.node_ident.size.llvm_load(self)
            assignment_type = LLVM_TYPE_NAMES[node.node_type.base_type]

            self.add(f"{load_temp_var} = load {self_type}*, {self_type}** %{node.val.name}")
            self.add(f"{space_temp_var} = alloca {self_type}, i32 {size}")

            self.add(f"call void @llvm.memcpy.p0{assignment_type}.p0{assignment_type}.i32("
                     f"{assignment_type}* {space_temp_var}, {assignment_type}* {load_temp_var},"
                     f" i32 {size}, i1 0)")

            self.add(f"store {self_type}* {space_temp_var}, {self_type}** %{node.var.name}")
            return

        if isinstance(node.var, ArrayElemNode):
            target_ptr = f"{node.var.llvm_load_ptr(self)}"
            var_name = node.var.name.name
        else:
            target_ptr = f"%{node.var.name}"
            var_name = node.var.name

        value_type = LLVM_TYPE_NAMES[node.node_type.base_type]
        if isinstance(node.val, LiteralNode):
            value_index = self.increment_var_index(var_name)
            value = node.val.llvm_load(self)
            self.add(f"%{var_name}.{value_index} = {add} {value_type} "
                     f"{0.0 if node.node_type.base_type == BaseType.DOUBLE else 0}, {value}")
            self.add(f"store {value_type} %{var_name}.{value_index}, {value_type}* {target_ptr}")

        elif isinstance(node.val, ExprNode):
            res = node.val.llvm_load(self)
            self.add(f"store {value_type} {res}, {value_type}* {target_ptr}")

    @visitor.when(ArrayDeclNode)
    def llvm_gen(self, node: ArrayDeclNode):
        index = self.increment_var_index(node.name.name)
        count_arg = node.value.llvm_load(self)
        node_type = LLVM_TYPE_NAMES[node.node_type.base_type]
        value_type = LLVM_TYPE_NAMES[node.value.node_type.base_type]

        self.add(f"%{node.name.name}.{index} = alloca {node_type}, {value_type} {count_arg}")
        self.add(f"%{node.name.name} = alloca {node_type}*")
        self.add(f"store {node_type}* %{node.name.name}.{index}, {node_type}** %{node.name.name}")

    @visitor.when(IfNode)
    def llvm_gen(self, node: IfNode):
        index = self.increment_var_index('if')
        cond_res = node.cond.llvm_load(self)
        eq_label = f"IfTrue.0.{index}"
        neq_label = f"IfFalse.0.{index}"
        res_label = f"IfEnd.0.{index}"

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
        condition = node.cond.llvm_load(self)
        self.add(f"br i1 {condition}, label %{for_body}, label %{for_exit}")

        self.add(f"\n{for_body}:")
        node.body.llvm_gen(self)
        self.add(f"br label %{for_hatch}\n")

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

        condition = node.cond.llvm_load(self)
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
            res = node.expr.llvm_load(self) if node.expr is not None else LLVM_TYPE_NAMES[BaseType.VOID]
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

        self.add(f"define {func_type} @{node.name.name} ({node.param_list.llvm_load(self)}) "'{\n')

        if len(node.param_list.children) > 0:
            for arg in node.param_list.children:
                arg_type = LLVM_TYPE_NAMES[arg.type_var.name]
                if isinstance(arg, ParamNode):
                    self.add(f"%{arg.name} = alloca {arg_type}")
                    self.add(f"store {arg_type} %c{arg.name}, {arg_type}* %{arg.name}")
                elif isinstance(arg, ArrayDeclNode):
                    index = self.increment_var_index(arg.name.name)
                    self.add(f"%{arg.name.name} = alloca {arg_type}*")
                    self.add(f"%{arg.name.name}.{index} = alloca {arg_type}, i32 {arg.value.llvm_load(self)}")
                    self.add(f"call void @llvm.memcpy.p0{arg_type}.p0{arg_type}.i32("
                             f"{arg_type}* %{arg.name.name}.{index}, {arg_type}* %c{arg.name.name}, "
                             f"i32 {arg.value.llvm_load(self)}, i1 0)")
                    self.add(f"store {arg_type}* %{arg.name.name}.{index}, {arg_type}** %{arg.name.name}")

        node.list.llvm_gen(self)

        if next((x for x in node.list.children if isinstance(x, ReturnNode)), None) is None:
            self.add("ret void")
        self.add("}")

    @visitor.when(CallNode)
    def llvm_gen(self, node: CallNode):
        node.llvm_load(self)
